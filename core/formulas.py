"""Fizik formul veritabani ve formul cozucu.

Her formul bir denklem olarak saklanir; kullanici bilinenleri verdiginde
bilinmeyen degisken icin cozulur. Birim ve boyut kontrolu de yapilir.
"""
import re
import sympy as sp

from . import units as U
from .solver import parse, fmt_expr, latex as _tex, SolveError


def F(fid, topic, tr, en, eq, vars_, kw_tr="", kw_en="", note_tr="", note_en=""):
    return {
        "id": fid, "topic": topic, "tr": tr, "en": en, "eq": eq,
        "vars": vars_, "kw_tr": kw_tr.split("|") if kw_tr else [],
        "kw_en": kw_en.split("|") if kw_en else [],
        "note_tr": note_tr, "note_en": note_en,
    }


# vars_: {"sembol": ("turkce ad", "english name", "birim")}
FORMULAS = [
    # --- Kinematik ---------------------------------------------------------
    F("v_ort", "kinematik", "Ortalama hiz", "Average velocity",
      "v = dx/dt",
      {"v": ("hiz", "velocity", "m/s"), "dx": ("yer degistirme", "displacement", "m"),
       "dt": ("zaman", "time", "s")},
      "ortalama hiz|hiz formulu|yer degistirme zaman", "average velocity|speed"),
    F("kin_v", "kinematik", "Hiz-zaman bagintisi", "Velocity-time relation",
      "v = v0 + a*t",
      {"v": ("son hiz", "final velocity", "m/s"), "v0": ("ilk hiz", "initial velocity", "m/s"),
       "a": ("ivme", "acceleration", "m/s^2"), "t": ("zaman", "time", "s")},
      "hiz zaman|sabit ivme|ivmeli hareket", "velocity time|constant acceleration"),
    F("kin_x", "kinematik", "Konum-zaman bagintisi", "Position-time relation",
      "x = x0 + v0*t + a*t**2/2",
      {"x": ("konum", "position", "m"), "x0": ("ilk konum", "initial position", "m"),
       "v0": ("ilk hiz", "initial velocity", "m/s"),
       "a": ("ivme", "acceleration", "m/s^2"), "t": ("zaman", "time", "s")},
      "konum zaman|alinan yol|mesafe", "position time|distance"),
    F("kin_v2", "kinematik", "Hiz-yol bagintisi (Torricelli)", "Torricelli equation",
      "v**2 = v0**2 + 2*a*dx",
      {"v": ("son hiz", "final velocity", "m/s"), "v0": ("ilk hiz", "initial velocity", "m/s"),
       "a": ("ivme", "acceleration", "m/s^2"), "dx": ("yol", "displacement", "m")},
      "kayarsa sondaki hizi|kayarak sondaki hiz|m kayarsa hizi|yol sonunda hizi|sondaki hizi|torricelli|hiz yol|zamansiz", "torricelli|velocity displacement"),
    F("ivme", "kinematik", "Ivme tanimi", "Acceleration definition",
      "a = dv/dt",
      {"a": ("ivme", "acceleration", "m/s^2"), "dv": ("hiz degisimi", "velocity change", "m/s"),
       "dt": ("zaman", "time", "s")},
      "ivme|hizlanma", "acceleration"),
    F("egik_menzil", "kinematik", "Egik atis menzili", "Projectile range",
      "R = v0**2*sin(2*theta)/g",
      {"R": ("menzil", "range", "m"), "v0": ("ilk hiz", "initial speed", "m/s"),
       "theta": ("atis acisi (rad)", "launch angle (rad)", "rad"),
       "g": ("yercekimi ivmesi", "gravity", "m/s^2")},
      "egik atis|menzil|atis mesafesi", "projectile|range",
      "45 derecede menzil maksimumdur.|ne kadar uzaga gider|atis mesafesi|ucus menzili", "Range is maximum at 45 degrees."),
    F("egik_h", "kinematik", "Egik atis maksimum yukseklik", "Projectile max height",
      "H = v0**2*sin(theta)**2/(2*g)",
      {"H": ("maksimum yukseklik", "max height", "m"), "v0": ("ilk hiz", "initial speed", "m/s"),
       "theta": ("aci (rad)", "angle (rad)", "rad"), "g": ("yercekimi", "gravity", "m/s^2")},
      "egik atis yukseklik|maksimum yukseklik|en yuksek nokta|tepe noktasi|maksimum yukseklik|cikabilecegi yukseklik", "projectile height|max height"),
    F("serbest_dusme", "kinematik", "Serbest dusme", "Free fall",
      "h = g*t**2/2",
      {"h": ("yukseklik", "height", "m"), "g": ("yercekimi", "gravity", "m/s^2"),
       "t": ("dusme suresi", "fall time", "s")},
      "serbest dusme|dusme|yukseklik zaman|havada kalma suresi|dusme suresi|ne kadar surede duser|ucus suresi", "free fall|drop"),
    F("merkezcil", "kinematik", "Merkezcil ivme", "Centripetal acceleration",
      "a = v**2/r",
      {"a": ("merkezcil ivme", "centripetal acceleration", "m/s^2"),
       "v": ("cizgisel hiz", "tangential speed", "m/s"),
       "r": ("yaricap", "radius", "m")},
      "merkezcil ivme|dairesel hareket", "centripetal|circular motion"),
    F("acisal", "kinematik", "Acisal hiz - cizgisel hiz", "Angular-linear velocity",
      "v = omega*r",
      {"v": ("cizgisel hiz", "linear speed", "m/s"),
       "omega": ("acisal hiz", "angular velocity", "rad/s"),
       "r": ("yaricap", "radius", "m")},
      "acisal hiz|cizgisel hiz", "angular velocity"),
    F("periyot_frekans", "kinematik", "Periyot - frekans", "Period - frequency",
      "T = 1/f",
      {"T": ("periyot", "period", "s"), "f": ("frekans", "frequency", "Hz")},
      "periyot|frekans", "period|frequency"),

    # --- Dinamik -----------------------------------------------------------
    F("newton2", "dinamik", "Newton'un 2. yasasi", "Newton's second law",
      "F = m*a",
      {"F": ("kuvvet", "force", "N"), "m": ("kutle", "mass", "kg"),
       "a": ("ivme", "acceleration", "m/s^2")},
      "newton|kuvvet|f=ma|ikinci yasa", "newton second law|force"),
    F("agirlik", "dinamik", "Agirlik", "Weight",
      "W = m*g",
      {"W": ("agirlik", "weight", "N"), "m": ("kutle", "mass", "kg"),
       "g": ("yercekimi ivmesi", "gravity", "m/s^2")},
      "agirlik|kutle agirlik", "weight"),
    F("surtunme", "dinamik", "Surtunme kuvveti", "Friction force",
      "f = mu*N",
      {"f": ("surtunme kuvveti", "friction force", "N"),
       "mu": ("surtunme katsayisi", "friction coefficient", ""),
       "N": ("normal kuvvet", "normal force", "N")},
      "surtunme|surtunme kuvveti", "friction"),
    F("momentum", "dinamik", "Momentum", "Momentum",
      "p = m*v",
      {"p": ("momentum", "momentum", "kg·m/s"), "m": ("kutle", "mass", "kg"),
       "v": ("hiz", "velocity", "m/s")},
      "momentum|hareket miktari", "momentum"),
    F("impuls", "dinamik", "Impuls - momentum", "Impulse-momentum",
      "J = F*dt",
      {"J": ("impuls", "impulse", "N·s"), "F": ("kuvvet", "force", "N"),
       "dt": ("sure", "duration", "s")},
      "impuls|itme", "impulse"),
    F("hooke", "dinamik", "Hooke yasasi", "Hooke's law",
      "F = k*x",
      {"F": ("yay kuvveti", "spring force", "N"),
       "k": ("yay sabiti", "spring constant", "N/m"),
       "x": ("uzama", "extension", "m")},
      "hooke|yay|yay kuvveti|yay sabiti", "hooke|spring"),
    F("kutle_cekim", "dinamik", "Evrensel kutle cekim yasasi", "Newton's law of gravitation",
      "F = G*m1*m2/r**2",
      {"F": ("cekim kuvveti", "gravitational force", "N"),
       "G": ("kutle cekim sabiti", "gravitational constant", "m^3/(kg·s^2)"),
       "m1": ("1. kutle", "first mass", "kg"), "m2": ("2. kutle", "second mass", "kg"),
       "r": ("uzaklik", "distance", "m")},
      "kutle cekim|gravitasyon|cekim kuvveti", "gravitation|gravity force"),
    F("tork", "dinamik", "Tork (moment)", "Torque",
      "tau = r*F*sin(theta)",
      {"tau": ("tork", "torque", "N·m"), "r": ("kol uzunlugu", "lever arm", "m"),
       "F": ("kuvvet", "force", "N"), "theta": ("aci (rad)", "angle (rad)", "rad")},
      "tork|moment|donme kuvveti", "torque|moment"),
    F("aci_momentum", "dinamik", "Aci momentumu", "Angular momentum",
      "L = I*omega",
      {"L": ("aci momentumu", "angular momentum", "kg·m^2/s"),
       "I": ("eylemsizlik momenti", "moment of inertia", "kg·m^2"),
       "omega": ("acisal hiz", "angular velocity", "rad/s")},
      "aci momentumu|acisal momentum", "angular momentum"),
    F("donme_newton", "dinamik", "Donme icin Newton yasasi", "Rotational Newton's law",
      "tau = I*alpha",
      {"tau": ("tork", "torque", "N·m"),
       "I": ("eylemsizlik momenti", "moment of inertia", "kg·m^2"),
       "alpha": ("acisal ivme", "angular acceleration", "rad/s^2")},
      "donme|acisal ivme|eylemsizlik momenti", "rotational|angular acceleration"),
    F("yorunge_hiz", "dinamik", "Yorunge hizi", "Orbital velocity",
      "v = sqrt(G*M/r)",
      {"v": ("yorunge hizi", "orbital speed", "m/s"),
       "G": ("cekim sabiti", "gravitational constant", "m^3/(kg·s^2)"),
       "M": ("merkez kutle", "central mass", "kg"),
       "r": ("yorunge yaricapi", "orbital radius", "m")},
      "yorunge hizi|uydu hizi", "orbital velocity|satellite speed"),
    F("kacis_hiz", "dinamik", "Kacis hizi", "Escape velocity",
      "v = sqrt(2*G*M/r)",
      {"v": ("kacis hizi", "escape velocity", "m/s"),
       "G": ("cekim sabiti", "gravitational constant", "m^3/(kg·s^2)"),
       "M": ("kutle", "mass", "kg"), "r": ("yaricap", "radius", "m")},
      "kacis hizi|kurtulma hizi", "escape velocity"),
    F("kepler3", "dinamik", "Kepler 3. yasa", "Kepler's third law",
      "T**2 = 4*pi**2*a**3/(G*M)",
      {"T": ("yorunge periyodu", "orbital period", "s"),
       "a": ("yari buyuk eksen", "semi-major axis", "m"),
       "G": ("cekim sabiti", "gravitational constant", "m^3/(kg·s^2)"),
       "M": ("merkez kutle", "central mass", "kg")},
      "kepler|yorunge periyodu", "kepler|orbital period"),
    F("schwarzschild", "dinamik", "Schwarzschild yaricapi", "Schwarzschild radius",
      "rs = 2*G*M/c**2",
      {"rs": ("olay ufku yaricapi", "event horizon radius", "m"),
       "G": ("cekim sabiti", "gravitational constant", "m^3/(kg·s^2)"),
       "M": ("kutle", "mass", "kg"), "c": ("isik hizi", "speed of light", "m/s")},
      "schwarzschild|kara delik|olay ufku", "schwarzschild|black hole|event horizon"),

    # --- Enerji ------------------------------------------------------------
    F("kinetik", "enerji", "Kinetik enerji", "Kinetic energy",
      "Ek = m*v**2/2",
      {"Ek": ("kinetik enerji", "kinetic energy", "J"),
       "m": ("kutle", "mass", "kg"), "v": ("hiz", "speed", "m/s")},
      "kinetik enerji|hareket enerjisi", "kinetic energy"),
    F("potansiyel", "enerji", "Yercekimi potansiyel enerjisi", "Gravitational potential energy",
      "Ep = m*g*h",
      {"Ep": ("potansiyel enerji", "potential energy", "J"),
       "m": ("kutle", "mass", "kg"), "g": ("yercekimi", "gravity", "m/s^2"),
       "h": ("yukseklik", "height", "m")},
      "potansiyel enerji|cekim potansiyeli", "potential energy"),
    F("yay_enerji", "enerji", "Yay potansiyel enerjisi", "Spring potential energy",
      "Ep = k*x**2/2",
      {"Ep": ("yay enerjisi", "spring energy", "J"),
       "k": ("yay sabiti", "spring constant", "N/m"), "x": ("uzama", "extension", "m")},
      "yay enerjisi|esneklik enerjisi", "spring energy|elastic energy"),
    F("is", "enerji", "Is (kuvvet x yol)", "Work",
      "W = F*d*cos(theta)",
      {"W": ("is", "work", "J"), "F": ("kuvvet", "force", "N"),
       "d": ("yol", "distance", "m"), "theta": ("aci (rad)", "angle (rad)", "rad")},
      "is|yapilan is", "work"),
    F("guc", "enerji", "Guc", "Power",
      "P = W/t",
      {"P": ("guc", "power", "W"), "W": ("is/enerji", "work/energy", "J"),
       "t": ("sure", "time", "s")},
      "guc|kuvvet gucu", "power"),
    F("guc_hiz", "enerji", "Guc (kuvvet x hiz)", "Power (force x velocity)",
      "P = F*v",
      {"P": ("guc", "power", "W"), "F": ("kuvvet", "force", "N"),
       "v": ("hiz", "velocity", "m/s")},
      "guc hiz|anlik guc", "instantaneous power"),
    F("verim", "enerji", "Verim", "Efficiency",
      "eta = Pout/Pin",
      {"eta": ("verim", "efficiency", ""), "Pout": ("cikis gucu", "output power", "W"),
       "Pin": ("giris gucu", "input power", "W")},
      "verim|randiman", "efficiency"),
    F("E_mc2", "enerji", "Kutle-enerji esdegerligi", "Mass-energy equivalence",
      "E = m*c**2",
      {"E": ("enerji", "energy", "J"), "m": ("kutle", "mass", "kg"),
       "c": ("isik hizi", "speed of light", "m/s")},
      "e=mc2|kutle enerji|einstein", "mass energy|einstein"),

    # --- Termodinamik ------------------------------------------------------
    F("ideal_gaz", "termodinamik", "Ideal gaz yasasi", "Ideal gas law",
      "P*V = n*R*T",
      {"P": ("basinc", "pressure", "Pa"), "V": ("hacim", "volume", "m^3"),
       "n": ("mol sayisi", "moles", "mol"), "R": ("gaz sabiti", "gas constant", "J/(mol·K)"),
       "T": ("sicaklik", "temperature", "K")},
      "ideal gaz|gaz yasasi|pv=nrt", "ideal gas|gas law"),
    F("isi", "termodinamik", "Isi (sicaklik degisimi)", "Heat (sensible)",
      "Q = m*c*dT",
      {"Q": ("isi", "heat", "J"), "m": ("kutle", "mass", "kg"),
       "c": ("ozgul isi", "specific heat", "J/(kg·K)"),
       "dT": ("sicaklik degisimi", "temperature change", "K")},
      "isi|ozgul isi|sicaklik degisimi", "heat|specific heat"),
    F("gizli_isi", "termodinamik", "Gizli isi (hal degisimi)", "Latent heat",
      "Q = m*L",
      {"Q": ("isi", "heat", "J"), "m": ("kutle", "mass", "kg"),
       "L": ("gizli isi", "latent heat", "J/kg")},
      "gizli isi|erime isisi|buharlasma isisi", "latent heat|fusion|vaporization"),
    # HAL DEGISIMI + ISITMA tek denklemde. Olculdu: "0 derecede 0,5 kg
    # buzu eritip 20 dereceye getirmek icin gereken isi" sorusunda iki
    # ayri sureci (erime ve isitma) TOPLAMAK gerekiyor; zincir iki ayri
    # `Q` degerini toplayamiyor, yalnizca birini veriyordu (167000 ya da
    # 41860; dogrusu 208860).
    F("kalorimetre_toplam", "termodinamik",
      "Hal degisimi ve isitma icin toplam isi",
      "Total heat for melting then heating",
      "Q = m*L + m*c*dT",
      {"Q": ("toplam isi", "total heat", "J"),
       "m": ("kutle", "mass", "kg"),
       "L": ("gizli isi", "latent heat", "J/kg"),
       "c": ("ozgul isi", "specific heat", "J/(kg·K)"),
       "dT": ("sicaklik degisimi", "temperature change", "K")},
      # DIKKAT: anahtarlar ERITME fiilini SART kosmali. Ilk hâlinde
      # "isitmak icin gereken isi" gecen duz isitma sorusu da buraya
      # geliyordu ("2 kg suyu 20 dereceden 80 dereceye isitmak") ve
      # gizli isi terimi bosuna ekleniyordu (sayisal 39/39 -> 38/39).
      # "eritmek ve isitmak icin gereken isi" anahtari da SILINDI: kismi
      # eslesme yuzunden duz isitma sorusuna puan yaziyordu. Her anahtar
      # ERITME fiilini icermeli.
      "eritip isitmak|eritip getirmek|buzu eritip|eritip sicakliga|"
      "once eritip sonra isitmak|eritip sonra isitmak",
      "melt then heat|total heat melting and heating"),
    F("termo1", "termodinamik", "Termodinamigin 1. yasasi", "First law of thermodynamics",
      "dU = Q - W",
      {"dU": ("ic enerji degisimi", "internal energy change", "J"),
       "Q": ("sisteme verilen isi", "heat added", "J"),
       "W": ("sistemin yaptigi is", "work done", "J")},
      "birinci yasa|ic enerji|termodinamik", "first law|internal energy"),
    F("entropi", "termodinamik", "Entropi degisimi (tersinir)", "Entropy change",
      "dS = Q/T",
      {"dS": ("entropi degisimi", "entropy change", "J/K"),
       "Q": ("isi", "heat", "J"), "T": ("sicaklik", "temperature", "K")},
      "entropi|duzensizlik", "entropy"),
    F("carnot", "termodinamik", "Carnot verimi", "Carnot efficiency",
      "eta = 1 - Tc/Th",
      {"eta": ("verim", "efficiency", ""), "Tc": ("soguk kaynak", "cold reservoir", "K"),
       "Th": ("sicak kaynak", "hot reservoir", "K")},
      "carnot|isi makinesi verimi", "carnot|heat engine"),
    # Olculdu (zor problem seti, 2/20): asagidaki bagintilar cekirdekte
    # yoktu ve sorular yanlis formule gidiyordu. Her biri elle hesaplanmis
    # bir problemle dogrulandi.
    # Olculdu (zor set): asagidaki dort baginti cekirdekte yoktu ve
    # sorular ya yanlis formule gidiyor ya da sayi cikmiyordu.
    F("egik_surtunmeli_ivme", "mekanik",
      "Surtunmeli egik duzlemde ivme",
      "Acceleration on an incline with friction",
      "a = g*(sin(theta) - mu*cos(theta))",
      {"a": ("ivme", "acceleration", "m/s^2"),
       "g": ("yercekimi ivmesi", "gravity", "m/s^2"),
       "theta": ("egim acisi", "incline angle", "rad"),
       "mu": ("surtunme katsayisi", "friction coefficient", "")},
      "egik duzlemde surtunme ivme|egimli duzlemde ivme|"
      "surtunmeli egik duzlem|egik duzlemde kayan cisim ivmesi|"
      "egimli yuzeyde ivme",
      "incline friction acceleration|slope acceleration friction"),
    F("carpisma_enerji_kaybi", "mekanik",
      "Esnek olmayan carpismada kaybolan enerji",
      "Energy lost in a perfectly inelastic collision",
      "dEk = m1*m2*(v1 - v2)**2/(2*(m1 + m2))",
      {"dEk": ("kaybolan kinetik enerji", "kinetic energy lost", "J"),
       "m1": ("1. kutle", "mass 1", "kg"), "m2": ("2. kutle", "mass 2", "kg"),
       "v1": ("1. hiz", "speed 1", "m/s"), "v2": ("2. hiz", "speed 2", "m/s")},
      "carpismada kaybolan enerji|kaybolan kinetik enerji|"
      "carpismada kaybedilen enerji|yapisirsa kaybolan enerji|"
      "esnek olmayan carpismada enerji kaybi|isiya donusen enerji",
      "energy lost in collision|kinetic energy lost inelastic"),
    F("rc_gerilim", "elektrik",
      "RC devresinde kondansator gerilimi (dolarken)",
      "Capacitor voltage while charging in an RC circuit",
      "Vc = V0*(1 - exp(-t/(R*C)))",
      {"Vc": ("kondansator gerilimi", "capacitor voltage", "V"),
       "V0": ("kaynak gerilimi", "source voltage", "V"),
       "t": ("sure", "time", "s"), "R": ("direnc", "resistance", "ohm"),
       "C": ("siga", "capacitance", "F")},
      "kondansator gerilimi saniye sonra|rc devresinde gerilim|"
      "dolarken gerilim|kondansator dolarken gerilimi|"
      "saniye sonra kondansator gerilimi",
      "capacitor voltage charging|rc circuit voltage after"),
    F("bohr_gecis", "kuantum",
      "Bohr modelinde gecis enerjisi",
      "Transition energy in the Bohr model",
      # Ry cekirdekte NEGATIF saklanIyor (baglanma enerjisi, -13,6 eV).
      # Bu yuzden terimler n1-n2 sirasinda yazildi; yayilan foton
      # enerjisi POZITIF cikiyor (olculdu: ters sirada -1,63e-18).
      # Ry'nin isareti cekirdekte ve sabit tablosunda farkli olabiliyor
      # (baglanma enerjisi -13,6 eV ya da Rydberg +13,6 eV). Yayilan
      # foton enerjisi HER HALUKARDA pozitiftir; mutlak deger bunu
      # sabitler (olculdu: iki yolda da -1,63e-18 cikiyordu).
      # Ry sabit tablosundan eV cinsinden geliyor ve sonuc "10.2 J"
      # gibi BIRIMI YANLIS bir cevap uretiyordu (olculdu). Rydberg
      # enerjisi dogrudan JOULE olarak yaziliyor: 13,6057 eV.
      "E = 2.1798723e-18*Z**2*(1/n2**2 - 1/n1**2)",
      {"E": ("yayilan fotonun enerjisi", "emitted photon energy", "J"),
       "Z": ("atom numarasi", "atomic number", ""),
       "n1": ("ust duzey", "upper level", ""),
       "n2": ("alt duzey", "lower level", "")},
      # DIKKAT: "yayilan enerji" gibi genel bir anahtar KOYULMAMALI.
      # Olculdu: "gunes ne kadar enerji yayiyor" sorusu Stefan-Boltzmann
      # yerine buraya geliyordu (yonlendirme 40/40 -> 39/40). Her anahtar
      # DUZEY GECISINI adlandirmali.
      "gecerken yayilan fotonun enerjisi|duzeyler arasi gecis enerjisi|"
      "n den n e gecis enerjisi|hidrojen gecis enerjisi|"
      # Uzun "…yayilan fotonun enerjisi" turevleri GERI ALINDI: kismi
      # eslesme yuzunden "gunes ne kadar enerji yayiyor" sorusunu
      # Stefan-Boltzmann'dan caliyorlardi (yonlendirme 40 -> 39).
      "enerji duzeyi gecisi|n2 den n1 e gecis",
      "transition energy bohr|emitted photon energy level"),
    F("cift_yarik_sacak", "dalga", "Cift yarikta sacak araligi",
      "Fringe spacing in a double slit",
      "dy = lam*Lp/d",
      {"dy": ("sacak araligi", "fringe spacing", "m"),
       "lam": ("dalga boyu", "wavelength", "m"),
       "Lp": ("perde uzakligi", "screen distance", "m"),
       "d": ("yarik araligi", "slit separation", "m")},
      "sacak araligi|sacaklar arasi uzaklik|perdede sacak araligi|"
      "girisim sacak araligi|cift yarikta sacak",
      "fringe spacing|fringe separation double slit"),
    F("viraj_hiz", "mekanik", "Yatay virajda maksimum hiz",
      "Maximum speed on a flat curve",
      "v = sqrt(mu*g*r)",
      {"v": ("maksimum hiz", "maximum speed", "m/s"),
       "mu": ("surtunme katsayisi", "friction coefficient", ""),
       "g": ("yercekimi ivmesi", "gravity", "m/s^2"),
       "r": ("viraj yaricapi", "curve radius", "m")},
      "virajda maksimum hiz|viraj hizi|donemecte hiz|"
      "kaymadan alabilecegi hiz|savrulmadan hiz|yatay viraj",
      "maximum speed curve|flat curve speed|cornering speed"),
    F("atwood", "mekanik", "Atwood makinesi ivmesi",
      "Atwood machine acceleration",
      "a = g*(m2 - m1)/(m1 + m2)",
      {"a": ("ivme", "acceleration", "m/s^2"),
       "g": ("yercekimi ivmesi", "gravity", "m/s^2"),
       "m1": ("hafif kutle", "lighter mass", "kg"),
       "m2": ("agir kutle", "heavier mass", "kg")},
      "atwood|makaradan gecen ip|makara iki kutle|"
      "ipin uclarindaki kutleler|makarali sistem ivme",
      "atwood machine|pulley two masses"),
    F("yuvarlanma_hiz", "mekanik", "Yuvarlanarak inen cismin hizi",
      "Speed of a rolling body down a slope",
      "v = sqrt(2*g*h/(1 + k))",
      {"v": ("hiz", "speed", "m/s"),
       "g": ("yercekimi ivmesi", "gravity", "m/s^2"),
       "h": ("yukseklik", "height", "m"),
       "k": ("eylemsizlik carpani", "inertia factor", "")},
      "yuvarlanarak inen|yuvarlanan silindir|yuvarlanan kure|"
      "yuvarlanma hizi|egimden yuvarlanan",
      "rolling down incline|rolling cylinder speed|rolling sphere"),
    F("manyetik_yaricap", "elektromanyetizma",
      "Manyetik alanda yuklu parcacigin yorunge yaricapi",
      "Radius of a charged particle in a magnetic field",
      "r = m*v/(q*B)",
      {"r": ("yorunge yaricapi", "orbit radius", "m"),
       "m": ("kutle", "mass", "kg"), "v": ("hiz", "speed", "m/s"),
       "q": ("yuk", "charge", "C"),
       "B": ("manyetik alan", "magnetic field", "T")},
      "yorunge yaricapi|manyetik alanda yaricap|siklotron yaricapi|"
      "manyetik alanda dairesel hareket yaricap|parcacigin yaricapi",
      "orbit radius magnetic field|cyclotron radius|gyroradius"),
    F("carnot_is", "termodinamik", "Carnot makinesinin yaptigi is",
      "Work done by a Carnot engine",
      "W = Qh*(1 - Tc/Th)",
      {"W": ("yaptigi net is", "net work done", "J"),
       "Qh": ("alinan isi", "heat absorbed", "J"),
       "Tc": ("soguk kaynak", "cold reservoir", "K"),
       "Th": ("sicak kaynak", "hot reservoir", "K")},
      "carnot makinesi is|carnot yaptigi is|isi makinesi is|"
      "makinenin yaptigi is|carnot net is",
      "carnot work|work done by engine|net work heat engine"),
    F("izotermal_is", "termodinamik", "Izotermal iste yapilan is",
      "Work in an isothermal process",
      "W = n*R*T*log(V2/V1)",
      {"W": ("yapilan is", "work done", "J"),
       "n": ("mol sayisi", "moles", "mol"),
       "R": ("gaz sabiti", "gas constant", "J/(mol·K)"),
       "T": ("sicaklik", "temperature", "K"),
       "V2": ("son hacim", "final volume", "m^3"),
       "V1": ("ilk hacim", "initial volume", "m^3")},
      # Olculdu: bu soru IDEAL GAZ YASASI'na gidiyordu; "mol" ve "ideal
      # gaz" kelimeleri agir basiyordu. Izotermal ISE ozgu ifadeler eklendi.
      "izotermal is|izotermal genlesme is|sabit sicaklikta genlesme|"
      "izotermal surecte yapilan is|izotermal genlesirse yaptigi is|"
      "izotermal genlesme yapilan is|hacmi iki katina izotermal|"
      "sabit sicaklikta yapilan is|izotermal is nedir",
      "isothermal work|isothermal expansion work"),
    F("boltzmann_S", "termodinamik", "Boltzmann entropisi", "Boltzmann entropy",
      "S = kB*log(W)",
      {"S": ("entropi", "entropy", "J/K"),
       "kB": ("Boltzmann sabiti", "Boltzmann constant", "J/K"),
       "W": ("mikro durum sayisi", "microstates", "")},
      "boltzmann entropi|mikro durum", "boltzmann entropy|microstates"),
    F("stefan", "termodinamik", "Stefan-Boltzmann yasasi", "Stefan-Boltzmann law",
      "P = sigma*A*eps*T**4",
      {"P": ("isima gucu", "radiated power", "W"),
       "sigma": ("Stefan-Boltzmann sabiti", "Stefan-Boltzmann constant", "W/(m^2·K^4)"),
       "A": ("yuzey alani", "surface area", "m^2"),
       "eps": ("yayma katsayisi", "emissivity", ""),
       "T": ("sicaklik", "temperature", "K")},
      "stefan boltzmann|isima|kara cisim", "stefan boltzmann|blackbody radiation"),
    F("wien", "termodinamik", "Wien yer degistirme yasasi", "Wien's displacement law",
      "lam = bW/T",
      {"lam": ("tepe dalga boyu", "peak wavelength", "m"),
       "bW": ("Wien yer degistirme sabiti", "Wien displacement constant", "m·K"),
       "T": ("sicaklik", "temperature", "K")},
      "wien|tepe dalga boyu|kara cisim", "wien|peak wavelength"),
    F("isi_iletim", "termodinamik", "Isi iletimi (Fourier)", "Heat conduction",
      "Q = k*A*dT*t/L",
      {"Q": ("iletilen isi", "heat", "J"), "k": ("isi iletkenligi", "conductivity", "W/(m·K)"),
       "A": ("kesit alani", "area", "m^2"), "dT": ("sicaklik farki", "temp difference", "K"),
       "t": ("sure", "time", "s"), "L": ("kalinlik", "thickness", "m")},
      "isi iletimi|fourier|iletim", "heat conduction|fourier"),
    F("rms_hiz", "termodinamik", "Gaz molekullerinin rms hizi", "RMS molecular speed",
      "v = sqrt(3*kB*T/m)",
      {"v": ("rms hiz", "rms speed", "m/s"), "kB": ("Boltzmann sabiti", "Boltzmann", "J/K"),
       "T": ("sicaklik", "temperature", "K"), "m": ("molekul kutlesi", "molecular mass", "kg")},
      "rms hiz|molekul hizi|kinetik teori", "rms speed|kinetic theory"),

    # --- Elektrik & manyetizma ---------------------------------------------
    F("coulomb", "elektrik", "Coulomb yasasi", "Coulomb's law",
      "F = ke*q1*q2/r**2",
      {"F": ("elektriksel kuvvet", "electric force", "N"),
       "ke": ("Coulomb sabiti", "Coulomb constant", "N·m^2/C^2"),
       "q1": ("1. yuk", "charge 1", "C"), "q2": ("2. yuk", "charge 2", "C"),
       "r": ("uzaklik", "distance", "m")},
      "coulomb|elektriksel kuvvet|yuk", "coulomb|electric force"),
    F("E_alan", "elektrik", "Elektrik alan (nokta yuk)", "Electric field of point charge",
      "E = ke*q/r**2",
      {"E": ("elektrik alan", "electric field", "V/m"),
       "ke": ("Coulomb sabiti", "Coulomb constant", "N·m^2/C^2"),
       "q": ("yuk", "charge", "C"), "r": ("uzaklik", "distance", "m")},
      "elektrik alan|nokta yuk alani", "electric field"),
    F("E_kuvvet", "elektrik", "Elektrik alanda kuvvet", "Force in electric field",
      "F = q*E",
      {"F": ("kuvvet", "force", "N"), "q": ("yuk", "charge", "C"),
       "E": ("elektrik alan", "electric field", "V/m")},
      "alanda kuvvet|yuke etkiyen kuvvet", "force electric field"),
    F("potansiyel_V", "elektrik", "Elektrik potansiyeli", "Electric potential",
      "V = ke*q/r",
      {"V": ("potansiyel", "potential", "V"),
       "ke": ("Coulomb sabiti", "Coulomb constant", "N·m^2/C^2"),
       "q": ("yuk", "charge", "C"), "r": ("uzaklik", "distance", "m")},
      "elektrik potansiyeli|voltaj", "electric potential"),
    F("ohm", "elektrik", "Ohm yasasi", "Ohm's law",
      "V = I*R",
      {"V": ("gerilim", "voltage", "V"), "I": ("akim", "current", "A"),
       "R": ("direnc", "resistance", "ohm")},
      "ohm|gerilim akim direnc|v=ir", "ohm law|voltage current resistance"),
    # Seri/paralel esdeger direnc ve siga. Olculdu: "5 ohm ve 10 ohm
    # paralel bagli 12 V kaynaga bagli toplam akim" sorusu hicbir
    # formule ulasamiyor, genel Ohm yasasi anlatimina dusuyordu.
    F("direnc_seri", "elektrik", "Seri esdeger direnc",
      "Series equivalent resistance",
      "Rs = R1 + R2",
      {"Rs": ("esdeger direnc", "equivalent resistance", "ohm"),
       "R1": ("birinci direnc", "first resistance", "ohm"),
       "R2": ("ikinci direnc", "second resistance", "ohm")},
      "seri direnc|seri baglama|esdeger direnc seri|dirençler seri",
      "series resistance|resistors in series"),
    F("direnc_paralel", "elektrik", "Paralel esdeger direnc",
      "Parallel equivalent resistance",
      "Rp = R1*R2/(R1 + R2)",
      {"Rp": ("esdeger direnc", "equivalent resistance", "ohm"),
       "R1": ("birinci direnc", "first resistance", "ohm"),
       "R2": ("ikinci direnc", "second resistance", "ohm")},
      "paralel direnc|paralel baglama|esdeger direnc paralel|"
      "dirençler paralel|paralel bagli direnc",
      "parallel resistance|resistors in parallel"),
    F("siga_seri", "elektrik", "Seri esdeger siga",
      "Series equivalent capacitance",
      "Cs = C1*C2/(C1 + C2)",
      {"Cs": ("esdeger siga", "equivalent capacitance", "F"),
       "C1": ("birinci siga", "first capacitance", "F"),
       "C2": ("ikinci siga", "second capacitance", "F")},
      "seri kondansator|seri siga|kondansatorler seri",
      "capacitors in series"),
    F("siga_paralel", "elektrik", "Paralel esdeger siga",
      "Parallel equivalent capacitance",
      "Cp = C1 + C2",
      {"Cp": ("esdeger siga", "equivalent capacitance", "F"),
       "C1": ("birinci siga", "first capacitance", "F"),
       "C2": ("ikinci siga", "second capacitance", "F")},
      "paralel kondansator|paralel siga|kondansatorler paralel",
      "capacitors in parallel"),
    # Hizlandirici gerilimin verdigi enerji. Olculdu: "elektron 100 V ile
    # hizlandirilirsa kazandigi enerji" sorusu kinetik enerji formulune
    # gidip cozulemiyordu.
    F("yuk_enerji", "elektrik", "Yukun kazandigi enerji (qV)",
      "Energy gained by a charge",
      "E = q*V",
      {"E": ("enerji", "energy", "J"),
       "q": ("yuk", "charge", "C"),
       "V": ("hizlandirma gerilimi", "accelerating voltage", "V")},
      "hizlandirma gerilimi|gerilimle hizlandirilan|kazandigi enerji|"
      "yukun enerjisi|elektronvolt enerji|qv enerji",
      "accelerating voltage|energy gained by charge|qV"),
    # Hizlandirici gerilimden HIZ: qV = ½mv². Her fizik kitabinda ayri
    # bir baginti olarak verilir; olculdu: "elektron 200 V ile
    # hizlandirilirsa hizi" sorusu cozulemiyordu.
    # Yatay yuzeyde normal kuvvet. Olculdu: "surtunme katsayisi 0.4 olan
    # 10 kg cisme etkiyen surtunme kuvveti" sorusu cozulemiyordu, cunku
    # f = mu*N bagintisindaki N'yi uretecek halka yoktu.
    # Serbest dusmede carpma hizi: v = sqrt(2gh). Yer degistirme ile
    # YUKSEKLIK ayri buyuklukler oldugu icin (etiket kurali) yukseklikten
    # dogrudan hiz veren bir baginti gerekiyordu.
    F("dusme_hizi", "kinematik", "Serbest dusmede carpma hizi",
      "Impact speed in free fall",
      "v = sqrt(2*g*h)",
      {"v": ("carpma hizi", "impact speed", "m/s"),
       "g": ("yercekimi ivmesi", "gravity", "m/s^2"),
       "h": ("yukseklik", "height", "m")},
      "yuksekten dusen cismin hizi|yere carpma hizi|carpma hizi|"
      "dusen cismin carpma hizi|yuksekten birakilan cismin hizi|"
      "serbest dusme hizi",
      "impact speed|speed on impact|free fall speed"),
    F("normal_kuvvet", "dinamik", "Yatay yuzeyde normal kuvvet",
      "Normal force on a horizontal surface",
      "N = m*g",
      {"N": ("normal kuvvet", "normal force", "N"),
       "m": ("kutle", "mass", "kg"),
       "g": ("yercekimi ivmesi", "gravity", "m/s^2")},
      "normal kuvvet|yuzeyin tepki kuvveti|tepki kuvveti|"
      "yatay yuzeyde normal",
      "normal force|surface reaction force"),
    F("hizlandirma_hizi", "elektrik", "Hizlandirilan yukun hizi",
      "Speed of an accelerated charge",
      "v = sqrt(2*q*V/m)",
      {"v": ("hiz", "speed", "m/s"),
       "q": ("yuk", "charge", "C"),
       "V": ("hizlandirma gerilimi", "accelerating voltage", "V"),
       "m": ("kutle", "mass", "kg")},
      "hizlandirilan yukun hizi|gerilimle hizlandirilan hiz|"
      "hizlandirildiktan sonra hizi|elektron hizi gerilim|"
      "hizlandirilirsa hizi",
      "speed of accelerated charge|accelerating voltage speed"),
    F("elektrik_guc", "elektrik", "Elektriksel guc", "Electrical power",
      "P = V*I",
      {"P": ("guc", "power", "W"), "V": ("gerilim", "voltage", "V"),
       "I": ("akim", "current", "A")},
      # DIKKAT: buraya ciplak "guc nedir" KONULMAMALI. Olculdu: "2000 J
      # is 4 saniyede yapilirsa guc nedir" sorusu P = V*I'ya gidiyordu;
      # oysa mekanik guc sorusu. Anahtarlar ELEKTRIK baglamini tasimali.
      "elektrik gucu|watt|cekilen guc|devreden cekilen guc",
      "electrical power|power drawn from circuit"),
    F("guc_direnc", "elektrik", "Direncte harcanan guc (gerilimle)",
      "Power dissipated in a resistor (from voltage)",
      "P = V**2/R",
      {"P": ("guc", "power", "W"), "V": ("gerilim", "voltage", "V"),
       "R": ("direnc", "resistance", "ohm")},
      "direncte harcanan guc|direncin harcadigi guc|gerilim direnc guc|"
      "direncte guc|ampul gucu|isinan direnc gucu",
      "power dissipated resistor|power from voltage and resistance"),
    F("guc_akim_direnc", "elektrik", "Direncte harcanan guc (akimla)",
      "Power dissipated in a resistor (from current)",
      "P = I**2*R",
      {"P": ("guc", "power", "W"), "I": ("akim", "current", "A"),
       "R": ("direnc", "resistance", "ohm")},
      "akim direnc guc|akimla harcanan guc|i kare r",
      "power from current and resistance"),
    F("joule_isi", "elektrik", "Joule isisi", "Joule heating",
      "Q = I**2*R*t",
      {"Q": ("aciga cikan isi", "heat", "J"), "I": ("akim", "current", "A"),
       "R": ("direnc", "resistance", "ohm"), "t": ("sure", "time", "s")},
      "joule isisi|direncte isi", "joule heating"),
    F("direnc_tel", "elektrik", "Telin direnci", "Resistance of a wire",
      "R = rho*L/A",
      {"R": ("direnc", "resistance", "ohm"), "rho": ("ozdirenc", "resistivity", "ohm·m"),
       "L": ("uzunluk", "length", "m"), "A": ("kesit alani", "cross-section", "m^2")},
      "ozdirenc|tel direnci|kesit", "resistivity|wire resistance"),
    F("kapasitans", "elektrik", "Kondansator yuku", "Capacitor charge",
      "Q = C*V",
      {"Q": ("yuk", "charge", "C"), "C": ("sigma", "capacitance", "F"),
       "V": ("gerilim", "voltage", "V")},
      "kondansator|sigma|kapasitans", "capacitor|capacitance"),
    F("kond_enerji", "elektrik", "Kondansator enerjisi", "Capacitor energy",
      "E = C*V**2/2",
      {"E": ("depolanan enerji", "stored energy", "J"),
       "C": ("sigma", "capacitance", "F"), "V": ("gerilim", "voltage", "V")},
      "kondansator enerjisi", "capacitor energy"),
    F("paralel_plaka", "elektrik", "Paralel plakali kondansator", "Parallel plate capacitor",
      "C = eps0*epsr*A/d",
      {"C": ("sigma", "capacitance", "F"),
       "eps0": ("bosluk gecirgenligi", "vacuum permittivity", "F/m"),
       "epsr": ("bagil gecirgenlik", "relative permittivity", ""),
       "A": ("plaka alani", "plate area", "m^2"),
       "d": ("plaka arasi mesafe", "separation", "m")},
      "paralel plaka|kondansator sigasi", "parallel plate capacitor"),
    F("lorentz", "elektrik", "Manyetik kuvvet (Lorentz)", "Magnetic (Lorentz) force",
      "F = q*v*B*sin(theta)",
      {"F": ("manyetik kuvvet", "magnetic force", "N"), "q": ("yuk", "charge", "C"),
       "v": ("hiz", "speed", "m/s"), "B": ("manyetik alan", "magnetic field", "T"),
       "theta": ("aci (rad)", "angle (rad)", "rad")},
      "lorentz|manyetik kuvvet", "lorentz force|magnetic force"),
    F("tel_kuvvet", "elektrik", "Akim tasiyan tele etkiyen kuvvet", "Force on current-carrying wire",
      "F = B*I*L*sin(theta)",
      {"F": ("kuvvet", "force", "N"), "B": ("manyetik alan", "magnetic field", "T"),
       "I": ("akim", "current", "A"), "L": ("tel uzunlugu", "wire length", "m"),
       "theta": ("aci (rad)", "angle (rad)", "rad")},
      "tele etkiyen kuvvet|akim manyetik", "force on wire"),
    F("solenoid", "elektrik", "Solenoid ici manyetik alan", "Magnetic field in solenoid",
      "B = mu0*n*I",
      {"B": ("manyetik alan", "magnetic field", "T"),
       "mu0": ("bosluk gecirgenligi", "permeability", "N/A^2"),
       "n": ("birim uzunlukta sarim", "turns per length", "1/m"),
       "I": ("akim", "current", "A")},
      "solenoid|bobin manyetik alan", "solenoid|magnetic field"),
    F("tel_B", "elektrik", "Duz telin manyetik alani", "Field of a straight wire",
      "B = mu0*I/(2*pi*r)",
      {"B": ("manyetik alan", "magnetic field", "T"),
       "mu0": ("bosluk gecirgenligi", "permeability", "N/A^2"),
       "I": ("akim", "current", "A"), "r": ("uzaklik", "distance", "m")},
      "duz tel|tel manyetik alani|biot savart", "straight wire|biot savart"),
    F("faraday", "elektrik", "Faraday indukleme yasasi", "Faraday's law of induction",
      "emf = -N*dPhi/dt",
      {"emf": ("indukleme emk", "induced emf", "V"), "N": ("sarim sayisi", "turns", ""),
       "dPhi": ("aki degisimi", "flux change", "Wb"), "dt": ("sure", "time", "s")},
      "faraday|indukleme|emk", "faraday|induction|emf"),
    F("cyclotron", "elektrik", "Siklotron frekansi", "Cyclotron frequency",
      "f = q*B/(2*pi*m)",
      {"f": ("siklotron frekansi", "cyclotron frequency", "Hz"),
       "q": ("yuk", "charge", "C"), "B": ("manyetik alan", "magnetic field", "T"),
       "m": ("kutle", "mass", "kg")},
      "siklotron|manyetik alanda donme", "cyclotron frequency"),
    F("rlc", "elektrik", "RLC rezonans frekansi", "RLC resonance frequency",
      "f = 1/(2*pi*sqrt(L*C))",
      {"f": ("rezonans frekansi", "resonance frequency", "Hz"),
       "L": ("induktans", "inductance", "H"), "C": ("sigma", "capacitance", "F")},
      "rlc|rezonans|lc devresi", "rlc|resonance|lc circuit"),

    # --- Dalgalar & optik ---------------------------------------------------
    F("dalga", "dalga", "Dalga denklemi", "Wave equation",
      "v = f*lam",
      {"v": ("dalga hizi", "wave speed", "m/s"), "f": ("frekans", "frequency", "Hz"),
       "lam": ("dalga boyu", "wavelength", "m")},
      "dalga boyu|frekans hiz|dalga denklemi", "wave speed|wavelength"),
    F("snell", "optik", "Snell yasasi", "Snell's law",
      "n1*sin(t1) = n2*sin(t2)",
      {"n1": ("1. ortam kirilma indisi", "index 1", ""),
       "t1": ("gelme acisi (rad)", "incidence angle (rad)", "rad"),
       "n2": ("2. ortam kirilma indisi", "index 2", ""),
       "t2": ("kirilma acisi (rad)", "refraction angle (rad)", "rad")},
      "snell|kirilma|kirilma indisi", "snell|refraction"),
    F("mercek", "optik", "Ince mercek denklemi", "Thin lens equation",
      "1/f = 1/do + 1/di",
      {"f": ("odak uzakligi", "focal length", "m"),
       "do": ("cisim uzakligi", "object distance", "m"),
       "di": ("goruntu uzakligi", "image distance", "m")},
      "mercek|odak|ince mercek|ayna", "lens|focal length|mirror"),
    F("buyutme", "optik", "Buyutme", "Magnification",
      "M = -di/do",
      {"M": ("buyutme", "magnification", ""),
       "di": ("goruntu uzakligi", "image distance", "m"),
       "do": ("cisim uzakligi", "object distance", "m")},
      "buyutme|goruntu boyu", "magnification"),
    F("cift_yarik", "optik", "Cift yarikta girisim", "Double-slit interference",
      "d*sin(theta) = m*lam",
      {"d": ("yarik araligi", "slit separation", "m"),
       "theta": ("aci (rad)", "angle (rad)", "rad"),
       "m": ("girisim mertebesi", "order", ""),
       "lam": ("dalga boyu", "wavelength", "m")},
      "cift yarik|girisim|young", "double slit|interference|young"),
    F("kirinim", "optik", "Tek yarikta kirinim (minimum)", "Single-slit diffraction",
      "a*sin(theta) = m*lam",
      {"a": ("yarik genisligi", "slit width", "m"),
       "theta": ("aci (rad)", "angle (rad)", "rad"), "m": ("mertebe", "order", ""),
       "lam": ("dalga boyu", "wavelength", "m")},
      "kirinim|tek yarik", "diffraction|single slit"),
    F("doppler", "dalga", "Doppler olayi (ses)", "Doppler effect (sound)",
      "f = f0*(v + vo)/(v - vs)",
      # "duyulan" adi da yazili: hedef tespiti "duyulan frekans nedir"
      # sorusunda `f`yi bulamiyor, ses hizini (v) hedef saniyordu.
      {"f": ("algilanan duyulan frekans", "observed heard frequency", "Hz"),
       "f0": ("kaynak frekansi", "source frequency", "Hz"),
       "v": ("ses hizi", "sound speed", "m/s"),
       "vo": ("gozlemci hizi", "observer speed", "m/s"),
       "vs": ("kaynak hizi", "source speed", "m/s")},
      # Olculdu: "340 m/s ses hizinda 30 m/s ile YAKLASAN 1000 Hz kaynak
      # icin duyulan frekans" sorusu PERIYOT-FREKANS bagintisina gidiyordu.
      # Gunluk ifadeler ("yaklasan kaynak", "duyulan frekans") eklendi.
      "doppler|frekans kaymasi|yaklasan kaynak|uzaklasan kaynak|"
      "duyulan frekans|algilanan frekans|siren frekansi|"
      "kaynak yaklasirken frekans|hareketli kaynak frekans",
      "doppler effect|approaching source|observed frequency|siren"),
    # Yay-kutle sisteminde maksimum hiz: enerji korunumundan gelir
    # (½kx² = ½mv²), kitaplarda ayri baginti olarak verilir.
    # Basit harmonik hareketin KINEMATIGI eksikti. Olculdu: "30 m
    # genlikli, periyodu 10 s olan BHH'nin maksimum hizi" sorusuna
    # sistem Torricelli akis hizini ve kacis hizini zincirleyip
    # 24,26 m/s dedi; dogru cevap 2πA/T = 18,85 m/s. Yanlis cevap,
    # cevapsizliktan kotudur.
    # Duzgun dairesel harekette cizgisel hiz. Olculdu: "yaricapi 0.5 m,
    # periyodu 2 s dairesel hareketin cizgisel hizi" sorusunda sistem
    # yaricapi YER DEGISTIRME sanip v = dx/dt uyguladi ve 0,25 m/s dedi.
    # Dogru cevap 2πr/T = 1,57 m/s. Yaricap bir yer degistirme degildir.
    F("dairesel_hiz", "kinematik", "Duzgun dairesel harekette cizgisel hiz",
      "Linear speed in uniform circular motion",
      "v = 2*pi*r/T",
      {"v": ("cizgisel hiz", "linear speed", "m/s"),
       "r": ("yaricap", "radius", "m"),
       "T": ("periyot", "period", "s")},
      "dairesel hareket cizgisel hiz|dairesel hizi|cember uzerinde hiz|"
      "donme periyodundan hiz|tur atma hizi|yaricap periyot hiz",
      "circular motion linear speed|speed from radius and period"),
    F("bhh_acisal", "dalga", "Acisal frekans (periyottan)",
      "Angular frequency from period",
      "omega = 2*pi/T",
      {"omega": ("acisal frekans", "angular frequency", "rad/s"),
       "T": ("periyot", "period", "s")},
      "acisal frekans|omega periyot|acisal hiz periyottan|"
      "periyottan acisal frekans",
      "angular frequency|omega from period"),
    F("bhh_max_hiz", "dalga", "Basit harmonik harekette maksimum hiz",
      "Maximum speed in simple harmonic motion",
      "v = A*omega",
      {"v": ("maksimum hiz", "maximum speed", "m/s"),
       "A": ("genlik", "amplitude", "m"),
       "omega": ("acisal frekans", "angular frequency", "rad/s")},
      "basit harmonik hareket maksimum hiz|bhh maksimum hiz|"
      "genlikli harmonik hareket hizi|salinim maksimum hizi|"
      "harmonik hareket en yuksek hiz|denge noktasindaki hiz|"
      "yari capli harmonik hareket hizi",
      "maximum speed simple harmonic|shm maximum velocity|"
      "amplitude angular frequency speed"),
    F("bhh_max_ivme", "dalga", "Basit harmonik harekette maksimum ivme",
      "Maximum acceleration in simple harmonic motion",
      "a = A*omega**2",
      {"a": ("maksimum ivme", "maximum acceleration", "m/s^2"),
       "A": ("genlik", "amplitude", "m"),
       "omega": ("acisal frekans", "angular frequency", "rad/s")},
      "basit harmonik hareket maksimum ivme|bhh maksimum ivme|"
      "salinimda en buyuk ivme|uc noktadaki ivme",
      "maximum acceleration simple harmonic|shm maximum acceleration"),
    F("yay_max_hiz", "dalga", "Yay-kutle sisteminde maksimum hiz",
      "Maximum speed of a spring-mass system",
      "v = x*sqrt(k/m)",
      {"v": ("maksimum hiz", "maximum speed", "m/s"),
       "x": ("genlik", "amplitude", "m"),
       "k": ("yay sabiti", "spring constant", "N/m"),
       "m": ("kutle", "mass", "kg")},
      "yay maksimum hiz|yayin en buyuk hizi|genlikten maksimum hiz|"
      "cekilip birakilan yay hizi|salinim maksimum hizi|"
      "yaya bagli maksimum hiz",
      "maximum speed spring|amplitude maximum speed"),
    F("sarkac", "dalga", "Basit sarkac periyodu", "Simple pendulum period",
      "T = 2*pi*sqrt(L/g)",
      {"T": ("periyot", "period", "s"), "L": ("ip uzunlugu", "length", "m"),
       "g": ("yercekimi", "gravity", "m/s^2")},
      "sarkac|basit sarkac|periyot", "pendulum|period"),
    F("yay_sarkac", "dalga", "Yay-kutle periyodu", "Mass-spring period",
      "T = 2*pi*sqrt(m/k)",
      {"T": ("periyot", "period", "s"), "m": ("kutle", "mass", "kg"),
       "k": ("yay sabiti", "spring constant", "N/m")},
      "yay periyodu|harmonik hareket|shm", "spring period|shm"),
    F("ses_siddet", "dalga", "Ses siddet duzeyi", "Sound intensity level",
      "beta = 10*log(I/I0)/log(10)",
      {"beta": ("ses duzeyi", "sound level", "dB"),
       "I": ("siddet", "intensity", "W/m^2"),
       "I0": ("referans siddet (1e-12)", "reference intensity", "W/m^2")},
      "desibel|ses siddeti|db", "decibel|sound intensity"),
    F("telde_hiz", "dalga", "Gerilmis telde dalga hizi", "Wave speed on a string",
      "v = sqrt(T/mu)",
      {"v": ("dalga hizi", "wave speed", "m/s"), "T": ("gerilme kuvveti", "tension", "N"),
       "mu": ("birim boy kutle", "linear density", "kg/m")},
      "telde dalga|gerilme|tel hizi", "string wave|tension"),

    # --- Modern fizik -------------------------------------------------------
    F("foton", "kuantum", "Foton enerjisi", "Photon energy",
      "E = h*f",
      {"E": ("foton enerjisi", "photon energy", "J"),
       "h": ("Planck sabiti", "Planck constant", "J·s"),
       "f": ("frekans", "frequency", "Hz")},
      "foton|foton enerjisi|planck", "photon energy"),
    F("foton_lam", "kuantum", "Foton enerjisi (dalga boyu)", "Photon energy (wavelength)",
      "E = h*c/lam",
      {"E": ("enerji", "energy", "J"), "h": ("Planck sabiti", "Planck", "J·s"),
       "c": ("isik hizi", "light speed", "m/s"), "lam": ("dalga boyu", "wavelength", "m")},
      "foton dalga boyu|enerji dalga boyu", "photon wavelength"),
    F("fotoelektrik", "kuantum", "Fotoelektrik olay", "Photoelectric effect",
      "Ek = h*f - W",
      {"Ek": ("maks. kinetik enerji", "max kinetic energy", "J"),
       "h": ("Planck sabiti", "Planck", "J·s"), "f": ("frekans", "frequency", "Hz"),
       "W": ("is fonksiyonu", "work function", "J")},
      # Olculdu: "is fonksiyonu 2.3 eV olan metale 400 nm isik
      # dusurulurse firlayan elektronun maksimum kinetik enerjisi"
      # sorusu KINETIK ENERJI bagintisina gidiyordu ("kinetik enerji"
      # kelimeleri agir basiyordu). Fotoelektrige ozgu ifadeler eklendi.
      "fotoelektrik|is fonksiyonu|einstein|"
      "firlayan elektronun kinetik enerjisi|"
      "firlayan elektronun maksimum kinetik enerjisi|"
      "kopan elektronun enerjisi|metale isik dusurul|"
      "esik frekansi|esik dalga boyu|fotoelektron enerjisi",
      "photoelectric|work function|ejected electron kinetic energy|"
      "threshold frequency|photoemission"),
    # Dalga boyu cinsinden fotoelektrik: soru cogu zaman frekansi degil
    # DALGA BOYUNU verir (400 nm). Ara adim (f = c/lam) zincirde
    # kayboluyordu; tek denklemde yazmak hem kisa hem guvenli.
    F("fotoelektrik_lam", "kuantum",
      "Fotoelektrik olay (dalga boyu ile)",
      "Photoelectric effect (from wavelength)",
      "Ek = h*c/lam - W",
      {"Ek": ("maks. kinetik enerji", "max kinetic energy", "J"),
       "h": ("Planck sabiti", "Planck", "J·s"),
       "c": ("isik hizi", "speed of light", "m/s"),
       "lam": ("dalga boyu", "wavelength", "m"),
       "W": ("is fonksiyonu", "work function", "J")},
      "is fonksiyonu dalga boyu|nm isik dusurul|"
      "dalga boylu isikla fotoelektrik|"
      "firlayan elektronun maksimum kinetik enerjisi dalga boyu",
      "photoelectric from wavelength|work function wavelength"),
    F("debroglie", "kuantum", "de Broglie dalga boyu", "de Broglie wavelength",
      "lam = h/(m*v)",
      {"lam": ("dalga boyu", "wavelength", "m"),
       "h": ("Planck sabiti", "Planck", "J·s"), "m": ("kutle", "mass", "kg"),
       "v": ("hiz", "speed", "m/s")},
      "de broglie|madde dalgasi", "de broglie|matter wave"),
    F("belirsizlik", "kuantum", "Heisenberg belirsizlik ilkesi", "Heisenberg uncertainty",
      "dx*dp = hbar/2",
      {"dx": ("konum belirsizligi", "position uncertainty", "m"),
       "dp": ("momentum belirsizligi", "momentum uncertainty", "kg·m/s"),
       "hbar": ("indirgenmis Planck", "reduced Planck", "J·s")},
      "belirsizlik|heisenberg", "uncertainty|heisenberg"),
    F("kutu_enerji", "kuantum", "Sonsuz kuyuda enerji duzeyleri", "Particle in a box",
      "E = n**2*h**2/(8*m*L**2)",
      {"E": ("enerji duzeyi", "energy level", "J"), "n": ("kuantum sayisi", "quantum number", ""),
       "h": ("Planck sabiti", "Planck", "J·s"), "m": ("kutle", "mass", "kg"),
       "L": ("kuyu genisligi", "well width", "m")},
      "sonsuz kuyu|kutuda parcacik|enerji duzeyi", "particle in a box|infinite well"),
    F("bohr_E", "kuantum", "Bohr atomu enerji duzeyleri", "Bohr model energy levels",
      "E = -Ry*Z**2/n**2",
      {"E": ("enerji", "energy", "eV"),
       "Ry": ("Rydberg enerjisi", "Rydberg energy", "eV"),
       "Z": ("atom numarasi", "atomic number", ""),
       "n": ("bas kuantum sayisi", "principal quantum number", "")},
      "bohr|hidrojen enerji duzeyi|atom", "bohr model|hydrogen energy"),
    F("rydberg", "kuantum", "Rydberg formulu", "Rydberg formula",
      "1/lam = Rinf*Z**2*(1/n1**2 - 1/n2**2)",
      {"lam": ("dalga boyu", "wavelength", "m"),
       "Rinf": ("Rydberg sabiti", "Rydberg constant", "1/m"),
       "Z": ("atom numarasi", "atomic number", ""),
       "n1": ("alt duzey", "lower level", ""), "n2": ("ust duzey", "upper level", "")},
      "rydberg|spektral cizgi|balmer", "rydberg|spectral line|balmer"),
    F("yari_omur", "nukleer", "Radyoaktif bozunma", "Radioactive decay",
      "N = N0*exp(-log(2)*t/T)",
      {"N": ("kalan cekirdek", "remaining nuclei", ""),
       "N0": ("baslangic cekirdek", "initial nuclei", ""),
       "t": ("gecen sure", "elapsed time", "s"), "T": ("yari omur", "half-life", "s")},
      "yari omur|radyoaktif|bozunma", "half life|radioactive decay"),
    F("bozunma_sabiti", "nukleer", "Bozunma sabiti", "Decay constant",
      "lambda_ = log(2)/T",
      {"lambda_": ("bozunma sabiti", "decay constant", "1/s"),
       "T": ("yari omur", "half-life", "s")},
      "bozunma sabiti|lambda", "decay constant"),
    F("aktivite", "nukleer", "Aktivite", "Activity",
      "A = lambda_*N",
      {"A": ("aktivite", "activity", "Bq"),
       "lambda_": ("bozunma sabiti", "decay constant", "1/s"),
       "N": ("cekirdek sayisi", "number of nuclei", "")},
      "aktivite|becquerel", "activity|becquerel"),
    F("kutle_kusuru", "nukleer", "Baglanma enerjisi", "Binding energy",
      "E = dm*c**2",
      {"E": ("baglanma enerjisi", "binding energy", "J"),
       "dm": ("kutle kusuru", "mass defect", "kg"),
       "c": ("isik hizi", "light speed", "m/s")},
      "baglanma enerjisi|kutle kusuru", "binding energy|mass defect"),
    F("lorentz_gama", "gorelilik", "Lorentz carpani", "Lorentz factor",
      "gamma = 1/sqrt(1 - v**2/c**2)",
      {"gamma": ("Lorentz carpani", "Lorentz factor", ""),
       "v": ("hiz", "speed", "m/s"), "c": ("isik hizi", "light speed", "m/s")},
      "lorentz carpani|gama|gorelilik", "lorentz factor|gamma"),
    F("zaman_genlesme", "gorelilik", "Zaman genlesmesi", "Time dilation",
      "dt = dt0/sqrt(1 - v**2/c**2)",
      {"dt": ("duran gozlemcide gecen sure gozlenen sure", "dilated time", "s"),
       "dt0": ("oz sure", "proper time", "s"),
       "v": ("hiz", "speed", "m/s"), "c": ("isik hizi", "light speed", "m/s")},
      "hizla giden saatte gecen sure|duran gozlemcide ne kadar gecer|hareketli saatte gecen sure|gozlemcide gecen sure|zaman genlesmesi|zaman uzamasi", "time dilation"),
    F("boy_kisalma", "gorelilik", "Boy kisalmasi", "Length contraction",
      "L = L0*sqrt(1 - v**2/c**2)",
      {"L": ("gozlenen boy", "contracted length", "m"),
       "L0": ("oz boy", "proper length", "m"),
       "v": ("hiz", "speed", "m/s"), "c": ("isik hizi", "light speed", "m/s")},
      "boy kisalmasi|uzunluk kisalmasi", "length contraction"),
    F("rel_enerji", "gorelilik", "Gorel toplam enerji", "Relativistic energy",
      "E = m*c**2/sqrt(1 - v**2/c**2)",
      {"E": ("toplam enerji", "total energy", "J"), "m": ("durgun kutle", "rest mass", "kg"),
       "v": ("hiz", "speed", "m/s"), "c": ("isik hizi", "light speed", "m/s")},
      "gorel enerji|toplam enerji", "relativistic energy"),
    F("enerji_momentum", "gorelilik", "Enerji-momentum bagintisi", "Energy-momentum relation",
      "E**2 = (p*c)**2 + (m*c**2)**2",
      {"E": ("toplam enerji", "total energy", "J"), "p": ("momentum", "momentum", "kg·m/s"),
       "m": ("durgun kutle", "rest mass", "kg"), "c": ("isik hizi", "light speed", "m/s")},
      "enerji momentum|gorel momentum", "energy momentum relation"),

    # --- Akiskanlar ---------------------------------------------------------
    F("yogunluk", "akiskan", "Yogunluk", "Density",
      "rho = m/V",
      {"rho": ("yogunluk", "density", "kg/m^3"), "m": ("kutle", "mass", "kg"),
       "V": ("hacim", "volume", "m^3")},
      "yogunluk|ozkutle", "density"),
    F("basinc", "akiskan", "Basinc", "Pressure",
      "P = F/A",
      {"P": ("basinc", "pressure", "Pa"), "F": ("kuvvet", "force", "N"),
       "A": ("alan", "area", "m^2")},
      "basinc|kuvvet alan", "pressure"),
    F("hidrostatik", "akiskan", "Hidrostatik basinc", "Hydrostatic pressure",
      "P = rho*g*h",
      {"P": ("sivi basinci", "fluid pressure", "Pa"),
       "rho": ("yogunluk", "density", "kg/m^3"), "g": ("yercekimi", "gravity", "m/s^2"),
       "h": ("derinlik", "depth", "m")},
      "hidrostatik|sivi basinci|derinlik", "hydrostatic pressure"),
    F("arsimet", "akiskan", "Arsimet (kaldirma) kuvveti", "Buoyant force",
      "Fb = rho*g*V",
      {"Fb": ("kaldirma kuvveti", "buoyant force", "N"),
       "rho": ("sivi yogunlugu", "fluid density", "kg/m^3"),
       "g": ("yercekimi", "gravity", "m/s^2"),
       "V": ("batan hacim", "displaced volume", "m^3")},
      "arsimet|kaldirma kuvveti|yuzme", "buoyancy|archimedes"),
    F("bernoulli", "akiskan", "Bernoulli denklemi", "Bernoulli's equation",
      "P1 + rho*v1**2/2 + rho*g*h1 = P2 + rho*v2**2/2 + rho*g*h2",
      {"P1": ("1. basinc", "pressure 1", "Pa"), "P2": ("2. basinc", "pressure 2", "Pa"),
       "v1": ("1. hiz", "speed 1", "m/s"), "v2": ("2. hiz", "speed 2", "m/s"),
       "h1": ("1. yukseklik", "height 1", "m"), "h2": ("2. yukseklik", "height 2", "m"),
       "rho": ("yogunluk", "density", "kg/m^3"), "g": ("yercekimi", "gravity", "m/s^2")},
      "bernoulli|akiskan enerjisi", "bernoulli equation"),
    F("sureklilik", "akiskan", "Sureklilik denklemi", "Continuity equation",
      "A1*v1 = A2*v2",
      {"A1": ("1. kesit", "area 1", "m^2"), "v1": ("1. hiz", "speed 1", "m/s"),
       "A2": ("2. kesit", "area 2", "m^2"), "v2": ("2. hiz", "speed 2", "m/s")},
      "sureklilik|debi|kesit hiz", "continuity|flow rate"),
    F("reynolds", "akiskan", "Reynolds sayisi", "Reynolds number",
      "Re = rho*v*L/mu",
      {"Re": ("Reynolds sayisi", "Reynolds number", ""),
       "rho": ("yogunluk", "density", "kg/m^3"), "v": ("hiz", "speed", "m/s"),
       "L": ("karakteristik boyut", "characteristic length", "m"),
       "mu": ("dinamik viskozite", "dynamic viscosity", "Pa·s")},
      "reynolds|turbulans|laminer", "reynolds number|turbulence"),

    # ═══════════════════ MEKANIK (genisletme) ═══════════════════
    F("eylemsizlik_cubuk", "dinamik", "Eylemsizlik momenti (cubuk, merkez)",
      "Moment of inertia (rod, center)", "I = m*L**2/12",
      {"I": ("eylemsizlik momenti", "moment of inertia", "kg·m^2"),
       "m": ("kutle", "mass", "kg"), "L": ("uzunluk", "length", "m")},
      "eylemsizlik momenti cubuk|cubuk atalet momenti", "moment of inertia rod"),
    F("eylemsizlik_disk", "dinamik", "Eylemsizlik momenti (disk)",
      "Moment of inertia (disk)", "I = m*R**2/2",
      {"I": ("eylemsizlik momenti", "moment of inertia", "kg·m^2"),
       "m": ("kutle", "mass", "kg"), "R": ("yaricap", "radius", "m")},
      "eylemsizlik momenti disk|silindir atalet", "moment of inertia disk"),
    F("eylemsizlik_kure", "dinamik", "Eylemsizlik momenti (kure)",
      "Moment of inertia (sphere)", "I = 2*m*R**2/5",
      {"I": ("eylemsizlik momenti", "moment of inertia", "kg·m^2"),
       "m": ("kutle", "mass", "kg"), "R": ("yaricap", "radius", "m")},
      "eylemsizlik momenti kure|kure atalet", "moment of inertia sphere"),
    F("paralel_eksen", "dinamik", "Paralel eksen teoremi", "Parallel axis theorem",
      "I = Icm + m*d**2",
      {"I": ("yeni eksende atalet", "moment about new axis", "kg·m^2"),
       "Icm": ("kutle merkezinde atalet", "moment about CM", "kg·m^2"),
       "m": ("kutle", "mass", "kg"), "d": ("eksenler arasi mesafe", "axis distance", "m")},
      "paralel eksen teoremi|steiner", "parallel axis theorem|steiner"),
    F("donme_enerji", "enerji", "Donme kinetik enerjisi", "Rotational kinetic energy",
      "Ek = I*omega**2/2",
      {"Ek": ("donme kinetik enerjisi", "rotational KE", "J"),
       "I": ("eylemsizlik momenti", "moment of inertia", "kg·m^2"),
       "omega": ("acisal hiz", "angular velocity", "rad/s")},
      "donme kinetik enerjisi|donme enerjisi", "rotational kinetic energy"),
    F("yuvarlanma_enerji", "enerji", "Yuvarlanan cismin toplam enerjisi",
      "Rolling body total kinetic energy", "Ek = m*v**2*(1 + k)/2",
      {"Ek": ("toplam kinetik enerji", "total KE", "J"),
       "m": ("kutle", "mass", "kg"), "v": ("kutle merkezi hizi", "CM speed", "m/s"),
       "k": ("atalet katsayisi (I/mR^2)", "inertia factor", "")},
      "yuvarlanma|yuvarlanma enerjisi|yuvarlanan cisim|yuvarlanan kure", "rolling|rolling kinetic energy|rolling body"),
    F("kutle_merkezi", "dinamik", "Kutle merkezi (iki cisim)",
      "Center of mass (two bodies)", "xcm = (m1*x1 + m2*x2)/(m1 + m2)",
      {"xcm": ("kutle merkezi konumu", "CM position", "m"),
       "m1": ("1. kutle", "mass 1", "kg"), "x1": ("1. konum", "position 1", "m"),
       "m2": ("2. kutle", "mass 2", "kg"), "x2": ("2. konum", "position 2", "m")},
      "kutle merkezi|agirlik merkezi", "center of mass|centroid"),
    F("esnek_carpisma_v1", "dinamik", "Esnek carpisma (1. cismin son hizi)",
      "Elastic collision (final velocity 1)",
      "v1s = ((m1 - m2)*v1 + 2*m2*v2)/(m1 + m2)",
      {"v1s": ("1. cismin son hizi", "final velocity 1", "m/s"),
       "m1": ("1. kutle", "mass 1", "kg"), "m2": ("2. kutle", "mass 2", "kg"),
       "v1": ("1. ilk hiz", "initial velocity 1", "m/s"),
       "v2": ("2. ilk hiz", "initial velocity 2", "m/s")},
      "esnek carpisma|elastik carpisma|esnek carpisma hizlari|carpisma sonrasi hiz", "elastic collision|elastic collision velocity"),
    F("esnek_olmayan", "dinamik", "Tam esnek olmayan carpisma",
      "Perfectly inelastic collision", "v = (m1*v1 + m2*v2)/(m1 + m2)",
      {"v": ("ortak hiz", "common velocity", "m/s"),
       "m1": ("1. kutle", "mass 1", "kg"), "v1": ("1. hiz", "velocity 1", "m/s"),
       "m2": ("2. kutle", "mass 2", "kg"), "v2": ("2. hiz", "velocity 2", "m/s")},
      # Olculdu (taze sinav): "0,02 kg mermi 400 m/s ile 2 kg tahta
      # bloga SAPLANIRSA ortak hizlari" sorusu ISI ILETIMI bagintisina
      # gidiyordu. Carpismanin gunluk anlatimlari ("saplanir", "gomulur",
      # "yapisir") anahtarlarda yoktu.
      "esnek olmayan carpisma|plastik carpisma|ortak hiz|"
      "saplanirsa ortak hiz|bloga saplanir|mermi saplanir|"
      "gomulurse ortak hiz|yapisirsa ortak hiz|"
      "carpip birlikte hareket ederse hiz|birlikte hareket ederse ortak hiz",
      "inelastic collision|perfectly inelastic|bullet embeds|"
      "stick together common velocity"),
    F("egik_duzlem", "dinamik", "Egik duzlemde ivme (surtunmeli)",
      "Acceleration on an incline with friction",
      "a = g*(sin(theta) - mu*cos(theta))",
      {"a": ("ivme", "acceleration", "m/s^2"), "g": ("yercekimi ivmesi", "gravity", "m/s^2"),
       "theta": ("egim acisi (rad)", "incline angle (rad)", "rad"),
       "mu": ("surtunme katsayisi", "friction coefficient", "")},
      "egik duzlem|egik duzlemde ivme|ramp", "inclined plane|ramp acceleration"),
    F("merkezcil_kuvvet", "dinamik", "Merkezcil kuvvet", "Centripetal force",
      "F = m*v**2/r",
      {"F": ("merkezcil kuvvet", "centripetal force", "N"),
       "m": ("kutle", "mass", "kg"), "v": ("hiz", "speed", "m/s"),
       "r": ("yaricap", "radius", "m")},
      "merkezcil kuvvet|merkezkac kuvveti|dairesel kuvvet",
      "centripetal force|circular force"),
    F("gelgit", "dinamik", "Gelgit kuvveti (yaklasik)", "Tidal force (approximate)",
      "F = 2*G*M*m*r/d**3",
      {"F": ("gelgit kuvveti", "tidal force", "N"),
       "G": ("kutle cekim sabiti", "gravitational constant", "m^3/(kg·s^2)"),
       "M": ("cekici kutle", "attracting mass", "kg"),
       "m": ("cisim kutlesi", "body mass", "kg"),
       "r": ("cisim yaricapi", "body radius", "m"),
       "d": ("uzaklik", "distance", "m")},
      "gelgit kuvveti|tidal", "tidal force"),

    # ═══════════════════ ELEKTROMANYETIZMA (genisletme) ═══════════════════
    F("gauss_yasasi", "elektrik", "Gauss yasasi", "Gauss's law",
      "Phi = q/eps0",
      {"Phi": ("elektrik akisi", "electric flux", "V·m"),
       "q": ("kapali yuk", "enclosed charge", "C"),
       "eps0": ("bosluk elektrik gecirgenligi", "vacuum permittivity", "F/m")},
      "gauss yasasi|elektrik akisi|kapali yuzey",
      "gauss law|electric flux|closed surface"),
    F("elektrik_akisi", "elektrik", "Elektrik akisi (duzgun alan)",
      "Electric flux (uniform field)", "Phi = E*A*cos(theta)",
      {"Phi": ("elektrik akisi", "electric flux", "V·m"),
       "E": ("elektrik alan", "electric field", "V/m"),
       "A": ("yuzey alani", "area", "m^2"),
       "theta": ("aci (rad)", "angle (rad)", "rad")},
      "elektrik akisi|aki hesabi", "electric flux"),
    F("dipol_moment", "elektrik", "Elektrik dipol momenti", "Electric dipole moment",
      "p = q*d",
      {"p": ("dipol momenti", "dipole moment", "C·m"),
       "q": ("yuk", "charge", "C"), "d": ("yukler arasi mesafe", "separation", "m")},
      "elektrik dipol momenti|dipol", "electric dipole moment"),
    F("dipol_tork", "elektrik", "Dipole etkiyen tork", "Torque on a dipole",
      "tau = p*E*sin(theta)",
      {"tau": ("tork", "torque", "N·m"), "p": ("dipol momenti", "dipole moment", "C·m"),
       "E": ("elektrik alan", "electric field", "V/m"),
       "theta": ("aci (rad)", "angle (rad)", "rad")},
      "dipol tork|dipole etkiyen tork", "dipole torque"),
    F("rc_zaman", "elektrik", "RC zaman sabiti", "RC time constant",
      "tau = R*C",
      {"tau": ("zaman sabiti", "time constant", "s"),
       "R": ("direnc", "resistance", "ohm"), "C": ("sigma", "capacitance", "F")},
      "rc zaman sabiti|zaman sabiti|kondansator sarj",
      "rc time constant|charging time"),
    F("rl_zaman", "elektrik", "RL zaman sabiti", "RL time constant",
      "tau = L/R",
      {"tau": ("zaman sabiti", "time constant", "s"),
       "L": ("induktans", "inductance", "H"), "R": ("direnc", "resistance", "ohm")},
      "rl zaman sabiti|bobin zaman sabiti|kondansator dolma suresi|sarj suresi|bosalma suresi|bobin akim kararli|akim yukselme suresi", "rl time constant"),
    F("ozindukleme", "elektrik", "Ozindukleme emk", "Self-induced emf",
      "emf = L*dI/dt",
      {"emf": ("indukleme emk", "induced emf", "V"),
       "L": ("induktans", "inductance", "H"),
       "dI": ("akim degisimi", "current change", "A"),
       "dt": ("sure", "time", "s")},
      "ozindukleme|self indukleme|bobin emk", "self inductance|induced emf"),
    F("bobin_enerji", "elektrik", "Bobinde depolanan enerji", "Energy in an inductor",
      "E = L*I**2/2",
      {"E": ("depolanan enerji", "stored energy", "J"),
       "L": ("induktans", "inductance", "H"), "I": ("akim", "current", "A")},
      "bobin enerjisi|induktans enerjisi", "inductor energy"),
    F("transformator", "elektrik", "Transformator bagintisi", "Transformer relation",
      "Vs = Vp*Ns/Np",
      {"Vs": ("sekonder gerilim", "secondary voltage", "V"),
       "Vp": ("primer gerilim", "primary voltage", "V"),
       "Ns": ("sekonder sarim", "secondary turns", ""),
       "Np": ("primer sarim", "primary turns", "")},
      "transformator|trafo|sarim orani", "transformer|turns ratio"),
    F("hall", "elektrik", "Hall gerilimi", "Hall voltage",
      "VH = I*B/(n*q*t)",
      {"VH": ("hall gerilimi", "Hall voltage", "V"), "I": ("akim", "current", "A"),
       "B": ("manyetik alan", "magnetic field", "T"),
       "n": ("tasiyici yogunlugu", "carrier density", "1/m^3"),
       "q": ("tasiyici yuku", "carrier charge", "C"),
       "t": ("kalinlik", "thickness", "m")},
      "hall etkisi|hall gerilimi|tasiyici yogunlugu", "hall effect|hall voltage"),
    F("empedans_rlc", "elektrik", "Seri RLC empedansi", "Series RLC impedance",
      "Z = sqrt(R**2 + (XL - XC)**2)",
      {"Z": ("empedans", "impedance", "ohm"), "R": ("direnc", "resistance", "ohm"),
       "XL": ("indukstif reaktans", "inductive reactance", "ohm"),
       "XC": ("kapasitif reaktans", "capacitive reactance", "ohm")},
      "empedans|rlc empedans|ac direnc", "impedance|ac resistance"),
    F("reaktans_L", "elektrik", "Indukstif reaktans", "Inductive reactance",
      "XL = 2*pi*f*L",
      {"XL": ("indukstif reaktans", "inductive reactance", "ohm"),
       "f": ("frekans", "frequency", "Hz"), "L": ("induktans", "inductance", "H")},
      "indukstif reaktans|bobin reaktansi", "inductive reactance"),
    F("reaktans_C", "elektrik", "Kapasitif reaktans", "Capacitive reactance",
      "XC = 1/(2*pi*f*C)",
      {"XC": ("kapasitif reaktans", "capacitive reactance", "ohm"),
       "f": ("frekans", "frequency", "Hz"), "C": ("sigma", "capacitance", "F")},
      "kapasitif reaktans|kondansator reaktansi", "capacitive reactance"),
    F("guc_faktoru", "elektrik", "AC ortalama guc", "AC average power",
      "P = V*I*cos(phi)",
      {"P": ("ortalama guc", "average power", "W"),
       "V": ("etkin gerilim", "rms voltage", "V"),
       "I": ("etkin akim", "rms current", "A"),
       "phi": ("faz acisi (rad)", "phase angle (rad)", "rad")},
      "guc faktoru|ac guc|etkin guc", "power factor|ac power"),
    F("poynting", "elektrik", "Poynting vektoru (buyukluk)", "Poynting vector magnitude",
      "S = E*B/mu0",
      {"S": ("enerji akisi", "energy flux", "W/m^2"),
       "E": ("elektrik alan", "electric field", "V/m"),
       "B": ("manyetik alan", "magnetic field", "T"),
       "mu0": ("bosluk manyetik gecirgenligi", "vacuum permeability", "N/A^2")},
      "poynting vektoru|enerji akisi|isima siddeti", "poynting vector|energy flux"),

    # ═══════════════════ TERMODINAMIK (genisletme) ═══════════════════
    F("izotermal_is", "termodinamik", "Izotermal iste yapilan is",
      "Isothermal work", "W = n*R*T*log(V2/V1)",
      {"W": ("yapilan is", "work done", "J"), "n": ("mol sayisi", "moles", "mol"),
       "R": ("gaz sabiti", "gas constant", "J/(mol·K)"),
       "T": ("sicaklik", "temperature", "K"),
       "V1": ("ilk hacim", "initial volume", "m^3"),
       "V2": ("son hacim", "final volume", "m^3")},
      "izotermal is|sabit sicaklikta is", "isothermal work"),
    F("adyabatik", "termodinamik", "Adyabatik surec", "Adiabatic process",
      "P1*V1**gam = P2*V2**gam",
      {"P1": ("ilk basinc", "initial pressure", "Pa"),
       "V1": ("ilk hacim", "initial volume", "m^3"),
       "P2": ("son basinc", "final pressure", "Pa"),
       "V2": ("son hacim", "final volume", "m^3"),
       "gam": ("adyabatik us (Cp/Cv)", "adiabatic index", "")},
      "adyabatik|adyabatik surec|izentropik|hizli sikistirma|aniden sikistirma|isi alisverisi olmadan|pompa isinmasi", "adiabatic process|isentropic"),
    F("entalpi", "termodinamik", "Entalpi", "Enthalpy", "H = U + P*V",
      {"H": ("entalpi", "enthalpy", "J"), "U": ("ic enerji", "internal energy", "J"),
       "P": ("basinc", "pressure", "Pa"), "V": ("hacim", "volume", "m^3")},
      "entalpi|isi icerigi", "enthalpy"),
    F("gibbs", "termodinamik", "Gibbs serbest enerjisi", "Gibbs free energy",
      "G = H - T*S",
      {"G": ("gibbs serbest enerjisi", "Gibbs free energy", "J"),
       "H": ("entalpi", "enthalpy", "J"), "T": ("sicaklik", "temperature", "K"),
       "S": ("entropi", "entropy", "J/K")},
      "gibbs serbest enerjisi|serbest enerji|kendiliginden",
      "gibbs free energy|spontaneity"),
    F("helmholtz", "termodinamik", "Helmholtz serbest enerjisi",
      "Helmholtz free energy", "A = U - T*S",
      {"A": ("helmholtz enerjisi", "Helmholtz energy", "J"),
       "U": ("ic enerji", "internal energy", "J"),
       "T": ("sicaklik", "temperature", "K"), "S": ("entropi", "entropy", "J/K")},
      "helmholtz serbest enerjisi", "helmholtz free energy"),
    F("isi_pompasi", "termodinamik", "Isi pompasi etkinlik katsayisi",
      "Heat pump COP", "COP = Th/(Th - Tc)",
      {"COP": ("etkinlik katsayisi", "coefficient of performance", ""),
       "Th": ("sicak kaynak", "hot reservoir", "K"),
       "Tc": ("soguk kaynak", "cold reservoir", "K")},
      "isi pompasi|etkinlik katsayisi|cop", "heat pump|coefficient of performance"),
    F("sogutma_cop", "termodinamik", "Sogutucu etkinlik katsayisi",
      "Refrigerator COP", "COP = Tc/(Th - Tc)",
      {"COP": ("sogutma etkinligi", "cooling COP", ""),
       "Tc": ("soguk kaynak", "cold reservoir", "K"),
       "Th": ("sicak kaynak", "hot reservoir", "K")},
      "sogutucu|sogutma verimi|buzdolabi", "refrigerator cop|cooling"),
    F("serbest_yol", "termodinamik", "Ortalama serbest yol", "Mean free path",
      "lam = kB*T/(sqrt(2)*pi*d**2*P)",
      {"lam": ("ortalama serbest yol", "mean free path", "m"),
       "kB": ("Boltzmann sabiti", "Boltzmann constant", "J/K"),
       "T": ("sicaklik", "temperature", "K"),
       "d": ("molekul capi", "molecular diameter", "m"),
       "P": ("basinc", "pressure", "Pa")},
      "ortalama serbest yol|serbest yol", "mean free path"),
    F("van_der_waals", "termodinamik", "Van der Waals denklemi",
      "Van der Waals equation", "P = n*R*T/(V - n*b) - a*n**2/V**2",
      {"P": ("basinc", "pressure", "Pa"), "n": ("mol sayisi", "moles", "mol"),
       "R": ("gaz sabiti", "gas constant", "J/(mol·K)"),
       "T": ("sicaklik", "temperature", "K"), "V": ("hacim", "volume", "m^3"),
       "a": ("cekim duzeltmesi", "attraction term", "Pa·m^6/mol^2"),
       "b": ("hacim duzeltmesi", "volume term", "m^3/mol")},
      "van der waals|gercek gaz", "van der waals|real gas"),
    F("molar_isi", "termodinamik", "Molar isi kapasitesi", "Molar heat capacity",
      "Q = n*Cm*dT",
      {"Q": ("isi", "heat", "J"), "n": ("mol sayisi", "moles", "mol"),
       "Cm": ("molar isi kapasitesi", "molar heat capacity", "J/(mol·K)"),
       "dT": ("sicaklik degisimi", "temperature change", "K")},
      "molar isi kapasitesi|mol basina isi", "molar heat capacity"),

    # ═══════════════════ KUANTUM / MODERN (genisletme) ═══════════════════
    F("harmonik_kuantum", "kuantum", "Kuantum harmonik osilator enerjisi",
      "Quantum harmonic oscillator energy", "E = hbar*omega*(n + 0.5)",
      {"E": ("enerji duzeyi", "energy level", "J"),
       "hbar": ("indirgenmis Planck sabiti", "reduced Planck constant", "J·s"),
       "omega": ("acisal frekans", "angular frequency", "rad/s"),
       "n": ("kuantum sayisi", "quantum number", "")},
      "harmonik osilator enerjisi|kuantum osilator",
      "quantum harmonic oscillator|zero point energy"),
    F("compton", "kuantum", "Compton kaymasi", "Compton shift",
      "dlam = h*(1 - cos(theta))/(me*c)",
      {"dlam": ("dalga boyu kaymasi", "wavelength shift", "m"),
       "h": ("Planck sabiti", "Planck constant", "J·s"),
       "theta": ("sacilma acisi (rad)", "scattering angle (rad)", "rad"),
       "me": ("elektron kutlesi", "electron mass", "kg"),
       "c": ("isik hizi", "speed of light", "m/s")},
      "compton kaymasi|compton sacilmasi", "compton shift|compton scattering"),
    F("belirsizlik_enerji", "kuantum", "Enerji-zaman belirsizligi",
      "Energy-time uncertainty", "dE*dt = hbar/2",
      {"dE": ("enerji belirsizligi", "energy uncertainty", "J"),
       "dt": ("zaman belirsizligi", "time uncertainty", "s"),
       "hbar": ("indirgenmis Planck sabiti", "reduced Planck constant", "J·s")},
      "enerji zaman belirsizligi|omur genislik",
      "energy time uncertainty|lifetime broadening"),
    F("fermi_enerji", "katihal", "Fermi enerjisi (serbest elektron)",
      "Fermi energy (free electron gas)",
      "EF = hbar**2*(3*pi**2*n)**(2/3)/(2*me)",
      {"EF": ("fermi enerjisi", "Fermi energy", "J"),
       "hbar": ("indirgenmis Planck sabiti", "reduced Planck constant", "J·s"),
       "n": ("elektron yogunlugu", "electron density", "1/m^3"),
       "me": ("elektron kutlesi", "electron mass", "kg")},
      "fermi enerjisi|serbest elektron gazi", "fermi energy|free electron gas"),
    F("spin_moment", "kuantum", "Spin manyetik momenti", "Spin magnetic moment",
      "mu = g*muB*ms",
      {"mu": ("manyetik moment", "magnetic moment", "J/T"),
       "g": ("g carpani", "g-factor", ""),
       "muB": ("Bohr magnetonu", "Bohr magneton", "J/T"),
       "ms": ("spin kuantum sayisi", "spin quantum number", "")},
      "spin manyetik moment|manyetik moment", "spin magnetic moment"),
    F("zeeman", "kuantum", "Zeeman enerji yarilmasi", "Zeeman energy splitting",
      "dE = muB*B*mj",
      {"dE": ("enerji yarilmasi", "energy splitting", "J"),
       "muB": ("Bohr magnetonu", "Bohr magneton", "J/T"),
       "B": ("manyetik alan", "magnetic field", "T"),
       "mj": ("manyetik kuantum sayisi", "magnetic quantum number", "")},
      "zeeman|enerji yarilmasi|manyetik alanda cizgi",
      "zeeman effect|energy splitting"),

    # ═══════════════════ OPTIK (genisletme) ═══════════════════
    F("bragg", "optik", "Bragg yasasi", "Bragg's law", "n*lam = 2*d*sin(theta)",
      {"n": ("kirinim mertebesi", "diffraction order", ""),
       "lam": ("dalga boyu", "wavelength", "m"),
       "d": ("duzlemler arasi mesafe", "plane spacing", "m"),
       "theta": ("bragg acisi (rad)", "Bragg angle (rad)", "rad")},
      "bragg yasasi|x isini kirinimi|kristal duzlem",
      "bragg law|x-ray diffraction|crystal planes"),
    F("rayleigh", "optik", "Rayleigh cozunurluk olcutu", "Rayleigh criterion",
      "theta = 1.22*lam/D",
      {"theta": ("en kucuk ayirt edilebilir aci (rad)",
                 "minimum resolvable angle (rad)|ayrinti secme|en kucuk ayrinti|netlik siniri|goru keskinligi", "rad"),
       "lam": ("dalga boyu", "wavelength", "m"),
       "D": ("acikliK capi", "aperture diameter", "m")},
      "rayleigh cozunurluk|ayirma gucu|teleskop cozunurluk",
      "rayleigh criterion|resolving power"),
    F("brewster", "optik", "Brewster acisi", "Brewster's angle",
      "tan(thB) = n2/n1",
      {"thB": ("brewster acisi (rad)", "Brewster angle (rad)", "rad"),
       "n1": ("1. ortam indisi", "index 1", ""),
       "n2": ("2. ortam indisi", "index 2", "")},
      "brewster acisi|polarizasyon acisi", "brewster angle|polarizing angle"),
    F("malus", "optik", "Malus yasasi", "Malus's law", "I = I0*cos(theta)**2",
      {"I": ("gecen siddet", "transmitted intensity", "W/m^2"),
       "I0": ("gelen siddet", "incident intensity", "W/m^2"),
       "theta": ("polarizor acisi (rad)", "polarizer angle (rad)", "rad")},
      "malus yasasi|polarizor|polarize isik", "malus law|polarizer"),
    F("mercek_yapimci", "optik", "Mercek yapimcisi denklemi", "Lensmaker's equation",
      "1/f = (n - 1)*(1/R1 - 1/R2)",
      {"f": ("odak uzakligi", "focal length", "m"),
       "n": ("kirilma indisi", "refractive index", ""),
       "R1": ("1. yuzey yaricapi", "radius 1", "m"),
       "R2": ("2. yuzey yaricapi", "radius 2", "m")},
      "mercek yapimcisi|lensmaker|mercek yaricap",
      "lensmaker equation|lens radii"),
    F("teleskop", "optik", "Teleskop buyutmesi", "Telescope magnification",
      "M = fo/fe",
      {"M": ("buyutme", "magnification", ""),
       "fo": ("objektif odak uzakligi", "objective focal length", "m"),
       "fe": ("goz merceği odak uzakligi", "eyepiece focal length", "m")},
      "teleskop buyutmesi|durbun buyutme", "telescope magnification"),
    F("kritik_aci", "optik", "Tam yansima kritik acisi", "Critical angle",
      "sin(thc) = n2/n1",
      {"thc": ("kritik aci (rad)", "critical angle (rad)", "rad"),
       "n1": ("yogun ortam indisi", "denser index", ""),
       "n2": ("seyrek ortam indisi", "rarer index", "")},
      "kritik aci|tam yansima|fiber optik",
      "critical angle|total internal reflection"),

    # ═══════════════════ DALGA (genisletme) ═══════════════════
    F("tel_harmonik", "dalga", "Gerilmis telde harmonikler", "String harmonics",
      "f = n*v/(2*L)",
      {"f": ("harmonik frekansi", "harmonic frequency", "Hz"),
       "n": ("harmonik mertebesi", "harmonic number", ""),
       "v": ("dalga hizi", "wave speed", "m/s"),
       "L": ("tel uzunlugu", "string length", "m")},
      "telde harmonik|duran dalga frekansi|gitar teli",
      "string harmonics|standing wave frequency"),
    F("org_acik", "dalga", "Acik org borusu frekansi", "Open pipe frequency",
      "f = n*v/(2*L)",
      {"f": ("frekans", "frequency", "Hz"), "n": ("mertebe", "harmonic number", ""),
       "v": ("ses hizi", "sound speed", "m/s"), "L": ("boru boyu", "pipe length", "m")},
      "acik org borusu|acik boru|ucu acik", "open pipe|open organ pipe"),
    F("org_kapali", "dalga", "Kapali org borusu frekansi", "Closed pipe frequency",
      "f = n*v/(4*L)",
      {"f": ("frekans", "frequency", "Hz"),
       "n": ("tek mertebe (1,3,5...)", "odd harmonic", ""),
       "v": ("ses hizi", "sound speed", "m/s"), "L": ("boru boyu", "pipe length", "m")},
      "kapali org borusu|kapali boru|tek harmonik", "closed pipe|stopped pipe"),
    F("vurum", "dalga", "Vurum frekansi", "Beat frequency", "fb = f1 - f2",
      {"fb": ("vurum frekansi", "beat frequency", "Hz"),
       "f1": ("1. frekans", "frequency 1", "Hz"),
       "f2": ("2. frekans", "frequency 2", "Hz")},
      "vurum frekansi|beat|akort", "beat frequency|tuning"),
    F("sonum_orani", "dalga", "Sonum orani", "Damping ratio",
      "zeta = b/(2*sqrt(m*k))",
      {"zeta": ("sonum orani", "damping ratio", ""),
       "b": ("sonum katsayisi", "damping coefficient", "kg/s"),
       "m": ("kutle", "mass", "kg"), "k": ("yay sabiti", "spring constant", "N/m")},
      "sonum orani|kritik sonum|zeta", "damping ratio|critical damping"),
    F("mach", "dalga", "Mach sayisi", "Mach number", "Ma = v/a",
      {"Ma": ("mach sayisi", "Mach number", ""),
       "v": ("cisim hizi", "object speed", "m/s"),
       "a": ("ses hizi", "sound speed", "m/s")},
      "mach sayisi|ses hizi orani|sok dalgasi", "mach number|shock wave"),
    F("ses_hizi_gaz", "dalga", "Gazda ses hizi", "Speed of sound in a gas",
      "v = sqrt(gam*R*T/M)",
      {"v": ("ses hizi", "sound speed", "m/s"),
       "gam": ("adyabatik us", "adiabatic index", ""),
       "R": ("gaz sabiti", "gas constant", "J/(mol·K)"),
       "T": ("sicaklik", "temperature", "K"),
       "M": ("molar kutle", "molar mass", "kg/mol")},
      "gazda ses hizi|ses hizi sicaklik", "speed of sound in gas"),

    # ═══════════════════ KATIHAL ═══════════════════
    F("iletkenlik", "katihal", "Elektriksel iletkenlik", "Electrical conductivity",
      "sig = n*q*mob",
      {"sig": ("iletkenlik", "conductivity", "S/m"),
       "n": ("tasiyici yogunlugu", "carrier density", "1/m^3"),
       "q": ("tasiyici yuku", "carrier charge", "C"),
       "mob": ("mobilite", "mobility", "m^2/(V·s)")},
      "iletkenlik|ozdirenc tersi|tasiyici mobilite",
      "conductivity|carrier mobility"),
    F("hall_katsayisi", "katihal", "Hall katsayisi", "Hall coefficient",
      "RH = 1/(n*q)",
      {"RH": ("hall katsayisi", "Hall coefficient", "m^3/C"),
       "n": ("tasiyici yogunlugu", "carrier density", "1/m^3"),
       "q": ("tasiyici yuku", "carrier charge", "C")},
      "hall katsayisi|tasiyici isareti", "hall coefficient"),
    F("surukleme_hizi", "katihal", "Surukleme hizi", "Drift velocity",
      "vd = I/(n*A*q)",
      {"vd": ("surukleme hizi", "drift velocity", "m/s"),
       "I": ("akim", "current", "A"),
       "n": ("tasiyici yogunlugu", "carrier density", "1/m^3"),
       "A": ("kesit alani", "cross-section", "m^2"),
       "q": ("tasiyici yuku", "carrier charge", "C")},
      "surukleme hizi|drift hizi|elektron hizi", "drift velocity"),

    # ═══════════════════ ASTROFIZIK ═══════════════════
    F("ters_kare_isik", "astro", "Isik siddeti - uzaklik (ters kare)",
      "Inverse square law for light", "F = L/(4*pi*d**2)",
      {"F": ("gozlenen akı", "observed flux", "W/m^2"),
       "L": ("gercek isima gucu", "luminosity", "W"),
       "d": ("uzaklik", "distance", "m")},
      "ters kare yasasi|isik siddeti uzaklik|aki parlaklik",
      "inverse square law|flux luminosity"),
    F("kadir", "astro", "Kadir farki - parlaklik orani",
      "Magnitude difference", "dm = -2.5*log(F1/F2)/log(10)",
      {"dm": ("kadir farki", "magnitude difference", ""),
       "F1": ("1. akı", "flux 1", "W/m^2"), "F2": ("2. akı", "flux 2", "W/m^2")},
      "kadir|parlaklik kadir|magnitud", "magnitude|apparent magnitude"),
    F("uzaklik_modulu", "astro", "Uzaklik modulu", "Distance modulus",
      # Referans uzaklik acikca yazildi: "10" ciplak bir sayi degil, 10 parsek.
      # Aksi halde logaritmanin icinde boyutlu bir nicelik kalirdi.
      "mM = 5*log(d/d0)/log(10)",
      {"mM": ("uzaklik modulu (m-M)", "distance modulus", ""),
       "d": ("uzaklik", "distance", "pc"),
       "d0": ("referans uzaklik (10 pc)", "reference distance (10 pc)", "pc")},
      "uzaklik modulu|gorunen mutlak kadir", "distance modulus"),
    F("hubble", "astro", "Hubble-Lemaitre yasasi", "Hubble-Lemaitre law",
      "v = H0*d",
      {"v": ("uzaklasma hizi", "recession velocity", "m/s"),
       "H0": ("Hubble sabiti", "Hubble constant", "1/s"),
       "d": ("uzaklik", "distance", "m")},
      "hubble yasasi|uzaklasma hizi|evrenin genislemesi",
      "hubble law|recession velocity"),
    F("kirmizi_kayma", "astro", "Kirmizi kayma", "Redshift",
      "z = (lobs - lem)/lem",
      {"z": ("kirmizi kayma", "redshift", ""),
       "lobs": ("gozlenen dalga boyu", "observed wavelength", "m"),
       "lem": ("yayilan dalga boyu", "emitted wavelength", "m")},
      "kirmizi kayma|redshift|dalga boyu kaymasi", "redshift|wavelength shift"),
    F("jeans", "astro", "Jeans kutlesi (yaklasik)", "Jeans mass (approximate)",
      "MJ = (5*kB*T/(G*mu_m))**1.5*(3/(4*pi*rho))**0.5",
      {"MJ": ("jeans kutlesi", "Jeans mass", "kg"),
       "kB": ("Boltzmann sabiti", "Boltzmann constant", "J/K"),
       "T": ("sicaklik", "temperature", "K"),
       "G": ("kutle cekim sabiti", "gravitational constant", "m^3/(kg·s^2)"),
       "mu_m": ("ortalama parcacik kutlesi", "mean particle mass", "kg"),
       "rho": ("yogunluk", "density", "kg/m^3")},
      "jeans kutlesi|yildiz olusumu|bulut cokmesi",
      "jeans mass|star formation|cloud collapse"),

    # ═══════════════════ AKISKANLAR (genisletme) ═══════════════════
    F("torricelli_akis", "akiskan", "Torricelli akis hizi", "Torricelli's law",
      "v = sqrt(2*g*h)",
      {"v": ("cikis hizi", "efflux speed", "m/s"),
       "g": ("yercekimi ivmesi", "gravity", "m/s^2"),
       "h": ("sivi yuksekligi", "liquid height", "m")},
      "torricelli akis|delikten akis|bosalma hizi", "torricelli law|efflux"),
    F("poiseuille", "akiskan", "Poiseuille debisi", "Poiseuille flow rate",
      "Q = pi*dP*r**4/(8*mu*L)",
      {"Q": ("hacimsel debi", "volumetric flow", "m^3/s"),
       "dP": ("basinc farki", "pressure difference", "Pa"),
       "r": ("boru yaricapi", "pipe radius", "m"),
       "mu": ("dinamik viskozite", "dynamic viscosity", "Pa·s"),
       "L": ("boru uzunlugu", "pipe length", "m")},
      "poiseuille|laminer boru akisi|debi yaricap",
      "poiseuille|laminar pipe flow"),
    F("stokes", "akiskan", "Stokes surukleme kuvveti", "Stokes drag",
      "F = 6*pi*mu*r*v",
      {"F": ("surukleme kuvveti", "drag force", "N"),
       "mu": ("dinamik viskozite", "dynamic viscosity", "Pa·s"),
       "r": ("kure yaricapi", "sphere radius", "m"),
       "v": ("hiz", "speed", "m/s")},
      "stokes surukleme|viskoz direnc|kure direnci", "stokes drag|viscous drag"),
    F("surukleme_kuvveti", "akiskan", "Aerodinamik surukleme", "Aerodynamic drag",
      "F = Cd*rho*A*v**2/2",
      {"F": ("surukleme kuvveti", "drag force", "N"),
       "Cd": ("surukleme katsayisi", "drag coefficient", ""),
       "rho": ("akiskan yogunlugu", "fluid density", "kg/m^3"),
       "A": ("kesit alani", "frontal area", "m^2"),
       "v": ("hiz", "speed", "m/s")},
      "hava direnci|surukleme kuvveti|aerodinamik direnc",
      "drag force|air resistance"),
    F("kaldirma_kuvveti_kanat", "akiskan", "Kanat kaldirma kuvveti", "Lift force",
      "L = Cl*rho*A*v**2/2",
      {"L": ("kaldirma kuvveti", "lift force", "N"),
       "Cl": ("kaldirma katsayisi", "lift coefficient", ""),
       "rho": ("hava yogunlugu", "air density", "kg/m^3"),
       "A": ("kanat alani", "wing area", "m^2"),
       "v": ("hiz", "speed", "m/s")},
      "kaldirma kuvveti|ucak kanadi|lift", "lift force|wing"),
    F("yuzey_gerilimi", "akiskan", "Kilcal yukselme", "Capillary rise",
      "h = 2*gam*cos(theta)/(rho*g*r)",
      {"h": ("kilcal yukselme", "capillary rise", "m"),
       "gam": ("yuzey gerilimi", "surface tension", "N/m"),
       "theta": ("temas acisi (rad)", "contact angle (rad)", "rad"),
       "rho": ("yogunluk", "density", "kg/m^3"),
       "g": ("yercekimi", "gravity", "m/s^2"),
       "r": ("kilcal yaricap", "capillary radius", "m")},
      "kilcal yukselme|yuzey gerilimi|kapiler", "capillary rise|surface tension"),

    # ═══════════════════ TERMODINAMIK CEVRIMLERI ═══════════════════
    F("otto", "termodinamik", "Otto cevrimi verimi", "Otto cycle efficiency",
      "eta = 1 - 1/rc**(gam - 1)",
      {"eta": ("verim", "efficiency", ""),
       "rc": ("sikistirma orani", "compression ratio", ""),
       "gam": ("adyabatik us", "adiabatic index", "")},
      "otto cevrimi|benzinli motor verimi|sikistirma orani",
      "otto cycle|gasoline engine efficiency"),
    F("stefan_wien_tepe", "termodinamik", "Kara cisim tepe frekansi",
      # 5.879e10 ciplak bir sayi degil, birimi Hz/K olan Wien frekans sabiti
      "Blackbody peak frequency", "f = bWf*T",
      {"f": ("tepe frekansi", "peak frequency", "Hz"),
       "bWf": ("Wien frekans sabiti", "Wien frequency constant", "Hz/K"),
       "T": ("sicaklik", "temperature", "K")},
      "tepe frekansi|kara cisim frekans", "peak frequency|blackbody"),
    F("isi_tasinim", "termodinamik", "Tasinimla isi transferi (Newton)",
      "Convective heat transfer", "Q = h*A*dT*t",
      {"Q": ("aktarilan isi", "heat transferred", "J"),
       "h": ("tasinim katsayisi", "convection coefficient", "W/(m^2·K)"),
       "A": ("yuzey alani", "area", "m^2"),
       "dT": ("sicaklik farki", "temperature difference", "K"),
       "t": ("sure", "time", "s")},
      "tasinim|konveksiyon|newton soguma", "convection|newton cooling"),
    F("termal_genlesme", "termodinamik", "Boyca isil genlesme",
      "Linear thermal expansion", "dL = alpha*L0*dT",
      {"dL": ("uzunluk degisimi", "length change", "m"),
       "alpha": ("isil genlesme katsayisi", "expansion coefficient", "1/K"),
       "L0": ("ilk uzunluk", "initial length", "m"),
       "dT": ("sicaklik degisimi", "temperature change", "K")},
      "isil genlesme|termal genlesme|boyca uzama",
      "thermal expansion|linear expansion"),

    # ═══════════════════ NUKLEER (genisletme) ═══════════════════
    F("kutle_enerji_mev", "nukleer", "Kutle kusuru - enerji (u -> MeV)",
      # 931.494 sayisi, 1 atomik kutle biriminin MeV karsiligidir
      "Mass defect to energy", "E = dm*uMeV/u_",
      {"E": ("baglanma enerjisi", "binding energy", "MeV"),
       "dm": ("kutle kusuru", "mass defect", "u"),
       "uMeV": ("atomik kutle biriminin enerji karsiligi",
                "atomic mass unit energy equivalent", "MeV"),
       "u_": ("bir atomik kutle birimi", "one atomic mass unit", "u")},
      "kutle kusuru mev|baglanma enerjisi hesabi|931",
      "mass defect mev|binding energy calculation"),
    F("nukleon_basina", "nukleer", "Nukleon basina baglanma enerjisi",
      "Binding energy per nucleon", "Eb = E/A",
      {"Eb": ("nukleon basina enerji", "energy per nucleon", "MeV"),
       "E": ("toplam baglanma enerjisi", "total binding energy", "MeV"),
       "A": ("kutle numarasi", "mass number", "")},
      "nukleon basina baglanma|ortalama baglanma",
      "binding energy per nucleon"),
    F("cekirdek_yaricap", "nukleer", "Cekirdek yaricapi", "Nuclear radius",
      "R = r0*A**(1/3)",
      {"R": ("cekirdek yaricapi", "nuclear radius", "m"),
       "r0": ("yaricap sabiti (1.2 fm)", "radius constant", "m"),
       "A": ("kutle numarasi", "mass number", "")},
      "cekirdek yaricapi|nukleer yaricap", "nuclear radius"),
    F("sogurma", "nukleer", "Isin sogurma yasasi", "Radiation attenuation",
      "I = I0*exp(-mu_a*x)",
      {"I": ("cikan siddet", "transmitted intensity", "W/m^2"),
       "I0": ("gelen siddet", "incident intensity", "W/m^2"),
       "mu_a": ("sogurma katsayisi", "attenuation coefficient", "1/m"),
       "x": ("kalinlik", "thickness", "m")},
      "sogurma|zayiflama|yariya dusme kalinligi",
      "attenuation|absorption|half value layer"),
    F("doz", "nukleer", "Sogurulan doz", "Absorbed dose", "D = E/m",
      {"D": ("sogurulan doz", "absorbed dose", "Gy"),
       "E": ("sogurulan enerji", "absorbed energy", "J"),
       "m": ("kutle", "mass", "kg")},
      "sogurulan doz|gray|radyasyon dozu", "absorbed dose|gray"),

    # ═══════════════════ PLAZMA ═══════════════════
    F("debye", "plazma", "Debye uzunlugu", "Debye length",
      "lam = sqrt(eps0*kB*T/(n*e**2))",
      {"lam": ("debye uzunlugu", "Debye length", "m"),
       "eps0": ("bosluk elektrik gecirgenligi", "vacuum permittivity", "F/m"),
       "kB": ("Boltzmann sabiti", "Boltzmann constant", "J/K"),
       "T": ("sicaklik", "temperature", "K"),
       "n": ("elektron yogunlugu", "electron density", "1/m^3"),
       "e": ("temel yuk", "elementary charge", "C")},
      "debye uzunlugu|plazma perdeleme", "debye length|plasma screening"),
    F("plazma_frekans", "plazma", "Plazma frekansi", "Plasma frequency",
      "wp = sqrt(n*e**2/(eps0*me))",
      {"wp": ("plazma acisal frekansi", "plasma angular frequency", "rad/s"),
       "n": ("elektron yogunlugu", "electron density", "1/m^3"),
       "e": ("temel yuk", "elementary charge", "C"),
       "eps0": ("bosluk elektrik gecirgenligi", "vacuum permittivity", "F/m"),
       "me": ("elektron kutlesi", "electron mass", "kg")},
      "plazma frekansi|elektron salinim frekansi", "plasma frequency"),
    F("larmor", "plazma", "Larmor (siklotron) yaricapi", "Larmor radius",
      "rL = m*v/(q*B)",
      {"rL": ("larmor yaricapi", "Larmor radius", "m"),
       "m": ("parcacik kutlesi", "particle mass", "kg"),
       "v": ("dik hiz bileseni", "perpendicular speed", "m/s"),
       "q": ("yuk", "charge", "C"),
       "B": ("manyetik alan", "magnetic field", "T")},
      "larmor yaricapi|siklotron yaricapi|gyroradius",
      "larmor radius|gyroradius"),

    # ═══════════════════ AKUSTIK / ELEKTRONIK ═══════════════════
    F("ses_basinc_duzeyi", "dalga", "Ses basinc duzeyi", "Sound pressure level",
      "Lp = 20*log(p/p0)/log(10)",
      {"Lp": ("ses basinc duzeyi", "sound pressure level", "dB"),
       "p": ("ses basinci", "sound pressure", "Pa"),
       "p0": ("referans basinc (20 uPa)", "reference pressure", "Pa")},
      "ses basinc duzeyi|desibel basinc|spl", "sound pressure level|spl"),
    F("akustik_empedans", "dalga", "Akustik empedans", "Acoustic impedance",
      "Z = rho*v",
      {"Z": ("akustik empedans", "acoustic impedance", "Pa·s/m"),
       "rho": ("ortam yogunlugu", "medium density", "kg/m^3"),
       "v": ("ses hizi", "sound speed", "m/s")},
      "akustik empedans|ses empedansi", "acoustic impedance"),
    F("gerilim_bolucu", "elektrik", "Gerilim bolucu", "Voltage divider",
      "Vout = Vin*R2/(R1 + R2)",
      {"Vout": ("cikis gerilimi", "output voltage", "V"),
       "Vin": ("giris gerilimi", "input voltage", "V"),
       "R1": ("1. direnc", "resistance 1", "ohm"),
       "R2": ("2. direnc", "resistance 2", "ohm")},
      "gerilim bolucu|voltaj bolucu|dirençle bolme",
      "voltage divider|potential divider"),
    F("kesim_frekansi", "elektrik", "RC alcak geciren kesim frekansi",
      "RC low-pass cutoff frequency", "fc = 1/(2*pi*R*C)",
      {"fc": ("kesim frekansi", "cutoff frequency", "Hz"),
       "R": ("direnc", "resistance", "ohm"), "C": ("sigma", "capacitance", "F")},
      "kesim frekansi|alcak geciren|filtre frekansi",
      "cutoff frequency|low pass filter"),
    F("kalite_faktoru", "elektrik", "RLC kalite faktoru", "RLC quality factor",
      "Q = sqrt(L/C)/R",
      {"Q": ("kalite faktoru", "quality factor", ""),
       "L": ("induktans", "inductance", "H"),
       "C": ("sigma", "capacitance", "F"),
       "R": ("direnc", "resistance", "ohm")},
      "kalite faktoru|q faktoru|rezonans keskinligi",
      "quality factor|q factor|resonance sharpness"),

    # ═══════════════════ MALZEME / KATIHAL (genisletme) ═══════════════════
    F("young", "katihal", "Young modulu (gerilme-birim uzama)",
      "Young's modulus", "E = (F/A)/(dL/L0)",
      {"E": ("young modulu", "Young's modulus", "Pa"),
       "F": ("uygulanan kuvvet", "applied force", "N"),
       "A": ("kesit alani", "cross-section", "m^2"),
       "dL": ("uzama", "elongation", "m"),
       "L0": ("ilk uzunluk", "original length", "m")},
      "young modulu|elastisite modulu|gerilme birim uzama",
      "young modulus|elastic modulus|stress strain"),
    F("kayma_modulu", "katihal", "Kayma modulu", "Shear modulus",
      "G = (F/A)/(dx/L)",
      {"G": ("kayma modulu", "shear modulus", "Pa"),
       "F": ("kayma kuvveti", "shear force", "N"),
       "A": ("alan", "area", "m^2"),
       "dx": ("kayma miktari", "shear displacement", "m"),
       "L": ("kalinlik", "thickness", "m")},
      "kayma modulu|makaslama modulu", "shear modulus"),
    F("hacim_modulu", "katihal", "Hacim modulu", "Bulk modulus",
      "K = -dP*V/dV",
      {"K": ("hacim modulu", "bulk modulus", "Pa"),
       "dP": ("basinc degisimi", "pressure change", "Pa"),
       "V": ("ilk hacim", "initial volume", "m^3"),
       "dV": ("hacim degisimi", "volume change", "m^3")},
      "hacim modulu|sikistirilabilirlik", "bulk modulus|compressibility"),
    F("yariiletken_tasiyici", "katihal", "Ic yariiletken tasiyici yogunlugu",
      "Intrinsic carrier concentration", "ni = A_c*T**1.5*exp(-Eg/(2*kB*T))",
      {"ni": ("ic tasiyici yogunlugu", "intrinsic carrier density", "1/m^3"),
       "A_c": ("malzeme sabiti", "material constant", "1/(m^3·K^1.5)"),
       "T": ("sicaklik", "temperature", "K"),
       "Eg": ("yasak bant araligi", "band gap", "J"),
       "kB": ("Boltzmann sabiti", "Boltzmann constant", "J/K")},
      "ic tasiyici yogunlugu|yariiletken sicaklik|band araligi sicaklik",
      "intrinsic carrier|semiconductor temperature"),
    # --- Analitik mekanik (ileri kuram) ------------------------------------
    F("lagrange_fonksiyonu", "dinamik", "Lagrange fonksiyonu", "Lagrangian",
      "L = T - V",
      {"L": ("Lagrange fonksiyonu", "Lagrangian", "J"),
       "T": ("kinetik enerji", "kinetic energy", "J"),
       "V": ("potansiyel enerji", "potential energy", "J")},
      "lagrange fonksiyonu|lagrangian|kinetik eksi potansiyel|"
      "lagrange mekanigi",
      "lagrangian|kinetic minus potential",
      "Toplam enerji DEGILDIR: toplam T+V, Lagrange ise T-V'dir. Ikisini "
      "karistirmak en sik yapilan hatadir.",
      "Not the total energy: the Lagrangian is T minus V."),
    F("hamilton_fonksiyonu", "dinamik", "Hamilton fonksiyonu", "Hamiltonian",
      "H = T + V",
      {"H": ("Hamilton fonksiyonu", "Hamiltonian", "J"),
       "T": ("kinetik enerji", "kinetic energy", "J"),
       "V": ("potansiyel enerji", "potential energy", "J")},
      "hamilton fonksiyonu|hamiltonian|hamilton mekanigi|faz uzayi enerjisi",
      "hamiltonian|total energy",
      "Kisitlar zamana bagli degilse Hamilton fonksiyonu toplam enerjidir "
      "ve korunur. Kuantum mekaniginde Ĥ operatoru bunun karsiligidir.",
      "For time-independent constraints H is the conserved total energy."),
    F("etki", "dinamik", "Etki (action)", "Action",
      "S = L*dt",
      {"S": ("etki", "action", "J·s"),
       "L": ("Lagrange fonksiyonu", "Lagrangian", "J"),
       "dt": ("zaman araligi", "time interval", "s")},
      "etki integrali|en kucuk etki|etki ilkesi|varyasyon ilkesi",
      "action integral|least action",
      "Etkinin birimi J·s'dir — Planck sabitiyle ayni birim. Klasik davranis "
      "S >> ħ oldugunda ortaya cikar.",
      "Action shares units with Planck's constant."),
    F("boltzmann_faktoru", "termodinamik", "Boltzmann faktoru",
      "Boltzmann factor", "P = exp(-E/(kB*T))",
      {"P": ("goreli olasilik", "relative probability", ""),
       "E": ("durumun enerjisi", "state energy", "J"),
       "kB": ("Boltzmann sabiti", "Boltzmann constant", "J/K"),
       "T": ("sicaklik", "temperature", "K")},
      "boltzmann faktoru|boltzmann dagilimi|durum olasiligi|kanonik dagilim",
      "boltzmann factor|boltzmann distribution",
      "Yuksek enerjili durumlarin olasiligi USTEL olarak duser; sicaklik "
      "arttikca ust duzeyler dolmaya baslar.",
      "High-energy states are exponentially suppressed."),
    F("bolusum_serbest_enerji", "termodinamik",
      "Bolusum fonksiyonundan serbest enerji",
      "Free energy from the partition function", "F = -kB*T*lnZ",
      {"F": ("Helmholtz serbest enerjisi", "Helmholtz free energy", "J"),
       "kB": ("Boltzmann sabiti", "Boltzmann constant", "J/K"),
       "T": ("sicaklik", "temperature", "K"),
       "lnZ": ("bolusum fonksiyonunun logaritmasi",
               "log of the partition function", "")},
      "bolusum fonksiyonu|partition function|kanonik topluluk|"
      "istatistiksel mekanik serbest enerji",
      "partition function|canonical ensemble",
      "Z bilinirse sistemin butun termodinamigi bilinir: enerji, entropi ve "
      "basinc hepsi Z'den turetilir.",
      "Knowing Z means knowing all the thermodynamics."),
]

