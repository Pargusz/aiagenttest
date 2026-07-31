# -*- coding: utf-8 -*-
"""Lisans mufredatinin 3. ve 4. sinif cekirdegi.

Olculdu: dort yillik mufredat 125 baslikla tarandiginda ilk iki yil
dogrulanmis cekirdekten cevaplaniyordu, ama ust sinif dersleri ya
makale kirintilariyla ya da YANLIS konuyla cevaplaniyordu:

    "sacilma born yaklasimi"  -> "Gokyuzu Neden Mavi"
    "kanonik donusumler"      -> "Istatistiksel Topluluklar"
    "dalga kilavuzu"          -> "Dalga Hareketi ve Ses"

Yanlis konu, bosluktan daha kotudur: ogrenci emin bir cevap goruyor.
Bu dosya o bosluklari kapatir. Her konu ayni yapida: tanim, neden
boyle, bagintilar ve SAYISAL bir ornek.
"""
from .knowledge import T

MUFREDAT_KONULARI = [

# ── Kuantum mekanigi (3. sinif) ─────────────────────────────────────────
T("ozdes_parcaciklar", "Özdeş Parçacıklar ve İstatistik",
  "Identical Particles and Statistics", """
Klasik fizikte iki topu boyayip ayirt edebilirsiniz. Kuantum mekaniginde
iki elektron ILKESEL olarak ayirt edilemez — ve bu, evrenin yapisini
belirler.

**Simetrizasyon postulati:** Iki ozdes parcacigin yerleri degistirilince
dalga fonksiyonu ya AYNI kalir ya da ISARET degistirir:
    ψ(1,2) = ± ψ(2,1)
- **Bozonlar** (+): tam sayi spin (foton, fonon, He-4). Ayni durumda
  istedigi kadar bulunabilir → Bose-Einstein yogusmasi, lazer.
- **Fermiyonlar** (−): yari tam sayi spin (elektron, proton, notron).

**Pauli dislama ilkesi bir POSTULAT DEGILDIR:** Antisimetriklikten CIKAR.
Iki fermiyon ayni durumda olsaydi ψ(1,2) = -ψ(1,2) = 0 olurdu; yani boyle
bir durum yoktur. Periyodik tablonun, katilarin sertliginin ve beyaz
cucelerin ayakta durmasinin sebebi budur.

**Slater determinanti:** N fermiyonlu antisimetrik dalga fonksiyonu bir
determinant olarak yazilir; iki satir ayni olursa determinant sifirdir —
Pauli ilkesinin matematiksel ifadesi.

**Degis-tokus etkilesimi:** Simetri, gercek bir kuvvet olmadan enerji
farki yaratir. Ferromanyetizma bu "degis-tokus" enerjisinden dogar;
ortada manyetik dipol etkilesimi yoktur, sadece istatistik vardir.
""", """
Identical quantum particles are fundamentally indistinguishable, so the
wavefunction is either symmetric (bosons) or antisymmetric (fermions)
under exchange. Pauli exclusion is not a separate postulate: it follows
from antisymmetry. Exchange symmetry alone produces energy differences,
which is the origin of ferromagnetism.
""",
  eqs=["ψ(1,2) = ±ψ(2,1)", "ψ_A = (1/√2)[ψ_a(1)ψ_b(2) − ψ_a(2)ψ_b(1)]",
       "Slater determinantı"],
  ex_tr=["Iki elektron ayni uzaysal durumda olsun. Antisimetrik toplam "
         "dalga fonksiyonu icin spin kismi SINGLET olmak zorundadir "
         "(↑↓−↓↑)/√2. Helyum atominin temel durumu tam da budur: 1s² "
         "dizilimi ancak zit spinlerle mumkundur. Uyarilmis helyumda ise "
         "triplet durum daha DUSUK enerjilidir (ortohelyum), cunku "
         "antisimetrik uzaysal kisim elektronlari birbirinden uzak tutar "
         "ve Coulomb itmesi azalir."],
  ex_en=["Two electrons in the same spatial state must form a spin "
         "singlet — this is why helium's ground state is 1s2, and why "
         "orthohelium lies lower than parahelium when excited."],
  kw="ozdes parcaciklar|ayirt edilemezlik|simetrizasyon|bozon fermiyon|"
     "pauli dislama|slater determinanti|degis tokus etkilesimi|"
     "identical particles|exchange interaction",
  related="kuantum_formalizm|istatistik_topluluk"),

T("sacilma_kurami", "Saçılma Kuramı ve Born Yaklaşımı",
  "Scattering Theory and the Born Approximation", """
Parcacik fiziginin ve katihal deneylerinin tamami SACILMADIR: bir demeti
hedefe carptirip cikan dagilima bakariz. Kuram bu dagilimi potansiyele
baglar.

**Tesir kesiti:** Etkilesme olasiliginin ALAN cinsinden olcusudur.
Diferansiyel tesir kesiti dσ/dΩ, birim kati acida sacilan parcacik
sayisidir. Birimi barn'dir (1 barn = 10⁻²⁸ m²) — bir cekirdegin kesit
alani mertebesinde.

**Sacilma genligi:** Uzakta dalga fonksiyonu
    ψ ≈ e^(ikz) + f(θ)·e^(ikr)/r
bicimini alir. Olculebilir buyukluk dσ/dΩ = |f(θ)|².

**Born yaklasimi:** Potansiyel ZAYIFSA (gelen dalga fazla bozulmuyorsa)
sacilma genligi potansiyelin FOURIER DONUSUMUDUR:
    f(θ) = −(m/2πħ²) ∫ V(r) e^(i q·r) d³r,   q = k_son − k_ilk
Bu, saçılma deneyinin neden yapinin "fotografini" verdiginin cevabidir:
olculen dagilim, potansiyelin Fourier uzayindaki halidir. X isini
kirinimi, elektron mikroskobu ve derin esnek olmayan sacilma ayni
ilkeyle calisir.

**Kismi dalga acilimi:** Dusuk enerjide daha kullanislidir; dalga acisal
momentum bilesenlerine ayrilir ve her biri bir FAZ KAYMASI δ_l kazanir.
    σ = (4π/k²) Σ (2l+1) sin²δ_l
""", """
Scattering links the measured angular distribution to the potential. The
differential cross section is |f(θ)|². In the Born approximation the
scattering amplitude is the Fourier transform of the potential, which is
why diffraction experiments image structure. At low energy the partial
wave expansion with phase shifts is more useful.
""",
  eqs=["dσ/dΩ = |f(θ)|²", "f(θ) = −(m/2πħ²)∫V(r)e^(iq·r)d³r",
       "σ = (4π/k²)Σ(2l+1)sin²δ_l", "1 barn = 10⁻²⁸ m²"],
  ex_tr=["Yukawa potansiyeli V = V₀e^(−μr)/r icin Born yaklasimi "
         "f(q) = −2mV₀/(ħ²(q²+μ²)) verir. μ → 0 limitinde bu Coulomb "
         "potansiyeline doner ve dσ/dΩ ∝ 1/sin⁴(θ/2) cikar — Rutherford "
         "sacilma formulunun ta kendisi. Kuantum kuram, klasik hesabin "
         "sonucunu aynen dogrular; bu bir tesaduf degil, Coulomb "
         "potansiyelinin ozel bir ozelligidir."],
  ex_en=["The Born approximation for a Yukawa potential reduces to the "
         "Rutherford cross section as the screening vanishes."],
  kw="sacilma kurami|born yaklasimi|tesir kesiti|diferansiyel tesir kesiti|"
     "sacilma genligi|kismi dalga|faz kaymasi|barn birimi|"
     "scattering theory|born approximation|cross section",
  related="rutherford_sacilma|kuantum_formalizm"),

# ── Analitik mekanik (2-3. sinif) ───────────────────────────────────────
T("kanonik_donusum", "Kanonik Dönüşümler ve Poisson Parantezleri",
  "Canonical Transformations and Poisson Brackets", """
Hamilton formalizminin gucu, KOORDINAT SECME OZGURLUGUNDEDIR. Problemi
kolaylastiran yeni degiskenlere gecebiliriz — yeter ki hareket
denklemlerinin bicimi korunsun.

**Kanonik donusum:** (q,p) → (Q,P) donusumu, Hamilton denklemlerinin
bicimini koruyorsa kanoniktir. Uretici fonksiyon F ile kurulur; ornegin
F₂(q,P) icin p = ∂F₂/∂q, Q = ∂F₂/∂P.

**Poisson parantezi:**
    {A,B} = Σ (∂A/∂q ∂B/∂p − ∂A/∂p ∂B/∂q)
Herhangi bir buyuklugun zamanla degisimi
    dA/dt = {A,H} + ∂A/∂t
Yani {A,H} = 0 ise A KORUNUR. Noether teoreminin Hamilton dilindeki
karsiligi budur.

**Temel parantezler:** {q_i, p_j} = δ_ij, {q_i,q_j} = {p_i,p_j} = 0.
Bir donusumun kanonik olup olmadigi bu parantezlerin korunmasiyla
sinanir.

**Kuantum mekanigine kopru:** Dirac'in gozlemi sudur —
    {A,B}  →  (1/iħ)[Â,B̂]
Poisson parantezi komutatore gider. {q,p} = 1 bagintisi [x̂,p̂] = iħ
olur. Klasik mekanik ile kuantum mekanigi arasindaki en dogrudan
yapisal bag budur.

**Hamilton-Jacobi:** Uygun bir kanonik donusumle yeni Hamiltoniyeni
SIFIR yapabilirsek tum yeni degiskenler sabit olur; problem tamamen
cozulmus demektir. Dalga mekanigi bu denklemin kisa dalga boyu
limitinden dogmustur.
""", """
Canonical transformations preserve the form of Hamilton's equations.
Poisson brackets give dA/dt = {A,H}, so a vanishing bracket with H means
conservation. Dirac's correspondence {A,B} -> [A,B]/i(hbar) is the most
direct structural bridge from classical to quantum mechanics.
""",
  eqs=["{A,B} = Σ(∂A/∂q·∂B/∂p − ∂A/∂p·∂B/∂q)", "dA/dt = {A,H} + ∂A/∂t",
       "{q_i,p_j} = δ_ij", "{A,B} → [Â,B̂]/(iħ)"],
  ex_tr=["Harmonik osilator: H = p²/2m + ½mω²q². Acisal degiskenlere "
         "gecen kanonik donusum (eylem-aci degiskenleri) H = ωJ verir; "
         "burada J eylem degiskenidir ve SABITTIR. Hareket denklemi "
         "dθ/dt = ∂H/∂J = ω olur, yani θ = ωt + θ₀. Problem tek satirda "
         "cozulur. Bohr-Sommerfeld kuantumlamasi da tam olarak bu J'yi "
         "ħ'nin katlarina esitler."],
  ex_en=["Action-angle variables turn the oscillator Hamiltonian into "
         "H = ωJ, solving the motion in one line; Bohr-Sommerfeld "
         "quantisation then sets J to multiples of hbar."],
  kw="kanonik donusum|poisson parantezi|uretici fonksiyon|"
     "hamilton jacobi|eylem aci degiskenleri|canonical transformation|"
     "poisson bracket",
  related="hamilton|lagrange|kuantum_formalizm"),

# ── Elektromanyetik teori (3. sinif) ────────────────────────────────────
T("multipol", "Multipol Açılımı", "Multipole Expansion", """
Uzaktaki bir yuk dagiliminin potansiyelini tam hesaplamak zordur; ama
UZAKTAN bakinca ayrinti onemini yitirir. Multipol acilimi bunu duzenli
bir siraya sokar.

**Acilim:**
    V(r) = (1/4πε₀)[ Q/r + p·r̂/r² + (kuadrupol)/r³ + … ]
- **Monopol** Q = Σq: net yuk. Sifir degilse uzakta yalnizca bu gorulur.
- **Dipol** p = Σqr: net yuk sifirsa baskin terimdir. Su molekulunun
  dipol momenti bu yuzden onemlidir.
- **Kuadrupol:** ikisi de sifirsa devreye girer; cekirdek sekli
  (kuresel mi, elipsoit mi) kuadrupol momentinden anlasilir.

**Neden ise yarar:** Her terim mesafeyle daha hizli soner. Bir metre
uzaktaki molekulun ayrintisini bilmenize gerek yok — dipolu yeter. Bu,
fizikte "olcege gore basitlestirme"nin en temiz orneklerinden biridir.

**Legendre polinomlari ile:** Acilim aslinda 1/|r−r'| ifadesinin
Legendre polinomlarina acilmasidir:
    1/|r−r'| = Σ (r'^l / r^(l+1)) P_l(cosθ)
Bu yuzden kuresel simetrili problemlerde Legendre polinomlari her yerde
karsimiza cikar.

**Isima:** Zamanla degisen multipoller isima yayar. Dipol isimasi
en baskin kanaldir; kuadrupol isimasi cok daha zayiftir. Kutle
cekiminde dipol isimasi momentum korunumu yuzunden YASAKTIR — bu
yuzden kutle cekim dalgalari kuadrupol isimasidir ve bu kadar zayiftir.
""", """
Far from a charge distribution the potential organises into monopole,
dipole and quadrupole terms, each falling off faster. The expansion is
the Legendre expansion of 1/|r-r'|. Because gravitational dipole
radiation is forbidden by momentum conservation, gravitational waves are
quadrupole radiation — hence extremely weak.
""",
  eqs=["V = (1/4πε₀)[Q/r + p·r̂/r² + …]", "p = Σqᵢrᵢ",
       "1/|r−r'| = Σ(r'^l/r^(l+1))P_l(cosθ)"],
  ex_tr=["Su molekulunun dipol momenti p = 6,2×10⁻³⁰ C·m. 1 nm uzakta "
         "dipol potansiyeli V = p/(4πε₀r²) = "
         "(6,2×10⁻³⁰)/(1,11×10⁻¹⁰ × 10⁻¹⁸) ≈ 0,056 V. Aynı uzaklıkta tek "
         "bir elektronun potansiyeli 1,44 V'tur — yani net yuklu bir "
         "iyon, notr bir dipolden yaklasik 25 kat guclu etkir. "
         "Cozeltilerdeki iyon-dipol ve dipol-dipol etkilesim "
         "hiyerarsisi buradan gelir."],
  ex_en=["A water dipole gives ~0.056 V at 1 nm while a single electron "
         "gives 1.44 V — the origin of the ion-dipole hierarchy."],
  kw="multipol acilimi|dipol moment|kuadrupol moment|monopol|"
     "multipole expansion|dipole moment|quadrupole",
  related="elektrik_potansiyeli|maxwell"),

T("dalga_kilavuzu", "Dalga Kılavuzu ve İletim Hatları",
  "Waveguides and Transmission Lines", """
Bos uzayda elektromanyetik dalga her yone yayilir. Metal bir borunun
icine hapsedilirse KILAVUZLANIR — ama sinir kosullari ona sert bir
kural dayatir.

**Sinir kosulu:** Iletken yuzeyde elektrik alanin teget bileseni sifir
olmalidir. Bu, bir kutuda duran dalga kosuluyla ayni matematiktir ve
kilavuzun icinde yalnizca belirli MOD'larin var olabilecegi anlamina
gelir.

**Kesim frekansi:** Her modun bir alt siniri vardir; dikdortgen
kilavuzda
    f_c = (c/2)·√((m/a)² + (n/b)²)
Bundan dusuk frekansta dalga yayilmaz, ustel olarak soner. Kilavuz bir
YUKSEK GECIREN suzgectir. Mikrodalga firininin kapisindaki delikli
metal izgara da bu ilkeyle calisir: 2,45 GHz mikrodalga deliklerden
gecemez ama gorunur isik (cok daha yuksek frekans) gecer — icerisini
gorursunuz, mikrodalga disari cikmaz.

**Faz ve grup hizi:** Kilavuzda faz hizi ISIK HIZINDAN BUYUKTUR
(v_p = c/√(1−(f_c/f)²)), grup hizi ise kucuktur ve v_p·v_g = c²
bagintisi gecerlidir. Gorelilik ihlal edilmez: bilgi grup hiziyla gider.

**TE, TM, TEM:** Ici bos tek iletkenli kilavuzda TEM modu YOKTUR; iki
iletkenli hatlarda (koaksiyel kablo) vardir ve kesim frekansi yoktur —
bu yuzden koaksiyel kablo DC'den itibaren calisir.
""", """
A conducting guide imposes boundary conditions that allow only discrete
modes, each with a cutoff frequency: the guide is a high-pass filter. A
microwave oven's door mesh works this way. Phase velocity exceeds c while
group velocity stays below it, with v_p·v_g = c^2. Hollow single-conductor
guides have no TEM mode; coaxial lines do, so they work down to DC.
""",
  eqs=["f_c = (c/2)√((m/a)² + (n/b)²)", "v_p = c/√(1−(f_c/f)²)",
       "v_p·v_g = c²"],
  ex_tr=["WR-90 standart kilavuzu: a = 22,86 mm, b = 10,16 mm. Temel mod "
         "TE₁₀ icin f_c = c/(2a) = (3×10⁸)/(2×0,02286) = 6,56 GHz. "
         "Bu kilavuz X bandinda (8-12 GHz) kullanilir; 6,56 GHz altinda "
         "hicbir sey gecmez. Mikrodalga firin izgarasindaki ~2 mm delikler "
         "icin kesim ~75 GHz olur, yani 2,45 GHz kesinlikle gecemez."],
  ex_en=["WR-90 has a TE10 cutoff at 6.56 GHz; the ~2 mm holes in an oven "
         "door cut off near 75 GHz, far above the 2.45 GHz microwaves."],
  kw="dalga kilavuzu|kesim frekansi|te modu|tm modu|tem modu|"
     "koaksiyel kablo|iletim hatti|mikrodalga firin neden|waveguide|"
     "cutoff frequency|transmission line",
  related="elektromanyetik_dalga|maxwell"),

# ── Matematiksel fizik ──────────────────────────────────────────────────
T("vektor_analizi", "Vektör Analizi: Diverjans ve Stokes Teoremleri",
  "Vector Calculus: Divergence and Stokes Theorems", """
Maxwell denklemlerinin integral ve diferansiyel bicimleri arasindaki
kopru bu iki teoremdir. Fizikte "yerel yasa" ile "global yasa"yi
birbirine cevirirler.

**Diverjans (Gauss) teoremi:**
    ∮_S F·dA = ∫_V (∇·F) dV
Kapali bir yuzeyden cikan net akis, icerideki kaynaklarin toplamidir.
∇·E = ρ/ε₀ (diferansiyel Gauss yasasi) ile ∮E·dA = Q/ε₀ (integral
bicim) tam olarak bu teoremle esdegerdir.

**Stokes teoremi:**
    ∮_C F·dl = ∫_S (∇×F)·dA
Kapali bir egri boyunca dolanim, icerideki girdapliligin toplamidir.
Faraday yasasinin iki bicimi buradan birbirine gecer.

**Fiziksel okuma:**
- ∇·F : o noktada KAYNAK var mi? (yuk, kutle, akiskan cikisi)
- ∇×F : o noktada DONME var mi? (girdap, indukleme)
- ∇×(∇f) = 0 : gradyanin rotasyoneli sifir → korunumlu kuvvet
  potansiyelden turetilir.
- ∇·(∇×F) = 0 : rotasyonelin diverjansi sifir → manyetik tek kutup yok
  (∇·B = 0 bu yuzden dogaldir).

**Sureklilik denklemi:** ∂ρ/∂t + ∇·J = 0. Yuk korunumunun yerel
ifadesidir; Maxwell'in yer degistirme akimini eklemesi tam da bu
denklemi saglamak icindi.
""", """
The divergence and Stokes theorems convert between local and global
statements, which is exactly the relation between the differential and
integral forms of Maxwell's equations. Two identities matter physically:
curl of a gradient vanishes (conservative forces have potentials) and
divergence of a curl vanishes (no magnetic monopoles).
""",
  eqs=["∮F·dA = ∫(∇·F)dV", "∮F·dl = ∫(∇×F)·dA", "∇×(∇f) = 0",
       "∇·(∇×F) = 0", "∂ρ/∂t + ∇·J = 0"],
  ex_tr=["Nokta yuk icin E = kq r̂/r². Yaricapi R olan kure uzerinden "
         "akis: ∮E·dA = (kq/R²)(4πR²) = 4πkq = q/ε₀. Yaricap "
         "SADELESTI — akis kurenin buyuklugunden bagimsizdir. Diverjans "
         "teoremi bunun sebebini soyler: akis yalnizca ICERIDEKI yuke "
         "bagli, cunku yuk disinda ∇·E = 0'dir."],
  ex_en=["The flux of a point charge through any sphere is q/eps0 — the "
         "radius cancels, because the divergence vanishes away from the "
         "charge."],
  kw="vektor analizi|diverjans teoremi|gauss teoremi|stokes teoremi|"
     "rotasyonel|gradyan|sureklilik denklemi|nabla|"
     "divergence theorem|stokes theorem|curl|gradient",
  related="maxwell|gauss_yasasi"),

T("ozel_fonksiyonlar", "Özel Fonksiyonlar: Legendre, Bessel, Hermite",
  "Special Functions: Legendre, Bessel, Hermite", """
Bu fonksiyonlar keyfi degildir: her biri belirli bir SIMETRIDEKI
Laplace/Schrodinger denkleminin cozumudur. Hangi geometride
calisiyorsaniz o fonksiyon karsiniza cikar.

| Geometri | Denklem | Cozum |
|---|---|---|
| Kuresel | açısal kısım | Legendre P_l, kuresel harmonikler Y_lm |
| Silindirik | radyal kısım | Bessel J_n, Y_n |
| Harmonik tuzak | ½mω²x² | Hermite H_n |

**Legendre:** (1−x²)y″ − 2xy′ + l(l+1)y = 0. Kuresel harmonikler
Y_lm(θ,φ) hidrojen atominin acisal kismidir; l acisal momentum kuantum
sayisidir. Multipol acilimindaki P_l(cosθ) ile ayni fonksiyonlardir.

**Bessel:** Silindirik simetride cikar: davul zarinin titresim modlari,
optik fiberdeki alan dagilimi, dairesel dalga kilavuzu. Kokleri
DUZENSIZDIR — bu yuzden davulun ust ton frekanslari telin aksine tam
kat degildir ve davul "notasiz" duyulur.

**Hermite:** Kuantum harmonik osilatorun cozumu ψ_n ∝ H_n(ξ)e^(−ξ²/2).
n. seviyenin n tane dugumu vardir.

**Ortak nokta — Sturm-Liouville:** Ucu de ayni tipte bir ozdeger
problemidir. Bu yuzden hepsi ORTOGONALDIR ve keyfi bir fonksiyon
onlara acilabilir. Fourier serisinin genellemesi budur; fizikte
"tabana ayirma" hep bu yapiya dayanir.
""", """
These functions are not arbitrary: each solves Laplace or Schrodinger in
a particular symmetry — Legendre and spherical harmonics in spherical
geometry, Bessel in cylindrical, Hermite in a harmonic trap. All are
Sturm-Liouville eigenfunctions, hence orthogonal and complete, which is
why any function can be expanded in them.
""",
  eqs=["(1−x²)P_l″ − 2xP_l′ + l(l+1)P_l = 0",
       "x²J″ + xJ′ + (x²−n²)J = 0",
       "H_n″ − 2xH_n′ + 2nH_n = 0",
       "ψ_n ∝ H_n(ξ)·e^(−ξ²/2)"],
  ex_tr=["Dairesel bir davul zarinin temel modu J₀'in ilk kokunden "
         "gelir: x₀₁ = 2,405. Frekans f = (x₀₁/2πR)√(T/σ). Ikinci "
         "kok 5,520 oldugundan ikinci mod temel frekansin 5,520/2,405 = "
         "2,295 katidir — tam sayi DEGIL. Telde ise oranlar 2, 3, 4 "
         "olur. Davulun belirli bir nota vermemesinin matematiksel "
         "sebebi tam olarak budur."],
  ex_en=["A drumhead's overtone ratio is 5.520/2.405 = 2.295, not an "
         "integer — which is why drums do not sound a definite pitch."],
  kw="ozel fonksiyonlar|legendre polinomlari|kuresel harmonikler|"
     "bessel fonksiyonlari|hermite polinomlari|sturm liouville|"
     "ortogonal fonksiyonlar|special functions|spherical harmonics",
  related="kuantum_formalizm|matematiksel_yontemler"),

T("green_fonksiyonu", "Green Fonksiyonları", "Green's Functions", """
Green fonksiyonu tek bir fikirdir: **noktasal bir kaynagin cevabini
bul, sonra topla.** Dogrusal bir sistemde bu her zaman calisir.

**Tanim:** L bir dogrusal diferansiyel operator olsun. Green fonksiyonu
    L G(r,r') = δ(r−r')
denklemini saglar. O zaman L ψ = f(r) denkleminin cozumu
    ψ(r) = ∫ G(r,r') f(r') d³r'
Yani genel cozum, kaynagin nokta-cevaplarla AGIRLIKLI toplamidir.
Fizikteki adi "superpozisyon ilkesi"dir.

**Elektrostatikte:** ∇²V = −ρ/ε₀ icin G = 1/(4π|r−r'|). Cozum
    V(r) = (1/4πε₀)∫ ρ(r')/|r−r'| d³r'
Bu, lise fiziginde ezberlenen integralin NEREDEN geldiginin cevabidir:
Coulomb potansiyeli, Laplace operatorunun Green fonksiyonudur.

**Sinir kosullari:** Iletken bir duzlem varsa G degisir; goruntu yukleri
yontemi aslinda o geometrinin Green fonksiyonunu bulmaktir.

**Zamana bagli problemlerde:** Dalga denkleminin Green fonksiyonu
GECIKMELI potansiyeli verir — etki, r/c kadar zaman sonra ulasir.
Nedensellik matematige boyle girer.

**Kuantumda:** Propagator ⟨x'|e^(−iHt/ħ)|x⟩ bir Green fonksiyonudur;
Feynman diyagramlarindaki her ic cizgi bir propagatordur.
""", """
A Green's function is the response to a point source: solve LG = delta,
then superpose. In electrostatics it is 1/(4 pi |r-r'|), which is where
the Coulomb integral comes from. For the wave equation it gives retarded
potentials, encoding causality; in quantum field theory it is the
propagator drawn as an internal line in Feynman diagrams.
""",
  eqs=["L·G(r,r') = δ(r−r')", "ψ(r) = ∫G(r,r')f(r')d³r'",
       "G_Laplace = 1/(4π|r−r'|)"],
  ex_tr=["Topraklanmis sonsuz iletken duzlemin ustunde d yuksekliginde q "
         "yuku. Green fonksiyonu goruntu yukuyle kurulur: G, gercek yuk "
         "ile −q goruntu yukunun toplamidir. Duzlem uzerinde potansiyel "
         "kendiliginden sifir cikar. Yuke etkiyen kuvvet "
         "F = −kq²/(2d)² = −kq²/4d² — yani goruntu yukune olan uzaklik "
         "2d'dir, d degil. Ogrencilerin en cok hata yaptigi yer burasidir."],
  ex_en=["For a charge above a grounded plane the image construction gives "
         "F = -kq^2/(2d)^2; the separation is 2d, not d."],
  kw="green fonksiyonu|green fonksiyonlari|nokta kaynak cevabi|"
     "propagator|gecikmeli potansiyel|goruntu yukleri|"
     "greens function|propagator|retarded potential",
  related="maxwell|kuantum_alan"),

T("tensor", "Tensörler ve İndis Gösterimi", "Tensors and Index Notation", """
Tensor, "koordinat degistirince BELIRLI bir kurala gore donusen"
nesnedir. Fizik yasalari tensor denklemleri olarak yazilirsa, her
koordinat sisteminde ayni bicimde gecerli olur — gorelilik ilkesinin
matematiksel karsiligi budur.

**Mertebe:** skaler (0), vektor (1), matris benzeri (2)... Ama her
matris tensor DEGILDIR; onemli olan donusum kuralidir.

**Einstein toplam kurali:** Tekrar eden indis uzerinden toplanir:
    a_i b_i ≡ Σ a_i b_i
Bu, sayfalarca yazimi tek satira indirir.

**Fizikteki tensorler:**
- **Eylemsizlik tensoru** I_ij: donme ekseni ile acisal momentumun neden
  AYNI YONDE olmadigini acikliyor (L = Iω bir matris carpimidir).
- **Gerilme tensoru** σ_ij: kati cisimde bir yuzeye etkiyen kuvvet,
  yuzeyin yonelimine baglidir.
- **Elektromanyetik alan tensoru** F^μν: E ve B ayri seyler degildir;
  tek bir tensorun bilesenleridir. Bir cercevede saf elektrik alan,
  digerinde manyetik alan gorunur.
- **Metrik tensor** g_μν: uzayzamanda uzunlugu tanimlar. Genel
  gorelilikte kutle cekimi budur.

**Ust ve alt indis:** Kovaryant/kontravaryant ayrimi metrikle
baglanir: A_μ = g_μν A^ν. Duz uzayda ve Kartezyen koordinatta bu ayrim
kaybolur; bu yuzden lisans mekanigi boyunca fark edilmez.
""", """
A tensor is defined by how it transforms under a change of coordinates,
which is what makes tensor equations valid in every frame. The inertia
tensor explains why angular momentum need not be parallel to the rotation
axis; the field tensor shows E and B are components of one object; the
metric defines lengths and, in general relativity, gravity itself.
""",
  eqs=["a_i b_i ≡ Σᵢ a_i b_i", "L_i = I_ij ω_j", "A_μ = g_μν A^ν",
       "F^μν = ∂^μA^ν − ∂^νA^μ"],
  ex_tr=["Bir tuglayi kosegen ekseni etrafinda dondurun. Eylemsizlik "
         "tensoru kosegen degilse L = Iω carpimi, ω ile AYNI YONDE "
         "olmayan bir L verir. Sonuc: L sabit kalmak icin eksene surekli "
         "tork uygulanmalidir — dengesiz bir arac tekerleginin titremesi "
         "tam olarak budur. Balans agirligi eklemek, eylemsizlik "
         "tensorunu kosegenlestirmektir."],
  ex_en=["If the inertia tensor is not diagonal, L is not parallel to "
         "omega and a torque is needed to keep the axis fixed — this is "
         "why car wheels need balancing."],
  kw="tensor nedir|indis gosterimi|einstein toplam kurali|"
     "eylemsizlik tensoru|metrik tensor|alan tensoru|kovaryant|"
     "tensor|index notation|inertia tensor|metric tensor",
  related="genel_gorelilik|kati_cisim"),
]

