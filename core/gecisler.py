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

**3b. Zamanı ayır: KARAKTERİSTİK fonksiyon.**
`H` zamana açıkça bağlı değilse (`∂H/∂t = 0`) değişkenler ayrılabilir:
    S(q,t) = W(q) − E·t
Yerine koyunca `∂S/∂t = −E` olur ve Hamilton-Jacobi denklemi ZAMANDAN
ARINIR:
    **H(q, ∂W/∂q) = E**
Buna **Hamilton'un KARAKTERİSTİK fonksiyonu** `W(q)` denir; `S`ye ise
ASAL fonksiyon denir. İkisi karıştırılmamalıdır:

    S(q,t) — asal fonksiyon      — etkinin kendisi, S = ∫L dt
    W(q)   — karakteristik fonks. — indirgenmiş etki, W = ∫p·dq

**Karakteristik fonksiyonun fiziksel anlamı.** `p = ∂W/∂q` olduğundan
    W = ∫p dq
yani `W` **indirgenmiş etkidir** (abbreviated action). Üç okuması vardır:

  * **Geometrik:** `S = sabit` yüzeyleri zamanla İLERLER (dalga cephesi
    gibi), ama `W = sabit` yüzeyleri SABİTTİR ve yörüngeler onlara
    diktir. Yani `W`, hareketin yörüngesini zamandan bağımsız olarak
    kodlar — "yol", "zaman çizelgesi" değil.
  * **Değişimsel:** Hamilton ilkesi `δ∫L dt = 0` iken, Maupertuis
    ilkesi `δ∫p dq = 0`dır (sabit enerjide). `W` bu ikinci ilkenin
    fonksiyonelidir; enerji sabitken doğru olan "en kısa yol" ölçüsü.
  * **Kuantum köprüsü:** Eski kuantum kuramının Bohr-Sommerfeld
    koşulu doğrudan `W` üzerinden yazılır:
        ∮p dq = n·h
    WKB yaklaşımında dalga fonksiyonunun fazı da `W/ħ`dır:
    `ψ ~ e^(iW/ħ)·e^(−iEt/ħ)`. Yani karakteristik fonksiyon, klasik
    yörüngeyle kuantum fazı arasındaki doğrudan bağdır.

**Ne zaman hangisi?** `W` ayrılabilir sistemlerde (merkezî kuvvet,
periyodik hareket) çözümü tamamen cebire indirger ve etki-açı
değişkenlerinin (`J = ∮p dq`) temelidir. `S` ise zamana bağlı
problemlerde ve kuantum bağlantısında gereklidir.

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
3b. If H has no explicit time dependence, separate S(q,t) = W(q) - Et, giving
   the time-independent form H(q, dW/dq) = E. W is Hamilton's CHARACTERISTIC
   function (not to be confused with S, the principal function). Since
   p = dW/dq, W = int p dq is the abbreviated action. Surfaces of constant W
   are fixed and trajectories are normal to them, so W encodes the path
   rather than the schedule; it is the functional of Maupertuis' principle
   (delta int p dq = 0 at fixed energy), it carries the Bohr-Sommerfeld
   condition (closed integral of p dq = n h), and in WKB the phase is W/hbar.
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
       "S = ∫L dt", "S(q,t) = W(q) − Et", "H(q, ∂W/∂q) = E",
       "W = ∫p dq", "∮p dq = n·h", "p = ∇S", "ψ = A·e^(iS/ħ)",
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
     "karakteristik fonksiyon|hamiltonun karakteristik fonksiyonu|karakteristik fonksiyonun fiziksel anlami|indirgenmis etki|abbreviated action|maupertuis ilkesi|asal fonksiyon ile karakteristik fonksiyon farki|bohr sommerfeld kosulu|etki aci degiskenleri|"
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

