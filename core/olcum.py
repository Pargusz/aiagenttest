# -*- coding: utf-8 -*-
"""Gunluk dilde sorulan sorular dogru formule gidiyor mu?

Kullanici formul adini bilmez; "topun havada ne kadar kaldigi" der.
Bu olcum, formul tabaninin gunluk dil kapsamini sayiyla gosterir ve
her test kosusunda tekrar edilir; boylece kapsam sessizce gerileyemez.
"""
import re

YONLENDIRME_SORULARI = [
 ("topun havada ne kadar kaldigini nasil bulurum", "serbest_dusme egik_h egik_menzil"),
 ("kondansatorun dolmasi ne kadar surer", "rc_zaman"),
 ("kristalde x isini hangi acida yansir", "bragg"),
 ("teleskopum ne kadar kucuk ayrinti secebilir", "rayleigh"),
 ("gazi aniden sikistirinca sicakligi ne olur", "adyabatik"),
 ("donen bir cismi durdurmak icin gereken enerji", "donme_enerji"),
 ("bobinden gecen akim ne kadar surede kararli hale gelir", "rl_zaman"),
 ("roketi dunyadan kurtarmak icin ne kadar hiz gerekir", "kacis_hiz"),
 ("tahta parcasi suda neden yuzuyor", "arsimet"),
 ("yildizin bize uzakligini nasil olcerim", "uzaklik_modulu kadir"),
 ("arabanin fren mesafesi neye bagli", "kin_v2 kinetik"),
 ("asansor kablosu ne kadar gerilim tasir", "newton2 agirlik"),
 ("suyu kaynatmak icin ne kadar enerji gerekir", "isi gizli_isi"),
 ("buzdolabi ne kadar verimli calisir", "sogutma_cop isi_pompasi"),
 ("gitar teli hangi notayi calar", "tel_harmonik"),
 ("iki hoparlor arasinda neden vinlama olur", "vurum"),
 ("gozlugumun numarasi neye gore belirlenir", "mercek mercek_yapimci"),
 ("gunes gozlugu isigi nasil azaltiyor", "malus"),
 ("atom hangi renkte isik yayar", "rydberg bohr_E foton foton_lam"),
 ("radyoaktif madde ne zaman zararsiz hale gelir", "yari_omur bozunma_sabiti aktivite"),
 ("nukleer santral enerjiyi nereden aliyor", "kutle_enerji_mev kutle_kusuru nukleon_basina"),
 ("uydunun dunyaya dusmemesi icin hizi ne olmali", "yorunge_hiz merkezcil"),
 ("borudan gecen su debisi nasil hesaplanir", "sureklilik poiseuille"),
 ("ucak kanadi nasil kaldiriyor", "kaldirma_kuvveti_kanat bernoulli"),
 ("motorun verimi en fazla ne olabilir", "carnot otto_verim"),
 ("elektrik faturasi neye gore artiyor", "elektrik_guc guc"),
 ("trafo gerilimi nasil dusuruyor", "transformator"),
 ("miknatis bobinde neden akim ureti", "faraday"),
 ("metal isitilinca neden uzuyor", "termal_genlesme"),
 ("cam neden isigi buker", "snell"),
 ("uzak galaksiler neden kirmizi gorunuyor", "kirmizi_kayma hubble"),
 ("isik hizina yaklasinca zaman neden yavaslar", "zaman_genlesme"),
 ("elektronun yerini neden tam bilemiyoruz", "belirsizlik"),
 ("gunes ne kadar enerji yayiyor", "stefan ters_kare_isik"),
 ("sicak cisim neden kirmizi sonra beyaz gorunur", "wien stefan_wien_tepe"),
 ("yayin uzamasi ne kadar kuvvet demek", "hooke"),
 ("sarkacin periyodu neye bagli", "sarkac"),
 ("dalgic derinlikte neden basinc hisseder", "hidrostatik"),
 ("yariiletkenin direnci sicaklikla neden degisir", "yariiletken_tasiyici iletkenlik"),
 ("plazmada elektronlar hangi frekansta titrer", "plazma_frekans"),
]


def yonlendirme_puani():
    """Kac soru dogru formule gidiyor? (dogru, toplam) doner."""
    from . import formulas
    dogru = 0
    for soru, beklenen in YONLENDIRME_SORULARI:
        h = formulas.search(soru, limit=1)
        if h and h[0][1]["id"] in beklenen.split():
            dogru += 1
    return dogru, len(YONLENDIRME_SORULARI)


def basarisizlar():
    """Hangi sorular yanlis formule gidiyor?"""
    from . import formulas
    hatali = []
    for soru, beklenen in YONLENDIRME_SORULARI:
        h = formulas.search(soru, limit=1)
        bulunan = h[0][1]["id"] if h else "YOK"
        if bulunan not in beklenen.split():
            hatali.append((soru, bulunan, beklenen))
    return hatali


# ── Ogretim kapsami ─────────────────────────────────────────────────────────
# Bir konu sorusunun cevabi ya DOGRULANMIS malzemeden yapilandirilarak
# uretilir (tanim + baginti + cozumlu ornek + yaygin hata), ya da dil
# modeline kalir. Ikincisinde model baglam inceldiginde hata yapabiliyor
# (olculdu: "isi daima soguk cisimden sicak cisme aktarilir" dedi).
#
# Bu olcum, gunluk Turkce'nin farkli cekim ve kaliplarinda kac sorunun
# yapilandirilmis yola girdigini sayar. Hedef: mumkun oldugunca yuksek.