# ── Ikinci grup: istatistik fizik, nukleer, astrofizik, elektronik ─────────

MUFREDAT_KONULARI += [

T("faz_gecisi", "Faz Geçişleri ve Ising Modeli",
  "Phase Transitions and the Ising Model", """
Su 100 °C'de neden ANIDEN buhara doner? Sicakligi azicik degistirdiginizde
madde nicin butunuyle baska bir hale gecer? Faz gecisi kuraminin sordugu
soru budur.

**Duzen parametresi:** Gecisi tanimlayan buyukluk. Ferromiknatista
miknatislanma M, sivi-gazda yogunluk farki. Yuksek sicaklikta sifir,
kritik sicakligin altinda sifirdan farkli.

**Kendiliginden simetri kirilmasi:** Hamiltoniyen yukari-asagi simetrik
oldugu halde, T < T_c'de sistem BIR yonu secer. Yasa simetrik, cozum
degil. Ayni fikir parcacik fiziginde Higgs mekanizmasidir.

**Ising modeli:** En basit model — her komsu cifti icin enerji
    E = −J Σ s_i s_j,   s = ±1
1 boyutta faz gecisi YOKTUR (Ising, 1925). 2 boyutta vardir ve Onsager
1944'te TAM cozumu buldu — istatistik fizigin en unlu sonuclarindan.
Boyutun bu kadar belirleyici olmasi sasirticidir ve derstir: bir modelin
davranisi, denklemin bicimi kadar UZAYIN yapisina baglidir.

**Kritik ussler ve evrensellik:** T → T_c yakininda buyuklukler us
yasasiyla davranir: M ∼ (T_c−T)^β. Sasirtici olan sudur: tamamen farkli
sistemler (miknatis, sivi-gaz, alasim) AYNI ussleri verir. Mikroskobik
ayrintilar onemsizdir; yalnizca boyut ve simetri onemlidir. Buna
EVRENSELLIK denir ve renormalizasyon grubu bunu acikliyor.

**Birinci ve ikinci mertebe:** Birinci mertebede gizli isi vardir ve
duzen parametresi sicrar (buz-su). Ikinci mertebede sureklidir ama
turevi sicrar (Curie noktasi).
""", """
A phase transition is a qualitative change driven by a small parameter
change. The order parameter vanishes above T_c and is finite below, where
the system spontaneously breaks a symmetry the Hamiltonian still has. The
Ising model has no transition in 1D but does in 2D (Onsager, 1944).
Critical exponents are universal: only dimension and symmetry matter.
""",
  eqs=["E = −J Σ s_i s_j", "M ∼ (T_c − T)^β", "T_c(2B Ising) = 2J/(k·ln(1+√2))"],
  ex_tr=["Iki boyutlu kare orgu Ising modeli icin Onsager sonucu: "
         "kT_c/J = 2/ln(1+√2) = 2,269. Ortalama alan yaklasimi ise "
         "kT_c/J = 4 verir — %76 hatali. Sebep: ortalama alan, "
         "dalgalanmalari yok sayar; oysa kritik nokta CIVARINDA her "
         "olcekte dalgalanma vardir. Bu yuzden kritik olgular ayri bir "
         "kuram (renormalizasyon grubu) gerektirir."],
  ex_en=["Onsager gives kT_c/J = 2.269 in 2D while mean field predicts 4 — "
         "a 76% error, because mean field ignores the fluctuations that "
         "dominate near criticality."],
  kw="faz gecisi|faz gecisleri|ising modeli|kritik sicaklik|duzen parametresi|"
     "kendiliginden simetri kirilmasi|kritik us|evrensellik|curie noktasi|"
     "phase transition|ising model|critical exponent|universality",
  related="istatistik_topluluk|simetri"),

T("cekirdek_modelleri", "Çekirdek Modelleri ve Nükleer Tepkimeler",
  "Nuclear Models and Reactions", """
Cekirdek, guclu etkilesimle bagli bir cok-cisim sistemidir; tam cozumu
yoktur, bu yuzden birbirini tamamlayan MODELLER kullanilir.

**Sivi damla modeli:** Cekirdegi yuzey gerilimli bir damla gibi dusunur.
Weizsäcker formulu baglanma enerjisini verir: hacim, yuzey, Coulomb,
asimetri ve ciftlenme terimleri. Fisyonu ve baglanma enerjisi egrisinin
genel seklini iyi acikliyor.

**Kabuk modeli:** Nukleonlar, tipki atomdaki elektronlar gibi enerji
kabuklarina yerlesir. SIHIRLI SAYILAR — 2, 8, 20, 28, 50, 82, 126 —
dolu kabuklara karsilik gelir ve o cekirdekler alisilmadik derecede
kararlidir. Bu sayilar ancak SPIN-YORUNGE etkilesimi hesaba katilinca
cikar (Goeppert-Mayer ve Jensen, 1963 Nobel).

**Neden iki model birden?** Sivi damla toplu davranisi, kabuk modeli
tek parcacik davranisini acikliyor. Ikisi de dogrudur, farkli sorulara
cevap verirler — fizikte model kavraminin iyi bir dersidir.

**Baglanma enerjisi egrisi:** Nukleon basina baglanma enerjisi Fe-56
civarinda tepe yapar (~8,8 MeV). Bu yuzden hafif cekirdekler
BIRLESEREK (fuzyon), agir cekirdekler BOLUNEREK (fisyon) enerji verir.
Demirden sonra hicbiri enerji vermez — yildizlarin demir cekirdek
olusturunca cokmesinin sebebi budur.

**Tesir kesiti ve tepkimeler:** Nukleer tepkime hizi σ·Φ·N ile verilir.
Termal notronlarin U-235 fisyon tesir kesiti ~585 barn iken hizli
notronlarda ~1 barn'dir — reaktorlerde MODERATOR bu yuzden gerekir.
""", """
The liquid drop model explains collective behaviour and fission through
the Weizsacker formula; the shell model explains magic numbers (2, 8, 20,
28, 50, 82, 126), which only emerge once spin-orbit coupling is included.
Binding energy per nucleon peaks near Fe-56, so fusion releases energy
below it and fission above.
""",
  eqs=["B = a_V A − a_S A^(2/3) − a_C Z²/A^(1/3) − a_A(A−2Z)²/A ± δ",
       "sihirli sayılar: 2, 8, 20, 28, 50, 82, 126",
       "tepkime hızı = σ·Φ·N"],
  ex_tr=["U-235'in termal notron fisyon tesir kesiti 585 barn, hizli "
         "notron icin ~1 barn. Oran 585. Fisyonda cikan notronlar 2 MeV "
         "mertebesinde HIZLIDIR; onlari yavaslatmadan zincirleme tepkime "
         "surmez. Grafit ya da agir su moderator olarak tam bu isi "
         "yapar: notronu termal enerjiye (0,025 eV) indirip tesir "
         "kesitini yuzlerce kat buyutur."],
  ex_en=["Thermal fission of U-235 has a 585 barn cross section versus ~1 "
         "barn for fast neutrons, which is why reactors need a moderator."],
  kw="cekirdek modelleri|kabuk modeli|sivi damla modeli|sihirli sayilar|"
     "weizsacker|baglanma enerjisi egrisi|nukleer tepkime|moderator|"
     "fisyon tesir kesiti|nuclear shell model|magic numbers|liquid drop",
  related="nukleer|baglanma_enerjisi"),

T("yildiz_evrimi", "Yıldız Yapısı ve Evrimi",
  "Stellar Structure and Evolution", """
Yildiz, kutle cekimi ile basincin milyarlarca yil suren dengesidir.
Denge bozuldugunda yildizin kaderi tek bir sayiya baglidir: KUTLESI.

**Hidrostatik denge:** dP/dr = −Gρ(r)m(r)/r². Ic basinc, ustteki
katmanlarin agirligini tasir. Enerji uretimi durursa basinc duser ve
yildiz coker — yildizin parlamasi, cokmesini engelledigi icin sarttir.

**Enerji kaynagi:** Cekirdekte hidrojen fuzyonu. Gunes'te proton-proton
zinciri, daha agir yildizlarda CNO cevrimi baskindir. Fuzyon hizi
sicakliga asiri duyarlidir (CNO icin ~T¹⁷), bu yuzden yildizlar cok
kararli bir termostat gibi calisir.

**Hertzsprung-Russell diyagrami:** Parlaklik-sicaklik grafigi. Yildizlarin
%90'i ANAKOL uzerindedir; bu, hidrojen yaktiklari donemdir. Kutle
buyudukce yildiz daha parlak ve daha KISA omurludur: L ∼ M³·⁵ oldugundan
omur ∼ M/L ∼ M^(−2,5). On kat agir bir yildiz Gunes'ten yaklasik 300 kat
kisa yasar.

**Son evre — kutleye gore:**
- M < 8 M☉ : dis katmanlar atilir, geriye BEYAZ CUCE kalir.
- 8-25 M☉ : cekirdek cokmesi supernovasi → NOTRON YILDIZI.
- > 25 M☉ : → KARA DELIK.

**Chandrasekhar siniri:** Beyaz cuceyi ayakta tutan sey, elektronlarin
DEJENERE basincidir — Pauli dislama ilkesinin makroskobik sonucu.
Ama kutle 1,44 M☉'i asarsa elektronlar goreli hale gelir, basinc yeterince
hizli artamaz ve cokme kacinilmaz olur. Ia tipi supernovalarin hepsinin
ayni parlakligi vermesinin sebebi budur; kozmolojide "standart mum"
olarak kullanilmalari ve evrenin hizlanan genislemesinin bu yolla
bulunmasi buradan gelir.
""", """
A star is a balance between gravity and pressure. On the main sequence it
burns hydrogen, with L ~ M^3.5 so massive stars die fastest. The endpoint
depends on mass: white dwarf, neutron star or black hole. White dwarfs are
supported by electron degeneracy pressure and cannot exceed the
Chandrasekhar limit of 1.44 solar masses — which is why type Ia supernovae
are standard candles.
""",
  eqs=["dP/dr = −Gρm/r²", "L ∼ M^3.5", "ömür ∼ M^(−2.5)",
       "M_Ch ≈ 1,44 M☉"],
  ex_tr=["Gunes'in anakol omru ~10 milyar yil. 10 M☉'lik bir yildiz icin "
         "omur ∼ 10 × 10^(−2,5) = 10 / 316 ≈ 32 milyon yil. Yani on kat "
         "agir yildiz, 300 kattan fazla kisa yasar. Evrendeki agir "
         "elementlerin hizla uretilmis olmasinin sebebi budur: en agir "
         "yildizlar cok cabuk dogup cok cabuk patlar."],
  ex_en=["A 10 solar mass star lives about 32 million years versus the "
         "Sun's 10 billion — heavy elements are produced fast."],
  kw="yildiz evrimi|yildiz yapisi|hidrostatik denge|hertzsprung russell|"
     "anakol|beyaz cuce|notron yildizi|chandrasekhar siniri|"
     "dejenere basinc|standart mum|stellar evolution|white dwarf|"
     "chandrasekhar limit",
  related="kara_delik|nukleer"),

T("elektronik", "Yarıiletken Devre Elemanları",
  "Semiconductor Devices", """
Fizik laboratuvarinin ve her olcum duzeneginin dili elektroniktir. Uc
eleman yeter: diyot, transistor, islemsel yukselteC.

**Diyot:** p-n eklemi. Ileri yonde ~0,7 V'tan sonra iletir, ters yonde
iletmez. Akim ustel bagintiya uyar:
    I = I₀(e^(qV/nkT) − 1)
Buradaki kT/q ≈ 25,7 mV oda sicakliginda "termal gerilim"dir; yani
diyodun davranisi dogrudan ISTATISTIK FIZIKTEN gelir. Kullanimi:
dogrultma, koruma, LED, gunes hucresi (ayni eklem, ters yonde calisir).

**Transistor (BJT):** Kucuk taban akimi, buyuk kolektor akimini denetler:
I_C = β·I_B, β tipik olarak 100-300. Anahtar ya da yukselteC olarak
kullanilir. MOSFET'te denetim akimla degil GERILIMLE yapilir; sayisal
devrelerin tamami bu yuzden MOSFET'tir.

**Islemsel yukselteC (opamp):** Cok yuksek kazancli fark yukselteci.
Geri beslemeli kullanildiginda iki altin kural gecerlidir:
1. Girisler arasi gerilim farki sifirdir (sanal kisa devre).
2. Girislerden akim akmaz.
Bu iki kuralla evirici yukseltecin kazanci dogrudan cikar:
    V_out/V_in = −R_f/R_in
Kazanc yalnizca DIRENC ORANINA baglidir; opampin kendi kazancina bagli
DEGILDIR. Geri beslemenin gucu budur ve ayni fikir denetim kuramindan
biyolojiye kadar her yerdedir.

**Laboratuvarda:** Yukselteci fotodiyot ile birlestirip isik olcersiniz;
termocift ile sicaklik olcersiniz. Olcum duzeneginin kalitesi cogu zaman
deneyin kalitesini belirler.
""", """
Three devices cover most laboratory electronics. The diode's exponential
I-V comes straight from statistical physics, with kT/q = 25.7 mV at room
temperature. A bipolar transistor gives I_C = beta·I_B; MOSFETs switch on
voltage, which is why digital logic uses them. With feedback, an op-amp's
gain is set only by a resistor ratio, not by the amplifier itself.
""",
  eqs=["I = I₀(e^(qV/nkT) − 1)", "kT/q ≈ 25,7 mV (300 K)",
       "I_C = β·I_B", "V_out/V_in = −R_f/R_in"],
  ex_tr=["Evirici yukselteC: R_in = 1 kΩ, R_f = 47 kΩ. Kazanc "
         "−47 kΩ/1 kΩ = −47. Giristeki 10 mV'luk termocift sinyali "
         "cikista 470 mV olur; eksi isaret yalnizca faz tersligini "
         "gosterir. Opampin acik cevrim kazanci 100.000 olsa da sonuc "
         "degismez — hesap yalnizca iki dirence baglidir. Devrenin "
         "elemanlardan bagimsiz calismasi tam da bu yuzdendir."],
  ex_en=["With R_in = 1 k and R_f = 47 k the gain is -47, independent of "
         "the op-amp's own open-loop gain of 100000."],
  kw="diyot|diyot nedir|p-n eklemi|transistor|transistor calisma prensibi|"
     "bjt|mosfet|islemsel yukseltec|opamp|op-amp|evirici yukseltec|"
     "geri besleme|elektronik|diode|transistor|operational amplifier",
  related="yariiletken|bant_kurami"),

T("sayisal_yontemler_fizik", "Fizikte Sayısal Yöntemler",
  "Numerical Methods in Physics", """
Fizik problemlerinin cogunun analitik cozumu YOKTUR. Uc cisim problemi,
gercek potansiyeller, akiskanlar — hepsi sayisal cozulur. Onemli olan
yontemin ne zaman guvenilir oldugunu bilmektir.

**Diferansiyel denklem cozumu:**
- **Euler:** y_{n+1} = y_n + h·f(t_n,y_n). Basit ama hatasi O(h); enerji
  sistematik olarak KAYAR. Yorunge hesabinda gezegen spiral cizerek
  kacar — bu yontem hatasidir, fizik degil.
- **Runge-Kutta 4 (RK4):** Hata O(h⁴). Genel amacli standart yontem.
- **Simplektik (Verlet):** Enerjiyi uzun vadede KORUR. Gezegen ve
  molekuler dinamik simulasyonlarinda RK4'ten daha uygundur, cunku
  hassasiyetten cok KARARLILIK gerekir.

Ders: "daha dogru yontem" her zaman "daha iyi yontem" degildir; hangi
niceligin korunmasini istediginize baglidir.

**Kok bulma:** Bisection (yavas ama garantili), Newton-Raphson (hizli
ama turev ister ve isinlanabilir).

**Integrasyon:** Yamuk O(h²), Simpson O(h⁴). Cok boyutlu integrallerde
Monte Carlo kullanilir: hatasi 1/√N'dir ve BOYUTTAN BAGIMSIZDIR — bu
yuzden istatistik fizikte ve parcacik simulasyonlarinda vazgecilmezdir.

**Kararlilik:** Isi denklemi gibi PDE'lerde acik semalar ancak
    Δt ≤ Δx²/(2α)
kosuluyla kararlidir (CFL kosulu). Bu kosul saglanmazsa cozum patlar —
ve patlayan sey fizik degil, algoritmadir.

**Her zaman sinayin:** Bilinen bir analitik cozumle karsilastirin,
adim boyutunu yariya indirip sonucun degismedigini gorun, korunan
buyuklukleri (enerji, momentum) izleyin.
""", """
Most physics problems have no closed-form solution. Euler is O(h) and
drifts in energy; RK4 is O(h^4); symplectic integrators conserve energy
long-term and are preferred for orbits and molecular dynamics. Monte Carlo
error scales as 1/sqrt(N) independent of dimension. Explicit PDE schemes
need the CFL condition or they blow up — an algorithmic failure, not a
physical one.
""",
  eqs=["Euler: y_{n+1} = y_n + h·f", "RK4 hata ∼ O(h⁴)",
       "Monte Carlo hata ∼ 1/√N", "CFL: Δt ≤ Δx²/(2α)"],
  ex_tr=["Dairesel yorunge simulasyonu, h = 0,01 adimla. Euler ile bir "
         "yildan sonra yaricap yaklasik %5 buyur ve yorunge disari "
         "acilir; RK4 ile hata 10⁻⁶ mertebesinde kalir; Verlet ile "
         "yaricap dalgalanir ama ORTALAMASI sabittir. Uc yontem de "
         "'yanlis' degil — biri hizli, biri hassas, biri kararli. "
         "Milyon adimlik bir simulasyonda dogru secim Verlet'tir."],
  ex_en=["Over one orbit-year Euler drifts ~5% outward, RK4 stays near "
         "1e-6, and Verlet oscillates about a constant mean — the right "
         "choice for long runs is the symplectic one."],
  kw="sayisal yontemler|euler yontemi|runge kutta|rk4|verlet|"
     "simplektik|diferansiyel denklem sayisal cozumu|kok bulma|"
     "newton raphson|simpson kurali|cfl kosulu|kararlilik|"
     "numerical methods|runge kutta|symplectic integrator",
  related="matematiksel_yontemler|monte_carlo"),
]