def _sozluk_bagla():
    """Gunluk dil sozlugunu formullere isle.

    Formul tanimlarindaki anahtar kelimeler terimseldir ("egik atis
    menzili"); kullanici ise "top nereye duser" diye sorar. Sozluk ayri
    dosyada tutulur ve burada baglanir, boylece yeni soru kaliplari formul
    tanimlarina dokunmadan eklenebilir.
    """
    from .sozluk import EK_ANAHTAR
    from .notlar import NOTLAR
    bilinmeyen = []
    global _ARAMA_INDEKS
    _ARAMA_INDEKS = None
    for fid, (tr, en) in EK_ANAHTAR.items():
        f = next((x for x in FORMULAS if x["id"] == fid), None)
        if f is None:
            bilinmeyen.append(fid)
            continue
        for kw in tr.split("|"):
            if kw and kw not in f["kw_tr"]:
                f["kw_tr"].append(kw)
        for kw in en.split("|"):
            if kw and kw not in f["kw_en"]:
                f["kw_en"].append(kw)
    # Fiziksel anlam notlari: modele denklemin yaninda NE ANLAMA geldigi de
    # verilsin diye. Bos birakilan bosluğu model kendi dolduruyordu.
    for fid, (n_tr, n_en) in NOTLAR.items():
        f = next((x for x in FORMULAS if x["id"] == fid), None)
        if f is None:
            bilinmeyen.append(fid)
            continue
        if not f.get("note_tr"):
            f["note_tr"] = n_tr
        if not f.get("note_en"):
            f["note_en"] = n_en
    return bilinmeyen


