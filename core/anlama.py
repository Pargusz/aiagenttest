"""Anlama katmani: kullanicinin ne sordugunu cozmeye calisir.

Dil modeli yok; bunun yerine dort asamali belirli (deterministik) bir islem:

  1. Yazim duzeltme  — ogrenilmis sozlukle en yakin kelimeyi bulur
  2. Es anlamli genisletme — "isi sigasi" ile "ozgul isi" ayni seye gider
  3. Soru tipi tespiti — tanim / neden / nasil / karsilastirma / hesap ...
  4. Varlik cikarimi  — konu, formul, sabit, birim, sayi

Boylece "entropy nedir" ile "entrpi neden artar" farkli sekillerde islenir:
birincisi tanim ister, ikincisi nedensel aciklama.
"""
import difflib
import re

from . import knowledge, formulas, units, db
from .learner import normalize, STOP

# ── Es anlamlilar / TR-EN kopruleri ─────────────────────────────────────────
# Solda kullanicinin yazabilecegi bicimler, sagda sistemin bildigi karsilik.
ESANLAM = {
    # termodinamik
    "isi sigasi": "ozgul isi", "isil kapasite": "ozgul isi",
    "specific heat": "ozgul isi", "heat capacity": "ozgul isi",
    "duzensizlik": "entropi", "disorder": "entropi", "entropy": "entropi",
    "isi makinesi": "carnot", "heat engine": "carnot",
    "ideal gaz denklemi": "ideal gaz yasasi", "ideal gas law": "ideal gaz yasasi",
    # mekanik
    "hareket yasalari": "newton yasalari", "laws of motion": "newton yasalari",
    "newton kanunlari": "newton yasalari",
    "hareket enerjisi": "kinetik enerji", "kinetic energy": "kinetik enerji",
    "konum enerjisi": "potansiyel enerji", "potential energy": "potansiyel enerji",
    "hareket miktari": "momentum", "atalet": "eylemsizlik",
    "merkezkac": "merkezcil", "serbest dusus": "serbest dusme",
    "egik atma": "egik atis", "projectile": "egik atis",
    # elektrik
    "gerilim": "voltaj", "voltage": "voltaj", "potansiyel fark": "voltaj",
    "elektrik akimi": "akim", "current": "akim",
    "direnç": "direnc", "resistance": "direnc",
    "sigma": "kapasitans", "capacitance": "kapasitans",
    "manyetik akı": "manyetik aki", "magnetic field": "manyetik alan",
    # kuantum / modern
    "dolanma": "dolaniklik", "entanglement": "dolaniklik",
    "quantum entanglement": "kuantum dolanikligi",
    "belirsizlik prensibi": "belirsizlik ilkesi",
    "uncertainty principle": "belirsizlik ilkesi",
    "dalga parcacik": "ikili doga", "wave particle": "ikili doga",
    "izafiyet": "gorelilik", "relativity": "gorelilik",
    "special relativity": "ozel gorelilik",
    "general relativity": "genel gorelilik",
    "kara delik": "kara delik", "black hole": "kara delik",
    "yari omur": "yari omur", "half life": "yari omur",
    # optik / dalga
    "kirilma": "kirilma indisi", "refraction": "kirilma",
    "girisim": "girisim", "interference": "girisim",
    "kirinim": "kirinim", "diffraction": "kirinim",
    "ses hizi": "ses", "sound speed": "ses",
    # genel
    "formulu": "formul", "formülü": "formul", "denklemi": "denklem",
    "hesaplama": "hesap", "cozumu": "cozum",
}

# Soru tipi kaliplari — sirasi onemli, ustteki once denenir
_SORU_TIPLERI = [
    ("karsilastir", re.compile(
        r"\b(fark[iı]?\s*(nedir|ne)|aras[iı]ndaki fark|kar[sş][iı]la[sş]t[iı]r|"
        r"hangisi (daha|iyi)|ile\s+.*\s+aras[iı]nda|vs\.?|versus|"
        r"difference between|compare|which is better)\b")),
    ("neden", re.compile(
        r"\b(neden|ni[cç]in|niye|sebebi|nedeni|neye ba[gğ]l[iı]|"
        r"why|what causes|reason for|because of what)\b")),
    ("nasil", re.compile(
        r"\b(nas[iı]l|ne [sş]ekilde|hangi yolla|yöntemi|yontemi|ad[iı]m ad[iı]m|"
        r"how does|how do|how is|in what way|by what method)\b")),
    ("dogrula", re.compile(
        r"\b(do[gğ]ru mu|yanl[iı][sş] m[iı]|ger[cç]ek mi|emin misin|"
        r"is it true|is that correct|are you sure|verify)\b")),
    ("ne_zaman", re.compile(r"\b(ne zaman|hangi (y[iı]l|tarih)|when was|when did)\b")),
    ("kim", re.compile(r"\b(kim|kimdir|ke[sş]fetti|buldu|who (is|was|discovered))\b")),
    ("miktar", re.compile(
        r"\b(ka[cç]|ne kadar|de[gğ]eri (ne|ka[cç])|how (much|many)|"
        r"what is the value)\b")),
    ("tanim", re.compile(
        r"\b(nedir|ne demek|ne anlama|tan[iı]m[iı]|a[cç][iı]kla|anlat|"
        r"what is|what are|define|explain|describe)\b")),
]


