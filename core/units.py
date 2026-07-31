"""Birim sistemi, boyut analizi ve fiziksel sabitler.

Boyut vektoru: (m, kg, s, A, K, mol, cd)
Her birim -> (SI'ye cevirme carpani, boyut vektoru, ofset)
Ofset sadece sicaklik (C, F) icin kullanilir.
"""
import re
import math

DIM_NAMES = ("m", "kg", "s", "A", "K", "mol", "cd")


def D(m=0, kg=0, s=0, A=0, K=0, mol=0, cd=0):
    return (m, kg, s, A, K, mol, cd)


DIMENSIONLESS = D()

# --- Turetilmis boyutlar -----------------------------------------------------
DIM_LABELS = {
    D(): "boyutsuz",
    D(m=1): "uzunluk",
    D(kg=1): "kutle",
    D(s=1): "zaman",
    D(A=1): "akim",
    D(K=1): "sicaklik",
    D(mol=1): "madde miktari",
    D(cd=1): "isik siddeti",
    D(m=2): "alan",
    D(m=3): "hacim",
    D(m=1, s=-1): "hiz",
    D(m=1, s=-2): "ivme",
    D(kg=1, m=1, s=-2): "kuvvet",
    D(kg=1, m=2, s=-2): "enerji / is / isi",
    D(kg=1, m=2, s=-3): "guc",
    D(kg=1, m=-1, s=-2): "basinc / gerilme",
    D(kg=1, m=1, s=-1): "momentum / impuls",
    D(kg=1, m=2, s=-1): "aci momentumu / etki",
    D(s=-1): "frekans",
    D(kg=-1, m=-2, s=4, A=2): "kapasitans",
    D(kg=-1, m=-3, s=4, A=2): "elektrik gecirgenligi",
    D(kg=1, m=2, s=-3, A=-1): "gerilim (voltaj)",
    D(kg=1, m=2, s=-3, A=-2): "direnc",
    D(kg=-1, m=-2, s=3, A=2): "iletkenlik",
    D(kg=1, m=2, s=-2, A=-1): "manyetik aki",
    D(kg=1, s=-2, A=-1): "manyetik alan (B)",
    D(kg=1, m=2, s=-2, A=-2): "induktans",
    D(A=1, s=1): "elektrik yuku",
    D(kg=1, m=1, s=-3, A=-1): "elektrik alan (E)",
    D(kg=1, m=2, s=-2, K=-1): "entropi / isi kapasitesi",
    D(m=3, s=-1): "hacimsel debi",
    D(kg=1, m=-3): "yogunluk",
    D(kg=1, m=-1, s=-1): "dinamik viskozite",
    D(m=2, s=-1): "kinematik viskozite / difuzyon",
}


def dim_label(dim):
    return DIM_LABELS.get(tuple(dim), dim_str(dim))


def dim_str(dim):
    parts = []
    for n, p in zip(DIM_NAMES, dim):
        if p:
            parts.append(n if p == 1 else "%s^%g" % (n, p))
    return "·".join(parts) if parts else "1"


def dim_mul(a, b):
    return tuple(x + y for x, y in zip(a, b))


def dim_div(a, b):
    return tuple(x - y for x, y in zip(a, b))


def dim_pow(a, n):
    return tuple(x * n for x in a)


# --- Temel birimler ----------------------------------------------------------
# ad: (SI carpani, boyut, ofset)
UNITS = {}


def _u(names, factor, dim, offset=0.0):
    for n in names.split():
        UNITS[n] = (factor, dim, offset)