SOZLUK_BILINMEYEN = _sozluk_bagla()


def ogrenilenleri_bagla():
    """Daha once ogrenilmis ifadeleri arama tabanina kat.

    Veritabani hazir olmadan cagrilmamali; bu yuzden import sirasinda degil,
    ilk kullanimda (brain baslatirken) cagriliyor.
    """
    global _ARAMA_INDEKS
    from . import sozluk
    n = 0
    for fid, ifadeler in sozluk.ogrenilenler().items():
        f = BY_ID.get(fid)
        if not f:
            continue
        for ifade in ifadeler:
            if ifade not in f["kw_tr"]:
                f["kw_tr"].append(ifade)
                n += 1
    if n:
        _ARAMA_INDEKS = None
    return n


def ifade_ogren(fid, soru, dogrula=None):
    """Bir soru ifadesini formule bagla ve kalici olarak ogren.

    Yalnizca dil modeli sayesinde dogru formule ulasildiginda cagrilir.
    Eklemeden sonra `dogrula` cagrilir; olcum duserse ekleme geri alinir.
    Boylece ogrenme sistemi ancak iyilestirebilir, bozamaz.

    Doner: eklenen ifade ya da None.
    """
    global _ARAMA_INDEKS
    from . import sozluk
    f = BY_ID.get(fid)
    if not f:
        return None

    kelimeler = [w for w in _norm(soru).split()
                 if len(w) > 2 and w not in _SORU_KELIMESI]
    if len(kelimeler) < 2:
        return None
    ifade = " ".join(kelimeler[:6])

    # Zaten buluyorsa ogrenmeye gerek yok
    mevcut = search(soru, limit=1)
    if mevcut and mevcut[0][1]["id"] == fid and mevcut[0][0] >= 40:
        return None

    veri = sozluk.ogrenilenler()
    liste = veri.get(fid, [])
    if ifade in liste or ifade in f["kw_tr"]:
        return None

    onceki_puan = dogrula() if dogrula else None
    f["kw_tr"].append(ifade)
    _ARAMA_INDEKS = None

    def _geri_al():
        global _ARAMA_INDEKS
        f["kw_tr"].remove(ifade)
        _ARAMA_INDEKS = None

    # 1) Ifade gercekten hedef formule goturuyor mu? Goturmuyorsa ekleme
    # bir ise yaramaz, sadece tabani kirletir.
    yeni = search(soru, limit=1)
    if not yeni or yeni[0][1]["id"] != fid:
        _geri_al()
        return None
    # 2) Mevcut olcumu dusurmemeli
    if dogrula is not None and dogrula() < onceki_puan:
        _geri_al()
        return None

    liste.append(ifade)
    veri[fid] = liste[-sozluk.OGRENME_SINIRI:]
    sozluk._kaydet(veri)
    return ifade