OGRETIM_SORULARI = [
    # Ayni konu, farkli cekim ve kaliplarda
    "termodinamik anlat",
    "termodinamigin ikinci yasasini anlat",
    "termodinamigin yasalari nelerdir",
    "entropi nedir",
    "entropinin artmasini anlat",
    "entropi neden artar",
    "newton yasalari",
    "newton yasalarini ogret",
    "newton'un ikinci yasasini aciklar misin",
    "kinetik enerji nedir",
    "kinetik enerjiyi anlat",
    "enerjinin korunumunu ogret",
    "snell yasasi",
    "snell yasasini ogret",
    "isigin kirilmasini anlat",
    "ozel gorelilik nedir",
    "gorelilik teorisini anlat",
    "zaman genlesmesini aciklar misin",
    "kuantum mekaniginin temelleri",
    "belirsizlik ilkesini anlat",
    "dalga parcacik ikiligini ogret",
    "elektrik alani nedir",
    "manyetik alani anlat",
    "faraday indukleme yasasini ogret",
    "ohm yasasini anlat",
    "basit harmonik hareketi ogret",
    "sarkac hareketini anlat",
    "doppler etkisini aciklar misin",
    "arsimet ilkesini anlat",
    "bernoulli denklemini ogret",
    "ideal gaz yasasini anlat",
    "carnot cevrimini ogret",
    "fotoelektrik olayi anlat",
    "bohr atom modelini ogret",
    "yari omur nedir",
    "radyoaktif bozunmayi anlat",
    "kutle cekim yasasini ogret",
    "kepler yasalarini anlat",
    "momentum korunumunu ogret",
    "tork nedir nasil hesaplanir",
    # İleri kuram — olculdu: bunlar eskiden "elimde bilgi yok" aliyordu
    "noether teoremini turet",
    "simetri ile korunum arasindaki bag nedir",
    "lagrange mekanigini anlat",
    "hamilton denklemlerini ogret",
    "en kucuk etki ilkesi nedir",
    "alan kuramina giris yap",
    "istatistiksel topluluklari anlat",
    # Kilit deneyler — "bunu deneysel olarak nasil biliyoruz" sorulari
    "stern gerlach deneyi ne gosterdi",
    "elektronun spini deneysel olarak nasil biliniyor",
    "cift yarik deneyini anlat",
    "michelson morley deneyi ne gosterdi",
    "fotoelektrik deneyi neyi kanitladi",
    "millikan yag damlasi deneyi",
    "rutherford sacilma deneyini anlat",
    "bell testleri neyi gosterdi",
    "kutle cekim dalgalari nasil gozlendi",
    "kozmik mikrodalga arka plan nasil bulundu",
    "higgs bozonu nasil kesfedildi",
    # Lisansustu cekirdek
    "maxwell denklemlerini anlat",
    "isik neden elektromanyetik dalgadir",
    "kuantum mekaniginin postulatlari nelerdir",
    "komutator nedir neden onemli",
    "perturbasyon kuramini anlat",
    "bant kuramini ogret",
    "bloch teoremi nedir",
    "standart modeli anlat",
    "temel parcaciklar nelerdir",
    "boyut analizini ogret",
    "hata yayilimi nasil hesaplanir",
    "olcum belirsizligi nedir",
    "fourier analizi fizikte ne ise yarar",
    # Fizikciler: kim, ne yapti, neyi degistirdi
    "einstein kimdir",
    "newton kimdir",
    "emmy noether kim",
    "marie curie ne yapti",
    "feynman kimdir",
    "maxwell kimdir",
    "planck kimdir",
    "niels bohr kimdir",
    # Kimya
    "periyodik tablo neden boyle duzenlenmis",
    "elektron dizilimi nasil yapilir",
    "kimyasal bag turleri nelerdir",
    "aktivasyon enerjisi nedir",
    "katalizor nasil calisir",
    "tepkime hizi neden sicaklikla artar",
    "gibbs serbest enerjisi nedir",
    "kizilotesi spektroskopi nedir",
    "nmr nasil calisir",
    "sera gazi neden isi tutar",
    # Biyoloji / biyofizik
    "aksiyon potansiyeli nedir",
    "zar potansiyeli nasil olusur",
    "nernst denklemi nedir",
    "miyelin neden iletimi hizlandirir",
    "hucre icinde difuzyon nasil calisir",
    "brown hareketi nedir",
    "molekuler motorlar nasil calisir",
    "radyasyonun biyolojik etkisi nedir",
    "sievert ile gray farki nedir",
    "iyonlastirici radyasyon nedir",
    # Gunluk hayattan klasik sorular
    "gokyuzu neden mavi",
    "gun batimi neden kirmizi",
    "bulutlar neden beyaz",
    "buz neden yuzer",
    "gemi neden batmaz",
    "gokkusagi nasil olusur",
    "metal neden soguk hisseder",
    "yuksekte su neden erken kaynar",
    "terlemek neden serinletir",
    # 3-4. sinif cekirdegi. Olculdu: bunlar ya makale kirintisiyla ya da
    # YANLIS konuyla cevaplaniyordu ("born yaklasimi" -> "gokyuzu mavi").
    "ozdes parcaciklar nedir",
    "born yaklasimi nedir",
    "tesir kesiti nedir",
    "kanonik donusumler nedir",
    "poisson parantezi nedir",
    "multipol acilimi nedir",
    "dalga kilavuzu nasil calisir",
    "green fonksiyonu nedir",
    "legendre polinomlari nedir",
    "bessel fonksiyonlari nerede kullanilir",
    "tensor nedir",
    "diverjans teoremi nedir",
    "stokes teoremi nedir",
    "ising modeli nedir",
    "faz gecisi nedir",
    "cekirdek kabuk modeli nedir",
    "sihirli sayilar nedir",
    "yildiz evrimi nasil olur",
    "chandrasekhar siniri nedir",
    "diyot nasil calisir",
    "transistor nasil calisir",
    "islemsel yukseltec nedir",
    "runge kutta yontemi nedir",
    "sayisal yontemlerde kararlilik nedir",
    "statik denge kosullari nelerdir",
    "normal modlar nedir",
    "poisson denklemi nedir",
    "dipol isimasi nedir",
    "varyasyonel yontem nedir",
    "maxwell boltzmann hiz dagilimi nedir",
    "laplace donusumu nedir",
    "bravais orgusu nedir",
    "fonon nedir",
    "yariiletkenlerde katkilama nedir",
    "kirmiziya kayma nedir",
    "osiloskopta tetikleme nedir",
    "en kucuk kareler yontemi nedir",
    "plazma fizigi nedir",
    "kaos kurami nedir",
    "kara cisim isinimi nedir",
]


def ogretim_puani():
    """Kac soru yapilandirilmis ders cevabi aliyor? (dogru, toplam)"""
    from . import ogretim
    yapili = 0
    for soru in OGRETIM_SORULARI:
        try:
            d = ogretim.ders_ver(soru, "tr")
        except Exception:
            d = None
        if d and any(im in d for im in ("Çözümlü örnek", "Sık yapılan hata",
                                        "Hangi bağıntıyla")):
            yapili += 1
    return yapili, len(OGRETIM_SORULARI)


def ogretim_bosluklari():
    """Hangi sorular yapilandirilmis cevap alamiyor?"""
    from . import ogretim
    eksik = []
    for soru in OGRETIM_SORULARI:
        try:
            d = ogretim.ders_ver(soru, "tr")
        except Exception:
            d = None
        if not (d and any(im in d for im in ("Çözümlü örnek", "Sık yapılan hata",
                                             "Hangi bağıntıyla"))):
            eksik.append(soru)
    return eksik


# ── Turkce sorgunun Ingilizce korpusa erisimi ───────────────────────────────
# Korpusun yaklasik %80'i Ingilizce. Turkce sorulan sorular bulgulara hic
# ulasamiyordu (olculdu: 8 sorudan 2'si). Ceviri koprusu bunu duzeltti;
# bu olcum geriye dusmeyi engeller.

TURKCE_ERISIM_SORULARI = [
    "kuantum dolanikligi", "superiletkenlik", "topolojik yalitkan",
    "plazma frekansi", "kara delik", "entropi", "kirilma indisi",
    "karanlik madde", "higgs bozonu", "faz gecisi",
]


def turkce_erisim_puani():
    """Kac Turkce sorgu korpustan bulgu getirebiliyor? (dogru, toplam)"""
    from . import retrieval
    dogru = 0
    for q in TURKCE_ERISIM_SORULARI:
        try:
            if retrieval.insights(q, limit=3):
                dogru += 1
        except Exception:
            pass
    return dogru, len(TURKCE_ERISIM_SORULARI)


def turkce_erisim_bosluklari():
    from . import retrieval
    return [q for q in TURKCE_ERISIM_SORULARI
            if not retrieval.insights(q, limit=3)]


# ── Sadece ADIYLA erisim ────────────────────────────────────────────────────
# Kullanicinin olcutu: "bir universite ogrencisi hic zorlanmadan, sembol
# kullanmadan bile SADECE ADINI vererek dogru bilgiyi alabilmeli."
# Bu olcum tam olarak onu sinar: tek kelime ya da iki kelimelik ad,
# soru cumlesi yok, sembol yok.

AD_SORULARI = [
    "entropi", "doppler", "carnot", "lagrange", "hamilton", "noether",
    "kirchhoff", "nernst", "bernoulli", "arşimet", "lorentz", "schrödinger",
    "heisenberg", "maxwell", "fourier", "bohr", "planck", "einstein",
    "feynman", "curie", "aksiyon potansiyeli", "periyodik tablo",
    "arrhenius", "brown hareketi", "sievert", "spektroskopi", "bant kuramı",
    "higgs", "stern gerlach", "michelson morley", "özel görelilik",
    "genel görelilik", "kuantum tünelleme", "termodinamik", "elektromanyetik",
]


def _ad_cevabi_yeterli(metin):
    if not metin or len(metin) < 380:
        return False
    d = metin.lower()
    return not any(x in d for x in ("bilgim yok", "yeterli bilgi",
                                    "no verified information"))


# ── Ingilizce erisim ────────────────────────────────────────────────────────
# ODTU basta olmak uzere birçok bolum fizigi INGILIZCE okutur; ogrenci
# ders notundaki terimle sorar. Olculdu: "black-body radiation" sorusu
# "Radyasyonun Biyolojik Etkisi" konusuna, "Bose-Einstein condensation"
# ise "Kutle-enerji esdegerligi" formulune gidiyordu.

