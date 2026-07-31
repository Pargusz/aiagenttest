# -*- coding: utf-8 -*-
"""Kendi kendini genisletme motoru.

Sorun: 16.000 makale okundugu halde sistemin sayilari sabit kaliyordu —
"3 yol haritam var", "27 konu", "190 formul". Okunan makaleler yalnizca
literatur taramasi icin kullaniliyor, sistemin YAPABILDIKLERINI
buyutmuyordu.

Bu modul, biriken makalelerden yeni YETENEK uretir:

1. `yol_haritalari` — her fizik alt alani icin yol haritasi. Ilk ucu asama
   (temeller, cekirdek kavramlar, araclar) alanin dogru pedagojisidir ve
   elle yazilmistir; dorduncu asama DOGRUDAN korpustan gelir: o alanin
   makale basliklarinda en cok gecen konu ifadeleri. Yeni makaleler geldikce
   bu asama kendiliginden guncellenir ve yeterli makale biriken her yeni
   alan icin yeni bir harita acilir.

2. `konu_sayisi` — cekirdek 27 konuya ek olarak sentezlenebilen kavramlar.

Kalite kapisi: bir alan icin harita ancak yeterli sayida makale ve en az
uc gecerli konu ifadesi varsa uretilir. Ifadeler genel kelime listesinden
gecirilir ("system", "analysis" gibi her makalede gecen kelimeler elenir).
"""
import collections
import re

from . import db