T("hamilton_akisi",
  "Hamilton Akışı: Gözlenebilirler Neden Üreteçtir",
  "Hamiltonian Flow: Why Observables Are Generators", """
Operatör cebirinin kuantum mekaniğinde neden ZORUNLU olarak ortaya
çıktığının cevabı burada başlar. Klasik mekanikte de gözlenebilirler
birer ÜRETEÇTİR; kuantumlama bu yapıyı korur.

**1. Faz uzayı bir simplektik manifolddur.**
`(q,p)` uzayında temel nesne bir metrik değil, kapalı ve dejenere
olmayan 2-formdur:
    ω = Σᵢ dqᵢ ∧ dpᵢ
Uzunluk kavramı yoktur; ALAN kavramı vardır. Klasik mekaniğin bütün
yapısı bu formdan çıkar.

**2. Hamilton vektör alanı.**
Her `H` fonksiyonu bir vektör alanı tanımlar; tanım denklemi:
    ι_{X_H} ω = dH
Bileşenlerini açarsak:
    X_H = (∂H/∂p)·∂/∂q − (∂H/∂q)·∂/∂p
Bu alanın integral eğrileri tam olarak Hamilton denklemleridir:
    q̇ = ∂H/∂p,     ṗ = −∂H/∂q
Yani **hareket, `H`nin ürettiği akıştır** — `φ_t: (q₀,p₀) → (q(t),p(t))`.

**3. Poisson parantezi bu akışın türevidir.**
    {A,H} = ω(X_A, X_H) = X_H(A)
ve dolayısıyla
    dA/dt = {A,H}
Parantez soyut bir tanım değil, "A niceliğinin H akışı boyunca ne kadar
değiştiği"dir.

**4. Her gözlenebilir kendi akışını üretir.**
`H`ye özel bir şey yok. Herhangi bir `G` fonksiyonu sonsuz küçük bir
kanonik dönüşüm üretir:
    δq = ε ∂G/∂p,     δp = −ε ∂G/∂q
Somut karşılıklar:
    G = p    → uzayda ÖTELEME
    G = L_z  → z ekseni etrafında DÖNME
    G = H    → ZAMAN evrimi
İşte klasik mekaniğin en derin ifadesi: **gözlenebilirler simetri
dönüşümlerinin üreteçleridir.** Noether teoremi bunun sonucudur —
`{G,H} = 0` ise hem `G` korunur hem de `G`nin ürettiği dönüşüm bir
simetridir.

**5. Akış kanonik yapıyı korur.**
`φ_t` altında `ω` değişmez (`L_{X_H} ω = 0`, Cartan formülü ve `d²=0`
ile). Sonuçları:
  * Her `φ_t` bir KANONİK DÖNÜŞÜMDÜR.
  * `ω^n/n!` hacim formu korunur — **Liouville teoremi**.
  * Faz uzayı hacmi sıkıştırılamaz; istatistiksel mekaniğin temeli.

**6. Kuantuma geçiş: akış ÜNİTER olur.**
Şimdi asıl nokta. Klasikte `G` bir akış üretiyordu; kuantumda `Ĝ` bir
ÜNİTER dönüşüm üretir:
    Klasik:  A → A + ε{A,G}          (Poisson akışı)
    Kuantum: Â → Â + (ε/iħ)[Â,Ĝ]     (üniter akış)
    sonlu:   Û(ε) = e^(−iεĜ/ħ)
Heisenberg denklemi bunun zaman hâlidir:
    dÂ/dt = [Â,Ĥ]/(iħ)
Klasik `dA/dt = {A,H}` ile satır satır aynı.

**Operatör cebiri neden zorunlu?** Çünkü fizik "gözlenebilir = üreteç"
yapısı üzerine kuruludur. Bir dönüşüm grubunun (öteleme, dönme, zaman
evrimi) Hilbert uzayındaki temsili üniterdir (Wigner teoremi: simetriler
üniter ya da anti-üniter olmalıdır ki olasılıklar korunsun). Üniter
grupların üreteçleri de Hermit OPERATÖRLERDİR (Stone teoremi). Yani
gözlenebilirlerin operatör olması bir tercih değil, "gözlenebilir üreteç
demektir" cümlesinin Hilbert uzayındaki zorunlu karşılığıdır.
""", """
Operator algebra is forced because observables are generators already in
classical mechanics.

1. Phase space carries a symplectic form omega = sum dq ^ dp.
2. Each H defines a Hamiltonian vector field by iota_X omega = dH, whose
   integral curves are Hamilton's equations: motion is the flow of H.
3. {A,H} = X_H(A), so dA/dt = {A,H} measures change along that flow.
4. Any G generates an infinitesimal canonical transformation: p generates
   translations, L_z rotations, H time evolution. Observables are the
   generators of symmetries; Noether follows.
5. The flow preserves omega, hence is canonical, and preserves phase volume
   (Liouville).
6. Quantum mechanically the same generator produces a UNITARY flow,
   U = exp(-i eps G/hbar), and A -> A + (eps/i hbar)[A,G] replaces
   A -> A + eps{A,G}. Heisenberg's equation mirrors dA/dt = {A,H}.

By Wigner's theorem symmetries act unitarily, and by Stone's theorem the
generators of unitary groups are self-adjoint operators. So "observable =
generator" forces observables to be operators.
""",
  eqs=["ω = Σ dqᵢ ∧ dpᵢ", "ι_{X_H} ω = dH", "dA/dt = {A,H} = X_H(A)",
       "δq = ε∂G/∂p, δp = −ε∂G/∂q", "Û(ε) = e^(−iεĜ/ħ)",
       "dÂ/dt = [Â,Ĥ]/(iħ)"],
  ex_tr=["Öteleme üreteci: G = p alalım. δq = ε·∂p/∂p = ε, δp = 0 — "
         "yani sistem ε kadar ötelenir ve momentum değişmez. Kuantum "
         "karşılığı Û(ε) = e^(−iεp̂/ħ) ve gerçekten "
         "Û(ε)ψ(x) = ψ(x−ε). Momentum operatörünün −iħ∂/∂x olmasının "
         "sebebi tam olarak budur: türev, ötelemenin üretecidir."],
  ex_en=["Take G = p: the flow shifts q by epsilon and leaves p fixed. The "
         "quantum counterpart is U = exp(-i eps p/hbar), which translates "
         "psi, which is exactly why p = -i hbar d/dx."],
  kw="hamilton akisi|hamiltonian flow|simplektik yapi|simplektik form|"
     "faz uzayi geometrisi|hamilton vektor alani|"
     "gozlenebilirler neden uretec|uretec ve simetri|"
     "sonsuz kucuk kanonik donusum|kanonik donusum uretici|"
     "operator cebiri neden ortaya cikar|operator cebiri zorunlulugu|"
     "liouville teoremi faz hacmi|wigner teoremi|stone teoremi|"
     "heisenberg denklemi klasik karsiligi|"
     "symplectic form|hamiltonian vector field|generators of symmetries|"
     "why operator algebra is necessary",
  related="kanonik_donusum|poisson_komutator|noether|hamilton|"
          "lagrange_hamilton_gecis|stone_von_neumann|ehrenfest_teoremi"),