# Duzeltilmemesi gereken gunluk kelimeler. Bunlar dagarcikta olmadigi icin
# "yanlis yazilmis" sanilip fizik terimlerine cevriliyordu: "misin" -> "isin".
KORUNAN = set("""
misin mısın musun müsün miyim mıyım muyum müyüm midir mıdır mudur mudur
mısınız misiniz musunuz musunuz degil değil değildir degildir olur olmaz
lutfen lütfen tamam peki sanki hani yani zaten ancak fakat ayrica ayrıca
biraz cok çok daha hemen simdi şimdi sonra once önce kadar gibi diye
bana sana ona bize size onlara benim senin onun bizim sizin
acar acsana anlatir anlatır soyler söyler yazar cozer çözer verir
misal mesela ornegin örneğin acaba galiba belki kesin tabii tabi
please could would should thanks thank okay sure maybe about again
alakali alakasiz alaka ilgili ilgisiz
naber nbr nbrs napiyorsun napiyon haber keyif keyifler selam merhaba
gunaydin iyi aksamlar kolay gelsin gorusuruz hosca kal tamamdir
artar artis artiyor azalir azaliyor degisir değişir degismez sabit kalir
olur olmaz gerekir gider gelir duser düşer cikar çıkar verir alir yapar eder
doner döner akar uzar kisalir kısalır isinir ısınır sogur soğur yuzer yüzer
batar kayar dolar bosalir boşalır etkiler baglidir bağlıdır tasir taşır
yansir yansır kirilir kırılır titrer salinir salınır donusur dönüşür
denklem denklemi denklemin denklemler denklemleri sistem sistemi sistemin
sistemler sistemleri kod kodu kodun sayisal sayısal cozum çözüm cozumu
hesap hesabi hesabı grafik grafigi grafiği matris matrisi vektor vektör
fonksiyon fonksiyonu integral turev türev deger değer degeri değeri
hiz hız hizi hızı kuvvet kuvveti enerji enerjisi basinc basınç sicaklik
sicakligi sıcaklık sıcaklığı akim akım akimi akımı gerilim gerilimi
direnc direnç direnci frekans frekansi frekansı dalga dalgasi dalgası
konu konusu konuda konular konulari konuları hakkinda hakkında ilgili
nasil nasıl nasildi nasıldı nasilsa neydi neydin niye nicin niçin kimdi
oldu olmus olmuş olacak olurdu vardi vardı yoktu bunlar sunlar sunu bunu
simule simüle simulasyon simülasyon simulasyonu benzetim video videolar
ders dersi dersler dersleri anlat anlatim anlatım ogret öğret ogretir
uret üret uretir üretir uretim üretim uretme üretme soru sorular sorusu
ornek örnek ornegi örneği ozet özet cizim çizim ciz çiz goster göster
cam cama camdan camin camı su suya sudan suyun hava havaya havadan
buz buza buzdan cisim cisme cismin tel telden telin
gecis geçiş gecisi geçişi gecise gecisini geçişini gecilir geçilir
gecer geçer gecen geçen ispat ispatla ispatlar ispatlamak kanit kanıt
kanitla kanıtla turet türet turetim türetim turetilir türetilir
iliski ilişki iliskisi ilişkisi baglanti bağlantı baglantisi bağlantısı
arasinda arasında arasindaki arasındaki operator operatör operatoru
operatörü hamiltonyen hamiltonyan lagranjiyen kuantumlama
""".split())


# ── Yazim duzeltme ──────────────────────────────────────────────────────────
_SOZLUK = {"kelimeler": None}


