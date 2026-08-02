# -*- coding: utf-8 -*-
"""BILESIK sorular: tek soruda birden cok asama istenmesi.

Olculdu (dis degerlendirme, GPT):

    Soru : "Lagrange fonksiyonundan baslayarak Euler-Lagrange
            denklemlerini elde ediniz. DAHA SONRA Legendre donusumunu
            kullanarak Hamilton fonksiyonuna gecisi ispatlayiniz.
            Hamilton-Jacobi denklemini tureterek dalga fonksiyonu ile
            iliskisini aciklayiniz VE SON OLARAK Schrodinger
            denkleminin Hamiltonyen operatorunu klasik Hamilton
            fonksiyonundan nasil elde ettiginizi gosteriniz."
    Cevap: yalnizca Legendre donusumu karti.

Degerlendirme: "cevap yanlis degil, sorunun yaklasik %25'ini
karsiliyor." Dort asamadan uc tanesi hic cevaplanmamis.

KOK NEDEN, ve bu tek soruya OZEL DEGIL: sistem soruyu tek bir arama
sorgusu gibi okuyor, en yuksek puanli KONUYU bulup duruyordu. Oysa
soru bir konu sormuyor; sirayla YAPILACAK ISLER listesi veriyor.
"Once X, sonra Y, ardindan Z" kalibindaki her soru ayni sekilde
sakatlaniyordu — asama sayisi kac olursa olsun cevap tek kart
kaliyordu.

Bu dosya soruyu once ASAMALARINA ayirir, her asamayi kendi basina
eslestirir ve cevaplari SORUDAKI SIRAYLA birlestirir. Boylece cevabin
kapsami, sorunun kapsamiyla olculebilir hale gelir.

Kasitli olarak MUHAFAZAKAR davranir: ancak birden cok asama gercekten
ayirt edilebiliyorsa ve en az ikisi cekirdekte guclu karsilik
buluyorsa devreye girer. Aksi halde None doner ve eski yol islemeye
devam eder — yani bu modul bir seyi bozamaz, yalnizca eksik kalani
tamamlar.
"""
import re

from . import knowledge, kopru

# ── Asama sinirlari ───────────────────────────────────────────────────
# Iki tur sinir var ve IKISI de gerekli (olculdu):
#   * Sirali baglac: "daha sonra", "son olarak", ...
#   * CUMLE sonu: soruyu yazan kisi asamalari cogu zaman ayri
#     cumlelere koyar ve arada baglac kullanmaz. Yalnizca baglaca
#     bakinca 4 asamali soru 3 asama goruldu ve Legendre adimi
#     Hamilton-Jacobi adimiyla ayni parcada eridi.
# Uzun kalip once gelmeli ("daha sonra", "sonra"dan once denenmeli).
_BAGLAC = re.compile(
    r"(?:^|\s+)(?:"
    r"ve\s+son\s+olarak|en\s+son\s+olarak|son\s+olarak|en\s+sonunda|"
    r"bunun\s+ardindan|bunun\s+uzerine|bunu\s+takiben|devaminda|"
    r"daha\s+sonra|sonrasinda|ardindan|akabinde|"
    r"ikinci\s+olarak|ucuncu\s+olarak|dorduncu\s+olarak|"
    r"and\s+finally|finally|lastly|after\s+that|subsequently|"
    r"secondly|thirdly|then\s+|next\s+"
    r")\s*", re.I)

# Cumle sonu: nokta/soru/unlem + bosluk. Ondalik sayilari bolmemek
# icin noktadan sonra rakam gelmemeli.
_CUMLE = re.compile(r"(?<=[\.\?\!;])\s+(?![0-9])")

# Her asamanin bir IS istedigini gosteren fiiller. Bir parca bunlardan
# birini icermiyorsa muhtemelen asama degil, yan cumledir.
_ISTEK = re.compile(
    r"(elde\s+ed\w*|turet\w*|ispatla\w*|ispat\s+ed\w*|kanitla\w*|"
    r"goster\w*|acikla\w*|cikar\w*|yaz\w*|kur\w*|bul\w*|hesapla\w*|"
    r"anlat\w*|tanimla\w*|"
    r"derive\w*|prove\w*|show\w*|obtain\w*|explain\w*|find\w*)", re.I)