# ── Ucuncu grup: mufredat taramasinda cekirdeksiz kalan basliklar ─────────
# Olculdu: "statik denge" sorusuna FIZYOTERAPI makalesi, "maxwell boltzmann
# dagilimi" sorusuna Boltzmann SABITI, "normal modlar" sorusuna galaksi
# morfolojisi makalesi donuyordu.

MUFREDAT_KONULARI += [

T("statik_denge", "Statik Denge ve Yapılar", "Static Equilibrium", """
Bir cisim duruyorsa iki kosul birden saglanir:
    ΣF = 0   ve   Στ = 0
Ikincisi cogu zaman unutulur. Kuvvetler dengelense bile tork dengesizse
cisim DONER.

**Tork nerede alinir:** Denge halinde toplam tork HER noktaya gore
sifirdir. Bu bir kolayliktir: bilinmeyen bir kuvvetin uygulama noktasini
donme merkezi secerseniz o kuvvet denklemden duser.

**Kutle merkezi:** Cismin agirligi kutle merkezine etkiyormus gibi
hesaplanir. Bir cisim, kutle merkezinin izdusumu DESTEK ALANI icinde
kaldigi surece devrilmez. Pisa Kulesi hala ayakta cunku kutle merkezi
tabanin disina cikmadi.

**Belirsiz problemler:** Dort ayakli bir masada dort bilinmeyen tepki
kuvveti vardir ama denge yalnizca uc denklem verir. Bu tur problemler
STATIKCE BELIRSIZDIR; cozum icin cismin sekil degistirmesini
(elastikligi) hesaba katmak gerekir. Sallanan masalarin sebebi budur.

**Mukavemet baglantisi:** Gercek yapilarda kirisin her kesitinde ic
kuvvet ve moment vardir; kopru ve bina hesaplari bu dagilimlari izler.
""", """
Equilibrium needs both zero net force and zero net torque. Torque can be
evaluated about any point, which lets you eliminate an unknown force. A
body tips when the projection of its centre of mass leaves the support
base. Four-legged tables are statically indeterminate: equilibrium alone
does not fix the reactions, so elasticity must be included.
""",
  eqs=["ΣF = 0", "Στ = 0", "τ = r·F·sinθ", "x_cm = Σmᵢxᵢ/Σmᵢ"],
  ex_tr=["4 m'lik 20 kg'lik homojen tahta, bir ucundan 1 m iceride "
         "desteklenmis. Uzun ucun ucuna kac kg konursa devrilir? "
         "Destek noktasina gore tork: tahtanin agirligi kutle "
         "merkezinde (2 m'de), yani destekten 1 m saga: 20·9,81·1 = "
         "196 N·m saat yonunde... Denge icin kisa taraftaki 1 m'lik "
         "kola konacak yuk m·9,81·1 ≥ 196 → m ≥ 20 kg. Yani en az "
         "kendi kutlesi kadar."],
  ex_en=["A 4 m, 20 kg plank supported 1 m from one end needs at least "
         "20 kg on the short arm to balance."],
  kw="statik denge|denge kosullari|tork dengesi|kutle merkezi|devrilme|"
     "statikce belirsiz|kiris|static equilibrium|torque balance",
  related="tork|newton_yasalari"),

T("normal_modlar", "Normal Modlar ve Özdeğer Problemi",
  "Normal Modes and the Eigenvalue Problem", """
Birbirine bagli iki sarkac karisik, duzensiz gorunen bir hareket yapar.
Ama DOGRU koordinatlarda bakilirsa hareket, her biri basit harmonik olan
bagimsiz parcalara ayrilir. Bunlara NORMAL MOD denir.

**Kurulum:** Kucuk salinimlarda hareket denklemleri
    M ẍ = −K x
bicimindedir (M kutle matrisi, K sertlik matrisi). x = A e^(iωt) denenirse
    (K − ω²M) A = 0
Bu bir OZDEGER problemidir: cozumun var olmasi icin det(K − ω²M) = 0.
Kokler normal mod frekanslarini, ozvektorler mod SEKILLERINI verir.

**Fiziksel anlam:** Normal modda butun parcaciklar AYNI frekansta ve
sabit faz iliskisiyle salinir. Genel hareket, normal modlarin
superpozisyonudur — kac serbestlik derecesi varsa o kadar mod.

**Nerede karsimiza cikar:** Molekullerin titresim modlari (IR
spektroskopisi bunlari olcer), koprulerin rezonans frekanslari, kristal
orgu titresimleri (fononlar), bina deprem analizi.

**Ozdeger problemi genel olarak:** A v = λ v. Fizikte her yerde:
eylemsizlik tensorunun ozvektorleri ana eksenlerdir; kuantum mekaniginde
ozdegerler olculebilir degerlerdir; gerilme tensorunde ozdegerler ana
gerilmelerdir. Hepsinde ayni soru sorulur: "bu donusumun DEGISTIRMEDIGI
yonler hangileri?"
""", """
Coupled oscillators look complicated until you change coordinates: the
motion separates into independent normal modes. Setting x = A exp(iwt)
turns the equations into the eigenvalue problem (K - w^2 M)A = 0, whose
eigenvalues are the mode frequencies and eigenvectors the mode shapes.
The same structure appears for the inertia tensor, stress tensor and
quantum observables.
""",
  eqs=["M·ẍ = −K·x", "det(K − ω²M) = 0", "A·v = λ·v"],
  ex_tr=["Ayni yay sabiti k ile duvara ve birbirine bagli iki esit kutle. "
         "det(K − ω²M) = 0 iki kok verir: ω₁ = √(k/m) (kutleler BIRLIKTE "
         "hareket eder, ortadaki yay hic gerilmez) ve ω₂ = √(3k/m) "
         "(kutleler ZIT yonde hareket eder). Oran √3 = 1,732. Simetrik "
         "mod her zaman daha DUSUK frekansta olur, cunku daha az yay "
         "gerilir."],
  ex_en=["Two coupled masses give w1 = sqrt(k/m) (in phase) and "
         "w2 = sqrt(3k/m) (out of phase); the symmetric mode is always "
         "lower because fewer springs stretch."],
  kw="normal modlar|normal mod|bagli osilatorler|mod sekli|"
     "ozdeger problemi|ozdeger ozvektor|kosegenlestirme|"
     "titresim modlari|normal modes|eigenvalue problem|coupled oscillators",
  related="harmonik|tensor"),

T("poisson_laplace", "Poisson ve Laplace Denklemleri",
  "Poisson and Laplace Equations", """
Elektrostatigin merkezi problemi sudur: yuk dagilimi ve sinir kosullari
verilmis, potansiyeli bul.

**Denklemler:**
    ∇²V = −ρ/ε₀   (Poisson — yuk varken)
    ∇²V = 0        (Laplace — yuksuz bolgede)

**Teklik teoremi:** Sinir kosullari verilmisse cozum TEKTIR. Bu, fizikte
"kurnazca tahmin" yapmayi mesru kilar: bir sekilde bir cozum bulduysaniz
ve sinir kosullarini sagliyorsa, O cozumdur. Goruntu yukleri yonteminin
gecerliligi tam olarak buna dayanir.

**Ortalama deger ozelligi:** Laplace denkleminin cozumu, herhangi bir
kurenin merkezinde, kure yuzeyindeki ORTALAMAYA esittir. Sonuc: yuksuz
bolgede potansiyelin yerel maksimumu ya da minimumu OLAMAZ. Earnshaw
teoremi budur — durgun yuklerle kararli levitasyon imkansizdir.
Manyetik levitasyon ancak diyamanyetizma ya da aktif denetimle olur.

**Cozum yontemleri:**
1. **Degiskenlerine ayirma:** Simetriye uygun koordinatta V = R(r)Θ(θ)Φ(φ)
   yazilir; kuresel simetride Legendre polinomlari, silindirikte Bessel
   fonksiyonlari cikar.
2. **Goruntu yukleri:** Iletken sinirlar, kurgusal yuklerle degistirilir.
3. **Green fonksiyonu:** Genel cozum.
4. **Sayisal (relaksasyon):** Her nokta komsularinin ortalamasi yapilir;
   ortalama deger ozelliginin dogrudan uygulanmasidir.
""", """
Poisson's equation with boundary conditions has a unique solution, which
legitimises clever guessing such as image charges. Laplace solutions obey
the mean value property, so no local extremum exists in a charge-free
region — Earnshaw's theorem, forbidding stable electrostatic levitation.
Separation of variables produces Legendre or Bessel functions depending on
the symmetry.
""",
  eqs=["∇²V = −ρ/ε₀", "∇²V = 0", "V(merkez) = ⟨V⟩_yüzey"],
  ex_tr=["Yaricapi R olan topraklanmis iletken kurenin merkezinden d > R "
         "uzakta q yuku. Goruntu yuku q' = −qR/d, merkezden R²/d "
         "uzakliktadir. Kure yuzeyinde potansiyel kendiliginden sifir "
         "cikar; teklik teoremi geregi bu CEVAPTIR. Yuke etkiyen kuvvet "
         "cekicidir: topraklanmis notr bir iletken, yuklu cismi her zaman "
         "ceker — balonun duvara yapismasinin sebebi."],
  ex_en=["A grounded sphere's image charge is -qR/d at R^2/d; uniqueness "
         "guarantees this is the solution, and the force is always "
         "attractive."],
  kw="poisson denklemi|laplace denklemi|teklik teoremi|"
     "ortalama deger ozelligi|earnshaw teoremi|degiskenlerine ayirma|"
     "goruntu yukleri yontemi|sinir deger problemi|"
     "poisson equation|laplace equation|uniqueness theorem|image charges",
  related="elektrik_potansiyeli|green_fonksiyonu"),

T("dipol_isimasi", "Dipol Işıması ve Larmor Formülü",
  "Dipole Radiation and the Larmor Formula", """
Durgun yuk isima yapmaz. Sabit hizla giden yuk de yapmaz. Isima
IVMELENEN yuklerden gelir — butun anten fizigi ve isik uretimi budur.

**Larmor formulu:** Goreli olmayan ivmeli bir yukun yaydigi guc
    P = q²a²/(6πε₀c³)
Guc ivmenin KARESIYLE artar ve c³ ile boluner — bu yuzden gunluk
ivmelerde isima olculemeyecek kadar zayiftir.

**Yon dagilimi:** dP/dΩ ∝ sin²θ. Isima ivme ekseni boyunca SIFIRDIR, dik
yonde en buyuktur. Bir anteni tepesinden dinlerseniz sinyal alamazsiniz;
antenin "olu bolgesi" budur.

**Dipol isimasi:** Salinan bir dipol icin
    P = ω⁴p₀²/(12πε₀c³)
ω⁴ bagimliligi cok onemlidir: yuksek frekans cok daha guclu isir. Gogun
mavi olmasi (Rayleigh sacilmasi) tam olarak bu ω⁴ carpanidir — sacilma,
ikincil dipol isimasidir.

**Klasik atomun cokusu:** Bohr yorungesindeki elektron ivmelidir; Larmor
formulune gore isima yayip ~10⁻¹¹ saniyede cekirdege dusmeliydi. Klasik
fizigin atomu aciklayamamasinin en keskin kaniti budur ve kuantum
kuramina gecisin sebeplerinden biridir.

**Gecikmeli potansiyeller:** Alanlar anlik degil, r/c gecikmesiyle
ulasir. Isimanin kaynagi bu gecikmedir; alan cizgilerindeki "kink"
isik hiziyla disari yayilir.
""", """
Only accelerating charges radiate. Larmor's formula gives P = q^2 a^2 /
(6 pi eps0 c^3), with a sin^2(theta) pattern that vanishes along the
acceleration axis. Oscillating dipoles radiate as omega^4, which is why
Rayleigh scattering favours blue. Applied to the Bohr atom, the same
formula predicts collapse in 10^-11 s — a decisive failure of classical
physics.
""",
  eqs=["P = q²a²/(6πε₀c³)", "dP/dΩ ∝ sin²θ", "P = ω⁴p₀²/(12πε₀c³)"],
  ex_tr=["Bohr yarıcapinda (0,529 Å) elektronun ivmesi a = v²/r ≈ "
         "9,0×10²² m/s². Larmor: P = (1,6×10⁻¹⁹)²(9,0×10²²)²/"
         "(6π×8,85×10⁻¹²×2,7×10²⁵) ≈ 4,6×10⁻⁸ W. Elektronun toplam "
         "enerjisi 13,6 eV = 2,2×10⁻¹⁸ J oldugundan omru "
         "2,2×10⁻¹⁸/4,6×10⁻⁸ ≈ 5×10⁻¹¹ s cikar. Klasik fizige gore atom "
         "bir saniyenin milyarda birinden kisa surede cokerdi."],
  ex_en=["Larmor radiation would collapse the Bohr atom in about 5e-11 s."],
  kw="dipol isimasi|larmor formulu|ivmeli yuk isimasi|anten isimasi|"
     "gecikmeli potansiyeller|klasik atomun cokusu|"
     "dipole radiation|larmor formula|radiating charge",
  related="multipol|elektromanyetik_dalga|sacilma"),

T("varyasyonel_yontem", "Varyasyonel Yöntem ve Yaklaşık Çözümler",
  "Variational Method and Approximations", """
Schrodinger denklemi cok az sistemde tam cozulur. Varyasyonel yontem,
tam cozum olmadan TEMEL DURUM ENERJISINE guvenilir bir ust sinir verir.

**Varyasyonel ilke:** Herhangi bir normalize deneme fonksiyonu ψ icin
    E[ψ] = ⟨ψ|H|ψ⟩ ≥ E₀
Yani hesapladiginiz enerji her zaman gercek temel durum enerjisinden
BUYUK ya da esittir. Deneme fonksiyonunu parametreli secip enerjiyi
minimize edersiniz; ne kadar iyi tahmin, o kadar yakin sonuc.

**Neden guvenilir:** Sonuc bir SINIRDIR, tahmin degil. Iki farkli deneme
fonksiyonundan kucuk enerji vereni daha iyidir — karsilastirma olcutu
kendiliginden gelir.

**Neden dikkatli olunmali:** Enerji iyi cikar ama dalga fonksiyonu
kotu olabilir. Enerji, hataya IKINCI mertebeden duyarlidir (δE ∼ δψ²),
bu yuzden vasat bir dalga fonksiyonu bile iyi enerji verir. Baska
buyuklukler (dipol momenti, yogunluk) icin ayni sey gecerli DEGILDIR.

**Diger yaklasik yontemler:**
- **Perturbasyon:** Hamiltoniyen cozulebilir bir kismin uzerine KUCUK bir
  ek ise kullanilir.
- **WKB:** Potansiyel yavas degisiyorsa; tunelleme olasiligi bu yolla
  hesaplanir.
- **Hartree-Fock:** Cok elektronlu sistemlerde her elektron, digerlerinin
  ORTALAMA alaninda hareket eder.

Hangi yontemi secmek gerektigi, sorunun yapisina bakmakla anlasilir —
lisans kuantum dersinin asil ogrettigi beceri budur.
""", """
The variational principle guarantees that the expectation value of H in
any trial state is an upper bound on the ground state energy, so
minimising over parameters gives a reliable bound rather than a guess.
Energy is second-order insensitive to errors in the wavefunction, so good
energies can come from mediocre wavefunctions — a warning when computing
other observables.
""",
  eqs=["E[ψ] = ⟨ψ|H|ψ⟩/⟨ψ|ψ⟩ ≥ E₀", "∂E/∂α = 0"],
  ex_tr=["Helyum atomu: elektronlarin birbirini perdelemesi yuzunden "
         "etkin cekirdek yuku Z'yi degisken alalim. Varyasyonel hesap "
         "Z_etkin = 27/16 = 1,6875 verir (gercek Z = 2). Enerji "
         "−77,5 eV cikar; deneysel deger −79,0 eV. Hata yalnizca %1,9 — "
         "ustelik tek parametreli, cok basit bir deneme fonksiyonuyla. "
         "Z_etkin < 2 olmasinin fiziksel anlami: her elektron, digerinin "
         "cekirdegi kismen perdeledigini 'gorur'."],
  ex_en=["A one-parameter trial function gives Z_eff = 1.6875 for helium "
         "and an energy within 1.9% of experiment."],
  kw="varyasyonel yontem|varyasyonel ilke|deneme fonksiyonu|"
     "rayleigh ritz|yaklasik yontemler|wkb|hartree fock|"
     "variational method|trial wavefunction",
  related="kuantum_formalizm|perturbasyon"),

T("hiz_dagilimi", "Maxwell-Boltzmann Hız Dağılımı",
  "Maxwell-Boltzmann Speed Distribution", """
Bir gazdaki molekullerin hepsi ayni hizda degildir; bir DAGILIMLARI
vardir. Maxwell'in 1860'ta buldugu bu dagilim, istatistiksel fizigin
ilk buyuk basarisidir.

**Dagilim:**
    f(v) = 4π(m/2πkT)^(3/2) · v² · e^(−mv²/2kT)
Iki carpanin yarisidir: v² (hizli olmanin daha cok "yol" sunmasi —
faz uzayi hacmi) ve ustel Boltzmann carpani (yuksek enerjinin daha
az olasi olmasi). Carpim, tepe yapan asimetrik bir egri verir.

**Uc karakteristik hiz:**
- En olasi:      v_p = √(2kT/m)
- Ortalama:      v̄ = √(8kT/πm) = 1,128 v_p
- Karekok ortalama kare: v_rms = √(3kT/m) = 1,225 v_p

Sirasi her zaman v_p < v̄ < v_rms'dir; dagilimin sag kuyrugu uzun
oldugu icin ortalamalar tepe degerinden buyuktur.

**Sonuclari:**
- **Kacan atmosfer:** Kuyrukta kacis hizini asan molekuller hep vardir.
  Bu yuzden Dunya hidrojeni ve helyumu tutamaz, azotu tutar. Ay ise
  hicbirini tutamaz.
- **Tepkime hizi:** Arrhenius carpani exp(−Ea/RT), bu dagilimin engeli
  asan kismini sayar.
- **Buharlasma sogutmasi:** En hizli molekuller kacar, geriye kalan
  ortalama duser.
- **Doppler genislemesi:** Spektrum cizgilerinin genisligi bu hiz
  dagilimindan gelir; yildiz sicakligi boyle olculur.
""", """
Molecular speeds follow f(v) proportional to v^2 exp(-mv^2/2kT), the
product of phase-space volume and the Boltzmann factor. The most probable,
mean and rms speeds always appear in that order. The high-speed tail
explains atmospheric escape, Arrhenius reaction rates, evaporative cooling
and Doppler line broadening.
""",
  eqs=["f(v) ∝ v²·e^(−mv²/2kT)", "v_p = √(2kT/m)", "v̄ = √(8kT/πm)",
       "v_rms = √(3kT/m)"],
  ex_tr=["Oda sicakliginda (300 K) azot molekulu (28 u = 4,65×10⁻²⁶ kg): "
         "v_rms = √(3×1,38×10⁻²³×300/4,65×10⁻²⁶) = 517 m/s. Sesin "
         "havadaki hizi 343 m/s — ayni mertebede, ve tesaduf degil: ses "
         "molekul carpismalariyla tasinir, dolayisiyla molekul hizini "
         "asamaz. Hidrojen icin ayni hesap 1930 m/s verir; Dunya'nin "
         "kacis hizi 11,2 km/s olsa da dagilimin kuyrugu milyarlarca "
         "yilda hidrojeni tuketmeye yeter."],
  ex_en=["Nitrogen at 300 K has v_rms = 517 m/s, close to the 343 m/s "
         "speed of sound — not a coincidence, since sound travels by "
         "molecular collisions."],
  kw="maxwell boltzmann dagilimi|hiz dagilimi|en olasi hiz|"
     "ortalama hiz|rms hiz|molekul hizlari|atmosfer kacisi|"
     "maxwell boltzmann distribution|speed distribution|rms speed",
  related="ideal_gaz|istatistik_topluluk|boltzmann_faktoru"),

T("laplace_donusumu", "Laplace ve Fourier Dönüşümleri",
  "Laplace and Fourier Transforms", """
Ikisi de ayni isi yapar: TUREVI CARPMAYA cevirir, boylece diferansiyel
denklemi cebirsel denkleme dondurur.

**Laplace donusumu:**
    F(s) = ∫₀^∞ f(t)e^(−st) dt
Temel ozellik: L{f′} = sF(s) − f(0). Yani turev, s ile carpma olur ve
baslangic kosulu KENDILIGINDEN denkleme girer. Baslangic deger
problemleri icin en pratik yontemdir.

**Yontem:** Denklemi donustur → cebirsel coz → ters donusturu al.
Devre analizinde direnc R, indukto sL, kondansator 1/sC olur; butun
devre bir cebir problemine iner.

**Transfer fonksiyonu:** H(s) = Cikis(s)/Giris(s). Kutuplarin yeri
sistemin kararliligini soyler: gercel kismi pozitif kutup varsa sistem
patlar. Denetim kuraminin temeli budur.

**Fourier donusumu:**
    F(ω) = ∫ f(t)e^(−iωt) dt
Sinyali frekans bilesenlerine ayirir. Laplace baslangic degeri
problemleri icin, Fourier ise SUREKLI rejim ve spektrum analizi icin
uygundur.

**Fizikteki yeri:** Kuantum mekaniginde konum ve momentum uzaylari
birbirinin Fourier donusumudur — belirsizlik ilkesi, dar bir fonksiyonun
donusumunun genis olmasi gercegidir; matematiksel bir teoremdir.
Kristalografide olculen kirinim deseni, elektron yogunlugunun Fourier
donusumudur.

**Evrisim teoremi:** Zaman uzayindaki evrisim, frekans uzayinda
carpmadir. Sinyal suzme, goruntu isleme ve olcum aletinin cozunurluk
etkisi bu teoremle hesaplanir.
""", """
Both transforms turn differentiation into multiplication, converting
differential equations into algebra. Laplace suits initial value problems
and circuits (R, sL, 1/sC) and gives transfer functions whose poles decide
stability. Fourier suits steady state and spectra. Position and momentum
in quantum mechanics are Fourier conjugates, which is where the
uncertainty principle comes from mathematically.
""",
  eqs=["F(s) = ∫₀^∞ f(t)e^(−st)dt", "L{f′} = sF(s) − f(0)",
       "F(ω) = ∫f(t)e^(−iωt)dt", "L{f*g} = F·G"],
  ex_tr=["RC devresi: RC·dV/dt + V = V₀. Laplace alalim: "
         "RC(sV(s) − 0) + V(s) = V₀/s → V(s) = V₀/(s(1+RCs)). Ters "
         "donusum V(t) = V₀(1 − e^(−t/RC)) verir. Diferansiyel denklem "
         "hic cozulmedi; yalnizca cebir yapildi ve bir tablodan "
         "bakildi. Muhendislikte bu yontemin tercih edilmesinin sebebi "
         "budur."],
  ex_en=["Laplace turns the RC equation into algebra, giving "
         "V = V0(1 - exp(-t/RC)) without solving a differential "
         "equation."],
  kw="laplace donusumu|fourier donusumu|transfer fonksiyonu|"
     "evrisim teoremi|frekans uzayi|kutup kararlilik|"
     "laplace transform|fourier transform|convolution theorem",
  related="fourier|matematiksel_yontemler"),

T("kristal_yapi", "Kristal Yapı ve Ters Örgü",
  "Crystal Structure and the Reciprocal Lattice", """
Kati hal fiziginin butun dili PERIYODIKLIK uzerine kuruludur.

**Bravais orgusu:** Uzayda, her noktadan bakildiginda ayni gorunen
nokta kumesi. Uc boyutta tam 14 tane vardir; bu bir deney sonucu degil,
SIMETRI siniflandirmasidir (Bravais, 1848).

**Birim hucre:** Orgeyi doldurmaya yeten en kucuk yapi tasi. Yaygin
yapilar: basit kubik, hacim merkezli (BCC — demir), yuzey merkezli
(FCC — bakir, altin), hekzagonal siki paket (HCP — cinko).

**Dolgu carpani:** FCC ve HCP'de %74 — kurelerin ulasabildigi en yuksek
yogunluk (Kepler sanisi, 1998'de kanitlandi). BCC'de %68, basit kubikte
%52. Metallerin cogunun FCC ya da HCP olmasinin sebebi budur.

**Miller indisleri (hkl):** Duzlemleri adlandirmanin standart yolu.
Duzlemin eksenleri kestigi noktalarin TERSLERI alinip tam sayiya
cevrilir. (100), (110), (111) en cok gecen duzlemlerdir.

**Ters orgu:** Gercek orgunun Fourier donusumu. Kirinim deneyinde
gordugunuz sey dogrudan gercek orgu DEGIL, ters orgudur. Bragg kosulu
ters orguda basitce "sacilma vektoru bir ters orgu vektorune esit
olmali" der.

**Brillouin bolgesi:** Ters orgunun birim hucresi. Elektron ve fonon
dagilim bagintilarinin cizildigi yer burasidir; bant kurami bu bolge
uzerinde tanimlanir.
""", """
Crystals are classified by their 14 Bravais lattices. Packing fractions
are 74% for FCC and HCP — the densest possible — 68% for BCC and 52% for
simple cubic. Miller indices label planes by reciprocal intercepts.
Diffraction measures the reciprocal lattice, not the direct one, and the
Brillouin zone (its unit cell) is where band structure is plotted.
""",
  eqs=["dolgu(FCC) = π/(3√2) = 0,74", "1/d² = (h²+k²+l²)/a² (kübik)",
       "G = h·b₁ + k·b₂ + l·b₃"],
  ex_tr=["FCC bakirin orgu sabiti a = 3,615 Å. (111) duzlemleri arasi "
         "uzaklik: d = a/√(1+1+1) = 3,615/1,732 = 2,087 Å. Cu-Kα "
         "isini (λ = 1,542 Å) icin Bragg: sinθ = λ/2d = "
         "1,542/(2×2,087) = 0,369 → θ = 21,7°, yani 2θ = 43,4°. "
         "Bakirin toz kirinim deseninde ilk siddetli tepe tam olarak "
         "buradadir."],
  ex_en=["Copper's (111) spacing of 2.087 A gives a first diffraction peak "
         "at 2-theta = 43.4 degrees with Cu-K-alpha."],
  kw="kristal yapi|bravais orgusu|birim hucre|fcc bcc hcp|"
     "miller indisleri|ters orgu|brillouin bolgesi|dolgu carpani|"
     "crystal structure|bravais lattice|reciprocal lattice|miller indices",
  related="bragg|bant_kurami"),

T("fonon_isi", "Fononlar ve Katıların Isı Sığası",
  "Phonons and the Heat Capacity of Solids", """
Kristalde atomlar yerlerinde durmaz; bagli yaylar gibi salinir. Bu
salinimlarin normal modlari kuantalandiginda FONON denir.

**Dagilim bagintisi:** Tek atomlu zincirde
    ω(k) = 2√(K/m)·|sin(ka/2)|
Kucuk k'de dogrusaldir (ω ≈ v_s k) — ses dalgasidir. Brillouin bolgesi
kenarinda duzlesir; orgu, dalga boyu orgu sabitine yaklasan dalgalari
tasiyamaz.

**Akustik ve optik dallar:** Birim hucrede iki farkli atom varsa iki dal
olusur. Akustik dalda komsu atomlar BIRLIKTE, optik dalda ZIT yonde
hareket eder. Optik fononlar isikla dogrudan etkilesir; IR sogurma ve
Raman sacilmasi bunlari olcer.

**Isi sigasi — tarihsel bir bilmece:**
- **Dulong-Petit (1819):** C = 3R, sicakliktan bagimsiz. Oda
  sicakliginda dogru, dusuk sicaklikta TAMAMEN yanlis.
- **Einstein (1907):** Tum modlar ayni frekansta varsayildi. Dusuk
  sicaklikta ustel duser — deneyden hizli.
- **Debye (1912):** Modlarin bir frekans dagilimi oldugu kabul edildi.
  Sonuc C ∝ T³ ve deneyle tam uyum. Katilarin isi sigasinin dusuk
  sicaklikta neden hizla azaldiginin dogru aciklamasi budur.

**Neden onemli:** Isi sigasi, metallerde elektron katkisiyla (C ∝ T)
birlikte olculur; C/T'nin T²'ye karsi grafigi dogru verir ve egimden
Debye sicakligi, kesim noktasindan elektron yogunlugu okunur. Bir
grafikten iki ayri fizik cikar.

**Isil iletim ve direnc:** Fononlar isiyi tasir; fonon-fonon ve
fonon-elektron sacilmasi ise elektrik direncinin sicaklikla artmasinin
sebebidir.
""", """
Lattice vibrations quantised into phonons have a dispersion that is linear
at small k (sound) and flattens at the zone boundary. Acoustic and optical
branches appear with two atoms per cell. Dulong-Petit fails at low
temperature; Einstein's model falls too fast; Debye's gives C proportional
to T^3, matching experiment.
""",
  eqs=["ω(k) = 2√(K/m)|sin(ka/2)|", "C_Dulong = 3R",
       "C_Debye ∝ T³ (düşük T)", "C_metal = γT + AT³"],
  ex_tr=["Bakirin Debye sicakligi Θ_D = 343 K. 10 K'de orgu isi sigasi "
         "C ∝ (T/Θ_D)³ = (10/343)³ = 2,5×10⁻⁵ — oda sicakligindaki "
         "degerin kirk binde biri. Bu yuzden dusuk sicaklikta "
         "elektronlarin dogrusal katkisi (γT) baskin hale gelir ve "
         "olculebilir; Sommerfeld katsayisi bu bolgede belirlenir."],
  ex_en=["Copper's lattice heat capacity at 10 K is 2.5e-5 of its room "
         "temperature value, letting the electronic term dominate."],
  kw="fonon|fononlar|orgu titresimleri|dagilim bagintisi|"
     "akustik optik fonon|debye modeli|einstein modeli|dulong petit|"
     "katilarin isi sigasi|phonon|debye model|heat capacity of solids",
  related="kristal_yapi|bant_kurami"),

T("yariiletken_fizigi", "Yarıiletken Fiziği ve Katkılama",
  "Semiconductor Physics and Doping", """
Yariiletkenin ozelligi, iletkenliginin KONTROL EDILEBILIR olmasidir.
Butun modern elektronik bu tek gercege dayanir.

**Bant araligi:** Si icin 1,12 eV, Ge 0,67 eV, GaAs 1,42 eV. Oda
sicakliginda kT = 0,026 eV; yani termal uyarilma ancak ustel carpanla
elektron gecirir: n_i ∝ e^(−Eg/2kT). Sicaklik arttikca yariiletkenin
direnci DUSER — metalin tersine.

**Katkılama:** Silisyuma (4 degerlikli) fosfor (5 degerlikli) katilirsa
fazla elektron kalir → n-tipi. Bor (3 degerlikli) katilirsa elektron
eksigi (bosluk) olusur → p-tipi. Katki yogunlugu, tasiyici sayisini
milyonlarca kat degistirebilir; iletkenlik "ayarlanabilir" hale gelir.

**Kutle etkisi yasasi:** n·p = n_i² her zaman gecerlidir. Bir tasiyici
turunu artirmak digerini azaltir.

**p-n eklemi:** n ve p bolgeleri birlestiginde sinirda difuzyon olur,
geride sabit iyonlar kalir ve bir TUKENIM BOLGESI ile ic gerilim olusur.
Silisyum icin bu ~0,7 V'tur — diyodun esik geriliminin sebebi budur.

**Uygulamalar ayni eklem:**
- Ileri yonde surulurse: diyot, LED (bosluk-elektron birlesmesi foton
  verir; renk bant araligiyla belirlenir).
- Ters yonde isikla: fotodiyot, gunes hucresi.
- Uc katmanli: transistor.

**Neden LED'in rengi sabit:** Foton enerjisi bant araligina esittir,
E = hf. GaN icin Eg ≈ 3,4 eV → mor-mavi. Mavi LED'in 1990'larda
bulunmasi (2014 Nobel) beyaz LED aydinlatmayi mumkun kildi.
""", """
Semiconductors matter because their conductivity is controllable. Intrinsic
carriers scale as exp(-Eg/2kT), so resistance falls with temperature,
opposite to metals. Doping changes carrier density by orders of magnitude
while np = ni^2 always holds. A p-n junction builds a depletion region and
a ~0.7 V built-in potential in silicon, which is the diode's threshold.
""",
  eqs=["n_i ∝ T^(3/2)·e^(−Eg/2kT)", "n·p = n_i²", "E_foton = E_g",
       "Si: E_g = 1,12 eV"],
  ex_tr=["Kirmizi LED'in dalga boyu 630 nm. Foton enerjisi "
         "E = hc/λ = 1240/630 = 1,97 eV. Bu, GaAsP'nin bant araligina "
         "karsilik gelir. Mavi LED icin 470 nm → 2,64 eV gerekir ve bu, "
         "GaN gibi genis bant aralikli malzeme ister; mavi LED'in "
         "kirmizidan otuz yil sonra bulunmasinin sebebi malzeme "
         "zorlugudur, fizik degil."],
  ex_en=["A 630 nm red LED corresponds to 1.97 eV; blue needs 2.64 eV, "
         "requiring wide-gap GaN."],
  kw="yariiletken|yariiletkenler|katkilama|n tipi p tipi|"
     "bant araligi|tukenim bolgesi|p-n eklemi|led rengi|"
     "kutle etkisi yasasi|semiconductor|doping|band gap|pn junction|"
     "p-n junction|p n junction|pn eklemi|diode physics|"
     "how does a p-n junction work",
  related="bant_kurami|elektronik"),

T("kirmizi_kayma_kozmoloji", "Kırmızıya Kayma ve Evrenin Genişlemesi",
  "Redshift and the Expansion of the Universe", """
Uzak galaksilerin tayfindaki cizgiler, laboratuvardakine gore daha uzun
dalga boyunda gorulur. Bu KIRMIZIYA KAYMADIR ve modern kozmolojinin
temel gozlemidir.

**Tanim:** z = (λ_gozlenen − λ_kaynak)/λ_kaynak

**Uc farkli sebep — karistirmamak onemli:**
1. **Doppler:** Kaynak bize gore hareket ediyorsa. Yildizlarin yerel
   hareketleri boyledir.
2. **Kozmolojik:** Galaksiler uzayin ICINDE bize dogru ya da bizden
   uzaga kosmuyor; ARADAKI UZAY genisliyor. Isik yolda ilerlerken
   dalga boyu uzuyor: 1 + z = a(bugün)/a(yayıldığı an). Bu, en sik
   yapilan kavram hatasidir.
3. **Kutle cekimsel:** Isik guclu bir kutle cekim alanindan cikarken
   enerji kaybeder (Pound-Rebka deneyi).

**Hubble yasasi:** v = H₀d. H₀ ≈ 70 km/s/Mpc. Bu, evrenin bir merkezi
oldugunu GOSTERMEZ; her gozlemci ayni seyi gorur, tipki sisen bir
balonun uzerindeki her nokta gibi.

**Hubble zamani:** 1/H₀ ≈ 14 milyar yil — evrenin yasinin kaba
mertebesi.

**Hizlanan genisleme:** Ia tipi supernovalar standart mum olarak
kullanildiginda, uzak galaksilerin beklenenden SONUK oldugu bulundu
(1998, 2011 Nobel). Yani genisleme yavaslamiyor, HIZLANIYOR. Sebebi
"karanlik enerji" olarak adlandiriliyor; ne oldugu bilinmiyor ve
evrenin enerji butcesinin ~%68'ini olusturuyor.

**Kozmik mikrodalga arka plan:** z ≈ 1100'den gelir; evren o an
saydamlasmisti. Sicakligi 2,725 K'dir ve genisleme yuzunden sogumustur.
""", """
Redshift comes from three distinct causes — Doppler motion, the expansion
of space itself (1+z = a_now/a_then), and gravity. Hubble's law v = H0 d
implies no centre: every observer sees the same recession. Type Ia
supernovae showed in 1998 that the expansion is accelerating.
""",
  eqs=["z = (λ_göz − λ_kaynak)/λ_kaynak", "1 + z = a₀/a_yayılma",
       "v = H₀·d", "H₀ ≈ 70 km/s/Mpc", "1/H₀ ≈ 14 milyar yıl"],
  ex_tr=["Bir galakside hidrojenin 656,3 nm'lik H-alfa cizgisi 689,1 nm'de "
         "gorulsun. z = (689,1−656,3)/656,3 = 0,050. Dusuk z icin "
         "v ≈ cz = 0,050 × 3×10⁵ = 1,5×10⁴ km/s. Hubble yasasindan "
         "d = v/H₀ = 15000/70 = 214 Mpc ≈ 700 milyon isik yili. Isik "
         "yola ciktiginda Dunya'da henuz karmasik canlilar yoktu."],
  ex_en=["An H-alpha line at 689.1 nm gives z = 0.050, hence about 214 Mpc "
         "or 700 million light years."],
  kw="kirmizi kayma|kirmiziya kayma|redshift|hubble yasasi|"
     "evrenin genislemesi|kozmolojik kayma|karanlik enerji|"
     "hizlanan genisleme|hubble sabiti|expansion of the universe",
  related="hubble|cmb_gozlem"),

T("olcum_aletleri", "Laboratuvar Ölçüm Teknikleri",
  "Laboratory Measurement Techniques", """
Fizik deneyinin kalitesi cogu zaman olcum duzeneginin kalitesidir.

**Osiloskop:** Gerilimi ZAMANIN fonksiyonu olarak gosterir.
- **Tetikleme (trigger):** Ekranin durmasini saglayan sey budur. Dalga
  akiyorsa tetikleme seviyesi yanlistir.
- **Bant genisligi:** Aletin gecirebildigi en yuksek frekans. Kare
  dalganin keskin kenarlari yuksek harmonikler icerir; dusuk bant
  genisligi kenarlari yuvarlatir. Kabaca: yukselme suresi ≈ 0,35/BW.
- **Prob:** ×10 prob sinyali onda bire dusurur ama devreyi daha az
  yukler (10 MΩ). Olcum aleti devreyi DEGISTIRMEMELIDIR — olcmenin
  birinci kurali.
- **Kuplaj:** DC tum sinyali, AC yalnizca degisen kismi gosterir.

**Multimetre:** Gerilim olcerken PARALEL, akim olcerken SERI baglanir.
Ic direnci yuksek (voltmetre) ya da dusuk (ampermetre) olmalidir.
Ampermetreyi paralel baglamak kisa devredir — laboratuvarda en sik
yapilan hata.

**Kilitlemeli yukselteC (lock-in):** Gurultunun icinde kaybolmus bir
sinyali cikarir. Sinyali bilinen bir frekansta module edip yalnizca o
frekansi dinler; gurultunun geri kalani ortalamada kaybolur. Bu yontemle
gurultunun binde biri buyuklugundeki sinyaller olculebilir.

**Ortak ilkeler:** Topraklama dongusunden kacinin, kablo ekranlamasi
kullanin, olcum aletinin giris empedansini devreye gore secin, ve her
zaman bilinen bir referansla kalibre edin.
""", """
Measurement quality often decides experiment quality. An oscilloscope
needs correct triggering, adequate bandwidth (rise time about 0.35/BW) and
an appropriate probe: the instrument must not disturb the circuit.
Voltmeters go in parallel with high input impedance, ammeters in series
with low. Lock-in amplifiers recover signals far below the noise floor by
detecting only at a known modulation frequency.
""",
  eqs=["yükselme süresi ≈ 0,35/BW", "V_ölçülen = V·R_in/(R_in + R_kaynak)"],
  ex_tr=["100 MHz bant genisligindeki bir osiloskopla olculebilecek en "
         "kisa yukselme suresi 0,35/10⁸ = 3,5 ns. Gercek sinyalin "
         "yukselme suresi 2 ns ise olculen deger "
         "√(2² + 3,5²) = 4,0 ns cikar — yani asil olcumu ALETINIZ "
         "belirler. Kural: aletin bant genisligi, sinyal bant "
         "genisliginin en az bes kati olmalidir."],
  ex_en=["A 100 MHz scope cannot show a rise time below 3.5 ns; measuring "
         "a 2 ns edge yields 4.0 ns — the instrument dominates."],
  kw="osiloskop|osiloskop kullanimi|tetikleme|bant genisligi|prob|"
     "multimetre|voltmetre ampermetre|lock-in|kilitlemeli yukseltec|"
     "olcum teknikleri|oscilloscope|measurement technique",
  related="olcum_belirsizlik|elektronik"),

T("egri_uydurma", "En Küçük Kareler ve Eğri Uydurma",
  "Least Squares and Curve Fitting", """
Deney verisi hicbir zaman tam bir dogru uzerine dusmez. Soru sudur:
verilerin "en iyi" tanimi hangisidir ve ne kadar guvenilirdir?

**En kucuk kareler ilkesi:** Artiklarin karelerinin toplamini en kucuk
yapan parametreler secilir:
    χ² = Σ [(y_i − f(x_i))/σ_i]²
Neden kare? Cunku olcum hatalari Gauss dagilimliysa, χ²'yi en kucuk
yapmak EN COK OLABILIRLIK cozumudur. Yani bu keyfi bir tercih degil,
istatistigin sonucudur.

**Agirliklandirma:** σ_i ile bolme, hassas olculen noktalara daha cok
soz hakki verir. Esit hata varsayimi yapiliyorsa sade en kucuk kareler
elde edilir.

**Dogru uydurma:** y = ax + b icin egim ve kesisim kapali formulle
bulunur; egimin belirsizligi de verilerin sacilmasindan hesaplanir.
Sonucu "a = 2,03" diye degil, "a = 2,03 ± 0,04" diye yazmak zorunludur.

**Uyum iyiligi:** Indirgenmis ki-kare χ²/ν ≈ 1 olmalidir (ν = serbestlik
derecesi).
- χ²/ν >> 1: model yetersiz ya da hatalar kucuk tahmin edilmis.
- χ²/ν << 1: hatalar buyuk tahmin edilmis (ya da veriye asiri uyum).

**Dogrusallastirma tuzagi:** y = Ae^(bx) iliskisini log alarak dogruya
cevirmek pratiktir, ama HATALARI carpitir: log donusumu buyuk degerlerin
hatasini kucultur. Dogrusu, dogrusal olmayan uydurmayi dogrudan yapmaktir.

**Korelasyon nedensellik degildir:** R² yuksek olabilir; bu, modelin
DOGRU oldugunu degil, veriyi iyi tanimladigini gosterir.
""", """
Least squares minimises the sum of squared residuals, which is the maximum
likelihood solution when errors are Gaussian. Weighting by 1/sigma gives
precise points more influence. Always quote a fitted parameter with its
uncertainty, and check the reduced chi-square: far above 1 means a poor
model or underestimated errors. Linearising an exponential distorts the
error weighting.
""",
  eqs=["χ² = Σ[(yᵢ − f(xᵢ))/σᵢ]²", "a = [nΣxy − ΣxΣy]/[nΣx² − (Σx)²]",
       "χ²/ν ≈ 1"],
  ex_tr=["Bes noktali bir dogru uydurmasinda χ² = 12,4 cikti ve iki "
         "parametre uyduruldu. Serbestlik derecesi ν = 5 − 2 = 3, yani "
         "χ²/ν = 4,1. Bu deger 1'den cok buyuk: ya olcum hatalari "
         "oldugundan kucuk yazildi ya da veri dogrusal degil. Sonucu "
         "'uyum iyi' diye raporlamak yanlis olur — once artiklarin "
         "grafigine bakip sistematik bir egilim olup olmadigi "
         "gorulmelidir."],
  ex_en=["A reduced chi-square of 4.1 signals underestimated errors or a "
         "wrong model; inspect the residual plot before reporting."],
  kw="en kucuk kareler|egri uydurma|dogru uydurma|ki kare|"
     "indirgenmis ki kare|artiklar|uyum iyiligi|regresyon|korelasyon|"
     "least squares|curve fitting|chi square|goodness of fit",
  related="olcum_belirsizlik|hata_yayilimi"),
]

