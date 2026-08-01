# -*- coding: utf-8 -*-
"""TURETIMLER (ikinci parti): kuantum formalizmi ve ileri konular.

turetimler.py ile ayni kural: her madde bir ISPATTIR, formul karti
degil. Atlanan adim yok; "gosterilebilir ki" demiyoruz.

Bu parti, 20 soruluk kuramsal olcumde bos kalan konulari kapatir:
Fourier donusumu, Hermit operatorler, grup/faz hizi, Dirac gosterimi,
merdiven operatorleri, Klein-Gordon/Dirac, minimal baglasim, yol
integrali, Pauli matrisleri ve WKB.
"""
from .knowledge import T

TURETIM2_KONULARI = [

T("fourier_momentum", "Konum ve Momentum Uzayı: Fourier Dönüşümü",
  "Position and Momentum Space: the Fourier Transform", """
ψ(x) parçacığın konum hakkındaki bilgisini taşır. Momentum hakkındaki
bilgi nerede? Aynı fonksiyonun içinde — Fourier dönüşümüyle okunur.

**1. Momentum özdurumları.**
p̂ = −iħ ∂/∂x operatörünün özfonksiyonlarını arayalım:
    −iħ ∂u_p/∂x = p·u_p  ⇒  u_p(x) = (1/√(2πħ))·e^(ipx/ħ)
Öndeki sabit normlamadan gelir: ⟨u_p'|u_p⟩ = δ(p − p').

**2. Açılım.**
{u_p} tam bir küme oluşturur, yani her ψ(x) bunların üstüne yazılabilir:
    ψ(x) = (1/√(2πħ)) ∫ φ(p)·e^(ipx/ħ) dp
Katsayı fonksiyonu φ(p), ψ'nin momentum uzayındaki hâlidir.

**3. Ters dönüşüm.**
İki tarafı e^(−ip'x/ħ) ile çarpıp x üzerinden integre edelim ve
    ∫ e^(i(p−p')x/ħ) dx = 2πħ·δ(p − p')
bağıntısını kullanalım:
    **φ(p) = (1/√(2πħ)) ∫ ψ(x)·e^(−ipx/ħ) dx**
İki fonksiyon birbirinin Fourier eşidir. Bilgi aynıdır, gösterim farklı.

**4. Parseval: olasılık korunur.**
    ∫|ψ(x)|² dx = ∫|φ(p)|² dp
Yani |φ(p)|², momentumu p civarında bulma olasılık yoğunluğudur —
Born kuralının momentum uzayındaki karşılığı.

**5. Fiziksel anlam ve belirsizlik.**
Fourier analizinin bilinen bir özelliği: bir fonksiyon dar ise dönüşümü
geniştir. σ_x·σ_k ≥ 1/2 (matematiksel bir teoremdir). p = ħk koyunca
    Δx·Δp ≥ ħ/2
**Belirsizlik ilkesi buradan da çıkar** — dalga tanımının kaçınılmaz
sonucudur, ölçüm aletinin kusuru değil. Keskin momentumlu bir durum
(tek düzlem dalga) tüm uzaya yayılır; keskin konumlu bir durum (delta)
tüm momentumları içerir.
""", """
The momentum eigenfunctions of p = -i hbar d/dx are plane waves
u_p = exp(ipx/hbar)/sqrt(2 pi hbar). Expanding psi in them gives
psi(x) = int phi(p) u_p dp, and multiplying by a conjugate plane wave and
integrating inverts it: phi(p) = int psi(x) exp(-ipx/hbar) dx /
sqrt(2 pi hbar). Parseval's theorem shows the norms agree, so |phi|^2 is
the momentum probability density. Because a narrow function has a wide
transform, sigma_x sigma_k >= 1/2, i.e. dx dp >= hbar/2.
""",
  eqs=["u_p(x) = e^(ipx/ħ)/√(2πħ)",
       "ψ(x) = (1/√(2πħ))∫φ(p)e^(ipx/ħ)dp",
       "φ(p) = (1/√(2πħ))∫ψ(x)e^(−ipx/ħ)dx",
       "∫|ψ|²dx = ∫|φ|²dp"],
  ex_tr=["Gauss paketi ψ(x) ∝ e^(−x²/2a²) için φ(p) ∝ e^(−a²p²/2ħ²) — "
         "yine Gauss. σ_x = a/√2, σ_p = ħ/(a√2) ve çarpımları tam ħ/2. "
         "Gauss, minimum belirsizlik durumudur."],
  ex_en=["A Gaussian transforms into a Gaussian with sigma_x sigma_p = hbar/2."],
  kw="fourier donusumu dalga fonksiyonu|momentum uzayi dalga fonksiyonu|"
     "konum momentum uzayi donusum|momentum temsili|"
     "fourier ile momentum uzayi|phi p psi x donusum|"
     "fourier transform wave function|momentum space representation",
  related="belirsizlik_ispat|born_kurali|kuantum_formalizm"),

T("hermit_operator", "Hermit Operatörler ve Gerçel Özdeğerler",
  "Hermitian Operators and Real Eigenvalues", """
Ölçtüğümüz her şey gerçel bir sayıdır. Bu basit gerçek, gözlenebilirleri
temsil eden operatörlerin biçimini belirler.

**1. Tanım.**
Â operatörü Hermit (kendine eş) ise, her ψ, φ için
    ⟨φ|Âψ⟩ = ⟨Âφ|ψ⟩
Integral biçiminde: ∫φ*(Âψ)dx = ∫(Âφ)*ψ dx. Kısaca Â† = Â.

**2. Özdeğerler GERÇELDIR — ispat.**
Âψ = aψ olsun (ψ ≠ 0, normlu). Hermitlik tanımında φ = ψ alalım:
    ⟨ψ|Âψ⟩ = ⟨Âψ|ψ⟩
Sol taraf: ⟨ψ|aψ⟩ = a⟨ψ|ψ⟩ = a.
Sağ taraf: ⟨aψ|ψ⟩ = a*⟨ψ|ψ⟩ = a*.
O hâlde **a = a\\***, yani a gerçeldir. ∎

**3. Farklı özdeğerlerin özdurumları DİKTİR.**
Âψ₁ = a₁ψ₁, Âψ₂ = a₂ψ₂ ve a₁ ≠ a₂ olsun.
    ⟨ψ₂|Âψ₁⟩ = a₁⟨ψ₂|ψ₁⟩
    ⟨Âψ₂|ψ₁⟩ = a₂*⟨ψ₂|ψ₁⟩ = a₂⟨ψ₂|ψ₁⟩   (a₂ gerçel)
Hermitlik ikisini eşitler:
    (a₁ − a₂)⟨ψ₂|ψ₁⟩ = 0  ⇒  ⟨ψ₂|ψ₁⟩ = 0
Bu yüzden özdurumlar bir DIK TABAN kurar ve her durum onların üstüne
açılabilir. Ölçüm sonuçlarının bir "tam liste" oluşturmasının sebebi budur.

**4. Beklenen değer de gerçeldir.**
⟨Â⟩ = ⟨ψ|Âψ⟩ = ⟨Âψ|ψ⟩ = ⟨ψ|Âψ⟩* ⇒ ⟨Â⟩ gerçel.

**5. Örnek: p̂ neden Hermit?**
p̂ = −iħ∂/∂x için kısmi integrasyon:
    ∫φ*(−iħ ψ')dx = [−iħφ*ψ] + ∫(−iħφ')*ψ dx
ψ, φ sonsuzda sıfıra gittiğinden sınır terimi düşer ve eşitlik sağlanır.
**Sınır terimi kritiktir**: sonlu bir aralıkta uygun sınır koşulu
konmazsa p̂ Hermit OLMAZ — bu, kutu içindeki parçacıkta momentumun
neden dikkatli ele alınması gerektiğini açıklar.
""", """
Observables are real, and that fixes the form of their operators.
A is Hermitian if <phi|A psi> = <A phi|psi>. Setting phi = psi for an
eigenstate gives a = a*, so eigenvalues are real. For distinct eigenvalues,
(a1 - a2)<psi2|psi1> = 0 forces orthogonality, so eigenstates form a
complete orthogonal basis. Integration by parts shows p = -i hbar d/dx is
Hermitian provided the boundary term vanishes.
""",
  eqs=["Â† = Â", "⟨φ|Âψ⟩ = ⟨Âφ|ψ⟩", "a = a*", "⟨ψ₂|ψ₁⟩ = 0 (a₁≠a₂)"],
  ex_tr=["Ĥ = −(ħ²/2m)∇² + V Hermit'tir (V gerçelse). Bu yüzden enerji "
         "özdeğerleri gerçeldir ve özdurumlar diktir; sonsuz kuyudaki "
         "sin(nπx/L) fonksiyonlarının birbirine dik olması bunun sonucudur."],
  ex_en=["H = -(hbar^2/2m) lap + V is Hermitian for real V, so energies are "
         "real and eigenstates orthogonal."],
  kw="hermit operator|hermitsel operator|kendine es operator|"
     "ozdegerler neden reel|gozlenebilir hermit olmali|"
     "hermit ozdeger ispat|dik ozdurumlar|"
     "hermitian operator|real eigenvalues proof|self-adjoint",
  related="kuantum_formalizm|born_kurali|belirsizlik_ispat"),

T("grup_faz_hizi", "Serbest Parçacık, Grup Hızı ve Faz Hızı",
  "Free Particle, Group Velocity and Phase Velocity", """
Serbest parçacığın dalga fonksiyonu ışıktan hızlı bir "faz hızı" verir.
Çelişki değildir; parçacık faz hızıyla değil GRUP hızıyla gider.

**1. Serbest parçacık çözümü.**
V = 0 için zamandan bağımsız Schrödinger:
    −(ħ²/2m)ψ'' = Eψ  ⇒  ψ = A e^(ikx),  E = ħ²k²/2m
Zaman çarpanıyla birlikte:
    Ψ(x,t) = A e^(i(kx − ωt)),  ħω = E ⇒ **ω(k) = ħk²/2m**
Bu, dağılım (dispersiyon) bağıntısıdır ve doğrusal DEĞİLDİR.

**2. Faz hızı.**
Sabit faz noktası: kx − ωt = sabit ⇒
    v_faz = ω/k = ħk/2m = **p/2m = v/2**
Klasik hızın yarısı! Üstelik tek bir düzlem dalga her yerde aynı
genliktedir — hiçbir yere "yerleşmiş" değildir, dolayısıyla bir
parçacığı temsil edemez.

**3. Dalga paketi ve grup hızı.**
Gerçek bir parçacık, k₀ çevresinde dar bir dağılımın üst üste
binmesidir:
    Ψ(x,t) = ∫ φ(k) e^(i(kx − ω(k)t)) dk
ω(k)'yi k₀ çevresinde açalım:
    ω(k) ≈ ω₀ + (dω/dk)|₀ (k − k₀) + ...
Yerine koyup düzenleyince paketin ZARFI (x − (dω/dk)t) biçiminde
ilerler. Yani zarfın hızı:
    **v_grup = dω/dk**

**4. Grup hızı klasik hıza EŞITTIR.**
ω = ħk²/2m için
    v_grup = dω/dk = ħk/m = p/m = **v_klasik** ∎
Daha genel olarak ω = E/ħ ve k = p/ħ ile
    v_grup = dω/dk = dE/dp
Klasik mekanikte de dE/dp = v'dir (E = p²/2m). Kuantum dalga paketi,
klasik parçacığın hızıyla gider — Ehrenfest teoreminin dalga dilindeki
karşılığı budur.

**5. Yayılma.** İkinci terim (d²ω/dk²) sıfır olmadığı için paket
zamanla GENİŞLER. Bu, serbest parçacığın konumunun zamanla daha da
belirsizleşmesi demektir.
""", """
A free particle gives psi = A exp(i(kx - wt)) with w = hbar k^2 / 2m.
The phase velocity w/k = p/2m is half the classical speed, and a single
plane wave is spread over all space, so it cannot represent a particle.
A wave packet built around k0 moves with the group velocity dw/dk = hbar
k/m = p/m, which equals the classical speed. More generally
v_group = dE/dp, matching classical mechanics. The second derivative of
w(k) makes the packet spread with time.
""",
  eqs=["ω(k) = ħk²/2m", "v_faz = ω/k = v/2", "v_grup = dω/dk = ħk/m = v",
       "v_grup = dE/dp"],
  ex_tr=["Elektron 1×10⁶ m/s ile gidiyorsa k = mv/ħ = 8,6×10⁹ 1/m. "
         "Faz hızı 5×10⁵ m/s (yarısı), grup hızı 1×10⁶ m/s — "
         "parçacığın gerçek hızı."],
  ex_en=["For an electron at 1e6 m/s the phase velocity is half that; the "
         "group velocity equals 1e6 m/s."],
  kw="grup hizi faz hizi|serbest parcacik cozumu|dispersiyon bagintisi|"
     "grup hizi klasik hiza esit|dalga paketi hizi|faz hizi neden yarisi|"
     "group velocity phase velocity|free particle solution|wave packet",
  related="kanonik_kuantumlama|klasik_limit|fourier_momentum"),

T("dirac_gosterim", "Dirac Gösterimi: Ket, Bra ve Matris Karşılıkları",
  "Dirac Notation: kets, bras and their matrix form", """
Dirac gösterimi bir kısaltma değil, bir DÜŞÜNME biçimidir: durumu
gösterimden (konum mu momentum mu) ayırır.

**1. Ket ve bra.**
|ψ⟩ bir durumdur — bir Hilbert uzayı vektörü. ⟨ψ| ise onun eşleniği
(dual vektör). Sonlu boyutta:
    |ψ⟩ = (c₁, c₂, ..., cₙ)ᵀ   (sütun)
    ⟨ψ| = (c₁*, c₂*, ..., cₙ*)  (satır, eşlenik transpoze)

**2. İç çarpım = satır × sütun.**
    ⟨φ|ψ⟩ = Σᵢ dᵢ* cᵢ   (bir SAYI, genelde karmaşık)
Özellikler: ⟨φ|ψ⟩ = ⟨ψ|φ⟩*, ⟨ψ|ψ⟩ ≥ 0. Norm: ‖ψ‖ = √⟨ψ|ψ⟩ = 1.
Sürekli durumda ⟨φ|ψ⟩ = ∫φ*(x)ψ(x)dx.

**3. Dış çarpım = sütun × satır = MATRIS.**
    |ψ⟩⟨φ| = matris, elemanları (|ψ⟩⟨φ|)ᵢⱼ = cᵢ dⱼ*
Bu bir OPERATÖRDÜR: |ψ⟩⟨φ| ile |χ⟩'ye etki edince ⟨φ|χ⟩·|ψ⟩ verir.

**4. Tamlık bağıntısı — en çok kullanılan araç.**
{|n⟩} dik-normlu tam bir taban ise:
    **Σₙ |n⟩⟨n| = Î**
Bunu istediğiniz yere sokabilirsiniz. Örneğin:
    |ψ⟩ = Î|ψ⟩ = Σₙ |n⟩⟨n|ψ⟩ = Σₙ cₙ|n⟩,  cₙ = ⟨n|ψ⟩
Yani açılım katsayısı bir iç çarpımdır. Konum tabanında
    ψ(x) = ⟨x|ψ⟩
— dalga fonksiyonu, durumun konum tabanındaki BILESENIDIR.

**5. Operatörün matris elemanları.**
    Aₘₙ = ⟨m|Â|n⟩
Â|ψ⟩ = Σₘ (Σₙ Aₘₙ cₙ)|m⟩. Yani operatörün etkisi, matris çarpımıdır.
Hermitlik matris dilinde: Aₘₙ = Aₙₘ*.

**6. Somut örnek — spin-1/2.**
Taban: |↑⟩ = (1,0)ᵀ, |↓⟩ = (0,1)ᵀ.
    ⟨↑|↓⟩ = 0 (dik), ⟨↑|↑⟩ = 1
    |↑⟩⟨↑| = [[1,0],[0,0]] — yukarı spine izdüşüm operatörü
    Ŝ_z = (ħ/2)[[1,0],[0,−1]]
Durum |ψ⟩ = α|↑⟩ + β|↓⟩ için ⟨Ŝ_z⟩ = (ħ/2)(|α|² − |β|²).
""", """
Dirac notation separates the state from its representation. A ket is a
column vector, a bra its conjugate transpose. The inner product <phi|psi>
is a number; the outer product |psi><phi| is a matrix, i.e. an operator.
The completeness relation sum |n><n| = I lets one expand any state, and
psi(x) = <x|psi> shows the wave function is just the component in the
position basis. Operators act as matrices with elements A_mn = <m|A|n>.
For spin-1/2 the basis is (1,0) and (0,1), with S_z = (hbar/2) diag(1,-1).
""",
  eqs=["⟨φ|ψ⟩ = Σ dᵢ*cᵢ", "|ψ⟩⟨φ| (operatör)", "Σₙ|n⟩⟨n| = Î",
       "ψ(x) = ⟨x|ψ⟩", "Aₘₙ = ⟨m|Â|n⟩"],
  ex_tr=["|ψ⟩ = (1/√2)(|↑⟩ + |↓⟩) durumunda ⟨Ŝ_z⟩ = (ħ/2)(1/2 − 1/2) = 0. "
         "Ölçüm ±ħ/2 verir ama ortalama sıfırdır — süperpozisyonun anlamı."],
  ex_en=["For an equal superposition <S_z> = 0 although each measurement "
         "gives +-hbar/2."],
  kw="dirac gosterimi|ket bra|bra ket notasyonu|ic carpim dis carpim|"
     "tamlik bagintisi|operator matris elemani|durum vektoru gosterim|"
     "dirac notation|bra-ket|completeness relation|outer product",
  related="kuantum_formalizm|hermit_operator|pauli_su2"),

T("merdiven_operator", "Kuantum Harmonik Osilatör ve Merdiven Operatörleri",
  "Quantum Harmonic Oscillator and Ladder Operators", """
Klasik osilatör her enerjiyi alabilir. Kuantum osilatörde enerji
basamaklıdır — ve bunu diferansiyel denklem çözmeden, yalnızca cebirle
göstermek mümkündür.

**1. Klasik hatırlatma.**
mẍ = −kx ⇒ x(t) = A cos(ωt + φ), ω = √(k/m). Enerji E = ½kA²:
genlik sürekli olduğu için enerji de süreklidir.

**2. Kuantum Hamiltonyeni.**
    Ĥ = p̂²/2m + ½mω²x̂²

**3. Merdiven operatörlerini tanımla.**
    â  = √(mω/2ħ)·(x̂ + i p̂/(mω))      (yok etme)
    â† = √(mω/2ħ)·(x̂ − i p̂/(mω))      (yaratma)
[x̂,p̂] = iħ kullanarak komütatörü hesaplayalım:
    [â, â†] = (mω/2ħ)·(i/(mω))·(−[x̂,p̂] + [p̂,x̂])·... = **1**

**4. Hamiltonyeni yeniden yaz.**
â†â çarpımını açıp [x̂,p̂] = iħ'yi kullanınca:
    â†â = Ĥ/(ħω) − 1/2  ⇒  **Ĥ = ħω(â†â + ½) = ħω(N̂ + ½)**
N̂ = â†â "sayı operatörü"dür.

**5. Merdiven bağıntıları — ispatın kalbi.**
    [Ĥ, â†] = ħω â†,   [Ĥ, â] = −ħω â
Ĥ|n⟩ = E|n⟩ ise:
    Ĥ(â†|n⟩) = (âĤ† + ħωâ†)|n⟩ = (E + ħω)(â†|n⟩)
Yani â†|n⟩ de bir özdurumdur, enerjisi **ħω daha yüksek**. Aynı şekilde
â|n⟩ enerjiyi ħω düşürür. Basamaklar ħω aralıklıdır.

**6. Neden AYRIK — taban durumu zorunluluğu.**
⟨n|â†â|n⟩ = ‖â|n⟩‖² ≥ 0 olduğundan E ≥ ħω/2: enerji sınırsız
düşemez. O hâlde merdivenin bir ALT BASAMAĞI olmalı; öyle bir |0⟩
vardır ki
    â|0⟩ = 0
Bu koşul E₀ = ħω/2 verir. Yukarıya â† ile tırmanınca:
    **Eₙ = ħω(n + ½),  n = 0,1,2,...**
Ayrıklığın sebebi budur: aşağıdan sınırlı bir merdiven, tam sayı
basamaklar zorunlu kılar. ∎

**7. Sıfır nokta enerjisi.** E₀ = ħω/2 ≠ 0. Klasikte parçacık dipte
durabilir; kuantumda duramaz, çünkü hem x hem p keskin sıfır olsaydı
belirsizlik ilkesi bozulurdu.
""", """
The quantum oscillator's spectrum follows from algebra alone. Define
a = sqrt(m w/2 hbar)(x + i p/(m w)) and its adjoint; [x,p] = i hbar gives
[a, a+] = 1 and H = hbar w (a+ a + 1/2). From [H, a+] = hbar w a+ it
follows that a+ raises the energy by hbar w and a lowers it. Since
<n|a+a|n> >= 0 the energy is bounded below, so a lowest state with
a|0> = 0 must exist, fixing E0 = hbar w/2 and E_n = hbar w (n + 1/2).
Discreteness comes from a ladder bounded below.
""",
  eqs=["Ĥ = p̂²/2m + ½mω²x̂²", "[â, â†] = 1", "Ĥ = ħω(â†â + ½)",
       "[Ĥ, â†] = ħω â†", "Eₙ = ħω(n + ½)"],
  ex_tr=["ω = 10¹⁴ rad/s olan bir molekül titreşimi için "
         "E₀ = ħω/2 = 1,055e-34·1e14/2 = 5,3×10⁻²¹ J ≈ 0,033 eV. "
         "Basamak aralığı ħω = 0,066 eV — kızılötesi bölge, bu yüzden "
         "titreşimler IR spektroskopisiyle görülür."],
  ex_en=["A molecular vibration with w = 1e14 rad/s has spacing hbar w "
         "= 0.066 eV, in the infrared."],
  kw="merdiven operatorleri|yaratma yok etme operatoru|"
     "kuantum harmonik osilator turet|enerji seviyeleri neden ayrik|"
     "a dagger operator|sifir nokta enerjisi|osilator cebirsel cozum|"
     "ladder operators|creation annihilation|quantum harmonic oscillator",
  related="kuantum_formalizm|belirsizlik_ispat|kanonik_kuantumlama"),

T("klein_gordon_dirac", "Görelilikçi Denklemler: Klein-Gordon ve Dirac",
  "Relativistic Equations: Klein-Gordon and Dirac", """
Schrödinger denklemi göreli değildir: zamanda birinci, uzayda ikinci
mertebedendir. Bu asimetri Lorentz değişmezliğiyle bağdaşmaz.

**1. İlk deneme neden başarısız?**
Göreli enerji E² = p²c² + m²c⁴. Karekök alıp operatör yapmak
    Ĥ = √(p̂²c² + m²c⁴)
denenirse, karekök içindeki ∇² sonsuz mertebeli bir seri verir; yerel
olmayan (non-local) bir denklem çıkar ve uzay-zaman simetrisi görünmez.

**2. Klein-Gordon: kareyi al.**
E → iħ∂/∂t, p → −iħ∇ koyup KARELI ifadeyi kullanalım:
    −ħ²∂²ψ/∂t² = −ħ²c²∇²ψ + m²c⁴ψ
    ⇒ **(□ + m²c²/ħ²)ψ = 0**,  □ = (1/c²)∂²/∂t² − ∇²
Lorentz değişmezdir. Ama iki ciddi sorun:
  * Zamanda İKİNCİ mertebe olduğu için ψ(t₀) yetmez, ∂ψ/∂t(t₀) de
    gerekir; olasılık yorumu bozulur.
  * Süreklilik denkleminden çıkan ρ = (iħ/2mc²)(ψ*∂ψ/∂t − ψ∂ψ*/∂t)
    **NEGATIF olabilir**. Olasılık yoğunluğu negatif olamaz.
  * Ayrıca E = ±√(p²c² + m²c⁴): negatif enerjiler.

**3. Dirac'ın çıkış yolu: zamanda BİRİNCİ mertebe.**
Dirac şunu istedi: denklem zamanda birinci mertebeden olsun (olasılık
kurtulsun) ama karesi Klein-Gordon'u versin. Bunun için
    iħ ∂ψ/∂t = (cα·p̂ + βmc²)ψ
biçimini aradı. Karesinin E² = p²c² + m²c⁴ vermesi için α ve β şu
koşulları sağlamalı:
    αᵢαⱼ + αⱼαᵢ = 2δᵢⱼ,  αᵢβ + βαᵢ = 0,  β² = 1
**Bu koşullar sayılarla sağlanamaz** (iki sayı hep komüte eder).
En küçük çözüm 4×4 MATRISLERDIR. Dolayısıyla ψ dört bileşenlidir.

**4. Ne kazanıldı?**
  * ρ = ψ†ψ ≥ 0 — olasılık yoğunluğu her zaman pozitif.
  * Dört bileşen ikişer ikişer ayrışır: **spin yukarı/aşağı** ve
    **parçacık/antiparçacık**. Spin, denkleme elle konmadı; Lorentz
    değişmezliği + birinci mertebe koşulundan ÇIKTI.
  * Elektronun manyetik momenti g ≈ 2 kendiliğinden çıkar.
  * Negatif enerji çözümleri kalır ama artık yorumu vardır:
    antiparçacıklar (Dirac denizi, sonra Feynman-Stückelberg yorumu).

**5. Sonuç.** Klein-Gordon spin-0 parçacıkları (örneğin pion) için
doğrudur; olasılık yoğunluğu değil YÜK yoğunluğu olarak yorumlanır.
Dirac denklemi spin-1/2 için doğrudur. Yani "başarısızlık" değil,
her denklemin kendi spin sınıfı vardır.
""", """
The Schrodinger equation is first order in time and second in space, which
clashes with Lorentz invariance. Squaring E^2 = p^2c^2 + m^2c^4 gives the
Klein-Gordon equation, which is invariant but second order in time, so its
density can be negative and the probability interpretation fails. Dirac
demanded a first-order equation whose square reproduces Klein-Gordon; the
required anticommutation relations cannot be met by numbers, only by 4x4
matrices. The result has a positive density psi-dagger psi and, remarkably,
predicts spin and antiparticles rather than assuming them.
""",
  eqs=["E² = p²c² + m²c⁴", "(□ + m²c²/ħ²)ψ = 0",
       "iħ∂ψ/∂t = (cα·p̂ + βmc²)ψ",
       "αᵢαⱼ + αⱼαᵢ = 2δᵢⱼ", "ρ = ψ†ψ ≥ 0"],
  ex_tr=["Elektron için mc² = 0,511 MeV. Klein-Gordon'un negatif enerji "
         "çözümleri E = −0,511 MeV'den aşağısını gösterir; Dirac bunu "
         "pozitron olarak yorumlar ve 1932'de Anderson pozitronu bulur."],
  ex_en=["Dirac's negative-energy solutions were interpreted as the "
         "positron, found by Anderson in 1932."],
  kw="klein gordon denklemi|dirac denklemi turet|"
     "relativistik schrodinger neden basarisiz|negatif enerji cozumleri|"
     "goreli dalga denklemi|dirac matrisleri neden|"
     "klein-gordon equation|dirac equation derivation|relativistic quantum",
  related="ozel_gorelilik|kanonik_kuantumlama|pauli_su2"),

T("minimal_baglasim", "Minimal Bağlaşım ve Ayar (Gauge) Değişmezliği",
  "Minimal Coupling and Gauge Invariance", """
Elektromanyetik alan Schrödinger denklemine nasıl girer? Cevap tek bir
kuralda: p̂ → p̂ − qA.

**1. Klasik köken.**
Yüklü parçacığın Lagrange fonksiyonu:
    L = ½mv² − qφ + q**v·A**
Eşlenik momentum artık mv değildir:
    **p** = ∂L/∂**v** = m**v** + q**A**
Yani KANONIK momentum p ile KİNETİK momentum mv farklıdır:
    m**v** = **p** − q**A**
Hamilton fonksiyonu H = p·v − L hesaplanınca:
    **H = (p − qA)²/2m + qφ**

**2. Kuantumlama.**
Kanonik kuantumlama p → p̂ = −iħ∇ der. Yerine koyunca:
    iħ ∂ψ/∂t = [ (−iħ∇ − q**A**)²/2m + qφ ] ψ
"Minimal bağlaşım" budur: serbest denklemde ∇ yerine
    **∇ → ∇ − (iq/ħ)A**   (kovaryant türev, D)
yazmak yeterlidir.

**3. Neden "minimal"?** Alanı denkleme sokmanın en az varsayımlı yolu
olduğu için. Ek terimler (örneğin spin-alan bağlaşımı) elle eklenebilir
ama gerekmez — Dirac denkleminde kendiliğinden çıkarlar.

**4. Ayar dönüşümü.**
Elektromanyetik alanlar potansiyelleri tek belirlemez:
    **A** → **A** + ∇χ,   φ → φ − ∂χ/∂t
**B** = ∇×**A** ve **E** değişmez. Peki ψ?

**5. Dalga fonksiyonu FAZ kazanır — ispat.**
Denklemin biçimi korunsun istiyorsak ψ da dönüşmeli:
    **ψ → ψ' = e^(iqχ/ħ) ψ**
Kontrol: kovaryant türev bu dönüşüm altında
    (∇ − (iq/ħ)(A + ∇χ))(e^(iqχ/ħ)ψ)
    = e^(iqχ/ħ)[∇ψ + (iq/ħ)(∇χ)ψ − (iq/ħ)(A + ∇χ)ψ]
    = e^(iqχ/ħ)(∇ − (iq/ħ)A)ψ
Yani **Dψ aynı fazla dönüşür** — denklem biçimini korur. ∎
|ψ'|² = |ψ|² olduğu için gözlenebilirler değişmez.

**6. Anlamı.** Sıradan türev ayar altında biçimi bozar; kovaryant türev
bozmaz. Elektromanyetik alanın varlığı, yerel faz serbestliğinin
(U(1) ayar simetrisi) ZORUNLU sonucudur. Aynı mantık SU(2) ve SU(3)'e
genişletilince zayıf ve güçlü etkileşimler çıkar — Standart Model'in
kurulma biçimi budur.

**7. Aharonov-Bohm.** A'nın kendisi ölçülemez sanılırdı; ama kapalı bir
halka boyunca ∮A·dl = Φ (manyetik akı) faz farkı üretir ve girişim
deseninde GÖRÜLÜR — B alanı parçacığın geçtiği yerde sıfır olsa bile.
""", """
For a charged particle L = m v^2/2 - q phi + q v.A, so the canonical
momentum is p = mv + qA and H = (p - qA)^2/2m + q phi. Quantising gives
minimal coupling: replace grad by grad - (iq/hbar)A. Under a gauge change
A -> A + grad(chi), phi -> phi - d(chi)/dt, the wave function must pick up
a phase psi -> exp(iq chi/hbar) psi; substituting shows the covariant
derivative transforms with the same phase, so the equation keeps its form
and |psi|^2 is unchanged. Electromagnetism is thus the consequence of local
U(1) phase freedom.
""",
  eqs=["p = mv + qA", "H = (p − qA)²/2m + qφ",
       "∇ → ∇ − (iq/ħ)A", "A → A + ∇χ, ψ → e^(iqχ/ħ)ψ"],
  ex_tr=["Aharonov-Bohm halkasında faz farkı Δθ = qΦ/ħ. Bir elektron "
         "(q = 1,6e-19 C) ve Φ = 4,1e-15 Wb (akı kuantumu) için "
         "Δθ = 2π — girişim deseni tam bir periyot kayar."],
  ex_en=["In the Aharonov-Bohm ring the phase shift is q Phi/hbar; one flux "
         "quantum shifts the pattern by a full period."],
  kw="minimal baglasim|minimal coupling|p eksi qA|"
     "gauge donusumu schrodinger|ayar degismezligi|kovaryant turev|"
     "elektromanyetik alanda schrodinger|aharonov bohm faz|"
     "gauge invariance|covariant derivative|electromagnetic coupling",
  related="maxwell_denklemleri|kanonik_kuantumlama|noether_ispat"),

T("yol_integrali", "Feynman Yol İntegrali ve En Az Etki",
  "The Feynman Path Integral and Least Action", """
Klasik mekanikte parçacık TEK bir yol izler: etkiyi durağan yapan yol.
Kuantum mekaniğinde parçacık BÜTÜN yolları izler; klasik yol, geriye
kalan tek yoldur.

**1. Klasik başlangıç: en az etki.**
    S[x(t)] = ∫ L(x, ẋ, t) dt,   δS = 0 ⇒ Euler-Lagrange
Klasik yol, etkinin durağan olduğu yoldur.

**2. Feynman'ın postülatı.**
A noktasından B'ye geçiş genliği, TÜM yolların katkılarının toplamıdır
ve her yol aynı BÜYÜKLÜKTE, farklı FAZDA katkı verir:
    **K(B,A) = ∫ 𝒟[x(t)] · e^(iS[x]/ħ)**
Faz, o yolun etkisidir (ħ birimlerinde).

**3. Klasik limit neden çıkar — durağan faz.**
ħ çok küçük olduğunda S/ħ devasadır; komşu yollar arasında faz çılgınca
salınır ve katkılar BİRBİRİNİ GÖTÜRÜR. Götürmediği tek yer, fazın
komşu yollara göre değişmediği yerdir:
    δS = 0
Yani **klasik yol, katkısı sağ kalan tek yoldur**. En az etki ilkesi,
yol integralinin ħ→0 limitidir. Klasik mekaniğin "neden" durağan etki
kullandığı sorusunun cevabı budur.

**4. Schrödinger denklemiyle eşdeğerlik — kısa yol.**
Çok kısa bir ε aralığı için tek bir "yol dilimi" yeter:
    ψ(x, t+ε) = (1/A)∫ exp(i/ħ [ m(x−y)²/2ε − εV(x) ]) ψ(y,t) dy
η = x − y koyup ε ve η'da açalım. Gauss integralleri:
    ∫e^(imη²/2ħε)dη = √(2πiħε/m) ≡ A
    ⟨η²⟩ = iħε/m
Soldaki ψ(x,t+ε) ≈ ψ + ε∂ψ/∂t, sağdaki ψ(y) ≈ ψ − η∂ψ/∂x +
(η²/2)∂²ψ/∂x². Yerine koyup ε'nin birinci mertebesini eşitleyince:
    ε ∂ψ/∂t = (iħε/2m)∂²ψ/∂x² − (iε/ħ)Vψ
ε ile sadeleştirip iħ ile çarpalım:
    **iħ ∂ψ/∂t = −(ħ²/2m)∂²ψ/∂x² + Vψ** ∎
Yol integrali ile Schrödinger denklemi eşdeğerdir.

**5. Neden değerli?** Yol integrali Lagrange dilinde yazılır, bu yüzden
Lorentz değişmezliği açıktır; alan kuramında ve istatistik mekanikte
(t → −iτ ile) doğal araçtır.
""", """
Classically a particle follows the single path that makes the action
stationary. Feynman's postulate is that the amplitude is a sum over all
paths, each contributing exp(iS/hbar). When hbar is small the phases of
neighbouring paths cancel except where dS = 0, so the classical path is
the survivor: least action is the hbar -> 0 limit of the path integral.
Expanding a single short-time slice with Gaussian integrals and matching
terms of order epsilon reproduces the Schrodinger equation, proving the
two formulations equivalent.
""",
  eqs=["S = ∫L dt", "K(B,A) = ∫𝒟[x] e^(iS/ħ)", "δS = 0 (klasik yol)",
       "iħ∂ψ/∂t = −(ħ²/2m)∂²ψ/∂x² + Vψ"],
  ex_tr=["Serbest parçacık için yol integrali doğrudan hesaplanabilir: "
         "K(x,t;0,0) = √(m/2πiħt)·exp(imx²/2ħt). Bu, Schrödinger "
         "denkleminin serbest yayıcısıyla (propagator) birebir aynıdır."],
  ex_en=["For a free particle the path integral gives the standard "
         "propagator sqrt(m/2 pi i hbar t) exp(i m x^2 / 2 hbar t)."],
  kw="yol integrali|feynman yol integrali|path integral turet|"
     "en az etki ilkesi kuantum|duragan faz klasik yol|"
     "yol integrali schrodinger esdeger|propagator turet|"
     "path integral formulation|sum over histories|stationary phase",
  related="lagrange|klasik_limit|kanonik_kuantumlama"),

T("pauli_su2", "Spin, Pauli Matrisleri ve SU(2) Cebri",
  "Spin, Pauli Matrices and the SU(2) Algebra", """
Spin, "kendi ekseni etrafında dönme" DEĞİLDİR. Klasik açısal momentumdan
türetilemez; bunun matematiksel sebebi vardır.

**1. Neden klasik türetilemez — iki kanıt.**
*(a) Yörünge açısal momentumu yalnızca TAM SAYI verir.* L̂ = r̂ × p̂
tanımından çıkan küresel harmonikler Y_ℓm, tek değerlilik koşulu
(φ → φ + 2π'de aynı değer) yüzünden ℓ = 0,1,2,... verir. Spin-1/2 bu
listede YOKTUR. Yarım tam sayı, r × p biçiminde bir operatörden çıkamaz.

*(b) Klasik dönme hızı ışık hızını aşardı.* Elektronu r ≈ 10⁻¹⁵ m
yarıçaplı bir küre sayıp ħ/2 açısal momentum vermek için gereken yüzey
hızı c'nin yüzlerce katı çıkar. Yani "dönen top" resmi tutarsızdır.

**2. O hâlde spin nedir?** Açısal momentum CEBRİNİ sağlayan, ama uzayda
bir dönmeye karşılık gelmeyen içsel bir serbestlik derecesi. Tanımı
cebridir:
    **[Ŝᵢ, Ŝⱼ] = iħ εᵢⱼₖ Ŝₖ**

**3. Pauli matrisleri.**
Spin-1/2 için Ŝ = (ħ/2)**σ**, burada
    σ_x = [[0,1],[1,0]],  σ_y = [[0,−i],[i,0]],  σ_z = [[1,0],[0,−1]]

**4. Cebri sağladıklarını İSPATLA.**
σ_x σ_y çarpımını açalım:
    σ_x σ_y = [[0,1],[1,0]]·[[0,−i],[i,0]] = [[i,0],[0,−i]] = i σ_z
    σ_y σ_x = [[0,−i],[i,0]]·[[0,1],[1,0]] = [[−i,0],[0,i]] = −i σ_z
O hâlde
    [σ_x, σ_y] = 2i σ_z
Ŝ = (ħ/2)σ koyunca:
    [Ŝ_x, Ŝ_y] = (ħ²/4)[σ_x,σ_y] = (ħ²/4)(2iσ_z) = iħ·(ħ/2)σ_z = iħŜ_z ∎
Diğer bileşenler döngüsel olarak aynıdır. Ayrıca
    σᵢ² = I,  {σᵢ, σⱼ} = 2δᵢⱼ I  (antikomütasyon)

**5. SU(2) ve 4π dönüşü.**
Dönme operatörü: Û(θ) = e^(−iθ·**σ**/2). z ekseni çevresinde 2π dönme:
    Û(2π) = e^(−iπσ_z) = **−I**
Yani spinör 2π dönmede İŞARET DEĞİŞTİRİR; başlangıca dönmek için 4π
gerekir. Bu, SU(2)'nin SO(3)'ün ÇİFT ÖRTÜSÜ olmasının fiziksel
görünümüdür. Vektörlerde (SO(3)) böyle bir şey olmaz — spin gerçekten
farklı bir nesnedir.

**6. Ölçülebilir sonuç.** İşaret değişimi tek başına gözlenemez (global
faz), ama girişimde GÖZLENİR: nötron interferometrisi deneyleri (1975)
2π dönmede desenin ters döndüğünü doğrulamıştır.
""", """
Spin cannot come from r x p: single-valuedness of spherical harmonics
forces integer l, and a classical spinning electron would need surface
speeds far above c. Spin is defined by its algebra [S_i, S_j] = i hbar
eps S_k. With S = (hbar/2) sigma, direct multiplication gives
sigma_x sigma_y = i sigma_z and sigma_y sigma_x = -i sigma_z, hence
[sigma_x, sigma_y] = 2 i sigma_z and therefore [S_x, S_y] = i hbar S_z.
The rotation operator exp(-i theta sigma/2) gives -I for a 2 pi rotation:
SU(2) double-covers SO(3), confirmed by neutron interferometry.
""",
  eqs=["[Ŝᵢ,Ŝⱼ] = iħεᵢⱼₖŜₖ", "Ŝ = (ħ/2)σ", "[σ_x,σ_y] = 2iσ_z",
       "σᵢ² = I", "Û(2π) = −I"],
  ex_tr=["σ_z'nin özdeğerleri ±1, yani Ŝ_z = ±ħ/2. Stern-Gerlach "
         "deneyinde gümüş atom demetinin İKİYE ayrılması tam bu iki "
         "özdeğerin gözlenmesidir — sürekli bir dağılım değil."],
  ex_en=["The eigenvalues +-hbar/2 are exactly the two beams seen in the "
         "Stern-Gerlach experiment."],
  kw="pauli matrisleri|spin su2 cebri|spin neden klasik degil|"
     "spin 1/2 operatorleri|pauli matris komutator ispat|"
     "su2 cebri saglar|4 pi donus spinor|"
     "pauli matrices|spin algebra proof|SU(2) double cover",
  related="stern_gerlach|dirac_gosterim|klein_gordon_dirac"),

T("wkb_yaklasimi", "WKB Yaklaşımı ve Klasik Sınır",
  "The WKB Approximation and the Classical Limit", """
Potansiyel yavaş değişiyorsa Schrödinger denklemi yaklaşık olarak
çözülebilir — ve çözüm doğrudan klasik mekaniğe bağlanır.

**1. Kurulum.**
    −(ħ²/2m)ψ'' + Vψ = Eψ  ⇒  ψ'' + k²(x)ψ = 0,
    k(x) = √(2m(E − V(x)))/ħ = p(x)/ħ

**2. Üstel deneme (ansatz).**
Dalga fonksiyonunu şu biçimde yazalım — bu bir kayıp değil, tanımdır:
    **ψ(x) = e^(iS(x)/ħ)**
Türevleri alıp yerine koyalım:
    ψ' = (i/ħ)S' ψ,   ψ'' = [(i/ħ)S'' − (1/ħ²)S'²] ψ
Denkleme koyunca:
    (i/ħ)S'' − (1/ħ²)S'² + k² = 0
ħ² ile çarpalım:
    **iħS'' − S'² + p²(x) = 0**                       (∗)

**3. ħ'ye göre seri.**
    S = S₀ + ħS₁ + ħ²S₂ + ...
(∗)'da mertebe mertebe eşitleyelim.

*ħ⁰ mertebesi:*  S₀'² = p²  ⇒  **S₀ = ±∫p(x)dx**
Bu tam olarak klasik mekaniğin İNDİRGENMİŞ ETKİSİDİR. Aynı denklem
(S'² = p²) Hamilton-Jacobi denklemidir. **Yani WKB'nin sıfırıncı
mertebesi klasik mekaniktir.**

*ħ¹ mertebesi:*  iS₀'' − 2S₀'S₁' = 0 ⇒ S₁' = iS₀''/(2S₀') = ip'/(2p)
    ⇒ S₁ = (i/2)ln p  ⇒  e^(iħS₁/ħ) = 1/√p

**4. WKB çözümü.**
    **ψ(x) ≈ (C/√(p(x))) · exp(±(i/ħ)∫p(x)dx)**
Genlikteki 1/√p sezgiseldir: parçacık yavaş olduğu yerde (p küçük) daha
uzun zaman geçirir, orada bulunma olasılığı |ψ|² ∝ 1/p artar — klasik
olasılık dağılımıyla birebir aynı.

**5. Geçerlilik koşulu.**
Seriyi kestiğimiz için ħS₁ ≪ S₀ olmalı. Bu şu koşula indirgenir:
    **|dλ/dx| ≪ 1**,  λ = ħ/p (yerel de Broglie dalga boyu)
Yani potansiyel, bir dalga boyu mesafesinde AZ değişmeli. Koşul
p → 0 olan DÖNÜM NOKTALARINDA (E = V) bozulur; orada Airy
fonksiyonlarıyla bağlantı kurulur.

**6. Klasik sınır (ħ→0).**
ħ → 0 iken λ = ħ/p → 0 olur ve koşul her yerde sağlanır. Faz S₀/ħ
devasa olur, hızlı salınır; ölçülebilen şey yalnızca genliktir ve
|ψ|² ∝ 1/p klasik dağılımı verir. **WKB, kuantumdan klasiğe geçişin
matematiksel köprüsüdür.**

**7. Uygulama — Bohr-Sommerfeld.** Kapalı bir yörüngede ψ tek değerli
olmalı: ∮p dx = (n + ½)·2πħ. Bu, eski kuantum kuramının kuantumlama
koşuludur ve harmonik osilatörde tam olarak Eₙ = ħω(n+½) verir.
""", """
For a slowly varying potential write psi = exp(iS/hbar); substituting gives
i hbar S'' - S'^2 + p^2 = 0. Expanding S in powers of hbar, the order-hbar^0
term is S0' = p, i.e. the Hamilton-Jacobi equation of classical mechanics,
and the next order gives the 1/sqrt(p) amplitude. The result
psi ~ exp(i int p dx/hbar)/sqrt(p) is valid when the local de Broglie
wavelength changes little over itself, and it breaks down at turning points.
As hbar -> 0 the condition always holds and |psi|^2 ~ 1/p reproduces the
classical distribution; quantisation of closed orbits gives Bohr-Sommerfeld.
""",
  eqs=["ψ = e^(iS/ħ)", "iħS'' − S'² + p² = 0", "S₀ = ∫p dx",
       "ψ ≈ (C/√p)e^(±(i/ħ)∫p dx)", "|dλ/dx| ≪ 1", "∮p dx = (n+½)2πħ"],
  ex_tr=["Harmonik osilatörde ∮p dx = 2πE/ω. Bohr-Sommerfeld koşulu "
         "2πE/ω = (n+½)2πħ ⇒ E = ħω(n+½) — tam çözümle birebir aynı. "
         "WKB burada yaklaşık değil, KESIN sonucu verir."],
  ex_en=["For the harmonic oscillator WKB gives exactly E = hbar w (n+1/2)."],
  kw="wkb yaklasimi|wkb turet|yarı klasik yaklasim|"
     "hamilton jacobi kuantum|klasik sinir hbar sifir|"
     "bohr sommerfeld kuantumlama|donum noktasi wkb|"
     "WKB approximation|semiclassical|Hamilton-Jacobi limit",
  related="klasik_limit|kanonik_kuantumlama|merdiven_operator"),
]
