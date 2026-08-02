# -*- coding: utf-8 -*-
"""Ileri kuram: analitik mekanik, simetriler, alan kurami.

Olculdu ve gorulduu: sistem "Noether teoremini turet" sorusuna
"bu konuda elimde bilgi yok" diyordu. Sebebi acikti — cekirdek bilgi
lisans mufredatiyla sinirliydi; 28.000 kaynak baglam katiyor ama cekirdegi
buyutmuyordu.

Burada eksik olan kuramsal omurga elle yazilir: Lagrange ve Hamilton
formalizmi, en kucuk etki ilkesi, Noether teoremi, simetri-korunum bagi,
alan kurami ve ayar simetrisi. Her konu cekirdek konular gibi
yapilandirilmistir (tanim, bagintilar, cozumlu ornek) ve `knowledge.TOPICS`
listesine katilir.
"""
from .knowledge import T

KURAM_KONULARI = [

T("varyasyon", "En Küçük Etki İlkesi", "Principle of Least Action", """
Klasik mekanik iki farkli ama esdeger dille yazilabilir. Newton dili
kuvvetlerle calisir: cisme etkiyen kuvvetleri topla, F = ma yaz. Varyasyon
dili ise butun yorungeye birden bakar.

**Etki (action):** Bir yorungenin etkisi, Lagrange fonksiyonunun zaman
boyunca integralidir:  S = ∫ L dt.  Burada L = T - V (kinetik eksi
potansiyel enerji).

**Ilke:** Bir cisim, baslangic ve bitis noktalari sabitken, etkiyi DURAGAN
yapan yorungeyi izler (δS = 0). "En kucuk" adi gelenekseldir; dogrusu
duraganliktir — bazen maksimum, cogu zaman minimumdur.

**Neden onemli:** Kuvvet kavramina hic girmeden hareket denklemleri cikar.
Kisitli sistemlerde (sarkac, egik duzlem, donen cisim) Newton dilinde
bilinmeyen tepki kuvvetlerini yazmak zorundasiniz; varyasyon dilinde
kisitlar koordinat seciminde kendiliginden karsilanir.

**Kapsam:** Yalnizca mekanikle sinirli degildir. Optikte Fermat ilkesi
(isik en kisa zamanli yolu izler), genel gorelilikte Einstein-Hilbert
etkisi, parcacik fiziginde Standart Model — hepsi bir etki ilkesinden
turer. Modern fizigin ortak dili budur.
""", """
Classical mechanics can be written in two equivalent languages: Newton's
(forces) and the variational one (the whole path at once). The action is
S = the time integral of the Lagrangian L = T - V, and a body follows the
path that makes the action stationary. Fermat's principle in optics, the
Einstein-Hilbert action in general relativity and the Standard Model all
follow from an action principle.
""",
  eqs=["S = ∫ L dt", "L = T - V", "δS = 0"],
  ex_tr=["Serbest dusen cisim: L = ½mv² - mgy. Euler-Lagrange denklemi "
         "d/dt(∂L/∂v) - ∂L/∂y = 0 verir: m·dv/dt = -mg, yani a = -g. "
         "Newton'un sonucunun aynisi, ama kuvvet cizmeden."],
  ex_en=["Free fall: L = mv²/2 - mgy gives a = -g via Euler-Lagrange."],
  kw="en kucuk etki|etki ilkesi|varyasyon ilkesi|action principle|"
     "least action|lagrange fonksiyonu|fermat ilkesi",
  related="lagrange|hamilton|noether"),

T("lagrange", "Lagrange Mekaniği", "Lagrangian Mechanics", """
Newton mekaniginin kisitli sistemlerde kullanissiz kalmasi uzerine
gelistirilen genel formalizm.

**Genellestirilmis koordinatlar:** Sistemi tanimlayan bagimsiz degiskenler
q₁, q₂, ... (aci, uzunluk, ne uygunsa). Sarkacta tek koordinat yeter: aci θ.
Newton dilinde ip gerilmesini yazmak zorundasiniz; burada gerek yok.

**Lagrange fonksiyonu:** L(q, q̇, t) = T - V

**Euler-Lagrange denklemi:** Her koordinat icin
    d/dt (∂L/∂q̇ᵢ) - ∂L/∂qᵢ = 0
Bu denklemler hareket denklemleridir; Newton yasalarina esdegerdir ama
kisitlari kendiliginden karsilar.

**Doner (cyclic) koordinat:** L bir koordinati acikca icermiyorsa
(∂L/∂qᵢ = 0), ona esleşen genellestirilmis momentum pᵢ = ∂L/∂q̇ᵢ KORUNUR.
Bu, Noether teoreminin en basit halidir.

**Kisitlar:** Holonom kisitlar koordinat seciminde erir. Erimiyorsa
Lagrange carpanlari kullanilir ve carpanlar tam da kisit kuvvetlerini
verir.
""", """
Lagrangian mechanics uses generalized coordinates and L = T - V. The
Euler-Lagrange equations d/dt(dL/dq') - dL/dq = 0 are the equations of
motion, equivalent to Newton's laws but automatically handling constraints.
If a coordinate does not appear in L, its conjugate momentum is conserved.
""",
  eqs=["L = T - V", "d/dt(∂L/∂q̇) - ∂L/∂q = 0", "p = ∂L/∂q̇"],
  ex_tr=["Basit sarkac: T = ½mL²θ̇², V = -mgL·cosθ, yani L = ½mL²θ̇² + mgL·cosθ. "
         "Euler-Lagrange: mL²θ̈ = -mgL·sinθ → θ̈ = -(g/L)·sinθ. "
         "Kucuk acida sinθ ≈ θ olur ve ω = √(g/L) cikar. "
         "Ip gerilmesini hic yazmadik."],
  ex_en=["Simple pendulum: L = mL²θ'²/2 + mgL·cosθ gives θ'' = -(g/L)sinθ."],
  kw="lagrange mekanigi|lagrange denklemi|euler lagrange|"
     "genellestirilmis koordinat|lagrangian|analitik mekanik",
  related="varyasyon|hamilton|noether"),

T("hamilton", "Hamilton Mekaniği", "Hamiltonian Mechanics", """
Lagrange formalizminin, hiz yerine MOMENTUM kullanan esdegeri. Kuantum
mekanigine ve istatistiksel mekanige acilan kapi budur.

**Gecis (Legendre donusumu):** p = ∂L/∂q̇ tanimlanir ve
    H(q, p, t) = Σ p·q̇ - L

**H ne zaman toplam enerjidir?** Otomatik degildir; IKI kosul birden
gerekir: (a) baglar/koordinat donusumu zamandan bagimsiz olmali
(skleronom), (b) potansiyel hiza bagli olmamali. Bu ikisi saglanirsa
H = T + V olur. Aksi halde H yine korunabilir ama toplam enerji
DEGILDIR — donen bir cerceve ya da manyetik alandaki yuk bunun
orneginidir. Ayrica L acikca zamana bagli degilse H korunur; bu ayri
bir ifadedir (dH/dt = -∂L/∂t).

**Hamilton denklemleri:** Ikinci mertebeden tek denklem yerine, birinci
mertebeden IKI denklem:
    q̇ = ∂H/∂p        ṗ = -∂H/∂q

**Faz uzayi:** Sistemin durumu (q, p) ciftiyle bir noktadir; zaman icinde
bu nokta faz uzayinda bir egri cizer. Liouville teoremi, faz uzayi
hacminin korundugunu soyler — istatistiksel mekanigin temeli budur.

**Neden onemli:** Kuantum mekaniginde zaman evrimini Hamilton OPERATORU
yonetir (Schrödinger denklemi: iħ ∂ψ/∂t = Ĥψ). Dikkat: Ĥ, klasik H
fonksiyonunun "karsiligi" degil, KANONIK KUANTUMLAMA ile elde edilen
TEMSILIDIR — H(q,p) ifadesinde q ve p yerine q̂, p̂ operatorleri konur ve
konum gosteriminde Ĥ = -(ħ²/2m)∇² + V(x) cikar. Klasik Poisson parantezi
{A,H}, kuantumda komutatore [Â,Ĥ]/(iħ) donusur.
""", """
Hamiltonian mechanics replaces velocities with momenta via a Legendre
transform: H = Σp·q' - L, usually the total energy. The equations of motion
become first order: q' = dH/dp, p' = -dH/dq. Phase space and Liouville's
theorem follow, and the Hamiltonian carries over to quantum mechanics.
""",
  eqs=["H = Σ p·q̇ - L", "q̇ = ∂H/∂p", "ṗ = -∂H/∂q", "H = T + V"],
  ex_tr=["Yay-kutle: H = p²/(2m) + ½kx². Hamilton denklemleri: "
         "ẋ = p/m ve ṗ = -kx. Ikisini birlestirince mẍ = -kx, "
         "yani basit harmonik hareket. Faz uzayinda yorunge bir elipstir "
         "ve elipsin alani korunur."],
  ex_en=["Mass-spring: H = p²/2m + kx²/2 gives x' = p/m, p' = -kx."],
  kw="hamilton denklemleri nedir|hamilton equations|hamiltons equations|hamilton's equations|hamiltonian mechanics|hamilton mekanigi|hamilton denklemleri|faz uzayi|hamiltonian|"
     "poisson parantezi|legendre donusumu|liouville",
  related="lagrange|varyasyon|kuantum_temelleri"),

T("noether", "Noether Teoremi", "Noether's Theorem", """
Fizigin en derin sonuclarindan biri: **her surekli simetri bir korunum
yasasi dogurur.** Emmy Noether 1918'de kanitladi.

**Ifade:** Etki (S = ∫L dt) surekli bir donusum altinda degismiyorsa, bu
donusuma esleşen bir buyukluk zamanla korunur.

**Uc temel ornek:**

| Simetri | Korunan buyukluk |
|---|---|
| Zamanda oteleme (yasalar dun de bugun de ayni) | **Enerji** |
| Uzayda oteleme (yasalar burada da orada da ayni) | **Momentum** |
| Donme (yasalar yonden bagimsiz) | **Acisal momentum** |

**Turetimin fikri:** q → q + εδq donusumu altinda L degismiyorsa
(δL = 0), Euler-Lagrange denklemi kullanilarak

    d/dt ( ∂L/∂q̇ · δq ) = 0

elde edilir. Parantez icindeki buyukluk KORUNUR. Ozel hal: L koordinati
acikca icermiyorsa δq = 1 alinir ve p = ∂L/∂q̇ korunur.

**Neden onemli:** Korunum yasalari artik "deneyle bulunmus kurallar" degil,
simetrilerin zorunlu sonucudur. Modern fizikte yon budur: once simetri
secilir, korunan buyuklukler ve etkilesimler ondan tureor. Ayar
simetrisinden elektrik yuku korunumu, renk simetrisinden guclu etkilesim
bu sekilde cikar.
""", """
Noether's theorem: every continuous symmetry of the action yields a
conserved quantity. Time translation gives energy, space translation gives
momentum, rotation gives angular momentum. Conservation laws are therefore
consequences of symmetry, not independent empirical rules.
""",
  eqs=["δS = 0 → d/dt(∂L/∂q̇ · δq) = 0",
       "zaman otelemesi → enerji korunumu",
       "uzay otelemesi → momentum korunumu",
       "donme simetrisi → acisal momentum korunumu"],
  ex_tr=["Merkezi kuvvet alaninda (V yalnizca r'ye bagli) L, φ acisini "
         "acikca icermez. O halde p_φ = mr²φ̇ korunur — bu acisal "
         "momentumdur. Kepler'in 'esit zamanda esit alan' yasasi tam olarak "
         "bu korunumun geometrik ifadesidir."],
  ex_en=["In a central field L does not contain the angle φ, so p_φ = mr²φ' "
         "is conserved: this is angular momentum, and Kepler's equal-area "
         "law is its geometric statement."],
  kw="noether|noether teoremi|simetri korunum|surekli simetri|"
     "korunum yasasi neden|symmetry conservation",
  related="lagrange|varyasyon|hamilton"),

T("simetri", "Simetriler ve Korunum Yasaları", "Symmetries and Conservation", """
Fizikte simetri, "bir seyi degistirdiginizde yasalarin degismemesi"
demektir. Modern fizigin duzenleyici ilkesi budur.

**Surekli simetriler** (Noether teoremi gecerlidir):
- Zamanda oteleme → enerji korunumu
- Uzayda oteleme → momentum korunumu
- Donme → acisal momentum korunumu
- Ayar (gauge) simetrisi → yuk korunumu

**Kesikli simetriler** (korunum yasasi vermez ama secim kurali koyar):
- **P (parite):** uzayin ayna goruntusu. Zayif etkilesim pariteyi BOZAR
  (Wu deneyi, 1956) — bu, fizigin en sasirtici deneysel sonuclarindandir.
- **C (yuk esleniligi):** parcacik ↔ antiparcacik.
- **T (zaman tersinmesi):** filmi geriye sarma.
- **CPT:** ucunun birlikte uygulanmasi her yerel kuantum alan kuraminda
  korunur; bu bir teoremdir.

**Kirilmis simetri:** Yasalar simetrik oldugu halde COZUM simetrik
olmayabilir. Miknatis sogudukca belli bir yonu "secer" — yasalarda o yon
ayricalikli degildi. Higgs mekanizmasi da boyle bir kendiliginden simetri
kirilmasidir ve parcaciklara kutle kazandirir.
""", """
Symmetry means the laws stay the same under a transformation. Continuous
symmetries give conservation laws (Noether); discrete ones (P, C, T) give
selection rules. Parity is violated by the weak interaction (Wu, 1956).
Spontaneous symmetry breaking — laws symmetric but the solution not — is
behind magnetism and the Higgs mechanism.
""",
  eqs=["CPT korunur", "zayif etkilesimde P bozulur"],
  ex_tr=["Bir kristal, 90° donme altinda ayni gorunuyorsa dorttl simetriye "
         "sahiptir; bu, izinli fonon modlarini ve optik ozelliklerini "
         "belirler. Simetri, hangi gecislerin YASAK oldugunu soyler."],
  ex_en=["Crystal symmetry fixes which phonon modes and optical transitions "
         "are allowed."],
  kw="simetri|parite|cpt|simetri kirilmasi|kendiliginden simetri|"
     "ayar simetrisi|gauge|symmetry breaking",
  related="noether|alan_kurami"),

T("alan_kurami", "Alan Kuramına Giriş", "Introduction to Field Theory", """
Parcacik yerine ALAN temel nesnedir: uzayin her noktasinda tanimli bir
buyukluk. Elektromanyetik alan, kuantumlandiginda fotonlar olarak gorunur.

**Klasik alan kurami:** Lagrange yogunlugu ℒ(φ, ∂φ) yazilir, etki
S = ∫ℒ d⁴x olur ve alan denklemleri yine Euler-Lagrange'dan cikar.
Maxwell denklemleri boyle turetilebilir.

**Kuantum alan kurami (KAK):** Alanlar operator olur. Parcaciklar alanin
uyarilmalaridir — "elektron" dedigimiz sey elektron alaninin bir
kuantumudur. Parcacik sayisi sabit degildir; yaratilip yok edilebilir.
Antimadde bu cercevede zorunlu bir sonuctur.

**Ayar (gauge) ilkesi:** Yerel bir faz simetrisi dayatirsaniz, etkilesimi
tasiyan alan KENDILIGINDEN ortaya cikar. U(1) simetrisi elektromanyetizmayi,
SU(2)×U(1) elektrozayif kurami, SU(3) guclu etkilesimi verir. Standart
Model bu uc simetrinin uzerine kuruludur.

**Renormalizasyon:** Hesaplarda cikan sonsuzluklar, olculebilir
buyukluklerin yeniden tanimlanmasiyla giderilir. Bu bir hile degildir:
kuram, hangi olcekte bakildigina gore "kosan" sabitler ongorur ve bu
kosma deneyle dogrulanmistir.
""", """
In field theory the field is fundamental; particles are its excitations.
The gauge principle — demanding local phase symmetry — generates the
interaction carriers: U(1) gives electromagnetism, SU(2)xU(1) the
electroweak theory, SU(3) the strong force. Renormalization makes the
infinities harmless and predicts running couplings, confirmed by experiment.
""",
  eqs=["S = ∫ ℒ d⁴x", "U(1) → elektromanyetizma", "SU(3) → guclu etkilesim"],
  ex_tr=["Elektromanyetik alan icin ℒ = -¼F_{μν}F^{μν} - j^μA_μ yazilir; "
         "Euler-Lagrange denklemleri dogrudan Maxwell denklemlerini verir. "
         "Yani Maxwell yasalari bir simetri ve bir etki ilkesinden cikar."],
  ex_en=["From ℒ = -F²/4 - jA the Euler-Lagrange equations give Maxwell's "
         "equations."],
  kw="alan kurami|kuantum alan kurami|qft|ayar kurami|gauge theory|"
     "standart model|renormalizasyon|field theory",
  related="simetri|noether|kuantum_temelleri"),

T("istatistik_topluluk", "İstatistiksel Topluluklar", "Statistical Ensembles", """
Termodinamik, makroskobik buyuklukleri (P, V, T) iliskilendirir ama
NEDENINI soylemez. Istatistiksel mekanik, bunlari 10²³ parcacigin
davranisindan turer.

**Mikrodurum / makrodurum:** Makrodurum (P, V, T) sayisiz mikrodurumla
gerceklestirilebilir. Entropi, bu sayinin logaritmasidir: S = k·lnΩ.

**Topluluklar:**
- **Mikrokanonik** (E, V, N sabit): yalitilmis sistem. Tum erisebilir
  mikrodurumlar esit olasilikli.
- **Kanonik** (T, V, N sabit): isi banyosuyla temasta. Bir durumun
  olasiligi P ∝ e^(-E/kT) — Boltzmann dagilimi.
- **Buyuk kanonik** (T, V, μ sabit): parcacik alisverisi de var.

**Bolusum fonksiyonu:** Z = Σ e^(-Eᵢ/kT). Butun termodinamik buyuklukler
Z'den turetilir: F = -kT·lnZ, ⟨E⟩ = -∂lnZ/∂β, S = -∂F/∂T.
Z bilinirse sistem hakkinda bilinmesi gereken her sey bilinir.

**Kuantum istatistigi:** Ayirt edilemez parcaciklar icin dagilim degisir:
tam sayili spinliler (bozonlar) Bose-Einstein, yari tam sayili spinliler
(fermiyonlar) Fermi-Dirac dagilimina uyar. Pauli dislama ilkesi ikincisinin
dogrudan sonucudur.
""", """
Statistical mechanics derives thermodynamics from microstates. Entropy is
S = k lnΩ; the canonical ensemble gives the Boltzmann factor e^(-E/kT), and
the partition function Z encodes everything: F = -kT lnZ. Indistinguishable
particles follow Bose-Einstein or Fermi-Dirac statistics.
""",
  eqs=["S = k·lnΩ", "P ∝ e^(-E/kT)", "Z = Σ e^(-Eᵢ/kT)", "F = -kT·lnZ"],
  ex_tr=["Iki durumlu sistem (enerjiler 0 ve ε): Z = 1 + e^(-ε/kT). "
         "Ortalama enerji ⟨E⟩ = ε/(e^(ε/kT) + 1). Yuksek sicaklikta iki "
         "durum esit dolar (⟨E⟩ → ε/2), dusuk sicaklikta sistem taban "
         "durumunda donar (⟨E⟩ → 0)."],
  ex_en=["Two-level system: Z = 1 + e^(-ε/kT), giving ⟨E⟩ = ε/(e^(ε/kT)+1)."],
  kw="istatistiksel mekanik|topluluk|kanonik|bolusum fonksiyonu|"
     "partition function|boltzmann dagilimi|mikrodurum|ensemble",
  related="termodinamik|kuantum_temelleri"),
]
