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

Bu koşulları birlikte sağlayan başka bir seçim yoktur — ama iddiayı
doğru kurmak gerekir. **Stone-von Neumann teoremi** "başka operatör
yoktur" demez; şunu der: kanonik komütasyon bağıntılarının (Weyl
biçiminde, sürekli ve indirgenemez) her temsili, Schrödinger temsiline
**üniter eşdeğerdir**. Yani `x̂`yi çarpma, `p̂`yi `−iħ∇` alan gösterim
tek olası gösterim değil, tek olası gösterim SINIFIDIR; ötekiler ondan
bir üniter dönüşümle elde edilir ve aynı fiziği verir (momentum
uzayındaki gösterim buna örnektir). Bu anlamda `p̂ = −iħ∇` keyfi bir
tercih değildir; fizikçe farklı bir seçenek yoktur.

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
   translations, T(a) = exp(-i a p/hbar)) and with [x,p] = i hbar.
   Stone-von Neumann does not say "no other operator exists": it says
   every continuous irreducible representation of the CCR in Weyl form
   is unitarily EQUIVALENT to the Schrodinger one. So the choice is
   unique up to unitary equivalence, not literally unique.
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

T("potansiyel_operatoru",
  "Newton Kuvvetinden Potansiyel Enerji Operatörüne",
  "From Newton's Force to the Potential Energy Operator", """
Hamiltonyende kinetik terim `−(ħ²/2m)∇²` gibi bir TÜREV operatörüyken,
potansiyel terim neden sadece `V(x)` ile ÇARPMA? Soru budur, ve cevabı
Newton'un ikinci yasasına kadar geri gider.

**1. Kuvvetten potansiyel enerjiye (klasik uç).**
Newton: `F = ma = dp/dt`. Bir kuvvetin potansiyeli olabilmesi için
KORUNUMLU olması gerekir; üç ifade birbirine denktir:
    ∮F·dr = 0   ⇔   ∇×F = 0   ⇔   F = −∇V
Son adım Poincaré önermesidir: rotasyoneli sıfır olan alan bir skalerin
gradyanıdır. Potansiyel enerji o skalerdir:
    V(r) = −∫F·dr
Eksi işaret bir tanım seçimidir; kuvvetin V'nin AZALDIĞI yöne bakması
için konur. Buradan enerji korunumu çıkar:
    dE/dt = d/dt(½mv² + V) = mv·a + ∇V·v = v·(F + ∇V) = 0

**2. Klasik Hamilton fonksiyonu.**
    H(x,p) = p²/(2m) + V(x)
Dikkat: `V` yalnızca KONUMUN fonksiyonudur, momentum içermez. Bütün
mesele bu tek gözlemde saklıdır.

**3. Kuantumlama: hangi terim hangi operatöre gider?**
Kanonik kuantumlama `x → x̂`, `p → p̂` der; klasik ifadedeki her
değişkenin yerine operatörü konur. O hâlde
    V(x) → V̂ = V(x̂)
Bir operatörün fonksiyonu, spektral teoremle özdurumları üzerinden
tanımlanır: `V(x̂)|x₀⟩ = V(x₀)|x₀⟩`.

**4. Konum gösteriminde `x̂` neden çarpmadır?**
Konum özdurumu `|x₀⟩`, `x̂|x₀⟩ = x₀|x₀⟩` sağlar; dalga fonksiyonu bu
tabana açılımın katsayısıdır: `ψ(x) = ⟨x|ψ⟩`. O hâlde
    ⟨x|x̂|ψ⟩ = x⟨x|ψ⟩ = x·ψ(x)
Yani konum gösteriminde `x̂` işlemi "x ile çarp"tır. Bu bir varsayım
değil, `ψ(x)`in TANIMININ doğrudan sonucudur.

**5. Sonuç: `V̂` saf çarpma operatörüdür.**
    V̂ψ(x) = V(x)·ψ(x)
Türev yoktur, olamaz da. **Türev nereden geliyordu?** Yalnızca `p̂`den:
`p̂` ötelemenin üretecidir ve üreteç türevdir. Klasik bir büyüklük
momentuma bağlıysa kuantum karşılığında türev belirir; bağlı değilse
belirmez. `V` momentum içermediği için `V̂` türev içermez. Kinetik terim
`p²` taşıdığı için iki kez türev (`∇²`) taşır. Aradaki fark tam olarak
budur.

**6. Hermitlik sağlaması.**
`V(x)` gerçel ise:
    ⟨φ|V̂ψ⟩ = ∫φ*(Vψ)dx = ∫(Vφ)*ψ dx = ⟨V̂φ|ψ⟩
Çarpma operatörü kendiliğinden Hermit'tir; enerji özdeğerlerinin gerçel
çıkması bunu gerektirir. (Karmaşık `V` kullanılan yerler vardır —
soğurucu potansiyeller — ama o zaman olasılık bilerek korunmaz.)

**7. Çember kapanıyor: Newton'a geri dönüş.**
Ehrenfest teoremi beklenen değerler için şunu verir:
    d⟨p̂⟩/dt = −⟨∇V⟩ = ⟨F⟩
Yani `V̂`yi çarpma operatörü olarak koyduğumuzda, kuantum denklemi tam
olarak Newton'un ikinci yasasını beklenen değerler düzeyinde geri
üretir. Başlangıç noktamız `F = −∇V` idi; vardığımız yer `d⟨p⟩/dt = ⟨F⟩`.
Seçimin doğruluğunun kanıtı budur.

**8. Nerede dikkat: "çarpma olmak" TABANA bağlıdır.**
`V̂` yalnızca KONUM gösteriminde çarpmadır. Momentum gösteriminde `p̂`
çarpma olur, `x̂` ise `iħ∂/∂p` türevine döner ve `V̂` bir KATLAMA
(konvolüsyon) operatörü hâline gelir:
    (V̂φ)(p) = ∫Ṽ(p−p′)φ(p′)dp′/(2πħ)
Yani "potansiyel çarpma operatörüdür" cümlesi mutlak değil, konum
tabanına göre söylenmiş bir cümledir. Simetrik gerçek şudur: her taban,
kendi değişkenini çarpmaya, eşlenik değişkenini türeve çevirir.

**Tam Hamiltonyen:**
    Ĥ = T̂ + V̂ = −(ħ²/2m)∇² + V(x)
    iħ ∂ψ/∂t = [−(ħ²/2m)∇² + V(x)]ψ
""", """
Why is the kinetic term a derivative operator while the potential term is
just multiplication by V(x)?

1. Newton: F = ma. A force has a potential only if it is conservative;
   equivalently curl F = 0, hence F = -grad V, with V = -int F.dr.
2. The classical Hamiltonian is H = p^2/2m + V(x). Crucially V depends on
   position ALONE.
3. Canonical quantisation replaces x -> x_hat, p -> p_hat, so V -> V(x_hat),
   defined through the spectral theorem.
4. In the position representation psi(x) = <x|psi>, so <x|x_hat|psi> = x psi(x):
   x_hat acts by multiplication. This follows from the definition of psi(x).
5. Hence V_hat psi(x) = V(x) psi(x), with no derivative. Derivatives enter only
   through p_hat, the generator of translations; V carries no momentum
   dependence, so it carries no derivative. The kinetic term carries p^2 and
   therefore two derivatives.
6. Multiplication by a real V is automatically Hermitian.
7. Ehrenfest closes the circle: d<p>/dt = -<grad V> = <F>, recovering Newton's
   second law for expectation values.
8. Caveat: "multiplication" is basis dependent. In the momentum representation
   p_hat multiplies, x_hat becomes i hbar d/dp, and V_hat becomes a convolution.
""",
  eqs=["F = −∇V", "V(r) = −∫F·dr", "∇×F = 0", "H = p²/2m + V(x)",
       "V̂ψ(x) = V(x)ψ(x)", "d⟨p̂⟩/dt = −⟨∇V⟩ = ⟨F⟩",
       "Ĥ = −(ħ²/2m)∇² + V(x)"],
  ex_tr=["Harmonik salınıcı: F = −kx korunumludur, V = ½kx². "
         "Hamiltonyen Ĥ = −(ħ²/2m)d²/dx² + ½kx² olur; ikinci terim "
         "türev değil, ½kx² ile çarpmadır. Ehrenfest sağlaması: "
         "d⟨p⟩/dt = −k⟨x⟩, yani beklenen değerler tam olarak klasik "
         "yay denklemini izler — kuantum salınıcının merkezinin klasik "
         "gibi salınmasının sebebi budur."],
  ex_en=["Harmonic oscillator: F = -kx gives V = kx^2/2, so the potential "
         "term multiplies by kx^2/2 while Ehrenfest returns d<p>/dt = -k<x>."],
  kw="potansiyel enerji operatoru|potansiyel operatoru|"
     "potansiyel enerji terimi|carpma operatoru|"
     "potansiyel neden carpma operatoru|"
     "newton ikinci yasasindan schrodinger|"
     "kuvvetten potansiyel enerjiye|kuvvet ve potansiyel enerji|"
     "korunumlu kuvvet potansiyel|potansiyel enerji nereden gelir|"
     "hamiltonyende potansiyel terim|hamiltonyen potansiyel enerji|"
     "V(x) operatoru|neden turev degil carpma|"
     "konum gosteriminde carpma|"
     "potential energy operator|multiplication operator|"
     "why is the potential a multiplication operator|"
     "from newtons second law to schrodinger",
  related="kanonik_kuantumlama|kuantum_formalizm|hermit_operator|"
          "klasik_limit|is_enerji"),

