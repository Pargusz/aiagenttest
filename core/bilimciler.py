# -*- coding: utf-8 -*-
"""Fizikciler: hayatlari, calismalari ve NE DEGISTIRDIKLERI.

Bir ogrenci "Feynman kimdi" ya da "Emmy Noether ne yapti" diye sorabilir.
Bunlar fizik sorularidir: bir kuramin kim tarafindan, hangi soruyu
cozmek icin, hangi zorluga ragmen ortaya konuldugunu bilmek konuyu
anlamayi kolaylastirir.

Her kayit ayni yapida: kim, ne yapti, hangi problemi cozdu, bugun nerede
karsimiza cikiyor. Anekdot degil, FIZIK anlatiyoruz.
"""
from .knowledge import T

BILIMCILER = [

T("newton_kim", "Isaac Newton (1643-1727)", "Isaac Newton", """
**Ne yapti:** Hareket yasalarini ve evrensel kutle cekimini tek cercevede
birlestirdi; bunun icin gereken matematigi (kalkulus) de kendisi
gelistirdi.

**Cozdugu problem:** O gune kadar gokyuzu ve yeryuzu ayri yasalara tabi
sayiliyordu. Newton, elmayi dusuren kuvvetle Ay'i yorungede tutan kuvvetin
AYNI kuvvet oldugunu gosterdi. Bu, fizigin ilk buyuk BIRLESTIRMESIDIR.

**Yontemi:** Kepler'in gozlemsel yasalarindan yola cikip ters kare
yasasini turetti, sonra bu yasadan Kepler'in yasalarini geri cikardi —
kuramin sinandigi ilk ornek.

**Bugun nerede:** Uydu yorungeleri, kopru hesaplari, arac dinamigi.
Gunluk hizlarda Newton mekanigi hala kullaniliyor; gorelilik onu
gecersiz kilmadi, SINIRINI cizdi.

**Insan tarafi:** Principia'yi Halley'in israriyla yazdi. Optikte de
calisti; beyaz isigin renklere ayrildigini prizma deneyleriyle gosterdi.
""", """
Newton unified terrestrial and celestial motion, inventing calculus along
the way. He derived the inverse-square law from Kepler's observations and
then rederived Kepler's laws from it — the first great test of a physical
theory.
""",
  eqs=["F = m·a", "F = G·m₁m₂/r²"],
  ex_tr=["Ay'in merkezcil ivmesi: a = v²/r. Ay'in yorunge yaricapi "
         "3,84×10⁸ m, periyodu 27,3 gun. Hesap 2,72×10⁻³ m/s² verir. "
         "Yeryuzunde g = 9,81 m/s². Oran 3600 ≈ 60². Ay da Dunya "
         "yaricapinin 60 kati uzakta. Ters kare yasasinin ilk kaniti budur."],
  ex_en=["The Moon's centripetal acceleration is 1/3600 of g, and it is 60 "
         "Earth radii away — the inverse-square law's first check."],
  kw="newton kimdir|isaac newton|newton kim|newton hayati|principia",
  related="newton_yasalari|kutle_cekim"),

T("einstein_kim", "Albert Einstein (1879-1955)", "Albert Einstein", """
**Ne yapti:** 1905'te bir yilda dort makale yayimladi ve her biri ayri bir
alani degistirdi: fotoelektrik olay (isik kuantasi), Brown hareketi
(atomlarin varligi), ozel gorelilik, E = mc².

**Cozdugu problem:** Maxwell denklemleri isik hizini SABIT veriyordu ama
Newton mekanigi hizlarin toplanmasini gerektiriyordu. Ikisi bir arada
duramazdi. Einstein, Newton'un mutlak zaman varsayimindan vazgecti —
denklemleri degil, VARSAYIMI degistirdi.

**Genel gorelilik (1915):** Kutle cekimi bir kuvvet degil, uzayzamanin
egriligidir. 1919 gunes tutulmasinda isigin Gunes'in yaninda buküldügü
olculdu ve kuram dogrulandi.

**Bugun nerede:** GPS (hem ozel hem genel gorelilik duzeltmesi olmadan
gunde kilometrelerce hata), nukleer enerji (E = mc²), kara delikler,
kutle cekim dalgalari.

**Ilginc:** Nobel'i gorelilikle degil FOTOELEKTRIK OLAYLA aldi. Kuantum
mekaniginin olasiliksal yorumunu ise omru boyunca kabul etmedi;
"Tanri zar atmaz" sozü bu tartismadandir. EPR makalesi (1935) bu
itirazdan dogdu ve ironik bicimde bugun kuantum bilgi kuraminin temeli.
""", """
In 1905 Einstein published four papers that each changed a field:
photoelectric effect, Brownian motion, special relativity, E = mc². He
resolved the clash between Maxwell and Newton by abandoning absolute time.
General relativity (1915) recast gravity as spacetime curvature, confirmed
in 1919. His Nobel was for the photoelectric effect, not relativity.
""",
  eqs=["E = mc²", "E = hf - W", "Gμν = 8πG/c⁴ · Tμν"],
  ex_tr=["GPS uydusu yerde kalan saate gore: ozel gorelilik yuzunden gunde "
         "7 mikrosaniye GERI, genel gorelilik yuzunden 45 mikrosaniye ILERI "
         "gider. Net 38 mikrosaniye. Duzeltilmezse konum hatasi gunde "
         "yaklasik 11 km olurdu."],
  ex_en=["GPS clocks run 38 microseconds fast per day; uncorrected this is "
         "an 11 km position error."],
  kw="einstein kimdir|albert einstein|einstein kim|einstein hayati|"
     "1905 mucize yili|einstein nobel",
  related="ozel_gorelilik|genel_gorelilik|fotoelektrik_deney"),

T("noether_kim", "Emmy Noether (1882-1935)", "Emmy Noether", """
**Ne yapti:** Simetri ile korunum yasalari arasindaki bagi kanitladi
(Noether teoremi, 1918). Ayni zamanda modern soyut cebirinin
kuruculardandir.

**Cozdugu problem:** Genel gorelilikte enerji korunumu tuhaf davraniyordu;
Hilbert ve Klein bu sorunu Noether'e goturdu. Noether yalnizca o sorunu
cozmedi — TUM korunum yasalarinin nereden geldigini gosterdi.

**Neden bu kadar onemli:** Korunum yasalari artik deneyle bulunmus
kurallar degil, simetrilerin zorunlu sonucudur. Modern fizigin calisma
bicimi budur: once simetri secilir, kuram ondan insa edilir. Standart
Model bu yolla kurulmustur.

**Karsilastigi engeller:** Kadin oldugu icin universitede resmi kadro
alamadi; yillarca Hilbert'in adi altinda ucretsiz ders verdi. 1933'te
Nazi Almanyasi'ndan ayrilmak zorunda kaldi, ABD'ye gitti ve iki yil sonra
oldu. Einstein, olumunun ardindan yazdigi mektupta onu "matematik
tarihinin en onemli yaratici dehalarindan biri" olarak andi.
""", """
Noether proved that every continuous symmetry yields a conservation law
(1918), answering a puzzle about energy conservation in general relativity
and revealing where all conservation laws come from. Denied a formal
academic post because she was a woman, she lectured for years under
Hilbert's name.
""",
  eqs=["surekli simetri → korunan buyukluk"],
  ex_tr=["Fizik yasalari dun de bugun de ayniysa (zamanda oteleme "
         "simetrisi) ENERJI korunur. Bu bir gozlem degil, teoremin "
         "sonucudur. Evrenin genisledigi kozmolojik olceklerde bu simetri "
         "tam gecerli olmadigi icin enerji korunumu da alisildik bicimde "
         "yazilamaz."],
  ex_en=["Time-translation symmetry implies energy conservation; where that "
         "symmetry fails (expanding cosmology), so does the usual statement "
         "of energy conservation."],
  kw="emmy noether kimdir|noether kim|noether hayati|noether teoremi kim",
  related="noether|simetri"),

T("curie_kim", "Marie Curie (1867-1934)", "Marie Curie", """
**Ne yapti:** Radyoaktivite kavramini tanimladi (terimi kendisi
turetti), polonyum ve radyum elementlerini kesfetti.

**Cozdugu problem:** Becquerel uranyum tuzlarinin fotograf plakasini
kararttigini bulmustu ama sebebi bilinmiyordu. Curie, isimayi elektrometreyle
NICEL olarak olctu ve sunu gosterdi: isima miktari yalnizca uranyum
miktarina bagli; sicaklik, basinc ya da kimyasal bilesim etkilemiyor.
Demek ki kaynak molekullerde degil, ATOMUN KENDISINDEDIR. Bu, atomun
bolunmez oldugu inancini yikan olculerden biridir.

**Yontemi:** Tonlarca pekblend cevherini yillarca isleyerek bir gram
radyum elde etti — laboratuvar emeginin klasik ornegidir.

**Bugun nerede:** Radyoterapi, tibbi goruntuleme, radyometrik yas tayini.
Birinci Dunya Savasi'nda seyyar rontgen araclari kurdu.

**Ilk ve tek:** Iki farkli bilim dalinda Nobel alan tek kisi (1903 fizik,
1911 kimya). Radyasyonun zararlari o donemde bilinmiyordu; not defterleri
bugun hala radyoaktiftir ve kursun kutularda saklanir.
""", """
Curie defined radioactivity, discovered polonium and radium, and showed
quantitatively that emission depends only on the amount of the element —
not on temperature, pressure or chemical form — proving the source lies in
the atom itself. She remains the only person with Nobel Prizes in two
different sciences.
""",
  eqs=["A = λN", "N(t) = N₀·e^(-λt)"],
  ex_tr=["Radyum-226'nin yari omru 1600 yil. 1 gram radyumda yaklasik "
         "2,7×10²¹ atom var; aktivite A = λN hesabi 3,7×10¹⁰ bozunma/saniye "
         "verir. Bu deger tam olarak 1 CURIE biriminin tanimidir."],
  ex_en=["One gram of radium-226 gives 3.7e10 decays per second — the "
         "definition of the curie."],
  kw="marie curie kimdir|curie kim|radyoaktivite kesfi|polonyum radyum",
  related="yari_omur|nukleer"),

T("feynman_kim", "Richard Feynman (1918-1988)", "Richard Feynman", """
**Ne yapti:** Kuantum elektrodinamigini (QED) yeniden formule etti;
Feynman diyagramlarini gelistirdi. Yol integrali formalizmi onun eseridir.

**Cozdugu problem:** QED hesaplarinda sonsuzluklar cikiyordu.
Renormalizasyon bu sonsuzluklari denetim altina aldi ve QED, fizigin en
hassas dogrulanmis kurami oldu: elektronun manyetik momenti 12 haneye
kadar deneyle uyusuyor.

**Feynman diyagramlari:** Karmasik integralleri CIZIME cevirdi. Bir cizgi
bir parcacigi, bir kose bir etkilesimi gosterir. Bu, hesabi yapilabilir
kildigi kadar duşunulebilir de kildi — bugun parcacik fiziginin ortak
dili.

**Yol integrali:** Parcacik tek bir yol izlemez; MUMKUN TUM yollarin
katkisi toplanir. Klasik yol, bu toplamda katkilarin ust uste bindigi
yoldur — en kucuk etki ilkesinin kuantum karsiligi.

**Ogretmenligi:** "Feynman Dersleri" hala okunuyor. Ilkesi suydu: bir
konuyu birinci sinif ogrencisine anlatamiyorsaniz, gercekten
anlamamissinizdir.

**Challenger:** 1986 mekigi kazasi komisyonunda, O-ring contasinin sogukta
esnekligini kaybettigini bir bardak buzlu suya batirarak canli yayinda
gosterdi.
""", """
Feynman reformulated QED with diagrams and the path-integral approach,
where a particle's amplitude sums over all possible paths and the classical
path is where contributions add constructively. QED became the most
precisely verified theory in physics. He was also a legendary teacher.
""",
  eqs=["genlik = Σ e^(iS/ħ)", "klasik yol: δS = 0"],
  ex_tr=["Yol integralinde her yolun katkisi e^(iS/ħ). Gunluk olceklerde "
         "S >> ħ oldugundan komsu yollarin fazlari hizla degisir ve "
         "birbirini goturur; yalnizca S'nin duragan oldugu yolun cevresi "
         "ayakta kalir. Klasik mekanik bu sekilde kuantumdan cikar."],
  ex_en=["Paths contribute e^(iS/hbar); for S >> hbar all but the stationary "
         "path cancel, recovering classical mechanics."],
  kw="feynman kimdir|richard feynman|feynman diyagrami|yol integrali|"
     "feynman dersleri|qed kim",
  related="alan_kurami|varyasyon"),

T("maxwell_kim", "James Clerk Maxwell (1831-1879)", "James Clerk Maxwell", """
**Ne yapti:** Elektrik, manyetizma ve isigi tek kuramda birlestirdi.
Ayrica gazlarin kinetik kuramina Maxwell hiz dagilimini kazandirdi.

**Cozdugu problem:** Faraday'in deneysel bulgulari (alan cizgileri,
indukleme) matematiksel bir cerceveden yoksundu. Maxwell bunlari
denklemlere dokerken bir tutarsizlik fark etti: Ampere yasasi yuk
korunumuyla celisiyordu. Eksik terimi (yer degistirme akimi) EKLEYINCE
denklemler dalga cozumu verdi.

**Ongoru:** Dalganin hizi c = 1/√(μ₀ε₀) cikiyordu. Bu iki sabit tamamen
elektriksel ve manyetik olcumlerden geliyordu; iclerinde isikla ilgili
hicbir sey yoktu. Sonuc olculen isik hiziyla ayniydi. Maxwell "isik bir
elektromanyetik dalgadir" dedi — KURAM, isigin ne oldugunu ongordu.

**Dogrulanmasi:** Hertz, 1887'de radyo dalgalarini laboratuvarda uretip
olctu. Radyo, radar, mikrodalga, kablosuz iletisim — hepsi bu ongorunun
uzantisi.

**Kinetik kuram:** Gaz molekullerinin hizlarinin bir DAGILIMI oldugunu
gosterdi. Istatistiksel fizigin ilk buyuk basarisi.
""", """
Maxwell turned Faraday's experiments into equations, spotted that Ampere's
law violated charge conservation, and added the displacement current. The
equations then predicted waves travelling at 1/sqrt(mu0 eps0) — the speed
of light. Hertz produced such waves in 1887.
""",
  eqs=["c = 1/√(μ₀ε₀)", "∇×B = μ₀J + μ₀ε₀ ∂E/∂t"],
  ex_tr=["Maxwell'in kullandigi degerler: μ₀ = 4π×10⁻⁷ ve ε₀ = 8,854×10⁻¹². "
         "c = 1/√(μ₀ε₀) = 2,998×10⁸ m/s. O donemde isik hizi Fizeau "
         "tarafindan yaklasik 3,15×10⁸ m/s olculmustu — yeterince yakin bir "
         "uyum, ve gerisi tarih."],
  ex_en=["1/sqrt(mu0 eps0) = 2.998e8 m/s matched Fizeau's measured speed of "
         "light."],
  kw="maxwell kimdir|james clerk maxwell|maxwell kim|maxwell hayati",
  related="maxwell|elektromanyetik_dalga"),

T("planck_kim", "Max Planck (1858-1947)", "Max Planck", """
**Ne yapti:** Kara cisim isinimini aciklamak icin enerjinin KESIKLI
paketler halinde alinip verildigini varsaydi (1900). Kuantum fiziginin
baslangic noktasi budur.

**Cozdugu problem:** Klasik fizik, kara cismin yaydigi enerjinin kisa
dalga boylarinda sonsuza gitmesini ongoruyordu ("morotesi felaketi").
Deney bunu kesinlikle desteklemiyordu.

**Cozum:** E = hf varsayimi. Planck bunu bastan bir fizik gercegi olarak
degil, "hesabi kurtaran matematiksel bir care" olarak gordu ve yillarca
klasik bir aciklama aradi. Einstein 1905'te fotoelektrik olayla bunun
gercekten fiziksel oldugunu gosterdi.

**Bugun nerede:** Planck sabiti h, 2019'dan beri KILOGRAMIN tanimidir.
Yani kutle biriminin kendisi artik bu sabite dayaniyor.

**Kisisel:** Nazi doneminde Almanya'da kaldi ve bilim insanlarini korumaya
calisti; oglu Erwin, Hitler'e suikast girisimine katildigi icin 1945'te
idam edildi.
""", """
Planck introduced E = hf in 1900 to fix the ultraviolet catastrophe,
regarding it at first as a mathematical device rather than physics.
Einstein showed in 1905 that it was real. Since 2019 Planck's constant
defines the kilogram.
""",
  eqs=["E = h·f", "h = 6,62607015×10⁻³⁴ J·s"],
  ex_tr=["Morotesi felaketi: klasik Rayleigh-Jeans yasasi yayilan gucu "
         "λ⁻⁴ ile buyutur, yani kisa dalga boyunda sonsuza gider. Planck'in "
         "kuantum varsayimi yuksek frekansli modlarin uyarilmasini "
         "zorlastirir (E = hf buyuk olur) ve egri tepe yapip duser — "
         "olculen bicim tam da budur."],
  ex_en=["Quantisation suppresses high-frequency modes and turns the "
         "diverging classical curve into the observed peaked spectrum."],
  kw="planck kimdir|max planck|planck sabiti kim|kuantum baslangici|"
     "morotesi felaketi",
  related="kara_cisim|kuantum_temelleri"),

T("bohr_kim", "Niels Bohr (1885-1962)", "Niels Bohr", """
**Ne yapti:** Atomun kuantum modelini kurdu (1913); Kopenhag yorumunun
mimari oldu.

**Cozdugu problem:** Rutherford'un cekirdekli atomu klasik fizige gore
KARARSIZDI — donen elektron isima yayarak enerji kaybeder ve saniyenin
cok kucuk bir kesrinde cekirdege dusmeliydi. Ustelik atomlarin yaydigi
isik surekli degil, KESIKLI cizgiler halindeydi.

**Cozum:** Elektron yalnizca acisal momentumun ħ'nin tam katı oldugu
yorungelerde bulunabilir; bu yorungelerde isima YAPMAZ. Bir duzeyden
digerine atlarken aradaki enerji farki foton olarak yayilir. Hidrojen
spektrumu boylece TAM olarak aciklandi.

**Sinirlari:** Model tek elektronlu atomlarda calisir; helyumda bile
yetersiz kalir. 1925-26'da tam kuantum mekanigi (Heisenberg, Schrödinger)
onun yerini aldi. Ama fikri — kesikli enerji duzeyleri — kaldi.

**Einstein ile tartismasi:** Yillar suren Bohr-Einstein tartismasi kuantum
mekaniginin ne anlama geldigi uzerineydi. Bohr'un tamamlayicilik ilkesi
ve olcumun rolu bu tartismada sekillendi.
""", """
Bohr's 1913 model postulated stable quantised orbits, explaining why the
nuclear atom does not collapse and why hydrogen emits discrete lines. It
fails beyond one electron, but the idea of discrete energy levels
survived. The Bohr-Einstein debates shaped the interpretation of quantum
mechanics.
""",
  eqs=["m·v·r = n·ħ", "E_n = -13,6·Z²/n² eV", "hf = E₂ - E₁"],
  ex_tr=["Hidrojende n=3'ten n=2'ye gecis: ΔE = 13,6(1/4 - 1/9) = 1,89 eV. "
         "λ = hc/ΔE = 656 nm — Balmer serisinin kirmizi H-alfa cizgisi. "
         "Gokyuzundeki kirmizi nebulalarin rengi tam olarak budur."],
  ex_en=["The n=3 to n=2 transition gives 1.89 eV, i.e. 656 nm — the red "
         "H-alpha line seen in nebulae."],
  kw="bohr kimdir|niels bohr|bohr modeli kim|kopenhag yorumu",
  related="bohr_E|kuantum_temelleri"),
]