# ── Secmeli ders cekirdegi ──────────────────────────────────────────────────
# Olculdu: "plazma fizigi" -> "Fizigin Matematiksel Yontemleri",
# "kaos ve dogrusal olmayan dinamik" -> "Dogrusal olmayan optik".

MUFREDAT_KONULARI += [

T("plazma", "Plazma Fiziği", "Plasma Physics", """
Plazma, maddenin dorduncu halidir: yeterince isitilan gaz iyonlasir ve
serbest yuklerden olusan, TOPLU davranan bir ortama donusur. Evrendeki
gorunur maddenin %99'undan fazlasi plazmadir.

**Ne zaman plazma sayilir:** Uc kosul birden gerekir —
1. **Debye perdelemesi:** Bir yukun etkisi λ_D = √(ε₀kT/ne²) mesafesinde
   perdelenir. Sistem bu uzunluktan cok daha buyuk olmalidir.
2. **Debye kuresinde cok parcacik:** N_D >> 1, yoksa istatistik anlamsiz.
3. **Carpisma frekansi < plazma frekansi:** Toplu davranis baskin olmali.

**Plazma frekansi:** ω_p = √(ne²/ε₀m). Elektronlar denge konumundan
sapinca bu frekansta salinir. Sonuc: ω < ω_p olan dalgalar YANSIR,
buyuk olanlar GECER. Kisa dalga radyonun iyonkureden yansiyip kitalar
arasi gitmesi ve uydu haberlesmesinin GHz'de yapilmasi ayni fizigin
iki yuzudur.

**Manyetik alanda:** Yukler alan cizgileri etrafinda siklotron
frekansiyla (ω_c = qB/m) doner ve cizgi boyunca serbestce akar. Plazma
boylece "manyetik olarak hapsedilebilir" — tokamak fikri budur.

**Fuzyon icin Lawson olcutu:** Enerji kazanci icin n·τ·T carpimi belirli
bir esigi asmalidir. Zorluk, sicaklik (10⁸ K), yogunluk ve hapsedilme
suresini AYNI ANDA saglamaktir.

**Nerede karsimiza cikar:** Yildizlar, gunes ruzgari, iyonkure, floresan
lamba, neon tabela, plazma ekran, yari iletken uretiminde asindirma,
kaynak arki, simsek.
""", """
Plasma is ionised gas with collective behaviour, making up over 99% of
visible matter. Debye screening, many particles per Debye sphere and
collective dominance define it. Waves below the plasma frequency reflect —
why shortwave radio bounces off the ionosphere. Magnetic confinement
exploits gyration about field lines, and fusion requires the Lawson triple
product.
""",
  eqs=["λ_D = √(ε₀kT/ne²)", "ω_p = √(ne²/ε₀m)", "ω_c = qB/m",
       "n·τ·T > eşik (Lawson)"],
  ex_tr=["Iyonkurenin F katmaninda elektron yogunlugu n ≈ 10¹² m⁻³. "
         "Plazma frekansi f_p = (1/2π)√(ne²/ε₀m) = 8,98√n Hz = "
         "8,98×10⁶ = 9,0 MHz. Bu yuzden kisa dalga (3-30 MHz) yayinlar "
         "gece iyonkureden yansiyip binlerce kilometre gider, FM radyo "
         "(100 MHz) ise gecip uzaya kacar. Amator telsizcilerin gece "
         "daha uzak mesafelere ulasmasinin sebebi budur."],
  ex_en=["The ionospheric F layer has f_p ≈ 9 MHz, so shortwave reflects "
         "while FM at 100 MHz escapes."],
  kw="plazma|plazma fizigi|debye uzunlugu|plazma frekansi|"
     "iyonkure|tokamak|manyetik hapsetme|lawson olcutu|siklotron frekansi|"
     "maddenin dorduncu hali|plasma physics|debye length|plasma frequency",
  related="fuzyon|elektromanyetik_dalga"),

T("kaos", "Kaos ve Doğrusal Olmayan Dinamik",
  "Chaos and Nonlinear Dynamics", """
Kaos, rastgelelik DEGILDIR. Denklemler tamamen belirlidir; ama baslangic
kosullarina duyarlilik, uzun vadeli ongoruyu imkansiz kilar.

**Baslangic kosullarina duyarlilik:** Iki yakin baslangic, uzsel olarak
ayrilir: δ(t) ≈ δ₀·e^(λt). λ (Lyapunov ussu) pozitifse sistem kaotiktir.
Ongoru ufku, olcum hassasiyetiyle LOGARITMIK buyur — hassasiyeti bin kat
artirmak ongoru suresini yalnizca ln(1000)/λ kadar uzatir. Hava
tahmininin neden iki haftada tikandiginin cevabi budur.

**Kelebek etkisi:** Lorenz'in 1963'te hava modelini incelerken buldugu
sey; uc denklemli basit bir sistem bile kaotik olabilir. Kaos icin
DOGRUSAL OLMAMA ve en az uc boyut gerekir (surekli sistemlerde).

**Faz uzayi ve cekiciler:** Sonumlu sistemler bir noktaya (sabit nokta)
ya da bir dongude (limit dongusu) yerlesir. Kaotik sistemler ise TUHAF
CEKICI uzerinde dolasir: sinirli bir bolgede kalir ama asla ayni yoldan
gecmez ve kesirli boyutlu (fraktal) bir yapi olusturur.

**Periyot ikilenmesi ve evrensellik:** Lojistik harita x_{n+1} = r·x_n(1−x_n)
r arttikca 2, 4, 8, 16... periyotlu davranisa gecer ve r ≈ 3,5699'da
kaosa girer. Ardisik catallanma araliklarinin orani δ = 4,6692...
(Feigenbaum sabiti) — bu sayi, haritanin ayrintisindan BAGIMSIZDIR.
Farkli sistemlerde ayni sayi cikar; faz gecislerindeki evrensellikle
ayni turden bir olgudur.

**Fizikte nerede:** Ucus cisim problemi, cift sarkac, turbulans, kalp
ritmi, Ay'in uzun vadeli yorungesi, asteroit kusagindaki Kirkwood
bosluklari.
""", """
Chaos is deterministic but unpredictable: nearby trajectories separate
exponentially with a positive Lyapunov exponent, so the prediction horizon
grows only logarithmically with measurement precision. Lorenz showed three
equations suffice. Chaotic motion lives on strange attractors of fractal
dimension, and the period-doubling route has the universal Feigenbaum
constant 4.6692.
""",
  eqs=["δ(t) ≈ δ₀·e^(λt)", "x_{n+1} = r·x_n(1 − x_n)",
       "δ_Feigenbaum = 4,6692…", "λ > 0 → kaos"],
  ex_tr=["Hava tahmininde Lyapunov ussu kabaca λ ≈ 1/gun. Baslangic "
         "hatasini 1000 kat kucultursek kazanc ln(1000)/λ = 6,9 gundur. "
         "Yani olcum agini bin kat iyilestirmek tahmini iki haftadan "
         "uc haftaya cikarir, bir aya degil. Bu, teknolojik degil "
         "MATEMATIKSEL bir sinirdir."],
  ex_en=["With a Lyapunov exponent of about 1/day, a thousand-fold better "
         "initial data buys only about seven extra days of forecast."],
  kw="kaos|kaos kurami|dogrusal olmayan dinamik|lyapunov ussu|"
     "kelebek etkisi|tuhaf cekici|periyot ikilenmesi|lojistik harita|"
     "feigenbaum sabiti|fraktal|chaos theory|strange attractor|"
     "butterfly effect|nonlinear dynamics",
  related="faz_gecisi|sayisal_yontemler_fizik"),
]