# Uzunluk
_u("m metre meter metres meters", 1.0, D(m=1))
_u("km kilometre kilometer", 1e3, D(m=1))
_u("cm santimetre centimeter", 1e-2, D(m=1))
_u("mm milimetre millimeter", 1e-3, D(m=1))
_u("um µm mikrometre micrometer micron", 1e-6, D(m=1))
_u("nm nanometre nanometer", 1e-9, D(m=1))
_u("pm pikometre picometer", 1e-12, D(m=1))
_u("fm femtometre femtometer fermi", 1e-15, D(m=1))
_u("A_ang angstrom Å", 1e-10, D(m=1))
_u("mile mil", 1609.344, D(m=1))
_u("inch inc in_ ", 0.0254, D(m=1))
_u("ft foot feet", 0.3048, D(m=1))
_u("yd yard", 0.9144, D(m=1))
_u("au astronomicalunit", 1.495978707e11, D(m=1))
_u("ly isikyili lightyear", 9.4607304725808e15, D(m=1))
_u("pc parsek parsec", 3.0856775814913673e16, D(m=1))

# Kutle
_u("kg kilogram", 1.0, D(kg=1))
_u("g gram", 1e-3, D(kg=1))
_u("mg miligram milligram", 1e-6, D(kg=1))
_u("ug µg mikrogram microgram", 1e-9, D(kg=1))
_u("ton tonne t", 1e3, D(kg=1))
_u("lb pound", 0.45359237, D(kg=1))
_u("oz ounce", 0.028349523125, D(kg=1))
_u("u amu dalton Da", 1.66053906892e-27, D(kg=1))
_u("Msun gunes_kutlesi solarmass", 1.98892e30, D(kg=1))

# Zaman
_u("s saniye sec second seconds sn sny snye saniyesi", 1.0, D(s=1))
_u("ms milisaniye millisecond", 1e-3, D(s=1))
_u("us µs mikrosaniye microsecond", 1e-6, D(s=1))
_u("ns nanosaniye nanosecond", 1e-9, D(s=1))
_u("ps pikosaniye picosecond", 1e-12, D(s=1))
_u("fs femtosaniye femtosecond", 1e-15, D(s=1))
_u("dk dakika min minute", 60.0, D(s=1))
_u("saat hour h hr", 3600.0, D(s=1))
_u("gun day d", 86400.0, D(s=1))
_u("hafta week", 604800.0, D(s=1))
_u("yil year yr a", 3.15576e7, D(s=1))

# Akim / yuk
_u("A amper ampere", 1.0, D(A=1))
_u("mA miliamper milliampere", 1e-3, D(A=1))
_u("uA µA mikroamper microampere", 1e-6, D(A=1))
_u("C coulomb kulon", 1.0, D(A=1, s=1))
_u("e elementarycharge", 1.602176634e-19, D(A=1, s=1))
_u("mC millicoulomb", 1e-3, D(A=1, s=1))
_u("uC µC microcoulomb", 1e-6, D(A=1, s=1))
_u("nC nanocoulomb", 1e-9, D(A=1, s=1))

# Sicaklik
_u("K kelvin", 1.0, D(K=1))
_u("degC celsius santigrat C_deg", 1.0, D(K=1), 273.15)
_u("degF fahrenheit", 5.0 / 9.0, D(K=1), 255.372222222222)
_u("R rankine", 5.0 / 9.0, D(K=1))

# Madde / isik
_u("mol mole", 1.0, D(mol=1))
_u("mmol millimole", 1e-3, D(mol=1))
_u("cd kandela candela", 1.0, D(cd=1))

# Kuvvet
_u("N newton", 1.0, D(kg=1, m=1, s=-2))
_u("kN kilonewton", 1e3, D(kg=1, m=1, s=-2))
_u("mN millinewton", 1e-3, D(kg=1, m=1, s=-2))
_u("dyn dyne", 1e-5, D(kg=1, m=1, s=-2))
_u("lbf poundforce", 4.4482216152605, D(kg=1, m=1, s=-2))
_u("kgf kilogramforce", 9.80665, D(kg=1, m=1, s=-2))

