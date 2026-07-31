# -*- coding: utf-8 -*-
"""Gunluk hayattan fizik: herkesin sordugu klasik sorular.

Olculdu: "gokyuzu neden mavi" sorusuna sistem, icinde "mavi kart" gecen
bir Turk vatandaslik hukuku makalesini getiriyordu. Fizigin en bilinen
sorusu cekirdekte yoktu ve korpus tek bir kelime uzerinden alakasiz bir
kaynaga kaydi.

Bu sorular basit gorunur ama cevaplari gercek fiziktir: sacilmanin
dalga boyu bagimligi, kaldirma kuvveti, kirilma ve dispersiyon. Bir
ogretmenin bunlari hazir ve dogru bilmesi gerekir.
"""
from .knowledge import T

GUNLUK_KONULAR = [

T("sacilma", "Işığın Saçılması: Gökyüzü Neden Mavi",
  "Light Scattering: Why the Sky is Blue", """
**Kisa cevap:** Havadaki molekuller mavi isigi kirmizidan cok daha
siddetli sacar.

**Rayleigh sacilmasi:** Isik, dalga boyundan cok kucuk parcaciklara
(hava molekulleri, ~0,3 nm) carptiginda sacilma siddeti
    I ∝ 1/λ⁴
Mavi (450 nm) ile kirmizi (700 nm) arasindaki oran (700/450)⁴ ≈ 5,8.
Yani mavi isik yaklasik ALTI KAT daha cok sacilir. Gokyuzunun her
yerinden gozumuze bu sacilmis mavi isik gelir.

**Peki neden mor degil?** Morun dalga boyu daha da kisa, yani daha da
cok sacilir. Iki sebep: Gunes'in tayfinda mor isik daha azdir, ve insan
gozunun mor duyarliligi dusuktur. Ikisi birlesince gogu MAVI goruruz.

**Gun batimi neden kirmizi:** Gunes ufka yakinken isik atmosferde cok
daha uzun yol kat eder. Mavi bilesen yol boyunca sacilip dagilir, geriye
kirmizi-turuncu kalir. Ayni fizigin ters yuzudur.

**Bulutlar neden beyaz:** Bulut damlaciklari (~10 μm) isigin dalga
boyundan BUYUKTUR. Bu durumda Rayleigh degil Mie sacilmasi gecerlidir ve
sacilma dalga boyuna neredeyse hic bagli degildir — tum renkler esit
sacilir, sonuc beyazdir. Yagmur bulutlarinin gri gorunmesi ise isigin
kalin bulutu asamamasindandir.

**Denizin mavisi:** Kismen gogun yansimasi, kismen de suyun kirmizi
isigi sogurmasidir — iki ayri mekanizma.
""", """
Air molecules scatter blue light far more strongly than red, since
Rayleigh scattering goes as 1/lambda^4: blue is scattered about six times
more than red. Sunsets are red because the long slant path scatters the
blue away. Clouds are white because their droplets are larger than the
wavelength, putting them in the Mie regime where scattering is nearly
wavelength-independent.
""",
  eqs=["I ∝ 1/λ⁴", "I_mavi/I_kirmizi = (λ_k/λ_m)⁴"],
  ex_tr=["Oran hesabi: (700/450)⁴ = (1,556)⁴ = 5,86. Mavi isik kirmiziya "
         "gore yaklasik 5,9 kat daha cok sacilir. Ayni yasa yuzunden "
         "sis lambalari SARI secilir: uzun dalga boyu sis damlaciklarinda "
         "daha az sacilir ve daha uzaga ulasir."],
  ex_en=["(700/450)^4 = 5.9, so blue scatters about six times more than red; "
         "the same law is why fog lights are yellow."],
  kw="gokyuzu neden mavi|gok neden mavi|gokyuzunun rengi|gun batimi neden "
     "kirmizi|bulutlar neden beyaz|rayleigh sacilmasi|mie sacilmasi|"
     "isik sacilmasi|why is the sky blue|rayleigh scattering",
  related="dalga_boyu|optik"),

T("kaldirma_gunluk", "Yüzme ve Batma: Buz Neden Yüzer",
  "Floating and Sinking: Why Ice Floats", """
**Arsimet ilkesi:** Bir cisme etki eden kaldirma kuvveti, TASIRDIGI
sivinin agirligina esittir: F = ρ_sivi · V_batan · g.

**Yuzme kosulu:** Cisim, agirligi kadar sivi tasirabiliyorsa yuzer. Bu da
ortalama yogunlugun sividan kucuk olmasi demektir.

**Buz neden yuzer:** Su, donarken GENISLEYEN ender maddelerden biridir.
Hidrojen bagi, katı halde molekulleri acik ve bosluklu bir kafese
oturtur. Buzun yogunlugu 917 kg/m³, suyunki 1000 kg/m³. Oran 0,917 —
yani buzdaginin yaklasik %92'si su altindadir, ancak %8'i gorunur.

**Bu bir tesaduf degil, hayat sartidir:** Buz batsaydi goller dipten
donar, yazin da erimezdi; su altindaki yasam surekli buz altinda kalirdi.

**Celik gemi neden batmaz:** Celigin yogunlugu suyun sekiz kati, ama
geminin ORTALAMA yogunlugu (govde + icindeki hava) sudan kucuktur. Onemli
olan malzemenin degil, cismin butununun yogunlugudur.

**Yuzen cismin ne kadari batar:** Denge halinde
    V_batan / V_toplam = ρ_cisim / ρ_sivi
""", """
Buoyancy equals the weight of displaced fluid. Ice floats because water
expands on freezing (917 vs 1000 kg/m3), so about 92% of an iceberg sits
below the surface. A steel ship floats because its average density,
including the enclosed air, is less than water's.
""",
  eqs=["F = ρ_sıvı·V_batan·g", "V_batan/V = ρ_cisim/ρ_sıvı"],
  ex_tr=["Buzdagi: 917/1000 = 0,917. Hacminin %91,7'si su altinda, %8,3'u "
         "ustunde. 'Buzdaginin gorunen kismi' deyimi tam da bu sayidir. "
         "Insan vucudunun yogunlugu ~985 kg/m³ oldugundan ciger dolu "
         "nefeste yuzeriz; nefes verince yogunluk artar ve batariz."],
  ex_en=["Ice at 917 kg/m3 in water at 1000 leaves 8.3% above the surface."],
  kw="buz neden yuzer|neden yuzer|neden batar|gemi neden batmaz|"
     "buzdagi|arsimet gunluk|yuzme kosulu|why does ice float",
  related="arsimet|yogunluk"),

T("gokkusagi", "Gökkuşağı ve Renklere Ayrılma", "Rainbows and Dispersion", """
**Nasil olusur:** Yagmur damlasina giren isik once KIRILIR, damlanin arka
yuzeyinden YANSIR, cikarken tekrar kirilir. Kirilma indisi dalga boyuna
bagli oldugu icin (dispersiyon) her renk biraz farkli acida cikar.

**Neden hep 42 derece:** Damladan cikan isinlarin sapma acisinin bir
EN KUCUK degeri vardir; isik o acinin cevresinde yigilir. Kirmizi icin
bu aci ~42,4°, mor icin ~40,7°. Bu yuzden gokkusagi hep ayni buyuklukte
gorunur ve merkezi, Gunes'in tam karsi yonundedir (antisolar nokta).

**Neden yay bicimli:** 42°'lik kosulu saglayan tum yonler, bakis
dogrultusu etrafinda bir KONI olusturur. Yerden bakinca bu koninin
yalnizca ust kismini goruruz — yay. Ucaktan bakarsaniz gokkusagini tam
DAIRE olarak gorebilirsiniz.

**Ikincil gokkusagi:** Damla icinde IKI kez yansiyan isik ~51°'de ikinci
bir yay yapar ve renk sirasi TERSTIR. Iki yay arasi (Alexander karanlik
kusagi) daha koyudur, cunku oraya hicbir isin sacilmaz.

**Neden herkes farkli gokkusagi gorur:** Aci, GOZLEMCININ konumuna
gore tanimlidir. Yaninizdaki kisi baska damlalardan gelen isigi gorur.
""", """
Refraction, internal reflection and refraction again inside raindrops
produce a bow at about 42 degrees, where the deviation angle has a minimum
and light piles up. The secondary bow at 51 degrees has reversed colours
from a second internal reflection.
""",
  eqs=["n₁sinθ₁ = n₂sinθ₂", "θ_kirmizi ≈ 42,4°", "θ_mor ≈ 40,7°"],
  ex_tr=["Suyun kirilma indisi kirmizi icin 1,331, mor icin 1,344. Bu "
         "kucuk fark (%1) 1,7 derecelik aci farkina donusur ve "
         "gokkusaginin genisligi tam olarak budur. Dispersiyon kucuk "
         "sebeplerin gorunur sonuclara donusmesinin guzel bir ornegidir."],
  ex_en=["The refractive index differs by 1% between red and violet, which "
         "becomes the 1.7 degree width of the bow."],
  kw="gokkusagi nasil olusur|gokkusagi neden|gokkusagi renkleri|dispersiyon|"
     "prizma renk|neden 42 derece|rainbow|why rainbow",
  related="snell|optik"),

T("gunluk_termo", "Günlük Isı Soruları", "Everyday Heat Questions", """
**Metal neden tahtadan soguk hisseder?** Ikisi de oda sicakligindadir.
Fark ISIL ILETKENLIKTEDIR: metal, elinizden isiyi hizla ceker
(k ≈ 200 W/m·K), tahta cekemez (k ≈ 0,15). Cildiniz sicakligi degil,
ISI KAYBI HIZINI hisseder.

**Kaynayan su neden 100 °C'de kalir?** Verilen isi sicakligi degil, HAL
DEGISIMINI besler (gizli isi). Suyun buharlasma gizli isisi 2260 kJ/kg —
ayni suyu 0'dan 100'e cikarmanin bes katindan fazla.

**Yuksek yerde su neden daha erken kaynar?** Kaynama, buhar basincinin
DIS BASINCA esitlendigi noktadir. 2000 m'de basinc ~0,8 atm, su ~93 °C'de
kaynar. Erken kaynar ama daha SOGUK kaynar; bu yuzden yemek gec pisher.

**Uflemek neden hem isitir hem sogutur?** Elinize agzinizi acip
uflediginizde yavas ve sicak hava gelir. Dudaklarinizi buzunce hava
genisleyerek soguru ve hizli akis buharlasmayi artirir.

**Terlemek neden serinletir?** Buharlasma, en enerjik molekulleri
goturur; geride kalanin ortalama enerjisi, yani SICAKLIGI duser.
Nemli havada buharlasma yavaslar, bu yuzden bunaltir.
""", """
Metal feels colder than wood at the same temperature because it conducts
heat away faster. Boiling water stays at 100 C because the energy goes
into the phase change. At altitude water boils cooler because boiling
happens when vapour pressure equals ambient pressure.
""",
  eqs=["Q = m·c·ΔT", "Q = m·L", "P = k·A·ΔT/d"],
  ex_tr=["100 g suyu 20 °C'den 100 °C'ye cikarmak: Q = 0,1×4186×80 = "
         "33,5 kJ. Ayni suyu tamamen buharlastirmak: Q = 0,1×2260000 = "
         "226 kJ. Yani KAYNATMAK, isitmaktan yaklasik yedi kat daha fazla "
         "enerji ister. Tencerenin kapagini kapatmanin sebebi budur."],
  ex_en=["Heating 100 g of water to boiling costs 33.5 kJ; evaporating it "
         "costs 226 kJ — about seven times more."],
  kw="metal neden soguk hisseder|su neden 100 derecede kalir|"
     "yuksekte su neden erken kaynar|terlemek neden serinletir|"
     "gizli isi gunluk|isil iletkenlik gunluk",
  related="isi|gizli_isi"),
]
