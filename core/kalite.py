"""Makale kalite denetimi.

Amac: yalnizca fizikle gercekten ilgili, geri cekilmemis, bilimsel agirligi
olan makalelerin bilgiye donusmesi.

Tasarim karari — **kaynagin kendi siniflandirmasina guven**:
anahtar kelimeyle "bu fizik mi" diye bakmak yaniltici. Denetimde `Cosmological
billiards` ve `Virasoro cebirleri` gibi gercek kuramsal fizik makaleleri
"fizik disi" sayilmisti, cunku ozette "enerji, kuvvet, dalga" gecmiyordu.
Oysa arXiv'in `hep-th` kategorisi ya da OpenAlex'in "Physics and Astronomy"
alani bu bilgiyi zaten kesin olarak veriyor. Anahtar kelime yalnizca hicbir
siniflandirmasi olmayan kaynaklarda (DergiPark) son care olarak kullanilir.
"""
import re

from .learner import normalize, fizik_ilgili

# arXiv'in fizik kategorileri — bunlar zaten tanimi geregi fiziktir
ARXIV_FIZIK = ("physics.", "quant-ph", "gr-qc", "hep-", "nucl-", "astro-ph",
               "cond-mat", "math-ph", "nlin.", "chem-ph", "plasm-ph")

# OpenAlex alan adlari (primary_topic.field.display_name)
OPENALEX_FIZIK_ALAN = {
    "physics and astronomy", "materials science",
    "earth and planetary sciences", "chemistry",
    "mathematics", "engineering",
}
# Bunlardan yalnizca fizik ve malzeme dogrudan kabul; digerleri ek kanit ister
OPENALEX_KESIN = {"physics and astronomy", "materials science"}

# Fizik disi oldugu acik alanlar — bunlar asla alinmaz
YASAK_ALAN = {
    "arts and humanities", "social sciences", "psychology", "economics",
    "business", "management", "nursing", "dentistry", "veterinary",
    "health professions", "medicine",
}

# Baslikta gecerse fizik disi kabul edilen izler (DergiPark gibi
# siniflandirmasiz kaynaklar icin)
YASAK_IZ = re.compile(
    r"\b(hukuk|siyaset|sosyoloji|felsefe(?!.*fizik)|ilahiyat|teoloji|edebiyat|"
    r"tarih(?!.*fizik)|egitim fakultesi|ogretmen adaylar|ogrenci gorusleri|"
    r"muhasebe|isletme|pazarlama|turizm|iletisim fakultesi|"
    r"hemsirelik|dis hekimligi|veteriner|beden egitimi|spor bilimleri|"
    # Ingilizce karsiliklari: "physical activity/education/therapy" fizik
    # DEGILDIR ama "physical" kelimesi yuzunden fizik sanilyordu (olculdu:
    # OAPEN'den "National Recommendations for Physical Activity" kabul
    # edildi).
    r"physical (activity|education|therapy|fitness|exercise)|"
    r"physical therapist|sport (science|medicine)|nursing|dentistry|"
    r"veterinary|theology|jurisprudence|marketing|accounting|tourism|"
    r"din |islam|kuran|hadis|sosyal bilgiler|"
    # Iktisat/piyasa metinleri "enerji" ve "dalgalanma" gecirdigi icin
    # fizik sanilabiliyordu
    r"piyasas[iı]|fiyat|borsa|enflasyon|ekonomi(k)? buyume|finansal|"
    r"yatirim|ihracat|ithalat|gsyih|tuketici|arz talep)\b")


def kabul_edilir_mi(p):
    """Bu makale bilgiye donusturulmeli mi? (kabul, neden) doner."""
    kaynak = p.get("source", "")
    baslik = (p.get("title") or "")
    ozet = (p.get("abstract") or "")
    n = normalize(baslik + " " + ozet[:1200])

    # 1) Geri cekilmis makale asla alinmaz
    if p.get("geri_cekik"):
        return False, "geri cekilmis"

    # 2) Ozet cok kisaysa bilgi degeri yok
    if len(ozet) < 120:
        return False, "ozet cok kisa"

    # 3) Acikca fizik disi alan
    alan = normalize(p.get("alan") or "")
    if alan and any(y in alan for y in YASAK_ALAN):
        return False, "fizik disi alan: %s" % alan

    # 4) Kaynagin kendi siniflandirmasi
    if kaynak == "arxiv":
        kat = (p.get("categories") or "").lower()
        if any(k in kat for k in ARXIV_FIZIK):
            return True, "arxiv fizik kategorisi"
        return False, "arxiv fizik disi kategori"

    if kaynak == "openalex":
        if alan in OPENALEX_KESIN:
            return True, "openalex fizik alani"
        if alan in OPENALEX_FIZIK_ALAN:
            # Komsu alan: ek olarak fizik icerigi aranir
            if fizik_ilgili(baslik + " " + ozet[:1500]):
                return True, "komsu alan + fizik icerigi"
            return False, "komsu alan, fizik icerigi yok"
        if not alan:
            if fizik_ilgili(baslik + " " + ozet[:1500]):
                return True, "alan bilinmiyor, fizik icerigi var"
            return False, "alan bilinmiyor, fizik icerigi yok"
        return False, "fizik disi alan: %s" % alan

    # 5) Siniflandirmasi olmayan kaynaklar (DergiPark, DOAJ)
    if YASAK_IZ.search(n):
        return False, "fizik disi konu izi"
    if fizik_ilgili(baslik + " " + ozet[:1500]):
        return True, "fizik icerigi dogrulandi"
    return False, "fizik icerigi bulunamadi"


def puan(p):
    """0-100 arasi kalite puani.

    Atif sayisi tek olcut degil: yeni makaleler henuz atif almamis olur.
    Bu yuzden hakemlilik, ozet zenginligi ve alan kesinligi de sayilir.
    """
    s = 0.0
    atif = p.get("atif")
    if atif is not None and atif >= 0:
        # Atif logaritmik olceklenir: 0->0, 10->26, 100->40, 1000->53
        import math
        s += min(40.0, 13.0 * math.log10(atif + 1))
    else:
        s += 8.0                      # bilinmiyor: notr

    hakemli = p.get("hakemli")
    if hakemli == 1:
        s += 25.0
    elif hakemli == 0:
        s += 12.0                     # onbaski: degerli ama hakem gormemis
    else:
        s += 8.0

    alan = normalize(p.get("alan") or "")
    if alan in OPENALEX_KESIN:
        s += 15.0
    elif alan:
        s += 8.0

    ozet = p.get("abstract") or ""
    if len(ozet) > 900:
        s += 12.0
    elif len(ozet) > 400:
        s += 8.0
    elif len(ozet) > 180:
        s += 4.0

    if p.get("dergi"):
        s += 5.0
    yil = str(p.get("published") or "")[:4]
    if yil.isdigit() and int(yil) >= 2015:
        s += 3.0
    return round(min(s, 100.0), 1)