T("poisson_komutator",
  "Poisson Parantezinden Komütatöre ve Belirsizlik İlkesine",
  "From the Poisson Bracket to the Commutator and the Uncertainty Principle", """
Klasik mekaniğin cebiri ile kuantum mekaniğinin cebiri arasındaki köprü
budur. Zincir şudur: **Poisson parantezi → komütatör → [x̂,p̂] = iħ →
Δx·Δp ≥ ħ/2.** Her halkayı ayrı ayrı kuralım.

**1. Klasik faz uzayı ve Poisson parantezi.**
Klasik bir sistemin DURUMU, 2N boyutlu faz uzayında bir NOKTADIR:
`(q₁…q_N, p₁…p_N)`. Gözlenebilirler bu uzayda tanımlı FONKSİYONLARDIR.
İki gözlenebilirin Poisson parantezi:
    {A,B} = Σᵢ (∂A/∂qᵢ · ∂B/∂pᵢ − ∂A/∂pᵢ · ∂B/∂qᵢ)

**2. Temel parantez.**
`A = q`, `B = p` alalım. `∂q/∂q = 1`, `∂p/∂p = 1`, `∂q/∂p = 0`,
`∂p/∂q = 0` olduğundan:
    {q,p} = 1·1 − 0·0 = **1**
Genel olarak `{qᵢ,pⱼ} = δᵢⱼ`, `{qᵢ,qⱼ} = {pᵢ,pⱼ} = 0`.

**3. Poisson parantezi zaman evrimini yönetir.**
    dA/dt = {A,H} + ∂A/∂t
Hamilton denklemleri bunun özel hâlleridir:
    q̇ = {q,H} = ∂H/∂p,     ṗ = {p,H} = −∂H/∂q
Yani klasik mekaniğin BÜTÜN dinamiği bu paranteze yüklüdür.

**4. Parantezin cebirsel yapısı — asıl ipucu.**
Poisson parantezi dört özelliğe sahiptir:
    (i)   Ters simetri: {A,B} = −{B,A}
    (ii)  İki-doğrusallık: {aA+bB, C} = a{A,C} + b{B,C}
    (iii) Leibniz (çarpım kuralı): {AB,C} = A{B,C} + {A,C}B
    (iv)  Jacobi: {A,{B,C}} + {B,{C,A}} + {C,{A,B}} = 0
Bu dört özellik, faz uzayı fonksiyonlarını bir **Lie cebiri** yapar.

**5. Dirac'ın gözlemi.**
Operatörlerin komütatörü `[Â,B̂] = ÂB̂ − B̂Â` de TAM OLARAK aynı dört
özelliği sağlar — ters simetri, iki-doğrusallık, Leibniz, Jacobi. İki
farklı matematiksel nesne, aynı cebirsel iskelet.

Dirac buradan şunu önerdi: kuantumlama, bu Lie cebirini KORUYAN bir
eşlemedir.
    {A,B} → [Â,B̂]/(iħ)

**`iħ` çarpanı neden zorunlu?** İki gerekçe:
  * **Hermitlik:** Â ve B̂ Hermit ise `[Â,B̂]† = (ÂB̂−B̂Â)† = B̂Â−ÂB̂
    = −[Â,B̂]`, yani komütatör ANTİ-Hermit'tir. Gözlenebilir olması için
    `i`ye bölmek gerekir: `[Â,B̂]/i` Hermit olur.
  * **Boyut:** `{A,B}` niceliğinin boyutu `[A][B]/(etki)`dir, `[Â,B̂]`
    niceliğininki `[A][B]`. Aradaki farkı kapatan sabitin boyutu ETKİ
    (enerji×zaman) olmalıdır — bu ħ'dir.

**6. Kanonik komütasyon bağıntısı.**
`{q,p} = 1` sonucunu kurala sokalım:
    [x̂,p̂] = iħ·{x,p} = **iħ**

**Doğrudan sağlaması** (konum gösterimi, keyfi ψ üzerinde):
    x̂p̂ψ = x·(−iħ ∂ψ/∂x) = −iħx ψ′
    p̂x̂ψ = −iħ ∂(xψ)/∂x = −iħ(ψ + xψ′)
    (x̂p̂ − p̂x̂)ψ = −iħxψ′ + iħψ + iħxψ′ = **iħψ**   ∎
Yani bağıntı yalnızca varsayılmış değil, operatörlerin kendisinden
hesaplanmıştır.

**7. Konum ve momentum neden DEĞİŞMELİ değil?**
Cebirsel cevap yukarıdadır; fiziksel cevap şudur: `p̂` uzayda ötelemenin
üretecidir. "Önce ötele, sonra konumu ölç" ile "önce konumu ölç, sonra
ötele" aynı şey değildir — ilkinde okuduğun değer `x`, ikincisinde
`x+a`dır. İki işlemin sırası fiziksel olarak fark ettiği için
operatörleri de değişmez.

**8. Faz uzayından Hilbert uzayına.**
Geçişin tablosu:
    Klasik                        Kuantum
    durum = faz uzayında nokta →  durum = Hilbert uzayında vektör |ψ⟩
    gözlenebilir = fonksiyon   →  gözlenebilir = Hermit operatör
    {A,B}                      →  [Â,B̂]/(iħ)
    dA/dt = {A,H}              →  dÂ/dt = [Â,Ĥ]/(iħ)   (Heisenberg resmi)
Son satır dikkat çekicidir: kuantum hareket denklemi, klasik olanın
birebir aynısıdır — yalnızca parantez değişmiştir.

**9. Belirsizlik ilkesi — Robertson türetimi.**
Şimdi zincirin son halkası. Â, B̂ Hermit; `|ψ⟩` normlu olsun. Sapma
operatörlerini tanımlayalım:
    |f⟩ = (Â − ⟨Â⟩)|ψ⟩,     |g⟩ = (B̂ − ⟨B̂⟩)|ψ⟩
Tanım gereği `⟨f|f⟩ = (ΔA)²` ve `⟨g|g⟩ = (ΔB)²`.

**Cauchy-Schwarz eşitsizliği:**
    ⟨f|f⟩·⟨g|g⟩ ≥ |⟨f|g⟩|²
yani
    (ΔA)²(ΔB)² ≥ |⟨f|g⟩|²

`z = ⟨f|g⟩` yazalım. Her karmaşık sayı için `|z|² = (Re z)² + (Im z)²`,
dolayısıyla `|z|² ≥ (Im z)²`. Sanal kısmı hesaplayalım:
    Im z = (z − z*)/(2i) = (⟨f|g⟩ − ⟨g|f⟩)/(2i)
Açalım:
    ⟨f|g⟩ = ⟨ψ|(Â−⟨Â⟩)(B̂−⟨B̂⟩)|ψ⟩ = ⟨ÂB̂⟩ − ⟨Â⟩⟨B̂⟩
    ⟨g|f⟩ = ⟨B̂Â⟩ − ⟨Â⟩⟨B̂⟩
Farkları ortalama terimleri götürür:
    ⟨f|g⟩ − ⟨g|f⟩ = ⟨ÂB̂⟩ − ⟨B̂Â⟩ = ⟨[Â,B̂]⟩
O hâlde `Im z = ⟨[Â,B̂]⟩/(2i)` ve
    (ΔA)²(ΔB)² ≥ |⟨[Â,B̂]⟩/(2i)|² = ¼|⟨[Â,B̂]⟩|²
Karekök alalım:
    **ΔA·ΔB ≥ ½|⟨[Â,B̂]⟩|**   (Robertson eşitsizliği)  ∎

**10. Heisenberg bağıntısı.**
`Â = x̂`, `B̂ = p̂` koyalım; 6. adımdan `[x̂,p̂] = iħ` (bir sayı, durumdan
bağımsız):
    Δx·Δp ≥ ½|iħ| = **ħ/2**   ∎

Zincir tamamlandı: `{x,p} = 1` → `[x̂,p̂] = iħ` → `Δx·Δp ≥ ħ/2`.
**Belirsizlik ilkesi bir postülat değildir**; klasik faz uzayının
cebirsel yapısı kuantumlanınca kendiliğinden çıkan bir SONUÇTUR. Fiziksel
okuması da açıktır: değişmeyen iki gözlenebilirin ortak özdurumu
yoktur, dolayısıyla ikisinin birden keskin olduğu bir durum yoktur.

**11. Kuralın sınırı (dürüst not).**
Dirac kuralı tam bir cebir eşyapısı DEĞİLDİR. **Groenewold-van Hove
teoremi**: bütün Poisson parantezlerini birebir komütatörlere taşıyan
bir kuantumlama eşlemesi, derecesi 3 ve üstü polinomlar için mevcut
değildir. Sebebi sıralama belirsizliğidir: klasikte `xp = px`, kuantumda
`x̂p̂ ≠ p̂x̂` olduğu için `xp` niceliğinin karşılığı seçim ister
(simetrik/Weyl sıralaması). Kural, kanonik çift için KESİN, genel
gözlenebilirler için ħ'nin birinci mertebesinde geçerlidir.
""", """
The chain is: Poisson bracket -> commutator -> [x,p] = i hbar -> dx dp >= hbar/2.

1. Classical states are points in a 2N-dimensional phase space and observables
   are functions on it. {A,B} = sum_i (dA/dq_i dB/dp_i - dA/dp_i dB/dq_i).
2. Directly, {q,p} = 1 and {q_i,p_j} = delta_ij.
3. Dynamics: dA/dt = {A,H}; Hamilton's equations are special cases.
4. The bracket is antisymmetric, bilinear, obeys Leibniz and Jacobi - a Lie
   algebra.
5. The commutator [A,B] = AB - BA satisfies exactly the same four properties,
   so Dirac proposed the structure-preserving map {A,B} -> [A,B]/(i hbar).
   The i is needed because a commutator of Hermitian operators is
   anti-Hermitian; hbar is needed because the bracket carries one inverse
   power of action.
6. Hence [x,p] = i hbar, which is verified directly:
   (xp - px)psi = -i hbar x psi' + i hbar(psi + x psi') = i hbar psi.
7. They fail to commute because p generates translations: translating then
   measuring position differs from measuring then translating.
8. Robertson: with |f> = (A - <A>)|psi> and |g> = (B - <B>)|psi>,
   Cauchy-Schwarz gives (dA)^2(dB)^2 >= |<f|g>|^2 >= (Im<f|g>)^2, and
   <f|g> - <g|f> = <[A,B]>, so dA dB >= |<[A,B]>|/2.
9. With A = x, B = p this gives dx dp >= hbar/2. The uncertainty principle is
   a consequence, not a postulate.
10. Caveat: by the Groenewold-van Hove theorem no quantisation map reproduces
    all Poisson brackets exactly beyond quadratic order; ordering ambiguities
    (Weyl) appear. The rule is exact for the canonical pair.
""",
  eqs=["{A,B} = Σ(∂A/∂q·∂B/∂p − ∂A/∂p·∂B/∂q)", "{q,p} = 1",
       "dA/dt = {A,H}", "{A,B} → [Â,B̂]/(iħ)", "[x̂,p̂] = iħ",
       "ΔA·ΔB ≥ ½|⟨[Â,B̂]⟩|", "Δx·Δp ≥ ħ/2"],
  ex_tr=["Açısal momentumda sağlama: klasik {Lₓ,L_y} = L_z parantezi "
         "Dirac kuralıyla [L̂ₓ,L̂_y] = iħL̂_z olur. Robertson eşitsizliği "
         "ΔLₓ·ΔL_y ≥ (ħ/2)|⟨L̂_z⟩| verir — açısal momentumun iki bileşeni "
         "üçüncüsü sıfırdan farklıyken aynı anda keskin olamaz. "
         "Kuantum sayılarının neden tek bir eksen (genelde z) üzerinden "
         "verildiğinin sebebi budur."],
  ex_en=["Angular momentum: {Lx,Ly} = Lz becomes [Lx,Ly] = i hbar Lz, and "
         "Robertson gives dLx dLy >= (hbar/2)|<Lz>|, which is why only one "
         "component is quantised alongside L^2."],
  kw="poisson parantezi|poisson brackets|poisson parantezinden komutatore|"
     "komutator bagintisi|komutator nasil elde edilir|"
     "kanonik komutasyon bagintisi|klasik faz uzayindan hilbert uzayina|"
     "faz uzayi hilbert uzayi gecis|dirac kuantumlama kurali|"
     "konum ve momentum neden degismeli degil|"
     "x ve p neden komut etmez|neden degismeli degil|"
     "belirsizlik ilkesi ispati|belirsizlik ilkesi turetimi|"
     "robertson esitsizligi|heisenberg belirsizlik ispat|"
     "belirsizlik ilkesi nereden cikar|komutatorden belirsizlik|"
     "groenewold van hove|weyl siralama|"
     "poisson bracket to commutator|canonical commutation relation|"
     "robertson inequality|derivation of uncertainty principle",
  related="kanonik_kuantumlama|kuantum_formalizm|hermit_operator|"
          "belirsizlik_ilkesi|lagrange_hamilton_gecis|kanonik_donusum"),

