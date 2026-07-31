# -*- coding: utf-8 -*-
"""Formullerin fiziksel anlami.

Formul tabani denklemi ve degiskenleri biliyordu ama denklemin NE ANLAMA
geldigini bilmiyordu. Dil modeline yalnizca denklem verilince aradaki bosluğu
kendisi dolduruyor ve hata yapabiliyordu: adyabatik sikistirmayi anlatirken
"sistemin ic enerjisi degismez" dedi — oysa Q=0 oldugu icin ic enerji tam da
yapilan is kadar DEGISIR (dU = -W).

Buradaki notlar elle yazilmis, dogrulanmis fizik ifadeleridir ve baglama
eklenir. Model artik dogru malzemeyle konusur; bosluğu kendi doldurmaz.

Bicim:  "formul_id": ("turkce aciklama", "english explanation")
"""

NOTLAR = {
    # ── Kinematik ─────────────────────────────────────────────────────────
    "kin_v2": ("Zaman icermez: sure bilinmiyorken hiz ve yol arasinda bag "
               "kurar. Fren mesafesinin hizin KARESIYLE artmasinin sebebi "
               "budur — hiz iki katina cikarsa mesafe dort katina cikar.",
               "Time-free relation; braking distance grows with the SQUARE "
               "of speed."),
    "serbest_dusme": ("Havada kalma suresi kutleye bagli degildir; hava "
                      "direnci ihmal edilirse tuy de tas da ayni surede duser.",
                      "Fall time does not depend on mass when drag is "
                      "negligible."),
    "egik_menzil": ("Menzil 45 derecede en buyuktur; 30 ile 60 derece ayni "
                    "menzili verir. Hava direnci varsa en iyi aci 45'in "
                    "altina duser.",
                    "Range peaks at 45 degrees; 30 and 60 give equal range."),
    "merkezcil": ("Ivme hiz yonunu degistirir, buyuklugunu degil. Dairesel "
                  "harekette hiz sabit olsa bile ivme sifir degildir.",
                  "This acceleration changes direction, not speed."),

    # ── Dinamik ───────────────────────────────────────────────────────────
    "newton2": ("Kuvvet hizin degil IVMENIN sebebidir. Sabit hizla giden bir "
                "cisme etkiyen net kuvvet sifirdir.",
                "Force causes acceleration, not velocity; constant velocity "
                "means zero net force."),
    "surtunme": ("Surtunme kuvveti temas alanina degil, normal kuvvete "
                 "baglidir. Genis lastik daha cok tutmaz — bu yaygin bir "
                 "yanlis anlamadir.",
                 "Friction depends on normal force, not contact area."),
    "impuls": ("Ayni hiz degisimi uzun surede olusursa kuvvet kucuk olur. "
               "Hava yastigi, emniyet kemeri ve tatami bu ilkeyle calisir.",
               "Same momentum change over longer time means smaller force."),
    "esnek_olmayan": ("Momentum korunur ama kinetik enerji korunmaz; kaybolan "
                      "enerji sekil degistirme, isi ve sese gider.",
                      "Momentum is conserved, kinetic energy is not."),
    "aci_momentum": ("Dis tork yoksa acisal momentum korunur. Patinajcinin "
                     "kollarini toplayinca hizlanmasinin sebebi budur: "
                     "eylemsizlik momenti kucululunce acisal hiz buyur.",
                     "Angular momentum is conserved without external torque."),
    "tork": ("Ayni kuvvet, kol uzunlugu arttikca daha buyuk donme etkisi "
             "yapar. Uzun anahtarla somun sokmek bu yuzden kolaydir.",
             "The same force gives more turning effect with a longer arm."),
    "kacis_hiz": ("Kutleden bagimsizdir: tas da roket de ayni hizi ister. "
                  "Yonu de onemli degildir, yalnizca buyuklugu.",
                  "Independent of the escaping object's mass."),
    "kutle_cekim": ("Uzaklikla ters KARE olarak azalir: mesafe iki katina "
                    "cikarsa kuvvet dortte bire duser.",
                    "Inverse-square: doubling distance quarters the force."),

    # ── Enerji ────────────────────────────────────────────────────────────
    "kinetik": ("Hiz iki katina cikarsa enerji DORT katina cikar. Trafikte "
                "hizin kucuk bir artisinin carpisma siddetini cok "
                "buyutmesinin sebebi budur.",
                "Doubling speed quadruples kinetic energy."),
    "verim": ("Verim hicbir gercek makinede %100 olamaz; isi makinelerinde "
              "ustten Carnot verimiyle sinirlidir.",
              "Efficiency is never 100%; heat engines are capped by Carnot."),
    "donme_enerji": ("Donen bir cismin enerjisi kutlenin eksene gore NASIL "
                     "dagildigina baglidir; ayni kutleli iki cisim farkli "
                     "enerji tasiyabilir.",
                     "Depends on how mass is distributed about the axis."),
    "yuvarlanma_enerji": ("Yuvarlanan cisim enerjisini oteleme ve donme "
                          "arasinda paylastirir. Egik duzlemde once inen, "
                          "kutlesi eksene daha yakin olandir (once kure, "
                          "sonra disk, en son halka).",
                          "Rolling splits energy between translation and "
                          "rotation; compact bodies win the race."),

    # ── Elektrik ──────────────────────────────────────────────────────────
    "ohm": ("Yalnizca omik iletkenler icin gecerlidir; diyot ve lamba "
            "flamani gibi elemanlarda direnc sabit degildir.",
            "Holds only for ohmic conductors."),
    "direnc_tel": ("Direnc uzunlukla artar, kesitle azalir. Ince kablonun "
                   "isinmasinin sebebi budur.",
                   "Resistance grows with length, falls with cross-section."),
    "rc_zaman": ("Bir zaman sabitinde kondansator son degerinin %63'une "
                 "ulasir; pratikte 5 tau sonunda (%99) dolmus sayilir.",
                 "One time constant reaches 63%; ~5 tau is considered full."),
    "rl_zaman": ("Bobin akimin ANI degisimine karsi koyar; akim tam da bu "
                 "yuzden basamak seklinde degil ustel olarak yukselir.",
                 "An inductor opposes sudden current change."),
    "faraday": ("Akimi ureten manyetik alanin kendisi degil, DEGISIMIDIR. "
                "Sabit bir miknatis yaninda duran bobinde akim olusmaz.",
                "It is the CHANGE of flux that drives current, not flux."),
    "transformator": ("Yalnizca alternatif akimda calisir; gerilim dusen "
                      "tarafta akim ayni oranda yukselir, guc korunur.",
                      "Works only with AC; stepping voltage down steps "
                      "current up."),
    "coulomb": ("Kutle cekimiyle ayni bicimdedir ama hem itici hem cekici "
                "olabilir ve mertebece cok daha gucludur.",
                "Same form as gravity but can repel and is far stronger."),
    "lorentz": ("Kuvvet hiza dik oldugu icin manyetik alan yuke IS YAPMAZ; "
                "yalnizca yolunu bukup enerjisini degistirmeden dondurur.",
                "Magnetic force does no work; it only bends the path."),

    # ── Termodinamik ──────────────────────────────────────────────────────
    "termo1": ("Enerjinin korunumudur: sisteme verilen isi ya ic enerjiyi "
               "artirir ya da is yapar. Ikisi ayni anda da olabilir.",
               "Energy conservation: heat added raises internal energy or "
               "does work."),
    "adyabatik": ("Adyabatik surecte isi alisverisi YOKTUR (Q = 0), ama bu "
                  "ic enerjinin sabit kaldigi anlamina GELMEZ. Birinci yasa "
                  "dU = Q - W oldugundan, Q = 0 iken dU = -W'dir: gaz "
                  "sikistirilirken uzerine is yapilir, ic enerjisi artar ve "
                  "sicakligi YUKSELIR. Bisiklet pompasinin isinmasinin ve "
                  "dizel motorda yakitin kendiliginden tutusmasinin sebebi "
                  "budur. Genlesirken tersi olur: gaz is yapar, soguyur.",
                  "In an adiabatic process Q = 0, but internal energy is NOT "
                  "constant: dU = -W. Compression does work on the gas, so "
                  "its internal energy and temperature RISE (bicycle pump, "
                  "diesel ignition). Expansion cools it."),
    "izotermal_is": ("Sicaklik sabit oldugundan ideal gazda ic enerji "
                     "degismez; sisteme verilen tum isi ise donusur.",
                     "At constant temperature all added heat becomes work."),
    "carnot": ("Ulasilabilecek en yuksek verimdir; gercek motorlar her zaman "
               "bunun altinda kalir. Yalnizca sicaklik FARKINA baglidir, "
               "calisma maddesine degil.",
               "The upper bound on efficiency; depends only on temperatures."),
    "entropi": ("Yalitilmis bir sistemde entropi azalmaz. Bu, zamanin yonunu "
                "belirleyen tek temel yasadir.",
                "Entropy never decreases in an isolated system."),
    "isi": ("Isi ile sicaklik ayni sey degildir: isi aktarilan enerjidir, "
            "sicaklik ise moleküllerin ortalama kinetik enerjisinin olcusudur.",
            "Heat is transferred energy; temperature measures average "
            "molecular kinetic energy."),
    "gizli_isi": ("Hal degisimi sirasinda sicaklik SABIT kalir; verilen tum "
                  "enerji baglari kirmaya gider. Kaynayan suyun 100 C'de "
                  "kalmasinin sebebi budur.",
                  "Temperature stays constant during a phase change."),
    "ideal_gaz": ("Dusuk basinc ve yuksek sicaklikta iyi calisir; molekul "
                  "hacmi ve molekuller arasi cekim ihmal edilir.",
                  "Valid at low pressure and high temperature."),
    "stefan": ("Yayilan guc sicakligin DORDUNCU kuvvetiyle artar: sicaklik "
               "iki katina cikarsa isinim on alti katina cikar.",
               "Radiated power scales with the FOURTH power of temperature."),
    "wien": ("Cisim isindikca yaydigi isigin tepe dalga boyu kisalir: once "
             "kizil, sonra turuncu, en sonunda beyaz gorunur.",
             "Hotter bodies peak at shorter wavelengths."),
    "termal_genlesme": ("Kopru derzleri, ray bosluklari ve boru kompansatorleri "
                        "bu genlesmeye yer acmak icindir.",
                        "Expansion joints exist to accommodate this."),

    # ── Dalga ─────────────────────────────────────────────────────────────
    "doppler": ("Kaynak yaklasirken dalga boyu kisalir (ses tizlesir), "
                "uzaklasirken uzar (kalinlasir). Ayni ilke isikta kirmizi "
                "kaymayi verir.",
                "Approaching shortens wavelength; receding lengthens it."),
    "sarkac": ("Kucuk salinimlarda periyot GENLIGE ve KUTLEYE bagli "
               "degildir; yalnizca uzunluga ve yercekimine baglidir.",
               "For small swings the period depends on length and g only."),
    "tel_harmonik": ("Teli germek sesi inceltir, kalinlastirmak veya "
                     "uzatmak kalinlastirir. Gitar akordu bu bagintiyla "
                     "yapilir.",
                     "Tighter or shorter strings sound higher."),
    "vurum": ("Iki yakin frekans ust uste binince siddet yavas yavas "
              "artip azalir. Akort yaparken duyulan 'vin vin' sesi budur; "
              "vurum kaybolunca akort tamamdir.",
              "Two close frequencies produce a slow beating; zero beat "
              "means in tune."),
    "org_kapali": ("Bir ucu kapali boru yalnizca TEK harmonikleri uretir; "
                   "bu yuzden ayni uzunluktaki acik boruya gore bir oktav "
                   "pes calar.",
                   "A closed pipe produces only odd harmonics."),

    # ── Optik ─────────────────────────────────────────────────────────────
    "snell": ("Isik yogun ortama girerken normale yaklasir, seyrek ortama "
              "cikarken uzaklasir. Sudaki kasigin kirik gorunmesi budur.",
              "Light bends toward the normal entering a denser medium."),
    "kritik_aci": ("Kritik acinin uzerinde isik hic disari cikamaz, tamamen "
                   "yansir. Fiber optik kablolar bu ilkeyle calisir.",
                   "Beyond the critical angle light is totally reflected."),
    "rayleigh": ("Ayirma gucu acikligin capiyla artar, dalga boyuyla azalir. "
                 "Buyuk teleskoplarin ustunlugu isik toplamaktan cok "
                 "buradan gelir.",
                 "Resolution improves with aperture, worsens with wavelength."),
    "bragg": ("Yansima her acida degil, yalnizca belirli acilarda guclu "
              "olur; bu acilardan kristal duzlemleri arasindaki mesafe "
              "olculur. DNA'nin cift sarmal yapisi boyle bulundu.",
              "Strong reflection occurs only at specific angles, revealing "
              "crystal plane spacing."),
    "malus": ("Iki polarize filtre dik konuma geldiginde isik tamamen "
              "sonuyor. Gunes gozlugu yatay yansimalari boyle keser.",
              "Crossed polarizers block light completely."),
    "mercek": ("Isaret kurali onemlidir: gercek goruntu mercek arkasinda "
               "olusur ve perdede goruntulenebilir, sanal goruntu "
               "goruntulenemez.",
               "Real images can be projected on a screen; virtual ones "
               "cannot."),

    # ── Kuantum ───────────────────────────────────────────────────────────
    "fotoelektrik": ("Elektronu koparan sey isigin SIDDETI degil "
                     "FREKANSIDIR. Esik frekansin altinda isik ne kadar "
                     "parlak olursa olsun elektron kopmaz — klasik dalga "
                     "kurami bunu aciklayamaz.",
                     "Frequency, not intensity, determines whether electrons "
                     "are ejected."),
    "belirsizlik": ("Bu bir olcum yetersizligi degil, dogaya ait bir "
                    "siniridir; daha iyi bir aletle asilamaz.",
                    "A fundamental limit of nature, not a measurement flaw."),
    "debroglie": ("Her cismin bir dalga boyu vardir ama gunluk cisimlerde "
                  "bu deger olculemeyecek kadar kucuktur.",
                  "Everything has a wavelength; for everyday objects it is "
                  "immeasurably small."),
    "bohr_E": ("Enerji duzeyleri kesiklidir; elektron ancak izinli duzeyler "
               "arasinda atlar ve farki foton olarak yayar.",
               "Energy levels are discrete; transitions emit photons."),

    # ── Nukleer ───────────────────────────────────────────────────────────
    "yari_omur": ("Yari omur maddenin miktarina bagli degildir ve "
                  "degistirilemez: sicaklik, basinc veya kimyasal islem "
                  "bozunma hizini etkilemez.",
                  "Half-life is fixed and unaffected by temperature or "
                  "chemistry."),
    "nukleon_basina": ("Egri demirde (Fe-56) en yuksektir. Demirden hafif "
                       "cekirdekler birlesince (fuzyon), agir cekirdekler "
                       "bolununce (fisyon) enerji aciga cikar.",
                       "Peaks at iron; lighter nuclei fuse and heavier ones "
                       "fission to release energy."),

    # ── Gorelilik ─────────────────────────────────────────────────────────
    "zaman_genlesme": ("Etki karsiliklidir ve gunluk hizlarda olculemeyecek "
                       "kadar kucuktur; ama GPS uydularinin saatleri bu "
                       "duzeltme yapilmazsa gunde ~38 mikrosaniye kayar ve "
                       "konum hatasi kilometrelere ulasir.",
                       "Negligible at everyday speeds, but GPS clocks need "
                       "this correction."),
    "E_mc2": ("Kutle ve enerji ayni seyin iki yuzudur. Cok kucuk bir kutle "
              "cok buyuk enerjiye karsilik gelir; nukleer enerjinin kaynagi "
              "budur.",
              "Mass and energy are two faces of the same thing."),

    # ── Akiskan ───────────────────────────────────────────────────────────
    "arsimet": ("Kaldirma kuvveti, cismin TASIRDIGI sivinin agirligina "
                "esittir. Cismin yogunlugu sividan kucukse yuzer, buyukse "
                "batar. Geminin batmamasi, govdesinin icindeki hava "
                "sayesinde ortalama yogunlugunun sudan kucuk olmasindandir.",
                "Buoyant force equals the weight of displaced fluid."),
    "bernoulli": ("Akiskan hizlandiginda basinci DUSER. Sadece surtunmesiz "
                  "ve sikistirilamaz akista, tek bir akim cizgisi boyunca "
                  "gecerlidir.",
                  "Faster flow means lower pressure, along a streamline."),
    "sureklilik": ("Kesit daralinca akiskan hizlanir; hortumun ucunu "
                   "sikinca suyun daha uzaga firlamasinin sebebi budur.",
                   "Narrower cross-section means faster flow."),
    "poiseuille": ("Debi yaricapin DORDUNCU kuvvetiyle artar: damar capinin "
                   "yarilanmasi akisi on altida bire dusurur. Damar "
                   "tikanikliklarinin neden bu kadar tehlikeli oldugunu "
                   "aciklar.",
                   "Flow scales with the FOURTH power of radius."),
    "surukleme_kuvveti": ("Hava direnci hizin karesiyle artar; bu yuzden "
                          "dusen cisim bir sure sonra sabit bir limit hiza "
                          "ulasir ve daha fazla hizlanmaz.",
                          "Drag grows with speed squared, producing a "
                          "terminal velocity."),

    # ── Astro ─────────────────────────────────────────────────────────────
    "hubble": ("Galaksiler uzayin icinde hareket etmiyor; uzayin kendisi "
               "genisliyor. Bu yuzden uzak galaksiler daha hizli uzaklasir.",
               "Space itself expands; farther galaxies recede faster."),
    "ters_kare_isik": ("Uzaklik iki katina cikinca gorulen parlaklik dortte "
                       "bire duser; yildiz uzakliklari boyle olculur.",
                       "Brightness falls as the inverse square of distance."),
}