# arXiv kategorisi -> (TR ad, EN ad, anahtar kelimeler, temeller_tr, cekirdek_tr)
# Temeller ve cekirdek elle yazilmistir: bir alanin on kosullari korpustan
# cikarilamaz, cikarilsaydi da guvenilir olmazdi. Korpus ileri asamayi besler.
ALANLAR = {
    "quant-ph": (
        "Kuantum Mekaniği", "Quantum Mechanics",
        "kuantum|kuantum mekanigi|quantum|dalga fonksiyonu|schrodinger",
        ["Lineer cebir: vektör uzayları, iç çarpım, özdeğer problemi",
         "Karmaşık sayılar ve Fourier analizi",
         "Klasik mekanikte Hamilton formalizmi",
         "Olasılık ve istatistik temelleri"],
        ["Dalga-parçacık ikiliği, de Broglie dalga boyu",
         "Schrödinger denklemi ve dalga fonksiyonunun yorumu",
         "Kutuda parçacık, potansiyel engel, tünelleme",
         "Kuantum harmonik salınıcı",
         "Belirsizlik ilkesi ve operatörler",
         "Hidrojen atomu, kuantum sayıları, spin"]),
    "cond-mat.stat-mech": (
        "İstatistiksel Mekanik", "Statistical Mechanics",
        "istatistiksel mekanik|statistical mechanics|entropi|ensemble|"
        "termodinamik istatistik",
        ["Termodinamiğin dört yasası",
         "Olasılık dağılımları, ortalama ve varyans",
         "Kombinatorik ve Stirling yaklaşımı",
         "Kısmi türev ve toplam diferansiyel"],
        ["Mikrodurum, makrodurum ve Boltzmann entropisi",
         "Kanonik ve büyük kanonik topluluk",
         "Bölüşüm fonksiyonundan termodinamiğe geçiş",
         "Maxwell-Boltzmann, Bose-Einstein, Fermi-Dirac dağılımları",
         "Faz geçişleri ve kritik olaylar",
         "Dalgalanma-yayılım teoremi"]),
    "physics.optics": (
        "Optik ve Fotonik", "Optics and Photonics",
        "optik|isik|mercek|kirinim|girisim|optics|photonics|lazer",
        ["Dalga denklemi ve harmonik dalgalar",
         "Karmaşık sayılarla dalga gösterimi (fazör)",
         "Maxwell denklemlerinin temel biçimi",
         "Trigonometri ve küçük açı yaklaşımı"],
        ["Yansıma, kırılma, Snell yasası, tam yansıma",
         "İnce mercek ve ayna denklemleri, görüntü kurma",
         "Girişim: çift yarık, ince film",
         "Kırınım: tek yarık, ızgara, Rayleigh ölçütü",
         "Polarizasyon: Malus ve Brewster",
         "Işığın maddeyle etkileşimi, dispersiyon"]),
    "physics.flu-dyn": (
        "Akışkanlar Dinamiği", "Fluid Dynamics",
        "akiskan|akiskanlar|hidrodinamik|fluid|turbulans|akis",
        ["Vektör analizi: gradyan, diverjans, rotasyonel",
         "Kısmi diferansiyel denklemlere giriş",
         "Newton yasaları ve momentum korunumu",
         "Boyut analizi ve boyutsuz sayılar"],
        ["Süreklilik denklemi ve kütle korunumu",
         "Bernoulli denklemi ve uygulamaları",
         "Viskozite, Newton ve Newton olmayan akışkanlar",
         "Navier-Stokes denklemleri",
         "Laminer ve türbülanslı akış, Reynolds sayısı",
         "Sınır tabaka ve sürükleme kuvveti"]),
    "cond-mat.mtrl-sci": (
        "Malzeme Fiziği", "Materials Physics",
        "malzeme|katihal|kristal|yariiletken|materials|solid state",
        ["Atom yapısı ve bağ türleri",
         "Kristal örgü ve birim hücre kavramı",
         "Kuantum mekaniğinin temelleri",
         "İstatistiksel dağılımlar (Fermi-Dirac)"],
        ["Kristal yapılar ve Miller indisleri",
         "X-ışını kırınımı ve Bragg yasası",
         "Bant kuramı: iletken, yalıtkan, yarıiletken",
         "Serbest elektron modeli ve Fermi enerjisi",
         "Fononlar ve ısı kapasitesi",
         "Kusurlar, dislokasyonlar ve mekanik özellikler"]),
    "gr-qc": (
        "Görelilik ve Kütle Çekimi", "Relativity and Gravitation",
        "gorelilik|relativity|kutle cekimi|kara delik|uzayzaman|einstein",
        ["Özel görelilik: Lorentz dönüşümleri",
         "Tensör cebiri ve indis gösterimi",
         "Diferansiyel geometri temelleri",
         "Klasik alan kuramı ve varyasyon ilkesi"],
        ["Eşdeğerlik ilkesi ve serbest düşüş",
         "Metrik tensör ve eğrilik",
         "Einstein alan denklemleri",
         "Schwarzschild çözümü ve kara delikler",
         "Yerçekimsel kırmızıya kayma ve zaman genlemesi",
         "Kütle çekim dalgaları"]),
    "astro-ph": (
        "Astrofizik", "Astrophysics",
        "astrofizik|yildiz|galaksi|evren|kozmoloji|astro|gokbilim",
        ["Newton mekaniği ve kütle çekimi",
         "Işınım yasaları (Planck, Stefan-Boltzmann, Wien)",
         "Atom spektrumları",
         "Logaritmik ölçekler ve kadir sistemi"],
        ["Yıldız yapısı ve hidrostatik denge",
         "Hertzsprung-Russell diyagramı ve yıldız evrimi",
         "Nükleer füzyon ve enerji üretimi",
         "Uzaklık merdiveni: paralaks, Sefeidler, süpernovalar",
         "Galaksiler, karanlık madde kanıtları",
         "Hubble yasası ve evrenin genişlemesi"]),
    "physics.plasm-ph": (
        "Plazma Fiziği", "Plasma Physics",
        "plazma|plasma|iyonize|fuzyon reaktoru|tokamak",
        ["Elektromanyetizma: Maxwell denklemleri",
         "Yüklü parçacığın alandaki hareketi",
         "İstatistiksel mekanik ve dağılım fonksiyonları",
         "Akışkanlar dinamiğinin temelleri"],
        ["Plazma tanımı: Debye perdelemesi ve plazma frekansı",
         "Tek parçacık hareketi: Larmor yarıçapı, sürüklenmeler",
         "Manyetohidrodinamik (MHD) yaklaşımı",
         "Plazma dalgaları ve kararsızlıklar",
         "Çarpışmalar, direnç ve taşınım",
         "Füzyon koşulları ve Lawson ölçütü"]),
    "physics.class-ph": (
        "Klasik Fizik", "Classical Physics",
        "klasik fizik|klasik mekanik|classical physics|newton mekanigi",
        ["Türev ve integral",
         "Vektörler ve vektörel çarpım",
         "Diferansiyel denklemler (1. ve 2. mertebe)",
         "Trigonometri"],
        ["Kinematik: konum, hız, ivme",
         "Newton yasaları ve serbest cisim diyagramı",
         "İş, enerji ve korunum yasaları",
         "Momentum ve çarpışmalar",
         "Dönme hareketi, tork, açısal momentum",
         "Salınımlar ve dalgalar"]),
    # NOT: physics.comp-ph icin elle yazilmis "sayisal" haritasi zaten var;
    # ikisi ayni sorulari yakaliyor ve uretilmis olan hic acilmiyordu.
    # Burayi ATLAMIYORUZ ama anahtar kelimeleri cakismayacak bicimde
    # daraltiyoruz: elle yazilan giris duzeyini, bu ileri duzeyi anlatir.
    "physics.comp-ph": (
        "İleri Hesaplamalı Fizik", "Advanced Computational Physics",
        "ileri hesaplamali|ileri sayisal|yuksek basarimli|hpc|"
        "paralel hesaplama|advanced computational",
        ["Bir programlama dili (MATLAB/Octave veya Python)",
         "Lineer cebir ve matris işlemleri",
         "Diferansiyel denklemler",
         "Hata ve yuvarlama kavramı"],
        ["Sayısal türev ve integral, hata mertebesi",
         "Kök bulma ve optimizasyon",
         "Adi diferansiyel denklem çözücüleri (Runge-Kutta)",
         "Kısmi diferansiyel denklemler: sonlu fark yöntemi",
         "Monte Carlo yöntemleri",
         "Veri uydurma ve hata yayılımı"]),
    "cond-mat.soft": (
        "Yumuşak Madde Fiziği", "Soft Matter Physics",
        "yumusak madde|polimer|kolloid|soft matter|jel|sivi kristal",
        ["İstatistiksel mekanik temelleri",
         "Termodinamik potansiyeller",
         "Akışkanlar dinamiği",
         "Olasılık ve rastgele yürüyüş"],
        ["Brown hareketi ve yayınım",
         "Polimer zincirleri ve entropik esneklik",
         "Kolloidal etkileşimler ve kararlılık",
         "Yüzey gerilimi ve ıslatma",
         "Sıvı kristaller ve düzen parametresi",
         "Reoloji: viskoelastik davranış"]),
    "physics.app-ph": (
        "Uygulamalı Fizik", "Applied Physics",
        "uygulamali fizik|applied physics|cihaz|sensor|olcum",
        ["Elektrik devreleri ve Ohm yasası",
         "Ölçüm belirsizliği ve hata analizi",
         "Sinyal ve frekans kavramı",
         "Malzeme özelliklerinin temelleri"],
        ["Sensör ilkeleri: piezoelektrik, termoelektrik, optik",
         "Sinyal işleme: filtreler, gürültü, FFT",
         "Yarıiletken cihazlar: diyot, transistör",
         "Optik cihazlar ve lazerler",
         "Isı yönetimi ve termal tasarım",
         "Ölçüm düzeneği kurma ve kalibrasyon"]),
    "nlin.CD": (
        "Kaos ve Doğrusal Olmayan Dinamik", "Chaos and Nonlinear Dynamics",
        "kaos|dogrusal olmayan|nonlinear|chaos|attraktor|bifurkasyon",
        ["Adi diferansiyel denklemler",
         "Faz uzayı kavramı",
         "Lineer kararlılık analizi",
         "Sayısal çözücüler"],
        ["Sabit noktalar ve kararlılık",
         "Bifurkasyonlar",
         "Limit çevrimler ve Poincaré kesiti",
         "Lyapunov üsleri ve başlangıç koşuluna duyarlılık",
         "Tuhaf çekiciler ve fraktal boyut",
         "Zaman serisinden dinamik çıkarma"]),
    "math-ph": (
        "Matematiksel Fizik", "Mathematical Physics",
        "matematiksel fizik|mathematical physics|grup kurami|simetri",
        ["Lineer cebir ve fonksiyonel analiz temelleri",
         "Karmaşık analiz",
         "Diferansiyel denklemler",
         "Varyasyon hesabı"],
        ["Hilbert uzayları ve operatörler",
         "Grup kuramı ve simetriler",
         "Green fonksiyonları",
         "Özel fonksiyonlar (Legendre, Bessel, Hermite)",
         "Diferansiyel geometri ve manifoldlar",
         "Varyasyon ilkeleri ve Noether teoremi"]),
}

