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

from . import knowledge, kopru, nlu

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
#
# Olculdu: liste "coz" fiilini icermiyordu ve "Klasik harmonik osilator
# denklemini COZ. Daha sonra ayni sistemi kuantum mekaniginde cozerek
# yaratma/yok etme operatorlerini turet." sorusunda BIRINCI asama
# tamamen dusuyordu. Dahasi ikinci asama artgonderimliydi ("AYNI
# sistemi") ve devralacagi baglam da onunla birlikte kaybolmustu.
# Yonerge fiili listesi eksik kalirsa asama sessizce yok oluyor; bu
# yuzden liste sinav dilinde kullanilan fiillerin tamamini kapsamali.
# Liste nlu.py'de TEK yerde tutulur; iki kopya birbirinden sapiyordu.
_ISTEK = re.compile("(%s)" % nlu.YONERGE_KALIBI, re.I)


# Cevabin BICIMINI isteyen kelimeler. Bunlar bir fizik konusu
# adlandirmaz; nasil anlatilacagini soyler.
#
# Olculdu: sorunun son cumlesi "Tum ara adimlari, kullanilan
# matematiksel varsayimlari, fiziksel yorumlari ve yaklasik yontemleri
# eksiksiz olarak aciklamanizi istiyorum" bir ASAMA sanildi ve sistem
# "Varyasyonel Yontem ve Yaklasik Cozumler" anlatti — soruda hic
# istenmemis bir konu. Bu kalip her uzun sinav sorusunun sonunda
# bulunur, dolayisiyla kusur tek soruya ozel degildi.
_BICIM_KELIME = set("""
ara adim adimi adimlari adimlarini adimlariyla basamak basamaklari
varsayim varsayimi varsayimlari varsayimlarini kabul kabuller
yorum yorumu yorumlari yorumlarini gerekce gerekceleri
yontem yontemi yontemleri yontemlerini teknik teknikleri
yaklasik yaklasim yaklasimi yaklasimlari yaklasimlarini
adimlariyla asama asamalari sira sirasiyla
matematiksel fiziksel kavramsal kuramsal sayisal
kullanilan kullandigin izlenen secilen gerekli
eksiksiz eksiksizce atlamadan tam tamamen butun tum her
ayrintili detayli acik net anlasilir titiz
bicimde sekilde olarak halde duzeyde
aciklamanizi aciklamani aciklamanizi gostermenizi gostermeni
yazmanizi yazmani belirtmenizi belirtmeni vermenizi vermeni
istiyorum isterim rica beklerim lutfen ayrica
ile birlikte kadar gibi
""".split())


def _bicim_istegi_mi(parca):
    """Parca bir fizik konusu degil, cevabin BICIMINI mi istiyor?

    Olcut: parcadaki ANLAMLI kelimelerin hepsi bicim sozlugundeyse
    ortada adlandirilmis bir fizik kavrami yok demektir. Tek bir konu
    kelimesi bile varsa ("Hamilton-Jacobi ... fiziksel anlamini
    aciklayiniz") parca gercek bir asamadir ve dokunulmaz.
    """
    kelimeler = _anahtar_kelimeler(parca)
    if not kelimeler:
        return True
    return all(k in _BICIM_KELIME for k in kelimeler)


def _norm(s):
    return knowledge._norm(s or "")


# OK ZINCIRI: "A -> B -> C -> ... bunlarin her birini acikla".
# Ileri duzey sorularda cok kullanilan bicim. Buradaki ogeler kisa
# adlardir ve KENDILERINDE yonerge fiili YOKTUR; yonerge en sonda tek
# bir cumlede, hepsi icin birden verilir. Bu yuzden ok zinciri normal
# asama ayirmasindan AYRI ele alinir.
#
# Olculdu (canli sohbet): "δS = 0 → Euler-Lagrange → Hamilton →
# Hamilton-Jacobi → Schrodinger → Klein-Gordon → Dirac → Noether →
# Kuantum Alan Kurami  gecislerinin her birinin hangi fiziksel
# problemi cozdugunu ... aciklayiniz." Sekiz gecis istendi; asama
# ayirici 0 asama buldu ve cevapta Klein-Gordon, Dirac ve Noether
# HIC yer almadi.
_OK = re.compile(r"\s*(?:→|->|⇒|=>|➔|⟶)\s*")