# Enerji
_u("J joule", 1.0, D(kg=1, m=2, s=-2))
_u("kJ kilojoule", 1e3, D(kg=1, m=2, s=-2))
_u("MJ megajoule", 1e6, D(kg=1, m=2, s=-2))
_u("mJ millijoule", 1e-3, D(kg=1, m=2, s=-2))
_u("eV elektronvolt electronvolt", 1.602176634e-19, D(kg=1, m=2, s=-2))
_u("keV kiloelectronvolt", 1.602176634e-16, D(kg=1, m=2, s=-2))
_u("MeV megaelectronvolt", 1.602176634e-13, D(kg=1, m=2, s=-2))
_u("GeV gigaelectronvolt", 1.602176634e-10, D(kg=1, m=2, s=-2))
_u("TeV teraelectronvolt", 1.602176634e-7, D(kg=1, m=2, s=-2))
_u("cal kalori calorie", 4.184, D(kg=1, m=2, s=-2))
_u("kcal kilokalori kilocalorie", 4184.0, D(kg=1, m=2, s=-2))
_u("erg", 1e-7, D(kg=1, m=2, s=-2))
_u("kWh kilowattsaat kilowatthour", 3.6e6, D(kg=1, m=2, s=-2))
_u("Wh watthour", 3600.0, D(kg=1, m=2, s=-2))
_u("BTU btu", 1055.05585262, D(kg=1, m=2, s=-2))

# Guc
_u("W watt", 1.0, D(kg=1, m=2, s=-3))
_u("kW kilowatt", 1e3, D(kg=1, m=2, s=-3))
_u("MW megawatt", 1e6, D(kg=1, m=2, s=-3))
_u("GW gigawatt", 1e9, D(kg=1, m=2, s=-3))
_u("mW milliwatt", 1e-3, D(kg=1, m=2, s=-3))
_u("hp beygir horsepower", 745.6998715822702, D(kg=1, m=2, s=-3))

# Basinc
_u("Pa pascal", 1.0, D(kg=1, m=-1, s=-2))
_u("kPa kilopascal", 1e3, D(kg=1, m=-1, s=-2))
_u("MPa megapascal", 1e6, D(kg=1, m=-1, s=-2))
_u("GPa gigapascal", 1e9, D(kg=1, m=-1, s=-2))
_u("hPa hektopascal hectopascal", 1e2, D(kg=1, m=-1, s=-2))
_u("bar", 1e5, D(kg=1, m=-1, s=-2))
_u("mbar millibar", 1e2, D(kg=1, m=-1, s=-2))
_u("atm atmosfer atmosphere", 101325.0, D(kg=1, m=-1, s=-2))
_u("torr mmHg", 133.322387415, D(kg=1, m=-1, s=-2))
_u("psi", 6894.757293168, D(kg=1, m=-1, s=-2))

# Frekans / aci
_u("Hz hertz", 1.0, D(s=-1))
_u("kHz kilohertz", 1e3, D(s=-1))
_u("MHz megahertz", 1e6, D(s=-1))
_u("GHz gigahertz", 1e9, D(s=-1))
_u("THz terahertz", 1e12, D(s=-1))
_u("rpm devir_dakika", 1.0 / 60.0, D(s=-1))

# Yaygin bilesik hiz birimleri (tek simge olarak da yazilabilsin)
_u("mph", 0.44704, D(m=1, s=-1))
_u("kmh kph", 1.0 / 3.6, D(m=1, s=-1))
_u("knot kt deniz_mili_saat", 0.5144444444444445, D(m=1, s=-1))
_u("fps", 0.3048, D(m=1, s=-1))
_u("mach", 340.29, D(m=1, s=-1))
_u("rad radyan radian", 1.0, D())
_u("deg derece degree", math.pi / 180.0, D())
_u("sr steradyan steradian", 1.0, D())

