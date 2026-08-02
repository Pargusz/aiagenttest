# -*- coding: utf-8 -*-
"""TURETIMLER: lisansustu duzeyde adim adim ispatlar.

Olculdu: kullanicinin verdigi 20 zor kuramsal sorudan yalnizca 2'si tam
cevaplanabildi. Sebep yonlendirme degil ICERIK EKSIKLIGIYDI — sistem
"Born olasilik yorumunu ispatla" sorusuna elinde yazili bir ispat
olmadigi icin en yakin SAYISAL bagintiya tutunuyordu (fotoelektrik).

Bu dosya o boslugu kapatir. Her madde bir ISPATTIR: nereden basladigi,
hangi varsayimi kullandigi ve her ara adimi yazilidir. Formul karti
degil, turetimdir.

Yazim kurali: bir ogrenci bu metni okuyup kagida gecirebilmeli. Atlanan
adim birakmiyoruz; "gosterilebilir ki" demiyoruz.
"""
from .knowledge import T

TURETIM_KONULARI = [

T("born_kurali", "Born Kuralı: |ψ|² Neden Olasılık Yoğunluğudur",
  "The Born Rule: why |psi|^2 is a probability density", """
Schrödinger denklemi ψ'yi verir, ama ψ'nin kendisi ölçülemez: karmaşık
değerlidir. Ölçülebilen ne? Born'un yanıtı: |ψ|².

**1. Neden ψ'nin kendisi olamaz.**
ψ karmaşıktır; olasılık ise gerçel ve negatif olamaz. Ayrıca Schrödinger
denklemi doğrusaldır: ψ bir çözümse e^(iα)ψ da çözümdür. Fiziksel
tahminler bu **global faza** bağlı olmamalıdır. |e^(iα)ψ|² = |ψ|²
olduğundan modül karesi bu iki koşulu da sağlar.

**2. Neden |ψ|² korunur — süreklilik.**
Bir olasılık yoğunluğunun toplam integrali ZAMANLA DEĞİŞMEMELİDİR;
parçacık kaybolmaz. Bunu göstermek gerekir, varsaymak değil.
ρ = ψ*ψ tanımlayalım ve zaman türevini alalım:

    ∂ρ/∂t = ψ* ∂ψ/∂t + ψ ∂ψ*/∂t

Schrödinger denkleminden ∂ψ/∂t = (1/iħ)Ĥψ ve eşleniğinden
∂ψ*/∂t = −(1/iħ)(Ĥψ)*. Ĥ = −(ħ²/2m)∇² + V ve V gerçel olduğundan:

    ∂ρ/∂t = (iħ/2m)(ψ*∇²ψ − ψ∇²ψ*)
          = ∇·[(iħ/2m)(ψ*∇ψ − ψ∇ψ*)]
          = −∇·**j**

Burada **j** = (ħ/2mi)(ψ*∇ψ − ψ∇ψ*) olasılık akımıdır. Elde ettiğimiz

    ∂ρ/∂t + ∇·**j** = 0

bir SÜREKLILIK denklemidir. Tüm uzay üzerinden integre edip ψ'nin
sonsuzda sıfıra gittiğini kullanırsak yüzey terimi kaybolur:

    d/dt ∫|ψ|² d³r = 0

Yani ∫|ψ|² zamanla sabittir. **İşte bu, |ψ|²'nin olasılık yoğunluğu
olarak kullanılabilmesinin matematiksel gerekçesidir.** Başka hiçbir
basit ifade (örneğin |ψ| ya da Re ψ) böyle bir korunum vermez.

**3. Normlama koşulu.**
Sabit olan bu integrali 1'e ayarlarız:

    ∫ |ψ(r,t)|² d³r = 1

Bu bir seçimdir (ψ'yi bir sabitle çarpmak serbestti) ama 2. adım sayesinde
TUTARLI bir seçimdir: bir kez 1 yaptıysanız, her zaman 1 kalır.
Böylece P(V) = ∫_V |ψ|² d³r, parçacığı V bölgesinde bulma olasılığıdır.

**4. Sonuç ve sınır.**
Born kuralı denklemden TÜRETİLMEZ; bir POSTÜLATTIR. Yukarıda ispatlanan
şey, bu postülatın tutarlı olduğudur: doğrusallıkla, faz serbestliğiyle
ve olasılığın korunumuyla çelişmez. Gleason teoremi (1957) daha ileri
gider: Hilbert uzayı boyutu ≥ 3 ise, olasılık atamanın |⟨φ|ψ⟩|²'den
başka tutarlı bir yolu yoktur.
""", """
Schrodinger's equation gives psi, but psi itself is complex and cannot be
measured. Born's answer is |psi|^2. Two requirements fix it: probability
must be real and non-negative, and it must not depend on the global phase
(psi and exp(i a) psi describe the same state). Then one PROVES that the
total integral is conserved: writing rho = psi* psi and using the
Schrodinger equation gives d(rho)/dt + div j = 0 with
j = (hbar/2mi)(psi* grad psi - psi grad psi*). Integrating over all space
gives d/dt of the norm equal to zero, so setting it to 1 once keeps it 1.
Born's rule is a postulate; what is proved is its consistency.
""",
  eqs=["ρ = |ψ|² = ψ*ψ", "j = (ħ/2mi)(ψ*∇ψ − ψ∇ψ*)",
       "∂ρ/∂t + ∇·j = 0", "∫|ψ|² d³r = 1"],
  ex_tr=["Sonsuz kuyuda ψ_n = A·sin(nπx/L). Normlama: "
         "∫₀^L A²sin²(nπx/L)dx = A²·L/2 = 1 ⇒ A = √(2/L). "
         "Bu sabit keyfi değil, normlama koşulunun zorunlu sonucudur."],
  ex_en=["For the infinite well, normalisation forces A = sqrt(2/L)."],
  kw="born kurali|born olasilik yorumu|psi kare neden olasilik|"
     "olasilik yogunlugu ispat|normlama kosulu|dalga fonksiyonu olasilik|"
     "neden psi kare|born yorumu ispat|"
     "born rule|probability density proof|normalisation condition",
  related="kuantum_formalizm|olasilik_akimi|kuantum_temelleri"),

T("zaman_bagli_schrodinger",
  "Zamana Bağlı Schrödinger Denkleminin Türetimi",
  "Deriving the Time-Dependent Schrodinger Equation", """
Bu denklem **ispatlanmaz**, KURULUR. Ama keyfi değildir: klasik enerji
bağıntısı ile dalga tanımından, birkaç açık varsayımla çıkar.

**Başlangıç: klasik toplam enerji.**
    E = p²/2m + V(x)                                   (1)

**Varsayım 1 — parçacığa bir DALGA eşlik eder.**
Serbest parçacık için en basit dalga düzlem dalgadır:
    ψ(x,t) = A·e^(i(kx − ωt))                          (2)

**Varsayım 2 — dalga ile parçacık nicelikleri şöyle bağlıdır.**
    de Broglie:  p = ħk
    Planck-Einstein:  E = ħω
Bu ikisi deneyseldir (kırınım deneyleri, fotoelektrik olay).

**3. Zaman türevi ENERJİYİ verir.**
(2)'nin zamana göre türevi:
    ∂ψ/∂t = −iω·ψ
İki tarafı `iħ` ile çarpalım:
    **iħ ∂ψ/∂t = iħ(−iω)ψ = ħω·ψ = E·ψ**              (3)
Yani `iħ ∂/∂t` işlemi dalgadan ENERJİYİ çekip çıkarıyor.

**4. İkinci uzay türevi p²'yi verir.**
    ∂ψ/∂x = ik·ψ,   ∂²ψ/∂x² = (ik)²ψ = −k²ψ
`−ħ²/2m` ile çarpalım:
    **−(ħ²/2m) ∂²ψ/∂x² = (ħ²k²/2m)ψ = (p²/2m)·ψ**     (4)

**5. Klasik bağıntıyı dalgaya uygula.**
(1)'i ψ ile çarpalım:  E·ψ = (p²/2m)ψ + V·ψ
Sol tarafa (3)'ü, sağdaki ilk terime (4)'ü koyalım:

## `iħ ∂ψ/∂t = −(ħ²/2m) ∂²ψ/∂x² + V(x)ψ`

Üç boyutta `∂²/∂x² → ∇²`. Sağ taraf `Ĥψ`'dir, yani `iħ ∂ψ/∂t = Ĥψ`.

**Varsayım 3 — DOĞRUSALLIK.** Denklemi düzlem dalga için kurduk ama
her yere uyguluyoruz. Gerekçe: denklem doğrusaldır, dolayısıyla düzlem
dalgaların üst üste binmesi (Fourier) de çözümdür — ve her dalga paketi
böyle yazılabilir. Bu yüzden `V` sabit olmasa da denklem geçerli
sayılır; asıl sınav deneydir.

**Neden zamanda BİRİNCİ mertebe?** Çünkü ψ(t₀) verildiğinde geleceğin
belirlenmesini istiyoruz. İkinci mertebe olsaydı ∂ψ/∂t(t₀) de gerekirdi
ve olasılık yorumu bozulurdu (Klein-Gordon'da tam bu olur).

**Neden KOMPLEKS?** (3)'teki `i` atılamaz. Gerçel bir denklem
`∂ψ/∂t ∝ ∂²ψ/∂x²` biçiminde olurdu — bu ISI denklemidir ve dalga değil
sönüm verir. `i`, çözümü `e^(−iEt/ħ)` yapar: modülü 1, yani olasılık
korunur ama FAZ döner. Girişim buradan gelir. Kısacası kompleks olmak
bir kolaylık değil, zorunluluktur.

**Sınır: bu bir ispat değildir.** Düzlem dalgadan yola çıkıp genel bir
denklem yazdık; adım (5) bir GENELLEME'dir. Schrödinger denklemi bir
postülattır ve doğruluğu 100 yıllık deneyle sınanmıştır.
""", """
The equation is constructed, not proven, but not arbitrarily. Start from
E = p^2/2m + V and assume a plane wave psi = exp(i(kx - wt)) with
p = hbar k and E = hbar w. Then i hbar d(psi)/dt = E psi and
-(hbar^2/2m) d2(psi)/dx2 = (p^2/2m) psi. Substituting into the classical
energy relation gives i hbar d(psi)/dt = -(hbar^2/2m) lap psi + V psi.
Linearity justifies extending it beyond plane waves. First order in time
is required so that psi(t0) determines the future; the imaginary unit is
required because a real version would be the heat equation, giving decay
instead of interference.
""",
  eqs=["E = p²/2m + V", "ψ = A·e^(i(kx − ωt))", "p = ħk,  E = ħω",
       "iħ ∂ψ/∂t = Eψ", "−(ħ²/2m)∂²ψ/∂x² = (p²/2m)ψ",
       "iħ ∂ψ/∂t = −(ħ²/2m)∇²ψ + Vψ"],
  ex_tr=["Serbest parçacıkta V = 0 ve ψ = e^(i(kx−ωt)) koyalım: "
         "sol taraf ħω·ψ, sağ taraf (ħ²k²/2m)·ψ. Eşitlik ħω = ħ²k²/2m, "
         "yani E = p²/2m — başladığımız klasik bağıntı. Denklem kendi "
         "kuruluşunu doğruluyor."],
  ex_en=["For a free particle the equation returns E = p^2/2m."],
  # DIKKAT: anahtarlar DAR tutuldu. Genis hâlinde ("schrodinger
     # denkleminin kurulusu", "zamana bagli formu turet") bu konu baska
     # sorulari cekiyordu — Euler-Lagrange sorusu bile bu konuyla
     # eslestirilip yan yana konuyordu (olculdu: kuramsal 15/20 ->
     # 13/20). Her anahtar ZAMANA BAGLI SCHRODINGER'i adlandirmali.
  kw="zamana bagli schrodinger denklemi turet|"
     "zamana bagli schrodinger denklemi nasil|"
     "zaman bagimli schrodinger turet|"
     "schrodinger denkleminin zamana bagli formu|"
     "dalga fonksiyonu neden kompleks olmak zorunda|"
     "schrodinger neden zamanda birinci mertebe|"
     "time dependent schrodinger derivation",
  related="kanonik_kuantumlama|born_kurali|klein_gordon_dirac"),

T("olasilik_akimi", "Olasılık Akımı ve Süreklilik Denklemi",
  "Probability Current and the Continuity Equation", """
Yük korunumu elektrodinamikte ∂ρ/∂t + ∇·**J** = 0 ile yazılır. Kuantum
mekaniğinde birebir aynı yapı çıkar — ve bu tesadüf değildir.

**1. Başlangıç: Schrödinger denklemi ve eşleniği.**
    iħ ∂ψ/∂t = −(ħ²/2m)∇²ψ + Vψ                    (1)
    −iħ ∂ψ*/∂t = −(ħ²/2m)∇²ψ* + Vψ*                (2)
(2), (1)'in karmaşık eşleniğidir; V gerçel olduğu için V değişmez.
**Bu şart kritiktir**: V karmaşık olsaydı korunum bozulurdu.

**2. Yoğunluğun zaman türevi.**
ρ = ψ*ψ olsun.
    ∂ρ/∂t = ψ*(∂ψ/∂t) + ψ(∂ψ*/∂t)
(1)'i iħ'ye, (2)'yi −iħ'ye bölüp yerine koyalım:
    ∂ψ/∂t  = (iħ/2m)∇²ψ − (i/ħ)Vψ
    ∂ψ*/∂t = −(iħ/2m)∇²ψ* + (i/ħ)Vψ*
Toplayınca V terimleri **birbirini götürür**:
    ∂ρ/∂t = (iħ/2m)(ψ*∇²ψ − ψ∇²ψ*)

**3. Diverjans biçimine sokma.**
Şu özdeşliği kullanıyoruz:
    ∇·(ψ*∇ψ − ψ∇ψ*) = ψ*∇²ψ − ψ∇²ψ*
(çapraz terimler ∇ψ*·∇ψ birbirini götürür). O hâlde
    ∂ρ/∂t = (iħ/2m)∇·(ψ*∇ψ − ψ∇ψ*) = −∇·**j**
    **j** ≡ (ħ/2mi)(ψ*∇ψ − ψ∇ψ*) = (ħ/m)·Im(ψ*∇ψ)

**4. Süreklilik denklemi.**
    ∂ρ/∂t + ∇·**j** = 0
Bir hacim V üzerinden integre edip diverjans teoremini uygularsak:
    d/dt ∫_V ρ dV = −∮_S **j**·d**A**
Yani bir bölgedeki olasılığın azalması, ancak yüzeyden DIŞARI AKMASIYLA
olur. Olasılık yoktan var olmaz, yok olmaz — yalnızca akar.

**Yük korunumuyla benzerlik neden?** İkisi de aynı matematiksel
kaynaktan gelir: bir U(1) faz simetrisinden. ψ → e^(iα)ψ dönüşümü
fiziği değiştirmiyorsa, Noether teoremi korunan bir akım verir. Elektrik
yükü de aynı simetriden doğar. Benzerlik yüzeysel değil, yapısaldır.

**Örnek — düzlem dalga.** ψ = A·e^(i(kx−ωt)) için
    j = (ħ/m)·Im(ψ*·ikψ) = (ħk/m)|A|² = v|A|²
Beklendiği gibi: akım = hız × yoğunluk.
""", """
The same structure as charge conservation appears in quantum mechanics.
Starting from the Schrodinger equation and its conjugate (V must be real),
the time derivative of rho = psi* psi gives, after using the identity
div(psi* grad psi - psi grad psi*) = psi* lap psi - psi lap psi*,
d(rho)/dt + div j = 0 with j = (hbar/m) Im(psi* grad psi). For a plane wave
j = v |A|^2: current equals velocity times density. The analogy with charge
conservation is structural: both follow from a U(1) phase symmetry via
Noether's theorem.
""",
  eqs=["j = (ħ/2mi)(ψ*∇ψ − ψ∇ψ*)", "j = (ħ/m)·Im(ψ*∇ψ)",
       "∂ρ/∂t + ∇·j = 0", "d/dt∫ρdV = −∮j·dA"],
  ex_tr=["Düzlem dalga ψ = A·e^(i(kx−ωt)): j = (ħk/m)|A|² = v|A|². "
         "Akım, hız çarpı yoğunluktur — klasik sezgiyle birebir uyumlu."],
  ex_en=["Plane wave: j = (hbar k/m)|A|^2 = v |A|^2."],
  kw="olasilik akimi|probability current|sureklilik denklemi kuantum|"
     "olasilik akim yogunlugu|akim yogunlugu turet|"
     "yuk korunumu benzerlik kuantum|olasilik korunumu ispat|"
     "continuity equation quantum|probability current density",
  related="born_kurali|kuantum_formalizm|noether"),

T("belirsizlik_ispat", "Heisenberg Belirsizlik İlkesinin İspatı",
  "Proof of the Heisenberg Uncertainty Principle", """
Belirsizlik ilkesi bir "ölçüm bozar" hikâyesi değildir; komütatörden
çıkan bir EŞITSIZLIKTIR. İspat üç adımdır.

**1. Komütatörü kur: [x̂, p̂] = iħ.**
Operatörler bir fonksiyona etki eder; keyfi bir ψ alalım.
    x̂p̂ψ = x·(−iħ ∂ψ/∂x) = −iħx ∂ψ/∂x
    p̂x̂ψ = −iħ ∂(xψ)/∂x = −iħ(ψ + x ∂ψ/∂x)
Farkı alalım:
    (x̂p̂ − p̂x̂)ψ = −iħx∂ψ/∂x + iħψ + iħx∂ψ/∂x = iħψ
ψ keyfi olduğundan operatör özdeşliği olarak
    **[x̂, p̂] = iħ**
Türev ile çarpma işlemlerinin sırası değiştirilemez; belirsizliğin
kaynağı budur.

**2. Cauchy-Schwarz eşitsizliği.**
Â, B̂ Hermit operatörler; ⟨Â⟩, ⟨B̂⟩ beklenen değerler. Sapmaları
tanımlayalım: δÂ = Â − ⟨Â⟩, δB̂ = B̂ − ⟨B̂⟩. Şu iki vektörü alalım:
    |f⟩ = δÂ|ψ⟩,  |g⟩ = δB̂|ψ⟩
Cauchy-Schwarz:
    ⟨f|f⟩⟨g|g⟩ ≥ |⟨f|g⟩|²
Sol taraf tam olarak (ΔA)²(ΔB)²'dir.

**3. Sağ tarafı komütatöre bağla.**
⟨f|g⟩ karmaşık bir sayıdır; herhangi bir z için |z|² ≥ (Im z)².
    Im⟨f|g⟩ = (1/2i)(⟨f|g⟩ − ⟨g|f⟩) = (1/2i)⟨[δÂ, δB̂]⟩
            = (1/2i)⟨[Â, B̂]⟩
(sabitler komüte ettiği için δ'lar düşer). O hâlde
    (ΔA)²(ΔB)² ≥ |(1/2i)⟨[Â,B̂]⟩|² = (1/4)|⟨[Â,B̂]⟩|²
Karekök alınca **genel belirsizlik bağıntısı**:
    ΔA · ΔB ≥ (1/2)|⟨[Â, B̂]⟩|

**4. Konum-momentuma uygula.**
[x̂,p̂] = iħ olduğundan |⟨iħ⟩| = ħ ve
    **Δx · Δp ≥ ħ/2**

**Ne demek, ne demek değil.** Bu, "aletimiz kaba" demek değildir;
komüte etmeyen iki gözlenebilir için ORTAK bir özdurum yoktur. Eşitlik
yalnızca Gauss dalga paketinde sağlanır — minimum belirsizlik durumu.
Komüte eden operatörler için ([Â,B̂] = 0) sağ taraf sıfırdır: ikisi
aynı anda keskin ölçülebilir.
""", """
The uncertainty principle is an inequality from the commutator, not a
story about clumsy measurement. First, acting on an arbitrary psi shows
[x,p] = i hbar. Second, with deviations dA and dB, Cauchy-Schwarz gives
(dA)^2 (dB)^2 >= |<f|g>|^2. Third, |z|^2 >= (Im z)^2 and
Im<f|g> = (1/2i)<[A,B]> give the general relation
dA dB >= (1/2)|<[A,B]>|, hence dx dp >= hbar/2. Equality holds only for a
Gaussian packet; commuting observables give zero on the right.
""",
  eqs=["[x̂, p̂] = iħ", "ΔA·ΔB ≥ (1/2)|⟨[Â,B̂]⟩|", "Δx·Δp ≥ ħ/2",
       "ΔE·Δt ≥ ħ/2"],
  ex_tr=["Bir elektron 1 Å'lık bölgeye sıkışsa: Δp ≥ ħ/(2Δx) = "
         "1,055e-34/(2·1e-10) = 5,3×10⁻²⁵ kg·m/s. Karşılık gelen enerji "
         "p²/2m ≈ 1,5×10⁻¹⁹ J ≈ 0,95 eV. Atom boyutundaki enerjilerin "
         "eV mertebesinde olması bundandır."],
  ex_en=["Confining an electron to 1 A gives dp >= 5.3e-25 kg m/s, i.e. "
         "about 1 eV — why atomic energies are of order eV."],
  kw="belirsizlik ilkesi ispat|heisenberg ispat|cauchy schwarz belirsizlik|"
     "komutator belirsizlik|x p komutator ispat|delta x delta p|"
     "belirsizlik bagintisi turet|"
     "uncertainty principle proof|commutator proof|cauchy schwarz uncertainty",
  related="kuantum_formalizm|kanonik_kuantumlama|kanonik_donusum"),

T("noether_ispat", "Noether Teoreminin Varyasyonel İspatı",
  "Variational Proof of Noether's Theorem", """
Her sürekli simetri bir korunum yasası doğurur. İspat varyasyon
hesabından çıkar ve şaşırtıcı derecede kısadır.

**1. Kurulum.**
Etki: S = ∫ L(q, q̇, t) dt. Hareket denklemi Euler-Lagrange:
    d/dt(∂L/∂q̇) − ∂L/∂q = 0                        (EL)

**2. Sürekli simetri tanımı.**
Sonsuz küçük bir dönüşüm düşünelim:
    q → q + εδq,   t → t + εδt
Bu dönüşüm bir SIMETRIDIR demek, Lagrange'ın en fazla bir tam türev
kadar değişmesi demektir:
    δL = ε dF/dt   (bazı F için)
Çünkü tam türev etkiye yalnızca sınır terimi ekler, hareket denklemini
değiştirmez.

**3. Değişimi açalım.**
    δL = (∂L/∂q)δq + (∂L/∂q̇)δq̇
(EL) ile ∂L/∂q = d/dt(∂L/∂q̇) yazalım ve δq̇ = d(δq)/dt kullanalım:
    δL = d/dt(∂L/∂q̇)·δq + (∂L/∂q̇)·d(δq)/dt
       = **d/dt[ (∂L/∂q̇) δq ]**
Çarpım kuralının tersini tanıdık: iki terim tek bir tam türev oldu.

**4. Korunan nicelik.**
Simetri koşulu δL = ε dF/dt ile birleştirince:
    d/dt[ (∂L/∂q̇)δq − F ] = 0
Yani parantez içindeki nicelik ZAMANDA SABITTIR:
    **Q = (∂L/∂q̇)·δq − F = p·δq − F  (korunur)**

**5. Üç klasik sonuç.**

*Uzay ötelemesi* — δq = 1 (sabit kayma), L değişmiyorsa F = 0:
    Q = ∂L/∂q̇ = **p**  → momentum korunur.

*Dönme* — δφ ile dönme, L değişmiyorsa:
    Q = ∂L/∂φ̇ = **L_z**  → açısal momentum korunur.

*Zaman ötelemesi* — δt = 1 için ayrı hesap gerekir (t de değişiyor);
δL = dL/dt ⇒ F = L alınır ve
    Q = q̇(∂L/∂q̇) − L = **H**  → enerji korunur.
Hamilton fonksiyonunun Legendre dönüşümü olarak çıkması tesadüf değil;
zaman ötelemesinin korunan yükü tam olarak odur.

**Ters yön de doğrudur.** Korunan bir nicelik varsa, ona karşılık gelen
bir simetri vardır. Bu yüzden yeni bir korunum yasası gözlemek, yeni
bir simetri aramak demektir — parçacık fiziğinin yöntemi budur.
""", """
Every continuous symmetry yields a conservation law. With action
S = int L dt and the Euler-Lagrange equation, a symmetry means
delta L = eps dF/dt. Expanding delta L and using EL turns it into a total
derivative d/dt[(dL/dqdot) delta q], so Q = p delta q - F is conserved.
Space translation gives momentum, rotation gives angular momentum, and
time translation gives the Hamiltonian, i.e. energy. The converse also
holds, which is why a new conservation law signals a new symmetry.
""",
  eqs=["S = ∫L dt", "d/dt(∂L/∂q̇) = ∂L/∂q", "δL = ε dF/dt",
       "Q = (∂L/∂q̇)δq − F", "H = q̇(∂L/∂q̇) − L"],
  ex_tr=["Serbest parçacık: L = ½mq̇². Uzay ötelemesi δq = 1 simetridir "
         "(L, q'ya bağlı değil). Q = ∂L/∂q̇ = mq̇ = p. Momentum korunur — "
         "Newton'un birinci yasası, aslında bir simetrinin sonucudur."],
  ex_en=["Free particle L = m qdot^2/2: translation gives Q = m qdot = p."],
  kw="noether teoremi ispat|noether varyasyonel ispat|"
     "simetri korunum ispat|zaman simetrisi enerji korunumu|"
     "uzay simetrisi momentum korunumu|donme simetrisi acisal momentum|"
     "korunan yuk turet|"
     "noether theorem proof|symmetry conservation proof",
  related="lagrange|olasilik_akimi|simetri"),
]
