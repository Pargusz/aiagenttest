"""Ogrenme yol haritalari.

"Nereden baslamaliyim", "bana bir yol haritasi cikar", "ne ogretebilirsin"
turu sorulara verilen yanitlar. Her yol haritasi asamalara bolunmus somut bir
plandir: ne ogrenilecek, neden ogrenilecek, hangi alistirma yapilacak ve
ParguszPhysics'e ne yazarak denenecek.
"""
import re


def S(ad, sure, konular, neden, alistirma, dene):
    return {"ad": ad, "sure": sure, "konular": konular, "neden": neden,
            "alistirma": alistirma, "dene": dene}


PATHS = {}


def P(key, tr, en, kw, ozet_tr, ozet_en, asamalar, asamalar_en, ipuclari_tr=None,
      ipuclari_en=None):
    PATHS[key] = {
        "key": key, "tr": tr, "en": en,
        "kw": [k.strip() for k in kw.split("|") if k.strip()],
        "ozet_tr": ozet_tr.strip(), "ozet_en": ozet_en.strip(),
        "asamalar": asamalar, "asamalar_en": asamalar_en,
        "ipuclari_tr": ipuclari_tr or [], "ipuclari_en": ipuclari_en or [],
    }


# ══════════════════════════════════════════════════════════════════ MATLAB
P("matlab", "MATLAB / Octave Yol Haritası", "MATLAB / Octave Roadmap",
  "matlab|octave|simulink|m-file|kod yazma|programlama|programming",
  """
Sıfırdan başlayıp fizik problemlerini sayısal olarak çözebilecek düzeye kadar
beş aşamalı bir plan. Toplam süre, haftada 4-6 saat çalışmayla yaklaşık **8-10
hafta**.

MATLAB lisanslıysa onu kullanın; değilse **GNU Octave** ücretsizdir ve bu yol
haritasındaki her şeyi çalıştırır. Kod yazımı neredeyse birebir aynıdır.
""",
  """
A five-stage plan from zero to solving physics problems numerically. At 4-6
hours a week, expect roughly **8-10 weeks**.

Use MATLAB if you have a licence; otherwise **GNU Octave** is free and runs
everything in this roadmap. The syntax is almost identical.
""",
  [
    S("1. Temeller ve çalışma alanı", "1. hafta",
      ["Değişkenler, sayı türleri, `format long`",
       "Vektör ve matris oluşturma: `linspace`, `zeros`, `ones`, `:` işleci",
       "İndeksleme ve dilimleme: `v(3)`, `A(2,:)`, `v(end)`, mantıksal indeksleme",
       "Betik (script) ve fonksiyon dosyaları arasındaki fark",
       "`clear; clc; close all` alışkanlığı"],
      "MATLAB'da her şey matristir. Bu zihinsel modeli baştan oturtmazsanız "
      "sonraki her konu zorlaşır.",
      "10 elemanlı bir vektör üretin; çift indisli elemanlarını ayrı bir "
      "vektöre alın; 3×3 birim matrisin köşegenini 5 yapın.",
      "`90 km/h kac m/s` — birim çevirmeyi kontrol etmek için"),

    S("2. Vektörleştirme ve grafik", "2.-3. hafta",
      ["Eleman bazlı işleçler: `.*`, `./`, `.^` (en sık yapılan hata burada)",
       "Döngü yerine dizi işlemi yazma alışkanlığı",
       "`plot`, `xlabel`, `ylabel`, `title`, `legend`, `grid on`",
       "`subplot`, `figure`, `hold on`",
       "`semilogy`, `loglog` — üstel ve kuvvet yasalarını doğrulamak için"],
      "Vektörleştirme MATLAB'ı hızlı yapan şeydir. Ayrıca fizik grafiği "
      "üretmeyi öğrenmeden hiçbir sayısal sonucu yorumlayamazsınız.",
      "Eğik atış yörüngesini 5 farklı açı için tek grafikte çizin. Menzilin "
      "45°'de maksimum olduğunu grafikten gösterin.",
      "`egik atis icin matlab kodu`"),

    S("3. Denklem çözme ve lineer cebir", "4.-5. hafta",
      ["`A\\b` ile lineer sistem çözme (neden `inv(A)*b` değil?)",
       "`roots`, `fzero`, `fsolve` — kök bulma",
       "`eig` — özdeğer/özvektör",
       "`polyfit`, `polyval` — veri uydurma",
       "Koşullandırma sayısı `cond` ve sayısal kararlılık"],
      "Fizikteki problemlerin çoğu bir denklem sistemine indirgenir: devre "
      "analizi, statik denge, normal modlar, kuantum enerji düzeyleri.",
      "Kirchhoff yasalarıyla 3 döngülü bir devrenin akımlarını `A\\b` ile "
      "bulun. Sonra bir kütle-yay zincirinin normal modlarını `eig` ile çıkarın.",
      "`[[2,1],[1,3]] ozdegerleri`"),

    S("4. Diferansiyel denklemler", "6.-7. hafta",
      ["İkinci mertebe denklemi birinci mertebe sisteme çevirme",
       "`ode45` kullanımı ve anonim fonksiyonlar `@(t,y)`",
       "`odeset` ile tolerans ayarı (`RelTol`, `AbsTol`)",
       "Stiff sistemler ve `ode15s`",
       "Simplektik integratörler (Verlet) — uzun simülasyonlarda enerji korunumu"],
      "Klasik mekaniğin tamamı, devreler, ısı transferi, popülasyon "
      "modelleri — hepsi diferansiyel denklemdir. Bu aşama fizikte en çok "
      "işinize yarayacak olanıdır.",
      "Sönümlü sarkacı çözün. Sonra sönümü sıfır yapıp enerjinin sabit "
      "kaldığını grafikle doğrulayın — çözümünüzün doğruluk testi budur.",
      "`sonumlu osilator icin matlab kodu`"),

    S("5. Veri analizi ve sayısal yöntemler", "8.-10. hafta",
      ["`fft` ile frekans analizi, frekans ekseninin doğru kurulması",
       "Eğri uydurma: `lsqcurvefit`, `fminsearch`, ki-kare minimizasyonu",
       "Hata çubukları `errorbar` ve artık (residual) grafiği",
       "Sonlu farklarla PDE: ısı ve dalga denklemi, CFL kararlılık koşulu",
       "Monte Carlo yöntemleri"],
      "Deney verisi işlemek ve kısmi diferansiyel denklem çözmek, lisans "
      "laboratuvarından araştırmaya kadar her yerde gerekir.",
      "Gürültülü bir sönümlü salınım verisi üretin, üstel zarfı fit ederek "
      "sönüm katsayısını geri çıkarın ve artık grafiğiyle uyumu denetleyin.",
      "`fft analizi kodu yaz` ve `egri uydurma matlab`"),
  ],
  [
    S("1. Fundamentals and workspace", "week 1",
      ["Variables, numeric types, `format long`",
       "Creating vectors and matrices: `linspace`, `zeros`, `ones`, the `:` operator",
       "Indexing and slicing: `v(3)`, `A(2,:)`, `v(end)`, logical indexing",
       "Scripts versus function files",
       "The `clear; clc; close all` habit"],
      "In MATLAB everything is a matrix. Without that mental model, every "
      "later topic gets harder.",
      "Build a 10-element vector; extract its even-indexed entries; set the "
      "diagonal of a 3×3 identity matrix to 5.",
      "`90 km/h to m/s`"),

    S("2. Vectorisation and plotting", "weeks 2-3",
      ["Element-wise operators: `.*`, `./`, `.^` (the most common mistake)",
       "Writing array operations instead of loops",
       "`plot`, `xlabel`, `ylabel`, `title`, `legend`, `grid on`",
       "`subplot`, `figure`, `hold on`",
       "`semilogy`, `loglog` for exponential and power laws"],
      "Vectorisation is what makes MATLAB fast, and you cannot interpret any "
      "numerical result without being able to plot it.",
      "Plot projectile trajectories for 5 launch angles on one figure and show "
      "graphically that range peaks at 45°.",
      "`matlab code for projectile motion`"),

    S("3. Equation solving and linear algebra", "weeks 4-5",
      ["Solving linear systems with `A\\b` (why not `inv(A)*b`?)",
       "`roots`, `fzero`, `fsolve` for root finding",
       "`eig` for eigenvalues and eigenvectors",
       "`polyfit`, `polyval` for fitting",
       "Condition number `cond` and numerical stability"],
      "Most physics problems reduce to a linear system: circuit analysis, "
      "static equilibrium, normal modes, quantum energy levels.",
      "Solve a 3-loop circuit with Kirchhoff's laws via `A\\b`, then find the "
      "normal modes of a mass-spring chain with `eig`.",
      "`eigenvalues of [[2,1],[1,3]]`"),

    S("4. Differential equations", "weeks 6-7",
      ["Converting second-order equations to first-order systems",
       "Using `ode45` and anonymous functions `@(t,y)`",
       "Tolerances via `odeset` (`RelTol`, `AbsTol`)",
       "Stiff systems and `ode15s`",
       "Symplectic integrators (Verlet) for energy conservation"],
      "All of classical mechanics, circuits, heat transfer and population "
      "models are differential equations. This stage pays off the most.",
      "Solve the damped pendulum, then set damping to zero and verify "
      "graphically that energy stays constant — that is your accuracy test.",
      "`matlab code for damped oscillator`"),

    S("5. Data analysis and numerical methods", "weeks 8-10",
      ["`fft` for frequency analysis and building the frequency axis correctly",
       "Curve fitting: `lsqcurvefit`, `fminsearch`, chi-square minimisation",
       "Error bars with `errorbar` and residual plots",
       "PDEs by finite differences: heat and wave equations, the CFL condition",
       "Monte Carlo methods"],
      "Processing experimental data and solving PDEs is needed everywhere from "
      "the undergraduate lab to research.",
      "Generate noisy damped-oscillation data, fit the exponential envelope to "
      "recover the damping coefficient, and check the fit with a residual plot.",
      "`write an fft analysis script`"),
  ],
  ["`.*` ile `*` farkını karıştırmak en sık hatadır: `*` matris çarpımıdır, "
   "eleman bazlı çarpım `.*` ile yapılır.",
   "Bir sayısal çözümün doğruluğunu her zaman korunan bir nicelikle (enerji, "
   "momentum, yük) test edin. Kod hatasız çalışıyor olması doğru olduğu "
   "anlamına gelmez.",
   "Değişken adlarında birim kullanın: `L_m`, `t_s`, `E_J`. Birim karışıklığı "
   "sayısal fizikte en pahalı hata türüdür.",
   "Bu yol haritasındaki her `dene:` satırını bana yazarak çalışır kod "
   "alabilirsiniz; kodu değiştirerek öğrenmek sıfırdan yazmaktan hızlıdır."],
  ["Confusing `.*` with `*` is the most common error: `*` is matrix "
   "multiplication, element-wise uses `.*`.",
   "Always test a numerical solution against a conserved quantity (energy, "
   "momentum, charge). Running without errors does not mean being correct.",
   "Put units in variable names: `L_m`, `t_s`, `E_J`. Unit confusion is the "
   "most expensive class of bug in computational physics.",
   "Ask me any `try:` line from this roadmap to get working code; modifying "
   "code is a faster way to learn than writing from scratch."])