MUFREDAT_KONULARI += [

T("kara_cisim", "Kara Cisim Işıması ve Kuantumun Doğuşu",
  "Blackbody Radiation and the Birth of the Quantum", """
Kuantum fizigi, sicak bir cismin hangi renkte parladigi sorusundan
dogdu. Cevap klasik fizikle verilemedi.

**Kara cisim:** Uzerine dusen her dalga boyunu tamamen sogurup termal
dengede yeniden yayan ideal cisim. Yaydigi tayf yalnizca SICAKLIGA
baglidir; malzemeye degil. Icinde kucuk bir delik olan bosluk pratik
karsiligidir.

**Klasik cikmaz — morotesi felaketi:** Rayleigh-Jeans yasasi
    u(λ) ∝ kT/λ⁴
kisa dalga boyunda sonsuza gider. Yani klasik fizige gore sicak bir
firina bakan herkes olumcul morotesi almaliydi. Deney bunu kesinlikle
desteklemiyordu.

**Planck'in cozumu (1900):** Enerji, sureklice degil h·f'lik PAKETLER
halinde alinip verilir. Sonuc:
    u(λ,T) = (8πhc/λ⁵)·1/(e^(hc/λkT) − 1)
Kisa dalga boyunda ustel terim modlarin uyarilmasini bastirir, egri
tepe yapip duser — olculen bicim tam budur.

**Iki sonucu ayrica turetilir:**
- **Wien yer degistirme:** λ_max·T = 2,898×10⁻³ m·K. Sicaklik artinca
  tepe kisa dalga boyuna kayar; demir once kirmizi, sonra beyaz parlar.
- **Stefan-Boltzmann:** P = σAT⁴. Toplam guc sicakligin DORDUNCU
  kuvvetiyle artar.

**Nerede kullanilir:** Yildiz sicakligi olcumu, termal kamera, kizil
otesi kulaklik termometresi, kozmik mikrodalga arka planin 2,725 K'lik
tayfi (evrendeki en mukemmel kara cisim tayfi olculmustur).
""", """
Quantum physics began with the colour of hot bodies. The classical
Rayleigh-Jeans law diverges at short wavelength — the ultraviolet
catastrophe. Planck's 1900 quantisation of energy in units of hf gives the
observed spectrum, from which Wien's displacement law and the
Stefan-Boltzmann law follow. The cosmic microwave background is the most
perfect blackbody spectrum ever measured.
""",
  eqs=["u(λ,T) = (8πhc/λ⁵)/(e^(hc/λkT) − 1)", "λ_max·T = 2,898×10⁻³ m·K",
       "P = σ·A·T⁴", "σ = 5,67×10⁻⁸ W/(m²K⁴)"],
  ex_tr=["Gunes yuzeyi 5778 K. Wien: λ_max = 2,898×10⁻³/5778 = 502 nm — "
         "yesil-sari bolge, yani gozumuzun en duyarli oldugu yer. "
         "Evrim bunu tesadufen secmedi. Stefan-Boltzmann ile birim "
         "alandan yayilan guc: σT⁴ = 5,67×10⁻⁸ × 5778⁴ = 6,3×10⁷ W/m². "
         "Sicaklik iki katina ciksaydi guc ON ALTI kat artardi."],
  ex_en=["The Sun at 5778 K peaks at 502 nm, where the human eye is most "
         "sensitive, and radiates 6.3e7 W/m2."],
  kw="kara cisim|kara cisim isinimi|kara cisim tayfi|morotesi felaketi|"
     "planck isima yasasi|rayleigh jeans|wien yer degistirme|"
     "stefan boltzmann yasasi|black-body radiation|blackbody radiation|"
     "black body|planck law|ultraviolet catastrophe|wien displacement",
  related="planck_kim|kuantum_temelleri|yildiz_evrimi"),
]
