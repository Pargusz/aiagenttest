"""Cekirdek fizik bilgi tabani (TR + EN).

Bu, botun "dogustan" bilgisidir. Ogrenme surecinde internetten cekilen
Wikipedia tanimlari ve makale ozetleri bunun uzerine eklenir.
"""
import re


def T(key, tr_title, en_title, tr, en, eqs=None, ex_tr=None, ex_en=None,
      kw="", related=""):
    return {
        "key": key, "tr_title": tr_title, "en_title": en_title,
        "tr": tr.strip(), "en": en.strip(),
        "eqs": eqs or [], "ex_tr": ex_tr or [], "ex_en": ex_en or [],
        "kw": [k.strip() for k in kw.split("|") if k.strip()],
        "related": [r.strip() for r in related.split("|") if r.strip()],
    }


TOPICS = [

T("newton_yasalari", "Newton'un Hareket Yasalari", "Newton's Laws of Motion", """
Klasik mekanigin temelini olusturan uc yasadir.

**1. Yasa (Eylemsizlik):** Uzerine net kuvvet etki etmeyen bir cisim, duruyorsa durmaya,
hareket ediyorsa sabit hizla dogrusal hareketine devam eder. Bu yasa ayni zamanda
"eylemsiz referans sistemi" kavramini tanimlar.

**2. Yasa:** Bir cisme etki eden net kuvvet, cismin momentumunun zamana gore
degisimine esittir: F = dp/dt. Kutle sabitse bu F = ma halini alir. Bu yasa vektorel
bir esitliktir; her eksen icin ayri ayri yazilir.

**3. Yasa (Etki-Tepki):** A cismi B'ye bir kuvvet uygularsa, B de A'ya esit buyuklukte
ve zit yonde bir kuvvet uygular. Bu iki kuvvet **farkli cisimlere** etki eder; bu
yuzden birbirini goturmezler.

**Onemli nokta:** 2. yasa yalnizca eylemsiz (ivmesiz) referans sistemlerinde
gecerlidir. Donen bir sistemde calisiyorsaniz merkezkac ve Coriolis gibi
"sozde kuvvetler" eklemeniz gerekir.
""", """
The three laws forming the foundation of classical mechanics.

**First law (inertia):** A body with no net force acting on it remains at rest or
continues in uniform straight-line motion. This law also defines what an inertial
reference frame is.

**Second law:** The net force on a body equals the rate of change of its momentum,
F = dp/dt. For constant mass this reduces to F = ma. It is a vector equation, so
you write one component equation per axis.

**Third law (action-reaction):** If A exerts a force on B, then B exerts an equal
and opposite force on A. These two forces act on **different bodies**, which is why
they never cancel each other.

**Key caveat:** the second law holds only in inertial frames. In a rotating frame you
must add fictitious forces such as centrifugal and Coriolis terms.
""",
  ["F = dp/dt", "F = m·a", "F_AB = -F_BA"],
  ["2 kg'lik bir kutuya yatay 10 N kuvvet uygulaniyor, surtunme yok. Ivme: a = F/m = 10/2 = 5 m/s². "
   "Eger 0.3 surtunme katsayili bir zeminde olsaydi: f = μmg = 0.3·2·9.81 = 5.89 N, "
   "net kuvvet 10 - 5.89 = 4.11 N, a = 2.06 m/s².",
   "Asansorde tartilan 70 kg'lik bir kisi: asansor yukari 2 m/s² ivmelenirken tartinin gosterdigi "
   "normal kuvvet N = m(g+a) = 70·(9.81+2) = 827 N, yani ~84 kg gorunur."],
  ["A 2 kg box is pushed with 10 N horizontally, frictionless: a = F/m = 5 m/s². With friction "
   "coefficient 0.3: f = μmg = 5.89 N, net force 4.11 N, so a = 2.06 m/s².",
   "A 70 kg person in an elevator accelerating upward at 2 m/s² feels N = m(g+a) = 827 N, "
   "reading about 84 kg on the scale."],
  kw="newton|hareket yasalari|eylemsizlik|etki tepki|f=ma|laws of motion|inertia|action reaction",
  related="momentum_korunumu|surtunme|dinamik"),

T("enerji_korunumu", "Enerjinin Korunumu", "Conservation of Energy", """
Yalitilmis bir sistemde toplam enerji sabittir; enerji yaratilamaz veya yok edilemez,
yalnizca bir turden digerine donusur.

**Mekanik enerji:** E = Ek + Ep. Yalnizca korunumlu kuvvetler (yercekimi, yay) is
yapiyorsa mekanik enerji korunur. Surtunme gibi korunumsuz kuvvetler varsa, kaybolan
mekanik enerji isiya donusur: ΔE_mek = W_surtunme.

**Is-enerji teoremi:** Bir cisme yapilan net is, kinetik enerjisindeki degisime esittir:
W_net = ΔEk. Bu teorem, kuvvet konuma bagli degisse bile gecerlidir (integral alinir).

**Neden korunur?** Noether teoremine gore enerjinin korunumu, fizik yasalarinin
zamanda otelemeye gore simetrik olmasindan kaynaklanir. Ilginc olan sudur: genisleyen
evrende bu simetri kirildigi icin kozmolojik olcekte enerji korunumu asikar degildir.
""", """
In an isolated system the total energy is constant; energy is neither created nor
destroyed, only converted from one form to another.

**Mechanical energy:** E = KE + PE. It is conserved when only conservative forces
(gravity, springs) do work. When non-conservative forces such as friction act, the
lost mechanical energy becomes heat: ΔE_mech = W_friction.

**Work-energy theorem:** the net work done on a body equals its change in kinetic
energy, W_net = ΔKE. This holds even when the force varies with position (you
integrate).

**Why is it conserved?** By Noether's theorem, energy conservation follows from the
time-translation symmetry of physical law. Notably, in an expanding universe that
symmetry is broken, so energy conservation is not straightforward on cosmological
scales.
""",
  ["E = Ek + Ep", "Ek = ½mv²", "Ep = mgh", "W_net = ΔEk", "P = dW/dt"],
  ["10 m yukseklikten birakilan 2 kg'lik cisim yere carparken: mgh = ½mv² → "
   "v = √(2gh) = √(2·9.81·10) = 14.0 m/s. Kutle sadelesir, yani tuy de tas da (havasiz ortamda) "
   "ayni hizla carpar.",
   "Yay sabiti 200 N/m olan yay 0.1 m sikistirilip 0.5 kg'lik bloga birakilirsa: "
   "½kx² = ½mv² → v = x√(k/m) = 0.1·√(200/0.5) = 2 m/s."],
  ["A 2 kg object dropped from 10 m: mgh = ½mv² → v = √(2gh) = 14.0 m/s. Mass cancels, so "
   "a feather and a stone hit at the same speed in vacuum.",
   "A spring with k = 200 N/m compressed 0.1 m released against a 0.5 kg block: "
   "v = x√(k/m) = 2 m/s."],
  kw="enerji korunumu|is enerji|kinetik|potansiyel|energy conservation|work energy theorem",
  related="newton_yasalari|termodinamik_yasalari"),

T("momentum_korunumu", "Momentumun Korunumu ve Carpismalar", "Conservation of Momentum and Collisions", """
Dis net kuvvet sifirsa, sistemin toplam momentumu korunur: Σp_ilk = Σp_son.
Bu, Newton'un 3. yasasinin dogrudan sonucudur.

**Esnek carpisma:** Hem momentum hem kinetik enerji korunur. Bir boyutta iki cisim icin
son hizlar analitik olarak bulunabilir. Esit kutleli esnek carpismada cisimler hizlarini
takas eder — bilardo toplarinda gordugumuz sey budur.

**Esnek olmayan carpisma:** Momentum korunur, kinetik enerji korunmaz (isiya, sese,
deformasyona gider). **Tam esnek olmayan** carpismada cisimler birlikte hareket eder ve
kinetik enerji kaybi maksimumdur.

**Kutle merkezi:** Carpisma probleminde kutle merkezi cercevesine gecmek isi cok
kolaylastirir; bu cercevede toplam momentum daima sifirdir.
""", """
If the net external force is zero, total momentum is conserved: Σp_before = Σp_after.
This follows directly from Newton's third law.

**Elastic collision:** both momentum and kinetic energy are conserved. In 1D the final
velocities have a closed form. For equal masses the objects simply exchange velocities —
which is what you see with billiard balls.

**Inelastic collision:** momentum is conserved but kinetic energy is not (it goes into
heat, sound, deformation). In a **perfectly inelastic** collision the bodies move
together and the kinetic-energy loss is maximal.

**Centre of mass:** switching to the centre-of-mass frame simplifies collision problems
enormously, since total momentum is identically zero there.
""",
  ["Σmv = sabit", "v1' = ((m1-m2)v1 + 2m2v2)/(m1+m2)", "J = FΔt = Δp"],
  ["3 kg, 4 m/s hizla giden cisim duran 1 kg'lik cisme tam esnek olmayan carpisiyor: "
   "ortak hiz v = (3·4)/(3+1) = 3 m/s. Kinetik enerji kaybi: 24 - 18 = 6 J (isiya gider).",
   "Tufek geri tepmesi: 4 kg tufekten 0.01 kg mermi 600 m/s ile cikiyor. "
   "Momentum korunumu: v_tufek = -(0.01·600)/4 = -1.5 m/s."],
  ["A 3 kg body at 4 m/s hits a stationary 1 kg body perfectly inelastically: "
   "v = 12/4 = 3 m/s, with 6 J of kinetic energy lost to heat.",
   "Rifle recoil: a 0.01 kg bullet at 600 m/s from a 4 kg rifle gives v = -1.5 m/s."],
  kw="momentum|carpisma|esnek|impuls|collision|elastic|inelastic|recoil",
  related="newton_yasalari|enerji_korunumu"),

T("termodinamik_yasalari", "Termodinamigin Yasalari", "Laws of Thermodynamics", """
**0. Yasa:** A ile B, B ile C termal dengedeyse A ile C de dengededir. Bu, sicakligin
olculebilir bir buyukluk olmasini mumkun kilar.

**1. Yasa:** ΔU = Q - W. Enerjinin korunumunun isi sureclerine uygulanmis halidir.
Isaret konvansiyonu onemlidir: Q sisteme verilen isi, W sistemin yaptigi istir.

**2. Yasa:** Yalitilmis bir sistemin entropisi asla azalmaz: ΔS ≥ 0. Bunun pratik
sonucu, isinin kendiliginden soguktan sicaga akamamasi ve hicbir isi makinesinin
Carnot veriminden (η = 1 - Tc/Th) daha verimli olamamasidir. 2. yasa, zamanin bir
yonu olmasinin ("zaman oku") temel fiziksel nedenidir.

**3. Yasa:** Mutlak sifira (0 K) yaklasirken kusursuz bir kristalin entropisi sifira
gider. Sonuc: mutlak sifira sonlu sayida adimda ulasilamaz.
""", """
**Zeroth law:** if A and B are in thermal equilibrium and B and C are too, then A and C
are as well. This is what makes temperature a measurable quantity.

**First law:** ΔU = Q - W. It is energy conservation applied to thermal processes. Sign
convention matters: Q is heat added to the system, W is work done by the system.

**Second law:** the entropy of an isolated system never decreases, ΔS ≥ 0. Practically,
heat cannot spontaneously flow from cold to hot, and no heat engine can beat the Carnot
efficiency η = 1 - Tc/Th. The second law is the fundamental reason time has a direction
(the "arrow of time").

**Third law:** as temperature approaches absolute zero the entropy of a perfect crystal
approaches zero, implying absolute zero cannot be reached in finitely many steps.
""",
  ["ΔU = Q - W", "ΔS ≥ 0", "η_Carnot = 1 - Tc/Th", "S = k_B ln W"],
  ["500 K ve 300 K arasinda calisan bir isi makinesinin maksimum verimi: "
   "η = 1 - 300/500 = 0.40, yani %40. 1000 J isi alirsa en fazla 400 J is yapabilir.",
   "Bir buz kalibi (273 K) erirken 334 kJ/kg gizli isi alir. 1 kg buz icin entropi artisi: "
   "ΔS = Q/T = 334000/273 = 1223 J/K."],
  ["A heat engine between 500 K and 300 K has maximum efficiency η = 1 - 300/500 = 40%. "
   "Given 1000 J of heat it can do at most 400 J of work.",
   "Melting 1 kg of ice at 273 K absorbs 334 kJ, so entropy increases by "
   "ΔS = Q/T = 1223 J/K."],
  kw="termodinamik|entropi|carnot|isi makinesi|thermodynamics|entropy|heat engine|second law",
  related="enerji_korunumu|istatistiksel_mekanik|ideal_gaz_kinetik"),

T("ideal_gaz_kinetik", "Ideal Gaz ve Kinetik Teori", "Ideal Gas and Kinetic Theory", """
Ideal gaz modeli, molekulleri boyutsuz ve aralarinda (carpisma disinda) etkilesim
olmayan parcaciklar olarak ele alir: PV = nRT.

**Kinetik teori kopruusu:** Basinc, molekullerin duvara carpmasindan dogar. Turetim
sonucunda PV = (1/3)Nm⟨v²⟩ bulunur. Bunu ideal gaz yasasiyla karsilastirinca ortaya
cok onemli bir sonuc cikar: (1/2)m⟨v²⟩ = (3/2)k_B T. Yani **sicaklik, molekullerin
ortalama kinetik enerjisinin bir olcusudur**.

**Esbolusum teoremi:** Her serbestlik derecesine ortalama (1/2)k_B T enerji duser.
Tek atomlu gaz icin 3 oteleme serbestligi vardir → U = (3/2)nRT, Cv = (3/2)R.
Iki atomlu gazda 2 donme serbestligi daha eklenir → Cv = (5/2)R.

**Maxwell-Boltzmann dagilimi:** Hizlar tek bir degerde degil, bir dagilima gore
saginilir. En olasi hiz, ortalama hiz ve rms hiz birbirinden farklidir:
v_p < v_ort < v_rms.

**Ne zaman bozulur?** Yuksek basinc ve dusuk sicaklikta molekul hacmi ve cekim
kuvvetleri onem kazanir; van der Waals denklemi bunlari duzeltir.
""", """
The ideal gas model treats molecules as point particles with no interaction except
collisions: PV = nRT.

**The kinetic-theory bridge:** pressure arises from molecules striking the walls.
The derivation gives PV = (1/3)Nm⟨v²⟩. Comparing with the ideal gas law yields a
profound result: (1/2)m⟨v²⟩ = (3/2)k_B T. That is, **temperature is a measure of the
average kinetic energy of the molecules**.

**Equipartition theorem:** each degree of freedom carries (1/2)k_B T on average. A
monatomic gas has 3 translational degrees → U = (3/2)nRT and Cv = (3/2)R. A diatomic
gas adds 2 rotational degrees → Cv = (5/2)R.

**Maxwell-Boltzmann distribution:** speeds are spread over a distribution rather than
sharing a single value, and the most probable, mean and rms speeds all differ:
v_p < v_mean < v_rms.

**Where it fails:** at high pressure and low temperature molecular volume and
attraction matter; the van der Waals equation corrects for both.
""",
  ["PV = nRT", "PV = (1/3)Nm⟨v²⟩", "½m⟨v²⟩ = (3/2)k_B T",
   "v_rms = √(3k_BT/m)", "(P + a n²/V²)(V - nb) = nRT"],
  ["Oda sicakliginda (300 K) azot molekulunun (28 u) rms hizi: "
   "v = √(3·1.38e-23·300/(28·1.66e-27)) = 517 m/s. Ses hizindan (346 m/s) buyuk olmasi "
   "tesaduf degil — ses molekullerin hareketiyle tasinir.",
   "1 mol ideal gaz 0 °C ve 1 atm'de: V = nRT/P = 1·8.314·273.15/101325 = 0.0224 m³ = 22.4 L."],
  ["At 300 K a nitrogen molecule (28 u) has v_rms = 517 m/s. That it exceeds the speed of "
   "sound (346 m/s) is no accident — sound is carried by molecular motion.",
   "One mole of ideal gas at 0 °C and 1 atm occupies V = nRT/P = 0.0224 m³ = 22.4 L."],
  kw="ideal gaz|kinetik teori|maxwell boltzmann|esbolusum|ideal gas|kinetic theory|equipartition|"
     # DIKKAT: buraya "ortalama kinetik enerji" gibi iki kelimesi birden
     # "kinetik enerji" olan bir anahtar KOYULMAMALI. Kismi eslesme
     # yuzunden her "kinetik enerji" sorusu bu konuya puan yaziyor ve
     # gorelilik/kuantum sorulari ideal gaza kayiyordu (olculdu: "ozel
     # gorelilikte enerji ifadesinden klasik kinetik enerjiyi turet"
     # sorusu 92 puanla ideal gaza gidiyordu).
     "sicaklik molekullerin kinetik enerjisi|"
     "sicaklik molekullerin hizi|esbolusum teoremi|rms hiz|"
     "molekullerin ortalama enerjisi",
  related="termodinamik_yasalari|istatistiksel_mekanik|enerji_korunumu"),

T("maxwell_denklemleri", "Maxwell Denklemleri", "Maxwell's Equations", """
Elektromanyetizmanin tamamini ozetleyen dort denklem:

1. **Gauss (elektrik):** ∇·E = ρ/ε₀ — elektrik alan yuklerden dogar, yukler alanin
   kaynagi ve ponoridir.
2. **Gauss (manyetik):** ∇·B = 0 — manyetik tek kutup (monopol) yoktur; manyetik alan
   cizgileri daima kapalidir.
3. **Faraday:** ∇×E = -∂B/∂t — degisen manyetik alan elektrik alan indukler. Eksi
   isaret Lenz yasasidir: indukleme degisime karsi koyar.
4. **Ampere-Maxwell:** ∇×B = μ₀J + μ₀ε₀ ∂E/∂t — akim ve degisen elektrik alan
   manyetik alan dogurur. Ikinci terim ("yer degistirme akimi") Maxwell'in ekledigi
   parcadir ve elektromanyetik dalgalarin varliginin anahtaridir.

**En buyuk sonuc:** Bos uzayda bu denklemler dalga denklemine indirgenir ve dalga hizi
c = 1/√(μ₀ε₀) ≈ 3×10⁸ m/s cikar. Bu deger olculen isik hizina esit oldugu icin Maxwell
"isik bir elektromanyetik dalgadir" sonucuna varmistir. Ayrica bu denklemler Galileo
donusumu altinda degismez degildir — bu celiski Einstein'i ozel gorelilige goturmustur.
""", """
Four equations that summarise all of electromagnetism:

1. **Gauss (electric):** ∇·E = ρ/ε₀ — electric fields originate from charges, which act
   as sources and sinks.
2. **Gauss (magnetic):** ∇·B = 0 — there are no magnetic monopoles; magnetic field
   lines always close on themselves.
3. **Faraday:** ∇×E = -∂B/∂t — a changing magnetic field induces an electric field. The
   minus sign is Lenz's law: induction opposes the change.
4. **Ampere-Maxwell:** ∇×B = μ₀J + μ₀ε₀ ∂E/∂t — currents and changing electric fields
   both produce magnetic fields. The second term (the "displacement current") is
   Maxwell's own addition and is the key to electromagnetic waves.

**The big payoff:** in free space these reduce to a wave equation with speed
c = 1/√(μ₀ε₀) ≈ 3×10⁸ m/s. Since this matched the measured speed of light, Maxwell
concluded light *is* an electromagnetic wave. These equations are also not invariant
under Galilean transformations — a contradiction that led Einstein to special relativity.
""",
  ["∇·E = ρ/ε₀", "∇·B = 0", "∇×E = -∂B/∂t", "∇×B = μ₀J + μ₀ε₀∂E/∂t",
   "c = 1/√(μ₀ε₀)"],
  ["c'yi sabitlerden hesaplayalim: 1/√(4π×10⁻⁷ · 8.854×10⁻¹²) = 2.998×10⁸ m/s. "
   "Sadece elektrik ve manyetizma deneylerinden olculen iki sabitten isik hizinin cikmasi "
   "fizik tarihinin en carpici sonuclarindan biridir.",
   "Bir kondansator sarj olurken plakalar arasinda akim yoktur ama degisen E alani vardir; "
   "yer degistirme akimi sayesinde Ampere yasasi burada da tutarli calisir."],
  ["Compute c from the constants: 1/√(4π×10⁻⁷ · 8.854×10⁻¹²) = 2.998×10⁸ m/s. Getting the "
   "speed of light out of two constants measured in purely electric and magnetic experiments "
   "is one of the most striking results in physics.",
   "While a capacitor charges there is no current between the plates but there is a changing "
   "E field; the displacement current keeps Ampere's law consistent there."],
  kw="maxwell|elektromanyetizma|gauss|faraday|ampere|electromagnetism|displacement current",
  related="elektromanyetik_dalga|ozel_gorelilik"),

T("elektromanyetik_dalga", "Elektromanyetik Dalgalar ve Spektrum", "Electromagnetic Waves and Spectrum", """
Elektromanyetik dalga, birbirini surekli olarak dogurun dik E ve B alanlarindan olusur;
her ikisi de yayilma yonune diktir (enine dalga).

**Ozellikleri:** E = cB, ortamda hiz v = c/n. Enerji akisi Poynting vektoru ile verilir:
S = (1/μ₀)E×B; ortalama siddet I = ½ε₀cE₀². Foton basinci P = I/c (soguran yuzey) veya
2I/c (yansitan yuzey) — gunes yelkeni bu ilkeyle calisir.

**Spektrum (artan frekans):** radyo → mikrodalga → kizilotesi → gorunur (400-700 nm) →
morotesi → X-isini → gama.

**Onemli ayrim:** Enine dalga olduklari icin **polarize** edilebilirler; ses gibi boyuna
dalgalar polarize edilemez. Ayrica bosluktan gecebilirler — ortam gerektirmezler, ki
19. yuzyilda "eter" arayisinin bosa cikmasinin nedeni budur.
""", """
An electromagnetic wave consists of mutually generating, perpendicular E and B fields,
both transverse to the propagation direction.

**Properties:** E = cB, and in a medium v = c/n. Energy flow is given by the Poynting
vector S = (1/μ₀)E×B, with mean intensity I = ½ε₀cE₀². Radiation pressure is P = I/c on
an absorbing surface, 2I/c on a reflecting one — the principle behind solar sails.

**Spectrum (increasing frequency):** radio → microwave → infrared → visible (400-700 nm)
→ ultraviolet → X-ray → gamma.

**Key distinction:** being transverse, they can be **polarised**; longitudinal waves such
as sound cannot. They also propagate through vacuum, needing no medium — which is why
the 19th-century search for the "aether" came up empty.
""",
  ["c = fλ", "E = cB", "I = ½ε₀cE₀²", "S = (1/μ₀)E×B", "n = c/v"],
  ["Yesil isik λ = 550 nm: f = c/λ = 3e8/550e-9 = 5.45×10¹⁴ Hz. Foton enerjisi "
   "E = hf = 3.6×10⁻¹⁹ J = 2.25 eV.",
   "Gunes sabiti Dunya'da ~1361 W/m². Bu isigi tamamen yansitan 1 m²'lik yelken uzerindeki "
   "kuvvet: F = 2I/c · A = 2·1361/3e8 = 9.1 µN. Kucuk ama surekli oldugu icin uzun yolculukta ise yarar."],
  ["Green light at λ = 550 nm: f = c/λ = 5.45×10¹⁴ Hz, photon energy E = hf = 2.25 eV.",
   "The solar constant at Earth is ~1361 W/m². On a perfectly reflecting 1 m² sail the force "
   "is F = 2I/c·A = 9.1 µN — tiny, but continuous, which is what makes it useful."],
  kw="elektromanyetik dalga|spektrum|isik|poynting|polarizasyon|em wave|spectrum|polarization",
  related="maxwell_denklemleri|optik_temelleri|foton"),

T("ozel_gorelilik", "Ozel Gorelilik", "Special Relativity", """
Iki postulat uzerine kuruludur:
1. Fizik yasalari tum eylemsiz cercevelerde aynidir.
2. Isik hizi c, kaynagin ve gozlemcinin hareketinden bagimsiz olarak her cercevede aynidir.

Ikinci postulat sezgiye aykiridir ama tum sonuclar bundan cikar.

**Sonuclar:** Zaman genlesmesi Δt = γΔt₀, boy kisalmasi L = L₀/γ, es zamanliligin
gorecelili, kutle-enerji esdegerligi E = γmc². Burada γ = 1/√(1-v²/c²).

**Yaygin yanlis anlama:** "Kutle hizla artar" ifadesi modern kullanimda terk edilmistir.
Kutle degismez (invaryant) bir buyukluktur; artan sey enerji ve momentumdur.

**Uzay-zaman:** Ayri ayri uzunluk ve sure gorecelidir, ama uzay-zaman araligi
s² = (ct)² - x² tum gozlemciler icin aynidir. Bu, gorelilikte gercekten "mutlak" olan seydir.

**Deneysel kanit:** Kozmik muonlarin yeryuzune ulasmasi (zaman genlesmesi olmasa
bozunurlardi), GPS uydularinin gunde ~7 µs'lik ozel gorelilik duzeltmesi, parcacik
hizlandiricilarindaki her olcum.
""", """
Built on two postulates:
1. The laws of physics are the same in all inertial frames.
2. The speed of light c is the same in every frame, independent of the motion of source
   or observer.

The second is counter-intuitive, but everything else follows from it.

**Consequences:** time dilation Δt = γΔt₀, length contraction L = L₀/γ, relativity of
simultaneity, and mass-energy equivalence E = γmc², where γ = 1/√(1-v²/c²).

**Common misconception:** "mass increases with speed" is abandoned in modern usage. Mass
is an invariant; what grows is energy and momentum.

**Spacetime:** lengths and durations are individually relative, but the spacetime interval
s² = (ct)² - x² is the same for all observers. That is what is genuinely absolute in
relativity.

**Experimental support:** cosmic-ray muons reaching the ground (they would decay without
time dilation), the ~7 µs/day special-relativistic correction in GPS satellites, and every
measurement in particle accelerators.
""",
  ["γ = 1/√(1-v²/c²)", "Δt = γΔt₀", "L = L₀/γ", "E = γmc²",
   "E² = (pc)² + (mc²)²", "u' = (u-v)/(1-uv/c²)"],
  ["0.8c hizla giden bir uzay gemisi: γ = 1/√(1-0.64) = 1.667. Gemide gecen 1 yil, "
   "Dunya'da 1.667 yil olarak olculur. Geminin 100 m'lik boyu Dunya'dan 60 m gorunur.",
   "Muonun oz yari omru 2.2 µs; 0.995c ile hareket ederken γ = 10, yani laboratuvarda "
   "22 µs yasar. Bu sayede 660 m yerine 6.6 km yol alabilir ve atmosferden yeryuzune ulasir."],
  ["A ship at 0.8c has γ = 1.667. One year aboard is measured as 1.667 years on Earth, and "
   "its 100 m length appears as 60 m from Earth.",
   "A muon's proper half-life is 2.2 µs; at 0.995c, γ = 10 so it lives 22 µs in the lab, "
   "travelling 6.6 km instead of 660 m — enough to reach the ground."],
  kw="lorentz donusumu|lorentz transformation|lorentz transformations|ozel gorelilik|zaman genlesmesi|boy kisalmasi|lorentz|einstein|special relativity|time dilation",
  related="genel_gorelilik|maxwell_denklemleri"),

T("genel_gorelilik", "Genel Gorelilik", "General Relativity", """
Einstein'in kutle cekimi kuramidir. Temel fikri **esdeglik ilkesi**dir: yerel olarak,
bir kutle cekim alaninda durmak ile ivmelenen bir cercevede olmak ayirt edilemez.

**Ana fikir:** Kutle cekimi bir kuvvet degil, kutle-enerjinin uzay-zamani egmesinin
sonucudur. Cisimler egri uzay-zamanda "en duz" yol olan jeodezikleri izler. John
Wheeler'in ozeti: madde uzay-zamana nasil egilecegini, uzay-zaman maddeye nasil
hareket edecegini soyler.

**Alan denklemleri:** G_μν + Λg_μν = (8πG/c⁴)T_μν. Sol taraf geometri, sag taraf
madde-enerji icerigi.

**Ongoruleri ve dogrulanmasi:** Merkur'un gunberi kaymasi (43"/yuzyil), isigin
kutle cekimiyle bukulmesi (1919 tutulmasi), kutle cekimsel kizila kayma (Pound-Rebka
deneyi), kara delikler (2019'da M87* goruntusu), kutle cekim dalgalari (2015'te LIGO).

**Gunluk hayatta:** GPS uydulari zayif alanda oldugu icin saatleri gunde ~45 µs hizli
isler; ozel gorelilikten gelen -7 µs ile birlikte net +38 µs duzeltme yapilmazsa
konum hatasi gunde ~10 km olur.
""", """
Einstein's theory of gravitation. Its foundation is the **equivalence principle**:
locally, standing in a gravitational field is indistinguishable from being in an
accelerating frame.

**Core idea:** gravity is not a force but the curvature of spacetime caused by
mass-energy. Bodies follow geodesics, the "straightest" paths in curved spacetime.
John Wheeler's summary: matter tells spacetime how to curve, spacetime tells matter
how to move.

**Field equations:** G_μν + Λg_μν = (8πG/c⁴)T_μν — geometry on the left, matter-energy
content on the right.

**Predictions and confirmations:** the perihelion precession of Mercury (43"/century),
gravitational light bending (the 1919 eclipse), gravitational redshift (Pound-Rebka),
black holes (the M87* image in 2019) and gravitational waves (LIGO, 2015).

**Everyday relevance:** GPS satellite clocks run ~45 µs/day fast because they sit in a
weaker field; combined with the -7 µs from special relativity, failing to apply the net
+38 µs correction would produce a position error of about 10 km per day.
""",
  ["G_μν + Λg_μν = (8πG/c⁴)T_μν", "r_s = 2GM/c²",
   "Δt/t = √(1 - r_s/r)", "Δν/ν = gh/c²"],
  ["Gunes'in Schwarzschild yaricapi: r_s = 2·6.674e-11·1.989e30/(3e8)² = 2.95 km. "
   "Gunes bu boyuta sikistirilsaydi kara delik olurdu. Dunya icin bu deger sadece 8.9 mm.",
   "Dunya yuzeyinde 100 m yukseklikteki saat, yerdeki saate gore Δν/ν = gh/c² = "
   "9.81·100/9e16 = 1.09×10⁻¹⁴ oraninda hizli isler. Bir yilda (3.16×10⁷ s) bu "
   "yaklasik 344 nanosaniyelik bir farka karsilik gelir."],
  ["The Sun's Schwarzschild radius is r_s = 2GM/c² = 2.95 km; compressed to that size it "
   "would be a black hole. For Earth the value is just 8.9 mm.",
   "A clock 100 m up runs faster by Δν/ν = gh/c² = 1.09×10⁻¹⁴, which over a year "
   "(3.16×10⁷ s) amounts to about 344 nanoseconds."],
  kw="genel gorelilik|kara delik|egrilik|jeodezik|einstein alan|general relativity|black hole|curvature",
  related="ozel_gorelilik|kozmoloji"),

T("kuantum_temelleri", "Kuantum Mekaniginin Temelleri", "Foundations of Quantum Mechanics", """
Atom altı olceklerde klasik fizik coker; kuantum mekanigi bu olcegin kuramidir.

**Dalga fonksiyonu ψ:** Sistemin tum bilgisini tasir. |ψ|² olasilik yogunlugudur
(Born yorumu). ψ'nin kendisi olculebilir bir buyukluk degildir; genlik olarak
girisim yapabilir ve kuantumun tuhafliginin kaynagi budur.

**Schrodinger denklemi:** iħ ∂ψ/∂t = Ĥψ. Zamanla evrimi belirler ve **deterministiktir**;
rastgelelik yalnizca olcum sirasinda devreye girer.

**Temel ilkeler:**
- *Superpozisyon:* Sistem ayni anda birden fazla ozdurumun toplaminda olabilir.
- *Belirsizlik:* ΔxΔp ≥ ħ/2. Bu bir olcum kusuru degil, dogamin temel bir ozelligidir —
  konum ve momentum Fourier esleri oldugu icin ortaya cikar.
- *Kuantalanma:* Bagli sistemlerde enerji kesikli degerler alir. Bu, sinir kosullarinin
  dogal sonucudur (tipki gitar telindeki duran dalgalar gibi).
- *Dolanıklık:* Iki parcacik ortak bir durumda olabilir; birinin olcumu digerinin
  durumunu aninda belirler. Bell esitsizligi deneyleri (2022 Nobel) bunun yerel gizli
  degiskenlerle aciklanamayacagini gostermistir.

**Yorumlar:** Kopenhag, cok dunyali, de Broglie-Bohm... Hepsi ayni ongoruleri verir;
aralarindaki secim su an deneysel degil felsefidir.
""", """
Classical physics breaks down at subatomic scales; quantum mechanics is the theory of
that regime.

**Wavefunction ψ:** carries all information about the system. |ψ|² is the probability
density (Born rule). ψ itself is not observable; it interferes as an amplitude, and that
is where quantum strangeness comes from.

**Schrodinger equation:** iħ ∂ψ/∂t = Ĥψ. It governs time evolution and is
**deterministic**; randomness enters only at measurement.

**Core principles:**
- *Superposition:* a system can be in a sum of several eigenstates at once.
- *Uncertainty:* ΔxΔp ≥ ħ/2 — not a measurement defect but a structural fact, arising
  because position and momentum are Fourier conjugates.
- *Quantisation:* bound systems have discrete energies, a natural consequence of boundary
  conditions (just like standing waves on a guitar string).
- *Entanglement:* two particles can share a joint state so that measuring one instantly
  fixes the other. Bell-inequality experiments (2022 Nobel) showed this cannot be
  explained by local hidden variables.

**Interpretations:** Copenhagen, many-worlds, de Broglie-Bohm and others all give the
same predictions; the choice between them is currently philosophical, not experimental.
""",
  ["iħ ∂ψ/∂t = Ĥψ", "Ĥψ = Eψ", "ΔxΔp ≥ ħ/2", "λ = h/p", "E = hf",
   "⟨A⟩ = ∫ψ*Âψ dx"],
  ["Sonsuz kuyuda (genislik L) elektron: E_n = n²h²/(8mL²). L = 1 nm icin taban durum "
   "E₁ = 6.02×10⁻²⁰ J = 0.376 eV. Kuyu daraldikca enerji L⁻² ile artar — bu yuzden "
   "kuantum noktalarinin rengi boyutlariyla ayarlanabilir.",
   "Belirsizlik ilkesinden atom boyutu tahmini: elektron 0.1 nm'ye hapsedilirse "
   "Δp ≥ ħ/(2Δx) = 5.3×10⁻²⁵ kg·m/s, kinetik enerji ~1 eV mertebesinde cikar. "
   "Atomlarin neden cokmedigi bu sekilde anlasilir."],
  ["Electron in an infinite well of width L: E_n = n²h²/(8mL²). For L = 1 nm the ground "
   "state is 0.376 eV. Energy scales as L⁻², which is why quantum-dot colour is tunable "
   "by size.",
   "Estimating atomic size from uncertainty: confining an electron to 0.1 nm gives "
   "Δp ≥ 5.3×10⁻²⁵ kg·m/s and a kinetic energy of order 1 eV — this is why atoms do not collapse."],
  kw="kuantum|dalga fonksiyonu|schrodinger|belirsizlik|superpozisyon|dolaniklik|quantum|wavefunction|entanglement",
  related="foton|atom_yapisi|kuantum_alan"),

T("foton", "Foton ve Isigin Ikili Dogasi", "Photons and Wave-Particle Duality", """
Isik hem dalga hem parcacik gibi davranir; hangi yuzunu gorecegimizi yaptigimiz deney
belirler.

**Dalga kaniti:** Girisim (Young cift yarik), kirinim, polarizasyon.
**Parcacik kaniti:** Fotoelektrik olay, Compton sacilmasi, kara cisim isimasi.

**Fotoelektrik olay:** Metalden elektron kopmasi isigin *siddetine* degil *frekansina*
baglidir. Esik frekansinin altinda ne kadar siddetli isik verirseniz verin elektron
kopmaz. Einstein bunu E = hf enerji paketleriyle acikladi (1921 Nobel'i bu calismayadir,
gorelilige degil).

**Compton sacilmasi:** X-isini bir elektrondan sacildiginda dalga boyu artar:
Δλ = (h/m_ec)(1-cosθ). Bu, fotonun momentum tasidiginin (p = h/λ) dogrudan kanitidir.

**de Broglie genellemesi:** Sadece isik degil, **her sey** dalga-parcacik ikiligi
gosterir: λ = h/p. Elektron kirinimi (Davisson-Germer, 1927) bunu dogrulamistir.
Gunumuzde 25000 atomluk molekullerle bile girisim gozlenmistir.
""", """
Light behaves as both wave and particle; which face you see depends on the experiment.

**Wave evidence:** interference (Young's double slit), diffraction, polarisation.
**Particle evidence:** the photoelectric effect, Compton scattering, blackbody radiation.

**Photoelectric effect:** electron ejection depends on light's *frequency*, not its
*intensity*. Below a threshold frequency no intensity ejects electrons. Einstein
explained this with quanta of energy E = hf (his 1921 Nobel was for this, not relativity).

**Compton scattering:** X-rays scattered off electrons increase in wavelength,
Δλ = (h/m_ec)(1-cosθ) — direct proof that photons carry momentum p = h/λ.

**de Broglie's generalisation:** not just light but **everything** shows wave-particle
duality, λ = h/p. Electron diffraction (Davisson-Germer, 1927) confirmed it, and
interference has now been observed with molecules of 25 000 atoms.
""",
  ["E = hf = hc/λ", "p = h/λ", "E_k = hf - W", "Δλ = (h/m_ec)(1-cosθ)"],
  ["Sodyumun is fonksiyonu 2.28 eV. 400 nm morumsu isik (3.10 eV) elektron koparir, "
   "kinetik enerjisi 3.10 - 2.28 = 0.82 eV olur. 600 nm turuncu isik (2.07 eV) ise "
   "ne kadar parlak olursa olsun hicbir elektron koparamaz.",
   "100 W ampul saniyede kac foton yayar? Ortalama 550 nm varsayarsak foton basina "
   "3.6×10⁻¹⁹ J, yani ~2.8×10²⁰ foton/s. Bu kadar cok olmasi isigin neden surekli gorundugunu aciklar."],
  ["Sodium's work function is 2.28 eV. Light at 400 nm (3.10 eV) ejects electrons with "
   "0.82 eV kinetic energy, while 600 nm light (2.07 eV) ejects none no matter how bright.",
   "How many photons per second from a 100 W bulb? At 550 nm each carries 3.6×10⁻¹⁹ J, "
   "giving ~2.8×10²⁰ photons/s — which is why light looks continuous."],
  kw="foton|fotoelektrik|compton|de broglie|ikili doga|photon|photoelectric|duality",
  related="kuantum_temelleri|elektromanyetik_dalga"),

T("atom_yapisi", "Atom Yapisi ve Kuantum Sayilari", "Atomic Structure and Quantum Numbers", """
**Tarihsel gelisim:** Thomson'un uzumlu kek modeli → Rutherford'un cekirdek kesfi
(altin varak deneyi) → Bohr'un kuantalanmis yorungeleri → kuantum mekaniksel orbital modeli.

**Bohr modeli:** Basarisi hidrojen spektrumunu dogru vermesidir: E_n = -13.6Z²/n² eV.
Ama sadece tek elektronlu sistemlerde calisir ve elektronun neden isima yapmadigini
aciklamaz — bu bir ara modeldir.

**Kuantum sayilari:**
- n (bas): enerji duzeyi, 1, 2, 3...
- ℓ (aci momentumu): 0..n-1, orbital sekli (s, p, d, f)
- m_ℓ (manyetik): -ℓ..+ℓ, uzaydaki yonelim
- m_s (spin): ±1/2

**Pauli dislama ilkesi:** Iki elektron ayni dort kuantum sayisina sahip olamaz. Periyodik
tablonun yapisi, kimyanin tamami ve beyaz cucelerin cokmemesi bu ilkeye dayanir.

**Orbital doldurma:** Aufbau ilkesi (dusuk enerjiden basla), Hund kurali (once tek tek
doldur, sonra esle). 4s'in 3d'den once dolmasi bu enerji siralamasinin sonucudur.
""", """
**Historical development:** Thomson's plum-pudding model → Rutherford's discovery of the
nucleus (gold-foil experiment) → Bohr's quantised orbits → the quantum-mechanical orbital
model.

**Bohr model:** its success was reproducing the hydrogen spectrum, E_n = -13.6Z²/n² eV.
But it works only for one-electron systems and cannot explain why the electron does not
radiate — it is a transitional model.

**Quantum numbers:**
- n (principal): energy level, 1, 2, 3...
- ℓ (angular momentum): 0..n-1, orbital shape (s, p, d, f)
- m_ℓ (magnetic): -ℓ..+ℓ, spatial orientation
- m_s (spin): ±1/2

**Pauli exclusion principle:** no two electrons share all four quantum numbers. The
structure of the periodic table, all of chemistry, and the stability of white dwarfs rest
on this.

**Filling orbitals:** the Aufbau principle (lowest energy first) and Hund's rule (singly
occupy before pairing). 4s filling before 3d follows from this energy ordering.
""",
  ["E_n = -13.6 Z²/n² eV", "r_n = n²a₀/Z", "1/λ = R_∞Z²(1/n₁² - 1/n₂²)",
   "L = √(ℓ(ℓ+1))ħ", "2n² elektron kapasitesi"],
  ["Hidrojende n=3'ten n=2'ye gecis (Balmer-α): ΔE = -13.6(1/9 - 1/4) = 1.89 eV, "
   "λ = 1240/1.89 = 656 nm — gorunur kirmizi. Bu cizgi yildiz tayflarinda en tanidik olanidir.",
   "Hidrojenin iyonlasma enerjisi: n=1'den n=∞'a, E = 13.6 eV. Helyum icin (Z=2) Bohr modeli "
   "54.4 eV verir ve tek elektronlu He⁺ icin bu deger dogrudur."],
  ["Hydrogen n=3 → n=2 (Balmer-α): ΔE = 1.89 eV, λ = 656 nm — visible red, the most familiar "
   "line in stellar spectra.",
   "Hydrogen ionisation energy (n=1 → ∞) is 13.6 eV. For He⁺ (Z=2) the Bohr model gives "
   "54.4 eV, which is correct for that one-electron ion."],
  kw="atom|bohr|orbital|kuantum sayilari|pauli|periyodik|atomic structure|quantum numbers|orbitals",
  related="kuantum_temelleri|nukleer_fizik"),

T("nukleer_fizik", "Nukleer Fizik", "Nuclear Physics", """
**Cekirdek:** Proton ve notronlardan (nukleonlar) olusur; guclu nukleer kuvvetle bir
arada tutulur. Bu kuvvet elektriksel itmeden ~100 kat guclu ama menzili sadece ~1 fm.

**Baglanma enerjisi:** Cekirdegin kutlesi, bilesenlerinin toplamindan azdir; fark
Δm, E = Δmc² ile baglanma enerjisine gitmistir. **Nukleon basina baglanma enerjisi**
egrisi Fe-56'da (8.8 MeV) maksimumdur. Bu tek egri hem fuzyonu hem fisyonu aciklar:
demirin solundaki cekirdekler birlesirse, saginfakiler bolunurse enerji aciga cikar.

**Radyoaktif bozunma turleri:**
- α: He-4 cekirdegi salinimi (agir cekirdekler), Z-2, A-4
- β⁻: notron → proton + elektron + antinotrino, Z+1
- β⁺: proton → notron + pozitron + notrino, Z-1
- γ: uyarilmis cekirdegin foton salmasi, Z ve A degismez

**Bozunma yasasi:** N(t) = N₀e^(-λt), λ = ln2/T½. Bu ussel yasa istatistikseldir;
tek bir cekirdegin ne zaman bozunacagi ilkesel olarak ongorulemez.
""", """
**The nucleus:** made of protons and neutrons (nucleons), bound by the strong nuclear
force — about 100 times stronger than electrostatic repulsion but with a range of only
~1 fm.

**Binding energy:** a nucleus weighs less than its parts; the mass defect Δm has gone
into binding energy via E = Δmc². The **binding energy per nucleon** curve peaks at
Fe-56 (8.8 MeV). That single curve explains both fusion and fission: nuclei lighter than
iron release energy by merging, heavier ones by splitting.

**Decay modes:**
- α: emission of a He-4 nucleus (heavy nuclei), Z-2, A-4
- β⁻: neutron → proton + electron + antineutrino, Z+1
- β⁺: proton → neutron + positron + neutrino, Z-1
- γ: photon emission from an excited nucleus, Z and A unchanged

**Decay law:** N(t) = N₀e^(-λt) with λ = ln2/T½. This exponential law is statistical; when
a given nucleus decays is in principle unpredictable.
""",
  ["E = Δmc²", "N = N₀e^(-λt)", "λ = ln2/T½", "A = λN",
   "Q = (m_ilk - m_son)c²"],
  ["C-14 tarihleme: T½ = 5730 yil. Bir orneknte baslangictaki C-14'un %25'i kalmissa "
   "iki yari omur gecmistir → 11460 yil.",
   "U-235 fisyonu basina ~200 MeV aciga cikar. 1 kg U-235'te 2.56×10²⁴ atom var, "
   "toplam 8.2×10¹³ J ≈ 20 kiloton TNT. Ayni kutle komurun ~3 milyon katı enerji verir."],
  ["C-14 dating: T½ = 5730 y. If 25% of the original C-14 remains, two half-lives have "
   "passed → 11 460 years.",
   "U-235 fission releases ~200 MeV each. One kg contains 2.56×10²⁴ atoms, totalling "
   "8.2×10¹³ J ≈ 20 kilotons of TNT — about 3 million times the energy of the same mass of coal."],
  kw="nukleer|cekirdek|radyoaktif|fisyon|fuzyon|yari omur|nuclear|radioactivity|fission|fusion",
  related="parcacik_fizigi|atom_yapisi"),

T("parcacik_fizigi", "Parcacik Fizigi ve Standart Model", "Particle Physics and the Standard Model", """
**Standart Model**, bilinen tum temel parcaciklari ve kutle cekimi disindaki uc kuvveti
tanimlar.

**Madde parcaciklari (fermiyonlar, spin ½):**
- *Kuarklar* (6): u, d, c, s, t, b — guclu kuvveti hisseder, hadronlari olusturur.
- *Leptonlar* (6): e, µ, τ ve karsilik gelen notrinolari — guclu kuvveti hissetmez.
- Uc "nesil" halinde duzenlenir; gunluk madde yalnizca ilk nesildendir (u, d, e).

**Kuvvet tasiyicilari (bozonlar, spin 1):**
- foton (γ): elektromanyetik, kutlesiz, sonsuz menzil
- W±, Z⁰: zayif kuvvet, agir (~80-91 GeV), bu yuzden menzili cok kisa
- gluon (8 adet): guclu kuvvet, renk yuku tasir

**Higgs bozonu (spin 0):** 2012'de CERN'de bulundu (125 GeV). Higgs alani, temel
parcaciklara kutle kazandirir. Onemli ayrinti: protonun kutlesinin yalnizca ~%1'i
Higgs'ten gelir; gerisi kuark-gluon baglanma enerjisidir.

**Acik sorular:** Kutle cekimi Standart Model'e dahil degil; karanlik madde ve karanlik
enerji aciklanmiyor; notrinolarin kutlesi modelde ongorulmemisti; madde-antimadde
asimetrisi cozulmus degil.
""", """
The **Standard Model** describes all known elementary particles and three of the four
forces (all but gravity).

**Matter particles (fermions, spin ½):**
- *Quarks* (6): u, d, c, s, t, b — feel the strong force and form hadrons.
- *Leptons* (6): e, µ, τ and their neutrinos — do not feel the strong force.
- They come in three "generations"; everyday matter uses only the first (u, d, e).

**Force carriers (bosons, spin 1):**
- photon (γ): electromagnetic, massless, infinite range
- W±, Z⁰: weak force, heavy (~80-91 GeV), hence very short range
- gluons (8): strong force, carrying colour charge

**Higgs boson (spin 0):** found at CERN in 2012 (125 GeV). The Higgs field gives mass to
elementary particles. An important detail: only ~1% of the proton's mass comes from the
Higgs; the rest is quark-gluon binding energy.

**Open questions:** gravity is not included; dark matter and dark energy are unexplained;
neutrino masses were not predicted; and the matter-antimatter asymmetry remains unsolved.
""",
  ["p = uud", "n = udd", "E = mc² (parcacik uretimi)",
   "m_H ≈ 125 GeV/c²", "Q_u = +2/3, Q_d = -1/3"],
  ["Proton yukunu kuarklardan hesaplayalim: uud = 2/3 + 2/3 - 1/3 = +1. "
   "Notron: udd = 2/3 - 1/3 - 1/3 = 0. Model tutarli.",
   "LHC'de iki proton 13 TeV'de carpistiginda, bu enerjiden E = mc² ile yeni parcaciklar "
   "uretilir. 125 GeV'lik Higgs uretmek icin yeterli enerji vardir ama olasilik cok dusuktur — "
   "bu yuzden milyarlarca carpisma gerekir."],
  ["Proton charge from quarks: uud = 2/3 + 2/3 - 1/3 = +1; neutron udd = 0. The model is "
   "consistent.",
   "When two protons collide at 13 TeV at the LHC, that energy creates new particles via "
   "E = mc². There is ample energy for a 125 GeV Higgs, but the probability is tiny — hence "
   "the need for billions of collisions."],
  kw="parcacik fizigi|standart model|kuark|lepton|higgs|bozon|particle physics|standard model|quark",
  related="nukleer_fizik|kuantum_alan"),

T("kuantum_alan", "Kuantum Alan Kurami", "Quantum Field Theory", """
Kuantum mekanigi ile ozel gorelilikin birlesimidir. Temel fikir: parcaciklar temel
degildir; **alanlar** temeldir ve parcaciklar bu alanlarin uyarilmalaridir (kuantumlari).

Elektron alani evrenin her yerindedir; "bir elektron" o alandaki lokalize bir
uyarilmadir. Bu, ozdes parcaciklarin neden tam olarak ozdes oldugunu aciklar.

**Neden gerekli?** Kuantum mekanigi parcacik sayisinin sabit oldugunu varsayar. Ama
E = mc² ile parcacik yaratilip yok edilebilir. QFT bunu dogal olarak icerir.

**Onemli kavramlar:**
- *Feynman diyagramlari:* Etkilesim genliklerini hesaplamak icin gorsel-cebirsel arac.
- *Sanal parcaciklar:* Ic hatlarda gorunen, kutle kabugunda olmayan ara terimler.
- *Renormalizasyon:* Hesaplarda cikan sonsuzluklarin sistematik olarak olculebilir
  buyukluklerle yeniden ifade edilmesi.
- *Vakum:* Bos degildir; sifir nokta dalgalanmalari icerir. Casimir etkisi bunun
  olculebilir bir sonucudur.

**Basarisi:** Elektronun anomal manyetik momenti (g-2), QED tarafindan 12 basamak
dogrulukla ongorulur — fizigin en hassas dogrulanmis ongorusudur.
""", """
QFT unites quantum mechanics with special relativity. The core idea: particles are not
fundamental; **fields** are, and particles are excitations (quanta) of those fields.

The electron field exists everywhere; "an electron" is a localised excitation of it. This
explains why identical particles are *exactly* identical.

**Why is it needed?** Quantum mechanics assumes a fixed particle number, but E = mc²
allows particles to be created and destroyed. QFT accommodates this naturally.

**Key concepts:**
- *Feynman diagrams:* a visual-algebraic tool for computing interaction amplitudes.
- *Virtual particles:* off-shell intermediate terms appearing on internal lines.
- *Renormalisation:* systematically re-expressing the infinities that arise in terms of
  measurable quantities.
- *The vacuum:* not empty — it holds zero-point fluctuations. The Casimir effect is a
  measurable consequence.

**Its triumph:** QED predicts the electron's anomalous magnetic moment (g-2) to twelve
digits — the most precisely verified prediction in physics.
""",
  ["ℒ = ψ̄(iγ^μ∂_μ - m)ψ", "[φ(x), π(y)] = iħδ(x-y)",
   "a_e = (g-2)/2 ≈ 0.00115965218", "F_Casimir/A = -π²ħc/(240d⁴)"],
  ["Casimir kuvveti: 1 µm arali iki plaka arasinda basinc = π²ħc/(240·(1e-6)⁴) = "
   "1.3×10⁻³ Pa. Kucuk gorunur ama mesafe 10 nm'ye dusurulurse 10⁸ kat artar ve "
   "MEMS cihazlarinda onemli hale gelir.",
   "e⁺e⁻ → µ⁺µ⁻ sureci icin esik enerji: 2m_µc² = 2·105.7 = 211.4 MeV. "
   "Bunun altinda ne kadar carpistirsaniz muon uretemezsiniz."],
  ["Casimir pressure between plates 1 µm apart: π²ħc/(240d⁴) = 1.3×10⁻³ Pa. Small, but at "
   "10 nm it grows by 10⁸ and matters for MEMS devices.",
   "Threshold for e⁺e⁻ → µ⁺µ⁻ is 2m_µc² = 211.4 MeV; below that no amount of collisions "
   "produces muons."],
  kw="kuantum alan|qft|feynman|renormalizasyon|casimir|vakum|quantum field theory|virtual particles",
  related="parcacik_fizigi|kuantum_temelleri"),

T("istatistiksel_mekanik", "Istatistiksel Mekanik", "Statistical Mechanics", """
Mikroskobik yasalar ile makroskobik termodinamik arasinda kopru kurar. Temel soru:
10²³ parcacigin tek tek denklemlerini cozemeyiz, ama istatistik kullanarak
sicaklik, basinc ve entropiyi turetebiliriz.

**Temel postulat:** Yalitilmis bir sistemde erisilebilir tum mikro durumlar esit
olasidir. Buradan Boltzmann entropisi cikar: S = k_B ln Ω.

**Toplulklar (ensembles):**
- *Mikrokanonik:* Yalitilmis sistem (E, V, N sabit)
- *Kanonik:* Isi banyosuyla temasta (T, V, N sabit) — en cok kullanilan
- *Buyuk kanonik:* Parcacik alisverisi de var (T, V, µ sabit)

**Bolusum fonksiyonu Z = Σe^(-E_i/k_BT):** Sistemin tum termodinamigi bundan turetilir.
F = -k_BT ln Z, sonra tum diger buyuklukler F'nin turevlerinden gelir. Z'yi
hesaplayabilirseniz sistemi cozmus olursunuz.

**Kuantum istatistigi:** Ozdes parcaciklar ayirt edilemez oldugu icin klasik sayim
yanlistir.
- *Bose-Einstein* (bozonlar): Ayni duruma sinirsiz doluluk → Bose-Einstein yogusmasi, lazer
- *Fermi-Dirac* (fermiyonlar): Pauli yasagi → metallerdeki elektron gazi, beyaz cuce basinci
""", """
Statistical mechanics bridges microscopic laws and macroscopic thermodynamics. The core
problem: we cannot solve 10²³ coupled equations, but with statistics we can derive
temperature, pressure and entropy.

**Fundamental postulate:** in an isolated system all accessible microstates are equally
probable. From this follows the Boltzmann entropy S = k_B ln Ω.

**Ensembles:**
- *Microcanonical:* isolated system (fixed E, V, N)
- *Canonical:* in contact with a heat bath (fixed T, V, N) — the most used
- *Grand canonical:* particles exchanged too (fixed T, V, µ)

**Partition function Z = Σe^(-E_i/k_BT):** all thermodynamics follows from it. With
F = -k_BT ln Z, every other quantity comes from derivatives of F. Compute Z and you have
solved the system.

**Quantum statistics:** identical particles are indistinguishable, so classical counting
is wrong.
- *Bose-Einstein* (bosons): unlimited occupancy → Bose-Einstein condensates, lasers
- *Fermi-Dirac* (fermions): Pauli exclusion → the electron gas in metals, white dwarf pressure
""",
  ["S = k_B ln Ω", "Z = Σe^(-βE_i)", "P_i = e^(-βE_i)/Z", "F = -k_BT ln Z",
   "⟨n⟩_BE = 1/(e^(β(E-µ))-1)", "⟨n⟩_FD = 1/(e^(β(E-µ))+1)"],
  ["Iki durumlu sistem (0 ve ε enerjili): Z = 1 + e^(-ε/kT). Yuksek sicaklikta iki durum "
   "esit dolar (P = ½ her biri); dusuk sicaklikta sistem taban durumda donar.",
   "Bir metalde Fermi enerjisi ~5 eV, yani ~58000 K'e karsilik gelir. Oda sicakliginda "
   "(0.025 eV) elektronlarin yalnizca cok kucuk bir kismi uyarilabilir — metallerin isi "
   "kapasitesinin neden beklenenden cok dusuk oldugu boyle aciklanir."],
  ["A two-level system (energies 0 and ε): Z = 1 + e^(-ε/kT). At high T both levels are "
   "equally occupied; at low T the system freezes into the ground state.",
   "A metal's Fermi energy of ~5 eV corresponds to ~58 000 K. At room temperature "
   "(0.025 eV) only a tiny fraction of electrons can be excited — which explains why the "
   "electronic heat capacity of metals is far smaller than classically expected."],
  kw="bose einstein yogusmasi|bose einstein condensation|bec|durum yogunlugu|density of states|fermi dirac statistics|maxwell boltzmann statistics|istatistiksel mekanik|bolusum fonksiyonu|boltzmann|fermi dirac|bose einstein|statistical mechanics|partition function",
  related="termodinamik_yasalari|ideal_gaz_kinetik|katihal"),

T("katihal", "Katihal Fizigi", "Solid State Physics", """
Kristal katilarin elektronik ve yapisal ozelliklerini inceler; yari iletken teknolojisinin
temelidir.

**Kristal yapi:** Periyodik orgu (lattice) + baz. Ters uzay ve Brillouin bolgesi,
kristallerde dalga davranisini analiz etmenin dogal cercevesidir. Bragg yasasi
(2d sinθ = nλ) X-isini kirinimiyla yapiyi belirlememizi saglar.

**Bant kurami:** Periyodik potansiyelde elektron enerjileri **bantlar** halinde toplanir
ve aralarinda **yasak bantlar** (band gap) bulunur. Bir malzemenin iletken, yalitkan mi
yoksa yari iletken mi oldugunu belirleyen sey budur:
- Iletken: valans bandi kismen dolu (Eg yok)
- Yari iletken: Eg ~ 0.1-3 eV (Si: 1.12 eV, GaAs: 1.42 eV)
- Yalitkan: Eg > ~4 eV

**Katkilama (doping):** Si'ye P eklenirse (n-tipi) fazla elektron, B eklenirse (p-tipi)
delik olusur. p-n eklemi diyot, transistor ve gunes hucresinin temelidir.

**Ilginc olgular:** Superiletkenlik (Cooper ciftleri, BCS kurami), kuantum Hall etkisi,
topolojik yalitkanlar, grafen gibi 2B malzemeler.
""", """
Solid state physics studies the electronic and structural properties of crystals; it
underpins semiconductor technology.

**Crystal structure:** a periodic lattice plus a basis. Reciprocal space and the
Brillouin zone are the natural framework for wave behaviour in crystals. Bragg's law
(2d sinθ = nλ) lets X-ray diffraction determine the structure.

**Band theory:** in a periodic potential electron energies group into **bands** separated
by **band gaps**. This determines whether a material is a conductor, insulator or
semiconductor:
- Conductor: partially filled valence band (no gap)
- Semiconductor: Eg ~ 0.1-3 eV (Si: 1.12 eV, GaAs: 1.42 eV)
- Insulator: Eg > ~4 eV

**Doping:** adding P to Si (n-type) supplies extra electrons; adding B (p-type) creates
holes. The p-n junction is the basis of diodes, transistors and solar cells.

**Notable phenomena:** superconductivity (Cooper pairs, BCS theory), the quantum Hall
effect, topological insulators, and 2D materials such as graphene.
""",
  ["2d sinθ = nλ", "E = ħ²k²/(2m*)", "n_i = √(N_cN_v)e^(-Eg/2kT)",
   "σ = neµ_e + peµ_h", "T_c (BCS) ≈ 1.14Θ_D e^(-1/N(0)V)"],
  ["Silisyumun 1.12 eV yasak bandi: hangi dalga boyunun altindaki isik sogurulur? "
   "λ = 1240/1.12 = 1107 nm. Bu yuzden Si gunes hucreleri kizilotesi isigin bir kismini "
   "kullanamaz ve teorik verim ~%33 ile sinirlidir (Shockley-Queisser).",
   "Bakirdaki serbest elektron yogunlugu 8.5×10²⁸ m⁻³. 1 A akim tasiyan 1 mm² kesitli telde "
   "surukleme hizi v = I/(nAe) = 7.4×10⁻⁵ m/s — saatte 27 cm! Elektrik sinyali hizlidir ama "
   "elektronlarin kendisi cok yavastir."],
  ["Silicon's 1.12 eV gap: light below which wavelength is absorbed? λ = 1240/1.12 = 1107 nm. "
   "That is why Si solar cells miss part of the infrared and are capped near 33% efficiency "
   "(Shockley-Queisser).",
   "Copper has 8.5×10²⁸ free electrons/m³. Carrying 1 A in a 1 mm² wire the drift velocity is "
   "7.4×10⁻⁵ m/s — 27 cm per hour. The signal is fast; the electrons are not."],
  kw="katihal|yari iletken|bant|kristal|doping|superiletken|solid state|semiconductor|band gap",
  related="istatistiksel_mekanik|kuantum_temelleri"),

T("optik_temelleri", "Optik", "Optics", """
**Geometrik optik:** Isigi isin olarak ele alir; dalga boyu engellere gore cok kucukse
gecerlidir.
- Yansima: θ_gelme = θ_yansima
- Kirilma (Snell): n₁sinθ₁ = n₂sinθ₂
- Tam yansima: n₁ > n₂ oldugunda θ_c = arcsin(n₂/n₁) uzerinde isik hic gecmez —
  fiber optik kablolarin calisma ilkesi budur.
- Mercek/ayna: 1/f = 1/d_o + 1/d_i, buyutme M = -d_i/d_o

**Dalga optigi:** Girisim ve kirinim, isigin dalga dogasini gerektirir.
- Cift yarik: d sinθ = mλ (maksimum)
- Tek yarik kirinimi: a sinθ = mλ (minimum)
- Kirinim sinirlanmasi (Rayleigh): θ = 1.22λ/D. Bu, teleskop ve mikroskoplarin
  cozunurluk sinirini belirler — daha buyuk aynanin asil faydasi budur.
- Ince film girisimi: sabun kopugu ve yag lekesindeki renkler.

**Polarizasyon:** Malus yasasi I = I₀cos²θ. Brewster acisinda (tanθ_B = n₂/n₁) yansiyan
isik tam polarize olur — polarize gunes gozlugu bu yuzden su ve yol parlamasini keser.
""", """
**Geometric optics:** treats light as rays; valid when the wavelength is much smaller
than the obstacles.
- Reflection: θ_i = θ_r
- Refraction (Snell): n₁sinθ₁ = n₂sinθ₂
- Total internal reflection: for n₁ > n₂, no light escapes beyond θ_c = arcsin(n₂/n₁) —
  the operating principle of optical fibre.
- Lenses/mirrors: 1/f = 1/d_o + 1/d_i, magnification M = -d_i/d_o

**Wave optics:** interference and diffraction require the wave nature of light.
- Double slit: d sinθ = mλ (maxima)
- Single-slit diffraction: a sinθ = mλ (minima)
- Diffraction limit (Rayleigh): θ = 1.22λ/D, setting the resolution of telescopes and
  microscopes — the main reason bigger mirrors help.
- Thin-film interference: the colours in soap bubbles and oil slicks.

**Polarisation:** Malus's law I = I₀cos²θ. At Brewster's angle (tanθ_B = n₂/n₁) reflected
light is fully polarised — which is why polarised sunglasses cut glare from water and roads.
""",
  ["n₁sinθ₁ = n₂sinθ₂", "1/f = 1/d_o + 1/d_i", "d sinθ = mλ",
   "θ_min = 1.22λ/D", "I = I₀cos²θ", "tanθ_B = n₂/n₁"],
  ["Sudan (n=1.33) havaya gecerken tam yansima acisi: θ_c = arcsin(1/1.33) = 48.8°. "
   "Havuzun dibinden yukari bakinca bu acinin disi ayna gibi gorunur.",
   "Hubble'in 2.4 m aynasi, 550 nm'de acisal cozunurlugu: θ = 1.22·550e-9/2.4 = 2.8×10⁻⁷ rad "
   "= 0.058 yay saniyesi. Ayni buyuklukteki yer teleskobu atmosfer yuzunden ~1 yay saniyesinde kalir."],
  ["Water (n=1.33) to air: θ_c = arcsin(1/1.33) = 48.8°. Looking up from the bottom of a "
   "pool, beyond that angle the surface acts as a mirror.",
   "Hubble's 2.4 m mirror at 550 nm resolves θ = 1.22λ/D = 2.8×10⁻⁷ rad = 0.058 arcsec, while "
   "a same-size ground telescope is limited to ~1 arcsec by the atmosphere."],
  kw="optik|mercek|kirilma|girisim|kirinim|polarizasyon|optics|lens|refraction|interference",
  related="elektromanyetik_dalga|dalga_hareketi"),

T("dalga_hareketi", "Dalga Hareketi ve Ses", "Wave Motion and Sound", """
**Dalga turleri:** Enine (dalgalanma yayilma yonune dik — isik, tel dalgalari) ve boyuna
(paralel — ses). Ses katilarda hem enine hem boyuna yayilabilir; sivilarda ve gazlarda
yalnizca boyuna.

**Temel bagintilar:** v = fλ, y(x,t) = A sin(kx - ωt + φ), k = 2π/λ, ω = 2πf.
Onemli: dalga hizi **ortamin ozelligidir**; frekans kaynagin ozelligidir. Dalga baska bir
ortama gecerken frekans degismez, dalga boyu degisir.

**Superpozisyon ve duran dalgalar:** Iki dalga ustuste binerse genlikler toplanir.
Zit yonlu iki ozdes dalga duran dalga olusturur; sabit uclu telde L = nλ/2 kosulu
harmonikleri belirler. Muzik aletlerinin perde yapisi bu.

**Vurum (beat):** Yakin frekansli iki ses f_vurum = |f₁ - f₂| ile genlik dalgalanmasi
yaratir. Gitar akordunda kullanilan sey budur.

**Doppler:** Kaynak veya gozlemci hareketliyse algilanan frekans degisir. Ses icin
f' = f(v±v_o)/(v∓v_s). Isik icin gorelilik gerekir; kirmizi kayma evrenin genislemesini
boyle olcuyoruz.

**Sok dalgasi:** Kaynak ses hizini asarsa (Mach konisi) sinθ = v/v_s.
""", """
**Types:** transverse (oscillation perpendicular to propagation — light, string waves) and
longitudinal (parallel — sound). Sound propagates both ways in solids but only
longitudinally in liquids and gases.

**Basics:** v = fλ, y(x,t) = A sin(kx - ωt + φ), k = 2π/λ, ω = 2πf. Crucially, wave speed
is a **property of the medium**, frequency a property of the source. Crossing into a new
medium, frequency stays fixed and wavelength changes.

**Superposition and standing waves:** overlapping waves add their amplitudes. Two identical
counter-propagating waves form a standing wave; on a fixed-end string L = nλ/2 sets the
harmonics — the basis of musical instruments.

**Beats:** two nearby frequencies produce an amplitude modulation at f_beat = |f₁ - f₂|,
the effect used to tune a guitar.

**Doppler:** motion of source or observer shifts the perceived frequency; for sound
f' = f(v±v_o)/(v∓v_s). Light requires relativity — cosmological redshift is how we measure
the expansion of the universe.

**Shock waves:** when the source exceeds the sound speed, the Mach cone satisfies
sinθ = v/v_s.
""",
  ["v = fλ", "y = A sin(kx - ωt)", "v_tel = √(T/µ)", "f_n = nv/(2L)",
   "f_vurum = |f₁-f₂|", "β = 10log(I/I₀) dB"],
  ["440 Hz'e akort edilen gitar teli 3 Hz vurum veriyorsa telin frekansi 437 veya 443 Hz'dir. "
   "Teli biraz gerip vurum azaliyorsa 437 imis demektir.",
   "Bir ses kaynagi 10 kat uzaklasirsa siddet 100 kat azalir (ters kare), "
   "ses duzeyi ise 10log(100) = 20 dB duser. Insan kulagi bunu 'yaklasik dortte bir kadar "
   "yuksek' olarak algilar."],
  ["A guitar string beating 3 Hz against a 440 Hz reference is at 437 or 443 Hz. If tightening "
   "it reduces the beat, it was 437 Hz.",
   "Moving 10× further from a source drops intensity 100× (inverse square) and the level by "
   "10log(100) = 20 dB, which the ear perceives as roughly a quarter as loud."],
  kw="dalga|ses|duran dalga|doppler|vurum|harmonik|wave|sound|standing wave|beats",
  related="optik_temelleri|elektromanyetik_dalga"),

T("akiskanlar", "Akiskanlar Mekanigi", "Fluid Mechanics", """
**Statik:** Hidrostatik basinc P = ρgh derinlikle artar ve **yalnizca derinlige** baglidir
(kabin sekline degil — hidrostatik paradoks). Pascal ilkesi: kapali akiskanda basinc her
yone esit iletilir; hidrolik pres bu ilkeyle kuvvet kazandirir.

**Arsimet:** Batan hacmin agirligi kadar kaldirma kuvveti etki eder: F_b = ρ_sivi·g·V_batan.
Bir cisim yuzer ancak ve ancak ortalama yogunlugu sividan kucukse.

**Dinamik:**
- *Sureklilik:* A₁v₁ = A₂v₂ (kutlenin korunumu). Daralan borudan gecen akiskan hizlanir.
- *Bernoulli:* P + ½ρv² + ρgh = sabit. Bu enerji korunumudur. Hizlanan akiskanin basinci
  duser. Ucak kanadi, karbüratör ve Venturi olcerin ilkesi.

**Bernoulli hakkinda uyari:** Ucak kaldirmasini yalnizca Bernoulli ile aciklamak eksiktir.
Kaldirma, kanadin havayi asagi yonlendirmesinin (Newton 3. yasa) ve dolasim (Kutta-Zhukovski)
kavramlarinin birlikte ele alinmasiyla dogru anlasilir.

**Viskozite ve rejim:** Reynolds sayisi Re = ρvL/µ akisin laminer (Re < ~2300 boruda) mi
turbulent (Re > ~4000) mi oldugunu belirler. Poiseuille yasasi laminer boru akisinda
debiyi verir: Q = πΔPr⁴/(8µL) — yaricapin **dorduncu kuvveti**! Damarlarda kucuk bir
daralma akisi dramatik dusurur.
""", """
**Statics:** hydrostatic pressure P = ρgh grows with depth and depends **only on depth**,
not the vessel shape (the hydrostatic paradox). Pascal's principle: pressure in a confined
fluid is transmitted equally in all directions — the basis of hydraulic presses.

**Archimedes:** the buoyant force equals the weight of displaced fluid,
F_b = ρ_fluid·g·V_displaced. A body floats exactly when its mean density is below the fluid's.

**Dynamics:**
- *Continuity:* A₁v₁ = A₂v₂ (mass conservation). Fluid speeds up through a constriction.
- *Bernoulli:* P + ½ρv² + ρgh = const — energy conservation. Faster flow means lower
  pressure: the principle behind the Venturi meter and carburettor.

**A caution about Bernoulli:** explaining aircraft lift by Bernoulli alone is incomplete.
Lift is properly understood through the wing deflecting air downward (Newton's third law)
together with circulation (Kutta-Zhukovsky).

**Viscosity and regime:** the Reynolds number Re = ρvL/µ decides whether flow is laminar
(Re < ~2300 in a pipe) or turbulent (Re > ~4000). Poiseuille's law gives laminar pipe flow:
Q = πΔPr⁴/(8µL) — the **fourth power** of radius. A small narrowing of a blood vessel cuts
flow dramatically.
""",
  ["P = ρgh", "F_b = ρgV", "A₁v₁ = A₂v₂", "P + ½ρv² + ρgh = sabit",
   "Re = ρvL/µ", "Q = πΔPr⁴/(8µL)"],
  ["10 m derinlikteki basinc: P = 1000·9.81·10 = 98100 Pa ≈ 1 atm. Yani her 10 m suda "
   "bir atmosfer eklenir; dalgiclarin 10 m'de toplam 2 atm hissetmesinin nedeni budur.",
   "Bir damar yaricapi %20 daralirsa (r → 0.8r), debi 0.8⁴ = 0.41 katina duser — "
   "yani %59 azalir. Kalp ayni akisi surdurmek icin basinci 2.4 kat artirmalidir."],
  ["Pressure at 10 m depth: P = ρgh = 98 100 Pa ≈ 1 atm. Every 10 m of water adds an "
   "atmosphere, which is why a diver at 10 m feels 2 atm total.",
   "If a vessel narrows by 20% (r → 0.8r), flow falls to 0.8⁴ = 0.41 of its value — a 59% "
   "drop. The heart must raise pressure 2.4× to maintain the same flow."],
  kw="akiskan|bernoulli|arsimet|basinc|viskozite|reynolds|fluid|buoyancy|pressure|viscosity",
  related="termodinamik_yasalari|newton_yasalari"),

T("kozmoloji", "Kozmoloji", "Cosmology", """
Evrenin butun olarak yapisini, kokenini ve evrimini inceler.

**Buyuk Patlama:** Evren ~13.8 milyar yil once cok sicak ve yogun bir durumdan
genislemeye basladi. Yaygin yanlis anlama: bu uzayda bir noktada olan bir "patlama"
degil, **uzayin kendisinin genislemesidir**. Galaksiler uzayda hareket etmiyor; aralarindaki
uzay buyuyor.

**Uc temel kanit:**
1. *Hubble-Lemaitre yasasi:* v = H₀d — uzak galaksiler daha hizli uzaklasiyor.
2. *Kozmik mikrodalga arka plan (CMB):* 2.725 K'lik neredeyse kusursuz kara cisim isimasi;
   evrenin 380 000 yasindaki halinden kalma. Kucuk sicaklik dalgalanmalari (~10⁻⁵)
   bugunku yapinin tohumlari.
3. *Hafif element bollugu:* Buyuk Patlama nukleosentezi ~%75 H, ~%25 He-4 ongorur ve
   gozlem bunu dogrular.

**Evrenin bilesenleri:** ~%5 siradan madde, ~%27 karanlik madde, ~%68 karanlik enerji.
Yani evrenin %95'inin ne oldugunu bilmiyoruz. Karanlik madde galaksi donme egrilerinden
ve kutle cekim merceklemesinden; karanlik enerji ise 1998'de kesfedilen **hizlanan
genislemeden** anlasildi.

**Acik problemler:** Hubble gerilimi (yerel ve CMB olcumleri farkli H₀ veriyor),
karanlik enerjinin dogasi, enflasyon mekanizmasi, madde-antimadde asimetrisi.
""", """
Cosmology studies the structure, origin and evolution of the universe as a whole.

**Big Bang:** the universe began expanding from a hot, dense state ~13.8 billion years ago.
A common misconception: it was not an explosion at a point in space but **the expansion of
space itself**. Galaxies are not moving through space; the space between them is growing.

**Three key pieces of evidence:**
1. *Hubble-Lemaitre law:* v = H₀d — more distant galaxies recede faster.
2. *Cosmic microwave background:* a near-perfect 2.725 K blackbody left from when the
   universe was 380 000 years old. Its tiny (~10⁻⁵) temperature fluctuations seeded all
   present-day structure.
3. *Light-element abundances:* Big Bang nucleosynthesis predicts ~75% H and ~25% He-4,
   which observation confirms.

**Composition:** ~5% ordinary matter, ~27% dark matter, ~68% dark energy — meaning we do
not know what 95% of the universe is. Dark matter is inferred from galactic rotation curves
and gravitational lensing; dark energy from the **accelerating expansion** discovered in 1998.

**Open problems:** the Hubble tension (local and CMB measurements disagree on H₀), the
nature of dark energy, the mechanism of inflation, and the matter-antimatter asymmetry.
""",
  ["v = H₀d", "H₀ ≈ 67-73 km/s/Mpc", "z = (λ_gozlenen - λ_kaynak)/λ_kaynak",
   "a(t) olcek carpani", "Ω_m + Ω_Λ + Ω_k = 1", "t_H = 1/H₀ ≈ 14.4 milyar yil"],
  ["100 Mpc uzaklikta bir galaksi: v = 70·100 = 7000 km/s ile uzaklasir. "
   "Kirmizi kayma z ≈ v/c = 0.023.",
   "Hubble zamani 1/H₀: H₀ = 70 km/s/Mpc = 2.27×10⁻¹⁸ s⁻¹, 1/H₀ = 4.4×10¹⁷ s = 14 milyar yil. "
   "Gercek yasin (13.8) bu kadar yakin cikmasi tesaduf degil; yavaslama ve hizlanma "
   "donemleri kabaca birbirini dengeler."],
  ["A galaxy at 100 Mpc recedes at v = H₀d = 7000 km/s, giving redshift z ≈ v/c = 0.023.",
   "Hubble time: H₀ = 70 km/s/Mpc = 2.27×10⁻¹⁸ s⁻¹, so 1/H₀ = 14 billion years. That this "
   "lands so near the true 13.8 is not a coincidence — the deceleration and acceleration eras "
   "roughly cancel."],
  kw="kozmoloji|buyuk patlama|hubble|cmb|karanlik madde|karanlik enerji|cosmology|big bang|dark matter",
  related="genel_gorelilik|astrofizik"),

T("astrofizik", "Astrofizik ve Yildizlar", "Astrophysics and Stars", """
**Yildizlarin enerji kaynagi:** Cekirdekteki nukleer fuzyon. Gunes'te proton-proton
zinciri hakimdir: 4¹H → ⁴He + 2e⁺ + 2ν + 26.7 MeV. Daha agir yildizlarda CNO cevrimi
one gecer.

**Hidrostatik denge:** Yildiz, ice dogru kutle cekimi ile disa dogru basinc gradyaninin
dengesindedir. Bu denge bozuldugunda yildiz ya buzuşur ya genisler — yildiz evriminin
tum asamalari bu dengenin degisimidir.

**Hertzsprung-Russell diyagrami:** Yildizlarin parlaklik-sicaklik grafigi. Yildizlarin
%90'i **ana kol** uzerindedir. Bir yildizin ana koldaki omru kutleye cok guclu baglidir:
t ∝ M/L ve L ∝ M^3.5, dolayisiyla t ∝ M^-2.5. Gunes'in 10 milyar yili varken 10 M☉ bir
yildiz sadece ~30 milyon yil yasar.

**Yildiz sonu (kutleye gore):**
- < 8 M☉: kirmizi dev → gezegenimsi bulutsu → **beyaz cuce** (Chandrasekhar siniri 1.4 M☉,
  elektron dejenerasyon basinci ile ayakta durur)
- 8-25 M☉: supernova (Tip II) → **notron yildizi** (~1.4-2.2 M☉, notron dejenerasyonu)
- > 25 M☉: → **kara delik**

**Mesafe merdiveni:** Paralaks (yakin) → Sefeid degiskenler (periyot-parlaklik iliskisi) →
Tip Ia supernova (standart mum) → kirmizi kayma. Her basamak bir oncekiyle kalibre edilir.
""", """
**Stellar energy source:** nuclear fusion in the core. In the Sun the proton-proton chain
dominates: 4¹H → ⁴He + 2e⁺ + 2ν + 26.7 MeV. In heavier stars the CNO cycle takes over.

**Hydrostatic equilibrium:** a star balances inward gravity against an outward pressure
gradient. Every stage of stellar evolution is a shift in that balance.

**Hertzsprung-Russell diagram:** luminosity versus temperature. About 90% of stars sit on
the **main sequence**. Main-sequence lifetime depends steeply on mass: t ∝ M/L with
L ∝ M^3.5, so t ∝ M^-2.5. The Sun gets 10 billion years; a 10 M☉ star only ~30 million.

**Stellar endpoints (by mass):**
- < 8 M☉: red giant → planetary nebula → **white dwarf** (Chandrasekhar limit 1.4 M☉,
  supported by electron degeneracy pressure)
- 8-25 M☉: Type II supernova → **neutron star** (~1.4-2.2 M☉, neutron degeneracy)
- > 25 M☉: → **black hole**

**Distance ladder:** parallax (nearby) → Cepheid variables (period-luminosity relation) →
Type Ia supernovae (standard candles) → redshift. Each rung is calibrated by the previous one.
""",
  ["L = 4πR²σT⁴", "4¹H → ⁴He + 26.7 MeV", "t ∝ M^-2.5",
   "M_Ch = 1.4 M☉", "m - M = 5log(d/10pc)", "λ_max T = 2.898×10⁻³ m·K"],
  ["Gunes'in yuzey sicakligi 5778 K. Wien yasasi ile tepe dalga boyu: "
   "λ = 2.898e-3/5778 = 502 nm — yesil bolge. Gozumuzun en duyarli oldugu yerin burasi olmasi "
   "evrimsel bir tesaduf degil.",
   "Gunes saniyede 4.3 milyon ton kutleyi enerjiye ceviriyor: P = 3.828×10²⁶ W, "
   "m = P/c² = 4.26×10⁹ kg/s. 4.6 milyar yilda toplam kaybi kutlesinin sadece ~%0.03'u."],
  ["The Sun's 5778 K surface peaks at λ = 2.898e-3/5778 = 502 nm by Wien's law — green, right "
   "where our eyes are most sensitive, which is no evolutionary accident.",
   "The Sun converts 4.3 million tonnes of mass to energy per second: m = P/c² = 4.26×10⁹ kg/s. "
   "Over 4.6 billion years that is only ~0.03% of its mass."],
  kw="astrofizik|yildiz|supernova|beyaz cuce|notron yildizi|hr diyagrami|astrophysics|stellar|supernova",
  related="kozmoloji|nukleer_fizik|genel_gorelilik"),

T("titresim", "Titresim ve Harmonik Hareket", "Oscillations and Harmonic Motion", """
**Basit harmonik hareket (BHH):** Geri cagirici kuvvet yer degistirmeyle orantili ve
zit yonluyse (F = -kx) ortaya cikar. Cozum: x(t) = A cos(ωt + φ), ω = √(k/m).

**Kritik ozellik:** Periyot **genlikten bagimsizdir** (izokronizm). Galileo'nun kesfettigi
bu ozellik sarkacli saatleri mumkun kilmistir. Ama bu yalnizca kucuk aci yaklasiminda
(sinθ ≈ θ) dogrudur; buyuk genlikte sarkacin periyodu artar.

**Sonumlu titresim:** F = -kx - bv. Uc rejim vardir:
- *Az sonumlu* (b² < 4mk): Genligi ussel azalan salinim
- *Kritik sonumlu* (b² = 4mk): En hizli sekilde salinimsiz denge — kapi kapayicilari,
  amortisorler bu sekilde tasarlanir
- *Asiri sonumlu:* Yavas, salinimsiz donus

**Zorlanmis titresim ve rezonans:** Dis kuvvet dogal frekansa yaklasinca genlik cok
buyur. Sonum ne kadar azsa rezonans o kadar keskin ve tehlikelidir. Tacoma Narrows
koprusunun cokmesi genellikle rezonansa baglanir ama gercek mekanizma aeroelastik
flutter'dir — bunlar farkli olgular.
""", """
**Simple harmonic motion (SHM):** arises when the restoring force is proportional and
opposite to displacement (F = -kx). Solution: x(t) = A cos(ωt + φ) with ω = √(k/m).

**Critical property:** the period is **independent of amplitude** (isochronism). Galileo's
discovery of this made pendulum clocks possible. It holds only in the small-angle
approximation (sinθ ≈ θ); at large amplitude a pendulum's period grows.

**Damped oscillation:** F = -kx - bv, with three regimes:
- *Underdamped* (b² < 4mk): oscillation with exponentially decaying amplitude
- *Critically damped* (b² = 4mk): fastest return with no overshoot — how door closers and
  shock absorbers are designed
- *Overdamped:* slow, non-oscillatory return

**Driven oscillation and resonance:** amplitude grows sharply as the driving frequency
approaches the natural one. The less damping, the sharper and more dangerous the resonance.
The Tacoma Narrows collapse is often attributed to resonance, but the actual mechanism was
aeroelastic flutter — a different phenomenon.
""",
  ["x = A cos(ωt + φ)", "ω = √(k/m)", "T = 2π√(m/k)", "T = 2π√(L/g)",
   "E = ½kA²", "ω_d = √(ω₀² - (b/2m)²)", "Q = ω₀m/b"],
  ["0.5 kg kutle 200 N/m yaya bagli: ω = √(200/0.5) = 20 rad/s, T = 0.314 s, f = 3.18 Hz. "
   "Genlik 5 cm ise toplam enerji E = ½·200·0.05² = 0.25 J ve maksimum hiz v = ωA = 1 m/s.",
   "1 m uzunlugunda sarkac: T = 2π√(1/9.81) = 2.006 s. Bu neredeyse tam 2 saniyedir — "
   "'saniye sarkaci' tanimlanirken metre bu iliskiden yararlanilarak dusunulmustur."],
  ["A 0.5 kg mass on a 200 N/m spring: ω = 20 rad/s, T = 0.314 s, f = 3.18 Hz. With 5 cm "
   "amplitude, E = ½kA² = 0.25 J and v_max = ωA = 1 m/s.",
   "A 1 m pendulum has T = 2π√(1/9.81) = 2.006 s — almost exactly two seconds, a relation "
   "considered when the metre was being defined."],
  kw="titresim|harmonik hareket|sarkac|rezonans|sonum|oscillation|shm|pendulum|resonance|damping",
  related="dalga_hareketi|newton_yasalari"),

T("elektrik_devre", "Elektrik Devreleri", "Electric Circuits", """
**Temel buyuklukler:** Akim I = dQ/dt (A), gerilim V (V), direnc R (Ω). Ohm yasasi V = IR
bir dogal yasa degil, **bazi** malzemelerin ampirik ozelligidir (ohmik malzemeler).
Diyot ve lamba filamani ohmik degildir.

**Seri ve paralel:**
- Seri: R_es = ΣR, akim ortak, gerilim bolusur
- Paralel: 1/R_es = Σ1/R, gerilim ortak, akim bolusur
- Kondansator icin tam tersi: seri 1/C_es = Σ1/C, paralel C_es = ΣC

**Kirchhoff yasalari:**
- *Dugum (akim):* Bir dugume giren akim cikana esittir (yuk korunumu)
- *Cevre (gerilim):* Kapali bir cevrede gerilim degisimlerinin toplami sifirdir
  (enerji korunumu)

**RC devresi:** Sarj V(t) = V₀(1 - e^(-t/RC)), desarj V(t) = V₀e^(-t/RC). Zaman sabiti
τ = RC; 5τ sonra islem pratik olarak tamamlanmistir.

**AC devreler:** Empedans kavrami direnci genellestirir. Z_R = R, Z_L = jωL, Z_C = 1/(jωC).
Seri RLC'de rezonans f₀ = 1/(2π√(LC)) — radyo alicisinin istasyon secmesi budur.
""", """
**Basic quantities:** current I = dQ/dt (A), voltage V (V), resistance R (Ω). Ohm's law
V = IR is not a law of nature but an empirical property of **some** materials (ohmic ones).
Diodes and lamp filaments are not ohmic.

**Series and parallel:**
- Series: R_eq = ΣR, shared current, divided voltage
- Parallel: 1/R_eq = Σ1/R, shared voltage, divided current
- Capacitors are the reverse: series 1/C_eq = Σ1/C, parallel C_eq = ΣC

**Kirchhoff's laws:**
- *Junction (current):* current in equals current out (charge conservation)
- *Loop (voltage):* voltage changes around a closed loop sum to zero (energy conservation)

**RC circuit:** charging V(t) = V₀(1 - e^(-t/RC)), discharging V(t) = V₀e^(-t/RC). Time
constant τ = RC; after 5τ the process is practically complete.

**AC circuits:** impedance generalises resistance — Z_R = R, Z_L = jωL, Z_C = 1/(jωC).
A series RLC resonates at f₀ = 1/(2π√(LC)), which is how a radio selects a station.
""",
  ["V = IR", "P = VI = I²R = V²/R", "R_seri = ΣR", "1/R_par = Σ1/R",
   "τ = RC", "Z = √(R² + (X_L - X_C)²)", "f₀ = 1/(2π√(LC))"],
  ["12 V pil, 4 Ω ve 8 Ω seri: I = 12/12 = 1 A. Dirençler uzerindeki gerilimler 4 V ve 8 V. "
   "Paralel baglanirsa R_es = 2.67 Ω, toplam akim 4.5 A olur.",
   "1 kΩ direnc ve 100 µF kondansator: τ = 0.1 s. Kondansatorun %99 dolmasi 5τ = 0.5 s surer. "
   "Bu, basit zamanlayici devrelerin calisma prensibi."],
  ["A 12 V battery with 4 Ω and 8 Ω in series: I = 1 A, with 4 V and 8 V across them. In "
   "parallel R_eq = 2.67 Ω and the total current is 4.5 A.",
   "With 1 kΩ and 100 µF, τ = 0.1 s, so the capacitor reaches 99% in 5τ = 0.5 s — the basis "
   "of simple timer circuits."],
  kw="devre|direnc|kirchhoff|rc devresi|empedans|seri paralel|circuit|resistance|impedance",
  related="maxwell_denklemleri|elektromanyetik_dalga"),

T("olcum_hata", "Olcum, Hata Analizi ve Anlamli Rakamlar", "Measurement, Error Analysis and Significant Figures", """
Deneysel fizigin temelidir; hesap dogru olsa bile hata analizi eksikse sonuc bilimsel degildir.

**Hata turleri:**
- *Rastgele hata:* Tekrarli olcumde sacilma yaratir; ortalama alarak azaltilir (√N ile).
- *Sistematik hata:* Tum olcumleri ayni yone kaydirir; tekrarla azalmaz, ancak
  kalibrasyonla bulunur. En tehlikeli olan budur.

**Belirsizlik yayilimi (bagimsiz degiskenler icin):**
- Toplama/cikarma: δz = √(δx² + δy²) — **mutlak** hatalar toplanir
- Carpma/bolme: δz/z = √((δx/x)² + (δy/y)²) — **bagil** hatalar toplanir
- Us alma z = x^n: δz/z = |n|·δx/x

**Anlamli rakamlar:** Sonuc, en az duyarli girdiden daha duyarli olamaz. Carpma/bolmede
en az anlamli rakam sayisi belirler; toplama/cikarmada en az ondalik basamak sayisi.
Ara hesaplarda fazladan basamak tutun, yalnizca son adimda yuvarlayin.

**Ortalama ve standart hata:** N olcumun ortalamasinin belirsizligi σ/√N'dir. Yani
duyarliligi 10 kat artirmak icin 100 kat fazla olcum gerekir — deney tasariminda bu
karsilastirma kritiktir.
""", """
This is the foundation of experimental physics; a calculation without error analysis is
not a scientific result, however correct the arithmetic.

**Types of error:**
- *Random:* produces scatter in repeated measurements; reduced by averaging (as √N).
- *Systematic:* shifts all measurements the same way; not reduced by repetition, only found
  by calibration. This is the dangerous kind.

**Propagation of uncertainty (independent variables):**
- Addition/subtraction: δz = √(δx² + δy²) — **absolute** errors add in quadrature
- Multiplication/division: δz/z = √((δx/x)² + (δy/y)²) — **relative** errors add
- Powers z = x^n: δz/z = |n|·δx/x

**Significant figures:** a result cannot be more precise than its least precise input. For
multiplication/division the smallest significant-figure count governs; for addition/
subtraction the smallest number of decimal places. Keep extra digits in intermediate steps
and round only at the end.

**Mean and standard error:** the uncertainty of a mean of N measurements is σ/√N. Improving
precision tenfold needs 100× more measurements — a critical trade-off in experiment design.
""",
  ["δz = √(δx² + δy²)", "δz/z = √((δx/x)² + (δy/y)²)", "SE = σ/√N",
   "δz/z = |n|δx/x", "χ² = Σ(y_i - f_i)²/σ_i²"],
  ["Dikdortgen: a = 5.0 ± 0.1 cm, b = 3.0 ± 0.1 cm. Alan A = 15.0 cm². "
   "Bagil hatalar: 0.02 ve 0.0333 → δA/A = √(0.02² + 0.0333²) = 0.0389, "
   "δA = 0.58 cm². Sonuc: A = 15.0 ± 0.6 cm².",
   "Sarkacla g olcumu: T = 2π√(L/g) → g = 4π²L/T². δg/g = √((δL/L)² + (2δT/T)²). "
   "Periyot hatasinin **2 kat** agirlikta olduguna dikkat edin — bu yuzden T'yi 10 salinim "
   "olcup bolerek hassaslastirmak, L'yi daha iyi olcmekten daha etkilidir."],
  ["Rectangle a = 5.0 ± 0.1 cm, b = 3.0 ± 0.1 cm. Area A = 15.0 cm², relative errors 0.02 "
   "and 0.0333 give δA/A = 0.0389, so A = 15.0 ± 0.6 cm².",
   "Measuring g with a pendulum: g = 4π²L/T², so δg/g = √((δL/L)² + (2δT/T)²). Note the period "
   "error carries **twice** the weight — which is why timing 10 swings and dividing beats "
   "measuring L more carefully."],
  kw="hata analizi|belirsizlik|anlamli rakam|olcum|standart sapma|error analysis|uncertainty|significant figures",
  related="matlab_fizik"),

T("matlab_fizik", "Fizikte MATLAB Kullanimi", "Using MATLAB in Physics", """
MATLAB, fizik problemlerinde sayisal cozum, veri analizi ve gorsellestirme icin yaygin
kullanilir. Ucretsiz alternatifi **GNU Octave** neredeyse tam uyumludur.

**Temel araclar:**
- *Vektorlestirme:* Donguler yerine dizi islemleri kullanin. `y = sin(x)` tum diziye
  uygulanir ve dongudan cok daha hizlidir.
- *ODE cozucusu:* `ode45` (genel amac, Runge-Kutta 4-5), `ode15s` (stiff sistemler).
  Ikinci mertebe denklemleri once birinci mertebe sisteme cevirin.
- *Lineer cebir:* `A\\b` ters alip carpmaktan hem hizli hem sayisal olarak daha kararlidir.
  `eig`, `svd`, `lu`, `qr`.
- *Sinyal analizi:* `fft`, `ifft`, `spectrogram`. FFT sonucunu yorumlarken frekans
  eksenini `f = (0:N-1)*fs/N` ile kurun ve tek tarafli spektrumda genligi 2/N ile olceklendirin.
- *Egri uydurma:* `polyfit`/`polyval` (polinom), `lsqcurvefit` (genel dogrusal olmayan),
  `fminsearch` (optimizasyon).
- *Sembolik:* `syms x`, `diff`, `int`, `dsolve`, `solve`, `simplify`.

**Fizikci icin pratik oneriler:**
- Birimleri kodun basinda sabit olarak tanimlayin ve hep SI'de calisin.
- ODE cozerken `odeset('RelTol',1e-8,'AbsTol',1e-10)` ile toleransi sikilastirin; enerji
  korunumunu bir kontrol degiskeni olarak izleyin — cozumun dogrulugunu boyle test edersiniz.
- Uzun simulasyonlarda simplektik integratorler (Verlet, leapfrog) ode45'ten daha iyi
  enerji korur. Gezegen yorungesi gibi problemlerde bu fark belirleyicidir.
""", """
MATLAB is widely used in physics for numerical solution, data analysis and visualisation.
The free alternative **GNU Octave** is nearly fully compatible.

**Core tools:**
- *Vectorisation:* use array operations instead of loops. `y = sin(x)` applies to the whole
  array and is far faster than looping.
- *ODE solvers:* `ode45` (general purpose, Runge-Kutta 4-5) and `ode15s` (stiff systems).
  Convert second-order equations to a first-order system first.
- *Linear algebra:* `A\\b` is both faster and numerically more stable than inverting.
  Also `eig`, `svd`, `lu`, `qr`.
- *Signal analysis:* `fft`, `ifft`, `spectrogram`. When interpreting an FFT, build the
  frequency axis as `f = (0:N-1)*fs/N` and scale a one-sided spectrum by 2/N.
- *Curve fitting:* `polyfit`/`polyval`, `lsqcurvefit`, `fminsearch`.
- *Symbolic:* `syms x`, `diff`, `int`, `dsolve`, `solve`, `simplify`.

**Practical advice for physicists:**
- Define units as constants at the top and work in SI throughout.
- Tighten tolerances with `odeset('RelTol',1e-8,'AbsTol',1e-10)`, and track energy
  conservation as a diagnostic — it is how you test whether the solution is trustworthy.
- For long simulations, symplectic integrators (Verlet, leapfrog) conserve energy far better
  than ode45. For planetary orbits this difference is decisive.
""",
  ["[t,y] = ode45(@(t,y) f(t,y), tspan, y0)", "x = A\\b",
   "Y = fft(y); f = (0:N-1)*fs/N", "p = polyfit(x,y,n)",
   "syms x; int(f,x)"],
  ["Sonumlu harmonik osilator icin ode45: once x'' + 2γx' + ω₀²x = 0 denklemini "
   "y₁ = x, y₂ = x' ile [y₂; -2γy₂ - ω₀²y₁] sistemine cevirin, sonra ode45'e verin.",
   "Bir sinyalin baskin frekansini bulmak: Y = fft(y); P = abs(Y(1:N/2+1))*2/N; "
   "f = (0:N/2)*fs/N; [~,i] = max(P); f(i) — bu, deney verisinden rezonans frekansi "
   "cikarmanin standart yoludur."],
  ["For a damped oscillator with ode45: rewrite x'' + 2γx' + ω₀²x = 0 as the system "
   "[y₂; -2γy₂ - ω₀²y₁] with y₁ = x, y₂ = x', then pass it to ode45.",
   "Finding a signal's dominant frequency: Y = fft(y); P = abs(Y(1:N/2+1))*2/N; "
   "f = (0:N/2)*fs/N; [~,i] = max(P); f(i) — the standard way to extract a resonance "
   "frequency from experimental data."],
  kw="matlab|octave|ode45|fft|sayisal|simulasyon|numerical|simulation|vectorization",
  related="olcum_hata|sayisal_yontemler"),

T("sayisal_yontemler", "Fizikte Sayisal Yontemler", "Numerical Methods in Physics", """
Cogu gercek fizik problemi analitik olarak cozulemez; sayisal yontemler bu yuzden
vazgecilmezdir.

**Kok bulma:** Bisection (yavas ama garantili), Newton-Raphson (hizli, turev gerekir,
kotu baslangicta iraksayabilir), secant (turevsiz Newton).

**Sayisal integral:** Yamuk kurali (O(h²)), Simpson (O(h⁴)), Gauss kuadraturu (duzgun
fonksiyonlar icin cok verimli), Monte Carlo (yuksek boyutta tek pratik secenek —
hata boyuttan bagimsiz olarak N^(-1/2) ile azalir).

**ODE cozucu:** Euler (basit ama kararsiz ve hatali), RK4 (standart is ati),
adaptif adimli RK45. **Stiff** sistemlerde (cok farkli zaman olcekleri) acik yontemler
cok kucuk adim gerektirir; ortuk (implicit) yontem kullanin.

**Simplektik integratorler:** Hamilton sistemleri icin. Velocity-Verlet ve leapfrog,
enerji hatasini biriktirmek yerine sinirli tutar. Molekuler dinamik ve gok mekaniginde
standarttir — RK4 daha dogru gorunse de milyonlarca adimda yorungeyi kaydirir.

**PDE:** Sonlu farklar (basit geometri), sonlu elemanlar (karmasik geometri), spektral
yontemler (periyodik, duzgun cozumler). Kararlilik icin CFL kosulunu (Δt ≤ Δx/v) mutlaka
kontrol edin.

**Genel uyari:** Kayan nokta aritmetiginde iki yakin sayiyi cikarmak (catastrophic
cancellation) anlamli basamaklari yok eder. Ikinci dereceden denklem kokunde bile bu
sorun ortaya cikar; formulu yeniden duzenleyin.
""", """
Most real physics problems have no analytic solution, which makes numerical methods
indispensable.

**Root finding:** bisection (slow but guaranteed), Newton-Raphson (fast, needs derivatives,
can diverge from a poor start), secant (derivative-free Newton).

**Numerical integration:** trapezoid (O(h²)), Simpson (O(h⁴)), Gaussian quadrature (very
efficient for smooth functions), Monte Carlo (the only practical option in high dimensions —
its error falls as N^(-1/2) independent of dimension).

**ODE solvers:** Euler (simple but unstable and inaccurate), RK4 (the standard workhorse),
adaptive RK45. For **stiff** systems (widely separated timescales) explicit methods need
tiny steps; use an implicit method.

**Symplectic integrators:** for Hamiltonian systems. Velocity-Verlet and leapfrog bound the
energy error rather than accumulating it. They are standard in molecular dynamics and
celestial mechanics — RK4 may look more accurate but drifts the orbit over millions of steps.

**PDEs:** finite differences (simple geometry), finite elements (complex geometry), spectral
methods (periodic, smooth solutions). Always check the CFL condition (Δt ≤ Δx/v) for stability.

**General warning:** in floating point, subtracting two nearby numbers (catastrophic
cancellation) destroys significant digits. It bites even in the quadratic formula — rearrange
the expression.
""",
  ["x_{n+1} = x_n - f(x_n)/f'(x_n)", "RK4: k1..k4 agirlikli ortalama",
   "∫ ≈ h/3·(f₀ + 4f₁ + 2f₂ + ... + f_n)", "Δt ≤ Δx/v (CFL)",
   "Verlet: x_{n+1} = 2x_n - x_{n-1} + a_n Δt²"],
  ["Gezegen yorungesi simulasyonunda RK4 ile 10⁶ adim sonra yorunge yavasca spirallesir "
   "(enerji kayar). Ayni problemde velocity-Verlet enerjiyi kucuk bir bant icinde tutar. "
   "Uzun vadeli kararlilik dogrulugun onunde gelir.",
   "10 boyutlu bir integral: 10 nokta/boyut ile kafes yontemi 10¹⁰ degerlendirme ister. "
   "Monte Carlo ile 10⁶ ornek %0.1 hata verir. Bu, istatistiksel fizikte Monte Carlo'nun "
   "neden hakim oldugunu aciklar."],
  ["Simulating a planetary orbit, RK4 slowly spirals after 10⁶ steps as energy drifts, while "
   "velocity-Verlet keeps energy within a small band. Long-term stability beats raw accuracy.",
   "A 10-dimensional integral with 10 points per axis needs 10¹⁰ grid evaluations; Monte Carlo "
   "gets 0.1% error with 10⁶ samples — why it dominates statistical physics."],
  kw="sayisal yontem|runge kutta|monte carlo|sonlu farklar|verlet|numerical methods|integration",
  related="matlab_fizik|olcum_hata"),
]