# ═══════════════════════════════════════════════════════════════════ FİZİK
P("fizik", "Fizik Yol Haritası", "Physics Roadmap",
  # Yalnizca KONU belirten anahtar kelimeler. "nereden baslamali" gibi niyet
  # ifadeleri buraya konmaz; yoksa "matlab ogrenmek istiyorum nereden
  # baslamaliyim" sorusu fizik yol haritasina duserdi.
  "fizik|physics|genel fizik|fizik dersi",
  """
Lise sonrası düzeyden başlayıp modern fiziğe kadar giden sıralı bir plan.
Sıralama keyfî değil: her aşama bir öncekinin matematiğini ve kavramlarını
kullanır.
""",
  """
An ordered plan from post-secondary level up to modern physics. The order is
not arbitrary: each stage uses the mathematics and concepts of the previous one.
""",
  [
    S("1. Matematik altyapısı", "önce bu",
      ["Türev ve integral (tek değişken)",
       "Vektörler, nokta ve vektörel çarpım",
       "Adi diferansiyel denklemler (1. ve 2. mertebe)",
       "Kısmi türev, gradyan / diverjans / rotasyonel",
       "Karmaşık sayılar ve Euler formülü"],
      "Fizik matematikle yazılır. Bu araçlar olmadan ilerlemek, ezberlemek "
      "demektir; ezber ilk zor problemde çöker.",
      "Bir vektör alanının diverjansını ve rotasyonelini elle hesaplayın, "
      "sonra bana doğrulatın.",
      "`diverjans [x*y, y*z, z*x]`"),

    S("2. Klasik mekanik", "2-3 ay",
      ["Newton yasaları, serbest cisim diyagramı",
       "İş, enerji, korunum yasaları",
       "Momentum ve çarpışmalar",
       "Dönme hareketi, tork, açısal momentum",
       "Basit harmonik hareket ve sönümlü/zorlanmış salınım",
       "(İleri) Lagrange ve Hamilton formalizmi"],
      "Bütün fiziğin dili burada kurulur: kuvvet, enerji, momentum, korunum. "
      "Kuantum mekaniği bile Hamilton formalizmi üzerine oturur.",
      "Eğik düzlemde sürtünmeli bir cismi hem Newton hem enerji yöntemiyle "
      "çözün; iki sonucun aynı çıkması gerekir.",
      "`newton yasalari nedir` ve `titresim ornek ver`"),

    S("3. Termodinamik ve istatistiksel fizik", "1-2 ay",
      ["Sıcaklık, ısı, iş; termodinamiğin yasaları",
       "İdeal gaz ve kinetik teori",
       "Entropi ve tersinmezlik",
       "Isı makineleri, Carnot verimi",
       "Bölüşüm fonksiyonu, Boltzmann dağılımı"],
      "Mikroskobik yasalardan makroskobik davranışın nasıl çıktığını gösteren "
      "tek alan budur. Entropi kavramı bilgisayar biliminden kozmolojiye kadar "
      "her yerde karşınıza çıkar.",
      "Carnot veriminin neden aşılamayacağını 2. yasayla tartışın; sonra "
      "sayısal bir örnek çözün.",
      "`Tc=300 K Th=500 K carnot verimi`"),

    S("4. Elektromanyetizma", "3-4 ay",
      ["Elektrostatik: Coulomb, Gauss, potansiyel",
       "Akım, direnç, devreler",
       "Manyetostatik: Biot-Savart, Ampère",
       "Faraday indüksiyonu ve Lenz yasası",
       "Maxwell denklemleri ve elektromanyetik dalgalar"],
      "Fiziğin en tamamlanmış klasik kuramıdır ve göreliliğe giden kapıdır: "
      "Maxwell denklemlerinin Galileo dönüşümüne uymaması Einstein'ı özel "
      "göreliliğe götürmüştür.",
      "Işık hızını yalnızca ε₀ ve μ₀'dan hesaplayın. Çıkan sayının ölçülen "
      "ışık hızına eşit olması tesadüf değildir.",
      "`maxwell denklemleri nedir`"),

    S("5. Dalgalar ve optik", "1-2 ay",
      ["Dalga denklemi, süperpozisyon, duran dalgalar",
       "Girişim ve kırınım",
       "Geometrik optik: mercek, ayna",
       "Polarizasyon",
       "Doppler olayı"],
      "Dalga davranışını anlamadan kuantum mekaniğine geçilemez; dalga "
      "fonksiyonu kavramı doğrudan buradan gelir.",
      "Çift yarık deneyinde saçak aralığını hesaplayın, sonra yarık "
      "aralığını iki katına çıkarınca ne olduğunu tahmin edip doğrulayın.",
      "`cift yarikta girisim formulu`"),

    S("6. Modern fizik", "3-4 ay",
      ["Özel görelilik: zaman genleşmesi, boy kısalması, E=γmc²",
       "Kuantum mekaniğinin temelleri: dalga fonksiyonu, Schrödinger denklemi",
       "Belirsizlik ilkesi, kuantalanma, tünelleme",
       "Atom yapısı ve kuantum sayıları",
       "Çekirdek fiziği ve parçacık fiziğine giriş"],
      "Buraya kadar öğrendiğiniz her şeyin nerede kırıldığını ve neyle "
      "değiştirildiğini görürsünüz. Fiziğin en çok sezgi bozan ama en çok "
      "doğrulanmış kısmıdır.",
      "Sonsuz kuyuda enerji düzeylerini elle türetin, sonra sayısal olarak "
      "çözüp karşılaştırın.",
      "`kuantum kuyusu simulasyonu`"),
  ],
  [
    S("1. Mathematical background", "start here",
      ["Single-variable calculus",
       "Vectors, dot and cross products",
       "Ordinary differential equations (1st and 2nd order)",
       "Partial derivatives, grad / div / curl",
       "Complex numbers and Euler's formula"],
      "Physics is written in mathematics. Without these tools you are "
      "memorising, and memorisation collapses at the first hard problem.",
      "Compute the divergence and curl of a vector field by hand, then have me "
      "check it.",
      "`divergence [x*y, y*z, z*x]`"),

    S("2. Classical mechanics", "2-3 months",
      ["Newton's laws, free-body diagrams",
       "Work, energy, conservation laws",
       "Momentum and collisions",
       "Rotation, torque, angular momentum",
       "Simple harmonic motion, damped and driven oscillation",
       "(Advanced) Lagrangian and Hamiltonian formalism"],
      "The vocabulary of all physics is set here. Even quantum mechanics is "
      "built on the Hamiltonian formalism.",
      "Solve a block on an inclined plane with friction using both Newton's "
      "laws and energy methods; the answers must agree.",
      "`what are newton's laws`"),

    S("3. Thermodynamics and statistical physics", "1-2 months",
      ["Temperature, heat, work; the laws of thermodynamics",
       "Ideal gas and kinetic theory",
       "Entropy and irreversibility",
       "Heat engines and Carnot efficiency",
       "Partition function, Boltzmann distribution"],
      "This is the only field showing how macroscopic behaviour emerges from "
      "microscopic law. Entropy shows up everywhere from computer science to "
      "cosmology.",
      "Argue from the second law why Carnot efficiency cannot be beaten, then "
      "work a numerical example.",
      "`Tc=300 K Th=500 K carnot efficiency`"),

    S("4. Electromagnetism", "3-4 months",
      ["Electrostatics: Coulomb, Gauss, potential",
       "Current, resistance, circuits",
       "Magnetostatics: Biot-Savart, Ampère",
       "Faraday induction and Lenz's law",
       "Maxwell's equations and electromagnetic waves"],
      "The most complete classical theory, and the doorway to relativity: the "
      "failure of Maxwell's equations under Galilean transformation led "
      "Einstein to special relativity.",
      "Compute the speed of light from ε₀ and μ₀ alone. That it matches the "
      "measured value is no coincidence.",
      "`what are maxwell's equations`"),

    S("5. Waves and optics", "1-2 months",
      ["Wave equation, superposition, standing waves",
       "Interference and diffraction",
       "Geometric optics: lenses and mirrors",
       "Polarisation",
       "The Doppler effect"],
      "You cannot move to quantum mechanics without understanding wave "
      "behaviour; the wavefunction concept comes directly from here.",
      "Compute the fringe spacing in a double-slit experiment, then predict "
      "and verify what doubling the slit separation does.",
      "`double slit interference formula`"),

    S("6. Modern physics", "3-4 months",
      ["Special relativity: time dilation, length contraction, E=γmc²",
       "Foundations of quantum mechanics: wavefunction, Schrödinger equation",
       "Uncertainty, quantisation, tunnelling",
       "Atomic structure and quantum numbers",
       "Introduction to nuclear and particle physics"],
      "You see where everything you learned breaks down and what replaces it. "
      "It is the least intuitive and most thoroughly verified part of physics.",
      "Derive the infinite-well energy levels by hand, then solve them "
      "numerically and compare.",
      "`quantum well simulation`"),
  ],
  ["Problem çözmeden fizik öğrenilmez. Okuduğunuz her bölümden sonra en az "
   "5 problem çözün; anladığınızı sanmakla anlamak arasındaki farkı ancak "
   "böyle görürsünüz.",
   "Her sonucu birim analiziyle denetleyin. Boyutları tutmayan bir sonuç "
   "kesinlikle yanlıştır; tutması ise doğru olma ihtimalini çok yükseltir.",
   "Sınır durumlarını kontrol edin: kütle sıfıra giderse, hız ışık hızına "
   "yaklaşırsa, açı 0 veya 90° olursa formülünüz ne veriyor?",
   "Bir konuyu bana `... nedir` diye sorup ardından `... ornek ver` "
   "diyebilirsiniz; anlatım ve çözümlü örnek birlikte gelir."],
  ["You cannot learn physics without solving problems. Do at least 5 after "
   "each chapter — that is the only way to tell understanding from the "
   "feeling of understanding.",
   "Check every result by dimensional analysis. A result whose dimensions "
   "fail is certainly wrong; one that passes is far more likely right.",
   "Check limiting cases: what does your formula give as mass goes to zero, "
   "as speed approaches c, or at 0 and 90 degrees?",
   "Ask me `what is ...` then `give an example of ...` to get an explanation "
   "and a worked problem together."])