# Elektrik
_u("V volt", 1.0, D(kg=1, m=2, s=-3, A=-1))
_u("kV kilovolt", 1e3, D(kg=1, m=2, s=-3, A=-1))
_u("mV millivolt", 1e-3, D(kg=1, m=2, s=-3, A=-1))
_u("ohm Ω", 1.0, D(kg=1, m=2, s=-3, A=-2))
_u("kohm kiloohm", 1e3, D(kg=1, m=2, s=-3, A=-2))
_u("Mohm megaohm", 1e6, D(kg=1, m=2, s=-3, A=-2))
_u("S siemens", 1.0, D(kg=-1, m=-2, s=3, A=2))
# Farad = C/V = A^2·s^4·kg^-1·m^-2. (eps0 birimi F/m oldugu icin
# m ussu bir eksiktir; ikisi karistirilmamali.)
_u("F farad", 1.0, D(kg=-1, m=-2, s=4, A=2))
_u("uF µF mikrofarad microfarad", 1e-6, D(kg=-1, m=-2, s=4, A=2))
_u("nF nanofarad", 1e-9, D(kg=-1, m=-2, s=4, A=2))
_u("pF pikofarad picofarad", 1e-12, D(kg=-1, m=-2, s=4, A=2))
_u("H henry", 1.0, D(kg=1, m=2, s=-2, A=-2))
_u("mH millihenry", 1e-3, D(kg=1, m=2, s=-2, A=-2))
_u("T tesla", 1.0, D(kg=1, s=-2, A=-1))
_u("mT millitesla", 1e-3, D(kg=1, s=-2, A=-1))
_u("G gauss", 1e-4, D(kg=1, s=-2, A=-1))
_u("Wb weber", 1.0, D(kg=1, m=2, s=-2, A=-1))

# Hacim / alan
_u("L litre liter", 1e-3, D(m=3))
_u("mL mililitre milliliter", 1e-6, D(m=3))
_u("ha hektar hectare", 1e4, D(m=2))
_u("barn", 1e-28, D(m=2))

# Logaritmik / boyutsuz olcekler
_u("dB desibel decibel", 1.0, D())
_u("dBm", 1.0, D())
_u("ppm", 1e-6, D())
_u("percent yuzde", 0.01, D())

# Radyoaktivite
_u("Bq becquerel", 1.0, D(s=-1))
_u("Ci curie", 3.7e10, D(s=-1))
_u("Gy gray", 1.0, D(m=2, s=-2))
_u("Sv sievert", 1.0, D(m=2, s=-2))