INGILIZCE_SORULAR = [
    ("what is special relativity", "Relativity"),
    ("explain the Born approximation", "Born"),
    ("what are canonical transformations", "Canonical"),
    ("black-body radiation", "Blackbody"),
    ("ultraviolet catastrophe", "Blackbody"),
    ("Bose-Einstein condensation", "Statistical"),
    ("Lorentz transformation", "Relativity"),
    ("density of states", "Statistical"),
    ("how does a p-n junction work", "Semiconductor"),
    ("Hamilton's equations", "Hamiltonian"),
    ("identical particles and Pauli exclusion", "Identical"),
    ("what is the Ising model", "Ising"),
    ("shell model of the nucleus", "Nuclear"),
    ("what is the Chandrasekhar limit", "Stellar"),
    ("Green's functions", "Green"),
    ("the Runge-Kutta method", "Numerical"),
    ("waveguide cutoff frequency", "Waveguide"),
    ("Maxwell-Boltzmann distribution", "Maxwell-Boltzmann"),
]


def ingilizce_puani():
    """Ingilizce ders terimleri dogru konuya gidiyor mu? (dogru, toplam)"""
    from . import brain
    dogru = 0
    for soru, beklenen in INGILIZCE_SORULAR:
        try:
            t = brain.respond(soru, session="_olcum_en",
                              lang_override="en").text
        except Exception:
            t = ""
        if beklenen.lower() in (t or "").lower():
            dogru += 1
    return dogru, len(INGILIZCE_SORULAR)


def ingilizce_bosluklari():
    from . import brain
    eksik = []
    for soru, beklenen in INGILIZCE_SORULAR:
        try:
            t = brain.respond(soru, session="_olcum_en",
                              lang_override="en").text
        except Exception:
            t = ""
        if beklenen.lower() not in (t or "").lower():
            ilk = (t or "").split("\n")[0][:44]
            eksik.append((soru, beklenen, ilk))
    return eksik


# ── Cok adimli odev problemleri ─────────────────────────────────────────────
# Kullanicinin birinci onceligi: "odev problemlerini garanti cozsun".
# Olculdu: baslangicta 12 sorudan 5'i cozulebiliyordu ve biri YANLIS
# cevap veriyordu ("R2 = -4 ohm").

ODEV_SORULARI = [
    ("10 m yuksekten birakilan 2 kg cismin yere carparken kinetik "
     "enerjisi nedir", "196"),
    ("2 kg cisim 20 m/s ile yukari atiliyor 3 saniye sonraki kinetik "
     "enerjisi nedir", "88.7"),
    ("12 V kaynaga seri bagli 4 ohm ve 8 ohm direnclerden gecen akim nedir",
     "1 A"),
    ("12 V kaynaga paralel bagli 4 ohm ve 12 ohm devreden gecen toplam akim",
     "4 A"),
    ("1000 kg araba 20 m/s hizdan 5 saniyede duruyor fren kuvveti nedir",
     "4000"),
    ("2 kg kutle 100 N/m yaya bagli 0.1 m cekilip birakiliyor maksimum "
     "hizi nedir", "0.707"),
    ("elektron 200 V ile hizlandirilirsa hizi ne olur", "8.38"),
    ("5 kg cisim 10 m/s hizla giderken kinetik enerjisi nedir", "250"),
    ("650 nm dalga boylu fotonun enerjisi nedir", "3.05"),
    ("2 mol ideal gaz 300 K'de 0.05 m3 hacimde basinci nedir", "9.97"),
    ("500 K ve 300 K arasinda calisan carnot makinesinin verimi nedir",
     "0.4"),
    ("3 mikrofarad ve 6 mikrofarad seri bagli esdeger siga nedir", "2"),
    ("100 m yuksekten birakilan cisim kac saniyede yere duser", "4.5"),
    ("20 m/s ile 30 derece aciyla atilan cismin menzili nedir", "35"),
    ("4 kg kutle 100 N/m yaya bagli periyodu nedir", "1.25"),
    ("12 V pil 3 ohm direncten gecen akim nedir", "4"),
    ("5 ohm ve 10 ohm paralel bagli esdeger direnc nedir", "3.33"),
    ("yari omru 5 yil olan maddenin bozunma sabiti nedir", "4.39"),
]

ODEV_SORULARI_EN = [
    ("a 2 kg mass moving at 3 m/s kinetic energy", "9 J"),
    ("a 1000 kg car decelerates from 20 m/s in 5 s braking force", "4000"),
    ("a ball dropped from 100 m, time to reach the ground", "4.5"),
    ("a ball dropped from 100 m, speed on impact", "44.2"),
    ("efficiency of a Carnot engine between 500 K and 300 K", "0.4"),
]


def _sayisal_cevap(metin):
    """Cevapta gercekten SAYISAL bir sonuc satiri var mi?"""
    import re as _re
    for satir in (metin or "").split("\n"):
        if satir.startswith("## `") and "**" in satir:
            return satir
    return ""


def odev_puani(lang="tr"):
    """Kac odev problemi SAYIYLA cevaplaniyor? (dogru, toplam)"""
    from . import brain
    sorular = ODEV_SORULARI if lang == "tr" else ODEV_SORULARI_EN
    dogru = 0
    for i, (soru, beklenen) in enumerate(sorular):
        try:
            t = brain.respond(soru, session="_olcum_odev%d" % i,
                              lang_override=lang).text
        except Exception:
            t = ""
        satir = _sayisal_cevap(t)
        if satir and beklenen.split(" ")[0].split(".")[0] in satir:
            dogru += 1
    return dogru, len(sorular)


def odev_bosluklari(lang="tr"):
    from . import brain
    sorular = ODEV_SORULARI if lang == "tr" else ODEV_SORULARI_EN
    eksik = []
    for i, (soru, beklenen) in enumerate(sorular):
        try:
            t = brain.respond(soru, session="_olcum_odev%d" % i,
                              lang_override=lang).text
        except Exception:
            t = ""
        satir = _sayisal_cevap(t)
        if not (satir and beklenen.split(" ")[0].split(".")[0] in satir):
            eksik.append((soru[:50], beklenen, satir[:30] or "(hesap yok)"))
    return eksik


# ── Tuzak sorular: kandirilmadan cozme ─────────────────────────────────────
# Kullanicinin sozleri: "hic zorlanmadan dogru cevaplar ile KANDIRILMADAN
# problem cozebilmesi lazim". Bu olcum tam da onu sinar: her soruda
# ogrenciyi (ve sistemi) yaniltacak bir tuzak var.

TUZAK_SORULARI = [
    # (soru, cevapta gecmesi gereken)
    ("1 kg + 30 metre + 22 cm kac eder", "yapılamaz"),
    ("30 m + 22 cm kac eder", "30.22"),
    ("5 J + 3 N kac eder", "yapılamaz"),
    # Oncul cevabi veriyor: surtunmesiz ortamda surtunme sifirdir
    ("surtunmesiz alanda 30 m yari capli basit harmonik hareket yapan "
     "bir hareketlinin periyodu 10 sny bu hareketlinin V si en yuksek "
     "oldugu noktadaki surtunme degerini hesapla", "0 N"),
    ("hava direnci ihmal edilen ortamda dusen cisme etkiyen hava "
     "direnci kuvveti nedir", "0 N"),
    ("sabit hizla giden arabanin ivmesi nedir", "0"),
    # Dogru fizik: BHH maksimum hizi
    ("30 m genlikli basit harmonik hareket periyodu 10 s maksimum hizi",
     "18.85"),
    ("2 m genlikli, periyodu 4 s olan harmonik hareketin maksimum hizi",
     "3.14"),
    # Fiziksel olmayan girdi sessizce kabul edilmemeli
    ("-5 kg kutleli cismin kinetik enerjisi 10 m/s hizda", "fiziksel değil"),
    ("-100 K sicaklikta 2 mol gazin 0.05 m3 hacimde basinci",
     "fiziksel değil"),
    # Sorulan buyuklugun birimi dogru olmali
    ("sabit hizla giden trenin uzerindeki net kuvvet nedir", "0 N"),
    ("dengede duran cismin ivmesi nedir", "0 m/s^2"),
    # Verilen ile sorulan karismamali
    ("kutlesi 5 kg olan cismin agirligi kac newton", "49"),
    # Yaricap bir yer degistirme degildir
    ("yaricapi 0.5 m periyodu 2 s dairesel hareket cizgisel hizi", "1.57"),
    ("yalitilmis sistemde disariya verilen isi kac joule", "0 J"),
    ("kutlesi 2 kg hizi 5 m/s olan cismin momentumu nedir", "10"),
    ("10 kg + 5 saniye kac eder", "yapılamaz"),
    ("3 saat kac saniye eder", "10800"),
]


