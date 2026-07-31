"""Dil modeli icin baglam derleme (RAG).

Model uydurmasin diye ona ne soyleyecegini biz veriyoruz: dogrulanmis
formuller, hesap sonuclari, cekirdek konu anlatimlari, okunmus makalelerden
cikarilan bulgular ve kaynaklar.

Kural: baglamdaki her sey ya elle yazilmis ve dogrulanmis bilgidir, ya
SymPy'nin hesabidir, ya da gercek bir makaleden alinmis cumledir. Modelin
kendi "hafizasindan" fizik anlatmasina izin verilmez.
"""
import re

from . import (knowledge, formulas, units, retrieval, bagintilar, sentez,
               nlu)
from .learner import STOP, normalize

# Bagimsiz kelimeler ("teori", "sistem") her metinde gectigi icin ortusme
# sayilmaz; yoksa anlamsiz bir sorgu bile baglam toplar.
_GENEL = set("""teori teorisi kuram yasa yasasi denklem formul sistem model
analiz fizik bilim olay etki ilke sey seyler bulunmayan
theory law equation formula system model analysis physics science thing""".split())


def _ilgili(sorgu, metin, gerekli=None):
    """Metin sorguyla gercekten ortusuyor mu?"""
    qw = {w for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{3,}", normalize(sorgu))}
    tw = {w for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{3,}", normalize(metin))}
    qw -= STOP | _GENEL
    tw -= STOP | _GENEL
    if not qw:
        return False
    if gerekli is None:
        gerekli = 2 if len(qw) >= 2 else 1
    return len(qw & tw) >= gerekli


def _formul_baglami(sorgu, lang="tr"):
    parcalar = []
    for _skor, f in formulas.search(sorgu, limit=3):
        if _skor < 25:
            continue
        ad = f["tr"] if lang == "tr" else f["en"]
        degiskenler = ", ".join(
            "%s = %s%s" % (s, (v[0] if lang == "tr" else v[1]),
                           (" [%s]" % v[2]) if v[2] else "")
            for s, v in f["vars"].items())
        parca = ("FORMUL: %s\n  denklem: %s\n  degiskenler: %s"
                 % (ad, f["eq"], degiskenler))
        # Fiziksel anlam: elle yazilmis, dogrulanmis aciklama. Bunu vermezsek
        # model denklemin anlamini kendi uyduruyor ve hata yapabiliyor
        # (adyabatik sikistirmada "ic enerji degismez" demisti).
        not_ = f.get("note_tr" if lang == "tr" else "note_en")
        if not_:
            parca += "\n  fiziksel anlam: " + not_
        parcalar.append(parca)
    return parcalar


def _konu_baglami(sorgu, lang="tr", uzun=False, esik=20, kaynaklar=None):
    parcalar = []
    for _skor, t in knowledge.search(sorgu, limit=1):
        if _skor < esik:        # zayif eslesme baglama girmemeli
            continue
        govde = t["tr"] if lang == "tr" else t["en"]
        if not uzun:
            cumleler = retrieval.summarize([govde], query=sorgu,
                                           max_sentences=8)
            govde = " ".join(cumleler)
        baslik = t["tr_title"] if lang == "tr" else t["en_title"]
        parca = "KONU: %s\n%s" % (baslik, govde[:3000])
        if t["eqs"]:
            parca += "\n  bagintilar: " + ", ".join(t["eqs"][:5])
        ornekler = t["ex_tr"] if lang == "tr" else t["ex_en"]
        if ornekler:
            parca += "\n  cozumlu ornek: " + ornekler[0][:400]
        parcalar.append(parca)
    return parcalar


def _sabit_baglami(sorgu):
    parcalar = []
    anahtar = units.find_constant(sorgu)
    if anahtar:
        v, u, _d, tr, _en = units.CONSTANTS[anahtar]
        parcalar.append("SABIT: %s = %s %s (%s)"
                        % (anahtar, units.fmt_exact(v), u, tr))
    return parcalar


def _bulgu_baglami(sorgu, limit=5):
    parcalar = []
    for b in retrieval.insights(sorgu, limit=limit,
                                turler=("tanim", "bulgu", "iliski")):
        parcalar.append("MAKALE BULGUSU [%s]: %s" % (b["tur"], b["cumle"][:400]))
    return parcalar


def _makale_baglami(sorgu, limit=4, kaynaklar=None):
    parcalar = []
    for p in retrieval.search_papers(sorgu, limit=limit * 2):
        ozet = (p.get("abstract") or "")
        # Konuyla ortusmeyen makale baglama girmemeli
        if not _ilgili(sorgu, (p.get("title") or "") + " " + ozet[:600]):
            continue
        if len(parcalar) >= limit:
            break
        cumleler = retrieval.summarize([ozet], query=sorgu, max_sentences=2)
        rozet = []
        if p.get("hakemli") == 1:
            rozet.append("hakemli")
        if (p.get("atif") or -1) > 0:
            rozet.append("%d atif" % p["atif"])
        parcalar.append("KAYNAK: %s (%s)\n  %s"
                        % ((p.get("title") or "")[:160],
                           ", ".join(rozet) or (p.get("source") or ""),
                           " ".join(cumleler)[:500]))
        if kaynaklar is not None and p.get("url"):
            kaynaklar.append({"baslik": (p.get("title") or "")[:160],
                              "url": p["url"],
                              "tur": p.get("source") or "makale"})
    return parcalar


def _turetilmis_baglami(sorgu, limit=3):
    """Makalelerin birlestirilmesinden turetilmis bilgi.

    Bu bilgiler tek bir makaleden degil, birden cok makalenin uzlasmasindan
    gelir; kanit sayisi baglama yazilir ki model bunu aktarabilsin.
    """
    parcalar = []
    try:
        from . import sentezbilgi
        for d in sentezbilgi.ara(sorgu, limit=limit):
            parcalar.append("TURETILMIS BILGI (%d bagimsiz makale destekliyor): %s"
                            % (d["kanit"], (d["ifade"] or "")[:400]))
    except Exception:
        pass
    return parcalar


def _bagintI_baglami(sorgu, limit=3):
    parcalar = []
    for e in bagintilar.ara(sorgu, limit=limit):
        parcalar.append("OGRENILEN BAGINTI: %s  (kaynak: %s)"
                        % (e["latex"], (e["baglam"] or "")[:80]))
    return parcalar


def derle_kaynakli(sorgu, lang="tr", hesap_sonucu=None, uzun=False):
    """derle() ile ayni, ama kullanilan kaynaklari da dondurur.

    Kullanici bilginin nereden geldigini gormek istiyor: cevabin altina
    kaynakca eklenebilmesi icin baglam kurulurken kaynak listesi toplanir.
    """
    kaynaklar = []
    metin = derle(sorgu, lang, hesap_sonucu, uzun, _kaynaklar=kaynaklar)
    # Ansiklopedik kavram kaynagini da ekle — ama YALNIZCA soruyla gercekten
    # ortusenleri. Kavram aramasi her sorguya bir sey donduruyor; "Hamilton
    # mekanigi" Higgs sorusunun kaynagi degildir.
    try:
        temiz = nlu.strip_command_words(sorgu) or sorgu
        for k in retrieval.search_concepts(temiz, limit=3, lang=lang) or []:
            if not k.get("url"):
                continue
            metin_k = (k.get("name") or "") + " " + (k.get("extract") or "")
            if not _ilgili(temiz, metin_k):
                continue
            kaynaklar.append({"baslik": k.get("name") or "",
                              "url": k["url"], "tur": "Wikipedia"})
    except Exception:
        pass
    # Ayni kaynagi iki kez yazma. Yuklenen belgelerin ayni basligi farkli
    # kayitlarda gecebiliyor; basliga da bakiyoruz.
    gorulen, benzersiz = set(), []
    for k in kaynaklar:
        anahtar = (k.get("url") or "", normalize(k.get("baslik") or "")[:60])
        if anahtar in gorulen or anahtar[1] in {a[1] for a in gorulen}:
            continue
        gorulen.add(anahtar)
        benzersiz.append(k)
    return metin, benzersiz[:6]


def derle(sorgu, lang="tr", hesap_sonucu=None, uzun=False, _kaynaklar=None):
    """Soru icin baglam metni uret.

    hesap_sonucu: dogrulanmis motorlardan gelen hazir yanit (varsa aynen
    korunur ve modele 'bunu aktar' diye verilir).
    """
    parcalar = []

    if hesap_sonucu:
        parcalar.append(
            ("DOGRULANMIS HESAP SONUCU (bu sayilari aynen kullan, degistirme):\n%s"
             if lang == "tr" else
             "VERIFIED CALCULATION (use these numbers exactly):\n%s")
            % hesap_sonucu[:3000])

    temiz = nlu.strip_command_words(sorgu) or sorgu
    # Ogrenilmis takma adlarla genislet: kullanicinin yazdigi terim
    # kaynaklardaki terimden farkli olabilir (Kazimir / Casimir).
    try:
        from . import bosluk as _bosluk
        temiz = _bosluk.genislet(temiz)
    except Exception:
        pass
    parcalar += _sabit_baglami(temiz)
    parcalar += _konu_baglami(temiz, lang, uzun)
    parcalar += _formul_baglami(temiz, lang)
    parcalar += _bagintI_baglami(temiz)
    parcalar += _turetilmis_baglami(temiz)
    parcalar += _bulgu_baglami(temiz, limit=6 if uzun else 4)
    parcalar += _makale_baglami(temiz, limit=4 if uzun else 3,
                                kaynaklar=_kaynaklar)

    # Katı esik bazen mesru sorulari da eliyor: "bir kutunun icindeki gaz
    # isinirsa ne olur" tam cumle olarak zayif eslesiyor ama icindeki "gaz"
    # kelimesi dogru konuyu (ideal gaz) getiriyor. Bos kalirsak icerik
    # kelimeleriyle ikinci bir deneme yapiyoruz.
    if len(parcalar) <= (1 if hesap_sonucu else 0):
        for kelime in _icerik_kelimeleri(temiz):
            # Yedek gecis: kelime zaten sorgudan geldigi icin esik dusuk
            parcalar += _konu_baglami(kelime, lang, uzun, esik=10)
            parcalar += _formul_baglami(kelime, lang)
            if parcalar:
                parcalar += _bulgu_baglami(kelime, limit=3)
                break

    # Cekirdekte yoksa sentezlenmis konu sayfasindan da besle
    if len(parcalar) <= (1 if hesap_sonucu else 0):
        m = sentez.malzeme(temiz, lang)
        if sentez.aciklanabilir_mi(m):
            parcalar.append("DERLENMIS KONU:\n" + sentez.sayfa(m, lang)[:2500])

    return "\n\n".join(parcalar)


def _icerik_kelimeleri(sorgu, limit=8):
    """Sorgudaki anlamli kelimeleri uzundan kisaya sirala.

    Turkce ekleri kabaca atilir ("isinirsa" -> "isin") ki konu aramasi
    tutabilsin.
    """
    kelimeler = []
    for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{3,}", normalize(sorgu)):
        if w in STOP or w in _GENEL:
            continue
        kok = re.sub(r"(irsa|ursa|erse|arsa|larin|lerin|inda|inde|dan|den|"
                     r"lar|ler|nin|nun|siz|lik|lik)$", "", w)
        for aday in (w, kok):
            if len(aday) >= 3 and aday not in kelimeler:
                kelimeler.append(aday)
    # Uzunluga gore siralamiyoruz: "gaz" kisa ama anahtar kelime, "isinirsa"
    # uzun ama tek basina bir konu getirmiyor. Sirayi bozmadan hepsini
    # deniyoruz.
    return kelimeler[:limit]


def bos_mu(baglam):
    return not (baglam or "").strip()