T("euler_lagrange_turetim",
  "En Küçük Etkiden Euler-Lagrange Denklemine",
  "From Least Action to the Euler-Lagrange Equation", """
Euler-Lagrange denklemi bir varsayım değildir; **en küçük etki
ilkesinden varyasyon hesabıyla TÜRETİLİR.** İspat şudur.

**1. Etki fonksiyoneli.**
Sistemin Lagrange fonksiyonu `L(q, q̇, t)` olsun. `t₁`den `t₂`ye giden
her YOL için bir sayı tanımlarız:
    S[q] = ∫_{t₁}^{t₂} L(q, q̇, t) dt
`S` bir fonksiyon değil FONKSİYONELDİR: girdisi bir sayı değil, bütün
bir `q(t)` yoludur.

**2. İlke.**
Hamilton ilkesi: gerçek yol, `S`yi DURAĞAN yapan yoldur.
    δS = 0
("En küçük" denir ama doğrusu duruğandır; minimum, maksimum ya da eyer
noktası olabilir.)

**3. Yolu varyasyona uğrat.**
Gerçek yol `q(t)` olsun. Komşu yolları tek bir parametreyle yazalım:
    q_ε(t) = q(t) + ε·η(t)
Burada `η(t)` keyfi düzgün bir fonksiyondur, ama **uçlar sabittir**:
    η(t₁) = η(t₂) = 0
Çünkü başlangıç ve bitiş noktalarını değiştirmiyoruz. Hızın varyasyonu:
    q̇_ε(t) = q̇(t) + ε·η̇(t)

**4. Etkiyi ε'ya göre türetle.**
    S(ε) = ∫ L(q + εη, q̇ + εη̇, t) dt
Duruğanlık koşulu `dS/dε|_{ε=0} = 0` demektir. Zincir kuralıyla:
    dS/dε|₀ = ∫ (∂L/∂q · η + ∂L/∂q̇ · η̇) dt = 0

**5. Kritik adım: PARÇALI İNTEGRASYON.**
İkinci terimde `η̇` var; `η`yi tek başına bırakmak için parçalı
integrasyon yaparız:
    ∫ (∂L/∂q̇)·η̇ dt = [ (∂L/∂q̇)·η ]_{t₁}^{t₂} − ∫ d/dt(∂L/∂q̇)·η dt
**Sınır terimi düşer**, çünkü 3. adımda `η(t₁) = η(t₂) = 0` koyduk. İşte
uçların sabit tutulmasının gerekçesi budur. Geriye:
    ∫ [ ∂L/∂q − d/dt(∂L/∂q̇) ] · η(t) dt = 0

**6. Varyasyon hesabının temel önermesi.**
`η(t)` KEYFİDİR. Sürekli bir `f(t)` için, uçlarda sıfırlanan her `η`
ile `∫f·η dt = 0` oluyorsa, zorunlu olarak `f(t) ≡ 0`dır. (Aksi hâlde
`f`nin sıfırdan farklı olduğu bir aralıkta `η`yi `f` ile aynı işaretli
seçip integrali sıfırdan farklı yapardık — çelişki.)

**7. Sonuç.**
    **d/dt(∂L/∂q̇) − ∂L/∂q = 0**   ∎
n serbestlik derecesi için her `qᵢ` bağımsız varyasyona uğratılır ve n
tane denklem çıkar.

**Sağlaması (Newton geri geliyor).**
Tek boyutta `L = ½mẋ² − V(x)`:
    ∂L/∂ẋ = mẋ,   d/dt(∂L/∂ẋ) = mẍ,   ∂L/∂x = −dV/dx = F
Denkleme koyarsak `mẍ − F = 0`, yani **F = ma**. Newton yasası, en küçük
etki ilkesinin bir sonucudur.

**Neden bu biçim daha güçlü?** Denklem koordinat seçimine göre biçim
değiştirmez (kutupsal, küresel, genelleştirilmiş koordinatlar aynı
kalıbı kullanır) ve bağ kuvvetleri hesaba hiç girmez. Ayrıca `L`nin bir
simetrisi varsa Noether teoremi doğrudan bir korunum yasası verir.
""", """
The Euler-Lagrange equation is derived, not assumed.

1. Action functional S[q] = int L(q, qdot, t) dt over a path.
2. Hamilton's principle: the true path makes S stationary, dS = 0.
3. Vary the path: q_eps = q + eps*eta with eta(t1) = eta(t2) = 0.
4. dS/deps at 0 = int (dL/dq * eta + dL/dqdot * etadot) dt = 0.
5. Integrate the second term by parts; the boundary term vanishes because
   eta vanishes at the endpoints, leaving
   int [dL/dq - d/dt(dL/dqdot)] eta dt = 0.
6. Since eta is arbitrary, the fundamental lemma of the calculus of
   variations forces the bracket to vanish.
7. Hence d/dt(dL/dqdot) - dL/dq = 0.

Check: L = m xdot^2/2 - V(x) returns m xddot = -dV/dx, i.e. F = ma.
""",
  eqs=["S[q] = ∫L(q,q̇,t)dt", "δS = 0", "q_ε = q + εη, η(t₁)=η(t₂)=0",
       "d/dt(∂L/∂q̇) − ∂L/∂q = 0"],
  ex_tr=["Serbest parçacık: L = ½mẋ². ∂L/∂x = 0 olduğundan "
         "d/dt(mẋ) = 0, yani mẋ = sabit — momentum korunur ve yol "
         "düz çizgidir. En küçük etki ilkesinin en yalın sonucu budur: "
         "kuvvet yoksa etkiyi durağan yapan yol doğrudur."],
  ex_en=["Free particle: L = m xdot^2/2 gives d/dt(m xdot) = 0, so momentum "
         "is conserved and the path is a straight line."],
  kw="euler lagrange denklemi turetimi|euler-lagrange turetimi|"
     "euler lagrange nasil elde edilir|euler lagrange ispati|"
     "en kucuk etki ilkesinden euler lagrange|"
     "lagrange fonksiyonundan euler lagrange|varyasyon hesabi turetim|"
     "etki fonksiyoneli varyasyon|hamilton ilkesi turetim|"
     "delta S = 0|parcali integrasyon varyasyon|"
     "varyasyon hesabinin temel onermesi|"
     "euler-lagrange equation derivation|principle of least action|"
     "calculus of variations derivation",
  related="varyasyon|lagrange|lagrange_hamilton_gecis|noether|"
          "hamilton_jacobi"),