def tuzak_puani():
    """Kac tuzak soru dogru cevaplaniyor? (dogru, toplam)"""
    from . import brain
    dogru = 0
    for i, (soru, beklenen) in enumerate(TUZAK_SORULARI):
        try:
            t = brain.respond(soru, session="_olcum_tuzak%d" % i).text
        except Exception:
            t = ""
        if beklenen.lower() in (t or "").lower():
            dogru += 1
    return dogru, len(TUZAK_SORULARI)


def tuzak_bosluklari():
    from . import brain
    eksik = []
    for i, (soru, beklenen) in enumerate(TUZAK_SORULARI):
        try:
            t = brain.respond(soru, session="_olcum_tuzak%d" % i).text
        except Exception:
            t = ""
        if beklenen.lower() not in (t or "").lower():
            eksik.append((soru[:52], beklenen,
                          (t or "").split("\n")[0][:40]))
    return eksik


# ── Problem korpusu ve ogrenilen semalar ───────────────────────────────────
# Kullanicinin istegi: "cozulmus problemlerden beslenip hic gormedigi
# sorulari da cozebilsin". Bunun olcusu iki sayidir:
#   * korpusa giren problem sayisi (ne kadar malzeme gordu)
#   * ogrenilen SEMA sayisi (kac farkli cozum yolunu tanidi)
# Semalar sayilardan bagimsizdir; bu yuzden yeni bir soruda ise yararlar.

def problem_durumu():
    """(problem_sayisi, sema_sayisi, sema_kaniti) doner."""
    from . import db
    try:
        c = db.conn()
        p = c.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
        s = c.execute("SELECT COUNT(*) FROM semalar").fetchone()[0]
        k = c.execute("SELECT COALESCE(SUM(kanit),0) FROM semalar"
                      ).fetchone()[0]
        return p, s, k
    except Exception:
        return 0, 0, 0


# ── Soruyu BUTUN olarak okuma olcumu ──────────────────────────────────────
# Olculdu (canli sohbet): "klasik kinetik enerji formulunden cikarak
# Hamiltonyan operatorunun kinetik enerji kismini ispatlar misin" sorusuna
# cumleden yalnizca "kinetik enerji" cekilip `Ek = mv²/2` karti donuyordu.
# Soruda IKI kavram ve aralarindaki GECIS isteniyordu.
#
# Bu olcum, cevabin sorunun HER IKI ucuna da deginip degmedigini sinar.
# Her satir: (soru, [A ucundan izler], [B ucundan izler]). Cevapta her iki
# listeden de en az bir iz bulunmalidir. Tek uca deginen cevap — ne kadar
# dogru olursa olsun — soruyu parca okumus demektir ve basarisiz sayilir.
KOPRU_SORULARI = [
    ("klasik fizik kinetik enerji formulunden cikarak schrodingerin "
     "denklemindeki hamiltonyan operatorunun kinetik enerji kismini "
     "ispatlar misin",
     ["p²/2m", "mv²", "½mv", "klasik"],
     ["p̂", "−iħ", "-iħ", "∇²", "operat"]),
    ("klasik fizikteki kinetik enerji ile kuantumdaki kinetik enerji "
     "operatoru arasindaki gecisi acikla",
     ["p²/2m", "mv²", "klasik"],
     ["p̂", "−iħ", "∇²", "kuantumlama"]),
    ("klasik mekanikten kuantum mekanigine nasil gecilir",
     ["klasik"], ["kuantumlama", "p̂", "−iħ", "∇²"]),
    ("momentum operatoru nereden geliyor",
     ["de Broglie", "duzlem dalga", "düzlem dalga", "ψ"],
     ["p̂", "−iħ", "-iħ"]),
    ("hamiltonyen operatorunun kinetik enerji kismi nasil elde edilir",
     ["p²/2m", "klasik", "Hamilton"], ["∇²", "p̂", "−iħ"]),
    ("kuantum etkilerini neden gunluk hayatta gormuyoruz",
     ["de Broglie", "λ", "kucuk", "küçük"],
     ["Ehrenfest", "klasik", "limit"]),
    ("newton mekanigi ile ozel gorelilik arasindaki iliski nedir",
     ["mv", "Newton", "klasik"], ["γ", "mc²", "goreli", "göreli"]),
    ("klasik momentum ile goreli momentum arasindaki iliski nedir",
     ["mv"], ["γ", "goreli", "göreli"]),
    ("lagrange ile hamilton formalizmi arasindaki gecis nasil olur",
     ["L", "Lagrange", "q̇"], ["Legendre", "∂L/∂q̇", "Hamilton"]),
    ("eslenik momentum nedir hamiltonyen nasil elde edilir",
     ["∂L/∂q̇", "eslenik", "eşlenik", "Lagrange"],
     ["Legendre", "Hamilton"]),
    ("elektrik alan ile manyetik alan arasindaki baglanti nedir",
     ["elektrik", "E"], ["manyetik", "B", "Maxwell"]),
    ("schrodinger denklemi nereden geliyor",
     ["de Broglie", "klasik", "p²/2m"],
     ["Schrödinger", "Schrodinger", "Ĥ", "∇²"]),
    ("ozel gorelilikte enerji ifadesinden klasik kinetik enerjiyi turet",
     ["γmc²", "γ", "goreli", "göreli"], ["mv²", "½mv", "klasik"]),
    ("poisson parantezi ile komutator arasindaki iliski nedir",
     ["Poisson", "{A,B}", "{q,p}"], ["iħ", "komut", "[Â", "[q̂"]),
]