# --- Fiziksel sabitler (CODATA 2022) ----------------------------------------
# ad: (deger, birim_string, boyut, aciklama_tr, aciklama_en)
CONSTANTS = {
    "c": (299792458.0, "m/s", D(m=1, s=-1), "Isik hizi (bosluk)", "Speed of light in vacuum"),
    "G": (6.67430e-11, "m^3/(kg·s^2)", D(m=3, kg=-1, s=-2), "Evrensel kutle cekim sabiti", "Gravitational constant"),
    "h": (6.62607015e-34, "J·s", D(kg=1, m=2, s=-1), "Planck sabiti", "Planck constant"),
    "hbar": (1.054571817e-34, "J·s", D(kg=1, m=2, s=-1), "Indirgenmis Planck sabiti", "Reduced Planck constant"),
    "e": (1.602176634e-19, "C", D(A=1, s=1), "Temel elektrik yuku", "Elementary charge"),
    "me": (9.1093837139e-31, "kg", D(kg=1), "Elektron kutlesi", "Electron mass"),
    "mp": (1.67262192595e-27, "kg", D(kg=1), "Proton kutlesi", "Proton mass"),
    "mn": (1.67492750056e-27, "kg", D(kg=1), "Notron kutlesi", "Neutron mass"),
    "u": (1.66053906892e-27, "kg", D(kg=1), "Atomik kutle birimi", "Atomic mass unit"),
    "NA": (6.02214076e23, "1/mol", D(mol=-1), "Avogadro sayisi", "Avogadro constant"),
    "kB": (1.380649e-23, "J/K", D(kg=1, m=2, s=-2, K=-1), "Boltzmann sabiti", "Boltzmann constant"),
    "R": (8.314462618, "J/(mol·K)", D(kg=1, m=2, s=-2, K=-1, mol=-1), "Ideal gaz sabiti", "Gas constant"),
    "sigma": (5.670374419e-8, "W/(m^2·K^4)", D(kg=1, s=-3, K=-4), "Stefan-Boltzmann sabiti", "Stefan-Boltzmann constant"),
    "eps0": (8.8541878188e-12, "F/m", D(kg=-1, m=-3, s=4, A=2), "Bosluk elektrik gecirgenligi", "Vacuum permittivity"),
    "mu0": (1.25663706127e-6, "N/A^2", D(kg=1, m=1, s=-2, A=-2), "Bosluk manyetik gecirgenligi", "Vacuum permeability"),
    "ke": (8.9875517862e9, "N·m^2/C^2", D(kg=1, m=3, s=-4, A=-2), "Coulomb sabiti", "Coulomb constant"),
    "g": (9.80665, "m/s^2", D(m=1, s=-2), "Standart yercekimi ivmesi", "Standard gravity"),
    "Rinf": (10973731.568157, "1/m", D(m=-1), "Rydberg sabiti", "Rydberg constant"),
    "Ry": (13.605693122994, "eV", D(kg=1, m=2, s=-2), "Rydberg enerjisi",
           "Rydberg energy"),
    "bW": (2.897771955e-3, "m·K", D(m=1, K=1), "Wien yer degistirme sabiti",
           "Wien displacement constant"),
    "bWf": (5.878925757e10, "Hz/K", D(s=-1, K=-1), "Wien frekans sabiti",
            "Wien frequency constant"),
    "uMeV": (931.49410372, "MeV", D(kg=1, m=2, s=-2),
             "Atomik kutle biriminin enerji karsiligi",
             "Atomic mass unit energy equivalent"),
    "a0": (5.29177210544e-11, "m", D(m=1), "Bohr yaricapi", "Bohr radius"),
    "alpha": (7.2973525643e-3, "", D(), "Ince yapi sabiti", "Fine-structure constant"),
    "muB": (9.2740100657e-24, "J/T", D(m=2, A=1), "Bohr magnetonu", "Bohr magneton"),
    "muN": (5.0507837393e-27, "J/T", D(m=2, A=1), "Nukleer magneton", "Nuclear magneton"),
    "F_faraday": (96485.33212, "C/mol", D(A=1, s=1, mol=-1), "Faraday sabiti", "Faraday constant"),
    "atm": (101325.0, "Pa", D(kg=1, m=-1, s=-2), "Standart atmosfer basinci", "Standard atmosphere"),
    "Vm": (0.02241396954, "m^3/mol", D(m=3, mol=-1), "Molar hacim (STP)", "Molar volume at STP"),
    "Msun": (1.98892e30, "kg", D(kg=1), "Gunes kutlesi", "Solar mass"),
    "Rsun": (6.957e8, "m", D(m=1), "Gunes yaricapi", "Solar radius"),
    "Mearth": (5.9722e24, "kg", D(kg=1), "Dunya kutlesi", "Earth mass"),
    "Rearth": (6.371e6, "m", D(m=1), "Dunya yaricapi", "Earth mean radius"),
    "AU": (1.495978707e11, "m", D(m=1), "Astronomik birim", "Astronomical unit"),
    "H0": (2.1927e-18, "1/s", D(s=-1), "Hubble sabiti (~67.7 km/s/Mpc)", "Hubble constant"),
    "Lsun": (3.828e26, "W", D(kg=1, m=2, s=-3), "Gunes isima gucu", "Solar luminosity"),
}

# Alternatif isimler (arama kolayligi icin)
CONST_ALIASES = {
    "isik hizi": "c", "speed of light": "c", "light speed": "c", "isikhizi": "c",
    "planck": "h", "planck sabiti": "h", "planck constant": "h",
    "hbar": "hbar", "h bar": "hbar", "indirgenmis planck": "hbar",
    "yercekimi": "g", "yer cekimi": "g", "gravity": "g", "yercekimi ivmesi": "g",
    "kutle cekim sabiti": "G", "gravitational constant": "G", "newton sabiti": "G",
    "elektron kutlesi": "me", "electron mass": "me",
    "proton kutlesi": "mp", "proton mass": "mp",
    "notron kutlesi": "mn", "neutron mass": "mn", "noytron kutlesi": "mn",
    "avogadro": "NA", "avogadro sayisi": "NA",
    "boltzmann": "kB", "boltzmann sabiti": "kB",
    "gaz sabiti": "R", "gas constant": "R", "ideal gaz sabiti": "R",
    "stefan": "sigma", "stefan boltzmann": "sigma",
    "elektron yuku": "e", "temel yuk": "e", "elementary charge": "e",
    "coulomb sabiti": "ke", "coulomb constant": "ke",
    "bohr yaricapi": "a0", "bohr radius": "a0",
    "ince yapi": "alpha", "fine structure": "alpha",
    "rydberg": "Rinf",
    "gunes kutlesi": "Msun", "solar mass": "Msun",
    "dunya kutlesi": "Mearth", "earth mass": "Mearth",
    "dunya yaricapi": "Rearth",
    "hubble": "H0", "hubble sabiti": "H0",
    "faraday": "F_faraday",
}