# Baslik ifadelerinden elenecek genel kelimeler
_GENEL_KELIME = set("""
the a an of in on for with and or to from by is are be as at we this that new
study analysis theory model system method methods using based approach effect
effects results result paper investigation problem problems case general via
its their our can may between within under over into about more most some
physics physical science sciences research review article letter comment reply
note notes brief report reports letters journal proceedings vol volume
one two three first second third part parts toward towards use uses used
role application applications properties property behavior behaviour
""".split())

EN_AZ_MAKALE = 20          # bir alan icin harita acmaya yetecek makale
EN_AZ_IFADE = 3            # korpustan gelmesi gereken en az konu ifadesi
DURUM_ANAHTARI = "uretilmis_yol_haritalari"


_SAYIM_ONBELLEK = {"makale": None, "sayilar": None}
_IFADE_ONBELLEK = {}


def _alan_makale_sayilari():
    """Her arXiv kategorisi icin makale sayisi.

    `categories` sutununda dizin yok; her cagri 14 tam tarama demek.
    Korpus buyuklugu degismedikce sonuc onbellekten verilir.
    """
    try:
        toplam = db.stats().get("makale", 0)
    except Exception:
        toplam = 0
    if _SAYIM_ONBELLEK["makale"] == toplam and _SAYIM_ONBELLEK["sayilar"]:
        return _SAYIM_ONBELLEK["sayilar"]
    c = db.conn()
    sayilar = {}
    for kat in ALANLAR:
        try:
            n = c.execute(
                "SELECT COUNT(*) FROM papers WHERE categories LIKE ?",
                ("%" + kat + "%",)).fetchone()[0]
        except Exception:
            n = 0
        sayilar[kat] = n
    _SAYIM_ONBELLEK["makale"] = toplam
    _SAYIM_ONBELLEK["sayilar"] = sayilar
    return sayilar


