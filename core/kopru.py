# -*- coding: utf-8 -*-
"""KOPRU sorulari: iki kavram arasindaki iliskiyi soran sorular.

Olculdu (canli sohbet kaydi, oturum s1785526574265):

    Soru : "klasik fizik kinetik enerji formulunden cikarak
            schrodingerin denklemindeki hamiltonyan operatoru kisminin
            kinetik enerji formulunu ispatlar misin ... arasindaki
            gecisi aciklamani istiyorum"
    Cevap: "### Kinetik enerji / Ek = m*v**2/2" + degisken listesi

Sistem cumleden yalnizca "kinetik enerji" parcasini cekip formul karti
bastI. Sorunun geri kalani — Schrodinger, Hamiltonyan operatoru,
"ispatla", "arasindaki gecis" — hic okunmadI. Yani soru BUTUN olarak
degil, PARCA olarak anlasildi ve bu yuzden cevap yanlisti.

Kok neden iki katmanlIydI:
  * Niyet siniflandiricisi "formul" diyordu (cumlede "formulunu" geciyor)
    ve formul karti tek bir kavrama kilitlenir.
  * "ispatlar misin" kalibi turetim niyetine takilmiyordu; desen
    \bispatla\b idi, kelime "ispatlar" olunca eslesmiyordu.

Bu dosya soruyu once BUTUN olarak okur: kac ayri kavram adlandirilmis ve
aralarinda bir ILISKI mi soruluyor? Oyleyse cevap tek kart olamaz.
Iliskinin kendisi cekirdekte yaziliysa (bkz. gecisler.py) o anlatim
verilir; degilse iki kavram ve aralarindaki baglar derlenir.
"""
import re

from . import knowledge, formulas

# ── Iliski isteyen kaliplar ────────────────────────────────────────────────
# GUCLU kalip: cumle acikca IKI sey arasindaki bagi soruyor. Bu kalip
# varsa cevap tek kavramla sinirli kalamaz.
_ILISKI_GUCLU = re.compile(
    r"(\baras(indaki|inda)\s+\w*\s*(gecis\w*|iliski\w*|bag\w*|fark\w*|"
    r"benzerlik\w*|nasil|ne)|"
    r"\b\w+(den|dan|ten|tan)\s+(cikarak|yola\s+cikarak|hareketle)|"
    # "X ifadesinden Y'yi turet", "X denkleminden Z elde et" — ayrilma
    # eki + turetme fiili. Olculdu: "ozel gorelilikte enerji ifadesinden
    # klasik kinetik enerjiyi turet" sorusu tek formul kartina dusuyordu.
    r"\b\w+(den|dan|ten|tan)\s+(?:\w+\s+){0,4}?"
    r"(turet|elde\s+et|cikar|gecil|ulas|var)\w*|"
    # "nasil gecilir / gecer / gecis yapilir" — yazim duzelticisi bazen
    # "gecilir"i "gecirilir" yapiyor (olculdu); kok kalibi ekleri kapsar.
    r"\bnasil\s+(gec\w*|donus\w*|baglan\w*|iliskilendiril\w*)|"
    r"\bnereden\s+(geliyor|gelir|cikiyor|cikar)|"
    r"\bbirbiri(yle|ne|nden|leriyle)\b|"
    r"\biliskilendir\w*|\bbagdastir\w*|\bkopru\w*|"
    r"\bgecis(i|ini|ine)?\s+(acikla\w*|anlat\w*|goster\w*)|"
    r"\bhow\s+(is|are|does|do)\s+.*\brelate|\brelationship\s+between|"
    r"\bconnection\s+between|\btransition\s+from|\bbridge\s+between|"
    r"\bdifference\s+between)", re.I)

# ISPAT kalibi: "ispatla", "turet", "goster ki". Tek kavramli bir turetim
# de olabilir (o zaman h_turetim dogru yerdir); bu yuzden tek basina
# yan yana anlatimi tetiklemez, yalnizca yazili bir GECIS konusu birebir
# eslesiyorsa devreye girer.
_ISPAT = re.compile(
    r"(\bispatla\w*|\bispat\s+(et\w*|ed\w*)|\bispatini\b|\bkanitla\w*|"
    r"\bturet\w*|\bcikarim\w*|\bgoster\w*\s+ki|"
    r"\bnasil\s+elde\s+edil\w*|"
    r"\bderive\b|\bderivation\b|\bprove\s+that\b|\bshow\s+that\b)", re.I)

_ILISKI = re.compile("(%s)|(%s)" % (_ILISKI_GUCLU.pattern, _ISPAT.pattern),
                     re.I)