# ── ZOR PROBLEM SETI ──────────────────────────────────────────────────────
# Kullanicinin hedefi: *"fizik alaninin Claude'u ... zor denilen sorulari
# bile rahatca cozebilmeli"*. Mevcut setleri (sayisal 39/39, odev 18/18)
# sistem zaten cozuyor; bu set farkli. Her problem ya cok adimli, ya dogru
# ILKEYI secmeyi gerektiriyor, ya da kurulusu gizli.
#
# Ilk olcum: 2/20. Bu sayi durustce buradadir ve yukselmesi gereken sayidir.
# Her satirin cevabi elle hesaplanip dogrulandi.
ZOR_PROBLEMLER = [
    # 1. Egik duzlem + surtunme + enerji (cok adimli, acili)
    ("30 derece egimli surtunme katsayisi 0.2 olan duzlemde 4 kg kutle "
     "durgun halden 5 m kayarsa sondaki hizi nedir", "5.66",
     # Beklenen deger "6.35" yaziliyordu ama ayni satirdaki hesap 5,66
     # veriyor: a = 9,8(sin30 - 0,2cos30) = 3,203 ve v = sqrt(2·3,203·5)
     # = 5,66 m/s. Sistem 5,661 diyordu ve olcum bunu YANLIS sayiyordu.
     "a = g(sin30 - 0.2cos30) = 3.203; v = sqrt(2*3.203*5) = 5.66"),

    # 2. Tam esnek olmayan carpisma: momentum korunur, enerji korunmaz (tuzak)
    ("3 kg cisim 4 m/s ile duran 5 kg cisme carpip birlikte hareket "
     "ederse ortak hizlari nedir", "1.5", "p: 3*4=(3+5)v -> v=1.5"),

    # 3. Carpismada kaybolan enerji
    ("3 kg 4 m/s ile duran 5 kg cisme carpip yapisirsa kaybolan kinetik "
     "enerji nedir", "15", "24 - 9 = 15 J"),

    # 4. Donme + oteleme: yuvarlanarak inen silindir
    ("egimden yuvarlanarak inen dolu silindir 2 m yukseklikten "
     "birakilirsa tabandaki hizi nedir", "5.11",
     "v=sqrt(4gh/3)=sqrt(4*9.8*2/3)=5.11"),

    # 5. RC devresi gecici hal
    ("100 mikrofarad kondansator 10 kilo ohm direncle 12 V'a baglanirsa "
     "1 saniye sonra gerilimi nedir", "7.58",
     "tau=1 s; V=12(1-e^-1)=7.58"),

    # 6. Carnot + gercek verim karsilastirma
    ("600 K ve 300 K arasinda calisan Carnot makinesi 1000 J isi alirsa "
     "yaptigi is nedir", "500", "eta=0.5 -> W=500 J"),

    # 7. Doppler: kaynak yaklasiyor
    ("340 m/s ses hizinda 30 m/s ile yaklasan 1000 Hz kaynak icin "
     "duyulan frekans nedir", "1096.8", "f=1000*340/(340-30)=1096.8"),

    # 8. Basit sarkac + kucuk aci
    ("2 m uzunlugundaki sarkacin periyodu nedir", "2.84",
     "T=2pi sqrt(2/9.8)=2.84"),

    # 9. Fotoelektrik: esik asilmasi
    ("is fonksiyonu 2.3 eV olan metale 400 nm isik dusurulurse "
     "firlayan elektronun maksimum kinetik enerjisi nedir", "1.281e-19",
     "E=1240/400=3.1 eV; Ek=0.8 eV = 1.281e-19 J (sistem SI verir)"),

    # 10. Merkezcil + surtunme: virajda maksimum hiz
    ("surtunme katsayisi 0.5 olan 50 m yaricapli virajda maksimum hiz "
     "nedir", "15.65", "v=sqrt(0.5*9.8*50)=15.65"),

    # 11. Ideal gaz: izotermal is
    ("2 mol ideal gaz 300 K'de hacmi iki katina izotermal genlesirse "
     "yaptigi is nedir", "3457",
     "W=nRT ln2 = 2*8.314*300*0.693=3457 J"),

    # 12. Zaman genlesmesi
    ("0.8c hizla giden saatte 1 saniye gecerse duran gozlemcide "
     "ne kadar gecer", "1.67", "gamma=1/0.6=1.667"),

    # 13. Manyetik alanda yuk: yaricap
    ("0.5 T alanda 2e6 m/s hizla giren elektronun yorunge yaricapi nedir",
     "2.27e-5", "r=mv/(qB)=9.11e-31*2e6/(1.6e-19*0.5)=2.28e-5 m"),

    # 14. Girisim: cift yarik
    ("0.1 mm aralikli cift yarikta 600 nm isikla 2 m uzaktaki perdede "
     "sacak araligi nedir", "0.012", "dy=lam*L/d=600e-9*2/1e-4=0.012 m"),

    # 15. Kalorimetre: buz eritme + isitma
    ("0 derecede 0.5 kg buzu eritip 20 dereceye getirmek icin gereken "
     "isi nedir", "208900",
     "0.5*334000 + 0.5*4186*20 = 167000+41860=208860 J"),

    # 16. Kacis hizi (Dunya)
    # DIKKAT: beklenen deger SI biriminde yazilmali. Ilk hâli "11.2"
    # (km/s) idi; sistem dogru cevabi 11190 m/s olarak veriyordu ve
    # olcum bunu YANLIS sayiyordu — olcum hatasi, sistem hatasi degil.
    ("dunyadan kacis hizi nedir", "11190",
     "sqrt(2GM/R) = 1.119e4 m/s = 11.2 km/s"),

    # 17. Bohr: n=2 -> n=1 gecis enerjisi
    ("hidrojen atomunda n=2 den n=1 e gecerken yayilan fotonun enerjisi "
     "nedir", "1.634e-18", "13.6(1-1/4)=10.2 eV = 1.634e-18 J"),

    # 18. Yay + enerji korunumu (maksimum sikisma)
    ("2 kg cisim 3 m/s ile 200 N/m yaya carparsa maksimum sikisma nedir",
     "0.3", "x=v sqrt(m/k)=3*sqrt(2/200)=0.3 m"),

    # 19. Atwood makinesi (iki kutle, makara)
    ("makaradan gecen ipin uclarindaki 3 kg ve 5 kg kutlelerin ivmesi "
     "nedir", "2.45", "a=(5-3)*9.8/8=2.45"),

    # 20. Ohm + guc: direncte harcanan
    ("12 V kaynaga bagli 4 ohm direncte harcanan guc nedir", "36",
     "P=V^2/R=144/4=36 W"),
]


