# -*- coding: utf-8 -*-
"""Lisansustu cekirdek: elektrodinamik, kuantum formalizmi, katihal,
parcacik fizigi ve matematiksel yontemler.

Cekirdek 44 konuya cikmisti (lisans + analitik mekanik + kilit deneyler).
Bir fizik profesorunun gunluk dilinde gecen ama hala eksik olan alanlar
burada: Maxwell denklemlerinin butunu, kuantum formalizmi (operatorler,
ozdeger problemi, pertürbasyon), bant kurami, Standart Model ve fizigin
matematiksel araclari.
"""
from .knowledge import T

ILERI_KONULAR = [

T("maxwell", "Maxwell Denklemleri", "Maxwell's Equations", """
Elektrik ve manyetizmanin tamamini dort denklemle anlatan cerceve.

**1. Gauss yasasi (elektrik):** ∇·E = ρ/ε₀
Elektrik alan cizgileri yuklerden baslar ve yuklerde biter. Kapali bir
yuzeyden gecen toplam aki, yalnizca icerideki yuke baglidir.

**2. Gauss yasasi (manyetizma):** ∇·B = 0
Manyetik tekkutup YOKTUR. Bir miknatisi ikiye bolerseniz iki miknatis
elde edersiniz, ayri kuzey ve guney kutbu degil.

**3. Faraday yasasi:** ∇×E = -∂B/∂t
Degisen manyetik alan elektrik alan dogurur. Eksi isareti Lenz yasasidir:
dogan akim, kendisini doguran degisime karsi koyar.

**4. Ampere-Maxwell yasasi:** ∇×B = μ₀J + μ₀ε₀ ∂E/∂t
Akim manyetik alan dogurur — ve Maxwell'in ekledigi ikinci terim: degisen
ELEKTRIK alani da manyetik alan dogurur. Bu terim olmadan denklemler yuk
korunumuyla celisir.

**En buyuk sonuc:** Bosluktaki denklemler (ρ = 0, J = 0) birlestirildiginde
dalga denklemi cikar ve dalganin hizi

    c = 1/√(μ₀ε₀) ≈ 3×10⁸ m/s

olur. Maxwell bu sayiyi hesapladiginda isik hiziyla ayni oldugunu gordu ve
"isik bir elektromanyetik dalgadir" sonucuna vardi — kuram, isigin ne
oldugunu ONGORDU.

**Ayar serbestligi:** E ve B, potansiyeller cinsinden yazilabilir
(E = -∇φ - ∂A/∂t, B = ∇×A). Potansiyeller tek degildir; ayar donusumu
altinda alanlar degismez. Bu serbestlik, kuantum alan kuraminin ayar
ilkesinin temelidir.
""", """
Maxwell's four equations: Gauss for E, no magnetic monopoles, Faraday's
induction, and Ampere-Maxwell with the displacement current. In vacuum they
combine into a wave equation with speed c = 1/sqrt(mu0 eps0), which matched
the measured speed of light — the theory predicted what light is.
""",
  eqs=["∇·E = ρ/ε₀", "∇·B = 0", "∇×E = -∂B/∂t",
       "∇×B = μ₀J + μ₀ε₀ ∂E/∂t", "c = 1/√(μ₀ε₀)"],
  ex_tr=["c = 1/√(μ₀ε₀) hesabi: μ₀ = 4π×10⁻⁷ T·m/A, ε₀ = 8,854×10⁻¹² F/m. "
         "Carpim 1,113×10⁻¹⁷, karekoku 3,336×10⁻⁹, tersi 2,998×10⁸ m/s. "
         "Iki elektrik olcumunden isik hizinin cikmasi, kuramin gucunu "
         "gosteren en carpici ornektir."],
  ex_en=["Computing 1/sqrt(mu0 eps0) from two electrical measurements gives "
         "2.998e8 m/s — the speed of light."],
  kw="manyetizma|manyetik alan|magnetism|magnetic field|elektrik ve manyetizma|elektromanyetizma|electromagnetism|maxwell denklemleri|maxwell|elektromanyetik kuram|gauss yasasi|"
     "ampere maxwell|yer degistirme akimi|isik elektromanyetik dalga",
  related="elektromanyetik_dalga|alan_kurami"),

T("kuantum_formalizm", "Kuantum Mekaniğinin Formalizmi",
  "Formalism of Quantum Mechanics", """
Kuantum mekaniginin matematiksel iskeleti dort postulata dayanir.

**1. Durum:** Sistemin durumu bir Hilbert uzayinda bir vektordur, |ψ⟩.
Normalizasyon ⟨ψ|ψ⟩ = 1'dir.

**2. Gozlenebilirler:** Olculebilir her buyukluk bir HERMITIAN operatore
karsilik gelir. Hermitian olmasi, ozdegerlerin gercel olmasini garanti
eder — olcum sonuclari gercel sayilardir.

**3. Olcum:** Bir olcumun sonucu, operatorun ozdegerlerinden biridir.
Ozdeger aᵢ'yi olcme olasiligi |⟨aᵢ|ψ⟩|² kadardir (Born kurali). Olcumden
sonra durum o ozduruma cokr.

**4. Zaman evrimi:** Olcum yapilmadigi surece durum Schrödinger
denklemine gore SUREKLI ve deterministik evrilir:
    iħ ∂|ψ⟩/∂t = Ĥ|ψ⟩

**Komutator:** [Â,B̂] = ÂB̂ - B̂Â. Iki operator komut ediyorsa (sifir
komutator) ayni anda kesin olculebilirler. Etmiyorsa belirsizlik bagintisi
gecerlidir:
    ΔA·ΔB ≥ ½|⟨[Â,B̂]⟩|
Konum ve momentum icin [x̂,p̂] = iħ olur ve buradan Δx·Δp ≥ ħ/2 cikar —
belirsizlik ilkesi bir postulat degil, formalizmin SONUCUDUR.

**Ozdeger problemi:** Ĥ|ψₙ⟩ = Eₙ|ψₙ⟩ denklemini cozmek, sistemin izinli
enerjilerini bulmak demektir. Kutuda parcacik, harmonik salinici ve
hidrojen atomu tam cozulebilen uc klasik ornektir.
""", """
Four postulates: states are Hilbert-space vectors; observables are
Hermitian operators; measurement yields an eigenvalue with probability
|<a|psi>|^2 and collapses the state; unmeasured evolution follows the
Schrodinger equation. The commutator [x,p] = i hbar yields the uncertainty
relation as a consequence, not a postulate.
""",
  eqs=["iħ ∂|ψ⟩/∂t = Ĥ|ψ⟩", "Ĥ|ψₙ⟩ = Eₙ|ψₙ⟩", "[x̂,p̂] = iħ",
       "ΔA·ΔB ≥ ½|⟨[Â,B̂]⟩|", "P(aᵢ) = |⟨aᵢ|ψ⟩|²"],
  ex_tr=["Kutuda parcacik (genislik L, sonsuz duvarlar): sinir kosullari "
         "ψ(0) = ψ(L) = 0, cozum ψₙ = √(2/L)·sin(nπx/L) ve "
         "Eₙ = n²π²ħ²/(2mL²). En dusuk enerji SIFIR DEGILDIR — hapsedilmis "
         "parcacik hic durgun olamaz, bu belirsizlik ilkesinin dogrudan "
         "sonucudur."],
  ex_en=["Particle in a box: E_n = n²π²ħ²/(2mL²); the ground state energy "
         "is not zero, a direct consequence of the uncertainty principle."],
  kw="kuantum formalizm|hilbert uzayi|operator|ozdeger problemi|"
     "komutator|born kurali|postulat|olcum problemi|schrodinger denklemi",
  related="belirsizlik|hamilton|kuantum_temelleri"),

T("perturbasyon", "Pertürbasyon Kuramı", "Perturbation Theory", """
Cok az kuantum problemi TAM cozulebilir. Gercek sistemler icin standart
yaklasim: cozulebilen bir probleme kucuk bir duzeltme eklemek.

**Kurulum:** Ĥ = Ĥ₀ + λV̂. Burada Ĥ₀ cozumunu bildigimiz kisim, V̂ kucuk
bozucu terim.

**Birinci mertebe enerji duzeltmesi:**
    Eₙ⁽¹⁾ = ⟨ψₙ⁰|V̂|ψₙ⁰⟩
Yani bozulmanin, bozulmamis durumdaki ORTALAMA degeri.

**Ikinci mertebe:**
    Eₙ⁽²⁾ = Σ_{m≠n} |⟨ψₘ⁰|V̂|ψₙ⁰⟩|² / (Eₙ⁰ - Eₘ⁰)
Taban durum icin payda hep negatiftir — taban durum enerjisi ikinci
mertebede HER ZAMAN asagi iter.

**Ne zaman calismaz:** Bozulmamis duzeyler dejenere ise (Eₙ⁰ = Eₘ⁰)
payda sifirlanir; dejenere pertürbasyon kurami gerekir. Ayrica bozulma
kucuk degilse seri yakinsamaz.

**Uygulamalar:** Zeeman etkisi (manyetik alanda duzey yarilmasi), Stark
etkisi (elektrik alanda), ince yapi, Lamb kaymasi. Kuantum
elektrodinamiginin en hassas ongoruleri (elektronun manyetik momenti,
12 haneye kadar dogru) pertürbasyon serisiyle hesaplanir.
""", """
Most quantum problems are not exactly solvable. Writing H = H0 + lambda V,
the first-order energy shift is the expectation value of V in the
unperturbed state; second order sums over intermediate states and always
lowers the ground state. Degeneracy requires the degenerate version.
""",
  eqs=["Ĥ = Ĥ₀ + λV̂", "Eₙ⁽¹⁾ = ⟨ψₙ⁰|V̂|ψₙ⁰⟩",
       "Eₙ⁽²⁾ = Σ |⟨m|V|n⟩|²/(Eₙ-Eₘ)"],
  ex_tr=["Zeeman etkisi: manyetik alan V̂ = -μ̂·B bozulmasi getirir. Birinci "
         "mertebe duzeltme ΔE = m_l·μ_B·B verir; yani her l duzeyi 2l+1 "
         "alt duzeye yarilir. Gozlenen spektrum cizgilerinin yarilmasi "
         "budur ve yildizlarin manyetik alanini bu yarilmadan olceriz."],
  ex_en=["Zeeman: first-order shift m_l·mu_B·B splits each level into 2l+1, "
         "which is how stellar magnetic fields are measured."],
  kw="perturbasyon|perturbasyon kurami|yaklasik cozum kuantum|"
     "zeeman|stark etkisi|birinci mertebe duzeltme|perturbation theory",
  related="kuantum_formalizm|zeeman"),

T("bant_kurami", "Bant Kuramı ve Bloch Teoremi", "Band Theory", """
Bir metalin neden iletken, elmasin neden yalitkan oldugunu aciklayan kuram.

**Bloch teoremi:** Periyodik bir potansiyelde (kristal orgu) elektronun
dalga fonksiyonu
    ψ_k(r) = e^(ik·r)·u_k(r),    u_k orgu periyoduyla periyodik
bicimindedir. Yani elektron kristalde SERBEST bir dalga gibi ilerler;
orgu yalnizca genligi module eder. Ideal bir kristalde elektron
sacilmadan gider — direncin kaynagi orgu KUSURLARI ve titresimlerdir.

**Bant olusumu:** Tek atomda kesikli duzeyler vardir. N atom bir araya
gelince her duzey N alt duzeye yarilir; N ~ 10²³ oldugundan bunlar
pratikte SUREKLI bir bant olusturur. Bantlar arasinda elektronun
bulunamayacagi YASAK ARALIKLAR (band gap) kalir.

**Siniflandirma:**
- **Iletken:** en ust dolu bant kismen dolu — elektronlar kolayca ust
  duzeylere gecebilir.
- **Yalitkan:** valans bandi tam dolu, yasak aralik buyuk (elmas: 5,5 eV).
- **Yariiletken:** yasak aralik kucuk (silisyum: 1,1 eV). Oda
  sicakliginda birkac elektron termal olarak gecebilir; sicaklik artinca
  iletkenlik ARTAR — metalin tersi.

**Katkilama (doping):** Silisyuma fosfor (5 degerli) katilirsa fazladan
elektron gelir (n tipi); bor (3 degerli) katilirsa delik olusur (p tipi).
p-n eklemi diyotun, iki eklem transistorun temelidir. Butun modern
elektronik bu kuram uzerine kuruludur.
""", """
Bloch's theorem: in a periodic potential the wavefunction is a plane wave
times a lattice-periodic function, so a perfect crystal offers no
resistance. Atomic levels broaden into bands separated by gaps; a partly
filled band gives a metal, a large gap an insulator, a small gap a
semiconductor. Doping creates n- and p-type material, hence diodes and
transistors.
""",
  eqs=["ψ_k(r) = e^(ik·r)·u_k(r)", "E_g(Si) ≈ 1,1 eV",
       "n ∝ exp(-E_g/2kT)"],
  ex_tr=["Silisyumda yasak aralik 1,1 eV. Oda sicakliginda kT ≈ 0,026 eV, "
         "yani exp(-1,1/0,052) ≈ 10⁻⁹ — cok kucuk ama sifir degil. Bu "
         "yuzden saf silisyum zayif iletir; katkilama bu sayiyi milyonlarca "
         "kat artirir."],
  ex_en=["In silicon E_g = 1.1 eV while kT = 0.026 eV, giving a tiny but "
         "non-zero carrier density; doping raises it by orders of magnitude."],
  kw="bant kurami|bloch teoremi|yasak aralik|band gap|valans bandi|"
     "iletim bandi|katkilama|doping|yariiletken kurami|p-n eklemi",
  related="yariiletken|katihal"),

T("standart_model", "Standart Model", "The Standard Model", """
Bilinen tum temel parcaciklari ve dort kuvvetten ucunu tek cercevede
anlatan kuram. Kutle cekimi DISINDA kalan her seyi kapsar.

**Madde parcaciklari (fermiyonlar, spin ½):** Uc aile halinde
- **Kuarklar:** yukari/asagi, tilsim/garip, ust/alt. Renk yuku tasirlar,
  guclu etkilesime katilirlar. Serbest halde bulunamazlar (hapsolma).
- **Leptonlar:** elektron, muon, tau ve karsilik gelen notrinolar.
  Renk yuku yoktur.

**Kuvvet tasiyicilar (bozonlar, spin 1):**
| Etkilesim | Tasiyici | Menzil |
|---|---|---|
| Elektromanyetik | foton (kutlesiz) | sonsuz |
| Zayif | W⁺, W⁻, Z⁰ (agir) | ~10⁻¹⁸ m |
| Guclu | 8 gluon | ~10⁻¹⁵ m |

**Higgs bozonu (spin 0):** Kutle mekanizmasi. W ve Z'nin agir, fotonun
kutlesiz olmasinin sebebi.

**Simetri yapisi:** SU(3) × SU(2) × U(1). Bu uc ayar simetrisi sirasiyla
guclu, zayif ve elektromanyetik etkilesimleri uretir.

**Basarilari:** Elektronun manyetik momenti 12 haneye kadar dogrudur — bu,
bilimin en hassas dogrulanmis ongorusudur. W, Z ve Higgs once kuramda
ongorulup sonra bulundu.

**Eksikleri (bilerek soyluyoruz):** Kutle cekimini icermez. Karanlik madde
ve karanlik enerjiyi aciklamaz. Notrinolarin kutlesini dogal bicimde
vermez. Madde-antimadde asimetrisini aciklamaya yetmez. Yani Standart
Model dogru ama TAM DEGILDIR.
""", """
The Standard Model covers three of the four forces with SU(3)xSU(2)xU(1)
symmetry: quarks and leptons in three generations, photon, W/Z and gluons
as carriers, plus the Higgs. Its prediction for the electron magnetic
moment is verified to twelve digits. It omits gravity, dark matter, dark
energy and neutrino masses.
""",
  eqs=["SU(3)×SU(2)×U(1)", "m_W ≈ 80,4 GeV", "m_Z ≈ 91,2 GeV",
       "m_H ≈ 125 GeV"],
  ex_tr=["Zayif etkilesimin menzili neden bu kadar kisa? Menzil, tasiyicinin "
         "kutlesiyle ters orantilidir: R ≈ ħ/(mc). W bozonu icin "
         "m = 80,4 GeV/c² koyunca R ≈ 2,5×10⁻¹⁸ m cikar — cekirdek "
         "capinin binde biri. Foton kutlesiz oldugu icin elektromanyetik "
         "etkilesimin menzili sonsuzdur."],
  ex_en=["Range R ~ hbar/(mc): for the 80.4 GeV W boson this gives 2.5e-18 m, "
         "while the massless photon gives infinite range."],
  kw="standart model|temel parcaciklar|kuark|lepton|gluon|w bozonu|"
     "z bozonu|parcacik fizigi|elektrozayif|guclu etkilesim",
  related="alan_kurami|higgs_kesfi|simetri"),

T("matematiksel_yontemler", "Fiziğin Matematiksel Yöntemleri",
  "Mathematical Methods of Physics", """
Fizikte tekrar tekrar karsiniza cikan matematik araclari ve HANGI FIZIK
SORUSUNU cozdukleri.

**Vektor analizi:** Gradyan (∇f) bir skalerin en hizli artis yonu —
potansiyelden kuvvet buradan cikar (F = -∇V). Diverjans (∇·F) kaynak
yogunlugu — Gauss yasasi budur. Rotasyonel (∇×F) donme egilimi — Faraday
ve Ampere yasalari budur.

**Fourier analizi:** Her periyodik sinyal sinuslerin toplamidir. Fizikteki
karsiligi: bir dalga paketini duzlem dalgalara ayirmak, kristalde ters
orgu, kuantum mekaniginde konum ve momentum gosterimleri arasindaki
gecis. Belirsizlik ilkesi, aslinda Fourier donusumunun bir ozelligidir:
zamanda dar olan sinyal frekansta genistir.

**Diferansiyel denklemler:** Fizigin dili. Ikinci mertebe lineer
denklemler (harmonik salinici, dalga denklemi, Schrödinger) en sik
gorulenlerdir. Ozel fonksiyonlar (Legendre, Bessel, Hermite) bunlarin
kuresel/silindirik/harmonik geometrideki cozumleridir.

**Karmasik sayilar:** Salinim ve dalga hesaplarini basitlestirir
(e^(iωt) gosterimi). Kuantum mekaniginde ise vazgecilmezdir: dalga
fonksiyonu doğası geregi karmasiktir.

**Tensorler:** Koordinat seciminden BAGIMSIZ fiziksel iliskiler yazmak
icin. Gerilme tensoru, atalet tensoru, elektromanyetik alan tensoru ve
genel gorelilikte metrik tensor.

**Boyut analizi:** En ucuz ve en guclu denetim. Bir denklemin iki tarafi
ayni boyutta degilse denklem yanlistir — hesaplamaya bile gerek yok.
Ayrica boyut analizi cogu zaman cevabin BICIMINI verir: sarkacin periyodu
yalnizca L ve g'den kurulabiliyorsa T ∝ √(L/g) olmak zorundadir.
""", """
The recurring mathematical tools and the physics they solve: vector
calculus (gradient/divergence/curl behind force, Gauss and Faraday),
Fourier analysis (wave packets, reciprocal space, and the uncertainty
principle as a Fourier property), differential equations and special
functions, complex numbers, tensors for coordinate-free relations, and
dimensional analysis, which often fixes the form of the answer.
""",
  eqs=["F = -∇V", "∇·E = ρ/ε₀", "∇×E = -∂B/∂t", "T ∝ √(L/g)"],
  ex_tr=["Boyut analiziyle sarkac periyodu: T yalnizca uzunluk L [m], "
         "yercekimi g [m/s²] ve kutle m [kg] ile kurulabilir. Zaman "
         "boyutu elde etmek icin kutle giremez (icinde kg yok), geriye "
         "√(L/g) kalir — birimi √(m / (m/s²)) = s. Sonuc: T = C·√(L/g). "
         "Sabit C = 2π'yi boyut analizi vermez, ama BICIMI tek hamlede "
         "verdi."],
  ex_en=["Dimensional analysis fixes the pendulum period as T = C sqrt(L/g); "
         "mass cannot enter, and only the constant is left undetermined."],
  kw="matematiksel yontemler|vektor analizi|gradyan|diverjans|rotasyonel|"
     "fourier analizi|ozel fonksiyonlar|tensor|boyut analizi|"
     "mathematical methods",
  related="maxwell|kuantum_formalizm"),

T("olcum_belirsizlik", "Ölçüm, Hata ve Belirsizlik",
  "Measurement, Error and Uncertainty", """
Deneysel fizigin omurgasi: bir sayi, belirsizligi verilmeden anlamsizdir.

**Iki hata turu:**
- **Rastgele hata:** Tekrarlarda saga sola sacilma. Olcum sayisini
  artirmak azaltir: ortalamanin standart hatasi σ/√N ile duser.
- **Sistematik hata:** Her olcumu ayni yone kaydirir (bozuk cetvel,
  kalibrasyonsuz alet). Tekrar etmek FAYDA ETMEZ; ancak yontem
  degistirerek ya da kalibrasyonla giderilir.

**Hata yayilimi:** Bagimsiz buyukluklerden hesaplanan bir sonucun
belirsizligi:
    f = f(x,y) icin   σ_f² = (∂f/∂x)²σ_x² + (∂f/∂y)²σ_y²
Carpim ve bolumde GORELI hatalar karelerinin toplami olarak birlesir:
    f = x·y → (σ_f/f)² = (σ_x/x)² + (σ_y/y)²

**Anlamli rakam:** Sonuc, en kaba olcumun duyarliligini asamaz.
Belirsizlik bir anlamli rakama yuvarlanir, sonuc da o basamaga gore
yazilir: 9,81 ± 0,03 m/s² dogru, 9,8134 ± 0,0312 yanlistir.

**Anlamlilik:** Fizikte bir sonucun "kesif" sayilmasi icin genellikle 5σ
aranir (rastlanti olasiligi ~1/3.500.000). 3σ yalnizca "kanit"tir. Bu
esik, cok sayida analiz yapildiginda yanlis pozitif cikma olasiligina
karsi konulmustur.
""", """
A number without an uncertainty is meaningless. Random errors shrink as
sigma/sqrt(N); systematic errors do not shrink with repetition. Errors
propagate in quadrature, and relative errors add in quadrature for
products. Physics calls 5 sigma a discovery and 3 sigma only evidence.
""",
  eqs=["σ_ort = σ/√N", "σ_f² = Σ (∂f/∂xᵢ)²σᵢ²",
       "(σ_f/f)² = (σ_x/x)² + (σ_y/y)²"],
  ex_tr=["Bir dikdortgenin kenarlari a = 10,0 ± 0,1 cm ve b = 5,0 ± 0,1 cm. "
         "Alan A = 50,0 cm². Goreli hatalar: 0,01 ve 0,02. Karelerinin "
         "toplaminin karekoku 0,0224, yani σ_A = 50,0 × 0,0224 ≈ 1,1 cm². "
         "Sonuc: A = 50 ± 1 cm². Dikkat: kucuk kenardaki hata baskin."],
  ex_en=["For a = 10.0±0.1 and b = 5.0±0.1 cm the area is 50 ± 1 cm²; the "
         "shorter side dominates the relative error."],
  kw="olcum belirsizligi|hata analizi|hata yayilimi|standart sapma|"
     "anlamli rakam|sistematik hata|rastgele hata|5 sigma|error propagation",
  related="matematiksel_yontemler"),
]