# ══════════════════════════════════════════════════════ SAYISAL / SİMÜLASYON
P("sayisal", "Sayısal Fizik ve Simülasyon Yol Haritası",
  "Computational Physics Roadmap",
  "sayisal fizik|simulasyon|hesaplamali fizik|computational|numerical|"
  "sayisal yontem|modelleme",
  """
Fizik problemlerini bilgisayarla çözmeyi öğrenme planı. MATLAB yol haritasının
2. aşamasını bitirmiş olmanız varsayılır (Python ile de aynı sırayı izleyebilirsiniz).
""",
  """
A plan for solving physics problems on a computer. It assumes you have finished
stage 2 of the MATLAB roadmap (the same order works in Python).
""",
  [
    S("1. Sayısal doğruluğun temelleri", "1 hafta",
      ["Kayan nokta aritmetiği, makine epsilonu",
       "Yuvarlama ve kesme hatası ayrımı",
       "Catastrophic cancellation (yakın sayıların farkı)",
       "Yakınsama mertebesi kavramı O(h), O(h²), O(h⁴)"],
      "Bu aşamayı atlayan herkes, sonucu yanlış olan ama hatasız çalışan bir "
      "kod yazar ve neden yanlış olduğunu bulamaz.",
      "İkinci derece denklemin köklerini standart formülle hesaplayın; "
      "b² ≫ 4ac olduğunda bir kökün neden anlamsız çıktığını gösterin ve "
      "formülü yeniden düzenleyerek düzeltin.",
      "`x^2 - 1000000*x + 1 = 0 coz`"),

    S("2. Kök bulma ve integral", "1-2 hafta",
      ["Bisection, Newton-Raphson, secant",
       "Yamuk ve Simpson kuralı",
       "Gauss kuadratürü",
       "Monte Carlo integrasyonu ve N^(-1/2) hata ölçeklemesi"],
      "Analitik çözümü olmayan integraller fizikte kuraldır, istisna değil. "
      "Yüksek boyutta Monte Carlo tek pratik seçenektir.",
      "Aynı integrali üç yöntemle hesaplayıp hatanın adım sayısıyla nasıl "
      "azaldığını log-log grafikte gösterin; eğimler mertebeleri vermeli.",
      "`monte carlo matlab kodu`"),

    S("3. Adi diferansiyel denklemler", "2 hafta",
      ["Euler, RK2, RK4 ve kararlılık",
       "Adaptif adım (RK45)",
       "Stiff sistemler ve örtük yöntemler",
       "Simplektik integratörler: Verlet, leapfrog"],
      "Uzun süreli simülasyonlarda doğruluk değil **kararlılık** belirleyicidir. "
      "RK4 gezegen yörüngesini yavaşça kaydırırken Verlet enerjiyi sınırlı tutar.",
      "Bir gezegen yörüngesini RK4 ve Verlet ile 10⁶ adım çözün; enerji "
      "kaymasını karşılaştırın.",
      "`gezegen yorungesi matlab kodu`"),

    S("4. Kısmi diferansiyel denklemler", "3-4 hafta",
      ["Sonlu farklar: ileri, geri, merkezi",
       "Açık ve örtük şemalar; kararlılık koşulları (CFL, r ≤ 0.5)",
       "Isı denklemi, dalga denklemi, Laplace denklemi",
       "Sınır koşulları: Dirichlet, Neumann"],
      "Alan kuramlarının, akışkanların ve ısı transferinin tamamı buradadır. "
      "Kararlılık koşulunu ihlal ederseniz çözüm birkaç adımda patlar.",
      "Isı denklemini r = 0.4 ve r = 0.6 ile çözün; ikincisinin neden "
      "patladığını grafikle gösterin.",
      "`isi denklemi matlab kodu`"),

    S("5. Özdeğer problemleri ve kuantum", "2-3 hafta",
      ["Hamiltonyeni matrise çevirme (sonlu farklar)",
       "`eig` ile enerji düzeyleri ve dalga fonksiyonları",
       "Normalizasyon ve fiziksel yorum",
       "Farklı potansiyeller: kare kuyu, harmonik, çift kuyu"],
      "Zamandan bağımsız Schrödinger denklemi bir özdeğer problemidir. Bunu "
      "kurabilirseniz istediğiniz potansiyeli çözebilirsiniz.",
      "Harmonik osilatörü sayısal çözün; enerji düzeylerinin (n+½)ħω "
      "olduğunu doğrulayın.",
      "`kuantum kuyusu simulasyonu`"),
  ],
  [
    S("1. Foundations of numerical accuracy", "1 week",
      ["Floating point, machine epsilon",
       "Round-off versus truncation error",
       "Catastrophic cancellation",
       "Order of convergence: O(h), O(h²), O(h⁴)"],
      "Skip this and you will write code that runs cleanly, gives wrong "
      "answers, and gives you no clue why.",
      "Compute quadratic roots with the standard formula, show why one root "
      "becomes meaningless when b² ≫ 4ac, and fix it by rearranging.",
      "`solve x^2 - 1000000*x + 1 = 0`"),

    S("2. Root finding and integration", "1-2 weeks",
      ["Bisection, Newton-Raphson, secant",
       "Trapezoid and Simpson's rule",
       "Gaussian quadrature",
       "Monte Carlo integration and N^(-1/2) error scaling"],
      "Integrals with no closed form are the rule in physics, not the "
      "exception, and in high dimensions Monte Carlo is the only option.",
      "Evaluate one integral three ways and show on a log-log plot how error "
      "falls with step count; the slopes should reveal the orders.",
      "`monte carlo matlab code`"),

    S("3. Ordinary differential equations", "2 weeks",
      ["Euler, RK2, RK4 and stability",
       "Adaptive stepping (RK45)",
       "Stiff systems and implicit methods",
       "Symplectic integrators: Verlet, leapfrog"],
      "For long runs, **stability** matters more than accuracy. RK4 drifts a "
      "planetary orbit while Verlet keeps energy bounded.",
      "Integrate a planetary orbit with RK4 and Verlet for 10⁶ steps and "
      "compare the energy drift.",
      "`planetary orbit matlab code`"),

    S("4. Partial differential equations", "3-4 weeks",
      ["Finite differences: forward, backward, central",
       "Explicit and implicit schemes; stability (CFL, r ≤ 0.5)",
       "Heat, wave and Laplace equations",
       "Boundary conditions: Dirichlet, Neumann"],
      "Field theories, fluids and heat transfer all live here. Violate the "
      "stability condition and the solution explodes within a few steps.",
      "Solve the heat equation at r = 0.4 and r = 0.6 and show graphically why "
      "the second blows up.",
      "`heat equation matlab code`"),

    S("5. Eigenvalue problems and quantum", "2-3 weeks",
      ["Turning a Hamiltonian into a matrix (finite differences)",
       "Energy levels and wavefunctions via `eig`",
       "Normalisation and physical interpretation",
       "Different potentials: square well, harmonic, double well"],
      "The time-independent Schrödinger equation is an eigenvalue problem. "
      "Set it up once and you can solve any potential.",
      "Solve the harmonic oscillator numerically and verify the levels are "
      "(n+½)ħω.",
      "`quantum well simulation`"),
  ])