def korpus_ifadeleri(kat, limit=1500, en_az=2, adet=8):
    """Bir alanin makale basliklarindan konu ifadeleri cikar.

    Fizikte makale basliklari anlamlidir: "topological insulator",
    "wave turbulence" gibi ifadeler alanin gercek konularidir. Genel
    kelime iceren n-gramlar elenir.
    """
    onbellek_anahtari = (kat, limit, en_az, adet)
    if onbellek_anahtari in _IFADE_ONBELLEK:
        return _IFADE_ONBELLEK[onbellek_anahtari]
    c = db.conn()
    say = collections.Counter()
    try:
        satirlar = c.execute(
            "SELECT title FROM papers WHERE categories LIKE ? "
            "AND geri_cekik = 0 LIMIT ?", ("%" + kat + "%", limit)).fetchall()
    except Exception:
        return []
    for r in satirlar:
        t = (r["title"] or "").lower()
        t = re.sub(r"[^a-z0-9\s-]", " ", t)
        kelimeler = [w for w in t.split() if len(w) > 2]
        for n in (2, 3):
            for i in range(len(kelimeler) - n + 1):
                grup = kelimeler[i:i + n]
                if any(w in _GENEL_KELIME for w in grup):
                    continue
                say[" ".join(grup)] += 1

    # Uzun ifade kisasini kapsiyorsa kisayi ele ("shallow water" vs
    # "dispersive shallow water"): ayni konuyu iki kez yazmayalim.
    adaylar = [(ifade, n) for ifade, n in say.most_common(60) if n >= en_az]
    secilen = []
    for ifade, n in adaylar:
        if any(ifade in s or s in ifade for s, _ in secilen):
            continue
        secilen.append((ifade, n))
        if len(secilen) >= adet:
            break
    _IFADE_ONBELLEK[onbellek_anahtari] = secilen
    return secilen


def _arac_asamasi(kat, lang="tr"):
    """Bu alanda sistemin GERCEKTEN sahip oldugu formul ve kodlari listele."""
    from . import formulas, matlab
    kat_konu = {
        "quant-ph": ("kuantum",), "cond-mat.stat-mech": ("termodinamik",),
        "physics.optics": ("optik",), "physics.flu-dyn": ("akiskan",),
        "cond-mat.mtrl-sci": ("katihal",), "gr-qc": ("gorelilik",),
        "astro-ph": ("astro",), "physics.plasm-ph": ("plazma",),
        "physics.class-ph": ("kinematik", "dinamik", "enerji"),
        "physics.comp-ph": (), "cond-mat.soft": ("akiskan", "termodinamik"),
        "physics.app-ph": ("elektrik",), "nlin.CD": ("dalga",),
        "math-ph": (),
    }
    konular = kat_konu.get(kat, ())
    formul_adlari = [f["tr"] if lang == "tr" else f["en"]
                     for f in formulas.FORMULAS if f["topic"] in konular]
    kat_sablon = {
        "quant-ph": ("kuantum_kuyu", "sembolik"),
        "cond-mat.stat-mech": ("monte_carlo", "termo_cevrim"),
        "physics.optics": ("optik_isin", "dalga_denklemi"),
        "physics.flu-dyn": ("laplace_pde", "isi_denklemi"),
        "cond-mat.mtrl-sci": ("matris_lineer", "egri_uydurma"),
        "gr-qc": ("sembolik", "yorunge"),
        "astro-ph": ("yorunge", "hareket_denklemi"),
        "physics.plasm-ph": ("hareket_denklemi", "vektor_alan"),
        "physics.class-ph": ("egik_atis", "sonumlu_osilator"),
        "physics.comp-ph": ("sayisal_integral", "ode_sistem", "optimizasyon"),
        "cond-mat.soft": ("monte_carlo", "istatistik_hata"),
        "physics.app-ph": ("rlc", "fft", "kontrol_sistem"),
        "nlin.CD": ("ode_sistem", "animasyon"),
        "math-ph": ("sembolik", "matris_lineer"),
    }
    sablonlar = [matlab.TEMPLATES[k]["tr" if lang == "tr" else "en"]
                 for k in kat_sablon.get(kat, ()) if k in matlab.TEMPLATES]
    return formul_adlari, sablonlar