BY_KEY = {t["key"]: t for t in TOPICS}


def _norm(s):
    s = (s or "").lower()
    for a, b in {"ı": "i", "İ": "i", "ş": "s", "ğ": "g", "ü": "u",
                 "ö": "o", "ç": "c", "â": "a"}.items():
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9\s]", " ", s)


# Her soruda gecen kaliplar; kismi eslesmede sayilmazlar
_SORU_KELIMESI = frozenset("""neden nasil nedir hangi nicin kimdir olur olan
    yapar eder misin nedeni sence lutfen bana beni bunu sunu bunun
    olarak biliyoruz biliyor bilinir anlat ogret acikla aciklar
    why how what which does when""".split())


def search(query, limit=5):
    q = _norm(query)
    qw = set(w for w in q.split() if len(w) > 2)
    qw4 = {w[:4] for w in qw}
    scored = []
    for t in TOPICS:
        score = 0
        for kw in t["kw"]:
            k = _norm(kw).strip()
            if not k:
                continue
            # Alt dizi degil tam kelime eslesmesi (bkz. formulas.search).
            # Sondaki \w{0,3}, Turkce cekim ekine izin verir: "boyut
            # analizi" anahtari "boyut analizini ogret" sorgusunda tam
            # eslesme sayilmiyordu ve konu esigin altinda kaliyordu.
            if re.search(r"(?<!\w)%s\w{0,3}(?!\w)" % re.escape(k), q):
                if len(k) >= 5 or " " in k:
                    score += 30 + len(k)
                elif (_KW_TEK.get(k)
                      and re.search(r"(?<!\w)%s\w{0,1}(?!\w)"
                                    % re.escape(k), q)):
                    # Kisa ama AYIRT EDICI anahtar: "nmr", "qed", "atp"
                    # gibi kisaltmalar tek bir konuda geciyorsa eslesme
                    # uzun bir anahtar kadar guveniliridir. Olculdu: "nmr
                    # nasil calisir" 14 puanda kalip 25 esigini gecemiyordu.
                    # Yalnizca 1 harflik ek toleransi veriyoruz ki kisa
                    # anahtarlar baska kelimelerin icine dusmesin
                    # ("isi" -> "isik").
                    score += 28
                else:
                    score += 12
            else:
                kws = set(k.split())
                if kws and kws <= qw:
                    score += 20
                elif len(kws) >= 2:
                    # KISMI eslesme — formul aramasindaki mekanizmanin
                    # aynisi. Turkce cekim eki yuzunden anahtar cumleye
                    # birebir oturmuyor: "elektronun spini deneysel olarak
                    # nasil biliyoruz" sorusu "elektron spini deney"
                    # anahtarini hic tutmuyordu (olculdu).
                    onemli = [w[:4] for w in kws
                              if len(w) > 3 and w not in _SORU_KELIMESI]
                    if len(onemli) >= 2:
                        tutan = sum(1 for on in onemli if on in qw4)
                        if tutan >= 2 and tutan * 2 >= len(onemli):
                            eksik = len(onemli) - tutan
                            score += max(0, 11 * tutan - 8 * eksik)
        for w in qw:
            if w in _norm(t["tr_title"]) or w in _norm(t["en_title"]):
                score += 12
            if w in _norm(t["tr"][:400]) or w in _norm(t["en"][:400]):
                score += 2
        if score:
            scored.append((score, t))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]