def _norm(s):
    return knowledge._norm(s or "")


def asamalar(metin):
    """Soruyu sirali asamalarina ayir; asama yoksa bos liste."""
    ham = metin or ""
    if len(ham) < 100:
        return []
    # Once cumlelere, sonra her cumleyi sirali baglaclara bol. Sira
    # onemli: cumle icindeki "ve son olarak" da ayri bir asamadir.
    parcalar = []
    for cumle in _CUMLE.split(ham):
        for p in _BAGLAC.split(_norm(cumle)):
            p = p.strip(" .;\n")
            if len(p) >= 15:
                parcalar.append(p)
    # Her parca bir IS istemeli; istemiyorsa asama degildir.
    parcalar = [p for p in parcalar if _ISTEK.search(p)]
    return parcalar if len(parcalar) >= 2 else []


# Konu adi tasimayan, yalnizca IS bildiren kelimeler. Bir asamaya
# baglam eklerken bunlari tasimanin faydasi yok.
_DOLGU = set("""ve ile veya ama fakat icin gibi kadar daha sonra once
sonrasinda ayrica butun tum her bir bu su o de da ki mi mu ne nasil
neden matematiksel olarak adim adimlariyla birlikte ara tam tamamen
ayrintili sekilde bicimde lutfen misin misiniz iniz ediniz elde turet
turetiniz ispatla ispatlayiniz goster gosteriniz acikla aciklayiniz
anlat yaz kur bul hesapla the and with for from that this then also
step steps show prove derive explain please""".split())


def _anahtar_kelimeler(metin):
    return [k for k in _norm(metin).split()
            if len(k) > 2 and k not in _DOLGU]


def _baglam(parcalar, parca):
    """Bir asamanin baglami: sorunun ONDEN gelen asamalari.

    Artgonderim geriye bakar ("bu formul" = bir onceki asamada
    adlandirilan sey), o yuzden yalnizca onceki parcalar verilir;
    sonrakileri katmak asamayi ileriye kaydiriyordu (olculdu).
    """
    try:
        i = parcalar.index(parca)
    except ValueError:
        return ""
    return " ".join(parcalar[:i])


# Artgonderim (anafora): asama oznesini onceki asamadan aliyor.
# "BU formulun", "AYNI sistemin", "O denklemin" ...
_ISARET = re.compile(r"(?<!\w)(bu|bunu|bunun|bunlar\w*|ayni|onu|onun|"
                     r"soz\s*konusu|yukaridaki|"
                     r"this|that|these|those|the\s+same)(?!\w)", re.I)


def _adaylar(parca, baglam="", esik=60, alt_esik=40):
    """Asamaya karsilik gelebilecek konular, en iyiden baslayarak.

    Iki ayri olculmus kusuru birlikte cozer.

    1. ARTGONDERIM. "Newton'dan baslayarak Lagrange denklemlerini
       ispatla. Daha sonra BU FORMULUN Hamilton formalizmine nasil
       donustugunu goster." Ikinci asama oznesini birinciden aliyor;
       tek basina arandiginda 28 puanla 'kara cisim isimasi'na
       dusuyordu. Boyle asamalar baglami devralmali.

    2. BAGLAMIN ASIRI KULLANIMI. Ama baglami HER zayif asamaya
       eklemek daha beter: "born kuralini turet" asamasi tek basina
       born_kurali'yi 55 puanla buluyordu — esigin hemen altinda —
       ve baglama dusunce 'potansiyel enerji operatoru'ne kayiyordu.
       Yani dogru cevap elimizdeyken yanlisiyla degistiriliyordu.

    Kural: asama KENDI oznesini adlandiriyorsa (isaret sifati yok)
    kendi eslesmesine guvenilir, alt esikle kabul edilir. Baglam
    yalnizca gercekten artgonderimli asamalar icin devreye girer.
    """
    hits = knowledge.search(parca, limit=5) or []
    if hits and hits[0][0] >= esik:
        return [t for _s, t in hits]

    artgonderimli = bool(_ISARET.search(parca))
    if artgonderimli and baglam:
        var = set(_norm(parca).split())
        ek = " ".join(k for k in _anahtar_kelimeler(baglam) if k not in var)
        if ek:
            hits2 = knowledge.search(parca + " " + ek, limit=5) or []
            if hits2 and hits2[0][0] >= esik:
                return [t for _s, t in hits2]

    # Kendi oznesini tasiyan asama, esigin altinda kalsa bile kendi
    # en iyi eslesmesini hak eder; baglamla degistirilmemeli.
    if hits and not artgonderimli and hits[0][0] >= alt_esik:
        return [t for _s, t in hits]
    return []


