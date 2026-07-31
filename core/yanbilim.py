# -*- coding: utf-8 -*-
"""Kimya ve biyoloji: fizikle kesisen cekirdek.

Kullanici fizik ve MATLAB'in yaninda kimya ve biyoloji de istedi. Bunlari
ayri birer bilim olarak degil, FIZIKLE KESISTIKLERI yerden anlatiyoruz —
sistemin gucu burada: atomun yapisi kuantum mekanigidir, tepkime hizi
istatistiksel mekaniktir, sinir hucresi bir RC devresidir.

Boylece cekirdek bilgi tutarli kalir: her konu yine tanim, bagintilar ve
cozumlu ornek tasir; hicbiri "genel kultur" duzeyinde degildir.
"""
from .knowledge import T

YAN_BILIM_KONULARI = [

# ── Kimya ───────────────────────────────────────────────────────────────
T("atom_yapisi_kimya", "Atom Yapısı ve Periyodik Eğilimler",
  "Atomic Structure and Periodic Trends", """
Periyodik tablo bir liste degil, KUANTUM MEKANIGININ sonucudur.

**Orbitaller:** Elektronlar Schrödinger denkleminin cozumleri olan
orbitallerde bulunur. Kuantum sayilari n (kabuk), l (alt kabuk sekli),
m_l (yonelim), m_s (spin). Pauli dislama ilkesi ayni dort sayiyi iki
elektronun paylasmasini yasaklar — periyodik tablonun satir ve sutun
yapisi buradan cikar.

**Doldurma:** Aufbau ilkesi (dusuk enerjiden basla), Hund kurali (esit
enerjili orbitalleri once tek tek doldur). 1s → 2s → 2p → 3s → 3p → 4s →
3d sirasi, 4s'in 3d'den once gelmesiyle dikkat ceker; bu, ekranlamanin
sonucudur.

**Periyodik egilimler ve SEBEPLERI:**
| Egilim | Saga dogru | Asagi dogru | Sebep |
|---|---|---|---|
| Atom yaricapi | azalir | artar | cekirdek yuku artar / yeni kabuk |
| Iyonlasma enerjisi | artar | azalir | elektron daha siki bagli |
| Elektronegatiflik | artar | azalir | ayni |

**Bag turleri:** Iyonik (elektron aktarimi), kovalent (paylasim),
metalik (ortak elektron denizi). Hangisinin olusacagini elektronegatiflik
FARKI belirler: ~1,7'nin ustunde iyonik, altinda kovalent egilim.
""", """
The periodic table is a consequence of quantum mechanics: orbitals from the
Schrodinger equation, filled under Pauli exclusion, Aufbau and Hund's rule.
Trends in radius, ionisation energy and electronegativity follow from
nuclear charge and shielding. Electronegativity difference decides ionic
versus covalent bonding.
""",
  eqs=["E_n ∝ -Z_eff²/n²", "elektron sayisi = 2n²",
       "ΔEN > 1,7 → iyonik egilim"],
  ex_tr=["Neden 4s, 3d'den once dolar? 4s orbitali cekirdege daha cok "
         "'nufuz eder' (penetrasyon) ve daha az ekranlanir, bu yuzden "
         "enerjisi 3d'nin altina duser. Ama iyonlasirken ONCE 4s bosalir — "
         "cunku dolduktan sonra 3d enerjisi daha da duser. Bu yuzden "
         "Fe²⁺ iyonu 3d⁶'dir, 3d⁴4s² degil."],
  ex_en=["4s fills before 3d due to penetration, yet ionises first because "
         "3d drops below 4s once occupied: Fe2+ is 3d6."],
  kw="atom yapisi|periyodik tablo|orbital|elektron dizilimi|"
     "iyonlasma enerjisi|elektronegatiflik|kimyasal bag|aufbau|hund|"
     "4s 3d|orbital doldurma|doldurma sirasi|penetrasyon|ekranlama|"
     "neden 4s once|pauli dislama",
  related="kuantum_formalizm|bohr_E"),

T("tepkime_kinetigi", "Tepkime Kinetiği ve Termodinamiği",
  "Reaction Kinetics and Thermodynamics", """
Bir tepkimenin OLUP OLMAYACAGI ile NE KADAR HIZLI olacagi ayri sorulardir.

**Olur mu? (termodinamik):** Gibbs serbest enerjisi karar verir:
ΔG = ΔH - TΔS. Negatifse tepkime kendiliginden olur. Dikkat: "kendiliginden"
demek "hizli" demek DEGILDIR — elmasin grafite donusmesi ΔG < 0'dir ama
milyarlarca yil surer.

**Ne kadar hizli? (kinetik):** Arrhenius denklemi:
    k = A·exp(-Ea/RT)
Aktivasyon enerjisi Ea, tepkimenin asmasi gereken engeldir. Ustel bagimlilik
yuzunden kucuk sicaklik artislari hizi cok buyutur.

**Katalizor:** Aktivasyon enerjisini DUSURUR, ΔG'yi degistirmez. Yani
dengeyi kaydirmaz, dengeye ulasmayi hizlandirir. Enzimler biyolojik
katalizorlerdir ve Ea'yi cok buyuk oranda dusururler.

**Denge:** ΔG° = -RT·lnK. Denge sabiti K, tepkimenin ne kadar ilerledigini
soyler. Le Chatelier ilkesi: dengeye dokunursaniz sistem karsi koyar.

**Fizikle bagi:** Arrhenius'taki exp(-Ea/RT) tam olarak Boltzmann
carpanidir — molekullerin kacinin engeli asacak enerjiye sahip oldugunu
sayar. Kimyasal kinetik, istatistiksel mekaniktir.
""", """
Whether a reaction happens (thermodynamics, dG = dH - TdS) is separate from
how fast (kinetics, Arrhenius k = A exp(-Ea/RT)). Catalysts lower Ea
without changing dG. The Arrhenius exponential is the Boltzmann factor:
chemical kinetics is statistical mechanics.
""",
  eqs=["ΔG = ΔH - TΔS", "k = A·exp(-Ea/RT)", "ΔG° = -RT·lnK"],
  ex_tr=["Aktivasyon enerjisi 50 kJ/mol olan bir tepkime 25 °C'den 35 °C'ye "
         "cikarilirsa hiz orani: k₂/k₁ = exp[(Ea/R)(1/T₁ - 1/T₂)] = "
         "exp[(50000/8,314)(1/298 - 1/308)] ≈ 1,9. Yani 10 derecelik artis "
         "hizi yaklasik IKI KATINA cikarir — laboratuvardaki 'her 10 "
         "derecede hiz ikiye katlanir' kuralinin sayisal karsiligi budur."],
  ex_en=["For Ea = 50 kJ/mol, a 10 °C rise roughly doubles the rate — the "
         "familiar rule of thumb, quantified."],
  kw="tepkime kinetigi|arrhenius|aktivasyon enerjisi|katalizor|"
     "gibbs serbest enerji|denge sabiti|reaksiyon hizi|le chatelier",
  related="gibbs|istatistik_topluluk|boltzmann_faktoru"),

T("molekuler_spektroskopi", "Moleküler Spektroskopi",
  "Molecular Spectroscopy", """
Molekullerin yapisini, onlara isik gonderip hangi frekanslari YUTTUKLARINA
bakarak buluruz. Kimyanin gozu budur.

**Uc enerji olcegi:** Elektronik gecisler (~eV, morotesi-gorunur),
titresim (~0,1 eV, kizilotesi), donme (~0,001 eV, mikrodalga). Uc
buyukluk mertebesi fark, uc ayri teknik demektir.

**Kizilotesi (IR):** Molekulun titresim modlarini olcer. Bir mod IR'de
gorunur olmasi icin titresim sirasinda DIPOL MOMENTI degismelidir. Bu
yuzden N₂ ve O₂ IR'de sessizdir — atmosferin buyuk kismi sera etkisine
katilmaz; CO₂ ve H₂O katilir.

**NMR:** Cekirdek spinlerinin manyetik alandaki Zeeman yarilmasi.
Kimyasal cevre yerel alani biraz degistirir (kimyasal kayma) ve bu,
molekuldeki her hidrojenin nerede oldugunu ele verir. MR goruntuleme
ayni ilkedir.

**Bagi kuvvetle iliskilendirme:** Titresim frekansi
    ν = (1/2π)·√(k/μ)
Burada k bag sertligi, μ indirgenmis kutle. Ucul bag ikili bagdan, ikili
bag tekli bagdan daha yuksek frekansta titresir — IR spektrumu bag turunu
dogrudan soyler.
""", """
Spectroscopy probes molecules by which frequencies they absorb: electronic
(~eV), vibrational (~0.1 eV, IR), rotational (~0.001 eV, microwave). An IR
mode is active only if the dipole moment changes, which is why N2 and O2
are transparent while CO2 and H2O are greenhouse gases. NMR uses nuclear
Zeeman splitting and chemical shift.
""",
  eqs=["ν = (1/2π)·√(k/μ)", "μ = m₁m₂/(m₁+m₂)", "ΔE = h·ν"],
  ex_tr=["C–H bagi: k ≈ 500 N/m, indirgenmis kutle μ = (12·1)/(13) u = "
         "0,923 u = 1,53×10⁻²⁷ kg. ν = (1/2π)√(500/1,53×10⁻²⁷) ≈ "
         "9,1×10¹³ Hz, yani dalga sayisi ~3000 cm⁻¹. IR spektrumunda C–H "
         "gerilmesi tam bu bolgede gorulur."],
  ex_en=["A C–H bond with k = 500 N/m gives ~3000 cm-1, exactly where C–H "
         "stretching appears in IR spectra."],
  kw="spektroskopi|kizilotesi|ir spektrum|nmr|titresim modu|"
     "kimyasal kayma|sera gazi neden|molekul titresimi",
  related="harmonik_kuantum|zeeman|elektromanyetik_dalga"),

# ── Biyoloji ────────────────────────────────────────────────────────────
T("biyofizik_hucre", "Hücre Zarı ve Sinir İletimi",
  "Cell Membrane and Nerve Conduction", """
Sinir hucresi, fizik acisindan bir RC DEVRESIDIR ve bu benzetme
mecazi degil, niceldir.

**Zar potansiyeli:** Hucre zari iyonlari secici gecirir. Iyonlarin
dengedeki potansiyel farki Nernst denklemiyle verilir:
    E = (RT/zF)·ln([disari]/[iceri])
Potasyum icin bu ~-90 mV, sodyum icin ~+60 mV cikar. Dinlenim potansiyeli
(-70 mV) bu ikisinin gecirgenlikle agirlikli birlesimidir (Goldman
denklemi).

**Zar bir kondansatordur:** Lipit cift tabaka yalitkan, iki yani
iletken. Kapasitans yaklasik 1 μF/cm². Iyon kanallari direnc gorevi
gorur. Zaman sabiti τ = RC, sinyalin ne kadar hizli degisebilecegini
belirler.

**Aksiyon potansiyeli:** Esik asilinca sodyum kanallari acilir, pozitif
geri besleme baslar ve potansiyel hizla +40 mV'a firlar; sonra potasyum
kanallari repolarize eder. Hodgkin-Huxley modeli bunu diferansiyel
denklemlerle tam olarak tanimlar (1952 Nobel).

**Iletim hizi:** Miyelin kilifi zar kapasitansini dusurur ve direncini
artirir; sinyal Ranvier bogumlari arasinda "atlar" (sicramali iletim).
Hiz 1 m/s'den 100 m/s'ye cikar.
""", """
A neuron is quantitatively an RC circuit: the lipid bilayer is a capacitor
(~1 uF/cm2) and ion channels are resistors. Equilibrium potentials follow
the Nernst equation; the action potential is a positive-feedback sodium
event described by Hodgkin-Huxley. Myelin lowers capacitance and raises
resistance, taking conduction from 1 m/s to 100 m/s.
""",
  eqs=["E = (RT/zF)·ln([dis]/[ic])", "τ = R·C", "C_zar ≈ 1 μF/cm²"],
  ex_tr=["Potasyum icin Nernst: disarida 5 mM, iceride 140 mM, T = 310 K, "
         "z = +1. E = (8,314×310/96485)·ln(5/140) = 0,0267×(-3,33) = "
         "-89 mV. Olculen dinlenim potansiyelinin (-70 mV) potasyum "
         "dengesine bu kadar yakin olmasi, dinlenimde zarin agirlikli "
         "olarak POTASYUMA gecirgen oldugunu soyler."],
  ex_en=["The Nernst potential for K+ is -89 mV; the resting potential of "
         "-70 mV being close to it shows the membrane is mainly K+ "
         "permeable at rest."],
  kw="sinir iletimi|aksiyon potansiyeli|zar potansiyeli|nernst denklemi|"
     "hodgkin huxley|miyelin|biyofizik|hucre zari",
  related="rc_zaman|kapasitans"),

T("biyofizik_molekul", "Moleküler Biyofizik", "Molecular Biophysics", """
Hucre icindeki fizik, gunluk sezgimizden farkli bir dunyada gecer: kucuk
olcekte VISKOZITE baskindir, eylemsizlik onemsizdir.

**Dusuk Reynolds sayisi:** Bir bakteri icin Re ~ 10⁻⁵. Bu, yuzmenin
bal icinde yuzmek gibi oldugu anlamina gelir — motoru durdurursaniz
bakteri bir atom capi kadar bile ilerlemeden durur. Bu yuzden bakteriler
kamci CEVIRIR, kurbaga gibi kulac atmazlar (Purcell'in 'tersinir kulac'
teoremi).

**Brown hareketi:** Termal carpismalar molekulleri rastgele surukler.
Yayilim: ⟨x²⟩ = 2Dt. Einstein-Stokes bagintisi D = kT/(6πηr) yaricapi
ve viskoziteyi baglar. Hucre icinde tasima buyuk olcude BU rastgele
yurumeyle olur — pompaya gerek yoktur.

**Enerji olcegi:** Hucredeki tum sureclerin olcusu kT'dir (oda
sicakliginda ~0,025 eV = 4,1×10⁻²¹ J). ATP hidrolizi ~20 kT verir;
hidrojen bagi ~2-5 kT'dir, yani termal gurultuyle KOLAY kirilir. DNA'nin
cift sarmali bu yuzden acilip kapanabilir.

**Molekuler motorlar:** Kinesin, miyozin, ATP sentaz. Verimleri %50'yi
asar — insan yapimi motorlarin cogundan iyi. Rastgele termal hareketten
yonlu is cikarirlar (Brown circeri, ama ikinci yasayi ihlal etmeden:
ATP tuketirler).
""", """
Inside a cell viscosity dominates and inertia is negligible (Re ~ 1e-5):
a bacterium stops within an atom's width when its motor stops, which is why
flagella rotate rather than paddle. Transport is largely Brownian, with
<x^2> = 2Dt and D = kT/(6 pi eta r). The energy scale is kT: ATP gives
~20 kT while a hydrogen bond is 2-5 kT.
""",
  eqs=["⟨x²⟩ = 2Dt", "D = kT/(6πηr)", "Re = ρvL/η", "kT ≈ 4,1×10⁻²¹ J"],
  ex_tr=["Bir proteinin (r ≈ 5 nm) suda yayilim katsayisi: "
         "D = kT/(6πηr) = (4,1×10⁻²¹)/(6π×10⁻³×5×10⁻⁹) ≈ 4,4×10⁻¹¹ m²/s. "
         "10 μm'lik bir hucreyi kat etmesi: t = x²/(2D) = "
         "(10⁻⁵)²/(2×4,4×10⁻¹¹) ≈ 1,1 saniye. Yani hucre icinde difuzyon "
         "YETERLIDIR; ama 1 metrelik bir sinir hucresi icin ayni hesap "
         "binlerce yil verir — bu yuzden aktif tasima gerekir."],
  ex_en=["A protein diffuses across a 10 um cell in about a second, but the "
         "same calculation over 1 m gives thousands of years — hence active "
         "transport."],
  kw="biyofizik|brown hareketi|difuzyon|dusuk reynolds|molekuler motor|"
     "hucre ici tasima|einstein stokes|atp enerji",
  related="reynolds|stokes|istatistik_topluluk"),

T("radyasyon_biyoloji", "Radyasyonun Biyolojik Etkisi",
  "Biological Effects of Radiation", """
Radyasyonun zarari, tasidigi enerjiden cok bu enerjiyi NASIL biraktigina
baglidir.

**Iyonlastirici / iyonlastirmayan:** Sinir yaklasik 10 eV'dir (molekul
baglarini kirmaya yeten enerji). Morotesi, X ve gama isinlari
iyonlastiricidir. Radyo dalgalari, mikrodalga ve gorunur isik degildir —
cep telefonu isimasi molekul bagi kiramaz, yalnizca isitir.

**Doz birimleri:**
- **Gray (Gy):** birim kutleye birakilan enerji, J/kg. Fiziksel doz.
- **Sievert (Sv):** biyolojik etkiyle agirliklandirilmis doz. Alfa
  parcaciklari ayni enerjiyi cok kisa mesafede biraktigi icin agirlik
  carpani 20'dir; foton ve elektron icin 1.

**Zarar mekanizmasi:** Dogrudan DNA kirilmasi ya da suyun radyolizi ile
olusan serbest radikaller. Cift zincir kirilmasi en tehlikelisidir;
hucre onaramazsa mutasyon ya da hucre olumu olur.

**Buyukluk duygusu:** Dogal fon ~2,4 mSv/yil. Bir akciger BT'si ~7 mSv.
Akut olumcul doz ~4-5 Sv (tek seferde). Radyoterapi tumore kasten
20-70 Gy verir — ama yalnizca hedefe odaklanmis olarak.

**Neden mesafe onemli:** Nokta kaynaktan doz hizi ters kare ile azalir.
Uzakligi iki katina cikarmak dozu DORTTE BIRE indirir; kalkan
kalinligi ise ustel azaltma saglar (I = I₀e^(-μx)).
""", """
Damage depends on how energy is deposited. Above ~10 eV radiation is
ionising; radio and microwaves are not and cannot break bonds. The gray
measures deposited energy, the sievert weights it biologically (alpha has a
factor of 20). Natural background is ~2.4 mSv/year; radiotherapy delivers
20-70 Gy to a target.
""",
  eqs=["1 Gy = 1 J/kg", "H[Sv] = w_R · D[Gy]", "I = I₀·e^(-μx)",
       "doz ∝ 1/r²"],
  ex_tr=["70 kg'lik bir kisi tum vucuduna 4 Gy alirsa toplam enerji "
         "4 × 70 = 280 J'dur. Bu, bir fincan cayi bir derece bile "
         "isitmaya yetmez — ama muhtemel olumcul dozdur. Zarar isidan "
         "degil, DNA'daki iyonlasmadan gelir. Radyasyonun tehlikesini "
         "'enerji miktari' ile olcmek bu yuzden yaniltir."],
  ex_en=["A lethal 4 Gy whole-body dose is only 280 J for a 70 kg person — "
         "not enough to warm a cup of tea. The danger is ionisation, not "
         "heat."],
  kw="radyasyon biyolojik etki|sievert|gray|doz|iyonlastirici radyasyon|"
     "radyoterapi|dna hasari|serbest radikal|sievert ile gray|"
     "gray ile sievert|doz birimleri|radyasyon dozu",
  related="doz|sogurma|nukleer"),
]