BY_ID = {f["id"]: f for f in FORMULAS}
TOPICS = sorted(set(f["topic"] for f in FORMULAS))


def _norm(s):
    s = (s or "").lower()
    tr = {"ı": "i", "İ": "i", "ş": "s", "ğ": "g", "ü": "u", "ö": "o", "ç": "c", "â": "a"}
    for a, b in tr.items():
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9\s=+\-*/^.]", " ", s)


# Her soruda gecen kaliplar; kismi eslesmede sayilmazlar
_SORU_KELIMESI = frozenset("""neden nasil nedir hangi nicin kimdir olur olan
    yapar eder mi mu misin nedeni sence lutfen bana beni bunu sunu
    why how what which does when""".split())


_ARAMA_INDEKS = None


def _indeks():
    """Arama icin sabit verileri bir kez hesapla.

    Sozluk eklendikten sonra 1600 anahtar kelime var; her sorguda bunlari
    yeniden normalize edip regex derlemek aramayi 128 ms'ye cikarmisti.
    Normalize edilmis bicimler ve derlenmis kaliplar burada bir kez
    uretilir.
    """
    global _ARAMA_INDEKS
    if _ARAMA_INDEKS is None:
        _ARAMA_INDEKS = []
        for f in FORMULAS:
            anahtarlar = []
            for kw in f["kw_tr"] + f["kw_en"]:
                k = _norm(kw).strip()
                if not k:
                    continue
                kws = frozenset(k.split())
                onemli = tuple(w[:4] for w in kws
                               if len(w) > 3 and w not in _SORU_KELIMESI)
                # Turkce cekim eki: "momentum" anahtari "momentumu"
                # sorgusunu tutmuyordu (olculdu: "6 kg cisim 4 m/s
                # momentumu" sorusu hicbir formule ulasamiyordu, ama
                # "momentum" yazinca 114 puanla buluyordu). Konu
                # aramasinda bu tolerans zaten vardi; formul aramasinda
                # yoktu. Kisa anahtarlarda ek verilmez ki "is" -> "isik"
                # gibi yanlis eslesmeler olmasin.
                _ek = r"\w{0,3}" if len(k) >= 5 else ""
                anahtarlar.append((
                    k,
                    re.compile(r"(?<!\w)%s%s(?!\w)" % (re.escape(k), _ek)),
                    kws,
                    onemli,
                    (30 + len(k)) if (len(k) >= 5 or " " in k) else 10,
                ))
            _ARAMA_INDEKS.append({
                "f": f,
                "kw": anahtarlar,
                "ad": _norm(f["tr"]) + " | " + _norm(f["en"]),
                "ad_tr": _norm(f["tr"]),
                "ad_en": _norm(f["en"]),
                "konu": _norm(f["topic"]),
                "var": [(_norm(t), _norm(e)) for t, e, _u in f["vars"].values()],
            })
    return _ARAMA_INDEKS