def _ok_zinciri(metin):
    """Ok zinciri varsa ogelerini dondur, yoksa bos liste."""
    ham = metin or ""
    if len(_OK.findall(ham)) < 2:
        return []            # en az uc oge (iki ok) aranir
    ogeler = []
    for parca in _OK.split(ham):
        # Ilk oge okun solunda, son oge sagindadir; son ogenin
        # ardindan genellikle YONERGE cumlesi gelir. Ogeyi ilk
        # satirindan alarak yonergeden ayiririz.
        ilk_satir = parca.strip().split("\n")[0].strip(" .;:,")
        if not ilk_satir:
            continue
        # SON oge ile YONERGE ayni satirda olabilir: "... → Kuantum
        # Alan Kurami gecislerinin her birinin ... aciklayiniz."
        # Kuram adlari kisadir; uzun parcanin ilk birkac kelimesini
        # aday sayariz. Yanlis tahmin zararsizdir, cunku ok ogesi
        # ancak ADI TUTAN bir konu bulursa kabul edilir (_ad_adaylari).
        # Olculdu: soru tek satir yazilinca son oge (Kuantum Alan
        # Kurami) tamamen dusuyordu.
        if len(ilk_satir) > 60:
            ilk_satir = " ".join(ilk_satir.split()[:4])
        ogeler.append(_norm(ilk_satir))
    # Formul kalintisi oge degildir: "δS = 0" normalizasyondan sonra
    # " s   0" olarak kaliyor ve konu aramasi bos donuyordu. Olcut,
    # ogenin gercek bir AD tasimasi: en az uc HARF.
    return [o for o in ogeler
            if sum(1 for ch in o if ch.isalpha()) >= 3]


def asamalar(metin):
    """Soruyu sirali asamalarina ayir; asama yoksa bos liste."""
    ham = metin or ""
    ok = _ok_zinciri(ham)
    if len(ok) >= 3:
        return ok
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
    # ...ve istenen is bir FIZIK konusu olmali, cevabin BICIMI degil.
    parcalar = [p for p in parcalar if not _bicim_istegi_mi(p)]
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


# Asama ICINDE sayilan kavramlarin ayraci: virgul ve "ve".
# NOT: asamalar _norm'dan gecmis olarak gelir ve _norm noktalama
# isaretlerini BOSLUGA cevirir; bu yuzden virgulun izi ARDISIK IKI
# BOSLUKTUR. Yalnizca virgule bakinca "A, B ve C" siralamasi ikiye
# bolunuyor ve ortadaki kavram kayboluyordu (olculdu: "Heisenberg
# belirsizlik ilkesi, Ehrenfest teoremi ve Schrodinger denklemi"
# uclusunde belirsizlik ilkesi dusuyordu).
_SAYIM = re.compile(r"\s{2,}|\s*,\s*|\s+ve\s+|\s+and\s+", re.I)

# ARAC EDATI: "X ARACILIGIYLA/YARDIMIYLA/KULLANARAK Y" kaliplarinda X,
# kullanilmasi istenen YONTEMDIR ve cogu zaman adiyla anilmis bir
# teoremdir. Turkcede son cekim edati kendinden HEMEN ONCEKI ad
# obegine baglanir; bu yuzden edattan onceki en fazla uc kelime
# alinir.
#
# Olculdu: "...elde edilen Hamiltonyen operatorunun EHRENFEST TEOREMI
# ARACILIGIYLA klasik Newton hareket denklemlerini nasil verdigini
# ispatlayiniz" asamasinda toplam kelime ortusmesi kanonik_kuantumlama'yi
# one gecirdi (136 / 121) ve kullanicinin adiyla istedigi teorem cevaba
# hic girmedi. Edattan BOLMEK yetmedi (parcanin basinda "hamiltonyen
# operatorunun" kaldigi icin yine ayni konu kazaniyordu); ise yarayan,
# edat oncesi ad obegini AYRICA aramak oldu.
_ARAC = re.compile(
    r"((?:\S+\s+){1,3}?)(?:araciligiyla|yardimiyla|kullanarak|"
    r"vasitasiyla|uzerinden|by\s+means\s+of|using)(?!\w)", re.I)


