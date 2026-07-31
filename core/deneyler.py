# -*- coding: utf-8 -*-
"""Kilit deneyler: bir seyi NEREDEN bildigimiz.

Olculdu: "elektronun spini neden 1/2, bunu deneysel olarak nasil biliyoruz"
sorusuna sistem alakasiz makale alintilari verdi. Cevap Stern-Gerlach
deneyidir ve cekirdek bilgide yoktu.

Fizigi ogretmek, yalnizca sonucu soylemek degil, o sonuca NASIL varildigini
anlatmaktir. Burada fizigin donum noktasi olan deneyler yer alir: ne
olculdu, ne bekleniyordu, ne cikti ve bu neyi degistirdi.
"""
from .knowledge import T

DENEY_KONULARI = [

T("stern_gerlach", "Stern-Gerlach Deneyi", "Stern-Gerlach Experiment", """
**Soru:** Acisal momentum surekli mi, kesikli mi? Elektronun "spin"i
gercekten var mi?

**Duzenek (1922, Otto Stern ve Walther Gerlach):** Gumus atomlarindan
olusan bir demet, DUZGUN OLMAYAN manyetik alandan gecirilir. Manyetik
momenti olan bir atom, alan gradyaninda sapar; sapma miktari momentin
alan yonundeki bilesenine baglidir.

**Klasik beklenti:** Manyetik momentler rastgele yonelmis olmali, dolayisiyla
perdede SUREKLI bir leke (dikey bir cizgi) gorulmeli.

**Gozlem:** Iki ayri nokta. Demet TAM IKIYE ayrildi; arada hicbir sey yok.

**Sonuc:** Acisal momentumun bir bileseni kesiklidir ve gumus atomunun
disinda kalan tek elektron icin yalnizca iki deger alabilir: ±ħ/2. Yani
elektronun spini s = 1/2'dir. Spin kuantum sayisi s icin izinli bilesen
sayisi 2s+1 kadardir; iki nokta gormek 2s+1 = 2, yani s = 1/2 demektir.

**Neden bu kadar onemli:** (i) Kuantumlanmanin dogrudan, gozle gorulur
kaniti. (ii) Spin, yorunge hareketinden gelmeyen ICSEL bir ozelliktir —
klasik karsiligi yoktur. (iii) Ardil Stern-Gerlach duzenekleri, kuantum
olcumunun durumu DEGISTIRDIGINI gosterir: x yonunde olctukten sonra z
yonunde olcerseniz onceki bilgi silinir.
""", """
Stern and Gerlach (1922) sent silver atoms through an inhomogeneous
magnetic field. Classically a continuous smear was expected; instead the
beam split into exactly two spots. Angular momentum is quantised and the
electron's spin is 1/2 (2s+1 = 2 components). Sequential Stern-Gerlach
setups also show that measurement changes the state.
""",
  eqs=["μ_z = ±ħ/2 · (ge/2m)", "bilesen sayisi = 2s+1 = 2 → s = 1/2"],
  ex_tr=["Perdede iki nokta gormek neden s = 1/2 demek? Spin s olan bir "
         "parcacigin z bileseni 2s+1 farkli deger alir. Iki deger gorduysek "
         "2s+1 = 2, yani s = 1/2. Uc nokta gorseydik s = 1 olurdu."],
  ex_en=["Two spots mean 2s+1 = 2, hence s = 1/2."],
  kw="stern gerlach|spin nasil olculur|spin deneyi|elektron spini deney|"
     "acisal momentum kuantumlanmasi|spin 1/2 kaniti",
  related="kuantum_temelleri|simetri"),

T("cift_yarik_deneyi", "Çift Yarık Deneyi", "Double-Slit Experiment", """
**Soru:** Isik ve madde dalga mi, parcacik mi?

**Duzenek:** Kaynaktan cikan isik (ya da elektron) iki dar yariktan gecer
ve perdeye duser.

**Gozlem:** Perdede girisim deseni — aydinlik ve karanlik seritler. Bu,
DALGA davranisidir; iki yariktan gelen dalgalar ust uste biner.

**Asil carpici kisim:** Kaynagi o kadar zayiflatin ki her seferinde tek bir
elektron gecsin. Her elektron perdede TEK bir nokta birakir (parcacik gibi).
Ama binlerce elektron biriktikce noktalar girisim desenini olusturur.
Tek parcacik "kendisiyle girisir".

**Hangi yariktan gectigini olcerseniz:** Desen KAYBOLUR. Yol bilgisi
edinmek girisimi yok eder. Bu, olcumun sistemi degistirmesinin en temiz
gosterimidir.

**Tarihce:** Young (1801) isikla yapti ve dalga kuramini kabul ettirdi.
Davisson-Germer (1927) elektronlarla kristal kirinimi gozledi ve de
Broglie'nin madde dalgasi ongorusunu dogruladi. Tonomura (1989) tek tek
elektronlarla deseni birikimli olarak filme aldi.

**Ne ogretir:** Kuantum nesneleri ne klasik dalga ne klasik parcaciktir;
hangi soruyu sorarsaniz o yuzunu gosterir.
""", """
The double-slit experiment shows interference (wave behaviour) even when
particles pass one at a time — each leaves a single dot, yet the pattern
builds up. Measuring which slit destroys the pattern. Young (1801) with
light, Davisson-Germer (1927) with electrons, Tonomura (1989) one electron
at a time.
""",
  eqs=["d·sinθ = m·λ", "λ = h/p (de Broglie)"],
  ex_tr=["50 keV enerjili bir elektronun de Broglie dalga boyu yaklasik "
         "5,5 pm'dir — atomlar arasi mesafe mertebesinde. Bu yuzden "
         "elektron kirinimi kristallerde gozlenebilir; gorunur isikla "
         "(500 nm) bu ayrinti gorulemez."],
  ex_en=["A 50 keV electron has λ ≈ 5.5 pm, comparable to atomic spacing."],
  kw="cift yarik|double slit|girisim deneyi|dalga parcacik ikiligi deney|"
     "davisson germer|elektron kirinimi|tek elektron girisim",
  related="kuantum_temelleri|optik"),

T("michelson_morley", "Michelson-Morley Deneyi", "Michelson-Morley Experiment", """
**Soru:** Isik hangi ortamda yayilir? "Esir" (aether) var mi?

**Beklenti (1887):** Dunya esir icinde hareket ediyorsa, isigin hizi
hareket yonune gore farkli olculmeli — tipki akintida yuzen birinin
akintiya karsi ve akintiyla farkli hizlar gormesi gibi.

**Duzenek:** Isik demeti ikiye bolunur, birbirine dik iki kolda gidip
gelir ve tekrar birlestirilir. Kollardaki hiz farki girisim seritlerini
kaydirir. Duzenek dondurulunce kayma degismelidir.

**Gozlem:** Kayma YOK. Beklenen etkinin en fazla kirkta biri kadar bir
sinir. Deney onlarca kez, farkli mevsimlerde, artan duyarlilikla tekrarlandi
— sonuc hep ayni.

**Sonuc:** Isik hizi gozlemcinin hareketinden BAGIMSIZDIR. Esir yoktur.

**Ne degistirdi:** Einstein 1905'te bunu bir postulat olarak aldi ve ozel
gorelilik kuruldu. Zaman genlesmesi, boy kisalmasi ve es zamanliligin
goreceliligi bu tek deneysel gercegin zorunlu sonuclaridir.
""", """
Michelson and Morley (1887) looked for a direction-dependent speed of
light caused by Earth's motion through the aether. No shift was found. The
speed of light is independent of the observer's motion; Einstein took this
as a postulate in 1905 and special relativity follows.
""",
  eqs=["c = sabit (tum eylemsiz cercevelerde)", "γ = 1/√(1-v²/c²)"],
  ex_tr=["Beklenen serit kaymasi Δ ≈ 2L·v²/(λc²) idi. L = 11 m, v = 30 km/s "
         "(Dunya'nin yorunge hizi), λ = 500 nm icin bu yaklasik 0,4 serit "
         "eder — duzenegin duyarliligi bunun cok ustundeydi. Yine de sifir "
         "olctuler."],
  ex_en=["The expected fringe shift was ~0.4 fringes, well within the "
         "apparatus's sensitivity; the measured shift was zero."],
  kw="michelson morley|esir deneyi|isik hizi sabit|aether|"
     "gorelilik deneysel kanit|isik hizi olcumu",
  related="ozel_gorelilik"),

T("fotoelektrik_deney", "Fotoelektrik Olay (Deney)", "Photoelectric Effect", """
**Soru:** Isik bir metalden elektron koparabilir mi, kopariyorsa neye
bagli?

**Klasik beklenti:** Isik dalgaysa, siddeti artirildikca elektronlar daha
cok enerji almalidir. Yeterince beklerseniz sonunda kopmalidirlar; kopma
icin "esik frekans" olmamalidir.

**Gozlem (Lenard 1902, Millikan 1916):**
1. Esik frekansin ALTINDA, isik ne kadar parlak olursa olsun elektron
   kopmaz.
2. Esigin ustunde, kopan elektronun MAKSIMUM kinetik enerjisi frekansla
   dogrusal artar; siddet yalnizca elektron SAYISINI artirir.
3. Kopma anidir (gecikme yok).

**Einstein'in aciklamasi (1905):** Isik, enerjisi E = hf olan paketler
(fotonlar) halinde gelir. Bir foton bir elektrona carpar; enerjisi cikis
isini W'dan buyukse elektron kopar:
    K_max = hf - W

**Millikan'in olcumu:** Grafik gercekten dogru ciktI ve egimden h sabiti
olculdu — Planck'in isinim yasasindan bagimsiz olarak ayni deger.

**Ne degistirdi:** Isigin kuantumlanmasi kabul edildi. Einstein Nobel'i
gorelilikle degil, bu calismayla aldi.
""", """
Below a threshold frequency no electrons are emitted no matter how bright
the light; above it the maximum kinetic energy grows linearly with
frequency while intensity only changes the count. Einstein (1905) explained
this with light quanta, K_max = hf - W; Millikan measured h from the slope.
""",
  eqs=["K_max = h·f - W", "f_esik = W/h"],
  ex_tr=["Cikis isi 2,3 eV olan sodyuma 400 nm (3,1 eV) isik dusurulurse "
         "K_max = 3,1 - 2,3 = 0,8 eV olur. 600 nm (2,07 eV) ile hicbir "
         "elektron kopmaz — isik ne kadar parlak olursa olsun."],
  ex_en=["For a 2.3 eV work function, 400 nm light gives K_max = 0.8 eV, "
         "while 600 nm ejects nothing regardless of intensity."],
  kw="fotoelektrik deney|millikan fotoelektrik|isik kuantumu kaniti|"
     "esik frekans|photoelectric experiment|einstein 1905",
  related="kuantum_temelleri"),

T("millikan_yag", "Millikan Yağ Damlası Deneyi", "Millikan Oil-Drop Experiment", """
**Soru:** Elektrik yuku surekli mi, yoksa en kucuk bir birimi var mi?

**Duzenek (1909):** Kucuk yag damlaciklari iki yuklu plaka arasina
puskurtulur. Damlalar surtunmeyle yuklenir. Elektrik alan kapaliyken damla
duser ve hava direnci yuzunden sabit bir limit hiza ulasir — buradan
yaricapi ve kutlesi bulunur. Alan acilinca damla yavaslar, durur ya da
yukselir; dengedeki alan degerinden yuku hesaplanir:
    qE = mg  →  q = mg/E

**Gozlem:** Olculen yukler rastgele degildi. Hepsi ortak bir degerin TAM
KATLARIYDI: e ≈ 1,6×10⁻¹⁹ C.

**Sonuc:** Elektrik yuku kuantumlanmistir. Temel yuk birimi e'dir.

**Neden onemli:** Thomson e/m oranini olcmustu; Millikan e'yi olcunce
elektronun KUTLESI de bulunabildi (m = 9,11×10⁻³¹ kg).

**Durustluk notu:** Millikan bazi damlalari defterinde "kotu" diye
isaretleyip disarida birakti; bu, bilim tarihinde veri seciciligi
tartismalarinin klasik ornegidir. Sonucu daha sonraki bagimsiz olcumlerle
dogrulanmistir, ama yontem elestirisi hakli bir uyaridir.
""", """
Millikan (1909) balanced charged oil drops in an electric field and found
every measured charge to be an integer multiple of e ≈ 1.6e-19 C, proving
charge quantisation. Combined with Thomson's e/m this gave the electron
mass. His selective exclusion of "bad" drops remains a classic case study
in data handling.
""",
  eqs=["q·E = m·g", "q = n·e", "e ≈ 1,602×10⁻¹⁹ C"],
  ex_tr=["Kutlesi 3,2×10⁻¹⁵ kg olan bir damla, 1,0×10⁵ V/m'lik alanda "
         "havada asili duruyorsa: q = mg/E = (3,2×10⁻¹⁵ · 9,81)/10⁵ "
         "≈ 3,1×10⁻¹⁹ C. Bu, 2e'ye karsilik gelir — damla iki fazla "
         "elektron tasiyor."],
  ex_en=["A drop suspended at 1e5 V/m with m = 3.2e-15 kg carries "
         "q ≈ 3.1e-19 C, i.e. two elementary charges."],
  kw="millikan|yag damlasi|temel yuk olcumu|yuk kuantumlanmasi|"
     "elektron yuku deneyi|oil drop",
  related="elektrik_alan"),

T("rutherford_sacilma", "Rutherford Saçılma Deneyi", "Rutherford Scattering", """
**Soru:** Atomun ici nasil? Kutle ve pozitif yuk nasil dagilmis?

**O gunku model (Thomson, "uzumlu kek"):** Pozitif yuk atom hacmine
yayilmis, elektronlar icine gomulu. Bu modele gore alfa parcaciklari
folyodan neredeyse hic sapmadan gecmeliydi.

**Duzenek (Geiger-Marsden, 1909; yorum Rutherford, 1911):** Ince altin
folyoya alfa parcaciklari gonderildi, sapma acilari sayildi.

**Gozlem:** Cogu alfa neredeyse sapmadan gecti — ama yaklasik 8.000'de
biri 90°'den fazla saptI, bazilari GERI dondu.

**Rutherford'un sozu:** "Sanki 15 incilik bir topu mendil kagidina atip
geri donmesi gibiydi."

**Sonuc:** Pozitif yuk ve kutlenin neredeyse tamami, atomun cok kucuk bir
merkezinde toplanmistir — CEKIRDEK. Atom hacminin buyuk kismi bostur.
Cekirdek yaricapi ~10⁻¹⁵ m, atom yaricapi ~10⁻¹⁰ m: yuz bin kat fark.

**Ne degistirdi:** Cekirdekli atom modeli. Ardindan Bohr, bu cekirdegin
etrafindaki elektronlarin neden ici cokmedigini aciklamak icin kuantum
kosullarini getirdi.
""", """
Geiger and Marsden fired alpha particles at gold foil. Most passed nearly
undeflected but about one in 8000 scattered beyond 90°, some straight back.
Charge and mass must be concentrated in a tiny nucleus: nuclear radius
~1e-15 m versus atomic radius ~1e-10 m.
""",
  eqs=["b = (k·q₁q₂/2E)·cot(θ/2)", "R_cekirdek ≈ 1,2·A^(1/3) fm"],
  ex_tr=["5 MeV'lik bir alfa parcaciginin altin cekirdegine (Z = 79) en "
         "yakin yaklasma mesafesi: d = 2kZe²/E ≈ 4,5×10⁻¹⁴ m. Bu deger "
         "atom yaricapindan (10⁻¹⁰ m) binlerce kat kucuk — cekirdegin ne "
         "kadar kucuk oldugunun dogrudan olcusu."],
  ex_en=["A 5 MeV alpha reaches ~4.5e-14 m from a gold nucleus, thousands "
         "of times smaller than the atomic radius."],
  kw="rutherford|alfa sacilmasi|altin folyo deneyi|cekirdek kesfi|"
     "geiger marsden|atom modeli deney",
  related="nukleer|kuantum_temelleri"),

T("bell_testi", "Bell Testleri ve Dolanıklık", "Bell Tests and Entanglement", """
**Soru:** Kuantum mekaniginin rastgeleligi gercek mi, yoksa henuz
bilmedigimiz "gizli degiskenler" mi var?

**Einstein-Podolsky-Rosen (1935):** Dolanik iki parcacikta birini olcunce
digerinin durumu aninda belirleniyor. EPR bunu kuramin EKSIK oldugunun
kaniti saydi: parcaciklar ayrilmadan once cevaplari "yanlarinda
tasiyor" olmali.

**Bell'in katkisi (1964):** Bu bir felsefe tartismasi olmaktan cikti.
Bell, yerel gizli degiskenler varsa olculebilir bir esitsizligin saglanmasi
GEREKTIGINI gosterdi:  |S| ≤ 2  (CHSH bicimi). Kuantum mekanigi ise
|S| = 2√2 ≈ 2,83 ongorur.

**Deneyler:** Freedman-Clauser (1972), Aspect (1982), ve boslu klari
kapatan deneyler (2015, Delft/NIST/Viyana). Sonuc her seferinde ayni:
esitsizlik BOZULUYOR, kuantum ongorusu dogru cikiyor.

**Sonuc:** Yerel gizli degisken kuramlari elenmistir. Doga ya yerel
degildir ya da olcum oncesi belirli degerler tasimaz.

**Ne degildir:** Bu, isiktan hizli haberlesme demek DEGILDIR. Dolanik
ciftin her iki ucunda da sonuclar tek basina rastgeledir; bagi gormek icin
iki tarafin verilerini klasik yoldan karsilastirmak gerekir.

**2022 Nobel Fizik Odulu** Aspect, Clauser ve Zeilinger'e bu calismalar
icin verildi.
""", """
Bell (1964) turned the EPR debate into an experiment: local hidden-variable
theories require |S| <= 2, quantum mechanics predicts 2√2. Experiments from
Freedman-Clauser (1972) through the loophole-free tests of 2015 all violate
the inequality. Local realism is excluded — but no faster-than-light
signalling is possible. Nobel Prize 2022.
""",
  eqs=["|S| ≤ 2 (yerel gizli degisken)", "|S| = 2√2 ≈ 2,83 (kuantum)"],
  ex_tr=["CHSH deneyinde iki dedektor, dort farkli aci ciftinde ilinti "
         "olcer. Klasik sinir 2'dir; olculen deger 2,4 civarina ciktiginda "
         "bu, istatistiksel olarak yerel gizli degiskenlerin elenmesi "
         "demektir."],
  ex_en=["Measured CHSH values around 2.4 exceed the classical bound of 2."],
  kw="bell testi|bell esitsizligi|dolaniklik deneyi|epr|chsh|"
     "aspect deneyi|yerel gercekcilik|entanglement experiment",
  related="kuantum_temelleri|simetri"),

T("kutle_cekim_dalgasi_gozlem", "Kütle Çekim Dalgalarının Gözlenmesi",
  "Detection of Gravitational Waves", """
**Soru:** Einstein'in 1916'da ongordugu uzayzaman dalgalanmalari gercek mi?

**Zorluk:** Etki inanilmaz kucuk. Gecen bir dalga, 4 km'lik bir kolun
boyunu bir protonun binde biri kadar degistirir (ΔL/L ~ 10⁻²¹).

**Duzenek (LIGO):** Dev bir Michelson interferometresi. Iki dik kol, lazer
isigi, ve kollardaki uzunluk farkinin girisimde yarattigi degisim olculur.
Iki ayri gozlemevi (Hanford ve Livingston, 3.000 km arayla) ayni sinyali
gormeli — yerel gurultu boylece elenir.

**Ilk gozlem (14 Eylul 2015, GW150914):** Iki kara deligin (36 ve 29 gunes
kutlesi) birlesmesi. Sinyal, kuramin ongordugu "cirp" bicimini — frekansi
ve genligi artan sonra aniden kesilen dalga — birebir tuttu. Yaklasik 3
gunes kutlesi enerjiye donusup dalga olarak yayilmisti.

**Cok haberci astronomi (2017, GW170817):** Iki notron yildizinin
birlesmesi hem kutle cekim dalgasi hem gama isini patlamasi hem gorunur
isik olarak gozlendi. Ayni olayin uc farkli haberciyle goruldugu ilk andi;
ayrica kutle cekim dalgalarinin isik hiziyla yayildigi dogrulandi.

**Ne degistirdi:** Gokyuzune bakmanin yeni bir yolu acildi — isik
yaymayan olaylar (kara delik birlesmeleri) artik gozlenebiliyor.
2017 Nobel Fizik Odulu.
""", """
LIGO detects strains of order 1e-21 with kilometre-scale interferometers.
GW150914 (2015) matched the predicted chirp of two merging black holes;
GW170817 (2017) was seen in gravitational waves, gamma rays and light,
confirming they travel at the speed of light. Nobel Prize 2017.
""",
  eqs=["h = ΔL/L ~ 10⁻²¹", "E_yayilan ≈ 3 M_gunes·c²"],
  ex_tr=["4 km'lik LIGO kolunda h = 10⁻²¹ gerinim, ΔL = 4×10³ · 10⁻²¹ "
         "= 4×10⁻¹⁸ m demektir — proton yaricapinin (10⁻¹⁵ m) binde biri. "
         "Bu duyarlilik, lazer isiginin kollarda yuzlerce kez gidip "
         "gelmesiyle saglanir."],
  ex_en=["A strain of 1e-21 over a 4 km arm is ΔL = 4e-18 m, a thousandth "
         "of a proton radius."],
  kw="ligo|kutle cekim dalgasi gozlem|gw150914|gravitational wave detection|"
     "interferometre|notron yildizi birlesmesi|cok haberci",
  related="genel_gorelilik|astro"),

T("cmb_gozlem", "Kozmik Mikrodalga Arka Plan", "Cosmic Microwave Background", """
**Soru:** Evren sicak ve yogun bir baslangictan mi geldi?

**Ongoru (Gamow, Alpher, Herman, 1948):** Buyuk Patlama dogruysa, erken
evrendeki sicak plazmanin isinimi bugun sogumus olarak her yonden
gelmelidir.

**Kesif (Penzias ve Wilson, 1965):** Bell Labs'ta bir anten, hangi yone
cevrilirse cevrilsin giderilemeyen bir gurultu veriyordu. Anteni
temizlediler, kuslari kovdular — gurultu kaldi. Bu gurultu, evrenin
kendisiydi: T ≈ 2,7 K'lik isinim.

**COBE (1992):** Tayf, olculebilecek en mukemmel kara cisim isinimi
egrisine uydu — Buyuk Patlama'nin en guclu kaniti. Ayrica 10⁻⁵
mertebesinde sicaklik dalgalanmalari bulundu: bugunku galaksilerin
tohumlari.

**WMAP ve Planck (2003-2018):** Dalgalanmalarin acisal tayfi olculdu.
Buradan evrenin yasi (13,8 milyar yil), duz oldugu ve icerigi (yaklasik
%5 siradan madde, %27 karanlik madde, %68 karanlik enerji) cikarildi.

**Ne ogretir:** Kozmoloji, spekulasyondan HASSAS OLCUM bilimine bu
gozlemlerle gecti. 1978 ve 2006 Nobel Fizik Odulleri bu calismalara
verildi.
""", """
Penzias and Wilson (1965) found an irremovable 2.7 K background from every
direction. COBE (1992) showed a near-perfect blackbody spectrum plus 1e-5
temperature fluctuations; WMAP and Planck turned those fluctuations into
precise numbers: age 13.8 Gyr, flat geometry, 5% ordinary matter, 27% dark
matter, 68% dark energy.
""",
  eqs=["T_CMB = 2,725 K", "λ_tepe = b/T (Wien)", "ΔT/T ~ 10⁻⁵"],
  ex_tr=["Wien yasasiyla: λ_tepe = 2,898×10⁻³/2,725 ≈ 1,06 mm — mikrodalga "
         "bolgesi. Isinim evrenin 380.000 yasindayken salindi; o zaman "
         "sicaklik ~3000 K idi, evren o gunden beri yaklasik 1100 kat "
         "genisledigi icin bugun 2,7 K goruyoruz."],
  ex_en=["Wien's law gives a peak near 1.06 mm; the radiation was released "
         "at ~3000 K and has redshifted by a factor ~1100."],
  kw="kozmik mikrodalga|cmb|penzias wilson|cobe|planck uydusu|"
     "buyuk patlama kaniti|arka plan isinimi",
  related="astro|genel_gorelilik"),

T("higgs_kesfi", "Higgs Bozonunun Keşfi", "Discovery of the Higgs Boson", """
**Soru:** Temel parcaciklar kutleyi nereden aliyor?

**Sorun:** Ayar simetrisi, etkilesim tasiyicilarinin KUTLESIZ olmasini
gerektirir. Ama zayif etkilesimin tasiyicilari (W ve Z) cok agirdir.

**Cozum onerisi (1964, Brout-Englert-Higgs ve digerleri):** Uzayin her
yerinde sifirdan farkli degeri olan bir alan bulunsun. Yasalar simetrik
kalir ama bu alanin TABAN DURUMU simetrik olmaz — kendiliginden simetri
kirilmasi. Parcaciklar bu alanla etkilestikce kutle kazanir. Kurama gore
alanin kendi uyarilmasi da bir parcacik olarak gorulmelidir.

**Arama:** Kutlesi kuram tarafindan sabitlenmemisti; on yillarca
hizlandiricilarda tarandi ve dislandi.

**Kesif (4 Temmuz 2012, CERN/LHC):** ATLAS ve CMS deneyleri, birbirinden
bagimsiz olarak ~125 GeV'de yeni bir parcacik gorduklerini duyurdu.
Istatistiksel anlamlilik 5σ esigini asti (rastlanti olma olasiligi
milyonda birden az).

**Nasil goruluyor:** Higgs neredeyse aninda bozunur; dogrudan gorulmez.
Bozunma urunleri sayilir — ozellikle iki foton (H → γγ) ve dort lepton
(H → ZZ → 4ℓ) kanallarinda, beklenen fon uzerinde bir tepe olarak.

**Sonuc:** Standart Model'in son eksik parcasi yerine oturdu. 2013 Nobel
Fizik Odulu Englert ve Higgs'e verildi.
""", """
Gauge symmetry demands massless carriers, yet W and Z are heavy. The
Brout-Englert-Higgs mechanism gives mass through spontaneous symmetry
breaking of a field with non-zero vacuum value. ATLAS and CMS independently
found the predicted boson at ~125 GeV on 4 July 2012 at 5 sigma, seen as a
peak in the two-photon and four-lepton channels. Nobel Prize 2013.
""",
  eqs=["m_H ≈ 125 GeV/c²", "H → γγ", "H → ZZ → 4ℓ", "anlamlilik ≥ 5σ"],
  ex_tr=["5σ ne demek? Gozlenen fazlaligin yalnizca istatistiksel dalgalanma "
         "olma olasiligi yaklasik 1/3.500.000'dir. Parcacik fiziginde "
         "'kesif' ilan etmek icin gelenek olarak bu esik aranir; 3σ "
         "yalnizca 'kanit' sayilir."],
  ex_en=["5 sigma corresponds to a chance of about 1 in 3.5 million; 3 sigma "
         "counts only as evidence."],
  kw="higgs|higgs bozonu kesfi|lhc|cern 2012|atlas cms|"
     "kutle mekanizmasi|simetri kirilmasi deney",
  related="alan_kurami|simetri"),
]