# Iliski sorulmasa bile IKI KAVRAM birlikte anilmissa ve biri otekinin
# genellemesi/limitiyse gecis anlatimi dogru cevaptir.
_GECIS_ANAHTARLARI = ("kanonik_kuantumlama", "klasik_limit",
                      "lagrange_hamilton_gecis", "newton_gorelilik_gecis",
                      "kanonik_donusum")


def _norm(s):
    return knowledge._norm(s or "")


def istek_mi(metin):
    """Metin iki sey arasindaki iliskiyi mi soruyor?"""
    return bool(_ILISKI.search(_norm(metin)))


def konu_bicimli_mi(metin):
    """Cevap FORMUL KARTI degil, ANLATIM bicminde mi olmali?

    Olculdu: "elektrik alan ile manyetik alan arasindaki baglanti nedir"
    sorusuna "Duz telin manyetik alani" formul karti donuyordu. Soru bir
    SAYI istemiyor, bir ILISKI istiyor; icinde sayi da yok. Boyle bir
    soruya formul karti basmak, cumleyi butun okumamaktir.
    """
    n = _norm(metin)
    if not _ILISKI_GUCLU.search(n):
        return False
    if re.search(r"\d", metin or ""):
        return False          # sayi verilmisse hesap istiyordur
    hits = knowledge.search(metin, limit=1) or []
    return bool(hits) and hits[0][0] >= 40


def _kavramlar(metin, esik_orani=0.5, en_fazla=3):
    """Metinde GERCEKTEN adi gecen konulari puanlariyla dondur."""
    hits = knowledge.search(metin, limit=8) or []
    if not hits:
        return []
    tepe = hits[0][0]
    if tepe < 25:
        return []
    esik = max(25, tepe * esik_orani)
    secili = []
    for skor, t in hits:
        if skor < esik:
            break
        secili.append((skor, t))
        if len(secili) >= en_fazla:
            break
    return secili


def _ayri_mi(a, b):
    """Iki konu gercekten AYRI kavram mi, yoksa ayni seyin iki adi mi?"""
    if a["key"] == b["key"]:
        return False
    # Baslik kelimeleri buyuk olcude ortaksa ayni konudur.
    ka = set(_norm(a["tr_title"]).split())
    kb = set(_norm(b["tr_title"]).split())
    if ka and kb and len(ka & kb) >= min(len(ka), len(kb)):
        return False
    return True


def _ozet(t, lang, satir=4):
    """Konu anlatiminin ilk anlamli paragrafi."""
    metin = (t["tr"] if lang == "tr" else t["en"]) or ""
    paragraflar = [p.strip() for p in metin.strip().split("\n\n") if p.strip()]
    if not paragraflar:
        return ""
    out = paragraflar[0]
    # Ilk paragraf cok kisaysa (tek cumlelik giris) ikinciyi de al.
    if len(out) < 160 and len(paragraflar) > 1:
        out += "\n\n" + paragraflar[1]
    cumleler = out.split("\n")
    return "\n".join(cumleler[:satir * 3])


def _tam_anlatim(t, lang):
    """Konunun tam metni: anlatim + bagintilar + ornek."""
    satir = ["### " + (t["tr_title"] if lang == "tr" else t["en_title"]), ""]
    satir.append((t["tr"] if lang == "tr" else t["en"]).strip())
    if t.get("eqs"):
        satir.append("\n**Temel bağıntılar:**" if lang == "tr"
                     else "\n**Key relations:**")
        for e in t["eqs"]:
            satir.append("- `%s`" % e)
    ex = t.get("ex_tr") if lang == "tr" else t.get("ex_en")
    if ex:
        satir.append("\n**Örnek:**" if lang == "tr" else "\n**Worked example:**")
        for e in ex:
            satir.append("- %s" % e)
    return "\n".join(satir)


def _ortak_bag(a, b):
    """Iki konu arasindaki yazili baglar."""
    baglar = []
    ra = set(a.get("related") or [])
    rb = set(b.get("related") or [])
    if b["key"] in ra or a["key"] in rb:
        baglar.append("dogrudan")
    ortak = ra & rb
    if ortak:
        baglar.append(ortak)
    return baglar


def _skorlar(metin, genislik=10):
    hits = knowledge.search(metin, limit=genislik) or []
    return {t["key"]: s for s, t in hits}