def _sozluk():
    """Duzeltmede kullanilacak kelime dagarcigi (bir kez kurulur)."""
    if _SOZLUK["kelimeler"] is not None:
        return _SOZLUK["kelimeler"]
    kelimeler = set()

    def ekle(metin):
        for w in re.findall(r"[a-zA-ZÀ-ÿğüşıöçĞÜŞİÖÇ]{4,}", metin or ""):
            kelimeler.add(normalize(w))

    for t in knowledge.TOPICS:
        ekle(t["tr_title"])
        ekle(t["en_title"])
        for k in t["kw"]:
            ekle(k)
        # Konu GOVDESI de dagarciga girer. Olculdu: "konu" kelimesi
        # dagarcikta olmadigi icin "konum" diye duzeltiliyordu; oysa
        # kendi anlatimlarimiz bu kelimelerle dolu. Dagarcik kullanicinin
        # yazdigi dili tanimali.
        ekle(t["tr"][:6000])
        for o in (t.get("ex_tr") or []):
            ekle(o)
    for f in formulas.FORMULAS:
        ekle(f["tr"])
        ekle(f["en"])
        for k in f["kw_tr"] + f["kw_en"]:
            ekle(k)
        for _s, (a, b, _u) in f["vars"].items():
            ekle(a)
            ekle(b)
    for k, v in units.CONSTANTS.items():
        ekle(v[3])
        ekle(v[4])
    for a in units.CONST_ALIASES:
        ekle(a)
    for a in ESANLAM:
        ekle(a)
    # Ogrenilmis kavram adlari da dagarciga girer
    try:
        for r in db.conn().execute(
                "SELECT name FROM concepts ORDER BY freq DESC LIMIT 3000"):
            ekle(r["name"])
    except Exception:
        pass
    kelimeler -= STOP
    _SOZLUK["kelimeler"] = kelimeler
    return kelimeler


def sozluk_tazele():
    _SOZLUK["kelimeler"] = None


def _ayni_kok(a, b, en_az=5):
    """Iki kelime ayni koke mi ait? (ortak on ek uzunluguna gore)

    "sistemini"/"sistemin" ayni koke ait; "entrpi"/"entropi" degil —
    ikincisinde fark kokte, ilkinde ektedir.
    """
    ortak = 0
    for x, y in zip(a, b):
        if x != y:
            break
        ortak += 1
    # Biri digerinin tam oneki ise fark yalnizca EKTEDIR; kisa
    # kelimelerde de boyledir. Olculdu: "konu" -> "konum" duzeltmesi
    # yapiliyordu, cunku ortak onek 4 idi ve esik 5'ti.
    if ortak >= 3 and (ortak == len(a) or ortak == len(b)):
        return True
    # Uzun ortak kokten sonra iki kisa ek: "gorelilikle" / "gorelilikte".
    # Bu da yazim hatasi degil, cekim farkidir.
    if ortak >= 6 and len(a) - ortak <= 3 and len(b) - ortak <= 3:
        return True
    if ortak < en_az:
        return False
    # Sadece ek farki: kelimelerden biri digerinin tam onekidir.
    # "sistemin" -> "sistemini" boyledir (ek eklenmis).
    # "kinetk" -> "kinetik" boyle DEGILDIR (harf dusmus); ortak on ek
    # 5 olsa da ikisi de devam ediyor, yani fark kokte. O duzeltilmeli.
    return ortak == len(a) or ortak == len(b)