# --- Birim ifadesi ayristirma -----------------------------------------------
_UNIT_TOKEN = re.compile(r"([A-Za-zµΩÅ_]+)\s*(?:\^|\*\*)?\s*(-?\d+(?:\.\d+)?)?")


def parse_unit(text):
    """'km/h', 'm/s^2', 'N*m', 'kg m / s^2' -> (carpan, boyut, ofset)."""
    if text is None:
        return None
    t = text.strip()
    if t == "" or t == "1":
        return (1.0, DIMENSIONLESS, 0.0)
    t = t.replace("·", "*").replace("×", "*").replace("÷", "/")
    t = re.sub(r"\s*/\s*", " / ", t)
    t = re.sub(r"\s*\*\s*", " ", t)

    # parantezli paydayi ac:  J/(mol*K) -> J / mol / K
    m = re.match(r"^(.*?)/\s*\((.*)\)\s*$", t)
    if m:
        num, den = m.group(1), m.group(2)
        den = re.sub(r"\s+", " ", den.strip())
        t = num + " / " + " / ".join(re.split(r"[\s]+", den))

    factor = 1.0
    dim = list(DIMENSIONLESS)
    offset = 0.0
    sign = 1
    single = True
    tokens = t.split()
    count = 0
    for tok in tokens:
        # "1/m", "1/s" gibi bicimlerdeki bas 1 bir birim degil, carpan.
        if tok == "1":
            count += 1
            continue
        if tok == "/":
            sign = -1
            single = False
            continue
        mm = _UNIT_TOKEN.match(tok)
        if not mm:
            return None
        name, expo = mm.group(1), mm.group(2)
        if name not in UNITS:
            # kucuk/buyuk harf toleransi
            cand = [k for k in UNITS if k.lower() == name.lower()]
            if not cand:
                return None
            name = cand[0]
        f, d, off = UNITS[name]
        p = float(expo) if expo else 1.0
        p *= sign
        factor *= f ** p
        dim = [x + y * p for x, y in zip(dim, d)]
        if off and p == 1 and len(tokens) == 1:
            offset = off
        count += 1
        sign = 1
    if count == 0:
        return None
    return (factor, tuple(dim), offset)


def convert(value, from_unit, to_unit):
    """Deger cevirme.

    Basarisizsa (None, hata) doner. Hata, cagiranin kullanicinin dilinde
    yazabilmesi icin ("bilinmeyen"|"boyut", ayrinti) bicimindedir.
    """
    a = parse_unit(from_unit)
    b = parse_unit(to_unit)
    if a is None:
        return None, ("bilinmeyen", from_unit)
    if b is None:
        return None, ("bilinmeyen", to_unit)
    if a[1] != b[1]:
        return None, ("boyut", (from_unit, dim_label(a[1]),
                                to_unit, dim_label(b[1])))
    si = value * a[0] + a[2]
    out = (si - b[2]) / b[0]
    return out, None


# Turkce cekim eki birimin parcasi degildir: ogrenci "5 saniyede",
# "10 metrelik", "2 kilogramlik" yazar. Olculdu: "5 saniyede duruyor"
# ifadesindeki 5 degeri ZAMAN olarak okunamayip ilk hiza atandi ve
# frenleme problemi cozulemedi.
_BIRIM_EKI = ("de", "da", "te", "ta", "den", "dan", "ten", "tan",
              "lik", "lik", "luk", "luk", "lık", "lük", "ye", "ya",
              "nin", "nın", "in", "ın", "un", "un", "si", "sı", "i")