T("hamilton_jacobi",
  "Hamilton-Jacobi Denklemi ve Dalga Fonksiyonuyla İlişkisi",
  "The Hamilton-Jacobi Equation and its Link to the Wave Function", """
Klasik mekaniğin kuantum mekaniğine EN ÇOK benzeyen biçimi budur.
Schrödinger'in denklemini bulurken izlediği yol da buydu.

**1. Kanonik dönüşüm fikri.**
Kanonik bir dönüşüm `(q,p) → (Q,P)`, üretici fonksiyon `S(q,P,t)` ile
tanımlanır:
    p = ∂S/∂q,     Q = ∂S/∂P,     K = H + ∂S/∂t
Burada `K` yeni Hamiltonyendir. Şimdi cesur bir soru: `K = 0` yapacak
bir dönüşüm seçebilir miyiz? Seçebilirsek yeni denklemler
`Q̇ = ∂K/∂P = 0`, `Ṗ = −∂K/∂Q = 0` olur — yani bütün yeni değişkenler
SABİTTİR ve hareket tamamen çözülmüş demektir.

**2. Hamilton-Jacobi denklemi.**
`K = 0` koşulunu yazalım:
    **H(q, ∂S/∂q, t) + ∂S/∂t = 0**
Bu, `S(q,t)` için bir kısmi diferansiyel denklemdir. Tek parçacık ve
`H = p²/2m + V` için açık biçimi:
    (1/2m)(∂S/∂x)² + V(x) + ∂S/∂t = 0

**3. `S` nedir? — ETKİNİN kendisidir.**
`dS/dt = ∂S/∂t + (∂S/∂q)q̇ = −H + pq̇ = L` olduğundan
    S = ∫L dt
Yani üretici fonksiyon, en küçük etki ilkesindeki ETKİDİR (Hamilton'un
asal fonksiyonu). Klasik mekanik böylece tek bir skaler alanın kısmi
diferansiyel denklemine indirgenir.

**4. Neden bu biçim dalgaları çağrıştırır?**
`S = sabit` yüzeyleri uzayda ilerleyen bir DALGA CEPHESİ gibi hareket
eder ve parçacık yörüngeleri bu cephelere diktir (`p = ∇S`). Bu, geometrik
optikteki ışın-dalga ilişkisinin tıpatıp aynısıdır: **Hamilton-Jacobi,
mekaniğin "geometrik optiği"dir.** Optikte ışınlar dalga denkleminin
kısa dalga boyu limitiyse, mekanikte de yörüngeler bir DALGA
denkleminin limiti olmalıdır. Schrödinger'in çıkış noktası buydu.

**5. Geçiş: `ψ = A·e^(iS/ħ)`.**
Dalga fonksiyonunu genlik ve fazla yazalım; fazın `S/ħ` olması boyut
gereğidir (`S` etki boyutundadır, `ħ` de öyle):
    ψ(x,t) = A(x,t)·e^(iS(x,t)/ħ)
Bunu zamana bağlı Schrödinger denklemine koyalım:
    iħ ∂ψ/∂t = −(ħ²/2m)∇²ψ + Vψ
Türevleri alalım:
    ∂ψ/∂t = (∂A/∂t + (i/ħ)A ∂S/∂t)·e^(iS/ħ)
    ∇ψ = (∇A + (i/ħ)A∇S)·e^(iS/ħ)
    ∇²ψ = (∇²A + (2i/ħ)∇A·∇S + (i/ħ)A∇²S − (1/ħ²)A(∇S)²)·e^(iS/ħ)
Yerine koyup `e^(iS/ħ)` sadeleşince, GERÇEL ve SANAL kısımlar iki ayrı
denklem verir:

  * **Gerçel kısım:**
        ∂S/∂t + (∇S)²/2m + V − (ħ²/2m)(∇²A/A) = 0
  * **Sanal kısım:**
        ∂A²/∂t + ∇·(A²∇S/m) = 0

**6. Klasik limit — çember kapanıyor.**
Gerçel kısımda `ħ → 0` alalım (ya da `A` yavaş değişiyorsa son terim
ihmal edilir):
    **∂S/∂t + (∇S)²/2m + V = 0**
Bu tam olarak 2. adımdaki Hamilton-Jacobi denklemidir. Yani:
**Schrödinger denklemi, klasik Hamilton-Jacobi denklemini `ħ → 0`
limitinde geri verir.** Atılan terim
    Q = −(ħ²/2m)(∇²A/A)
"kuantum potansiyeli" adını alır ve klasiklikten sapmanın tam ölçüsüdür.

Sanal kısım ise `ρ = A² = |ψ|²` ve `v = ∇S/m` yazılınca
    ∂ρ/∂t + ∇·(ρv) = 0
yani OLASILIK SÜREKLİLİK denklemidir — Born kuralının korunumu buradan
gelir.

**7. Ters yön: Hamilton-Jacobi'den Schrödinger'e.**
Schrödinger'in mantığı şuydu: `S`nin sağladığı denklem doğrusal DEĞİLDİR
((∇S)² terimi yüzünden), oysa girişim gözlenen bir olgudur ve girişim
DOĞRUSAL bir denklem gerektirir. `ψ = e^(iS/ħ)` koyup `S = −iħ ln ψ`
yazarsak, `(∇S)²` terimi `−ħ²(∇ψ)²/ψ²` olur — hâlâ doğrusal değil. Ama
`(∇S)² → −ħ²∇²ψ/ψ` seçimi yapılırsa denklem
    iħ ∂ψ/∂t = −(ħ²/2m)∇²ψ + Vψ
biçimine gelir ve **doğrusaldır**. Bu seçim, `p → −iħ∇` operatör
karşılığının ta kendisidir. Yani kanonik kuantumlama, "Hamilton-Jacobi
denklemini doğrusallaştıran" işlemdir.

**8. Zincirin tamamı.**
    δS = 0
      → Euler-Lagrange: d/dt(∂L/∂q̇) = ∂L/∂q
      → Legendre: H = Σpq̇ − L
      → Hamilton-Jacobi: H(q,∂S/∂q,t) + ∂S/∂t = 0
      → ψ = A e^(iS/ħ) ve doğrusallaştırma
      → Schrödinger: iħ∂ψ/∂t = Ĥψ,  Ĥ = −(ħ²/2m)∇² + V
Klasik mekanikten kuantum mekaniğine giden yolun tamamı budur.

**Nerede dikkat:** 7. adım bir İSPAT değil, bir GEREKÇEDİR.
Hamilton-Jacobi'den Schrödinger'i mantıksal zorunlulukla çıkaramazsınız;
kuantum mekaniği klasik mekaniğin bir sonucu değildir. Yapılan şey,
doğru denklemi BULMAYA yarayan bir kılavuzdur — doğruluğu deneyle
sınanır. Ters yön (Schrödinger → Hamilton-Jacobi, 6. adım) ise gerçek
bir matematiksel limittir.
""", """
The Hamilton-Jacobi equation is the form of classical mechanics closest to
quantum mechanics, and it is the road Schrodinger travelled.

1. A canonical transformation with generating function S(q,P,t) gives
   p = dS/dq and K = H + dS/dt. Demand K = 0.
2. That condition is the Hamilton-Jacobi equation:
   H(q, dS/dq, t) + dS/dt = 0, i.e. (dS/dx)^2/2m + V + dS/dt = 0.
3. S is the action itself: dS/dt = L, so S = int L dt.
4. Surfaces of constant S move like wavefronts, with trajectories normal to
   them - mechanics' "geometrical optics".
5. Write psi = A exp(iS/hbar) and substitute into the Schrodinger equation.
   The real part gives dS/dt + (grad S)^2/2m + V - (hbar^2/2m)(lap A)/A = 0;
   the imaginary part gives the continuity equation for rho = A^2.
6. As hbar -> 0 the real part becomes exactly Hamilton-Jacobi. The dropped
   term is the quantum potential.
7. Conversely, linearising Hamilton-Jacobi via psi = exp(iS/hbar) and the
   replacement (grad S)^2 -> -hbar^2 (lap psi)/psi produces the Schrodinger
   equation. That replacement IS the substitution p -> -i hbar grad.
8. Caveat: step 7 is a heuristic, not a proof. Quantum mechanics is not a
   consequence of classical mechanics; only the hbar -> 0 direction is a
   genuine limit.
""",
  eqs=["H(q, ∂S/∂q, t) + ∂S/∂t = 0", "(1/2m)(∂S/∂x)² + V + ∂S/∂t = 0",
       "S = ∫L dt", "p = ∇S", "ψ = A·e^(iS/ħ)",
       "∂ρ/∂t + ∇·(ρ∇S/m) = 0", "Q = −(ħ²/2m)(∇²A/A)"],
  ex_tr=["Serbest parçacık: V = 0 için Hamilton-Jacobi denklemi "
         "(1/2m)(∂S/∂x)² + ∂S/∂t = 0. Ayrıştırarak S = px − Et "
         "denenirse p²/2m = E çıkar. Karşılık gelen dalga "
         "ψ = A·e^(i(px−Et)/ħ) = A·e^(i(kx−ωt)) — düzlem dalga, "
         "p = ħk ve E = ħω ile. de Broglie bağıntıları "
         "Hamilton-Jacobi'nin en basit çözümünden doğrudan okunuyor."],
  ex_en=["Free particle: S = px - Et solves Hamilton-Jacobi with p^2/2m = E, "
         "and psi = A exp(i(px-Et)/hbar) is the plane wave, giving p = hbar k "
         "and E = hbar omega."],
  kw="hamilton jacobi denklemi|hamilton-jacobi denklemi turetimi|"
     "hamilton jacobi nasil elde edilir|hamilton jacobi ispati|"
     "hamiltonun asal fonksiyonu|uretici fonksiyon kanonik donusum|"
     "hamilton jacobi dalga fonksiyonu iliskisi|"
     "hamilton jacobiden schrodingere|klasik mekanikten dalga denklemine|"
     "kuantum potansiyeli|eylem ve dalga fonksiyonu|"
     "S = sabit dalga cephesi|mekanigin geometrik optigi|"
     "psi = A e^(iS/hbar)|schrodinger denklemini nasil buldu|"
     "hamilton-jacobi equation|hamiltons principal function|"
     "quantum potential|from hamilton-jacobi to schrodinger|"
     "wkb connection classical action",
  related="lagrange_hamilton_gecis|euler_lagrange_turetim|"
          "kanonik_kuantumlama|kanonik_donusum|klasik_limit|"
          "poisson_komutator"),

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