def _zor_eslesti(metin, beklenen, tol=0.02):
    """Cevapta beklenen SAYI var mi? Metin degil, SAYI karsilastirilir.

    Olculdu: sarkac sorusuna sistem `T = 2.837 s` demisti — dogru cevap.
    Ama olcum "2.84" dizgisini aradigi icin bunu YANLIS saymisti. Yuzde
    iki toleransli sayisal karsilastirma, yuvarlama farkindan dogan sahte
    basarisizliklari kaldirir.
    """
    try:
        hedef = float(beklenen)
    except Exception:
        return beklenen in (metin or "")
    # Bilimsel gosterim dahil tum sayilari topla (10^ ve ×10^ bicimleri de)
    duz = (metin or "").replace("×10^", "e").replace("·10^", "e")
    duz = duz.replace("10^", "1e").replace(",", "")
    for parca in re.findall(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", duz):
        try:
            deger = float(parca)
        except Exception:
            continue
        if hedef == 0:
            if abs(deger) < 1e-12:
                return True
            continue
        if abs(deger - hedef) <= abs(hedef) * tol:
            return True
    return False


def zor_puani():
    """Zor problemlerin kaci sayiyla dogru cevaplaniyor? (dogru, toplam)"""
    from . import brain
    dogru = 0
    for i, (soru, beklenen, _aciklama) in enumerate(ZOR_PROBLEMLER):
        try:
            t = brain.respond(soru, session="_olcum_zor%d" % i).text or ""
        except Exception:
            t = ""
        if _zor_eslesti(t, beklenen):
            dogru += 1
    return dogru, len(ZOR_PROBLEMLER)


def zor_bosluklari():
    """Hangi zor problemler cozulemiyor ve nereye gidiyor?"""
    from . import brain
    eksik = []
    for i, (soru, beklenen, _a) in enumerate(ZOR_PROBLEMLER):
        try:
            t = brain.respond(soru, session="_olcum_zor%d" % i).text or ""
        except Exception:
            t = ""
        if _zor_eslesti(t, beklenen):
            continue
        bas = [x for x in t.split("\n") if x.startswith("#")]
        eksik.append((soru[:50], beklenen,
                      bas[0][:38] if bas else "(hesap yok)"))
    return eksik



# ── KURAMSAL TURETIM OLCUMU ───────────────────────────────────────────────
# Kullanicinin verdigi 20 zor kuramsal soru (ispat/turetme). Sayisal
# problem DEGILLER; olcut de farkli: cevabin konuyu ANMASI yetmez,
# turetimin kilit adimlarini icermesi gerekir. Her satirda iki iz grubu
# var — baslangic noktasi ve turetimin sonucu — ikisi de bulunmalidir.
#
# Ilk olcum 2/20 idi. Icerik yazildikca ve yonlendirme duzeldikce yukseldi.
KURAMSAL_SORULAR = [
 ("Klasik fizik kinetik enerji formülünden başlayarak Schrödinger denklemindeki "
  "Hamiltonyen operatörünün kinetik enerji terimini matematiksel olarak türetir "
  "misin? Geçişte neden momentumun operatöre dönüştüğünü ve neden ikinci türev "
  "çıktığını ayrıntılı olarak açıkla.",
  ["p²/2m", "mv²", "½mv"], ["−iħ", "-iħ", "∇²", "p̂"]),

 ("Klasik mekanikte Newton'un ikinci yasasından başlayarak Lagrange denklemlerini, "
  "ardından Euler-Lagrange denklemini matematiksel olarak ispatla. Daha sonra bu "
  "formülün Hamilton formalizmine nasıl dönüştüğünü tüm ara adımlarla göster.",
  ["L = T", "Euler-Lagrange", "∂L/∂q"], ["Legendre", "H = Σ p", "∂H/∂p"]),

 ("Hamiltonyen formalizminden başlayarak zaman-bağımlı Schrödinger denklemini "
  "yalnızca matematiksel varsayımlar kullanarak türet. Planck sabitinin neden "
  "ortaya çıktığını ve dalga fonksiyonunun neden kompleks olmak zorunda olduğunu "
  "açıkla.",
  ["Ĥ", "Hamilton"], ["iħ ∂", "iħ∂", "iħ ∂ψ/∂t", "kompleks"]),

 ("Klasik momentum tanımı p=mv ile de Broglie'nin p=ℏk ilişkisi arasındaki "
  "bağlantıyı matematiksel olarak ispatla. Ardından bu bağıntının Schrödinger "
  "denklemine nasıl dönüştüğünü adım adım göster.",
  ["de Broglie", "p = ħk", "ħk"], ["λ = h", "e^(i(kx", "ψ"]),

 ("Dalga fonksiyonunun Born olasılık yorumuna neden ihtiyaç duyulduğunu "
  "matematiksel olarak açıkla. |ψ|² 'nin neden olasılık yoğunluğu olduğunu "
  "normlama koşulu üzerinden ispatla.",
  ["Born", "|ψ|²"], ["normla", "∫", "= 1"]),

 ("Schrödinger denkleminden başlayarak olasılık akımı denklemini türet. "
  "Süreklilik denkleminin nasıl elde edildiğini ve bunun yük korunumu ile "
  "benzerliğini ayrıntılı şekilde açıkla.",
  ["olasılık akım", "j ="], ["süreklilik", "∂ρ/∂t", "∇·j"]),

 ("Komütatör tanımından başlayarak [x, p̂]=iℏ bağıntısını matematiksel olarak "
  "ispatla. Daha sonra bu bağıntıdan Heisenberg Belirsizlik İlkesini "
  "Cauchy-Schwarz eşitsizliği kullanarak türet.",
  ["[x", "komütat", "iħ"], ["Cauchy", "belirsizlik", "ħ/2"]),

 ("Fourier dönüşümünü kullanarak konum uzayındaki dalga fonksiyonu ile momentum "
  "uzayındaki dalga fonksiyonu arasındaki dönüşümü matematiksel olarak ispatla. "
  "Bu dönüşümün fiziksel anlamını ayrıntılı açıkla.",
  ["Fourier"], ["φ(p)", "momentum uzay", "e^(-ipx"]),

 ("Kuantum mekaniğinde Hermit operatör kavramını matematiksel olarak tanımla. "
  "Gözlenebilir büyüklüklerin neden Hermit operatörlerle temsil edilmek zorunda "
  "olduğunu özdeğerlerin reel olması üzerinden ispatla.",
  ["Hermit"], ["özdeğer", "reel", "gerçel"]),

 ("Schrödinger denkleminden başlayarak serbest parçacık çözümünü elde et. Daha "
  "sonra bu çözümden grup hızı ve faz hızını hesapla. Grup hızının klasik parçacık "
  "hızına neden eşit olduğunu matematiksel olarak göster.",
  ["serbest parçacık", "e^(ikx"], ["grup hızı", "dω/dk", "faz hızı"]),

 ("Varyasyon hesabını kullanarak Euler-Lagrange denklemini sıfırdan türet. Daha "
  "sonra bu yöntemin Fermat'ın En Az Zaman İlkesi ile ilişkisini matematiksel "
  "olarak açıkla.",
  ["varyasyon", "δS", "δ∫"], ["Euler-Lagrange", "Fermat"]),

 ("Dirac gösterimini (|ψ⟩, ⟨ψ|) sıfırdan tanıt. İç çarpım, dış çarpım ve operatör "
  "kavramlarının matris gösterimine nasıl dönüştüğünü örneklerle matematiksel "
  "olarak göster.",
  ["ket", "|ψ⟩", "Dirac"], ["iç çarpım", "⟨ψ|", "matris"]),

 ("Klasik harmonik osilatör denklemini çöz. Daha sonra aynı sistemi kuantum "
  "mekaniğinde çözerek yaratma (a†) ve yok etme (a) operatörlerini türet. Enerji "
  "seviyelerinin neden ayrık olduğunu matematiksel olarak ispatla.",
  ["harmonik osilatör", "ω"], ["yaratma", "a†", "n + 1/2", "ayrık"]),

 ("Noether Teoremini varyasyon hesabından başlayarak matematiksel olarak ispatla. "
  "Zaman simetrisinin enerji korunumu, uzay simetrisinin momentum korunumu ve "
  "dönme simetrisinin açısal momentum korunumu ile ilişkisini ayrıntılı olarak "
  "göster.",
  ["Noether", "simetri"], ["enerji korunum", "momentum korunum", "açısal momentum"]),

 ("Schrödinger denklemini relativistik hale getirmeye çalışırken neden başarısız "
  "olunduğunu matematiksel olarak açıkla. Daha sonra Klein-Gordon ve Dirac "
  "denklemlerinin hangi matematiksel ihtiyaçlardan doğduğunu ayrıntılı olarak "
  "türet.",
  ["Klein-Gordon", "relativistik"], ["Dirac denklem", "negatif", "birinci mertebe"]),

 ("Elektromanyetik alan altında Schrödinger denklemindeki minimal bağlaşım "
  "dönüşümünü p→p−qA matematiksel olarak türet. Bunun gauge dönüşümleriyle "
  "ilişkisini ayrıntılı açıkla.",
  ["minimal", "p − qA", "p-qA", "qA"], ["gauge", "ayar"]),

 ("Feynman Yol İntegrali formülasyonunu klasik En Az Etki İlkesi'nden başlayarak "
  "sezgisel ve matematiksel olarak türet. Yol integrali ile Schrödinger "
  "denkleminin neden eşdeğer olduğunu açıkla.",
  ["yol integral", "Feynman"], ["e^(iS/ħ)", "etki", "S/ħ"]),

 ("Spin kavramının klasik açısal momentumdan neden türetilemeyeceğini matematiksel "
  "olarak göster. Pauli matrislerini kullanarak spin-1/2 operatörlerinin SU(2) "
  "cebrini sağladığını ispatla.",
  ["spin"], ["Pauli", "SU(2)", "σ"]),

 ("Kanonik kuantizasyon yöntemini klasik Poisson parantezlerinden başlayarak "
  "türet. Poisson parantezlerinin neden komütatörlere dönüştüğünü matematiksel "
  "olarak açıkla ve örneklerle göster.",
  ["Poisson"], ["komütat", "iħ", "{A,B}"]),

 ("Schrödinger denkleminin çözümünden başlayarak WKB yaklaşımını türet. "
  "Yaklaşımın hangi varsayımlar altında geçerli olduğunu ve klasik sınır (ℏ→0) "
  "ile bağlantısını ayrıntılı olarak açıkla.",
  ["WKB"], ["e^(iS/ħ)", "ħ→0", "Hamilton-Jacobi", "klasik limit"]),
]


def kuramsal_puani():
    """Kac kuramsal turetim, iki uca da degerek cevaplaniyor?"""
    from . import brain
    dogru = 0
    for i, (soru, a, b) in enumerate(KURAMSAL_SORULAR):
        try:
            t = brain.respond(soru, session="_olcum_kuram%d" % i).text or ""
        except Exception:
            t = ""
        if any(x.lower() in t.lower() for x in a) and \
                any(x.lower() in t.lower() for x in b):
            dogru += 1
    return dogru, len(KURAMSAL_SORULAR)


def kuramsal_bosluklari():
    from . import brain
    eksik = []
    for i, (soru, a, b) in enumerate(KURAMSAL_SORULAR):
        try:
            t = brain.respond(soru, session="_olcum_kuram%d" % i).text or ""
        except Exception:
            t = ""
        va = any(x.lower() in t.lower() for x in a)
        vb = any(x.lower() in t.lower() for x in b)
        if va and vb:
            continue
        bas = [x for x in t.split("\n") if x.startswith("#")]
        eksik.append((soru[:46], "A" if not va else "B",
                      bas[0][:36] if bas else "(bos)"))
    return eksik


# ── GENELLEME OLCUMU ──────────────────────────────────────────────────────
# Kullanicinin sorusu: "hic eklemedigimiz bu seviyede zor bir soruyu
# dogru bilebilecek mi?" Cevap tahminle degil SAYIYLA verilmeli.
#
# Iki grup:
#   A) VARYANT — yazilmis bir turetimin farkli ifade edilmis hâli.
#      Aramanin ve dil katmaninin saglamligini olcer.
#   B) YENI — sete hic konmamis, cekirdekte yazili OLMAYAN turetimler.
#      Gercek genellemeyi olcer. Burada yuksek puan ancak TURETIM
#      MOTORU hesaplayabiliyorsa gelir (bkz. turetimmotor.py).
#
# Ilk olcum: A 2/6, B 0/6. Motor kurulduktan sonra B'de viryal teoremi
# HESAPLANARAK cozuldu.

GENELLEME_VARYANT = [
 ("Bir gozlenebilirin operatorunun neden kendine es olmasi gerektigini, "
  "olcum sonuclarinin gercel olmasi sartindan yola cikarak goster.",
  ["Hermit", "kendine es"], ["gercel", "reel", "a = a*"]),
 ("Bir dalga paketinin zarfinin hangi hizla ilerledigini hesapla ve bunun "
  "parcacigin klasik hiziyla ayni oldugunu kanitla.",
  ["grup", "dω/dk", "zarf"], ["p/m", "klasik", "dE/dp"]),
 ("Yuklu bir parcacigin denklemine manyetik alani sokmanin en az varsayimli "
  "yolunu ve bunun faz serbestligiyle iliskisini acikla.",
  ["qA", "minimal"], ["gauge", "ayar", "faz"]),
 ("Titresen bir sistemin enerjisinin neden surekli olamayacagini, yukseltme "
  "ve alcaltma islemcileri kurarak goster.",
  ["â†", "yaratma", "merdiven"], ["ħω(n", "n + ½", "ayrık", "ayrik"]),
 ("Bir parcacigin bulunma olasiliginin zamanla korundugunu, bir akim "
  "tanimlayarak ispatla.",
  ["akım", "j ="], ["süreklilik", "∇·j", "korun"]),
 ("Iki islemci ayni anda keskin olcelemiyorsa aralarindaki bagintinin ne "
  "oldugunu ve bundan cikan alt siniri turet.",
  ["komütat", "[Â", "[x"], ["ħ/2", "Cauchy", "ΔA"]),
]

GENELLEME_YENI = [
 ("Ehrenfest teoremini ispatla: beklenen degerlerin klasik hareket "
  "denklemlerine uydugunu matematiksel olarak goster.",
  ["Ehrenfest"], ["d⟨x̂⟩/dt", "d⟨p̂⟩/dt", "⟨p̂⟩/m"]),
 ("Viryal teoremini kuantum mekaniginde ispatla: duragan durumda "
  "2⟨T⟩ = ⟨x dV/dx⟩ oldugunu goster.",
  ["Viryal", "x̂p̂"], ["2⟨T̂⟩", "dV/dx"]),
 ("Acisal momentum bilesenlerinin komutator cebrini hesaplayarak turet.",
  ["L̂x", "acisal momentum"], ["iħ L̂z", "iħL̂z"]),
 ("L kare ile Lz nin ayni anda olculebilir olup olmadigini komutator "
  "hesaplayarak goster.",
  ["L̂²"], ["= 0", "ayni anda", "aynı anda"]),
 ("Periyodik potansiyelde Bloch teoremini ispatla: dalga fonksiyonunun "
  "neden e^(ikr)·u(r) biciminde olmak zorunda oldugunu goster.",
  ["Bloch"], ["e^(ik", "periyodik", "u(r)"]),
 ("Fermi altin kuralini zamana bagli perturbasyon kuramindan turet.",
  ["Fermi", "altın kural"], ["geçiş hızı", "durum yoğunluğu", "2π/ħ"]),
]


def _genelleme_puan(liste, etiket):
    from . import brain
    tam = 0
    for i, (soru, a, b) in enumerate(liste):
        try:
            t = brain.respond(soru, session="_gen_%s%d" % (etiket, i)).text or ""
        except Exception:
            t = ""
        if any(x.lower() in t.lower() for x in a) and \
                any(x.lower() in t.lower() for x in b):
            tam += 1
    return tam, len(liste)


def genelleme_varyant_puani():
    """Yazilmis turetimin BASKA IFADESI kac soruda tutuyor?"""
    return _genelleme_puan(GENELLEME_VARYANT, "v")


def genelleme_yeni_puani():
    """HIC YAZILMAMIS turetimlerin kaci cozuluyor? (gercek genelleme)"""
    return _genelleme_puan(GENELLEME_YENI, "y")


# ── Kendi kendine ogrenme olcumu ──────────────────────────────────────────
# Kullanicinin istegi: *"sürekli bizim bir şeyi geliştirmemiz gerekmesin ...
# benzer ve yine zor olan soruları kendi kendine öğrensin"*.
#
# Bu olcum, sistemin ELLE YAZILMADAN kac bagi kendi cikardigini ve kendi
# urettigi zor sorularin kacinda iki uca birden degdigini gosterir. Sayilar
# korpus buyudukce artmali; azalirsa bir gerileme var demektir.

def ogrenme_durumu():
    """(ogrenilmis_kopru, acik_hedef, son_sinav) doner."""
    from . import kopruogren
    return kopruogren.durum()


def kendi_sinavi(adet=6):
    """Sistemin kendi uretip kendi cevapladigi zor sorular. (dogru, toplam)"""
    from . import kopruogren
    return kopruogren.sinav(adet=adet, kaydet=False)


def kopru_puani():
    """Kac kopru sorusu HER IKI uca da degiyor? (dogru, toplam)"""
    from . import brain
    dogru = 0
    for i, (soru, a, b) in enumerate(KOPRU_SORULARI):
        try:
            t = brain.respond(soru, session="_olcum_kopru%d" % i).text or ""
        except Exception:
            t = ""
        if any(x in t for x in a) and any(x in t for x in b):
            dogru += 1
    return dogru, len(KOPRU_SORULARI)


def kopru_bosluklari():
    from . import brain
    eksik = []
    for i, (soru, a, b) in enumerate(KOPRU_SORULARI):
        try:
            t = brain.respond(soru, session="_olcum_kopru%d" % i).text or ""
        except Exception:
            t = ""
        va, vb = any(x in t for x in a), any(x in t for x in b)
        if not (va and vb):
            bas = [x for x in t.split("\n") if x.startswith("#")]
            eksik.append((soru[:46],
                          "A" if not va else "B",
                          bas[0][:34] if bas else "(bos)"))
    return eksik


# Ayni SEMAYA uyan ama daha once hic gorulmemis problemler. Sema
# ogrenmenin ise yarayip yaramadigini olcer: sayilar ve kelimeler
# farkli, fizik ayni.
GORULMEMIS_SORULAR = [
    ("15 m yuksekten birakilan 4 kg cismin yere carparken kinetik "
     "enerjisi", "588"),
    ("7 m yuksekten birakilan 3 kg tasin yere carpma kinetik enerjisi",
     "205"),
    ("24 V kaynaga seri bagli 6 ohm ve 6 ohm direncten gecen akim", "2 A"),
    ("18 V kaynaga paralel bagli 6 ohm ve 3 ohm devreden gecen akim",
     "9 A"),
    ("5 m genlikli periyodu 4 s olan harmonik hareketin maksimum hizi",
     "7.85"),
    ("800 kg araba 15 m/s hizdan 3 saniyede duruyor fren kuvveti", "-4000"),
    ("yaricapi 2 m periyodu 8 s dairesel hareketin cizgisel hizi", "1.57"),
    ("proton 300 V ile hizlandirilirsa kazandigi enerji", "4.8"),
]


def gorulmemis_puani():
    """Hic gorulmemis ama ayni fizikteki problemler. (dogru, toplam)"""
    from . import brain
    dogru = 0
    for i, (soru, beklenen) in enumerate(GORULMEMIS_SORULAR):
        try:
            t = brain.respond(soru, session="_olcum_yeni%d" % i).text
        except Exception:
            t = ""
        if beklenen.split(" ")[0].split(".")[0] in (t or ""):
            dogru += 1
    return dogru, len(GORULMEMIS_SORULAR)


def gorulmemis_bosluklari():
    from . import brain
    eksik = []
    for i, (soru, beklenen) in enumerate(GORULMEMIS_SORULAR):
        try:
            t = brain.respond(soru, session="_olcum_yeni%d" % i).text
        except Exception:
            t = ""
        if beklenen.split(" ")[0].split(".")[0] not in (t or ""):
            son = [x for x in (t or "").split("\n") if x.startswith("## ")]
            eksik.append((soru[:48], beklenen,
                          son[0][:26] if son else "(hesap yok)"))
    return eksik


# ── Genis sayisal problem seti ─────────────────────────────────────────────
# Kullanicinin istegi: "her turlu sayisal problemi cozebilsin". Bu olcum
# mufredat boyunca yayilmis, tek ya da cok adimli sayisal problemleri
# sinar. Her biri elle dogrulanmis cevaplarla.

SAYISAL_PROBLEMLER = [
    # Kinematik
    ("20 m/s hizla giden arac 4 s'de 40 m/s'ye cikiyor ivmesi nedir", "5"),
    ("5 m/s2 ivmeyle duran araba 6 s sonra kac m/s olur", "30"),
    ("45 m yuksekten birakilan cisim kac saniyede duser", "3.02"),
    ("20 m/s ile 45 derece aciyla atilan cismin menzili", "40"),
    ("100 m yuksekten birakilan cismin yere carpma hizi", "44.2"),
    # Dinamik
    ("10 kg cisme 50 N kuvvet etki ederse ivmesi nedir", "5"),
    ("2 kg cisim 3 m/s2 ivmeyle hareket ederse kuvvet nedir", "6"),
    ("kutlesi 8 kg olan cismin agirligi", "78"),
    ("surtunme katsayisi 0.4 olan 10 kg cisme etkiyen surtunme kuvveti",
     "39"),
    ("1000 kg araba 20 m/s hizdan 5 saniyede duruyor fren kuvveti",
     "-4000"),
    # Enerji, momentum, guc
    ("4 kg cisim 6 m/s hizla giderken kinetik enerjisi", "72"),
    ("3 kg cisim 5 m yukseklikte potansiyel enerjisi", "147"),
    ("500 N kuvvetle 10 m yol alan cismin yaptigi is", "5000"),
    ("2000 J is 4 saniyede yapilirsa guc nedir", "500"),
    ("6 kg cisim 4 m/s hizla giderken momentumu", "24"),
    ("10 m yuksekten birakilan 2 kg cismin kinetik enerjisi", "196"),
    # Donme ve dairesel
    ("eylemsizlik momenti 2 kg m2 acisal hizi 5 rad/s donme kinetik "
     "enerjisi", "25"),
    ("yaricapi 0.5 m periyodu 2 s dairesel hareket cizgisel hizi",
     "1.57"),
    # BHH ve dalga
    ("yay sabiti 200 N/m kutle 2 kg olan sistemin periyodu", "0.62"),
    ("uzunlugu 1 m olan sarkacin periyodu", "2.00"),
    ("frekansi 500 Hz dalga boyu 0.68 m olan dalganin hizi", "340"),
    ("2 m genlikli periyodu 4 s harmonik hareketin maksimum hizi",
     "3.14"),
    # Termodinamik
    ("2 kg suyu 20 dereceden 80 dereceye isitmak icin gereken isi",
     "502320"),
    ("3 mol ideal gaz 400 K 0.02 m3 basinc", "4.98"),
    ("600 K ve 300 K arasindaki carnot verimi", "0.5"),
    ("0.5 kg buzu eritmek icin gereken isi", "167000"),
    # Elektrik
    ("12 V gerilim 4 ohm direnc akim", "3"),
    ("220 V ve 5 A icin elektriksel guc", "1100"),
    ("3 ohm ve 6 ohm paralel esdeger direnc", "2"),
    ("2 ohm ve 5 ohm seri esdeger direnc", "7"),
    ("12 V kaynaga seri bagli 4 ohm ve 8 ohm direnclerden gecen akim",
     "1 A"),
    # Manyetizma
    ("0.5 T manyetik alanda 2 m telden 3 A akim gecerse kuvvet", "3"),
    # Optik
    ("odak uzakligi 20 cm mercekte 60 cm uzaktaki cismin goruntu "
     "uzakligi", "0.3"),
    ("havadan cama 30 derece ile giren isigin kirilma acisi", "19"),
    # Modern fizik
    ("500 nm dalga boylu fotonun enerjisi", "3.97"),
    ("0.6c hizla giden cismin lorentz carpani", "1.25"),
    ("1 gram kutlenin enerji karsiligi", "8.98"),
    ("elektron 200 V ile hizlandirilirsa hizi", "8.38"),
    ("yari omru 5 yil olan maddenin bozunma sabiti", "4.39"),
]


def sayisal_puani():
    """Genis sayisal problem seti. (dogru, toplam)"""
    from . import brain
    dogru = 0
    for i, (soru, beklenen) in enumerate(SAYISAL_PROBLEMLER):
        try:
            t = brain.respond(soru, session="_olcum_say%d" % i).text
        except Exception:
            t = ""
        if beklenen in (t or ""):
            dogru += 1
    return dogru, len(SAYISAL_PROBLEMLER)


def sayisal_bosluklari():
    from . import brain
    eksik = []
    for i, (soru, beklenen) in enumerate(SAYISAL_PROBLEMLER):
        try:
            t = brain.respond(soru, session="_olcum_say%d" % i).text
        except Exception:
            t = ""
        if beklenen not in (t or ""):
            son = [x for x in (t or "").split("\n") if x.startswith("## ")]
            eksik.append((soru[:50], beklenen,
                          son[0][:24] if son else "(hesap yok)"))
    return eksik


def ad_erisim_puani():
    """Kac konu SADECE ADIYLA dogru ve dolu cevap aliyor? (dogru, toplam)"""
    from . import brain
    dogru = 0
    for a in AD_SORULARI:
        try:
            t = brain.respond(a, session="_olcum_ad").text
        except Exception:
            t = ""
        if _ad_cevabi_yeterli(t):
            dogru += 1
    return dogru, len(AD_SORULARI)


def ad_erisim_bosluklari():
    from . import brain
    eksik = []
    for a in AD_SORULARI:
        try:
            t = brain.respond(a, session="_olcum_ad").text
        except Exception:
            t = ""
        if not _ad_cevabi_yeterli(t):
            eksik.append(a)
    return eksik