# ── Ikinci parti: kalan cekirdek formuller ─────────────────────────────────
# Olcum: 190 cekirdek formulun 129'unda fiziksel anlam notu yoktu. Not yoksa
# ders anlatimi "denklem + degiskenler" duzeyinde kaliyor; ogretmen ise
# denklemin NE ANLAMA geldigini soyler.

NOTLAR.update({
    # Kinematik
    "v_ort": ("Ortalama hiz, yolun suresine bolumudur — ANLIK hizla ayni sey "
              "degildir. 100 km'yi 2 saatte giden araba hic 50 km/h'de "
              "gitmemis olabilir.",
              "Average speed is not instantaneous speed."),
    "kin_v": ("Sabit ivmede hiz zamanla DOGRUSAL artar. Grafigi bir dogrudur; "
              "egimi ivmedir.", "Velocity grows linearly under constant "
              "acceleration."),
    "kin_x": ("Yol, zamanin KARESIYLE artar. Bu yuzden ikinci saniyede "
              "alinan yol birinci saniyedekinin uc katidir.",
              "Displacement grows with the square of time."),
    "ivme": ("Ivme hizin degisim hizidir. Yavaslama da bir ivmedir (isareti "
             "hiz yonunun tersidir); 'ivme yok' demek 'hiz sabit' demektir.",
             "Deceleration is also acceleration."),
    "egik_h": ("Tepe noktasinda DUSEY hiz sifirdir ama yatay hiz ve ivme "
               "sifir degildir. Cisim orada durmuyor, yalnizca yukselmeyi "
               "birakiyor.", "At the peak only the vertical velocity is zero."),
    "acisal": ("Acisal hiz butun cisim icin aynidir; cizgisel hiz ise eksene "
               "uzakligina baglidir. Donen bir diskin kenari merkezden daha "
               "hizli hareket eder.",
               "Angular velocity is shared; linear velocity is not."),
    "periyot_frekans": ("Periyot ile frekans birbirinin tersidir: biri "
                        "buyurken digeri kucululur.",
                        "Period and frequency are reciprocals."),

    # Dinamik
    "agirlik": ("Kutle degismez, agirlik degisir. Ayda kutleniz ayni kalir "
                "ama agirliginiz altida bire duser.",
                "Mass is invariant; weight depends on local gravity."),
    "momentum": ("Momentum bir VEKTORDUR; yonu hizla aynidir. Carpismalarda "
                 "korunan sey budur, hiz degil.",
                 "Momentum is a vector and is what is conserved in collisions."),
    "hooke": ("Yalnizca ELASTIK bolgede gecerlidir. Yayi fazla gererseniz "
              "kalici sekil degisimi olur ve bagintiya uymaz.",
              "Valid only in the elastic region."),
    "donme_newton": ("Newton'un ikinci yasasinin donme karsiligidir: kuvvet "
                     "yerine tork, kutle yerine eylemsizlik momenti, ivme "
                     "yerine acisal ivme.",
                     "Rotational analogue of Newton's second law."),
    "yorunge_hiz": ("Yorunge hizi yalnizca merkez cismin kutlesine ve "
                    "yaricapa baglidir; uydunun kendi kutlesi hic girmez.",
                    "Orbital speed does not depend on the satellite's mass."),
    "kepler3": ("Yorunge periyodunun karesi, yari buyuk eksenin kupuyle "
                "orantilidir. Uzaktaki gezegen hem daha uzun yol alir hem "
                "daha yavas gider; bu yuzden yili cok daha uzundur.",
                "T squared scales with a cubed."),
    "schwarzschild": ("Bu yaricapin icinden isik bile kacamaz. Dunya bir "
                      "kara delik olsaydi yaricapi yaklasik 9 mm olurdu.",
                      "Not even light escapes from within this radius."),
    "eylemsizlik_cubuk": ("Ayni cubuk, ucundan dondurulurse ortasindan "
                          "dondurulmesine gore dort kat zor doner. Kutle "
                          "eksenden uzaklastikca donmeye direnc artar.",
                          "Inertia depends on how far the mass sits from the "
                          "axis."),
    "eylemsizlik_disk": ("Diskin eylemsizlik momenti halkanınkinin yarisidir: "
                         "kutlesi merkeze daha yakin dagilmistir.",
                         "A disk has half the inertia of a ring."),
    "eylemsizlik_kure": ("Katı kurede kutle en cok merkeze toplandigi icin "
                         "eylemsizlik momenti en kucuk olanlardandir; egik "
                         "duzlemde yarisi kure kazanir.",
                         "A solid sphere has the smallest inertia factor."),
    "paralel_eksen": ("Eksen kutle merkezinden uzaklastikca eylemsizlik "
                      "momenti HER ZAMAN artar; en kucuk deger kutle "
                      "merkezindedir.",
                      "Inertia is minimal about the centre of mass."),
    "kutle_merkezi": ("Bir cisim, kutle merkezinden desteklenirse dengede "
                      "kalir. Dis kuvvetler cismi sanki tum kutlesi bu "
                      "noktadaymis gibi hareket ettirir.",
                      "External forces move a body as if all mass were at "
                      "the centre of mass."),
    "esnek_carpisma_v1": ("Esnek carpismada hem momentum hem kinetik enerji "
                          "korunur. Esit kutleler carpisirsa hizlarini "
                          "takas ederler.",
                          "Equal masses exchange velocities in elastic "
                          "collisions."),
    "egik_duzlem": ("Egim acisi arttikca kaydirici bilesen buyur, normal "
                    "kuvvet kucululur; bu yuzden dik yokusta hem daha cok "
                    "cekilir hem daha az tutunur.",
                    "Steeper slopes increase the driving force and reduce "
                    "the normal force."),
    "merkezcil_kuvvet": ("Merkezcil kuvvet YENI bir kuvvet turu degildir; "
                         "surtunme, gerilme ya da cekim gibi mevcut bir "
                         "kuvvetin dairesel harekette oynadigi roldur. "
                         "'Merkezkac kuvvet' ise gercek bir kuvvet degil, "
                         "donen cerceveden bakmanin sonucudur.",
                         "Centripetal force is a role, not a new force."),
    "gelgit": ("Gelgiti yaratan cekim kuvvetinin kendisi degil, cismin iki "
               "yakasi arasindaki cekim FARKIDIR. Bu yuzden gunde iki kabarma "
               "olur.", "Tides come from the gradient of gravity, not gravity."),

    # Enerji
    "is": ("Kuvvet ile yer degistirme dik ise is SIFIRDIR. Bir cantayi elde "
           "tutup yatay yurumek fizik anlaminda is yapmak degildir.",
           "No work is done when force is perpendicular to displacement."),
    "potansiyel": ("Potansiyel enerji her zaman bir REFERANSA goredir; "
                   "sifiri nerede sectiginiz size kalmistir, onemli olan "
                   "FARKIDIR.", "Potential energy is defined up to a "
                   "reference level."),
    "yay_enerji": ("Yayda depolanan enerji uzamanin KARESIYLE artar: iki kat "
                   "germek dort kat enerji demektir.",
                   "Spring energy grows with the square of extension."),
    "guc": ("Guc, isin ne kadar HIZLI yapildigidir. Ayni isi yapan iki "
            "makineden hizli olani daha gucludur; toplam is aynidir.",
            "Power is the rate of doing work."),
    "guc_hiz": ("Sabit hizda giden aracin motor gucu, direnc kuvvetiyle hizin "
                "carpimidir. Hiz iki katina cikinca hava direnci dort kat, "
                "gereken guc SEKIZ kat artar.",
                "Required power grows with the cube of speed against drag."),

    # Elektrik
    "E_alan": ("Elektrik alan, birim yuke etkiyen kuvvettir; yuk olmasa da "
               "alan vardir. Alan cizgileri artidan eksiye dogrudur.",
               "The field exists whether or not a test charge is present."),
    "E_kuvvet": ("Pozitif yuke etkiyen kuvvet alanla ayni yonde, negatife "
                 "etkiyen ters yondedir.",
                 "Force is along the field for positive charges."),
    "potansiyel_V": ("Potansiyel bir NOKTA buyuklugudur, potansiyel farki ise "
                     "iki nokta arasindadir. Kuslarin tek telde durabilmesi "
                     "aralarinda fark olmamasindandir.",
                     "Voltage is a difference between two points."),
    "elektrik_guc": ("Elektrik faturasi gucu degil, guc x sure yani ENERJIYI "
                     "olcer (kWh). 2000 W'lik isitici bir saatte 2 kWh harcar.",
                     "Bills measure energy (kWh), not power."),
    "joule_isi": ("Isinma akimin KARESIYLE artar: akim iki katina cikarsa "
                  "kayip dort katina cikar. Yuksek gerilimle iletim bu "
                  "yuzden tercih edilir.",
                  "Resistive heating grows with the square of current."),
    "kapasitans": ("Kapasitans, kondansatorun geometrisine baglidir; uzerine "
                   "yuk koymadan da vardir. Yuk arttikca gerilim artar, "
                   "kapasitans sabit kalir.",
                   "Capacitance is set by geometry, not by stored charge."),
    "paralel_plaka": ("Plakalari yaklastirmak kapasitansi artirir; arada "
                      "yalitkan (dielektrik) varsa daha da artar.",
                      "Closer plates and dielectrics raise capacitance."),
    "kond_enerji": ("Kondansator enerjiyi ELEKTRIK ALANINDA depolar ve cok "
                    "hizli birakabilir; fotograf flasi ve defibrilator bu "
                    "yuzden kondansator kullanir.",
                    "Capacitors store field energy and release it fast."),
    "tel_B": ("Telin cevresindeki alan dairesel, siddeti uzaklikla TERS "
              "orantilidir (1/r) — noktasal yukun 1/r^2'sinden farkli.",
              "Field around a wire falls as 1/r, not 1/r squared."),
    "solenoid": ("Uzun bobinin icinde alan neredeyse duzgundur ve yaricapa "
                 "bagli degildir; sarim SIKLIGINA baglidir.",
                 "Field inside a long solenoid depends on turns per length."),
    "tel_kuvvet": ("Kuvvet hem akima hem alana diktir. Elektrik motorunun "
                   "donmesini saglayan budur.",
                   "The force is perpendicular to both current and field."),
    "ozindukleme": ("Bobin akimin DEGISIMINE karsi koyar; devre acilirken "
                    "kivilcim cikmasinin sebebi budur.",
                    "An inductor opposes change in current."),
    "bobin_enerji": ("Bobin enerjiyi MANYETIK alanda depolar; kondansator ise "
                     "elektrik alaninda. Ikisi devrede birbirini tamamlar.",
                     "Inductors store magnetic energy."),
    "hall": ("Hall gerilimi tasiyicilarin ISARETINI verir: yari iletkende "
             "deligin mi elektronun mu tasidigini boyle anlariz.",
             "The Hall voltage reveals the sign of the charge carriers."),
    "cyclotron": ("Dairesel frekans HIZDAN ve yaricaptan bagimsizdir; "
                  "parcacik hizlandikca yaricap buyur ama tur suresi "
                  "degismez. Siklotron bu yuzden calisir.",
                  "Cyclotron frequency is independent of speed."),
    "gauss_yasasi": ("Kapali yuzeyden gecen toplam aki, yalnizca ICERIDEKI "
                     "yuke baglidir; disaridaki yukler katkı vermez.",
                     "Only enclosed charge contributes to the total flux."),
    "elektrik_akisi": ("Aki, alanin yuzeyi ne kadar 'deldigi'dir; alan yuzeye "
                       "paralelse aki sifirdir.",
                       "Flux vanishes when the field is parallel to the "
                       "surface."),
    "dipol_moment": ("Dipol momenti buyudukce alanda hizalanma egilimi artar.",
                     "A larger dipole moment aligns more strongly."),
    "dipol_tork": ("Tork, dipol alana DIK iken en buyuk, hizalandiginda "
                   "sifirdir. Pusula ignesinin donmesi budur.",
                   "Torque is maximal when the dipole is perpendicular."),
    "rlc": ("Rezonansta bobinle kondansatorun etkileri birbirini goturur, "
            "devre saf direnc gibi davranir ve akim en buyuk olur. Radyo "
            "istasyonu secmek budur.",
            "At resonance the reactances cancel."),
    "empedans_rlc": ("Empedans alternatif akimda direncin karsiligidir ama "
                     "frekansa baglidir; dogru akimda tanimli degildir.",
                     "Impedance is frequency dependent."),
    "reaktans_L": ("Bobin yuksek frekansi zorlastirir: frekans arttikca "
                   "reaktansi buyur. Bu yuzden bobin 'yuksek frekans "
                   "engelleyici'dir.",
                   "Inductive reactance grows with frequency."),
    "reaktans_C": ("Kondansator yuksek frekansi kolaylastirir: frekans "
                   "arttikca reaktansi kuculur. Dogru akimi ise hic "
                   "gecirmez.",
                   "Capacitive reactance falls with frequency."),
    "guc_faktoru": ("Guc faktoru dusukse ayni isi yapmak icin daha cok akim "
                    "cekilir ve kablolar bosuna isinir; sanayide bu yuzden "
                    "duzeltilir.",
                    "A poor power factor wastes current."),
    "poynting": ("Enerji teller boyunca degil, tellerin CEVRESINDEKI alanda "
                 "tasinir. Isik da bu vektorle enerji tasir.",
                 "Energy flows in the field, not inside the wires."),

    # Termodinamik
    "boltzmann_S": ("Entropi, sistemin kac farkli mikro duzenlemeyle ayni "
                    "gorunumu verebilecegini sayar. Duzensizlik bu yuzden "
                    "olasilikla ilgilidir.",
                    "Entropy counts the microstates behind one macrostate."),
    "isi_iletim": ("Isi kaybi kalinlikla TERS orantilidir: yalitimi iki "
                   "katina cikarmak kaybi yariya indirir.",
                   "Heat loss is inversely proportional to thickness."),
    "isi_tasinim": ("Tasinimda isi akiskanin hareketiyle tasinir; ruzgar "
                    "ayni sicaklikta havayi daha sogutucu yapan budur.",
                    "Convection moves heat with the fluid itself."),
    "rms_hiz": ("Gaz molekullerinin hizi sicakligin KAREKOKUYLE artar ve "
                "kutlenin karekokuyle azalir; hafif gazlar bu yuzden daha "
                "hizli kacar.",
                "Molecular speed scales with the square root of temperature."),
    "serbest_yol": ("Basinc dustukce molekuller carpismadan daha uzun yol "
                    "alir; vakum teknolojisi bu buyuklukle calisir.",
                    "Mean free path grows as pressure falls."),
    "molar_isi": ("Molar isi kapasitesi maddenin kac serbestlik derecesi "
                  "oldugunu ele verir; tek atomlu gazlar icin 3R/2'dir.",
                  "Molar heat capacity reveals degrees of freedom."),
    "van_der_waals": ("Ideal gaz yasasina iki duzeltme ekler: molekullerin "
                      "kendi hacmi ve aralarindaki cekim. Yogusmayi bu "
                      "yuzden aciklayabilir.",
                      "Adds molecular volume and attraction to the ideal "
                      "gas law."),
    "entalpi": ("Sabit basincta alinan/verilen isi entalpi degisimine "
                "esittir; kimyada tepkime isilari bu yuzden entalpiyle "
                "verilir.",
                "At constant pressure, heat equals enthalpy change."),
    "gibbs": ("Tepkimenin kendiliginden olup olmayacagini Gibbs serbest "
              "enerjisinin ISARETI soyler: negatifse olur. Yalnizca enerji "
              "degil entropi de karar verir.",
              "A negative Gibbs energy means a spontaneous process."),
    "helmholtz": ("Sabit hacimde calisan sistemlerde kendiliginden olma "
                  "olcutudur; Gibbs'in sabit basinctaki karsiligidir.",
                  "The constant-volume counterpart of Gibbs energy."),
    "isi_pompasi": ("Isi pompasi enerji URETMEZ, tasir. Etkinligi 1'den "
                    "buyuk gorunur cunku disaridan bedava isi ceker.",
                    "A heat pump moves heat rather than creating it."),
    "sogutma_cop": ("Buzdolabi icerisini sogutur ama odayi ISITIR: cektigi "
                    "isi ile harcadigi elektrigi birlikte disari verir.",
                    "A refrigerator warms the room it cools into."),
    "otto": ("Verim yalnizca SIKISTIRMA ORANINA baglidir; benzinli motorlarda "
             "bu oran vurunti sinirina takilir, dizelde daha yuksek olabilir.",
             "Otto efficiency depends only on the compression ratio."),
    "stefan_wien_tepe": ("Cisim isindikca yaydigi isinimin tepe frekansi "
                         "yukselir; kizil kordan beyaz sicak demire gecis "
                         "budur.",
                         "Peak frequency rises with temperature."),

    # Dalga ve ses
    "dalga": ("Dalga hizi ORTAMIN ozelligidir; frekansi kaynak belirler. "
              "Ortam degisince frekans ayni kalir, dalga boyu degisir.",
              "Wave speed belongs to the medium, frequency to the source."),
    "telde_hiz": ("Teli germek dalga hizini artirir, kalinlastirmak azaltir. "
                  "Bas telleri bu yuzden kalindir.",
                  "Tension raises and mass density lowers wave speed."),
    "yay_sarkac": ("Periyot genlikten bagimsizdir ve yercekimine hic bagli "
                   "degildir; yay-kutle sistemi uzayda da ayni periyotla "
                   "salinir.",
                   "The period is independent of amplitude and gravity."),
    "ses_siddet": ("Ses siddeti uzaklikla ters KARE olarak azalir; iki kat "
                   "uzaklasinca dortte bire duser.",
                   "Sound intensity falls as the inverse square of distance."),
    "ses_basinc_duzeyi": ("Desibel LOGARITMIKTIR: 10 dB artis siddetin on "
                          "katina cikmasi demektir, kulak icinse yaklasik "
                          "iki kat gurultu.",
                          "Decibels are logarithmic."),
    "akustik_empedans": ("Iki ortamin empedansi cok farkliysa ses buyuk "
                         "olcude yansir; ultrason jeli tam da bu yansimayi "
                         "onlemek icindir.",
                         "Impedance mismatch causes reflection."),
    "ses_hizi_gaz": ("Sesin hizi sicaklikla artar ama BASINCA bagli "
                     "degildir; yuksek daglarda ses yavas degildir, sogugu "
                     "yuzunden yavastir.",
                     "Sound speed depends on temperature, not pressure."),
    "mach": ("Mach 1 asildiginda basinc dalgalari one gecemez ve sok dalgasi "
             "olusur; 'ses duvari' budur.",
             "Beyond Mach 1 pressure waves cannot outrun the source."),
    "sonum_orani": ("Sonum orani sistemin nasil duracagini belirler: "
                    "ζ < 1 salinarak (az sonum), ζ = 1 en hizli ve "
                    "salinimsiz (kritik sonum), ζ > 1 yavas ve salinimsiz "
                    "(asiri sonum). Arac amortisorleri kritik sonuma yakin "
                    "secilir: hizli oturur ama zipplamaz.",
                    "Zeta below 1 oscillates, 1 is critical, above 1 is "
                    "overdamped."),

    # Optik
    "buyutme": ("Buyutme negatifse goruntu TERSTIR. Mutlak degeri 1'den "
                "kucukse goruntu kucultulmustur.",
                "Negative magnification means an inverted image."),
    "cift_yarik": ("Girisim, isigin DALGA oldugunun dogrudan kanitidir; "
                   "parcacik modeli bu deseni aciklayamaz.",
                   "Interference is direct evidence of wave behaviour."),
    "kirinim": ("Yarik daraldikca desen GENISLER. Bu yuzden cok kucuk "
                "ayrintilari gormek icin kisa dalga boyu gerekir.",
                "Narrower slits spread the pattern wider."),
    "mercek_yapimci": ("Merceğin odagi hem yuzey egriliklerine hem malzemenin "
                       "kirilma indisine baglidir; ayni sekil farkli camda "
                       "farkli odak verir.",
                       "Focal length depends on curvature and index."),
    "teleskop": ("Teleskopun buyutmesi iki odak uzunlugunun oranidir; ama "
                 "asil onemli olan buyutme degil, isik toplama ve ayirma "
                 "gucudur.",
                 "Aperture matters more than magnification."),
    "brewster": ("Brewster acisinda yansiyan isik TAM polarizedir; polarize "
                 "gunes gozlugu su ve yol parlamasini bu yuzden keser.",
                 "At Brewster's angle reflected light is fully polarised."),
    "org_acik": ("Iki ucu acik boru TUM harmonikleri uretir; bir ucu kapali "
                 "boru yalnizca tek harmonikleri uretir ve bir oktav pes "
                 "calar.", "An open pipe produces all harmonics."),

    # Kuantum ve nukleer
    "foton": ("Fotonun enerjisi yalnizca FREKANSINA baglidir; isigin parlak "
              "olmasi foton SAYISINI artirir, enerjisini degil.",
              "Photon energy depends on frequency alone."),
    "foton_lam": ("Kisa dalga boyu = yuksek enerji. Morotesi bu yuzden "
                  "zararli, kizilotesi degil.",
                  "Shorter wavelength means higher energy."),
    "kutu_enerji": ("Kutuya hapsedilen parcacigin enerjisi KESIKLIDIR ve en "
                    "dusuk enerji sifir degildir; hapsedilmis parcacik hic "
                    "durgun olamaz.",
                    "Confinement quantises energy and forbids zero energy."),
    "harmonik_kuantum": ("Kuantum saliniciada en dusuk enerji sifir degil "
                         "hbar*w/2'dir; mutlak sifirda bile titresim surer.",
                         "Zero-point energy persists at absolute zero."),
    "rydberg": ("Her element kendine ozgu cizgiler yayar; yildizlarin "
                "bilesimini bu cizgilerden okuruz.",
                "Spectral lines are an elemental fingerprint."),
    "compton": ("Sacilan fotonun dalga boyu UZAR — foton enerji kaybeder. "
                "Bu, isigin parcacik gibi carpistiginin kanitidir.",
                "Compton scattering shows light behaves as a particle."),
    "belirsizlik_enerji": ("Kisa omurlu durumlarin enerjisi kesin degildir; "
                           "parcacik rezonanslarinin 'genisligi' buradan "
                           "gelir.", "Short-lived states have fuzzy energy."),
    "fermi_enerji": ("Mutlak sifirda bile elektronlarin enerjisi sifir "
                     "degildir: Pauli ilkesi hepsini en dusuk duzeye "
                     "koymamiza izin vermez.",
                     "Pauli exclusion keeps electrons energetic even at 0 K."),
    "spin_moment": ("Spin klasik bir donme DEGILDIR; parcaciğin ic "
                    "ozelligidir ve manyetik momente yol acar.",
                    "Spin is intrinsic, not literal rotation."),
    "zeeman": ("Manyetik alan enerji duzeylerini yarar; yildiz "
               "yuzeylerindeki manyetik alanlari bu yarilmadan olceriz.",
               "Magnetic fields split spectral lines."),
    "bozunma_sabiti": ("Bozunma sabiti buyudukce yari omur kisalir; ikisi "
                       "ters orantilidir.",
                       "A larger decay constant means a shorter half-life."),
    "aktivite": ("Aktivite ORNEK BUYUKLUGUNE baglidir: ayni maddenin iki "
                 "kati miktari iki kat aktivite verir, ama yari omru "
                 "degismez.",
                 "Activity scales with sample size; half-life does not."),
    "kutle_kusuru": ("Cekirdegin kutlesi parcalarinin toplamindan KUCUKTUR; "
                     "eksik kutle baglanma enerjisi olarak aciga cikmistir.",
                     "The mass deficit is the binding energy."),
    "kutle_enerji_mev": ("1 atomik kutle birimi 931,5 MeV'e karsilik gelir; "
                         "nukleer hesaplarin cevirme carpani budur.",
                         "One atomic mass unit equals 931.5 MeV."),
    "cekirdek_yaricap": ("Cekirdek yaricapi kutle numarasinin KUP KOKUYLE "
                         "artar; yani nukleon yogunlugu tum cekirdeklerde "
                         "yaklasik aynidir.",
                         "Nuclear density is nearly constant."),
    "sogurma": ("Zirh kalinligi arttikca isinim USTEL olarak azalir; hicbir "
                "kalinlik tam sifir yapmaz, yalnizca yeterince kucultur.",
                "Shielding reduces radiation exponentially, never to zero."),
    "doz": ("Ayni enerji, farkli isinim turlerinde farkli zarar verir; bu "
            "yuzden dozda agirlik carpani kullanilir.",
            "Different radiation types cause different damage."),

    # Gorelilik
    "lorentz_gama": ("Gama carpani 1'den kucuk olamaz; gunluk hizlarda "
                     "1'e cok yakindir, isik hizina yaklasinca hizla buyur.",
                     "Gamma is always at least 1."),
    "boy_kisalma": ("Kisalma yalnizca HAREKET YONUNDEDIR; dik boyutlar "
                    "degismez.", "Contraction occurs only along the motion."),
    "rel_enerji": ("Durgun cismin bile enerjisi vardir: E = mc^2. Toplam "
                   "enerji hiz arttikca gamma ile buyur.",
                   "Even a body at rest has energy."),
    "enerji_momentum": ("Bu baginti kutlesiz parcaciklar icin de gecerlidir: "
                        "foton icin E = pc olur.",
                        "For massless particles this gives E = pc."),

    # Akiskan
    "yogunluk": ("Yogunluk maddenin cinsine ozgudur, miktarina degil: bir "
                 "damla su ile bir kova suyun yogunlugu aynidir.",
                 "Density is intensive: it does not depend on amount."),
    "basinc": ("Ayni kuvvet kucuk alana uygulanirsa basinc buyur; kar "
               "ayakkabisi ile igne arasindaki fark budur.",
               "The same force over a smaller area gives higher pressure."),
    "hidrostatik": ("Basinc yalnizca DERINLIGE baglidir, kabin sekline ya da "
                    "toplam su miktarina degil.",
                    "Pressure depends on depth, not on container shape."),
    "reynolds": ("Reynolds sayisi boyutsuzdur; kucuk modelle yapilan ruzgar "
                 "tuneli deneyleri bu sayede gercek boyuta tasinir.",
                 "Reynolds number lets small models predict full scale."),
    "torricelli_akis": ("Delikten cikan suyun hizi, o yukseklikten serbest "
                        "dusen bir cismin hizina esittir.",
                        "Efflux speed equals free-fall speed from that "
                        "height."),
    "stokes": ("Kucuk ve yavas cisimlerde surtunme hizla DOGRU orantilidir; "
               "buyuk hizlarda ise hizin karesiyle artar.",
               "Stokes drag is linear in speed, valid at low Reynolds "
               "number."),
    "kaldirma_kuvveti_kanat": ("Kaldirma, kanadin havayi ASAGI itmesinin "
                               "tepkisidir; hucum acisi arttikca artar ama "
                               "belli bir aciyi gecince akis ayrilir ve "
                               "kanat 'stall' olur.",
                               "Lift is the reaction to deflecting air "
                               "downward."),
    "yuzey_gerilimi": ("Yuzey gerilimi sivinin yuzey alanini kucultme "
                       "egilimidir; damlanin kure olmasi bu yuzdendir.",
                       "Surface tension minimises surface area."),

    # Katihal ve plazma
    "iletkenlik": ("Metalde sicaklik artinca direnc ARTAR (orgu titresimi "
                   "artar); yariiletkende ise AZALIR (daha cok tasiyici "
                   "serbest kalir).",
                   "Metals and semiconductors respond oppositely to heat."),
    "hall_katsayisi": ("Isareti tasiyicinin turunu verir: negatifse elektron, "
                       "pozitifse delik tasiyor demektir.",
                       "The sign identifies the carrier type."),
    "surukleme_hizi": ("Elektronlar saatte birkac santimetre hizla ilerler; "
                       "ama elektrik alani neredeyse isik hiziyla yayildigi "
                       "icin lamba aninda yanar.",
                       "Drift is slow; the field propagates near light "
                       "speed."),
    "yariiletken_tasiyici": ("Tasiyici sayisi sicaklikla USTEL artar; "
                             "yariiletken cihazlarin sicakliga bu kadar "
                             "duyarli olmasinin sebebi budur.",
                             "Carrier density rises exponentially with "
                             "temperature."),
    "young": ("Young modulu malzemenin SERTLIGIDIR, saglamligi degil: cam "
              "celikten daha az esner ama cok daha kolay kirilir.",
              "Young's modulus measures stiffness, not strength."),
    "kayma_modulu": ("Sivilarin kayma modulu sifirdir; bu yuzden sivilar "
                     "sekil koruyamaz ve enine dalga tasiyamaz.",
                     "Liquids have zero shear modulus."),
    "hacim_modulu": ("Sivilar neredeyse sikistirilamaz; hidrolik sistemler "
                     "tam da bu ozellik sayesinde calisir.",
                     "Liquids are nearly incompressible."),
    "debye": ("Debye uzunlugu, bir yukun etkisinin plazmada ne kadar uzaga "
              "gidebildigidir; otesinde yuk perdelenir.",
              "Beyond the Debye length charges are screened."),
    "plazma_frekans": ("Plazma, kendi frekansindan DUSUK frekanslari yansitir. "
                       "Kisa dalga radyonun iyonosferden sekerek dunyayi "
                       "dolasmasi budur.",
                       "Plasma reflects waves below its own frequency."),
    "larmor": ("Manyetik alan yuklu parcaciklari spiral yorungeye hapseder; "
               "fuzyon reaktorlerinde plazmayi tutan ilke budur.",
               "Magnetic fields trap charged particles in spirals."),

    # Astro
    "kadir": ("Kadir olcegi TERSTIR: sayi kucuk oldukça cisim parlaktir. "
              "5 kadirlik fark tam 100 kat parlaklik demektir.",
              "Smaller magnitude means brighter."),
    "uzaklik_modulu": ("Gorunen ve mutlak parlaklik farki uzakligi verir; "
                       "'standart mum' yontemi budur.",
                       "The magnitude difference encodes distance."),
    "kirmizi_kayma": ("Kirmizi kayma galaksinin uzayda kosmasindan degil, "
                      "UZAYIN kendisinin genislemesinden gelir.",
                      "Cosmological redshift comes from expanding space."),
    "jeans": ("Bulut, kendi cekimi ic basinci yenecek kadar buyukse coker ve "
              "yildiz olusur; Jeans kutlesi bu esiktir.",
              "Above the Jeans mass a cloud collapses into stars."),

    # Elektronik
    "gerilim_bolucu": ("Gerilim direnclerle ORANTILI paylasilir; yuk "
                       "baglandiginda bu oran bozulur, bu yuzden bolucu "
                       "yuksek akim cekmeyen yerlerde kullanilir.",
                       "Loading changes a divider's ratio."),
    "kesim_frekansi": ("Kesim frekansinda cikis gucu yariya iner (-3 dB); "
                       "filtre burada 'kesmeye baslar', aniden durdurmaz.",
                       "At cutoff the output power halves."),
    "kalite_faktoru": ("Q buyudukce rezonans daha keskin olur: radyo "
                       "istasyonlarini birbirinden ayirmak kolaylasir ama "
                       "band genisligi daralir.",
                       "Higher Q means sharper resonance, narrower band."),
})