T("weyl_kuantumlama",
  "Weyl Kuantumlaması, Moyal Parantezi ve Dirac Kuralının Sınırı",
  "Weyl Quantization, the Moyal Bracket and the Limits of Dirac's Rule", """
Dirac kuralı `{A,B} → [Â,B̂]/(iħ)` bir REÇETEDİR ve eksiktir: klasikte
`qp = pq` iken kuantumda `q̂p̂ ≠ p̂q̂`dir, dolayısıyla `qp` niceliğinin
karşılığı belirsizdir. Weyl kuantumlaması bu belirsizliği kapatan somut
bir kuraldır.

**1. Sıralama sorunu.**
`qp` için hangisi? `q̂p̂`, `p̂q̂`, ya da ortalamaları? İlk ikisi Hermit
bile değildir (`(q̂p̂)† = p̂q̂`). Hermitlik zorunlu olduğuna göre en az
simetrikleştirme gerekir.

**2. Weyl'in çözümü: ÜSTELDE simetrikleştir.**
Klasik `f(q,p)` fonksiyonunun Fourier dönüşümü `f̃(σ,τ)` olsun. Weyl
eşlemesi:
    Ŵ[f] = (1/2π)² ∫∫ f̃(σ,τ) · e^(i(σq̂ + τp̂)) dσ dτ
Püf nokta `e^(i(σq̂+τp̂))` ifadesidir: `q̂` ve `p̂` üstelin İÇİNDE
toplanmış olduğu için sıralama kendiliğinden simetrikleşir. Sonuç her
zaman Hermit'tir.

**3. Ne veriyor?**
    qp    → (q̂p̂ + p̂q̂)/2
    q²p   → (q̂²p̂ + q̂p̂q̂ + p̂q̂²)/3
    q^m p^n → bütün olası sıralamaların ortalaması
Yani Weyl kuralı "tam simetrik sıralama"dır.

**4. Ters yön: Wigner dönüşümü.**
Eşleme tersine çevrilebilir. Bir `ρ̂` operatöründen faz uzayına dönen
fonksiyon Wigner fonksiyonudur:
    W(q,p) = (1/πħ)∫ ψ*(q+y) ψ(q−y) e^(2ipy/ħ) dy
`W` gerçeldir ve marjinalleri doğru olasılıkları verir, ama NEGATİF
değer alabilir — bu yüzden "yarı-olasılık" denir. Negatiflik, klasik bir
olasılık dağılımının açıklayamayacağı kuantum davranışın ölçüsüdür.

**5. Moyal parantezi: Dirac kuralının TAM hâli.**
Weyl eşlemesi altında operatör çarpımı, faz uzayında bir "yıldız
çarpımına" (`⋆`, Moyal çarpımı) karşılık gelir. Komütatörün karşılığı:
    {{f,g}} = (f⋆g − g⋆f)/(iħ)
Açılımı:
    {{f,g}} = {f,g} + O(ħ²)
**İşte Dirac kuralının kesin ifadesi budur:** Poisson parantezi, Moyal
parantezinin `ħ → 0` limitidir. Dirac'ın `{A,B} → [Â,B̂]/(iħ)` kuralı
ħ'nin BİRİNCİ mertebesinde doğrudur; daha yüksek mertebelerde düzeltme
terimleri vardır.

**6. Groenewold-van Hove teoremi — kuralın sınırı.**
Bütün Poisson parantezlerini tam olarak komütatörlere taşıyan bir
kuantumlama eşlemesi **YOKTUR** (derecesi 3 ve üstü polinomlar için).
Yani Dirac kuralı bir Lie cebiri eşyapısı değildir; olamaz da. Weyl
kuantumlaması iyi ve doğal bir seçimdir ama o da eşyapı kurmaz —
`{{f,g}} ≠ {f,g}` olduğu yerler tam olarak bu teoremin dediği yerlerdir.

**7. Üç kavramın ilişkisi (sık karıştırılır).**
    Dirac kuralı      : NE olması gerektiğini söyler — cebir korunsun.
                        Bir istektir, ħ'nin 1. mertebesinde sağlanır.
    Weyl kuantumlaması: NASIL yapılacağını söyler — somut, sıralama
                        belirsizliğini kapatan bir eşleme.
    Stone-von Neumann : NEREDE yaşadığını söyler — bu cebirin temsili,
                        üniter eşdeğerlik anlamında tektir.
Üçü ayrı sorulara cevap verir: gereklilik, gerçekleme, teklik.
""", """
Dirac's rule is a recipe with a gap: classically qp = pq but q p operators do
not commute, so the image of qp is ambiguous.

1. q p, p q are not even Hermitian on their own.
2. Weyl's fix is to symmetrise inside an exponential:
   W[f] = (1/2pi)^2 int f~(s,t) exp(i(s q + t p)) ds dt.
3. This gives qp -> (qp + pq)/2 and q^2 p -> (q^2 p + q p q + p q^2)/3: the
   average over all orderings.
4. The inverse map is the Wigner transform; W(q,p) is real with correct
   marginals but can be negative - a quasi-probability.
5. Operator products become a star product, and the commutator becomes the
   Moyal bracket {{f,g}} = (f*g - g*f)/(i hbar) = {f,g} + O(hbar^2). This is
   the precise content of Dirac's rule: the Poisson bracket is the hbar -> 0
   limit of the Moyal bracket.
6. Groenewold-van Hove: no quantisation map reproduces all Poisson brackets
   exactly beyond quadratic order, so no exact Lie algebra homomorphism exists.
7. The three notions answer different questions: Dirac says what should hold,
   Weyl says how to realise it, Stone-von Neumann says the representation is
   unique up to unitary equivalence.
""",
  eqs=["Ŵ[f] = (1/2π)²∫∫f̃(σ,τ)e^(i(σq̂+τp̂))dσdτ",
       "qp → (q̂p̂ + p̂q̂)/2", "W(q,p) = (1/πħ)∫ψ*(q+y)ψ(q−y)e^(2ipy/ħ)dy",
       "{{f,g}} = (f⋆g − g⋆f)/(iħ)", "{{f,g}} = {f,g} + O(ħ²)"],
  ex_tr=["Harmonik salınıcının taban durumu için Wigner fonksiyonu "
         "W(q,p) ∝ e^(−(mωq² + p²/mω)/ħ) — her yerde POZİTİF bir Gauss. "
         "Bu yüzden koherent durumlar 'en klasik' kuantum durumlardır. "
         "Buna karşılık birinci uyarılmış durumun Wigner fonksiyonu "
         "orijinde NEGATİFTİR; klasik bir faz uzayı dağılımıyla "
         "açıklanamaz."],
  ex_en=["The oscillator ground state has a positive Gaussian Wigner "
         "function, which is why coherent states are the most classical "
         "states; the first excited state is negative at the origin."],
  kw="weyl kuantumlamasi|weyl quantization|weyl siralama|"
     "siralama belirsizligi|operator siralamasi|"
     "wigner fonksiyonu|wigner donusumu|yari olasilik dagilimi|"
     "moyal parantezi|moyal bracket|yildiz carpimi|star product|"
     "groenewold van hove teoremi|dirac kuralinin siniri|"
     "dirac kuantumlama kurali|faz uzayi kuantum mekanigi|"
     "deformasyon kuantumlamasi|"
     "wigner function|ordering ambiguity|deformation quantization",
  related="poisson_komutator|kanonik_kuantumlama|stone_von_neumann|"
          "hamilton_akisi|klasik_limit"),

