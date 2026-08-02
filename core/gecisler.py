# -*- coding: utf-8 -*-
"""Kuramlar arasi GECISLER: birinden otekine nasil varilir.

Olculdu: kullanici sunu sordu —

    "Klasik fizik kinetik enerji formulunden cikarak Schrodinger
     denklemindeki Hamiltonyan operatorunun kinetik enerji kismini
     ispatlar misin?"

Sistem sorudan yalnizca "kinetik enerji" kelimesini alip Ek = mv²/2
kartini bastI. Schrodinger, Hamiltonyan, "gecis", "ispatla" — hepsi
dustu. Iki ayri eksik vardi:

  1. Soruyu BUTUN olarak okumamak (iki kavram + aralarindaki iliski).
  2. Cevabin kendisinin cekirdekte olmamasi: klasik nicelikten kuantum
     operatorune gecis (kanonik kuantumlama) yaziLI degildi.

Bu dosya ikinci eksigi kapatir. Buradaki her madde iki kuram arasinda
bir KOPRUDUR: nereden nereye, hangi adimla ve hangi varsayimla
gecildigi yazilir. Fizigin en ogretici yerleri bu gecislerdir; bir
formulu ezberlemek ile nereden geldigini bilmek ayri seylerdir.
"""
from .knowledge import T