def search(query, limit=6):
    """Formul ara. (skor, formul) listesi doner."""
    q = _norm(query)
    qw = set(w for w in q.split() if len(w) > 2)
    qw4 = {w[:4] for w in qw}
    scored = []
    for kayit in _indeks():
        f = kayit["f"]
        score = 0
        name_tr, name_en = kayit["ad_tr"], kayit["ad_en"]
        # Tam ad eslesmesi. Alt dizi degil kelime siniri araniyor: "sure"
        # kelimesi "pressure" icinde gectigi icin ses basinc duzeyi formulu
        # 60 puan aliyordu. Ayrica tek kelimelik bir sorgunun tam ad
        # eslesmesi sayilmasi yaniltici oldugu icin puani dusuk tutuluyor.
        qs = q.strip()
        if qs and qs in kayit["ad"] and re.search(
                r"(?<!\w)%s(?!\w)" % re.escape(qs), kayit["ad"]):
            score += 60 if len(qs.split()) >= 2 else 25
        for k, kalip, kws, onemli, kw_puan in kayit["kw"]:
            # Kelime siniri sart: "yol" anahtar kelimesi "yol haritasi"
            # sorgusuyla eslesip alakasiz bir formulu one cikarmasin diye
            # alt dizi degil tam kelime araniyor. Once ucuz `in` denetimi.
            if k in q and kalip.search(q):
                # Tek ve kisa bir kelimenin agirligi dusuk tutuluyor
                score += kw_puan
            else:
                if kws <= qw:
                    score += 26        # tam alt kume, kismi eslesmeyi yener
                elif len(kws) >= 2:
                    # Kismi eslesme. Turkce cekim yuzunden anahtar kelime
                    # cumleye birebir oturmuyor: "havada ne kadar kalir"
                    # ifadesi "havada ne kadar kaldigini" sorusuyla tam
                    # eslesmiyor. Ortak kelime sayisina gore puan veriyoruz;
                    # yarisindan azi tutuyorsa saymiyoruz.
                    # Soru kelimeleri ("neden", "nasil") her cumlede gectigi
                    # icin sayilmaz (onemli listesi indekste suzuluyor);
                    # yoksa "metal neden iyi iletir" anahtari
                    # "metal isitilinca neden uzuyor" sorusunu tutuyor.
                    if len(onemli) >= 2:
                        tutan = sum(1 for on in onemli if on in qw4)
                        if tutan >= 2 and tutan * 2 >= len(onemli):
                            # Anahtardaki EKSIK kelime de bilgi tasir:
                            # "donme kinetik enerjisi" anahtari, sorguda
                            # "donme" yokken tam eslesme kadar guclu
                            # olmamali. Yoksa "kinetik enerji" sorusu
                            # donme enerjisine gidiyor.
                            eksik = len(onemli) - tutan
                            score += max(0, 11 * tutan - 8 * eksik)
        for w in qw:
            if w in name_tr or w in name_en:
                score += 9
            if w in kayit["konu"]:
                score += 5
            for t, e in kayit["var"]:
                if w in t or w in e:
                    score += 4
        if score:
            # Turetilmis formuller cekirdegin onune gecmemeli: bunlar
            # alternatif bicimlerdir, bir sorunun birincil cevabi degil.
            # Ceza konmadan olcum 40/40'tan 37/40'a dusuyordu.
            if f.get("uretilmis"):
                score = int(score * 0.6)
            scored.append((score, f))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]