T("stone_von_neumann",
  "Stone-von Neumann Teoremi: Gösterimin Tekliği",
  "The Stone-von Neumann Theorem: Uniqueness of the Representation", """
"Konum çarpma, momentum `−iħ∇`" seçimi neden ZORUNLUDUR? Cevap bu
teoremdir — ama teoremin ne dediği sık sık fazla iddialı aktarılır.

**1. Önce sorun: `[x̂,p̂] = iħ` sınırlı operatörlerle SAĞLANAMAZ.**
Wintner-Wielandt teoremi: bir Banach cebirinde `[A,B] = cI` (c ≠ 0)
olamaz. Kanıt fikri: `[A,Bⁿ] = ncB^(n−1)` bağıntısından
`n|c|·‖B^(n−1)‖ ≤ 2‖A‖‖B‖·‖B^(n−1)‖` çıkar, yani `n|c| ≤ 2‖A‖‖B‖` her
`n` için — imkânsız. Sonuç: `x̂` ve `p̂` SINIRSIZ olmak zorundadır ve
sınırsız operatörlerin tanım kümesi sorunları vardır. Bu yüzden bağıntı
titiz biçimde ÜSTEL hâlde yazılır.

**2. Weyl biçimi.**
    Û(a) = e^(−iap̂/ħ)   (öteleme),   V̂(b) = e^(ibx̂/ħ)   (faz çarpımı)
İkisi de ÜNİTERDİR (sınırlı, tanım kümesi tüm uzay). Komütasyon bağıntısı
şu biçime girer:
    Û(a)V̂(b) = e^(−iab/ħ) V̂(b)Û(a)
Bu, `[x̂,p̂] = iħ`nin matematiksel olarak kusursuz karşılığıdır.

**3. Teorem.**
Ayrılabilir bir Hilbert uzayında, Weyl bağıntılarının **kuvvetli
sürekli** ve **indirgenemez** her temsili, `L²(ℝ)` üzerindeki Schrödinger
temsirine **ÜNİTER EŞDEĞERDİR.** Yani bir `Ŝ` üniter operatörü vardır ve
    Ŝ x̂_temsil Ŝ⁻¹ = (x ile çarpma),   Ŝ p̂_temsil Ŝ⁻¹ = −iħ d/dx

**4. Ne DEMEZ.**
"Başka operatör yoktur" DEMEZ. Momentum gösterimi (`p̂` çarpma, `x̂` ise
`iħ∂/∂p`) ve Bargmann-Fock gösterimi bambaşka görünürler ama üçü de
üniter eşdeğerdir; aradaki dönüşüm Fourier dönüşümüdür. Teoremin
söylediği, bunların hepsinin AYNI FİZİĞİ verdiğidir. "Teklik" bir
gösterim değil, bir EŞDEĞERLİK SINIFI teklığıdır.

**5. Üç koşul da gereklidir; biri düşerse teklik biter.**
  * **İndirgenemezlik.** Temsil indirgenebilirse (örneğin `L²(ℝ)⊕L²(ℝ)`),
    Schrödinger temsirinin katları çıkar; fiziksel olarak bu ek bir iç
    serbestlik derecesi (spin gibi) demektir.
  * **Süreklilik.** Kuvvetli süreklilik olmadan patolojik temsiller vardır.
  * **SONLU serbestlik derecesi.** En önemli koşul budur. Sonsuz
    serbestlik dereceli sistemlerde (ALAN KURAMI) teorem ÇÖKER:
    birbirine üniter eşdeğer OLMAYAN sonsuz sayıda temsil vardır.
    **Haag teoremi** bunun sonucudur — etkileşimli alan kuramında
    etkileşim resmi kesin anlamda mevcut değildir. Faz geçişleri,
    kendiliğinden simetri kırılması ve farklı vakumlar hep bu eşdeğer
    olmayan temsirlerle anlatılır.
  * Ayrıca konfigürasyon uzayı BASİT BAĞLANTILI değilse (delikli uzay)
    farklı temsiller doğar: Aharonov-Bohm etkisi ve iki boyutta anyonlar
    bu yüzden mümkündür.

**6. Sonuç — soruya doğru cevap.**
`p̂ = −iħ∇` seçimi, şu koşullar altında tektir: sonlu serbestlik
derecesi, indirgenemezlik, kuvvetli süreklilik. "Tek" derken üniter
eşdeğerlik kastedilir. Bu yüzden `p̂`yi seçmek keyfi değildir — fizikçe
farklı bir seçenek yoktur — ama "matematiksel olarak başka hiçbir
operatör olamaz" demek yanlıştır.

**Adaş uyarısı:** "Stone teoremi" ayrı bir teoremdir (tek parametreli
üniter grupların üreteci öz-eştir). İkisi birlikte kullanılır:
Stone teoremi gözlenebilirin OPERATÖR olmasını, Stone-von Neumann ise
o operatörün HANGİ operatör olduğunu verir.
""", """
Why is "position multiplies, momentum is -i hbar grad" forced?

1. [x,p] = i hbar cannot hold for bounded operators (Wintner-Wielandt), so
   x and p must be unbounded, with domain subtleties. The rigorous statement
   uses exponentials.
2. Weyl form: U(a) = exp(-i a p/hbar), V(b) = exp(i b x/hbar) are unitary and
   satisfy U(a)V(b) = exp(-i a b/hbar) V(b)U(a).
3. Theorem: on a separable Hilbert space, every strongly continuous
   irreducible representation of the Weyl relations is unitarily EQUIVALENT
   to the Schrodinger representation on L^2(R).
4. It does not say no other operator exists. The momentum and Bargmann-Fock
   representations look different but are unitarily equivalent (via Fourier).
   Uniqueness is of the equivalence class.
5. All three hypotheses matter. Reducibility adds internal degrees of freedom;
   continuity excludes pathologies; and with infinitely many degrees of freedom
   (field theory) the theorem fails outright - inequivalent representations
   exist, which is the content of Haag's theorem and the reason distinct vacua
   and spontaneous symmetry breaking are possible. Non-simply-connected
   configuration spaces also give inequivalent representations (Aharonov-Bohm,
   anyons).
6. Note the different Stone theorem: generators of one-parameter unitary groups
   are self-adjoint. Stone gives that observables ARE operators;
   Stone-von Neumann gives WHICH operators.
""",
  eqs=["Û(a) = e^(−iap̂/ħ)", "V̂(b) = e^(ibx̂/ħ)",
       "Û(a)V̂(b) = e^(−iab/ħ)V̂(b)Û(a)",
       "Ŝ x̂ Ŝ⁻¹ = x·,  Ŝ p̂ Ŝ⁻¹ = −iħd/dx"],
  ex_tr=["Momentum gösterimi somut örnektir: φ(p) = ⟨p|ψ⟩ alalım. "
         "Burada p̂ çarpma, x̂ ise iħ∂/∂p olur — konum gösteriminin "
         "tam tersi. İkisini bağlayan üniter operatör Fourier "
         "dönüşümüdür: Ŝ = F. Aynı deneyler, aynı özdeğerler, aynı "
         "olasılıklar; yalnızca taban farklı."],
  ex_en=["The momentum representation, where p multiplies and x is i hbar d/dp, "
         "is related to the Schrodinger one by the Fourier transform - the same "
         "physics in a different basis."],
  kw="stone von neumann teoremi|stone-von neumann|"
     "gosterimin tekligi|uniter esdegerlik|"
     "schrodinger gosterimi neden benzersiz|"
     "konum momentum operatorleri neden tek|"
     "weyl bagintilari|weyl relations|kanonik komutasyon temsili|"
     "haag teoremi|esdeger olmayan temsiller|"
     "sinirsiz operator komutator|wintner wielandt|"
     "stone teoremi uretec|aharonov bohm temsil|"
     "stone-von neumann theorem|uniqueness of representation|"
     "unitary equivalence|haags theorem",
  related="kanonik_kuantumlama|poisson_komutator|weyl_kuantumlama|"
          "hermit_operator|kuantum_formalizm|hamilton_akisi"),