def _arac_obekleri(parca):
    """Arac edatlarindan once gelen ad obekleri."""
    out = []
    for m in _ARAC.finditer(parca):
        obek = m.group(1).strip()
        if len(_anahtar_kelimeler(obek)) >= 1:
            out.append(obek)
    return out


def _ad_adaylari(oge, en_fazla=4):
    """Ok zinciri ogesi icin adaylar: ADI TUTAN konular.

    Ok zincirindeki oge, bir cumle degil bir ADDIR ("Dirac",
    "Hamilton", "Noether"). Bu yuzden normal esik burada ise yaramaz:
    tek kelimelik sorgu 14 puan aliyor ve dogru konu esigi gecemiyor.
    Komsu ogelerle birlikte aratmak da denendi ve DAHA KOTU: sorgu
    ogeyi kendinden uzaklastirip komsusunun konusuna cekiyor
    ("hamilton hamilton jacobi" -> hamilton_jacobi 102).

    Dogru olcut ADIN TUTMASIDIR: konunun basligi ya da anahtarlari
    ogeyi ICERMELI. Bu kural yalnizca ok zincirinde uygulanabilir,
    cunku orada ogenin TAMAMI bir addir; normal bir asamada ayni kural
    genel tabirleri de yakalayip cevabi sisiriyordu (bkz. asagidaki
    "adiyla anma" notu).
    """
    # BASLIKTA gecen ad, yalnizca anahtar listesinde gecene tercih
    # edilir. Olculdu: "Dirac" ogesi icin arama once weyl_kuantumlama'yi
    # veriyordu (anahtarlarinda "dirac kuantumlama kurali" var), oysa
    # dogru konu basliginda Dirac gecen klein_gordon_dirac.
    basliktan, anahtardan = [], []
    for _skor, t in knowledge.search(oge, limit=10) or []:
        baslikta = any(oge in _norm(t.get(a) or "")
                       for a in ("tr_title", "en_title"))
        anahtarda = any(oge in _norm(k) for k in (t.get("kw") or []))
        if baslikta:
            basliktan.append(t)
        elif anahtarda:
            anahtardan.append(t)
    return (basliktan + anahtardan)[:en_fazla]