def harita_uret(kat, lang="tr"):
    """Bir alan icin yol haritasi uret. Yetersizse None doner."""
    if kat not in ALANLAR:
        return None
    ad_tr, ad_en, kw, temeller, cekirdek = ALANLAR[kat]
    makale = _alan_makale_sayilari().get(kat, 0)
    if makale < EN_AZ_MAKALE:
        return None
    ifadeler = korpus_ifadeleri(kat)
    if len(ifadeler) < EN_AZ_IFADE:
        return None

    formul_adlari, sablonlar = _arac_asamasi(kat)
    guncel = ["%s  <span class='meta'>(%d makale)</span>" % (i.title(), n)
              for i, n in ifadeler]

    asamalar = [
        {"ad": "1. Ön koşullar", "sure": "önce bu",
         "konular": temeller,
         "neden": "Bu araçlar olmadan %s'nin denklemleri ezberlenir, "
                  "anlaşılmaz. Ezber ilk zor problemde çöker." % ad_tr,
         "alistirma": "Ön koşullardan en zayıf olduğunuzu seçin ve bana "
                      "o konuda 5 soru ürettirin.",
         "dene": "`%s hakkinda 5 soru uret`" % temeller[0].split(":")[0].lower()},
        {"ad": "2. Çekirdek kavramlar", "sure": "6-10 hafta",
         "konular": cekirdek,
         "neden": "%s'nin omurgası bunlar. Her birini bana anlattırıp "
                  "ardından kendiniz anlatmayı deneyin — anlatamadığınız "
                  "yer, anlamadığınız yerdir." % ad_tr,
         "alistirma": "Her kavram için bir günlük hayat örneği bulun.",
         "dene": "`%s nedir`" % cekirdek[0].split(",")[0].split(":")[0].lower()},
    ]

    if formul_adlari or sablonlar:
        konular = []
        if formul_adlari:
            konular.append("Doğrulanmış formüller (%d adet): %s"
                           % (len(formul_adlari),
                              ", ".join(formul_adlari[:6])
                              + (" …" if len(formul_adlari) > 6 else "")))
        for s in sablonlar:
            konular.append("MATLAB: %s" % s)
        konular.append("Boyut denetimi ile kendi sonucunuzu sınama")
        asamalar.append({
            "ad": "3. Araçlar ve hesap", "sure": "2-4 hafta",
            "konular": konular,
            "neden": "Bu alanda elimdeki doğrulanmış hesap araçları bunlar. "
                     "Formülleri herhangi bir değişkeni için çözebilir, "
                     "kodları çalıştırıp sonucu görebilirsiniz.",
            "alistirma": "Bir formülü seçip önce elle, sonra bana çözdürün; "
                         "sonuçları karşılaştırın.",
            "dene": "`%s`" % ((formul_adlari or ["kinetik enerji"])[0].lower())})

    asamalar.append({
        "ad": "4. Literatürden güncel konular", "sure": "sürekli",
        "konular": guncel,
        "neden": "Bu başlıklar, okuduğum %s makalesinden çıkarıldı — "
                 "alanın şu an gerçekten çalıştığı konular bunlar. "
                 "Yeni makaleler geldikçe bu liste kendiliğinden güncellenir."
                 % "{:,}".format(makale),
        "alistirma": "Bir başlığı seçip literatür taraması yaptırın, sonra "
                     "özetini kendi cümlelerinizle yazın.",
        "dene": "`%s hakkinda ne biliyorsun`" % ifadeler[0][0]})

    asamalar.append({
        "ad": "5. Kendi çalışman", "sure": "sürekli",
        "konular": ["Bir makale seçip PDF olarak yükleyin, birlikte inceleyelim",
                    "Öğrendiğiniz bir konuda kendinize 10 soru ürettirin",
                    "Bir problemi MATLAB'de çözüp sonucu doğrulatın",
                    "Anlatamadığınız konuyu tekrar sorun — anlatamamak, "
                    "anlamamaktır"],
        "neden": "Okumak yetmez; üretmek gerekir. Bu aşamada ben sınayıcı "
                 "olurum, siz anlatan.",
        "alistirma": "Haftada bir makale + bir kod + on soru.",
        "dene": "`%s hakkinda 10 soru uret`" % ad_tr.lower()})

    return {
        "key": "uretilmis:" + kat,
        "tr": ad_tr + " Yol Haritası",
        "en": ad_en + " Roadmap",
        "kw": kw.split("|"),
        "ozet_tr": ("Bu yol haritasını **ben oluşturdum**: ön koşullar ve "
                    "çekirdek kavramlar alanın standart müfredatından, "
                    "4. aşamadaki güncel konular ise okuduğum **%s %s "
                    "makalesinden** çıkarıldı. Yeni makaleler geldikçe "
                    "güncellenir."
                    % ("{:,}".format(makale), ad_tr.lower())),
        "ozet_en": ("I generated this roadmap: prerequisites and core "
                    "concepts follow the standard curriculum, while the "
                    "current topics in stage 4 come from the %s papers I "
                    "have read in this field." % "{:,}".format(makale)),
        "asamalar": asamalar,
        "asamalar_en": asamalar,
        "ipuclari_tr": None,
        "ipuclari_en": None,
        "uretilmis": True,
        "makale": makale,
    }