def _en_iyi_konu(parca, esik=60, baglam=""):
    ad = _adaylar(parca, baglam, esik)
    return ad[0] if ad else None


def _sec(parcalar):
    """Asamalari konulara esle; (asama, konu) ciftlerini sirayla dondur.

    Her asama KENDI bolumunu hak eder. En iyi konusu daha onceki bir
    asamaya gittiyse asamayi dusurmek yerine SIRADAKI adayina gecilir.
    Olculdu: 10 asamali soruda "belirsizlik ilkesinin ispatini yaz"
    asamasi, daha once secilmis poisson_komutator'e dusuyor ve
    sessizce kayboluyordu; ikinci adayi (belirsizlik_ispat) tam da
    aranan konuydu.

    coz() ve kapsam() AYNI islevi kullanir; ayri yazildiklarinda olcum
    cevabin gercekte ne icerdigini yansitmiyordu (olculdu).
    """
    out, gorulen = [], set()
    for p in parcalar:
        secilen = None
        for t in _adaylar(p, _baglam(parcalar, p)):
            if t["key"] not in gorulen:
                gorulen.add(t["key"])
                secilen = t
                break
        out.append((p, secilen))
    return out


def kapsam(metin):
    """Asamalar ve her birine karsilik gelen konu (olcum icin)."""
    return [(p[:48], t["key"] if t else None)
            for p, t in _sec(asamalar(metin))]


def coz(metin, lang="tr"):
    """Cok asamali soruysa asamalari SIRAYLA cevapla, degilse None."""
    parcalar = asamalar(metin)
    if not parcalar:
        return None
    # Sayisal bir problemse bu yol yanlistir; hesap istenmistir.
    if re.search(r"\d", metin or ""):
        return None

    secili = [t for _p, t in _sec(parcalar) if t is not None]

    # Tek konu bulduysak bilesik cevap uretmenin anlami yok; eski yol
    # zaten ayni karti verecek. Iki AYRI konu, kapsamin gercekten
    # genisledigi anlamina gelir.
    if len(secili) < 2:
        return None

    basliklar = [t["tr_title"] if lang == "tr" else t["en_title"]
                 for t in secili]
    bas = ("Soru birden çok aşama istiyor. Sırayla:\n" if lang == "tr"
           else "This question has several stages. In order:\n")
    for i, b in enumerate(basliklar, 1):
        bas += "%d. %s\n" % (i, b)

    govde = [bas.rstrip()]
    for i, t in enumerate(secili, 1):
        govde.append("\n---\n")
        govde.append("## %d. Aşama — %s" % (i, basliklar[i - 1])
                     if lang == "tr"
                     else "## Stage %d - %s" % (i, basliklar[i - 1]))
        # Baslik yukarida verildi; anlatimin kendi basligini tekrarlama.
        tam = kopru._tam_anlatim(t, lang)
        tam = re.sub(r"^###[^\n]*\n+", "", tam)
        govde.append(tam)
    return "\n".join(govde)