def get(key):
    return BY_KEY.get(key)


def list_topics(lang="tr"):
    return [(t["key"], t["tr_title"] if lang == "tr" else t["en_title"])
            for t in TOPICS]


# ── Ileri kuram ve kilit deneyler ───────────────────────────────────────────
# Olculdu: "Noether teoremini turet" ve "elektronun spini deneysel olarak
# nasil biliniyor" sorulari cevapsiz kaliyordu. Cekirdek bilgi lisans
# mufredatiyla sinirliydi; 28.000 kaynak baglam katiyor ama cekirdegi
# buyutmuyordu. Kuramsal omurga ve fizigin donum noktasi deneyleri ayri
# dosyalarda yazildi ve burada listeye katiliyor.
def _ileri_konulari_kat():
    from .kuram import KURAM_KONULARI
    from .deneyler import DENEY_KONULARI
    from .ileri import ILERI_KONULAR
    from .bilimciler import BILIMCILER
    from .yanbilim import YAN_BILIM_KONULARI
    from .gunluk import GUNLUK_KONULAR
    from .mufredat import MUFREDAT_KONULARI
    from .gecisler import GECIS_KONULARI
    from .turetimler import TURETIM_KONULARI
    var = {t["key"] for t in TOPICS}
    for t in (KURAM_KONULARI + DENEY_KONULARI + ILERI_KONULAR
              + BILIMCILER + YAN_BILIM_KONULARI + GUNLUK_KONULAR
              + MUFREDAT_KONULARI + GECIS_KONULARI
              + TURETIM_KONULARI):
        if t["key"] not in var:
            TOPICS.append(t)
            var.add(t["key"])
    return len(TOPICS)


_ileri_konulari_kat()
# BY_KEY, TOPICS listesi buyumeden once kurulmustu; yenilenmeli.
BY_KEY = {t["key"]: t for t in TOPICS}


def _kisa_anahtar_indeksi():
    """Kisa anahtarlardan hangileri TEK bir konuya ait?"""
    sayim = {}
    for t in TOPICS:
        for kw in t["kw"]:
            k = _norm(kw).strip()
            if k and " " not in k and len(k) < 5:
                sayim[k] = sayim.get(k, 0) + 1
    return {k: True for k, n in sayim.items() if n == 1}


_KW_TEK = _kisa_anahtar_indeksi()