def haritalari_tazele():
    """Tum uygun alanlar icin harita uret, sakla ve curriculum'a kat."""
    from . import curriculum
    uretilen = {}
    for kat in ALANLAR:
        h = harita_uret(kat)
        if h:
            uretilen[h["key"]] = h
    db.set_state(DURUM_ANAHTARI, {"haritalar": uretilen})
    for k, h in uretilen.items():
        curriculum.PATHS[k] = h
    return len(uretilen)


def haritalari_bagla():
    """Onbellekteki uretilmis haritalari curriculum'a kat (hizli acilis)."""
    from . import curriculum
    veri = db.get_state(DURUM_ANAHTARI)
    if not isinstance(veri, dict):
        return 0
    haritalar = veri.get("haritalar") or {}
    for k, h in haritalar.items():
        curriculum.PATHS[k] = h
    return len(haritalar)


def durum():
    """Genisleme motorunun ne urettigini ozetle."""
    from . import curriculum, sentez, knowledge, formulas
    uretilmis = [p for p in curriculum.PATHS.values() if p.get("uretilmis")]
    return {
        "yol_haritasi_toplam": len(curriculum.PATHS),
        "yol_haritasi_uretilmis": len(uretilmis),
        "cekirdek_konu": len(knowledge.TOPICS),
        "ogrenilen_konu": sentez.aciklanabilir_sayisi(),
        "formul": len(formulas.FORMULAS),
    }


# ── Formul bilesimi ─────────────────────────────────────────────────────────
# Makale metninden formul cikarmak denendi ve olculdu: 4.000 ozette bulunan
# 279 "esitlik"in neredeyse tamami "q=5/3" gibi parcalardi. Bunlari formule
# cevirmek, daha once temizledigimiz cop birikimini geri getirirdi.
#
# Bunun yerine formul tabani DOGRULANMIS cekirdekten buyutuluyor: ortak
# degiskeni olan iki formul birlestirilerek yeni bir bagintiya varilir
# (ornek: Ek = mv^2/2 ile v = v0 + a*t birleşince kinetik enerji dogrudan
# ivme ve zamandan hesaplanabilir). Uretilen her baginti,
#   - boyut denetiminden,
#   - geri yerine koymadan,
#   - var olan formullerle ayni olmama denetiminden
# gecmek zorunda. Yani taban yalnizca DOGRULANMIS bilgiyle buyur.
#
# Korpusun rolu: hangi alanin once islenecegini makale sayilari belirler.

BILESIM_ANAHTARI = "uretilmis_formuller"
_KOTU = ("zoo", "oo", "nan", "I")          # SymPy'nin bozuk sonuclari

# Hangi konular birlestirilebilir? Cebirsel olarak her formul her formulle
# birlestirilebilir ama sonuc fizik olmayabilir: kalorimetre formulunden
# cekilen kutleyi Newton yasasina koyunca "F = Q*a/(c*dT)" cikiyor — boyutu
# dogru, anlami yok. Yalnizca gercekten komsu alanlar birlestirilir.
KOMSU_KONULAR = {
    "kinematik": {"kinematik", "dinamik", "enerji"},
    "dinamik": {"dinamik", "kinematik", "enerji", "astro"},
    "enerji": {"enerji", "kinematik", "dinamik"},
    "elektrik": {"elektrik", "katihal"},
    "katihal": {"katihal", "elektrik"},
    "termodinamik": {"termodinamik", "akiskan"},
    "akiskan": {"akiskan", "termodinamik"},
    "dalga": {"dalga", "optik"},
    "optik": {"optik", "dalga", "kuantum"},
    "kuantum": {"kuantum", "optik", "nukleer"},
    "nukleer": {"nukleer", "kuantum", "gorelilik"},
    "gorelilik": {"gorelilik", "nukleer", "astro"},
    "astro": {"astro", "gorelilik", "dinamik"},
    "plazma": {"plazma", "elektrik"},
}


def _konular_uyumlu(a, b):
    return b["topic"] in KOMSU_KONULAR.get(a["topic"], {a["topic"]})