# Turkce cekim ekleri — "kondansatorun" ile "kondansator" eslessin diye
_EK = re.compile(
    r"(lardan|lerden|larin|lerin|larla|lerle|lari|leri|lara|lere|"
    r"nin|nun|nin|nde|nda|den|dan|tan|ten|deki|daki|ile|ler|lar|"
    r"si|su|si|yi|yu|ye|ya|in|un|im|um|de|da|te|ta|le|la|i|u|e|a)$")


def _kok(w):
    """Kelimeyi kabaca kokune indir. Kisa kelimelere dokunulmaz."""
    if len(w) <= 4:
        return w
    kok = _EK.sub("", w)
    # Unsuz yumusamasi: kitabi -> kitab -> kitap; sicakligi -> sicaklig -> sicaklik
    if len(kok) >= 4 and kok[-1] in "bcdg":
        kok = kok[:-1] + {"b": "p", "c": "c", "d": "t", "g": "k"}[kok[-1]]
    return kok if len(kok) >= 4 else w


def _koklar(metin):
    return {_kok(w) for w in _norm(metin).split() if len(w) > 2}


# Gunluk dilde sorulan sorulari konuya baglayan ipuclari. Kullanici
# "topun havada ne kadar kaldigi" diye soruyor; formul adinda "egik atis"
# yaziyor. Bu koprü olmadan aday listesi bos kaliyor.
KONU_IPUCU = {
    "kinematik": """top atis firlat dusme dus havada ucus zipla hiz ivme
        mesafe yol konum surat fren hizlan yavasla dusey yatay menzil
        ball throw fall flight speed acceleration distance projectile""",
    "dinamik": """kuvvet itme cek surtunme kutle newton agirlik yay denge
        tork moment donme eylemsizlik carpisma momentum egik duzlem
        force friction mass torque rotation collision momentum incline""",
    "enerji": """is guc enerji verim kinetik potansiyel korunum kaldir
        work power energy efficiency kinetic potential lift""",
    "elektrik": """akim gerilim volt amper direnc kondansator sigac bobin
        devre manyetik alan yuk transformator indukleme sarj bosal pil
        current voltage resistance capacitor inductor circuit magnetic charge""",
    "termodinamik": """sicaklik isi gaz basinc hacim entropi motor verim
        genlesme buhar erime kayna sogut isit sikistir mol termometre
        temperature heat gas pressure volume entropy engine expansion""",
    "dalga": """dalga ses frekans titres sarkac rezonans gitar tel boru
        yanki desibel genlik periyot ton perde sonik
        wave sound frequency oscillation pendulum resonance string pipe""",
    "optik": """isik mercek ayna lens goruntu kirilma yansima teleskop
        mikroskop renk ayrinti cozunurluk netlik kirinim polarizasyon
        gozluk odak buyutme prizma kristal
        light lens mirror image refraction telescope resolution diffraction""",
    "kuantum": """foton elektron atom duzey belirsizlik spin tunelleme
        orbital kuantum uyarilma taban hal dalga boyu
        photon electron atom uncertainty spin tunneling quantum""",
    "nukleer": """cekirdek radyoaktif yariomur bozun isin fisyon fuzyon doz
        nukleer izotop proton notron baglanma
        nucleus radioactive half-life decay fission fusion dose isotope""",
    "gorelilik": """gorelilik zaman genlesme boy kisalma isik hizi ikiz
        relativity time dilation length contraction lorentz""",
    "astro": """yildiz galaksi gezegen yorunge kacis kirmizi kayma parlaklik
        uzaklik evren genisleme kara delik teleskop gokyuzu
        star galaxy planet orbit escape redshift luminosity universe""",
    "akiskan": """sivi su akis boru kaldirma viskozite debi damla yuzme bat
        akiskan surukleme kanat basinc derinlik
        fluid liquid flow pipe buoyancy viscosity drag lift""",
    "katihal": """yariiletken kristal iletkenlik band hall silisyum diyot
        semiconductor crystal conductivity band gap""",
    "plazma": """plazma iyon debye larmor fuzyon reaktor iyonlas
        plasma ion debye larmor""",
}
_KONU_KOK = None