def _norm(s):
    s = (s or "").lower()
    for a, b in {"ı": "i", "İ": "i", "ş": "s", "ğ": "g", "ü": "u",
                 "ö": "o", "ç": "c", "â": "a"}.items():
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9\s]", " ", s)


# Turkce cekim ekleri: "fizige", "matlabi", "simulasyonu" gibi biçimlerin
# koke indirgenmesi icin. Uzundan kisaya denenir.
_SUFFIXES = ("larinda", "lerinde", "larini", "lerini", "lardan", "lerden",
             "lariyla", "leriyle", "lari", "leri", "lara", "lere", "larda",
             "lerde", "lar", "ler", "sinda", "sinde", "inda", "inde",
             "nda", "nde", "dan", "den", "tan", "ten", "nin", "nun",
             "yla", "yle", "ile", "in", "un", "ya", "ye", "na", "ne",
             "da", "de", "ta", "te", "yi", "yu", "i", "u", "e", "a")

# Son sessiz yumusamasi: fizik -> fizige, kitap -> kitabi
_SOFTEN = {"g": "k", "b": "p", "c": "c", "d": "t"}


def stem(word):
    w = _norm(word).strip()
    if len(w) < 4:
        return w
    for suf in _SUFFIXES:
        if len(w) > len(suf) + 2 and w.endswith(suf):
            w = w[:-len(suf)]
            break
    if w and w[-1] in _SOFTEN:
        w = w[:-1] + _SOFTEN[w[-1]]
    return w