def _kanonik(eq):
    """Denklemi karsilastirilabilir tek bicime indir.

    "F = W*a/g" ile "W = F*g/a" ayni bagintidir; ikisi de
    "F*g - W*a = 0" biçimine iner. Paydalar temizlenip pay carpanlarina
    ayrilarak bu ortak bicime ulasiyoruz.
    """
    import sympy as sp
    try:
        ifade = sp.together(eq.lhs - eq.rhs)
        pay, _payda = sp.fraction(ifade)
        return sp.factor(sp.expand(pay))
    except Exception:
        return None


def _ayni_mi(yeni_eq, mevcut_eq):
    """Iki denklem ayni bagintiyi mi anlatiyor?

    Kanonik biçimlerin orani bir tek terimse (sabit veya degisken carpimi,
    toplama icermeyen) iki denklem ayni bagintidir.
    """
    import sympy as sp
    a, b = _kanonik(yeni_eq), _kanonik(mevcut_eq)
    if a is None or b is None:
        return False
    try:
        if sp.simplify(a - b) == 0:
            return True
        oran = sp.cancel(a / b)
        if oran == 0:
            return False
        # Toplama iceriyorsa farkli bagintilardir
        return not oran.atoms(sp.Add)
    except Exception:
        return False


def _bilesim_dene(a, b, sym):
    """a formulunde sym yerine b'nin cozumunu koy. Yeni formul ya da None."""
    import sympy as sp
    from . import formulas

    # Her iki formul de sonuca en az iki degiskenle katkida bulunmali;
    # yoksa sonuc yalnizca bir degiskenin yeniden adlandirilmasi olur.
    if len(set(a["vars"]) - {sym}) < 2 or len(set(b["vars"]) - {sym}) < 2:
        return None
    if not _konular_uyumlu(a, b):
        return None
    try:
        eqa, eqb = formulas.sympy_eq(a), formulas.sympy_eq(b)
        s = sp.Symbol(sym)
        if s not in (eqb.lhs - eqb.rhs).free_symbols:
            return None
        cozumler = sp.solve(sp.Eq(eqb.lhs, eqb.rhs), s, dict=False)
    except Exception:
        return None
    if not cozumler or len(cozumler) > 2:
        return None
    coz = cozumler[0]
    try:
        yeni = sp.simplify(sp.Eq(eqa.lhs, eqa.rhs).subs(s, coz))
    except Exception:
        return None
    metin = str(yeni)
    if any(k in metin for k in _KOTU) or "Eq(" not in metin:
        return None
    if len(metin) > 120:                    # asiri karmasik: ogretici degil
        return None
    # Isaret artifaktlari (-sqrt(...) = x gibi) ogretici degil
    if metin.count("-") > 2:
        return None

    degiskenler = {}
    for kaynak in (a, b):
        for k, v in kaynak["vars"].items():
            if k != sym:
                degiskenler.setdefault(k, v)
    kalan = {str(x) for x in (yeni.lhs - yeni.rhs).free_symbols}
    degiskenler = {k: v for k, v in degiskenler.items() if k in kalan}
    if not (3 <= len(degiskenler) <= 6):
        return None

    sol = str(yeni.lhs)
    sag = str(yeni.rhs).replace("**", "^").replace("^", "**")
    return {
        "id": "bilesim_%s_%s" % (a["id"], b["id"]),
        "topic": a["topic"],
        "tr": "%s (%s yerine %s)" % (a["tr"], _degisken_adi(a, sym, "tr"),
                                     b["tr"].lower()),
        "en": "%s (%s from %s)" % (a["en"], _degisken_adi(a, sym, "en"),
                                   b["en"].lower()),
        "eq": "%s = %s" % (sol, sag),
        "vars": degiskenler,
        # Anahtar kelimeler ebeveynlerden devralinir: turetilmis baginti,
        # her iki formulun sorulariyla da bulunabilmeli.
        "kw_tr": _anahtar_devral(a, b, "kw_tr"),
        "kw_en": _anahtar_devral(a, b, "kw_en"),
        "note_tr": ("Bu bağıntıyı **ben türettim**: «%s» ile «%s» "
                    "formüllerini ortak değişken %s üzerinden birleştirdim. "
                    "Boyut denetimi ve geri yerine koyma sınamalarını geçti."
                    % (a["tr"], b["tr"], sym)),
        "note_en": ("I derived this by combining «%s» and «%s» through the "
                    "shared variable %s; it passed both verification checks."
                    % (a["en"], b["en"], sym)),
        "uretilmis": True,
        "kaynak": [a["id"], b["id"], sym],
    }


def _anahtar_devral(a, b, alan, en_fazla=8):
    """Iki ebeveynin en ozgun anahtar kelimelerini birlestir."""
    birlesik = []
    for kaynak in (a, b):
        for kw in kaynak.get(alan, []):
            k = (kw or "").strip()
            # Tek kelimelik genel anahtarlar turetilmis formule cekmemeli
            if len(k) >= 6 and " " in k and k not in birlesik:
                birlesik.append(k)
    return birlesik[:en_fazla]


