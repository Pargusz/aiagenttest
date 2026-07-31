# -*- coding: utf-8 -*-
"""Formuller icin gunluk dil sozlugu.

Kullanici formulun adini bilmez. "Bragg yasasi" demez, "kristalde x isini
hangi acida yansir" der. Formul tabanindaki anahtar kelimeler terimsel
oldugu icin bu tur sorular hicbir formule ulasmiyordu (olcum: %20).

Burada her formul icin insanlarin GERCEKTEN kullandigi ifadeler tutulur.
Ayri dosyada durmasinin sebebi: bu liste surekli buyuyecek. Yeni bir soru
kalibi ogrenildiginde formul tanimlarina dokunmadan buraya eklenir.

Bicim:  "formul_id": ("turkce ifadeler|...", "english phrases|...")
"""

EK_ANAHTAR = {
    # ── Kinematik ─────────────────────────────────────────────────────────
    "v_ort": ("kac km saat gider|ne kadar hizli gidiyor|ortalama surat",
              "how fast|average speed|km per hour"),
    "kin_v": ("saniyede duruyor|saniyede durur|hizdan duruyor|"
              "kac saniyede durur|frenleme ivmesi|yavaslama ivmesi|"
              "yukari atilan cismin hizi|yukari atiliyor hizi|"
              "asagi birakilan cismin hizi|kac saniye sonra hizi|"
              "saniye sonra hizi ne|sonraki hizi|"
              "ne kadar hizlanir|son hizi ne olur|hizlanan aracin hizi|"
              "duran araba hizlanirsa",
              "final velocity|speeds up|how fast after|"
              "decelerates from|comes to rest in|slows from|"
              "velocity after|speed after|deceleration|braking"),
    "kin_x": ("ne kadar yol alir|kac metre gider|kat edilen mesafe|"
              "hizlanirken alinan yol",
              "distance traveled|how far does it go"),
    "kin_v2": ("yere carpma hizi|carpma hizi|kac hizla carpar|"
               "yuksekten birakilan cismin hizi|dusen cismin hizi|"
               "fren mesafesi|durma mesafesi|ne kadar mesafede durur|"
               "frene basinca|kac metrede durur|hiz kare",
               "dropped from|falls from|speed on impact|hits the ground|impact speed|final speed after falling|braking distance|stopping distance|how far to stop"),
    "ivme": ("ne kadar hizlaniyor|sifirdan yuze|hizlanma orani|kac saniyede hizlanir",
             "acceleration rate|zero to hundred"),
    "egik_menzil": ("ne kadar uzaga duser|top nereye duser|atisin menzili|"
                    "en uzaga nasil atarim|kac metre oteye gider",
                    "how far does it land|projectile range|farthest throw"),
    "egik_h": ("ne kadar yukselir|en yuksek nokta|tepe noktasi|"
               "cikabilecegi yukseklik|kac metre yukselir",
               "maximum height|how high does it go|peak"),
    "serbest_dusme": ("havada ne kadar kalir|kac saniyede duser|dusme suresi|"
                      "kuleden birakilan|yukaridan birakinca|dusme yuksekligi|"
                      "havada kalma suresi",
                      "how long in the air|time to fall|dropped from height|"
                      "time to reach the ground|how long to fall|"
                      "time to hit the ground|falling time"),
    "merkezcil": ("virajda savrulma|donerken olusan ivme|dairesel harekette ivme",
                  "centripetal acceleration|going around a curve"),
    "acisal": ("kac devir atar|donme hizi|dakikada devir|carkin donmesi",
               "rpm|revolutions per minute|spin rate"),
    "periyot_frekans": ("kac saniyede bir tekrarlar|devir suresi|"
                        "saniyede kac kez",
                        "period and frequency|how often|cycles per second"),

    # ── Dinamik ───────────────────────────────────────────────────────────
    "newton2": ("fren kuvveti|durdurma kuvveti|frenleme kuvveti|"
                "kac newton kuvvet gerekir|uygulanan kuvvet|"
                "ne kadar kuvvet gerekir|itmek icin gereken kuvvet|"
                "halat gerilimi|asansor kablosu|ip ne kadar gerilir|"
                "kutle ivme kuvvet|cismi hareket ettirmek",
                "how much force is needed|tension in the cable|push an object"),
    "agirlik": ("kac kilo kac newton eder|tartida ne gosterir|"
                "yercekimi ne kadar ceker|ayda agirligim",
                "weight on scale|how heavy|gravity pull"),
    "surtunme": ("neden duruyor|zemin tutuyor mu|kayar mi|"
                 "surtunmeden dolayi yavaslama|kaymaya baslar mi",
                 "will it slide|friction force|does it stay put"),
    "hooke": ("yayi germek|yay ne kadar uzar|yayin uzamasi|yay sabiti|"
              "asinca uzayan yay|kuvvet uygulayinca uzama",
              "how much does the spring stretch|spring constant"),
    "momentum": ("hareket miktari|carpismada korunan|kutle carpi hiz",
                 "momentum of a moving object"),
    "impuls": ("carpma etkisi|hava yastigi neden|darbe suresi|"
               "carpismada etki suresi|yumusak inis",
               "airbag|impact force over time|impulse"),
    "esnek_carpisma_v1": ("bilardo topu carpismasi|carpisma sonrasi hizlar|"
                          "esnek carpisma sonrasi|carpip geri doner",
                          "billiard balls collide|after elastic collision"),
    "esnek_olmayan": ("iki arac carpisti|carpisip birlikte hareket|"
                      "yapisarak devam|carpisma sonrasi ortak hiz",
                      "cars crash and stick|combined velocity after crash"),
    "tork": ("somunu sikma|kolun ucundan itmek|kapiyi acmak|"
             "uzun anahtar neden kolay|donme etkisi|moment kolu",
             "loosen a bolt|why longer wrench|turning effect"),
    "donme_newton": ("donmeye baslamasi|acisal ivme|carki hizlandirmak",
                     "angular acceleration|start spinning"),
    "eylemsizlik_cubuk": ("cubugun eylemsizlik momenti|donen cubuk",
                          "moment of inertia of a rod"),
    "eylemsizlik_disk": ("diskin eylemsizlik momenti|tekerlek atalet|"
                         "volanin atalet momenti",
                         "moment of inertia of a disk|flywheel"),
    "eylemsizlik_kure": ("kurenin eylemsizlik momenti|top atalet momenti",
                         "moment of inertia of a sphere"),
    "paralel_eksen": ("ekseni kaydirinca atalet|paralel eksen",
                      "parallel axis theorem|shifted axis"),
    "merkezcil_kuvvet": ("virajda tutan kuvvet|savrulmayi engelleyen|"
                         "ipin ucunda dondururken|donerken ip gerilimi",
                         "force that keeps it in a circle|swinging on a rope"),
    "kutle_cekim": ("iki cisim birbirini ceker|cekim kuvveti|"
                    "dunya beni neden cekiyor|kutlelerin cekimi",
                    "gravitational attraction between masses"),
    "kacis_hiz": ("uzaya cikmak icin hiz|yercekiminden kurtulmak|"
                  "roketi firlatmak icin gereken hiz|kurtulma hizi|"
                  "dunyadan kacis",
                  "escape velocity|speed to leave earth|launch a rocket"),
    "yorunge_hiz": ("uydu hizi|yorungede kalmak icin hiz|"
                    "dunyaya dusmemesi icin|dairesel yorunge hizi",
                    "satellite speed|stay in orbit"),
    "kepler3": ("gezegenin yili|yorunge periyodu|dolanma suresi|"
                "gezegen gunesi kac yilda dolanir",
                "orbital period|planet year|how long to orbit"),
    "gelgit": ("gelgit|met cezir|ayin denizi cekmesi", "tides|tidal force"),
    "schwarzschild": ("kara delik yaricapi|olay ufku|"
                      "ne kadar sikisirsa kara delik",
                      "black hole radius|event horizon"),
    "kutle_merkezi": ("agirlik merkezi|denge noktasi|nereden tutmali",
                      "center of mass|balance point"),
    "aci_momentum": ("patinajci neden hizlanir|kollarini toplayinca|"
                     "acisal momentum korunumu|donerken hizlanma",
                     "figure skater spins faster|angular momentum"),
    "egik_duzlem": ("egik duzlemde kayma|rampa|yokusta kuvvet|"
                    "egimde asagi kayar mi",
                    "on a ramp|inclined plane|slope"),

    # ── Enerji ────────────────────────────────────────────────────────────
    "is": ("yapilan is|iterek is yapmak|ne kadar is yapildi|kaldirirken is",
           "work done by a force|pushing work"),
    "kinetik": ("hareket enerjisi|hizli cismin enerjisi|"
                "hiz iki kat olursa enerji", "energy of motion"),
    "potansiyel": ("yukseklik enerjisi|kaldirinca kazanilan enerji|"
                   "raftaki cismin enerjisi", "stored height energy"),
    "guc": ("saniyede yapilan is|kac watt|beygir gucu|ne kadar guclu",
            "power in watts|horsepower"),
    "guc_hiz": ("cekis gucu|hizda gereken guc|motor gucu hiz",
                "power needed at speed"),
    "verim": ("ne kadari ise doner|verim yuzde kac|kayip ne kadar|"
              "makine verimi",
              "efficiency percentage|how much is wasted"),
    "yay_enerji": ("yayda depolanan enerji|sikistirilmis yay|"
                   "yay firlatir mi", "energy stored in a spring"),
    "donme_enerji": ("donen cismin enerjisi|volan enerjisi|"
                     "donmeyi durdurmak icin enerji|donme kinetik enerjisi",
                     "rotational kinetic energy|energy of a spinning object"),
    "yuvarlanma_enerji": ("yuvarlanan topun enerjisi|egimde yuvarlanma|"
                          "hangisi once iner",
                          "rolling object energy|which rolls faster"),
    "E_mc2": ("kutle enerjiye donusur|madde enerji|einstein denklemi",
              "mass energy equivalence"),

    # ── Elektrik ──────────────────────────────────────────────────────────
    "ohm": ("devreden gecen akim|kac amper geciyor|gerilim direnc akim|"
            "voltaj bolununce", "current in a circuit|amps through"),
    "direnc_tel": ("kablonun direnci|ince kablo neden isinir|"
                   "telin uzunlugu direnc|kesit direnc",
                   "wire resistance|thin wire"),
    "elektrik_guc": ("elektrik faturasi|cihaz kac watt ceker|"
                     "tuketim ne kadar|kwh hesabi|enerji tuketimi",
                     "electricity bill|power consumption|watts drawn"),
    "joule_isi": ("kablo neden isiniyor|direncte olusan isi|"
                  "elektrikli isitici", "wire heats up|resistive heating"),
    "coulomb": ("iki yuk birbirini iter|elektrik cekim itme|"
                "yuklu cisimler arasindaki kuvvet",
                "force between two charges"),
    "E_kuvvet": ("elektrik alaninda kuvvet|yuke etkiyen kuvvet",
                 "force on a charge in a field"),
    "E_alan": ("elektrik alani ne kadar|alan siddeti",
               "electric field strength"),
    "potansiyel_V": ("elektriksel potansiyel|voltaj nereden gelir|gerilim",
                     "electric potential|voltage"),
    "kapasitans": ("kondansator kapasitesi|ne kadar yuk depolar|sigac",
                   "capacitance|how much charge stored"),
    "paralel_plaka": ("plakali kondansator|levhalar arasi|"
                      "plaka araligi kapasite", "parallel plate capacitor"),
    "kond_enerji": ("kondansatorde depolanan enerji|flas enerjisi",
                    "energy stored in a capacitor|camera flash"),
    "rc_zaman": ("kondansator dolma suresi|sarj olma suresi|"
                 "bosalma ne kadar surer|kondansator ne kadar surede dolar|"
                 "zaman sabiti rc",
                 "how long to charge a capacitor|RC time constant"),
    "rl_zaman": ("bobinde akim ne zaman kararli|akim yukselme suresi|"
                 "bobin zaman sabiti|akim kararli hale gelir",
                 "inductor current rise time|RL time constant"),
    "faraday": ("miknatis bobinde akim|miknatis akim uretir|bobinde akim uretir|"
                "miknatis hareket edince akim|dinamo|jeneratör nasil calisir|"
                "indukleme|manyetik degisim akim uretir|bisiklet dinamosu",
                "moving magnet induces current|generator|induction"),
    "ozindukleme": ("bobinin oz indukleme katsayisi|indüktans",
                    "self inductance of a coil"),
    "solenoid": ("bobinin ic manyetik alani|solenoid alani",
                 "magnetic field inside a coil"),
    "bobin_enerji": ("bobinde depolanan enerji", "energy stored in inductor"),
    "tel_B": ("telin cevresindeki manyetik alan|akim manyetik alan",
              "magnetic field around a wire"),
    "tel_kuvvet": ("akim tasiyan tele kuvvet|motor neden doner|"
                   "manyetik alanda tel", "force on a current carrying wire"),
    "lorentz": ("manyetik alanda hareket eden yuk|yuke etkiyen manyetik kuvvet",
                "force on a moving charge|Lorentz force"),
    "cyclotron": ("parcacik hizlandirici frekansi|siklotron",
                  "cyclotron frequency"),
    "hall": ("hall gerilimi|manyetik alan olcumu", "Hall voltage"),
    "transformator": ("trafo gerilimi dusurur|sarim orani|"
                      "220 volttan 12 volta|gerilim yukseltme",
                      "transformer turns ratio|step down voltage"),
    "rlc": ("rezonans frekansi|radyo istasyonu ayarlama|devre rezonansi",
            "resonant frequency|tuning a radio"),
    "empedans_rlc": ("devrenin empedansi|alternatif akimda direnc",
                     "circuit impedance"),
    "reaktans_C": ("kondansatorun reaktansi|kapasitif direnc",
                   "capacitive reactance"),
    "reaktans_L": ("bobinin reaktansi|indüktif direnc", "inductive reactance"),
    "guc_faktoru": ("guc faktoru|cos fi|reaktif guc", "power factor"),
    "kalite_faktoru": ("kalite faktoru|devrenin keskinligi", "Q factor"),
    "kesim_frekansi": ("filtre kesim frekansi|hangi frekansi keser",
                       "cutoff frequency|filter"),
    "gerilim_bolucu": ("gerilim bolucu|voltaj bolme|direnclerle gerilim dusurme",
                       "voltage divider"),
    "gauss_yasasi": ("gauss yasasi|kapali yuzeyden akı", "Gauss law"),
    "elektrik_akisi": ("elektrik akisi|yuzeyden gecen alan", "electric flux"),
    "dipol_moment": ("dipol momenti", "dipole moment"),
    "dipol_tork": ("dipole etkiyen tork|alanda donme egilimi",
                   "torque on a dipole"),
    "poynting": ("isigin tasidigi guc|elektromanyetik enerji akisi",
                 "Poynting vector|energy flow of light"),

    # ── Termodinamik ──────────────────────────────────────────────────────
    "isi": ("suyu isitmak icin enerji|kac joule gerekir|"
            "sicakligi yukseltmek|kaynatmak icin enerji|"
            "isitirken harcanan enerji",
            "energy to heat water|how much heat is needed"),
    "gizli_isi": ("buzu eritmek|suyu buharlastirmak|hal degisimi enerjisi|"
                  "erime isisi|buharlasma isisi",
                  "melting ice|boiling water|latent heat"),
    "molar_isi": ("molar isi kapasitesi|mol basina isi",
                  "molar heat capacity"),
    "ideal_gaz": ("balon neden siser|gaz basinci hacim sicaklik|"
                  "lastik havasi isinca|pv nrt",
                  "why does a balloon expand|gas law"),
    "termo1": ("ic enerji degisimi|birinci yasa|sisteme verilen isi",
               "first law of thermodynamics|internal energy change"),
    "adyabatik": ("hizli sikistirinca isinma|isi alisverisi olmadan|"
                  "pompa neden isinir|aniden sikistirma|"
                  "gaz sikisinca sicaklik", "sudden compression heats gas"),
    "izotermal_is": ("sabit sicaklikta yapilan is|izotermal genlesme",
                     "isothermal work"),
    "carnot": ("en fazla ne kadar verim|ideal motor verimi|"
               "isi makinesi verimi|teorik verim siniri",
               "maximum possible efficiency|Carnot engine"),
    "otto": ("benzinli motor verimi|sikistirma orani verim",
             "gasoline engine efficiency|compression ratio"),
    "sogutma_cop": ("buzdolabi verimi|klima performansi|sogutucu etkinligi|"
                    "sogutucunun etkinlik katsayisi|sogutucu cop|"
                    "buzdolabinin etkinlik katsayisi|sogutucu performansi",
                    "refrigerator efficiency|air conditioner COP"),
    "isi_pompasi": ("isi pompasi verimi|kombi isi pompasi",
                    "heat pump performance"),
    "entropi": ("duzensizlik artisi|entropi degisimi|geri donusumsuz",
                "entropy change|disorder"),
    "boltzmann_S": ("mikro durum sayisi|istatistiksel entropi",
                    "statistical entropy|microstates"),
    "entalpi": ("entalpi|tepkime isisi", "enthalpy|reaction heat"),
    "gibbs": ("tepkime kendiliginden olur mu|gibbs serbest enerjisi",
              "spontaneous reaction|Gibbs free energy"),
    "helmholtz": ("helmholtz serbest enerjisi", "Helmholtz free energy"),
    "stefan": ("sicak cismin yaydigi enerji|isinim gucu|"
               "gunes ne kadar enerji yayar|yayilan isinim",
               "radiated power|how much energy a hot body emits"),
    "wien": ("sicaklik ve renk|akkor neden kirmizi|kirmizi sonra beyaz|"
             "sicak cisim renk degistirir|tepe dalga boyu|"
             "hangi renkte parlar", "color temperature|peak wavelength"),
    "stefan_wien_tepe": ("tepe frekansi|isinimin en yogun frekansi",
                         "peak emission frequency"),
    "isi_iletim": ("duvardan isi kacisi|yalitim ne kadar iyi|"
                   "camdan isi kaybi|isi iletimi",
                   "heat loss through a wall|insulation"),
    "isi_tasinim": ("fanla sogutma|tasinimla isi kaybi",
                    "convective cooling|fan cooling"),
    "termal_genlesme": ("metal isinca uzar|metal isitilinca uzuyor|isitilinca genlesir|"
                        "ray araligi|kopru derzi|"
                        "isinca genlesme|sicakla uzama",
                        "metal expands when heated|thermal expansion"),
    "rms_hiz": ("gaz molekullerinin hizi|molekul ne kadar hizli",
                "speed of gas molecules"),
    "serbest_yol": ("ortalama serbest yol|molekul carpismadan once",
                    "mean free path"),
    "van_der_waals": ("gercek gaz denklemi|ideal olmayan gaz",
                      "real gas equation"),

    # ── Dalga ve ses ──────────────────────────────────────────────────────
    "dalga": ("dalga boyu frekans hiz|dalganin hizi", "wave speed"),
    "doppler": ("ambulans sesi neden degisir|yaklasinca tizlesir|"
                "uzaklasinca kalinlasir|siren sesi",
                "ambulance siren pitch|Doppler shift"),
    "sarkac": ("sarkacin periyodu|salinim suresi|duvar saati sarkaci|"
               "ipin ucundaki agirlik", "pendulum period|swing time"),
    "yay_sarkac": ("yaya asili kutlenin salinimi|kutle yay periyodu",
                   "mass on a spring oscillation"),
    "telde_hiz": ("teldeki dalga hizi|gergin tel", "wave speed on a string"),
    "tel_harmonik": ("gitar teli hangi notayi calar|tel akordu|"
                     "teli germek sesi inceltir|armonikler|perde",
                     "guitar string pitch|harmonics|tuning"),
    "org_acik": ("acik borunun sesi|flut|org borusu",
                 "open pipe frequency|flute"),
    "org_kapali": ("kapali boru sesi|bir ucu kapali",
                   "closed pipe frequency"),
    "vurum": ("iki ses vinlama yapar|akort ederken atma|vurum olayi|"
              "iki hoparlor arasinda dalgalanma", "beat frequency|tuning beats"),
    "ses_siddet": ("ses siddeti|uzaklastikca sesin azalmasi", "sound intensity"),
    "ses_basinc_duzeyi": ("kac desibel|gurultu seviyesi|ses yuksekligi",
                          "decibel level|how loud"),
    "akustik_empedans": ("akustik empedans|ultrason jeli neden",
                         "acoustic impedance"),
    "ses_hizi_gaz": ("sesin havadaki hizi|sicaklikla ses hizi",
                     "speed of sound in air"),
    "mach": ("ses duvari|mach sayisi|sesten hizli", "Mach number|supersonic"),
    "sonum_orani": ("amortisor|titresim sonumleme|sonum orani",
                    "damping ratio|shock absorber"),

    # ── Optik ─────────────────────────────────────────────────────────────
    "snell": ("isik neden bukulur|cam isigi buker|isigi buker|"
              "suda kasik kirik gorunur|camda kirilma|"
              "kirilma indisi|isik ortam degistirince",
              "why light bends|refraction|straw looks broken"),
    "mercek": ("goruntu nerede olusur|mercek denklemi|odak uzakligi goruntu|"
               "buyutec nasil calisir", "where does the image form|lens equation"),
    "mercek_yapimci": ("gozluk numarasi|mercegin odagi neye bagli|"
                       "diyoptri|mercek yapimi",
                       "eyeglass prescription|lens maker|diopter"),
    "buyutme": ("goruntu ne kadar buyuk|buyutme orani",
                "magnification|image size"),
    "cift_yarik": ("girisim deseni|iki yariktan gecen isik|"
                   "perdedeki cizgiler", "double slit interference|fringes"),
    "kirinim": ("tek yarikta kirinim|isik neden yayilir",
                "single slit diffraction"),
    "bragg": ("kristalde x isini|hangi acida yansir|kristal duzlemleri|"
              "x isini kirinimi|kristal yapisi olcumu",
              "x-ray crystal diffraction|Bragg angle"),
    "rayleigh": ("ayirma gucu|en kucuk ayrinti|cozunurluk siniri|"
                 "iki yildizi ayirt etmek|teleskobun keskinligi",
                 "resolving power|smallest detail|telescope resolution"),
    "brewster": ("yansiyan isik polarize|parlama acisi|brewster acisi",
                 "Brewster angle|glare polarization"),
    "malus": ("gunes gozlugu isigi azaltir|polarize filtre|"
              "iki filtre ust uste", "polarized sunglasses|Malus law"),
    "teleskop": ("teleskobun buyutmesi|dürbün buyutmesi",
                 "telescope magnification"),
    "kritik_aci": ("tam yansima|fiber optik nasil calisir|"
                   "isik disari cikamaz", "total internal reflection|fiber optic"),

    # ── Kuantum ───────────────────────────────────────────────────────────
    "foton": ("fotonun enerjisi|isik paketi|frekansa gore enerji",
              "photon energy"),
    "foton_lam": ("dalga boylu foton|dalga boyu foton enerjisi|"
                  "nm dalga boylu isik enerjisi|fotonun enerjisi dalga boyu|"
                  "dalga boyundan enerji|isigin dalga boyu enerjisi",
                  "photon energy from wavelength"),
    "fotoelektrik": ("isikla elektron kopmasi|neden mavi isik kopariyor|"
                     "isik carpinca elektron", "photoelectric effect"),
    "debroglie": ("madde dalgasi|elektronun dalga boyu|parcacik dalga",
                  "matter wave|de Broglie wavelength"),
    "bohr_E": ("atomun enerji duzeyleri|hidrojen atomu enerjisi|"
               "elektron hangi yorungede", "atomic energy levels|hydrogen atom"),
    "rydberg": ("atom hangi renkte isik yayar|spektrum cizgileri|"
                "hidrojen spektrumu|yayilan isigin dalga boyu",
                "spectral lines|what color does an atom emit"),
    "belirsizlik": ("yerini tam bilemeyiz|heisenberg|konum hiz belirsizligi|"
                    "neden kesin olcemeyiz",
                    "uncertainty principle|cannot know exactly"),
    "belirsizlik_enerji": ("enerji zaman belirsizligi|kisa omurlu durum",
                           "energy time uncertainty"),
    "kutu_enerji": ("kutudaki parcacik|kuyu icinde elektron",
                    "particle in a box"),
    "harmonik_kuantum": ("kuantum salinici|titresim enerji duzeyleri",
                         "quantum harmonic oscillator"),
    "compton": ("foton sacilmasi|compton kaymasi", "Compton scattering"),
    "spin_moment": ("elektronun spini|manyetik moment spin", "spin magnetic moment"),
    "zeeman": ("manyetik alanda cizgi yarilmasi|zeeman olayi", "Zeeman effect"),

    # ── Nukleer ───────────────────────────────────────────────────────────
    "yari_omur": ("kac yilda yariya iner|radyoaktif azalma|"
                  "ne zaman zararsiz olur|yari omur suresi|"
                  "karbon tarihleme",
                  "half life|how long until safe|carbon dating"),
    "bozunma_sabiti": ("bozunma sabiti|bozunma hizi", "decay constant"),
    "aktivite": ("radyoaktif aktivite|becquerel|saniyede bozunma",
                 "radioactive activity"),
    "kutle_kusuru": ("kutle kusuru|kaybolan kutle|baglanma enerjisi",
                     "mass defect|binding energy"),
    "nukleon_basina": ("nukleon basina baglanma enerjisi|"
                       "neden demir en kararli",
                       "binding energy per nucleon|why iron is stable"),
    "kutle_enerji_mev": ("nukleer santral enerjiyi nereden alir|"
                         "kutleden enerji|fisyon enerjisi|"
                         "nukleer enerji nasil aciga cikar",
                         "where nuclear energy comes from|fission energy"),
    "cekirdek_yaricap": ("cekirdegin yaricapi", "nuclear radius"),
    "sogurma": ("kurson kalinligi|isinim zayiflamasi|zirhlama",
                "radiation shielding|attenuation"),
    "doz": ("radyasyon dozu|ne kadar zararli|sievert", "radiation dose"),

    # ── Gorelilik ─────────────────────────────────────────────────────────
    "zaman_genlesme": ("zaman neden yavaslar|ikiz paradoksu|"
                       "hizli giden saat geri kalir|zaman genlesmesi|"
                       "isik hizina yaklasinca zaman",
                       "time slows down|twin paradox|time dilation"),
    "boy_kisalma": ("boy kisalmasi|hizli cisim kisalir",
                    "length contraction"),
    "lorentz_gama": ("lorentz carpani|gama faktoru", "Lorentz factor"),
    "rel_enerji": ("gorelilikte enerji|hizli parcacigin enerjisi",
                   "relativistic energy"),
    "enerji_momentum": ("enerji momentum bagintisi",
                        "energy momentum relation"),

    # ── Astro ─────────────────────────────────────────────────────────────
    "hubble": ("galaksiler neden uzaklasiyor|evrenin genislemesi|"
               "hubble yasasi", "galaxies moving away|expanding universe"),
    "kirmizi_kayma": ("uzak galaksiler neden kirmizi|kirmizi kayma|"
                      "isik kirmizilasmasi", "redshift|why galaxies look red"),
    "kadir": ("yildizin parlakligi|kadir farki|hangisi daha parlak",
              "star brightness|magnitude difference"),
    "uzaklik_modulu": ("yildizin uzakligi|yildiza ne kadar uzak|"
                       "uzaklik nasil olculur|parlakliktan uzaklik",
                       "distance to a star|distance modulus"),
    "ters_kare_isik": ("uzaklastikca isik azalir|isik siddeti uzaklik|"
                       "ters kare yasasi", "inverse square law of light"),
    "jeans": ("gaz bulutu cokmesi|yildiz olusumu|jeans kutlesi",
              "cloud collapse|star formation"),

    # ── Akiskan ───────────────────────────────────────────────────────────
    "yogunluk": ("yogunluk nedir|kutle hacim orani|hangi madde daha agir",
                 "density|mass per volume"),
    "basinc": ("basinc nedir|kuvvet alan orani|topuklu ayakkabi",
               "pressure|force per area"),
    "hidrostatik": ("derinlikte basinc|dalgic kulaklarim neden agrir|"
                    "su altinda basinc|derine indikce",
                    "pressure at depth|underwater pressure"),
    "arsimet": ("neden yuzuyor|neden batiyor|suda hafifleme|"
                "kaldirma kuvveti|tahta suda yuzer|gemi neden batmaz",
                "why does it float|buoyant force|Archimedes"),
    "bernoulli": ("hizli akan sivinin basinci|dus perdesi neden yapisir|"
                  "akiskan hizlaninca basinc duser",
                  "faster flow lower pressure|Bernoulli"),
    "sureklilik": ("kesit daralinca hizlanma|hortumu sikinca su hizlanir|"
                   "debi korunumu", "flow rate|narrower pipe faster flow"),
    "torricelli_akis": ("delikten akan su hizi|kaptaki delik",
                        "speed of water from a hole"),
    "poiseuille": ("borudan gecen debi|damar akisi|ince boruda akis|"
                   "boru capina gore akis", "flow through a pipe|blood flow"),
    "stokes": ("kuresel cismin surtunmesi|damla cokelmesi|"
               "sividaki yavaslama", "drag on a sphere|settling velocity"),
    "reynolds": ("akis turbulanli mi|laminer akis|reynolds sayisi",
                 "turbulent or laminar|Reynolds number"),
    "surukleme_kuvveti": ("hava direnci|aracin hava surtunmesi|"
                          "paraşütle inis|limit hiz",
                          "air resistance|drag force|terminal velocity"),
    "kaldirma_kuvveti_kanat": ("ucak nasil ucar|kanat kaldirma kuvveti|"
                               "kanat profili", "how a wing lifts|aerodynamic lift"),
    "yuzey_gerilimi": ("damla neden yuvarlak|kilcal yukselme|"
                       "su yuzeyinde yuruyen bocek",
                       "surface tension|capillary rise|water droplet"),

    # ── Katihal ───────────────────────────────────────────────────────────
    "young": ("malzeme ne kadar esner|gerilme uzama|young modulu|"
              "celik cubuk uzamasi", "Young modulus|how much it stretches"),
    "kayma_modulu": ("kayma modulu|burulma", "shear modulus"),
    "hacim_modulu": ("hacim modulu|sikistirilabilirlik", "bulk modulus"),
    "iletkenlik": ("iletkenlik|metal neden iyi iletir",
                   "electrical conductivity"),
    "hall_katsayisi": ("hall katsayisi|tasiyici turu",
                       "Hall coefficient|carrier type"),
    "surukleme_hizi": ("elektronlarin suruklenme hizi|elektron ne kadar yavas",
                       "electron drift velocity"),
    "yariiletken_tasiyici": ("yariiletken sicaklikla neden degisir|"
                             "silisyum iletkenligi|band araligi sicaklik|"
                             "yariiletkenin direnci",
                             "semiconductor temperature dependence|carrier density"),
    "fermi_enerji": ("fermi enerjisi|elektron denizi", "Fermi energy"),

    # ── Plazma ────────────────────────────────────────────────────────────
    "debye": ("debye perdeleme|plazma perdeleme uzunlugu", "Debye length"),
    "plazma_frekans": ("plazmada elektron titresimi|plazma frekansi|"
                       "iyonosfer radyo yansimasi", "plasma frequency"),
    "larmor": ("manyetik alanda spiral hareket|larmor yaricapi",
               "Larmor radius|gyroradius"),
}


# ── Ogrenilen ifadeler ────────────────────────────────────────────────────
# Kullanici bir soruyu, sozlukte olmayan bir bicimde sorabilir. Dil modeli
# o soruyu dogru formule baglayabilirse, kullanilan ifade buraya yazilir ve
# bir dahaki sefere deterministik arama hicbir modele ihtiyac duymadan
# dogrudan bulur. Sistem boylece her yeni soruyla biraz daha iyi olur.
#
# Guvenlik: ifade en az iki icerik kelimesi icermeli, en fazla 6 kelime
# olmali ve eklendikten sonra yonlendirme olcumunu bozmamali (bozarsa geri
# alinir). Formul basina en fazla OGRENME_SINIRI ifade tutulur.

OGRENME_SINIRI = 12
_DURUM_ANAHTARI = "sozluk_ogrenilen"


def ogrenilenler():
    """Kaydedilmis ifadeleri getir: {formul_id: [ifade, ...]}"""
    from . import db
    veri = db.get_state(_DURUM_ANAHTARI)
    return veri if isinstance(veri, dict) else {}


def _kaydet(veri):
    from . import db
    db.set_state(_DURUM_ANAHTARI, veri)