def duzelt(metin, esik=0.87):
    """Yazim hatalarini dagarciktaki en yakin kelimeyle duzelt.

    Yalnizca dagarcikta olmayan, 4+ harfli kelimeler denenir; boylece dogru
    yazilmis kelimeler ve sayilar bozulmaz.
    """
    if not metin:
        return metin, []
    sozluk = _sozluk()
    if not sozluk:
        return metin, []
    duzeltmeler = []

    def _degistir(m):
        kelime = m.group(0)
        n = normalize(kelime)
        if len(n) < 4 or n in sozluk or n in STOP or n.isdigit():
            return kelime
        if n in KORUNAN:
            return kelime
        # Kelimenin KOKU dagarcikta varsa bu bir yazim hatasi degil,
        # cekimli bir bicimdir. Olculdu: "devresinde" -> "cevresinde"
        # diye duzeltiliyordu; oysa koku olan "devre" dagarcikta var ve
        # duzeltme kelimenin ilk harfini degistiriyordu.
        try:
            from . import turkce as _tkr
            for _kok in _tkr.kokler(n):
                if len(_kok) >= 3 and _kok in sozluk:
                    return kelime
        except Exception:
            pass
        # Kelimenin bir ONEKI dagarcikta duruyorsa bu cekim ekidir.
        # Olculdu: "devresinde" -> "cevresinde" diye duzeltiliyordu ve
        # duzeltme ILK HARFI degistiriyordu; oysa "devresi" dagarcikta
        # var. Esik 5 harf: "entrpi"/"kinetk" gibi gercek yazim
        # hatalarinin dagarcikta boyle bir oneki bulunmuyor (olculdu).
        for _k in range(len(n) - 1, 4, -1):
            if n[:_k] in sozluk:
                return kelime

        yakin = difflib.get_close_matches(n, sozluk, n=1, cutoff=esik)
        if not yakin:
            return kelime
        # Turkce cekim eki duzeltme sayilmamali. "sistemini" dagarcikta yok
        # ama koku ("sistem") var; en yakin eslesme "sistemin" oldugu icin
        # kelime bozuluyordu. Ikisi ayni koke aitse dokunmuyoruz: gercek
        # yazim hatasi kokte olur, ekte degil.
        if _ayni_kok(n, yakin[0]):
            return kelime
        duzeltmeler.append((kelime, yakin[0]))
        return yakin[0]

    yeni = re.sub(r"[a-zA-ZÀ-ÿğüşıöçĞÜŞİÖÇ]{4,}", _degistir, metin)
    return yeni, duzeltmeler


def esanlam_ac(metin):
    """Es anlamli ifadeleri sistemin bildigi karsiliklariyla degistir."""
    n = normalize(metin or "")
    degisti = []
    for kaynak, hedef in sorted(ESANLAM.items(), key=lambda kv: -len(kv[0])):
        k = normalize(kaynak)
        if re.search(r"(?<!\w)%s(?!\w)" % re.escape(k), n):
            hn = normalize(hedef)
            if hn != k:
                n = re.sub(r"(?<!\w)%s(?!\w)" % re.escape(k), hn, n)
                degisti.append((kaynak, hedef))
    return n, degisti


def soru_tipi(metin):
    """Sorunun turunu belirle. Hicbirine uymuyorsa 'genel'."""
    n = normalize(metin or "")
    for tip, rx in _SORU_TIPLERI:
        if rx.search(n):
            return tip
    if n.strip().endswith("?"):
        return "tanim"
    return "genel"


def karsilastirma_taraflari(metin):
    """'X ile Y arasindaki fark' -> ('X', 'Y')."""
    n = re.sub(r"\s+", " ", metin or "").strip()
    kaliplar = [
        r"(.+?)\s+ile\s+(.+?)\s+aras[iı]ndaki\s+fark",
        r"(.+?)\s+ile\s+(.+?)\s+fark[iı]",
        r"(.+?)\s+(?:vs\.?|versus)\s+(.+)",
        r"difference between\s+(.+?)\s+and\s+(.+)",
        r"(.+?)\s+mi\s+(.+?)\s+mi",
        r"(.+?)\s+ve\s+(.+?)\s+aras[iı]nda",
        r"compare\s+(.+?)\s+(?:with|and|to)\s+(.+)",
    ]
    for k in kaliplar:
        m = re.search(k, n, re.I)
        if m:
            a = _temizle_taraf(m.group(1))
            b = _temizle_taraf(m.group(2))
            if a and b and a != b:
                return a, b
    return None


def _temizle_taraf(s):
    s = re.sub(r"\b(nedir|ne|nasil|arasindaki|fark|farki|acikla|anlat|"
               r"what|is|the|a|an|explain)\b", " ", s or "", flags=re.I)
    return re.sub(r"\s+", " ", s).strip(" ?.!,")


def coz(metin):
    """Mesaji topluca coz: duzelt, genislet, tipini bul.

    Dondurulen sozluk:
      ham, duzeltilmis, genisletilmis, duzeltmeler, esanlamlar, tip, taraflar
    """
    duzeltilmis, duzeltmeler = duzelt(metin)
    genis, esler = esanlam_ac(duzeltilmis)
    return {
        "ham": metin,
        "duzeltilmis": duzeltilmis,
        "genis": genis,
        "duzeltmeler": duzeltmeler,
        "esanlamlar": esler,
        "tip": soru_tipi(duzeltilmis),
        "taraflar": karsilastirma_taraflari(duzeltilmis),
    }