def _gecis_adayi(metin, adlar):
    """Adlandirilan kavramlara GERCEKTEN baglanan gecis konusu.

    Iki sart birden aranir:
      * Gecis konusunun kendi arama puani makul (tepe puanin yarisi).
      * Soruda adi gecen BASKA bir kavram, bu gecisin ucunda yazili.

    Ikinci sart olmadan asiri yayilma oluyordu (olculdu: "sicaklik ile
    kinetik enerji arasindaki bag" sorusu, icinde "kinetik enerji"
    gectigi icin kanonik kuantumlamaya gidiyordu; dogru cevap kinetik
    kuram, ⟨E⟩ = 3kT/2).
    """
    skor = _skorlar(metin)
    if not skor:
        return None
    tepe = max(skor.values())
    esik = max(30, tepe * 0.4)
    en_iyi = None
    for k in _GECIS_ANAHTARLARI:
        t = knowledge.get(k)
        if not t or skor.get(k, 0) < esik:
            continue
        # Kendisi disindaki adlandirilmis kavramlardan biri ucunda olmali
        if not (set(t.get("related") or []) & (adlar - {k})):
            continue
        if en_iyi is None or skor[k] > en_iyi[0]:
            en_iyi = (skor[k], t)
    return en_iyi[1] if en_iyi else None