def _ek_at(unit):
    u = (unit or "").strip()
    for ek in sorted(_BIRIM_EKI, key=len, reverse=True):
        if len(u) > len(ek) + 2 and u.lower().endswith(ek):
            aday = u[:-len(ek)]
            if parse_unit(aday) is not None:
                return aday
    return None


def to_si(value, unit):
    a = parse_unit(unit)
    if a is None:
        sade = _ek_at(unit)
        if sade:
            a = parse_unit(sade)
    if a is None:
        return None, None
    return value * a[0] + a[2], a[1]


def find_constant(query):
    """Metinden sabit bul."""
    q = query.strip()
    if q in CONSTANTS:
        return q
    ql = q.lower()
    if ql in CONST_ALIASES:
        return CONST_ALIASES[ql]
    for k in CONSTANTS:
        if k.lower() == ql:
            return k
    # kismi eslesme
    best = None
    for alias, key in CONST_ALIASES.items():
        if alias in ql and (best is None or len(alias) > len(best[0])):
            best = (alias, key)
    return best[1] if best else None


def fmt(value, sig=6):
    """Sayiyi okunakli bicimle."""
    if value is None:
        return "?"
    try:
        v = float(value)
    except Exception:
        return str(value)
    if v != v or v in (float("inf"), float("-inf")):
        return str(v)
    if v == 0:
        return "0"
    a = abs(v)
    if a >= 1e6 or a < 1e-4:
        s = ("%%.%de" % (sig - 1)) % v
        mant, exp = s.split("e")
        mant = mant.rstrip("0").rstrip(".")
        return "%s×10^%d" % (mant, int(exp))
    s = ("%%.%dg" % sig) % v
    return s


def fmt_exact(value, sig=12):
    """Sabitler icin: tam sayilar bilimsel gosterime cevrilmeden yazilir.

    Isik hizi '2.998×10^8' yerine tanimi geregi tam degeri olan
    '299792458' olarak gosterilir.
    """
    try:
        v = float(value)
    except (TypeError, ValueError):
        return fmt(value, sig)
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return fmt(v, sig)


# Cevirilerde once onerilecek yaygin birimler
PREFERRED = [
    "m", "km", "cm", "mm", "nm", "kg", "g", "mg", "ton", "s", "ms", "us", "ns",
    "dk", "saat", "gun", "yil", "N", "kN", "J", "kJ", "MJ", "eV", "keV", "MeV",
    "GeV", "cal", "kcal", "kWh", "W", "kW", "MW", "hp", "Pa", "kPa", "MPa",
    "bar", "atm", "mmHg", "psi", "Hz", "kHz", "MHz", "GHz", "K", "degC",
    "degF", "A", "mA", "V", "kV", "mV", "C", "F", "uF", "nF", "pF", "ohm",
    "kohm", "T", "mT", "G", "L", "mL", "mol", "rad", "deg", "km/h", "m/s",
]
_PREF_RANK = {u: i for i, u in enumerate(PREFERRED)}


def suggest_units(dim):
    """Verilen boyuta uyan birimleri listele.

    Ayni carpani paylasan es adlar (BTU/btu gibi) tekillestirilir ve
    gunluk kullanimda yaygin olan birimler basa alinir.
    """
    by_factor = {}
    for name, (f, d, off) in UNITS.items():
        if d != tuple(dim) or len(name) > 12 or off:
            continue
        key = round(f, 12)
        cur = by_factor.get(key)
        # Ayni carpan icin: once tercih listesindeki, yoksa en kisa ad
        if cur is None:
            by_factor[key] = name
        else:
            a = _PREF_RANK.get(name, 999)
            b = _PREF_RANK.get(cur, 999)
            if (a, len(name)) < (b, len(cur)):
                by_factor[key] = name
    names = list(by_factor.values())
    names.sort(key=lambda n: (_PREF_RANK.get(n, 999), len(n), n))
    return names[:14]