T("ehrenfest_teoremi",
  "Ehrenfest Teoremi ve Klasik Limitin Gerçek Koşulu",
  "Ehrenfest's Theorem and the True Condition for the Classical Limit", """
Kuantum mekaniği doğruysa Newton yasaları nereye gitti? Cevap: beklenen
değerlerde duruyorlar — ama sanıldığından daha dar bir koşulla.

**1. Genel bağıntı.**
`⟨Â⟩ = ⟨ψ|Â|ψ⟩` olsun. Zamana göre türetelim:
    d⟨Â⟩/dt = ⟨∂ψ/∂t|Â|ψ⟩ + ⟨ψ|Â|∂ψ/∂t⟩ + ⟨ψ|∂Â/∂t|ψ⟩
Schrödinger denklemi `∂ψ/∂t = Ĥψ/(iħ)` ve eşleniği
`⟨∂ψ/∂t| = −⟨ψ|Ĥ/(iħ)` yerine konursa:
    d⟨Â⟩/dt = (1/iħ)⟨ψ|(ÂĤ − ĤÂ)|ψ⟩ + ⟨∂Â/∂t⟩
yani
    **d⟨Â⟩/dt = (1/iħ)⟨[Â,Ĥ]⟩ + ⟨∂Â/∂t⟩**
Klasik `dA/dt = {A,H} + ∂A/∂t` ile satır satır aynı — Dirac kuralının
doğrudan sonucu.

**2. Konum için.**
`Ĥ = p̂²/2m + V` ve `[x̂,p̂] = iħ` ile:
    [x̂,p̂²] = p̂[x̂,p̂] + [x̂,p̂]p̂ = 2iħp̂
    [x̂,Ĥ] = [x̂,p̂²]/2m = iħp̂/m
Yerine koyarsak:
    **d⟨x̂⟩/dt = ⟨p̂⟩/m**
Klasik `ẋ = p/m` bağıntısı.

**3. Momentum için.**
`[p̂,V(x̂)]` hesabı (keyfi ψ üzerinde):
    p̂(Vψ) = −iħ(V′ψ + Vψ′),   V p̂ψ = −iħVψ′
    [p̂,V]ψ = −iħV′ψ
O hâlde `[p̂,Ĥ] = [p̂,V] = −iħ ∂V/∂x` ve
    **d⟨p̂⟩/dt = −⟨∂V/∂x⟩ = ⟨F(x̂)⟩**

**4. Birleştir.**
    m d²⟨x̂⟩/dt² = ⟨F(x̂)⟩
Newton'un ikinci yasası, beklenen değerler düzeyinde geri geldi. ∎

**5. KRİTİK İNCE NOKTA — burası çoğu anlatımda atlanır.**
Elde ettiğimiz `⟨F(x̂)⟩`dir, `F(⟨x̂⟩)` DEĞİL. Bunlar genelde EŞİT
DEĞİLDİR:
    ⟨F(x̂)⟩ ≠ F(⟨x̂⟩)
`F`yi `⟨x̂⟩` etrafında açalım:
    ⟨F(x̂)⟩ = F(⟨x̂⟩) + ½F″(⟨x̂⟩)·(Δx)² + …
Yani klasik denklem ancak düzeltme terimi ihmal edilebilirse geçerlidir.

**Tam eşitlik koşulu:** `F″ = 0`, yani `V` en fazla İKİNCİ derecedendir.
Üç durumda tam olarak klasik:
    V = 0        (serbest parçacık)
    V = −Fx      (düzgün alan)
    V = ½kx²     (harmonik salınıcı)
Bunların dışında Ehrenfest teoremi klasik hareketi **yaklaşık** verir ve
koşul şudur: dalga paketi, kuvvetin değiştiği ölçeğe göre DAR olmalı.

**6. Sonuç: Ehrenfest klasik limiti İSPATLAMAZ.**
Sık rastlanan "Ehrenfest teoremi klasik mekaniği kuantumdan çıkarır"
cümlesi fazla iddialıdır. Teorem yalnızca beklenen değerlerin klasik
BİÇİMDE denklemler sağladığını söyler. Gerçek klasik limit ayrıca şunu
gerektirir: paketin dar KALMASI. Oysa paketler yayılır — serbest
parçacıkta `Δx(t)` zamanla büyür — ve kaotik sistemlerde bu yayılma
üstel hızlıdır. Klasikliğin asıl mekanizması dekoherenstir.

**7. Korunum yasaları.**
`∂Â/∂t = 0` ve `[Â,Ĥ] = 0` ise `⟨Â⟩` sabittir. Klasik `{A,H} = 0`
koşulunun tıpatıp karşılığı; Noether teoreminin kuantum yüzü budur.
""", """
Where did Newton go? Into expectation values - under a narrower condition than
usually stated.

1. Differentiating <A> and using the Schrodinger equation gives
   d<A>/dt = (1/i hbar)<[A,H]> + <dA/dt>, mirroring dA/dt = {A,H} + dA/dt.
2. With H = p^2/2m + V: [x,H] = i hbar p/m, so d<x>/dt = <p>/m.
3. [p,V] = -i hbar dV/dx, so d<p>/dt = -<dV/dx> = <F>.
4. Hence m d^2<x>/dt^2 = <F(x)>.
5. The subtlety: this is <F(x)>, not F(<x>). Expanding,
   <F(x)> = F(<x>) + F''(<x>)(dx)^2/2 + ..., so the classical equation is exact
   only when F'' = 0, i.e. V at most quadratic: free particle, uniform field,
   harmonic oscillator. Otherwise it holds only for packets narrow compared to
   the scale on which the force varies.
6. So Ehrenfest does not by itself prove the classical limit: packets spread,
   exponentially fast in chaotic systems. Decoherence is the actual mechanism.
7. If [A,H] = 0 then <A> is conserved - the quantum face of Noether.
""",
  eqs=["d⟨Â⟩/dt = (1/iħ)⟨[Â,Ĥ]⟩ + ⟨∂Â/∂t⟩", "[x̂,Ĥ] = iħp̂/m",
       "d⟨x̂⟩/dt = ⟨p̂⟩/m", "[p̂,V] = −iħ ∂V/∂x",
       "d⟨p̂⟩/dt = −⟨∂V/∂x⟩ = ⟨F⟩", "m d²⟨x̂⟩/dt² = ⟨F(x̂)⟩",
       "⟨F(x̂)⟩ = F(⟨x̂⟩) + ½F″(⟨x̂⟩)(Δx)² + …"],
  ex_tr=["Harmonik salınıcı: F = −kx olduğundan F″ = 0 ve "
         "d⟨p⟩/dt = −k⟨x⟩ TAM olarak sağlanır. Bu yüzden koherent "
         "durumun merkezi, paket ne kadar geniş olursa olsun tam "
         "klasik yörüngeyi izler ve paket yayılmaz. Buna karşılık "
         "anharmonik bir kuyuda (V = λx⁴) F″ ≠ 0'dır; merkez klasik "
         "yörüngeden sapar ve sapma paketin genişliğiyle büyür."],
  ex_en=["For the oscillator F'' = 0, so d<p>/dt = -k<x> holds exactly and a "
         "coherent state follows the classical orbit without spreading; in an "
         "anharmonic well the centre drifts away from the classical path."],
  kw="ehrenfest teoremi|ehrenfest theorem|ehrenfest ispati|"
     "beklenen deger zaman turevi|beklenen degerlerin evrimi|"
     "kuantumdan newton yasasi|newton yasasi beklenen deger|"
     "klasik limit kosulu|dalga paketi yayilmasi|"
     "kuantum korunum yasasi komutator|"
     "d<x>/dt = <p>/m|klasik denklemler ne zaman tam|"
     "ehrenfest theorem derivation|expectation value dynamics|"
     "classical limit condition",
  related="klasik_limit|poisson_komutator|hamilton_akisi|"
          "kanonik_kuantumlama|potansiyel_operatoru|noether"),

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