def _degisken_adi(f, sym, lang="tr"):
    v = f["vars"].get(sym)
    if not v:
        return sym
    return v[0] if lang == "tr" else v[1]


def formul_uret(en_fazla=40, alan_sirasi=None):
    """Dogrulanmis cekirdekten yeni formuller ureterek tabani buyut.

    Uretilen her formul iki bagimsiz sinamadan gecer; gecemeyen atilir.
    Doner: (kabul edilen formul listesi, denenen sayisi)
    """
    import itertools
    import sympy as sp
    from . import formulas, dogrulama

    # Denklem karsilastirmasi pahali; yalnizca AYNI degisken kumesine sahip
    # formullerle karsilastiriyoruz. Farkli degiskenli iki denklem zaten
    # ayni olamaz.
    mevcut_eq = {}
    for f in formulas.FORMULAS:
        try:
            mevcut_eq.setdefault(frozenset(f["vars"]), []).append(
                formulas.sympy_eq(f))
        except Exception:
            pass

    # Alan onceligi korpustan: cok makale okunan alanin formulleri once
    sayilar = _alan_makale_sayilari()
    konu_agirlik = collections.Counter()
    kat_konu = {"quant-ph": "kuantum", "cond-mat.stat-mech": "termodinamik",
                "physics.optics": "optik", "physics.flu-dyn": "akiskan",
                "cond-mat.mtrl-sci": "katihal", "gr-qc": "gorelilik",
                "astro-ph": "astro", "physics.plasm-ph": "plazma",
                "physics.class-ph": "dinamik", "physics.app-ph": "elektrik"}
    for kat, n in sayilar.items():
        if kat in kat_konu:
            konu_agirlik[kat_konu[kat]] += n

    cekirdek = [f for f in formulas.FORMULAS if not f.get("uretilmis")]
    cekirdek.sort(key=lambda f: -konu_agirlik.get(f["topic"], 0))

    kabul, denendi, gorulen = [], 0, set()
    kaynak_sayisi = collections.Counter()
    for a, b in itertools.permutations(cekirdek, 2):
        if len(kabul) >= en_fazla:
            break
        # Cesitlilik: tek bir formulden turetilenler tabani doldurmasin
        if kaynak_sayisi[a["id"]] >= 3:
            continue
        ortak = set(a["vars"]) & set(b["vars"])
        if len(ortak) != 1:
            continue
        if not _konular_uyumlu(a, b):
            continue
        sym = next(iter(ortak))
        denendi += 1
        yeni = _bilesim_dene(a, b, sym)
        if not yeni:
            continue
        if yeni["eq"] in gorulen:
            continue
        gorulen.add(yeni["eq"])
        try:
            yeni_eq = formulas.sympy_eq(yeni)
        except Exception:
            continue
        anahtar = frozenset(yeni["vars"])
        if any(_ayni_mi(yeni_eq, m) for m in mevcut_eq.get(anahtar, [])):
            continue          # zaten bildigim bir baginti
        # Once ucuz boyut denetimi, sonra pahali geri yerine koyma
        if dogrulama.boyut_denetimi(yeni).get("ok") is not True:
            continue
        if dogrulama.geri_yerine_koy(yeni).get("ok") is not True:
            continue
        kabul.append(yeni)
        kaynak_sayisi[a["id"]] += 1
        mevcut_eq.setdefault(anahtar, []).append(yeni_eq)
    return kabul, denendi


def formulleri_kaydet(yeniler):
    """Uretilen formulleri kalici sakla."""
    veri = db.get_state(BILESIM_ANAHTARI)
    liste = veri.get("formuller", []) if isinstance(veri, dict) else []
    var = {f["eq"] for f in liste}
    for f in yeniler:
        if f["eq"] not in var:
            liste.append(f)
            var.add(f["eq"])
    db.set_state(BILESIM_ANAHTARI, {"formuller": liste})
    return len(liste)


def formulleri_bagla():
    """Saklanan uretilmis formulleri arama tabanina kat."""
    from . import formulas
    veri = db.get_state(BILESIM_ANAHTARI)
    if not isinstance(veri, dict):
        return 0
    n = 0
    for f in veri.get("formuller", []):
        if f["id"] in formulas.BY_ID:
            continue
        # vars sozlugu JSON'dan liste olarak doner; demete geri cevir
        f["vars"] = {k: tuple(v) for k, v in f["vars"].items()}
        formulas.FORMULAS.append(f)
        formulas.BY_ID[f["id"]] = f
        n += 1
    if n:
        formulas._ARAMA_INDEKS = None
    return n