def find(query):
    """Sorguya en uygun yol haritasini bul.

    Puanlar toplanmaz, en iyi anahtar kelime esimesi alinir: toplasaydik
    ust uste binen anahtar kelimeleri olan genel yol haritasi ("fizik"),
    daha ozel olani ("sayisal fizik") her zaman ezerdi.
    """
    q = _norm(query)
    qs = set(stem(w) for w in q.split() if len(w) > 2)
    best, best_score = None, 0
    for key, p in PATHS.items():
        score = 0
        # Anahtarin kendisi de bir eslesmedir: liste ekranda "sayisal yol
        # haritasi" diye gosteriyor, ama "sayisal" kelimesi kw listesinde
        # yoktu ve komut calismiyordu.
        ka = _norm(key.split(":", 1)[-1])
        if ka and re.search(r"(?<!\w)%s(?!\w)" % re.escape(ka), q):
            score = max(score, 20 + len(ka))
        for kw in p["kw"]:
            k = _norm(kw).strip()
            if not k:
                continue
            if re.search(r"(?<!\w)%s(?!\w)" % re.escape(k), q):
                score = max(score, 20 + len(k))
            elif " " not in k and stem(k) in qs:
                # Cekim eki almis hali ("fizige" -> "fizik")
                score = max(score, 16 + len(k))
        if score > best_score:
            best, best_score = p, score
    return best