def konu_tahmin(query, limit=3):
    """Sorunun hangi fizik konusuna dustugunu gunluk kelimelerden tahmin et."""
    global _KONU_KOK
    if _KONU_KOK is None:
        _KONU_KOK = {t: _koklar(k) for t, k in KONU_IPUCU.items()}
    qk = _koklar(query)
    if not qk:
        return []
    puanlar = [(len(qk & kk), t) for t, kk in _KONU_KOK.items()]
    puanlar = [(p, t) for p, t in puanlar if p]
    puanlar.sort(reverse=True)
    return [t for _p, t in puanlar[:limit]]


def genis_ara(query, limit=12):
    """Gevsek aday listesi uret — serbest cumleler icin.

    `search` kelime siniri ve tam eslesme arar; "kondansatorun dolmasi ne
    kadar surer" gibi bir cumleyi hic tutamaz ve bos doner. Burada Turkce
    ekleri atilarak kok duzeyinde ortusme aranir. Skorlar gevsek oldugu icin
    sonuc dogrudan kullanilmaz — yalnizca dil modeline sunulacak aday
    listesini olusturur, secimi model yapar, hesabi SymPy yapar.
    """
    qk = _koklar(query)
    if not qk:
        return []
    scored = []
    for f in FORMULAS:
        p = 0
        for alan, agirlik in ((f["tr"], 6), (f["en"], 6),
                              (f["kw_tr"] + f["kw_en"] and
                               " ".join(f["kw_tr"] + f["kw_en"]), 8),
                              (f["topic"], 3)):
            if not alan:
                continue
            p += agirlik * len(qk & _koklar(alan))
        for _sym, (t, e, _u) in f["vars"].items():
            p += 2 * len(qk & _koklar(t + " " + e))
        if p:
            scored.append((p, f))
    scored.sort(key=lambda x: -x[0])

    # Havuz inceyse konu tahmininden tamamla: model dogru formulu ancak
    # listede varsa secebilir, bos liste secim sansini sifirlar.
    hedef = min(limit, 6)
    if len(scored) < hedef:
        var = {id(f) for _p, f in scored}
        for konu in konu_tahmin(query):
            for f in FORMULAS:
                if f["topic"] == konu and id(f) not in var:
                    scored.append((1, f))
                    var.add(id(f))
                    if len(scored) >= hedef:
                        break
            if len(scored) >= hedef:
                break
    return scored[:limit]