def _asama_konulari(parca, baglam="", en_fazla=4):
    """Bir asamada adi gecen KONULARIN hepsi, gorunme sirasiyla.

    Olculdu (arastirma seviyesi soru): "Poisson parantezi, kanonik
    donusumler VE Hamilton akisindan baslayarak operator cebirinin
    neden zorunlu ortaya ciktigini aciklayiniz." Tek asama, ama
    ICINDE uc ayri kavram sayiliyor. Asama basina tek konu verince
    ikisi dusuyordu; ayni sey "Heisenberg belirsizlik ilkesi,
    Ehrenfest teoremi VE Schrodinger denklemi" asamasinda da oluyordu.

    Ileri duzey sorular kavramlari boyle SIRALAR; bu yuzden asamanin
    kendisi de bolunmelidir. Once asamanin butunu aranir (baglam
    butunde saklidir), sonra sayim ogeleri tek tek eklenir.

    en_fazla=4: olculdu, sinir 3 iken "Poisson parantezi, kanonik
    donusumler ve Hamilton akisindan baslayarak operator cebiri..."
    asamasinda dorduncu kavram (Hamilton akisi) disarida kaliyordu.
    Bir asamada dortten fazla kavram sayilmasi seyrek; sinirsiz
    birakmak da cevabi sisiriyor.
    """
    # DENENDI VE GERI ALINDI — "adiyla anilan konu one gecsin".
    # Fikir: asama bir teoremi ADIYLA aniyorsa (kw'si metinde aynen
    # geciyorsa) toplam kelime ortusmesini yensin. Gerekcesi olculmustu:
    # "...Hamiltonyen operatorunun EHRENFEST TEOREMI araciligiyla..."
    # asamasinda kanonik_kuantumlama 136, ehrenfest_teoremi 121 puan
    # aliyor ve adiyla istenen teorem cevaba hic girmiyordu.
    #
    # Neden geri alindi: "ad" ile "genel tabir" ayirt edilemedi.
    # Ayirt edicilik olcutu olarak once uzunluk/kelime sayisi (>=10
    # harf ya da 2 kelime), sonra "adi tek basina aratinca konu acik
    # ara birinci mi" denendi. Ikincisi de ayirmadi:
    #     hamiltonyen operatoru -> 2.67x   (genel tabir)
    #     ehrenfest teoremi     -> 1.39x   (gercek ad)
    # yani genel tabir gercek addan DAHA ayirt edici cikti. Sonuc:
    #   * 10 asamali soru 10 yerine 17 bolum uretti (sisme),
    #   * "belirsizlik ilkesinin ispatini yaz" asamasi poisson_komutator
    #     yerine olcum_hata'ya (olcum hatasi!) gitti — acik gerileme.
    # Kural kaldirildi; yerine ARAC EDATI ayraci kondu (bkz. _SAYIM).
    adaylar = _adaylar(parca, baglam)
    out = adaylar[:1]
    for oge in _arac_obekleri(parca) + _SAYIM.split(parca):
        if len(_anahtar_kelimeler(oge)) < 2:
            continue
        hits = knowledge.search(oge, limit=2) or []
        # Sayim ogesi kisa ve baglamsizdir; yalnizca GUCLU eslesme
        # kabul edilir, yoksa gurultu giriyor.
        if hits and hits[0][0] >= 60:
            for _s, t in hits[:1]:
                if all(t["key"] != u["key"] for u in out):
                    out.append(t)
        if len(out) >= en_fazla:
            break
    return out[:en_fazla]


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
    ok_mu = len(parcalar) >= 3 and all(len(p) <= 60 for p in parcalar)
    out, gorulen = [], set()
    for p in parcalar:
        baglam = _baglam(parcalar, p)
        adaylar = (_ad_adaylari(p) if ok_mu
                   else _asama_konulari(p, baglam))
        if ok_mu:
            # Ok zincirinde bir oge = bir ADdir, dolayisiyla BIR
            # konudur. Hepsini almak cevabi sisiriyor (olculdu: dokuz
            # ogeli zincir 14 bolum uretti; "noether" ogesi tek basina
            # uc konu cekti).
            #
            # Ayrica siradaki adaya GECILMEZ: adi tutan en iyi konu
            # zaten secilmisse oge KAPSANMIS demektir. Olculdu:
            # "Klein-Gordon" ve "Dirac" ogelerinin ikisi de ayni konuda
            # anlatiliyor; ikinciyi siradaki adaya tasiyinca cevaba
            # alakasiz bir konu (Weyl kuantumlamasi) giriyordu.
            yeni = [t for t in adaylar[:1] if t["key"] not in gorulen]
        else:
            yeni = [t for t in adaylar if t["key"] not in gorulen]
        if not yeni:
            # Asamanin bulduklarinin hepsi baska asamaya gitmis:
            # asamayi dusurmeden siradaki adayina bak.
            yeni = [t for t in _adaylar(p, baglam)
                    if t["key"] not in gorulen][:1]
        if not yeni:
            out.append((p, None))
            continue
        for t in yeni:
            gorulen.add(t["key"])
            out.append((p, t))
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
    # AMA ok zinciri kavramsaldir: icindeki rakam bir hesap istegi
    # degil, bir denklemin parcasidir. Olculdu: "δS = 0 → Euler-Lagrange
    # → ..." sorusunda tek basina "0" rakami bu kurala takiliyor ve
    # dokuz asamalik bilesik cevap komple iptal oluyordu.
    if not _ok_zinciri(metin) and re.search(r"\d", metin or ""):
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