def render(path, lang="tr"):
    """Yol haritasini metne cevir."""
    tr = lang == "tr"
    lines = ["### " + (path["tr"] if tr else path["en"]), ""]
    lines.append(path["ozet_tr"] if tr else path["ozet_en"])
    lines.append("")
    asamalar = path["asamalar"] if tr else path["asamalar_en"]
    for a in asamalar:
        lines.append("---")
        lines.append("")
        lines.append("#### %s  <span class='meta'>%s</span>" % (a["ad"], a["sure"]))
        lines.append("")
        for k in a["konular"]:
            lines.append("- " + k)
        lines.append("")
        lines.append("> **%s** %s" % ("Neden:" if tr else "Why:", a["neden"]))
        lines.append("")
        lines.append("**%s** %s" % ("Alıştırma:" if tr else "Exercise:",
                                    a["alistirma"]))
        lines.append("")
        lines.append("**%s** `%s`" % ("Bana yazın:" if tr else "Ask me:", a["dene"]))
        lines.append("")
    ip = path["ipuclari_tr"] if tr else path["ipuclari_en"]
    if ip:
        lines.append("---")
        lines.append("")
        lines.append("#### " + ("Yol boyunca işinize yarayacak dört şey"
                                if tr else "Four things that will help"))
        lines.append("")
        for i in ip:
            lines.append("- " + i)
    return "\n".join(lines)