GECIS_KONULARI = [

T("kanonik_kuantumlama",
  "Klasik Kinetik Enerjiden Kuantum Operatörüne",
  "From Classical Kinetic Energy to the Quantum Operator", """
Soru şudur: `Ek = ½mv²` gibi bir SAYI, nasıl olup da
`T̂ = −(ħ²/2m)∇²` gibi bir OPERATÖRE dönüşür?

**0. Önce: neden operatör kullanıyoruz?**
Klasik mekanikte bir parçacığın durumu `(x, p)` çiftidir ve her
gözlenebilir bu çiftin bir FONKSİYONUDUR — yani bir sayı verir.
Kuantum mekaniğinde durum ise bir **Hilbert uzayı vektörüdür** (`|ψ⟩`),
ve deneyler gösteriyor ki bir ölçüm tek bir değer değil, bir DEĞERLER
KÜMESİ verebilir (Stern-Gerlach'ta iki demet, atomda ayrık çizgiler).

Bir vektöre etki edip ondan sayı çıkaran ve "olası değerler kümesi"
kavramını taşıyan matematiksel nesne **doğrusal operatördür**: `Â|ψ⟩`
yine bir vektördür, `Â|ψₙ⟩ = aₙ|ψₙ⟩` özdeğer denklemi de o kümeyi
verir. Bu yüzden kuantum mekaniğinde **her gözlenebilir büyüklük bir
operatörle temsil edilir**; ölçüm sonuçları o operatörün özdeğerleridir.
Gerçel sonuç vermesi için operatörün **Hermit** olması gerekir.

Yani "klasik nicelik neden operatöre dönüşüyor" sorusunun cevabı, bu
geçişin kendisinde değil, kuantum mekaniğinin durum tanımındadır:
durum bir vektörse, gözlenebilir de bir operatördür. Aşağıdaki adımlar
o operatörün HANGİSİ olduğunu belirler.

**1. Klasik ifadeyi momentum cinsinden yaz.**
p = mv olduğundan
    Ek = ½mv² = p²/(2m)
Bu adım şart: kuantum mekaniğinde temel değişkenler konum ve
momentumdur, hız değil.

**2. Momentum operatörünü DE BROGLIE dalgasından oku.**
Serbest bir parçacığın dalga fonksiyonu düzlem dalgadır:
    ψ(x,t) = e^(i(kx − ωt))
de Broglie bağıntısı p = ħk. Şimdi türev alalım:
    ∂ψ/∂x = ik·ψ
İki tarafı −iħ ile çarpalım:
    −iħ ∂ψ/∂x = −iħ(ik)ψ = ħk·ψ = **p·ψ**

İşte kritik nokta: `−iħ ∂/∂x` işlemi, dalga fonksiyonundan momentumun
KENDİSİNİ çekip çıkarıyor. Bu yüzden momentum operatörü
    p̂ = −iħ ∂/∂x     (üç boyutta p̂ = −iħ∇)
diye tanımlanır.

Tanım keyfi değildir — ama gerekçesi yalnızca düzlem dalga DEĞİLDİR.
Üç koşul birlikte `p̂`yi **tek** seçenek olarak bırakır:

  * **de Broglie:** düzlem dalgada özdeğer `ħk` çıkmalı (yukarıdaki hesap).
  * **Öteleme simetrisi:** momentum, uzayda ötelemenin ÜRETECİDİR.
    `a` kadar ötelemenin operatörü `T̂(a) = e^(−iap̂/ħ)` olmalıdır;
    sonsuz küçük öteleme `ψ(x+ε) = ψ(x) + ε∂ψ/∂x` açılımıyla
    karşılaştırılınca üreteç doğrudan `−iħ∂/∂x` çıkar.
  * **Kanonik komütasyon:** `[x̂, p̂] = iħ` sağlanmalı; çarpma ve türev
    operatörleri bunu tam olarak verir (ispatı için bkz. belirsizlik
    ilkesi türetimi).

Bu üç koşulu birden sağlayan başka bir doğrusal operatör yoktur
(Stone-von Neumann teoremi bunu kesinleştirir). Yani `p̂ = −iħ∇`
bir tercih değil, zorunluluktur.

**3. Kinetik enerji operatörünü kur.**
Klasik ifadede p yerine p̂ koyarız:
    T̂ = p̂²/(2m) = (−iħ∇)·(−iħ∇)/(2m) = −ħ²∇²/(2m)
Çünkü (−i)² = −1. Tek boyutta:
    T̂ = −(ħ²/2m) ∂²/∂x²

**4. Hamiltonyeni tamamla.**
Klasik Hamilton fonksiyonu H = T + V idi. Aynı yerine koymayla
    Ĥ = T̂ + V̂ = −(ħ²/2m)∇² + V(r)
ve Ĥψ = Eψ yazınca zamandan bağımsız Schrödinger denklemi çıkar:
    −(ħ²/2m)∇²ψ + Vψ = Eψ

**Sağlaması:** Serbest parçacıkta V = 0 ve ψ = e^(ikx) alalım.
    −(ħ²/2m)(ik)²ψ = (ħ²k²/2m)ψ
Yani E = ħ²k²/2m = p²/2m — başladığımız klasik ifade. Çember kapandı.

**Bu geçişin adı ve kuralı:** Kanonik kuantumlama. Dirac'ın kuralıyla
    {A,B}_Poisson → [Â,B̂]/(iħ)
Klasik {x,p} = 1 bağıntısı, kuantum [x̂,p̂] = iħ olur. Belirsizlik
ilkesi bu komütatörden çıkar; ayrı bir varsayım değildir.

**Nerede dikkat:** Klasik ifadede çarpım sırası önemsizdir (xp = px),
operatörlerde değildir (x̂p̂ ≠ p̂x̂). Bu yüzden bazı büyüklüklerde
sıralama belirsizliği doğar ve simetrik (Weyl) sıralama seçilir.
Kanonik kuantumlama bir TÜREV değil, bir REÇETEDİR; doğruluğu
deneyle sınanır ve bugüne kadar sınavı geçmiştir.
""", """
How does the number Ek = mv^2/2 become the operator T = -(hbar^2/2m) del^2?

0. Why operators at all? Classically a state is the pair (x, p) and every
   observable is a FUNCTION of it, returning a number. In quantum
   mechanics the state is a vector in a Hilbert space, and measurements
   can yield a SET of values (two beams in Stern-Gerlach, discrete atomic
   lines). The object that acts on a vector and carries a set of possible
   values is a LINEAR OPERATOR, whose eigenvalues are the outcomes; it
   must be Hermitian for those to be real. So observables are operators
   because states are vectors — the steps below only fix WHICH operator.
1. Write it with momentum: Ek = p^2/2m.
2. Read the momentum operator off a de Broglie plane wave: with
   psi = exp(i(kx - wt)) and p = hbar k, we get -i hbar d(psi)/dx = p psi,
   so p_hat = -i hbar d/dx. The plane wave alone is not the full
   justification: p_hat is the unique linear operator consistent with
   de Broglie, with translation symmetry (momentum generates
   translations, T(a) = exp(-i a p/hbar)) and with [x,p] = i hbar
   (Stone-von Neumann).
3. Substitute: T = p_hat^2/2m = -(hbar^2/2m) del^2.
4. Add the potential: H = T + V gives the Schrodinger equation.

Check: for a free particle this returns E = p^2/2m, the classical
expression. The rule is canonical quantisation, with Dirac's
correspondence {A,B} -> [A,B]/(i hbar); the uncertainty principle then
follows from [x,p] = i hbar rather than being a separate postulate.
""",
  eqs=["Ek = p²/2m", "p̂ = −iħ∇", "T̂ = −(ħ²/2m)∇²",
       "Ĥ = −(ħ²/2m)∇² + V", "[x̂,p̂] = iħ"],
  ex_tr=["Sonsuz kuyuda sağlama: ψ_n = √(2/L)·sin(nπx/L). "
         "T̂ψ = −(ħ²/2m)·(−n²π²/L²)ψ = (n²π²ħ²/2mL²)ψ. "
         "Yani E_n = n²π²ħ²/(2mL²) = n²h²/(8mL²) — sonsuz kuyunun "
         "bilinen enerji düzeyleri. Operatörü klasik ifadeden kurduk, "
         "sonuç deneyle uyuşan spektrumu verdi."],
  ex_en=["For the infinite well the same operator yields "
         "E_n = n^2 h^2/(8 m L^2), the standard spectrum."],
  kw="klasik kinetik enerjiden kuantum operatorune|"
     "kinetik enerji operatoru|hamiltonyan operatoru|"
     "hamiltonyen operatoru|momentum operatoru|kanonik kuantumlama|"
     "klasik fizikten kuantuma gecis|schrodinger denklemi nasil cikar|"
     "schrodinger denklemi nereden gelir|"
     "schrodinger denklemi nereden geliyor|"
     "schrodinger denklemi nasil elde edilir|"
     "schrodinger denkleminin turetilmesi|"
     "klasik ile kuantum arasindaki gecis|operator karsiligi|"
     "canonical quantization|momentum operator|kinetic energy operator|"
     "hamiltonian operator|from classical to quantum",
  related="kuantum_formalizm|hermit_operator|kanonik_donusum|kuantum_temelleri"),

T("klasik_limit", "Kuantumdan Klasiğe: Karşılık Gelme İlkesi",
  "From Quantum to Classical: the Correspondence Principle", """
Kuantum mekaniği doğruysa, günlük ölçekte neden klasik fizik işliyor?

**Ehrenfest teoremi:** Beklenen değerler klasik denklemlere uyar:
    d⟨x⟩/dt = ⟨p⟩/m,    d⟨p⟩/dt = −⟨∂V/∂x⟩
Yani dalga paketinin MERKEZİ, Newton'un ikinci yasasına göre hareket
eder. Klasik yörünge, kuantum beklenen değerinin yörüngesidir.

**Neden fark etmiyoruz:** Bir toz tanesinin (m = 10⁻⁹ kg, v = 10⁻³ m/s)
de Broglie dalga boyu λ = h/mv ≈ 6,6×10⁻²² m'dir — atom çekirdeğinden
bile milyar kat küçük. Girişim etkileri gözlenemez.

**ħ → 0 limiti:** Formüllerde ħ'yi sıfıra götürmek klasik sonucu verir.
Örneğin sonsuz kuyuda düzeyler arası aralık ħ² ile orantılıdır; ħ küçüldükçe
enerji basamakları sıklaşır ve süreklilik gibi görünür.

**WKB yaklaşımı:** Potansiyel dalga boyuna göre yavaş değişiyorsa
ψ ≈ A·e^(iS/ħ) yazılır; S burada klasik ETKİDİR. Bu ifadeyi Schrödinger
denklemine koyup ħ→0 alınca Hamilton-Jacobi denklemi çıkar — klasik
mekaniğin en soyut biçimi. Dalga mekaniği ile klasik mekanik arasındaki
bağ tam olarak burada görünür.

**Ters yön de doğrudur:** Klasik mekanik, kuantum mekaniğinin
ħ→0 limitidir; ama kuantum mekaniği klasikten TÜRETİLEMEZ. Kanonik
kuantumlama bir reçetedir, bir ispat değil.
""", """
If quantum mechanics is right, why does classical physics work at our
scale? Ehrenfest's theorem shows expectation values obey the classical
equations. A dust grain's de Broglie wavelength is ~1e-21 m, far too
small for interference. Taking hbar -> 0 in the WKB form psi ~ exp(iS/hbar)
turns the Schrodinger equation into the Hamilton-Jacobi equation. The
classical limit follows from quantum theory, but not the reverse.
""",
  eqs=["d⟨x⟩/dt = ⟨p⟩/m", "d⟨p⟩/dt = −⟨∂V/∂x⟩", "ψ ≈ A·e^(iS/ħ)",
       "λ = h/(mv)"],
  ex_tr=["1 gramlık bir bilye 1 m/s ile giderken λ = h/mv = "
         "6,63×10⁻³⁴/(10⁻³·1) = 6,63×10⁻³¹ m. Bir atomun çapı "
         "10⁻¹⁰ m; oran 10⁻²¹. Bu yüzden bilye için kırınım deseni "
         "hiçbir zaman gözlenemez."],
  ex_en=["A 1 g marble at 1 m/s has a de Broglie wavelength of 6.6e-31 m, "
         "1e21 times smaller than an atom."],
  kw="klasik limit|karsilik gelme ilkesi|ehrenfest teoremi|"
     "kuantumdan klasige|neden klasik fizik isliyor|wkb yaklasimi|"
     "hbar sifira giderken|correspondence principle|classical limit|"
     "ehrenfest theorem|"
     "buyuk cisimlerde kuantum|makroskopik olcekte kuantum|"
     "gunluk olcekte kuantum|kuantum etkileri neden gorunmez|"
     "neden kuantum etkilerini gormuyoruz|buyuk cisimlerde gorunmuyor|"
     "kuantum neden gunluk hayatta yok|why don't we see quantum effects|"
     "macroscopic limit",
  related="kanonik_kuantumlama|kuantum_formalizm|varyasyonel_yontem"),

T("lagrange_hamilton_gecis",
  "Lagrange'dan Hamilton'a: Legendre Dönüşümü",
  "From Lagrange to Hamilton: the Legendre Transform", """
Lagrange formalizminde temel değişkenler (q, q̇); Hamilton formalizminde
(q, p). İkisi arasındaki geçiş bir LEGENDRE DÖNÜŞÜMÜDÜR.

**1. Eşlenik momentumu tanımla.**
    p_i = ∂L/∂q̇_i
Bu, "momentum" adının en genel hâlidir: kartezyende p = mv çıkar, ama
kutupsalda açısal koordinatın eşleniği açısal momentumdur.

**2. Legendre dönüşümünü uygula.**
    H(q, p, t) = Σ p_i q̇_i − L(q, q̇, t)
Burada q̇, adım 1'deki bağıntı ters çevrilerek p cinsinden yazılır.
Dönüşümün anlamı: bağımsız değişkeni q̇'dan p'ye çevirmek.

**3. Hamilton denklemlerini çıkar.**
H'nin tam diferansiyelini alıp Euler-Lagrange denklemini
(ṗ_i = ∂L/∂q_i) kullanınca
    q̇_i = ∂H/∂p_i,     ṗ_i = −∂H/∂q_i
İki tane ikinci mertebeden denklem yerine, 2n tane BİRİNCİ mertebeden
denklem elde edilir. Faz uzayı (q,p) resmi buradan doğar.

**Ne zaman H = E?** İki koşul birlikte sağlanırsa: bağlar zamandan
bağımsızsa (skleronom) ve potansiyel hıza bağlı değilse. O zaman
H = T + V. Aksi hâlde H yine korunabilir ama toplam enerji olmayabilir —
sık yapılan hata budur.

**Neden geçilir?** Hamilton biçimi kanonik dönüşümlere, Poisson
parantezlerine, Liouville teoremine ve kuantum mekaniğine açılır.
Kuantumlama Lagrange'dan değil, Hamilton'dan yapılır: klasik {q,p} = 1
bağıntısı [q̂,p̂] = iħ olur.
""", """
Lagrangian mechanics uses (q, qdot); Hamiltonian mechanics uses (q, p).
The bridge is a Legendre transform: define p = dL/d(qdot), then
H = sum(p qdot) - L, which yields qdot = dH/dp and pdot = -dH/dq. H equals
the total energy only when the constraints are time independent and the
potential is velocity independent. The Hamiltonian form is the one that
quantises: {q,p} = 1 becomes [q,p] = i hbar.
""",
  eqs=["p = ∂L/∂q̇", "H = Σ p q̇ − L", "q̇ = ∂H/∂p", "ṗ = −∂H/∂q"],
  ex_tr=["Yay-kütle: L = ½mẋ² − ½kx². p = ∂L/∂ẋ = mẋ ⇒ ẋ = p/m. "
         "H = pẋ − L = p²/m − (p²/2m − ½kx²) = p²/2m + ½kx². "
         "Hamilton denklemleri: ẋ = p/m, ṗ = −kx ⇒ mẍ = −kx. "
         "Newton'un sonucu geri geldi."],
  ex_en=["Spring-mass: L = m xdot^2/2 - k x^2/2 gives H = p^2/2m + k x^2/2 "
         "and the Hamilton equations reproduce m xddot = -k x."],
  kw="lagrangedan hamiltona|lagrange ile hamilton arasindaki|"
     "legendre donusumu|eslenik momentum|hamilton denklemleri nasil cikar|"
     "lagrange hamilton gecisi|hamiltonyen nasil elde edilir|"
     "faz uzayi neden|h ne zaman enerjiye esittir|"
     "legendre transform|from lagrangian to hamiltonian|"
     "conjugate momentum|hamilton equations derivation",
  related="lagrange|kanonik_donusum|kanonik_kuantumlama"),

T("newton_gorelilik_gecis",
  "Newton Mekaniğinden Göreliliğe Geçiş",
  "From Newtonian Mechanics to Relativity", """
Newton mekaniği yanlış değildir; SINIRLI geçerlidir. Sınırı görmek için
göreli ifadelerin düşük hızdaki açılımına bakmak yeter.

**Momentum:** p = γmv, γ = 1/√(1−v²/c²).
v ≪ c için γ ≈ 1 + v²/2c² olduğundan
    p ≈ mv(1 + v²/2c²) ≈ mv
Newton momentumu, göreli momentumun birinci terimidir.

**Enerji:** E = γmc². Aynı açılımla
    E ≈ mc² + ½mv² + (3/8)mv⁴/c² + …
İkinci terim tam olarak klasik kinetik enerjidir. Birinci terim (mc²)
klasik fizikte görünmez çünkü sabittir ve enerji farkları ölçülür.

**Ne zaman gerekli:** v = 0,1c'de γ = 1,005 — binde beş hata. v = 0,9c'de
γ = 2,29 — Newton mekaniği tamamen yanlış sonuç verir. GPS uydularının
hızı 3,9 km/s'dir (v/c ≈ 1,3×10⁻⁵) ama nanosaniye hassasiyeti
gerektiği için düzeltme yine de şarttır.

**Ders:** Yeni bir kuram, eskisini çürütmez; onu bir LIMIT olarak
içerir. Aynı ilişki kuantum-klasik arasında da vardır.
""", """
Newtonian mechanics is not wrong; it is a limit. Expanding relativistic
momentum and energy for v << c gives p ≈ mv and E ≈ mc^2 + mv^2/2, so the
classical expressions are the leading terms. At v = 0.1c gamma is 1.005;
at 0.9c it is 2.29 and Newton fails outright.
""",
  eqs=["p = γmv", "E = γmc² ≈ mc² + ½mv²", "γ ≈ 1 + v²/2c²"],
  ex_tr=["v = 0,1c için γ = 1/√(1−0,01) = 1,00504. Klasik kinetik enerji "
         "½mv² = 0,005mc²; göreli değer (γ−1)mc² = 0,00504mc². Fark "
         "binde 8. v = 0,5c'de γ = 1,155 ve fark %19'a çıkar — artık "
         "Newton kullanılamaz."],
  ex_en=["At 0.1c the classical and relativistic kinetic energies differ "
         "by 0.8%; at 0.5c by 19%."],
  kw="newtondan gorelilige gecis|klasik momentumun goreli hali|"
     "goreli enerji acilimi|newton ne zaman yetersiz|dusuk hiz limiti|"
     "newtonian limit of relativity|low speed limit|"
     "klasik momentum ile goreli momentum|goreli momentum nedir|"
     "relativistic momentum",
  related="ozel_gorelilik|newton_yasalari|momentum_korunumu|"
          "kanonik_kuantumlama"),
]