def coz(metin, lang="tr"):
    """Kopru sorusuysa butunlukcu cevabi uret, degilse None."""
    n = _norm(metin)
    guclu = bool(_ILISKI_GUCLU.search(n))
    ispat = bool(_ISPAT.search(n))
    if not (guclu or ispat):
        return None
    kavramlar = _kavramlar(metin)
    if not kavramlar:
        return None

    # 1) Iliskinin KENDISI cekirdekte yaziliysa dogrudan o anlatim verilir.
    #    (gecisler.py'deki kanonik kuantumlama, klasik limit, ...)
    tepe_skor, tepe = kavramlar[0]
    ek = [t for _s, t in kavramlar[1:] if _ayri_mi(t, tepe)]
    # Gecis konusu, soruda adi gecen OTEKI kavramlarla bagdasmali. Aksi
    # halde ortak kelimeler yuzunden yanlis gecis seciliyor (olculdu:
    # "ozel gorelilikte enerji ifadesinden klasik kinetik enerjiyi turet"
    # sorusu, "klasik"+"kinetik"+"enerji" kelimeleri basligina uydugu
    # icin kanonik kuantumlamaya gidiyordu; oysa soru gorelilik sorusu).
    _uyumlu = (not ek) or bool(set(tepe.get("related") or [])
                               & {t["key"] for t in ek})
    if tepe["key"] in _GECIS_ANAHTARLARI and tepe_skor >= 50 and _uyumlu:
        govde = _tam_anlatim(tepe, lang)
        if ek:
            govde += ("\n\n**İlgili konular:** " if lang == "tr"
                      else "\n\n**Related topics:** ")
            govde += ", ".join("*%s*" % (t["tr_title"] if lang == "tr"
                                         else t["en_title"]) for t in ek)
        return govde

    # Bundan sonrasi iki kavrami YAN YANA koyar. Yalnizca "turet" ya da
    # "ispatla" diyen tek kavramli bir soru buraya girmemeli; onun yeri
    # turetim isleyicisidir.
    if not guclu:
        return None

    ayri = [kavramlar[0]]
    for s, t in kavramlar[1:]:
        if all(_ayri_mi(t, u) for _q, u in ayri):
            ayri.append((s, t))
    # Bir GECIS konusu bir kavram degil, bir CEVAPTIR. Yan yana koyma
    # listesine karisirsa alakasiz eslesmeler cikiyor (olculdu: "sicaklik
    # ile kinetik enerji arasindaki bag" -> "Enerjinin Korunumu ile
    # Klasik Kinetik Enerjiden Kuantum Operatorune").
    ayri = [(s, t) for s, t in ayri if t["key"] not in _GECIS_ANAHTARLARI]
    if not ayri:
        return None

    # 2) Adlandirilan kavramlari birbirine BAGLAYAN yazili bir gecis var mi?
    #    Olculdu: "newton mekanigi ile ozel gorelilik arasindaki iliski"
    #    sorusunda ozel_gorelilik (68) tepedeydi, gecis konusu (42)
    #    ucuncu siradaydi; iki konuyu yan yana koymak yerine yazili
    #    gecisi vermek dogru cevaptir.
    adlar = {t["key"] for _s, t in ayri}
    kopru = _gecis_adayi(metin, adlar)
    if kopru:
        govde = _tam_anlatim(kopru, lang)
        ek = [t for _s, t in ayri if _ayri_mi(t, kopru)]
        if ek:
            govde += ("\n\n**Soruda geçen kavramlar:** " if lang == "tr"
                      else "\n\n**Concepts named in the question:** ")
            govde += ", ".join("*%s*" % (t["tr_title"] if lang == "tr"
                                         else t["en_title"]) for t in ek)
        return govde

    if len(ayri) < 2:
        return None

    # 2b) Elle yazili gecis yok — peki KENDI OGRENDIGI bir kopru var mi?
    #     Sistem, korpustan cikardigi ve iki bagimsiz kaynakla dogruladigi
    #     baglantilari `koprular` tablosunda tutar (bkz. kopruogren.py).
    #     Boylece her yeni veri partisi cevaplanabilir soru sayisini
    #     kendiliginden artirir; elle konu yazmak gerekmez.
    try:
        from . import kopruogren as _ko
        _ogrenilmis = _ko.kopru_bul(ayri[0][1]["key"], ayri[1][1]["key"], lang)
        if _ogrenilmis:
            return _ogrenilmis
    except Exception:
        pass

    # 3) Yazili gecis de ogrenilmis kopru de yoksa: iki kavrami yan yana
    #    koy, aralarindaki baglari goster.
    a, b = ayri[0][1], ayri[1][1]
    basl = ("## %s ile %s arasındaki ilişki" if lang == "tr"
            else "## How %s and %s are related")
    out = [basl % (a["tr_title"] if lang == "tr" else a["en_title"],
                   b["tr_title"] if lang == "tr" else b["en_title"]), ""]
    for t in (a, b):
        out.append("### " + (t["tr_title"] if lang == "tr" else t["en_title"]))
        out.append("")
        out.append(_ozet(t, lang))
        if t.get("eqs"):
            out.append("")
            for e in t["eqs"][:4]:
                out.append("- `%s`" % e)
        out.append("")

    # Buraya dusmek sunu demektir: iki kavramin ADINI biliyorum ama
    # ARALARINDAKI GECISI bilmiyorum. Cevap iki uca da deger, yine de
    # asil sorulan sey — bag — eksiktir. Bunu bir OGRENME HEDEFI olarak
    # kaydediyoruz; ogrenme motoru bir sonraki turunda bu cifti korpusta
    # arayip baglantiyi cikarmaya calisir (bkz. kopruogren.py).
    try:
        from . import kopruogren as _ko
        _ko.bosluk_kaydet(a["key"], b["key"], metin)
    except Exception:
        pass

    out.append("### Bağlantı" if lang == "tr" else "### The connection")
    out.append("")
    baglar = _ortak_bag(a, b)
    soylenen = False
    if "dogrudan" in baglar:
        out.append(("İki konu çekirdekte birbirine bağlı: biri ötekinin "
                    "doğrudan ilgili konusu olarak yazılı.") if lang == "tr"
                   else "The two topics are directly linked in the core "
                        "knowledge base.")
        soylenen = True
    ortak = [x for x in baglar if isinstance(x, set)]
    if ortak:
        adlar = []
        for k in sorted(ortak[0]):
            t = knowledge.get(k)
            if t:
                adlar.append(t["tr_title"] if lang == "tr" else t["en_title"])
        if adlar:
            out.append(("Ortak dayandıkları konular: %s." if lang == "tr"
                        else "They share these underlying topics: %s.")
                       % ", ".join(adlar))
            soylenen = True

    # Ortak DEGISKEN tasiyan formuller iki kavrami sayisal olarak baglar.
    ortak_f = _ortak_formul(a, b)
    if ortak_f:
        out.append(("Aynı büyüklükleri paylaşan bağıntılar:" if lang == "tr"
                    else "Relations sharing the same quantities:"))
        for ad, ifade in ortak_f:
            out.append("- **%s:** `%s`" % (ad, ifade))
        soylenen = True

    if not soylenen:
        out.append(("Çekirdekte bu iki konu arasında yazılı doğrudan bir "
                    "geçiş yok; yukarıdaki iki anlatımı karşılaştırarak "
                    "ilerleyin. İlişkiyi tam istiyorsanız hangi büyüklükten "
                    "hangisine geçmek istediğinizi yazın.") if lang == "tr"
                   else "The core has no written bridge between these two "
                        "topics; compare the two accounts above. Name the two "
                        "quantities you want connected for a sharper answer.")
    return "\n".join(out)


def _ortak_formul(a, b, en_fazla=3):
    """Iki konunun basliklarina birden eslesen formuller."""
    try:
        fa = formulas.search(a["tr_title"], limit=4) or []
        fb = formulas.search(b["tr_title"], limit=4) or []
    except Exception:
        return []
    ida = {f["id"] for _s, f in fa}
    out = []
    for _s, f in fb:
        if f["id"] in ida:
            out.append((f.get("tr") or f["id"], f.get("eq") or ""))
        if len(out) >= en_fazla:
            break
    return out
