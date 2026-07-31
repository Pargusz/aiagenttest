# -*- coding: utf-8 -*-
"""Gunluk dilde sorulan sorular dogru formule gidiyor mu?

Kullanici formul adini bilmez; "topun havada ne kadar kaldigi" der.
Bu olcum, formul tabaninin gunluk dil kapsamini sayiyla gosterir ve
her test kosusunda tekrar edilir; boylece kapsam sessizce gerileyemez.
"""

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