def render_stage(path, index, lang="tr"):
    """Tek bir asamayi genisleterek anlat (1 tabanli index)."""
    tr = lang == "tr"
    asamalar = path["asamalar"] if tr else path["asamalar_en"]
    if not (1 <= index <= len(asamalar)):
        return None
    a = asamalar[index - 1]
    lines = ["### %s — %s" % (path["tr"] if tr else path["en"], a["ad"]), ""]
    lines.append("<span class='meta'>%s · %s %d/%d</span>"
                 % (a["sure"], "aşama" if tr else "stage", index, len(asamalar)))
    lines.append("")
    lines.append("> **%s** %s" % ("Neden bu aşama:" if tr else "Why this stage:",
                                  a["neden"]))
    lines.append("")
    lines.append("**%s**" % ("Öğrenilecek konular" if tr else "Topics to learn"))
    lines.append("")
    for k in a["konular"]:
        lines.append("- " + k)
    lines.append("")
    lines.append("**%s** %s" % ("Alıştırma:" if tr else "Exercise:", a["alistirma"]))
    lines.append("")
    lines.append("**%s** `%s`" % ("Bana yazın:" if tr else "Ask me:", a["dene"]))
    lines.append("")
    if index < len(asamalar):
        sonraki = asamalar[index]["ad"]
        lines.append("---")
        lines.append("")
        lines.append(L_(tr, "Sonraki aşama: **%s**. Onu da açmak için "
                            "`%d. aşamayı anlat` yazın.",
                        "Next stage: **%s**. Ask `explain stage %d` for it.")
                     % (sonraki, index + 1))
    else:
        lines.append("---")
        lines.append("")
        lines.append(L_(tr, "Bu son aşama. Tüm haritayı görmek için "
                            "`%s yol haritası` yazabilirsiniz.",
                        "This is the final stage. Ask `%s roadmap` for the "
                        "whole plan.") % path["key"])
    return "\n".join(lines)


def L_(tr, a, b):
    return a if tr else b


_STAGE_RE = re.compile(
    r"(?:^|\D)(\d)\s*\.?\s*(?:asama|adim|aşama|adım|stage|step|bolum|bölüm)|"
    r"(?:asama|adim|aşama|adım|stage|step)\s*(\d)")


def stage_number(text):
    """Metinde bir asama numarasi geciyor mu? ('4. asamayi ac' -> 4)"""
    m = _STAGE_RE.search(_norm(text))
    if not m:
        return None
    n = m.group(1) or m.group(2)
    try:
        n = int(n)
    except (TypeError, ValueError):
        return None
    return n if 1 <= n <= 9 else None


def list_paths(lang="tr"):
    return [(p["key"], p["tr"] if lang == "tr" else p["en"])
            for p in PATHS.values()]