def describe(f, lang="tr"):
    """Formulu okunakli metne cevir."""
    name = f["tr"] if lang == "tr" else f["en"]
    lines = ["**%s** — `%s`" % (name, f["eq"])]
    lines.append("")
    lines.append("Degiskenler:" if lang == "tr" else "Variables:")
    for sym, (t, e, u) in f["vars"].items():
        label = t if lang == "tr" else e
        lines.append("- `%s` = %s%s" % (sym, label, (" [%s]" % u) if u else ""))
    note = f.get("note_tr" if lang == "tr" else "note_en")
    if note:
        lines.append("")
        lines.append("> " + note)
    return "\n".join(lines)


def sympy_eq(f):
    """Formulu SymPy denklemine cevir.

    Degisken adlari (Tc, v0, eps0, m1 ...) acikca sembol olarak bildirilir;
    aksi halde ortuk carpim donusumu bunlari `T*c`, `v*0` gibi parcalar.
    """
    syms = list(f["vars"].keys())
    eq = f["eq"]
    if "=" in eq:
        a, b = eq.split("=", 1)
        return sp.Eq(parse(a, symbols=syms), parse(b, symbols=syms))
    return sp.Eq(parse(eq, symbols=syms), 0)


def _us_mu(ifade, sembol):
    """Sembol denklemde yalnizca us konumunda mi geciyor?"""
    us_konumunda = False
    taban_konumunda = False
    for alt in sp.preorder_traversal(ifade):
        if isinstance(alt, sp.Pow):
            if sembol in alt.exp.free_symbols:
                us_konumunda = True
            if sembol in alt.base.free_symbols:
                taban_konumunda = True
        # exp/log argumanlari da askin cozum dogurur
        elif isinstance(alt, (sp.exp, sp.log)):
            if sembol in alt.args[0].free_symbols:
                us_konumunda = True
    if not us_konumunda:
        return False
    # Hem tabanda hem uste geciyorsa yine sembolik cozum denenmemeli
    return True if not taban_konumunda else True


# ── Sure sinirli calistirma ────────────────────────────────────────────────
# Sembolik cozum bazen bitmiyor. Ana is parcaciginda SIGALRM guvenilir;
# sunucu istek parcaciklarinda sinyal kullanilamaz, orada isi ayri bir
# parcacikta calistirip sure dolunca birakiyoruz (parcacik daemon oldugu
# icin surec kapaninca kendisi de gider).
SOLVE_SURE = 8.0
_ZAMAN_ASIMI = object()


def _sureli(fn, saniye):
    """fn()'i en fazla `saniye` kadar calistir; asarsa _ZAMAN_ASIMI dondur."""
    import threading
    if threading.current_thread() is threading.main_thread():
        import signal

        def _dolduysa(sig, cerceve):
            raise TimeoutError()

        eski = signal.signal(signal.SIGALRM, _dolduysa)
        signal.setitimer(signal.ITIMER_REAL, saniye)
        try:
            return fn()
        except TimeoutError:
            return _ZAMAN_ASIMI
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, eski)

    kutu = {}

    def _kos():
        try:
            kutu["v"] = fn()
        except BaseException as e:
            kutu["e"] = e

    ip = threading.Thread(target=_kos, daemon=True)
    ip.start()
    ip.join(saniye)
    if ip.is_alive():
        return _ZAMAN_ASIMI
    if "e" in kutu:
        raise kutu["e"]
    return kutu.get("v")


def _sayisal_kok(ifade, sembol, aralik=(-40.0, 40.0), adim=0.25):
    """Tek degiskenli ifadenin sayisal kokunu bul.

    Isaret degistiren ilk araliga bisection uygulanir; boylece SymPy'nin
    sembolik cozucusune hic girilmez ve hesap her zaman biter.
    """
    try:
        fn = sp.lambdify(sembol, ifade, "math")
    except Exception:
        return None
    a, b = aralik
    x = a
    onceki_x, onceki_y = None, None
    while x <= b:
        try:
            y = float(fn(x))
        except Exception:
            x += adim
            onceki_x, onceki_y = None, None
            continue
        if onceki_y is not None and onceki_y == 0:
            return onceki_x
        if onceki_y is not None and onceki_y * y < 0:
            lo, hi = onceki_x, x
            for _ in range(80):
                orta = (lo + hi) / 2.0
                try:
                    ym = float(fn(orta))
                except Exception:
                    return None
                if ym == 0:
                    return orta
                if float(fn(lo)) * ym < 0:
                    hi = orta
                else:
                    lo = orta
            return (lo + hi) / 2.0
        onceki_x, onceki_y = x, y
        x += adim
    return None


# ── Fiziksel siralama kisitlari ────────────────────────────────────────────
# Bazi formullerde iki degisken ayni birimdedir ve hangi sayinin hangisine
# ait oldugu METINDEN anlasilmaz: "500 K ve 300 K arasinda calisan Carnot
# makinesi" cumlesinde ikisi de sicakliktir. Sirayi FIZIK belirler: sicak
# kaynak soguk kaynaktan sicaktir.
#
# Olculdu: bu kural olmadan sistem Tc=500, Th=300 atadi ve ogrenciye
# "verim = -0.667" dedi — kesin ve emin bicimde YANLIS bir cevap.
SIRALI_DEGISKENLER = {
    # Atwood'da m2 AGIR kutledir; ters atanirsa ivme negatif cikar.
    # Olculdu: etikete gore dagitim 3 kg'i m2'ye, 5 kg'i m1'e yazdi.
    "atwood": [("m2", "m1")],
    "carnot": [("Th", "Tc")],
    "carnot_is": [("Th", "Tc")],   # sicak kaynak >= soguk kaynak          # sicak kaynak >= soguk kaynak
    "isi_pompasi": [("Th", "Tc")],
    "sogutma_cop": [("Th", "Tc")],
}


def sirali_duzelt(f, sayisal):
    """Fiziksel siralamayi bozan atamalari duzelt. (duzeltildi_mi, notlar)"""
    kisitlar = SIRALI_DEGISKENLER.get(f.get("id"))
    if not kisitlar:
        return False, []
    notlar = []
    for buyuk, kucuk in kisitlar:
        a, b = sayisal.get(buyuk), sayisal.get(kucuk)
        if a is None or b is None:
            continue
        if a < b:
            sayisal[buyuk], sayisal[kucuk] = b, a
            notlar.append((buyuk, kucuk))
    return bool(notlar), notlar


def solve_for(f, knowns, target=None):
    """Formulu bilinmeyen icin coz.

    knowns: {"sembol": sayi} - SI birimlerinde
    target: cozulecek sembol (None ise tek bilinmeyen otomatik secilir)
    """
    eq = sympy_eq(f)
    all_syms = set(f["vars"].keys())
    known_syms = set(k for k in knowns if k in all_syms)
    unknown = sorted(all_syms - known_syms)
    if target is None:
        if len(unknown) != 1:
            raise SolveError(
                "Tam olarak bir bilinmeyen gerekli. Bilinmeyenler: %s"
                % (", ".join(unknown) if unknown else "yok"))
        target = unknown[0]
    subs = {sp.Symbol(k): sp.Float(v) if isinstance(v, float) else sp.Integer(v)
            for k, v in knowns.items() if k != target and k in all_syms}
    eq2 = eq.subs(subs)
    hedef_sembol = sp.Symbol(target)

    # Hedef bir US ise (adyabatik surecte gamma gibi) sembolik cozum askin
    # bir denklem dogurur ve SymPy pratikte hic donmez. Boyle durumlarda
    # sayisal koke gidiyoruz: cevap yine dogru, ama hesap biter.
    if _us_mu(eq2.lhs - eq2.rhs, hedef_sembol):
        kok = _sayisal_kok(eq2.lhs - eq2.rhs, hedef_sembol)
        if kok is None:
            raise SolveError(
                "Bu degisken bir us konumunda; sayisal cozum bulunamadi. "
                "Diger degiskenlerin degerlerini kontrol edin.")
        return target, [kok], eq

    # SymPy'nin sembolik cozucusu bazi sayisal degerlerde PRATIKTE hic
    # donmuyor. Olculdu: test takimi bir gecede bitmedi ve arkada %99
    # islemciyle donen yedi surec birikmisti; hepsi bu cagrida asili
    # kalmisti. Hangi formul oldugu degere bagli, sabit degil — o yuzden
    # tek tek formul yamamak yerine cagrinin kendisine sure siniri
    # koyuyoruz. Sure asilirsa sayisal koke duşuyoruz: cevap yine dogru
    # cikar, hesap her durumda biter.
    sols = _sureli(lambda: sp.solve(eq2, hedef_sembol, dict=False),
                   SOLVE_SURE)
    if sols is _ZAMAN_ASIMI:
        kok = _sayisal_kok(eq2.lhs - eq2.rhs, hedef_sembol)
        if kok is None:
            raise SolveError(
                "Bu denklem verilen degerlerle makul surede cozulemedi.")
        return target, [kok], eq
    if not isinstance(sols, (list, tuple)):
        sols = [sols]
    out = []
    for s in sols:
        try:
            val = complex(sp.N(s))
            if abs(val.imag) < 1e-12:
                out.append(float(val.real))
            else:
                out.append(val)
        except Exception:
            out.append(fmt_expr(s))
    return target, out, eq


def symbolic_rearrange(f, target):
    """Formulu hedef degisken icin sembolik olarak duzenle."""
    eq = sympy_eq(f)
    sols = sp.solve(eq, sp.Symbol(target), dict=False)
    if not isinstance(sols, (list, tuple)):
        sols = [sols]
    return [fmt_expr(s) for s in sols]
