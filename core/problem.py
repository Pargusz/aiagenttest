# -*- coding: utf-8 -*-
"""Problem cozucu: soruyu CEVAPLA, formul listeleme.

Olculdu: "5 kg'lik blok 30 derece egimde, mu = 0.3, kayar mi, kayarsa
ivmesi ne?" sorusuna sistem sürtünme formulunu ve egik duzlem bagintisini
LISTELEDI, sonra "degerleri verirseniz hesaplarim" dedi — oysa degerler
soruda vardi. Bir profesor once karar verir (tan30 = 0,577 > 0,3 oldugundan
kayar), sonra hesaplar (a = 2,36 m/s²).

Bu modul uc isi sirayla yapar:

1. **Verilenleri oku** — dogal dildeki "5 kg", "30 derece", "mu = 0.3".
2. **Kosulu degerlendir** — "kayar mi", "yuzer mi", "kopar mi" gibi
   sorularin fiziksel olcutu vardir; once bu olcut hesaplanir ve karar
   yazilir.
3. **Sayisal cozum** — geriye kalan tek bilinmeyen SymPy ile cozulur ve
   adimlar gosterilir.

Karar olcutleri elle yazilmistir: hangi buyuklugun hangisiyle
karsilastirilacagi fizik bilgisidir, korpustan cikarilamaz.
"""
import math
import re

import sympy as sp

from . import formulas, nlu, units


# ── Karar olcutleri ─────────────────────────────────────────────────────────
# (anahtar kelimeler, gereken degiskenler, olcut fonksiyonu, aciklama)
# Olcut fonksiyonu (deger sozlugu) alir ve (karar_bool, sol, sag, metin)
# dondurur.

def _kayar_mi(v):
    """Egik duzlemde kayma: tan(theta) > mu ise kayar."""
    th = math.radians(v["theta_derece"])
    return (math.tan(th) > v["mu"], math.tan(th), v["mu"])


def _yuzer_mi(v):
    """Yuzme: cismin yogunlugu sivininkinden kucukse yuzer."""
    return (v["yogunluk_cisim"] < v["yogunluk_sivi"],
            v["yogunluk_cisim"], v["yogunluk_sivi"])


def _kacar_mi(v):
    """Kacis: hiz kacis hizini asiyorsa cisim kacar."""
    kacis = math.sqrt(2 * 6.674e-11 * v["kutle_gezegen"] / v["yaricap"])
    return (v["hiz"] > kacis, v["hiz"], kacis)


KARAR_OLCUTLERI = [
    {
        "ad": "egik_duzlemde_kayma",
        "kw": r"\b(kayar m[iı]|kayacak m[iı]|kaymaya baslar|hareket eder mi|"
              r"dengede (kalir|durur)|will it slide|does it slide)\b",
        "gerekli": ("theta_derece", "mu"),
        "olcut": _kayar_mi,
        "sol_ad": "tan θ", "sag_ad": "μ",
        "evet": "tan θ > μ olduğundan blok **kayar**.",
        "hayir": "tan θ ≤ μ olduğundan blok **kaymaz**, yerinde durur "
                 "(statik sürtünme yeterli).",
        "evet_en": "Since tan θ > μ the block **slides**.",
        "hayir_en": "Since tan θ <= μ the block **stays put**.",
        "sonraki_formul": "egik_duzlem",
    },
    {
        "ad": "yuzme",
        "kw": r"\b(yuzer m[iı]|batar m[iı]|yuzecek mi|will it float|does it "
              r"sink)\b",
        "gerekli": ("yogunluk_cisim", "yogunluk_sivi"),
        "olcut": _yuzer_mi,
        "sol_ad": "ρ_cisim", "sag_ad": "ρ_sıvı",
        "evet": "Cismin yoğunluğu sıvıdan küçük olduğundan **yüzer**.",
        "hayir": "Cismin yoğunluğu sıvıdan büyük olduğundan **batar**.",
        "evet_en": "The body **floats**.", "hayir_en": "The body **sinks**.",
        "sonraki_formul": "arsimet",
    },
]


# Dogal dilden ozel buyukluk okuma: aci, surtunme katsayisi, yogunluk
_ACI = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:derece|°|derecelik)", re.I)
_MU = re.compile(r"(?:mu|μ|surtunme\s*katsayisi|katsayisi)\s*[:=]?\s*"
                 r"(\d+(?:[.,]\d+)?)", re.I)


def _sayi(s):
    return float(str(s).replace(",", "."))


def ozel_degerler(metin):
    """Karar olcutlerinin ihtiyac duydugu buyuklukleri metinden oku."""
    v = {}
    m = _ACI.search(metin or "")
    if m:
        v["theta_derece"] = _sayi(m.group(1))
    m = _MU.search(metin or "")
    if m:
        v["mu"] = _sayi(m.group(1))
    return v


def karar_ver(soru, lang="tr"):
    """Soruda bir karar olcutu varsa degerlendir.

    Doner: (metin, olcut_kaydi, degerler) — yoksa (None, None, {}).
    """
    n = nlu.norm(soru or "")
    ozel = ozel_degerler(soru)
    for olcut in KARAR_OLCUTLERI:
        if not re.search(olcut["kw"], n):
            continue
        eksik = [g for g in olcut["gerekli"] if g not in ozel]
        if eksik:
            continue
        try:
            karar, sol, sag = olcut["olcut"](ozel)
        except Exception:
            continue
        tr = lang == "tr"
        satirlar = ["**" + ("Önce karar: koşul sağlanıyor mu?" if tr
                            else "First, the criterion") + "**", ""]
        satirlar.append("`%s = %.4g`   vs   `%s = %.4g`"
                        % (olcut["sol_ad"], sol, olcut["sag_ad"], sag))
        satirlar.append("")
        satirlar.append("→ " + (olcut["evet"] if karar else olcut["hayir"])
                        if tr else
                        "→ " + (olcut["evet_en"] if karar else olcut["hayir_en"]))
        return "\n".join(satirlar), olcut, ozel
    return None, None, {}


def _oku_sayi(x):
    """Sayiyi okunakli yaz.

    "%.4g" biçimi 83600 sayisini "8.36e+04" yapiyordu — dogru ama bir ders
    metninde okunmuyor. Makul aralikta duz yaziyoruz, uc mertebelerde
    bilimsel gosterime geciyoruz.
    """
    a = abs(x)
    if a == 0:
        return "0"
    if 1e-3 <= a < 1e7:
        # Tam sayiysa ondalik gosterme
        if abs(x - round(x)) < 1e-9 * max(a, 1):
            return "%d" % round(x)
        return ("%.4g" % x)
    us = "%.4e" % x
    taban, kuvvet = us.split("e")
    return "%s×10^%d" % (taban.rstrip("0").rstrip("."), int(kuvvet))


def _sembolik_coz(f, bilinen, hedef):
    """Formulu hedef icin coz ve sayisal sonucu dondur."""
    try:
        _t, cozumler, _e = formulas.solve_for(f, bilinen, target=hedef)
    except Exception:
        return None
    gercel = [x for x in cozumler if isinstance(x, float)]
    if not gercel:
        return None
    return kok_sec(f, hedef, gercel)


# ── Sorulan buyugu belirleme ────────────────────────────────────────────────
# Olculdu: "5 ohm ve 10 ohm paralel bagli esdeger direnc nedir" sorusunda
# uc degisken de ohm cinsindendir; sistem 10'u R1'e, 5'i Rp'ye atadi ve
# R2'yi cozdu. Oysa SORULAN Rp'dir. Sorulan buyukluk once belirlenip
# deger atamasindan cikarilmalidir.

# Bu "semboller" aslinda gunluk kelimelerdir; sembol olarak aranmazlar.
_KELIME_SEMBOL = {"a", "an", "the", "in", "of", "at", "on", "to", "is",
                  "it", "by", "as", "or", "if", "be", "no", "so", "we",
                  "ve", "ya", "da", "de", "bu", "su", "o", "ki", "mi"}

# Degiskenlerin adlarinda sik gecen, tek basina ayirt edici OLMAYAN kelimeler
_GENEL_AD = {"enerji", "energy", "deger", "value", "sayi", "number",
             "buyukluk", "quantity", "sabit", "constant", "katsayi",
             "coefficient", "fark", "difference", "toplam", "total",
             "ilk", "son", "first", "final", "initial"}


def _yumusak_kalip(ad):
    """Turkce unsuz yumusamasini da taniyan arama kalibi.

    "agirlik" + iyelik eki -> "agirligi" (k -> g). Duz onek eslesmesi
    bunu kaciriyordu ve olculdu: "cismin AGIRLIGI kac newton" sorusunda
    hedef, verilmis olan kutle secildi.
    """
    if not ad:
        return None
    son = ad[-1]
    yumusak = {"k": "[kg]", "p": "[pb]", "t": "[td]", "c": "[cc]"}
    govde = re.escape(ad[:-1])
    if son in yumusak:
        return r"(?<!\w)%s%s\w{0,3}(?!\w)" % (govde, yumusak[son])
    return r"(?<!\w)%s\w{0,3}(?!\w)" % re.escape(ad)


def hedef_tahmin(f, soru, lang="tr"):
    """Soruda ADIYLA anilan ve sorulan degiskeni bul (yoksa None)."""
    n = nlu.norm(soru or "")
    adaylar = []
    # Ogrenci cogu zaman adi degil SEMBOLU yazar: "V si en yuksek",
    # "F kactir". Sembol tek harflidir ama YALNIZ basina duruyorsa
    # ayirt edicidir. Olculdu: "bu hareketlinin V si" ifadesinde hedef
    # bulunamiyor ve zincir yanlis buyuklugu ariyordu.
    #
    # Sayidan hemen sonra gelen harf BIRIMDIR, sembol degil: "30 m"
    # ifadesindeki m, kutle sembolu sanilmamali.
    for sym in f["vars"]:
        # Tek harfli sembol, o dilde bir KELIME olabilir. Olculdu:
        # "a ball dropped from 100 m" cumlesindeki Ingilizce artikel
        # "a", ivme sembolu sanildi ve hedef yanlis secildi.
        if nlu.norm(sym) in _KELIME_SEMBOL:
            continue
        # Tek harfli sembole EK verilmez: "V" sembolu Turkce "ve"
        # kelimesini tutuyordu ve "220 V ve 5 A" sorusunda hedef V
        # seciliyordu (olculdu). Iki harften uzun sembollerde ek serbest.
        _s = nlu.norm(sym)
        kalip = ((r"(?<![\w])%s(?![\w])" % re.escape(_s)) if len(_s) <= 1
                 else (r"(?<![\w])%s(?:'\w*|\w{0,2})?(?![\w])"
                       % re.escape(_s)))
        for m in re.finditer(kalip, n):
            onceki = n[:m.start()].rstrip()
            if onceki and re.search(r"[\d.,]$", onceki):
                continue          # birim olarak kullanilmis
            adaylar.append((len(sym) + 6, sym))
            break

    for sym, (tr_ad, en_ad, _u) in f["vars"].items():
        for ad in (tr_ad, en_ad):
            a = nlu.norm(ad or "").strip()
            if len(a) < 4:
                continue
            if re.search(_yumusak_kalip(a), n):
                adaylar.append((len(a), sym))
                continue
            # Cok kelimeli ad birebir gecmiyorsa AYIRT EDICI kelimesi
            # aranir: degiskenin adi "fall time" iken soru "time to
            # reach the ground" diyor (olculdu: cevap sure yerine hiz
            # geliyordu). Puani dusuk tutulur ki birebir eslesme onde
            # kalsin.
            for kelime in a.split():
                if len(kelime) < 4 or kelime in _GENEL_AD:
                    continue
                if re.search(r"(?<!\w)%s\w{0,3}(?!\w)" % re.escape(kelime),
                             n):
                    adaylar.append((len(kelime) - 3, sym))
                    break
    if not adaylar:
        return None

    # SORU KELIMESINE YAKINLIK. Olculdu: "kutlesi 5 kg olan cismin
    # agirligi kac newton" sorusunda hedef "kutle" secildi — oysa kutle
    # VERILMIS, sorulan agirliktir. Sorulan buyukluk, soru kelimesinin
    # yanindaki buyukluktur.
    soru_yeri = None
    for m in re.finditer(r"\b(kac|nedir|ne kadar|bul|bulunuz|hesapla|"
                         r"kactir|what|find|calculate)\b", n):
        soru_yeri = m.start()
    if soru_yeri is not None:
        yeni_adaylar = []
        for puan, sym in adaylar:
            yer = None
            for ad in (f["vars"][sym][0], f["vars"][sym][1], sym):
                a = nlu.norm(ad or "").strip()
                if not a:
                    continue
                m = re.search(_yumusak_kalip(a), n)
                if m:
                    yer = m.start() if yer is None else min(yer, m.start())
            # Soru kelimesine yakinlik, puana eklenir (en fazla +8)
            if yer is not None:
                uzaklik = abs(soru_yeri - yer)
                yeni_adaylar.append((puan + max(0, 8 - uzaklik // 12), sym))
            else:
                yeni_adaylar.append((puan, sym))
        adaylar = yeni_adaylar

    # En UZUN eslesme kazanir: "esdeger direnc", "direnc"ten daha ozeldir.
    adaylar.sort(reverse=True)
    return adaylar[0][1]


def hedef_siralamasi(f, soru, lang="tr"):
    """Adi soruda gecen TUM degiskenler, en olasidan az olasiya.

    hedef_tahmin tek bir sembol dondurur; ama soruda birden fazla
    buyuklugun adi gecebilir. Olculdu: "surtunme katsayisi 0.4 olan
    10 kg cisme etkiyen surtunme kuvveti" sorusunda hem katsayi hem
    kuvvet adlandirilmis; uzun olan (katsayi) kazandi, oysa o VERILMIS.
    Cagiran taraf bilinenleri eleyip siradakini secebilmeli.
    """
    n = nlu.norm(soru or "")
    adaylar = []
    for sym, (tr_ad, en_ad, _u) in f["vars"].items():
        for ad in (tr_ad, en_ad):
            a = nlu.norm(ad or "").strip()
            if len(a) < 4:
                continue
            if re.search(_yumusak_kalip(a), n):
                adaylar.append((len(a), sym))
                break
    adaylar.sort(reverse=True)
    out = []
    for _p, sym in adaylar:
        if sym not in out:
            out.append(sym)
    return out


# ── Senaryo bilgisi ─────────────────────────────────────────────────────────
# Bazi ifadeler bir DEGERI dogrudan belirtir: "yukari atiliyor" demek
# ivmenin -g olmasi demektir. Bu fizik bilgisidir, metinden cikarilamaz.

SENARYOLAR = [
    # Parcacigin ADI yukunu ve kutlesini belirler. Olculdu: "elektron
    # 100 V ile hizlandirilirsa kazandigi enerji" sorusunda q verilmedigi
    # icin hesap yapilamiyordu; oysa "elektron" demek q = e demektir.
    {"kw": r"\belektron\b|\belectron\b",
     "degerler": {"q": 1.602176634e-19, "m": 9.1093837015e-31},
     "not_tr": "Elektron: `q = e = 1,602×10⁻¹⁹ C`, "
               "`m = 9,109×10⁻³¹ kg`.",
     "not_en": "Electron: q = e, m = 9.109e-31 kg."},
    {"kw": r"\bproton\b",
     "degerler": {"q": 1.602176634e-19, "m": 1.67262192369e-27},
     "not_tr": "Proton: `q = +e`, `m = 1,673×10⁻²⁷ kg`.",
     "not_en": "Proton: q = +e, m = 1.673e-27 kg."},
    {"kw": r"\balfa (parcacig|tanecig)",
     "degerler": {"q": 3.204353268e-19, "m": 6.6446573357e-27},
     "not_tr": "Alfa parçacığı: `q = 2e`, `m = 6,645×10⁻²⁷ kg`.",
     "not_en": "Alpha particle: q = 2e."},
    {"kw": r"\b(duruyor|durana kadar|duruncaya|durur|yavaslay|"
           r"comes to rest|stops|decelerat|brakes|slows to)\w*",
     "degerler": {"v": 0.0},
     # Verilen hiz ILK hizdir; son hiz sifirdir.
     "hiz_ilk": True,
     "not_tr": "Cisim duruyor: son hız `v = 0`.",
     "not_en": "The body stops: final speed v = 0."},
    {"kw": r"\b(yukari (atil|firlat|atiliy|atilan)|dikey atis|"
           r"yukari dogru atil|thrown upward|thrown up|"
           r"launched upward)",
     "degerler": {"a": -9.80665},
     # Atis probleminde verilen hiz ILK hizdir; sorulan sonraki hizdir.
     "hiz_ilk": True,
     "not_tr": "Yukarı atış: ivme aşağı yönde, `a = −g = −9,81 m/s²`.",
     "not_en": "Thrown upward: a = -g."},
    # Serbest birakmada ASAGI yonu pozitif almak dogaldir: yol da hiz da
    # ivme de ayni yondedir, isaret karisikligi olmaz. Olculdu: asagi
    # yon negatif alininca v² = 2a·dx negatif cikiyor ve cozum bulunmuyordu.
    {"kw": r"\b(serbest birak|birakil|birakiliyor|dusuruluyor|"
           r"serbest dus|yuksekten dus|yere carp|"
           r"dropped|released from rest|falls from|free fall)",
     "degerler": {"a": 9.80665, "v0": 0.0},
     "not_tr": "Serbest bırakma: `v₀ = 0`, aşağı yön pozitif alındı, "
               "`a = g = 9,81 m/s²`.",
     "not_en": "Released from rest with downward positive: v0 = 0, a = g."},
]


# ── Malzeme ve baglam sabitleri ────────────────────────────────────────────
# Olculdu: "2 kg suyu 20 dereceden 80 dereceye isitmak icin gereken isi"
# sorusu cozulemiyordu, cunku SUYUN OZGUL ISISI bilinmiyordu. Ogrenci
# bunu tablodan bakar; sistemin de bilmesi gerekir. Ayni sey buzun
# erime isisi, camin kirilma indisi, hidrojenin atom numarasi icin de
# gecerli.
#
# Bu degerler FIZIK bilgisidir ve elle yazilmistir; metinden cikarilamaz.
MALZEME = [
    {"kw": r"\bsu(yu|yun|ya|da)?\b|\bwater\b",
     "degerler": {"c": 4186.0},
     "not_tr": "Suyun özgül ısısı `c = 4186 J/(kg·K)` alındı.",
     "not_en": "Specific heat of water: 4186 J/(kg K)."},
    {"kw": r"\bbuz(u|un|dan)?\b|\bice\b",
     "degerler": {"L": 334000.0, "c": 2100.0},
     "not_tr": "Buzun erime gizli ısısı `L = 3,34×10⁵ J/kg`, özgül ısısı "
               "`c = 2100 J/(kg·K)` alındı.",
     "not_en": "Ice: latent heat 3.34e5 J/kg, specific heat 2100."},
    {"kw": r"\bbuhar(lastir|lasma)|\bkaynat|\bevaporat|\bboil",
     "degerler": {"L": 2260000.0},
     "not_tr": "Suyun buharlaşma gizli ısısı `L = 2,26×10⁶ J/kg` alındı.",
     "not_en": "Latent heat of vaporisation: 2.26e6 J/kg."},
    {"kw": r"\bhavadan cam\w*|\bhava\w*.{0,12}cam\w*|"
           r"\bair.{0,8}glass\b",
     "degerler": {"n1": 1.0, "n2": 1.5},
     "not_tr": "Havanın kırılma indisi `n₁ = 1,00`, camınki `n₂ = 1,50` "
               "alındı.",
     "not_en": "Air n1 = 1.00, glass n2 = 1.50."},
    {"kw": r"\bcamdan hava\w*|\bglass.{0,8}air\b",
     "degerler": {"n1": 1.5, "n2": 1.0},
     "not_tr": "Camın kırılma indisi `n₁ = 1,50`, havanınki `n₂ = 1,00` "
               "alındı.",
     "not_en": "Glass n1 = 1.50, air n2 = 1.00."},
    {"kw": r"\bhavadan su\w*|\bhava\w*.{0,12}\bsu(ya|da)\b",
     "degerler": {"n1": 1.0, "n2": 1.33},
     "not_tr": "Hava `n₁ = 1,00`, su `n₂ = 1,33` alındı.",
     "not_en": "Air n1 = 1.00, water n2 = 1.33."},
    {"kw": r"\bhidrojen\b|\bhydrogen\b",
     "degerler": {"Z": 1.0},
     "not_tr": "Hidrojen için atom numarası `Z = 1`.",
     "not_en": "Hydrogen: Z = 1."},
    {"kw": r"\bdusey (yukari )?(atil|firlat)|\bdik(ey)? yukari\b|"
           r"\bvertically upward\b",
     "degerler": {"theta": 1.5707963268},
     "not_tr": "Düşey atış: `θ = 90°`.",
     "not_en": "Vertical throw: theta = 90 degrees."},
    {"kw": r"\bdur(gun|an|uyorken)\b|"
           r"\bilk hiz(i|siz)? (sifir|yok)\b|\bfrom rest\b|"
           r"\bstarting from rest\b|\bharekete gec\w*",
     "degerler": {"v0": 0.0},
     "not_tr": "Durgun halden başlıyor: `v₀ = 0`.",
     "not_en": "Starts from rest: v0 = 0."},
    {"kw": r"\bdunya (yuzey|yuzeyinden)|\bearth'?s surface\b",
     "degerler": {"M": 5.972e24, "R": 6.371e6, "r": 6.371e6},
     "not_tr": "Dünya için `M = 5,97×10²⁴ kg`, `R = 6,37×10⁶ m` alındı.",
     "not_en": "Earth: M = 5.97e24 kg, R = 6.37e6 m."},
]


# "20 dereceden 80 dereceye" gibi ifadeler bir FARK bildirir. Olculdu:
# "2 kg suyu 20 dereceden 80 dereceye isitmak" sorusunda sicaklik farki
# (dT = 60 K) hic okunamiyordu ve isi hesabi yapilamiyordu.
_FARK = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(?:derece|°|C|K|santigrat)?\s*"
    r"(?:den|dan|'den|'dan)\s+"
    r"(\d+(?:[.,]\d+)?)\s*(?:derece|°|C|K|santigrat)?\s*"
    r"(?:ye|ya|'ye|'ya|e|a)\b", re.I)


def fark_degerleri(soru):
    """'X dereceden Y dereceye' -> {dT: Y-X}. Yoksa bos."""
    m = _FARK.search(soru or "")
    if not m:
        return {}
    try:
        a = float(m.group(1).replace(",", "."))
        b = float(m.group(2).replace(",", "."))
    except ValueError:
        return {}
    return {"dT": b - a, "dt": b - a}


# Isik hizinin kati olarak verilen hizlar: "0.6c", "0,8 c".
_ISIK_KATI = re.compile(r"(\d+(?:[.,]\d+)?)\s*c\b(?!\w)")


def isik_hizi_degerleri(soru):
    """'0.6c' -> {v: 1.8e8}. Olculdu: bu bicim hic okunamiyordu."""
    m = _ISIK_KATI.search(soru or "")
    if not m:
        return {}
    try:
        kat = float(m.group(1).replace(",", "."))
    except ValueError:
        return {}
    if not (0 < kat <= 1):
        return {}
    return {"v": kat * 299792458.0}


# Soruda acikca yazilmayan ama FIZIKTEN bilinen acilar. Bir kuvvet
# "yol boyunca" uygulanmissa aci sifirdir; manyetik alandaki tel
# aksi soylenmedikce alana diktir.
VARSAYILAN_ACI = [
    (r"\bis\b|\byaptigi is\b|\byapilan is\b|\bwork done\b",
     "theta", 0.0,
     "Kuvvet yol boyunca kabul edildi: `θ = 0`, `cos θ = 1`.",
     "Force taken along the displacement: theta = 0."),
    (r"\bmanyetik alan\w*.{0,40}\btel\w*|\btel\w*.{0,40}"
     r"\bmanyetik\w*|\bakim tasiyan tel\w*",
     "theta", 1.5707963268,
     "Tel alana dik kabul edildi: `θ = 90°`, `sin θ = 1`.",
     "Wire taken perpendicular to the field: theta = 90 degrees."),
]


def varsayilan_aci(soru, f):
    """Formul bir aci istiyorsa ve soruda yoksa fizikten doldur."""
    n = nlu.norm(soru or "")
    out, notlar = {}, []
    if re.search(r"\d+\s*(derece|°)", n):
        return out, notlar          # aci acikca verilmis
    for kalip, sym, deger, tr, en in VARSAYILAN_ACI:
        if sym in (f or {}).get("vars", {}) and re.search(kalip, n):
            out[sym] = deger
            notlar.append({"not_tr": tr, "not_en": en})
            break
    return out, notlar


def malzeme_degerleri(soru):
    """Metnin ima ettigi malzeme sabitleri: (degerler, notlar)."""
    n = nlu.norm(soru or "")
    degerler, notlar = {}, []
    for m in MALZEME:
        if re.search(m["kw"], n):
            for k, v in m["degerler"].items():
                degerler.setdefault(k, v)
            notlar.append(m)
    return degerler, notlar


def senaryo_degerleri(soru):
    """Ifadenin ima ettigi degerleri dondur: (degerler, notlar)."""
    n = nlu.norm(soru or "")
    degerler, notlar = {}, []
    for sen in SENARYOLAR:
        if re.search(sen["kw"], n):
            degerler.update(sen["degerler"])
            notlar.append(sen)
    # Malzeme sabitleri (suyun ozgul isisi, camin kirilma indisi...)
    md, mn = malzeme_degerleri(soru)
    for k, v in md.items():
        degerler.setdefault(k, v)
    notlar.extend(mn)
    # "20 dereceden 80 dereceye" -> dT = 60
    for k, v in fark_degerleri(soru).items():
        degerler.setdefault(k, v)
    # "0.6c" -> v = 1.8e8 m/s
    for k, v in isik_hizi_degerleri(soru).items():
        degerler.setdefault(k, v)
    return degerler, notlar


# ── Fiziksel makullugu denetle ──────────────────────────────────────────────
# Olculdu: "12 V kaynaga seri bagli 4 ohm ve 8 ohm direnclerden gecen akim"
# sorusuna sistem "R2 = -4 ohm" cevabini verdi. Negatif direnc diye bir sey
# yoktur; boyle bir sonucu basmaktansa cevap vermemek dogrudur.

NEGATIF_OLAMAZ = {
    "ohm": "direnc", "F": "siga", "H": "indüktans", "K": "mutlak sicaklik",
    "kg": "kutle", "m^3": "hacim", "s": "sure", "Hz": "frekans",
    "kg/m^3": "yogunluk", "J/K": "entropi kapasitesi", "mol": "mol sayisi",
}


# Girdi denetimi: bazi buyuklukler NEGATIF OLAMAZ. Olculdu: "-5 kg
# kutleli cismin kinetik enerjisi 10 m/s hizda" sorusuna sistem
# "Ek = -250 J" dedi. Negatif kutle de negatif kinetik enerji de yoktur;
# boyle bir girdiyi sessizce kabul etmek, kullaniciyi yaniltmaktir.
GIRDI_NEGATIF_OLAMAZ = {
    "kg": "kütle", "K": "mutlak sıcaklık", "m^3": "hacim",
    "kg/m^3": "yoğunluk", "ohm": "direnç", "F": "sığa", "H": "indüktans",
    "mol": "mol sayısı", "s": "süre", "Hz": "frekans",
}


def girdi_denetle(f, sayisal, lang="tr"):
    """Verilen degerler fiziksel olarak mumkun mu? Metin ya da None."""
    tr = lang == "tr"
    hatalar = []
    for sym, deger in (sayisal or {}).items():
        if sym not in f["vars"]:
            continue
        birim = f["vars"][sym][2]
        ad = f["vars"][sym][0] if tr else f["vars"][sym][1]
        try:
            d = float(deger)
        except (TypeError, ValueError):
            continue
        if d < 0 and birim in GIRDI_NEGATIF_OLAMAZ:
            hatalar.append((sym, ad, d, birim,
                            GIRDI_NEGATIF_OLAMAZ[birim]))
    if not hatalar:
        return None
    L = lambda a, b: a if tr else b
    satirlar = ["### " + L("Bu değer fiziksel değil",
                           "This value is not physical"), ""]
    for sym, ad, d, birim, tur in hatalar:
        satirlar.append(
            L("`%s` = %g %s verdiniz. **%s negatif olamaz.**"
              % (sym, d, birim, tur.capitalize()),
              "`%s` = %g %s is not possible: %s cannot be negative."
              % (sym, d, birim, tur)))
    satirlar.append("")
    satirlar.append(L(
        "Hesabı yine de yapsaydım anlamsız bir sayı çıkardı — örneğin "
        "negatif kütleyle kinetik enerji negatif görünür, oysa kinetik "
        "enerji hiçbir zaman negatif olamaz (½mv², v² ≥ 0).",
        "Computing anyway would produce a meaningless number."))
    satirlar.append("")
    satirlar.append("_" + L(
        "Değeri düzeltip tekrar sorarsanız hesabı yaparım.",
        "Fix the value and ask again.") + "_")
    return "\n".join(satirlar)


def kok_sec(f, hedef, kokler):
    """Birden fazla gercel kok varsa FIZIKSEL olani sec.

    Olculdu: "havadan cama 30 derece ile giren isigin kirilma acisi"
    sorusunda SymPy once t2 = π − asin(...) kokunu donduruyordu; bu
    matematiksel olarak dogru ama 160 derecelik bir kirilma acisi
    fiziksel degildir. Kirilma ve gelme acilari dar acidir.
    """
    if not kokler:
        return None
    birim = (f["vars"].get(hedef) or ("", "", ""))[2]
    if birim in ("rad", "radyan"):
        dar = [x for x in kokler if 0 <= x <= 1.5707963268 + 1e-9]
        if dar:
            return dar[0]
    pozitif = [x for x in kokler if x >= 0]
    return (pozitif or kokler)[0]


def makul_mu(f, hedef, deger):
    """Sonuc fiziksel olarak kabul edilebilir mi? (bool, sebep)"""
    try:
        d = float(deger)
    except (TypeError, ValueError):
        return True, ""
    birim = (f["vars"].get(hedef) or ("", "", ""))[2]
    if d < 0 and birim in NEGATIF_OLAMAZ:
        return False, ("`%s` bir %s ve negatif olamaz"
                       % (hedef, NEGATIF_OLAMAZ[birim]))
    # Yaricap, uzunluk gibi buyuklukler de negatif olamaz (isaretli
    # yer degistirme haric; onun adi "dx" ya da "yer degistirme"dir).
    ad = (f["vars"].get(hedef) or ("", "", ""))[0].lower()
    if d < 0 and birim == "m" and any(
            w in ad for w in ("yaricap", "uzunluk", "genislik", "kalinlik",
                              "yukseklik", "mesafe")):
        return False, "`%s` negatif olamaz" % hedef
    return True, ""


# ── Iki adimli devre problemi ───────────────────────────────────────────────
# Olculdu: "12 V kaynaga seri bagli 4 ohm ve 8 ohm direnclerden gecen akim"
# en sik gelen odev kalibi ve tek bir bagintiyla cozulemiyor. Once esdeger
# direnc, sonra Ohm yasasi. Adimlarin ikisi de gosterilir.

_OHM_DEGER = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:ohm|Ω|ω)\b", re.I)
_VOLT_DEGER = re.compile(r"(\d+(?:[.,]\d+)?)\s*(?:V|volt)\b")


def devre_zinciri(soru, lang="tr"):
    """Kaynak + iki direnc -> esdeger direnc -> akim. Yoksa None."""
    n = nlu.norm(soru or "")
    if not re.search(r"\b(akim|current|gecen akim)\b", n):
        return None
    seri = bool(re.search(r"\bseri\b|\bin series\b", n))
    paralel = bool(re.search(r"\bparalel\b|\bparallel\b", n))
    if not (seri or paralel):
        return None
    dirençler = [_sayi(x) for x in _OHM_DEGER.findall(soru or "")]
    gerilimler = [_sayi(x) for x in _VOLT_DEGER.findall(soru or "")]
    if len(dirençler) < 2 or not gerilimler:
        return None
    V = gerilimler[0]
    R1, R2 = dirençler[0], dirençler[1]
    if seri:
        Req = R1 + R2
        baginti, ad = "Rs = R1 + R2", "Seri" if lang == "tr" else "Series"
    else:
        if R1 + R2 == 0:
            return None
        Req = R1 * R2 / (R1 + R2)
        baginti = "Rp = R1·R2/(R1 + R2)"
        ad = "Paralel" if lang == "tr" else "Parallel"
    if Req <= 0:
        return None
    I = V / Req
    tr = lang == "tr"
    s = ["### " + ("Çözüm — iki adımlı devre" if tr
                   else "Solution — two-step circuit"), "",
         "**1. " + ("Eşdeğer direnç" if tr else "Equivalent resistance")
         + "**", "",
         "`%s`" % baginti, "",
         "`R = %s` → **%s Ω**" % (
             ("%g + %g" % (R1, R2)) if seri
             else ("%g·%g/(%g+%g)" % (R1, R2, R1, R2)), _oku_sayi(Req)),
         "",
         "**2. " + ("Ohm yasası" if tr else "Ohm's law") + "**", "",
         "`I = V/R = %g/%s`" % (V, _oku_sayi(Req)), "",
         "## `I` = **%s A**" % _oku_sayi(I), ""]
    if seri:
        s.append("_" + ("Seri devrede akım her elemandan aynıdır; "
                        "gerilim dirençlerle orantılı bölünür." if tr else
                        "In series the current is common to all elements.")
                 + "_")
    else:
        s.append("_" + ("Paralel devrede gerilim ortaktır; akım ters "
                        "orantılı bölünür: küçük dirençten büyük akım geçer."
                        if tr else
                        "In parallel the voltage is common; the smaller "
                        "resistor carries more current.") + "_")
    return "\n".join(s)


# ── Oncul okuma: sorunun kendi verdigi bilgiyi kacirma ─────────────────────
# Olculdu: "SURTUNMESIZ alanda ... SURTUNME degerini hesapla" sorusuna
# sistem basit harmonik hareket dersi anlatti. Oysa cevap sorunun
# icindeydi: surtunmesiz denmisse surtunme sifirdir.
#
# Bu tur sorular ogrenciyi de sinar: onculu okumadan formule atlayan
# yanilir. Bir cozucunun ilk isi VERILENLERI okumaktir.

ONCULLER = [
    {"kw": r"\bsurtunmesiz\b|\bsurtunme (yok|ihmal|sifir)|"
           r"\bfrictionless\b|\bno friction\b",
     "sorulan": r"\bsurtunme\w*\b|\bfriction\b",
     "deger": 0.0, "birim": "N",
     "tr": "Soruda ortam **sürtünmesiz** denmiş. O hâlde sürtünme "
           "kuvveti her noktada **sıfırdır** — hızın en büyük olduğu "
           "noktada da, başka bir noktada da.",
     "en": "The problem states a frictionless medium, so the friction "
           "force is zero everywhere."},
    {"kw": r"\bhava direnci (yok|ihmal|olmadig)|\bhavasiz ortam\b|"
           r"\bno air resistance\b|\bneglect(ing)? air\b",
     "sorulan": r"\bhava direnci\b|\bsurukleme\b|\bdrag\b",
     "deger": 0.0, "birim": "N",
     "tr": "Soruda **hava direnci ihmal ediliyor** denmiş; o hâlde "
           "sürükleme kuvveti **sıfırdır**.",
     "en": "Air resistance is neglected, so the drag force is zero."},
    {"kw": r"\byalitilmis\b|\byalitkan kap\b|\badyabatik\b|"
           r"\bisolated\b|\badiabatic\b",
     # Olculdu: "yalitilmis sistemde disariya verilen isi kac joule"
     # sorusu bu kalibi tutmayip makale ozetlerine dusuyordu.
     "sorulan": r"\bisi alisverisi\b|\bisi transferi\b|\bQ\b|"
                r"\b(disariya |cevreye |ortama )?(verilen|alinan|"
                r"kaybedilen|kazanilan) isi\b|\bisi kac\b|"
                r"\bheat exchange\b|\bheat (lost|gained|transferred)\b",
     "deger": 0.0, "birim": "J",
     "tr": "Sistem **yalıtılmış/adyabatik** denmiş: dışarıyla ısı "
           "alışverişi **yoktur** (Q = 0).",
     "en": "The system is isolated/adiabatic, so Q = 0."},
    {"kw": r"\bsabit hizla\b|\bduzgun hizla\b|\bdegismeyen hizla\b|"
           r"\bconstant (speed|velocity)\b",
     "sorulan": r"\bivme\w*\b|\bkuvvet\w*\b|\bacceleration\b|"
                r"\bforce\b",
     "deger": 0.0, "birim": "m/s^2",
     # Sorulan KUVVETSE birim newton olmali. Olculdu: "sabit hizla
     # giden trenin uzerindeki net kuvvet" sorusuna "0 m/s^2" dendi.
     "birim_secimi": [(r"\bkuvvet\w*\b|\bforce\b", "N"),
                      (r"\bivme\w*\b|\bacceleration\b", "m/s^2")],
     "tr": "**Sabit hızla** gidiyorsa ivme **sıfırdır**; Newton'un "
           "2. yasasına göre net kuvvet de sıfırdır.",
     "en": "At constant velocity the acceleration and the net force "
           "are zero."},
    {"kw": r"\bdengede\b|\bdurgun\b|\bhareketsiz\b|"
           r"\bin equilibrium\b|\bat rest\b",
     "sorulan": r"\bnet kuvvet\b|\bivme\w*\b|\bnet force\b|"
                r"\bacceleration\b",
     "deger": 0.0, "birim": "N",
     "birim_secimi": [(r"\bivme\w*\b|\bacceleration\b", "m/s^2"),
                      (r"\bkuvvet\w*\b|\bforce\b", "N")],
     "tr": "Cisim **dengede** olduğuna göre net kuvvet ve ivme "
           "**sıfırdır**.",
     "en": "In equilibrium the net force and acceleration vanish."},
]


def oncul_sadelestir(soru):
    """Onculun sifirladigi buyuklugu soru metninden cikar.

    Geriye kalan metin, sorudaki DIGER buyuklugu hesaplamak icin
    kullanilir: "surtunmesiz ... surtunme degerini hesapla" sorusunda
    surtunme sifirdir, ama ogrenci maksimum hizi da merak eder.
    """
    n = nlu.norm(soru or "")
    for o in ONCULLER:
        if re.search(o["kw"], n) and re.search(o["sorulan"], n):
            kalan = re.sub(o["sorulan"], " ", n)
            kalan = re.sub(r"\b(degerini|degeri|kuvvetini|kuvveti)\b",
                           " ", kalan)
            return re.sub(r"\s+", " ", kalan).strip()
    return None


def oncul_cevabi(soru, lang="tr"):
    """Sorunun kendi onculu cevabi veriyorsa dogrudan soyle.

    Doner: metin ya da None.
    """
    n = nlu.norm(soru or "")
    for o in ONCULLER:
        if not re.search(o["kw"], n):
            continue
        if not re.search(o["sorulan"], n):
            continue
        tr = lang == "tr"
        # Birim, SORULAN buyuklugu izler: ayni oncul hem ivmeyi hem
        # kuvveti sifirlar, ama ogrenci hangisini sorduysa onun
        # birimiyle cevap almalidir. Olculdu: "sabit hizla giden trenin
        # uzerindeki net KUVVET" sorusuna "0 m/s^2" deniyordu.
        birim = o["birim"]
        for kalip, br in (o.get("birim_secimi") or []):
            if re.search(kalip, n):
                birim = br
                break
        satirlar = [
            "### " + ("Önce verilenleri okuyalım" if tr
                      else "Read the premise first"), "",
            o["tr"] if tr else o["en"], "",
            "## **%g %s**" % (o["deger"], birim), "",
            "_" + ("Bu soru, öncülü okumadan formüle atlayanı yanıltmak "
                   "için kurulmuş. Bir problemin ilk adımı her zaman "
                   "verilenleri okumaktır." if tr else
                   "This question is designed to catch anyone who jumps "
                   "to a formula without reading the premise.") + "_",
        ]
        return "\n".join(satirlar)
    return None


def coz(soru, lang="tr"):
    """Soruyu bastan sona coz: karar + hesap + adimlar.

    Doner: metin ya da None (cozulemezse cagiran normal yola devam eder).
    """
    tr = lang == "tr"
    # Sorunun kendi onculu cevabi veriyor mu? ("surtunmesiz ... surtunme")
    _oncul = oncul_cevabi(soru, lang)
    if _oncul:
        return _oncul

    # Once bilinen COK ADIMLI kaliplar
    try:
        _zincir = devre_zinciri(soru, lang)
        if _zincir:
            return _zincir
    except Exception:
        pass
    karar_metni, olcut, ozel = karar_ver(soru, lang)

    # Hangi formulle devam edilecek?
    f = None
    if olcut and olcut.get("sonraki_formul"):
        f = formulas.BY_ID.get(olcut["sonraki_formul"])
    if f is None:
        vurus = [x for x in formulas.search(soru, limit=6)
                 if not x[1].get("uretilmis")]
        if not vurus:
            return None
        f = vurus[0][1]

    # SORULAN buyukluk once belirlenir; deger atamasi ona dokunmaz.
    hedef_ipucu = hedef_tahmin(f, soru, lang)

    # Verilenleri oku: once sembol biciminde, sonra dogal dilden
    bilinen = {}
    try:
        bilinen.update(nlu.extract_known_values(soru) or {})
    except Exception:
        pass
    try:
        for sym, (deger, birim) in (nlu.formul_degerleri(f, soru) or {}).items():
            if sym not in bilinen:
                bilinen[sym] = (deger, birim)
    except Exception:
        pass

    # Ozel okunan buyuklukleri formul degiskenlerine bagla
    ad_esleme = {"mu": ("mu",), "theta": ("theta",),
                 "theta_derece": ("theta",)}
    for anahtar, semboller in ad_esleme.items():
        if anahtar not in ozel:
            continue
        for sym in semboller:
            if sym in f["vars"] and sym not in bilinen:
                deger = ozel[anahtar]
                if anahtar == "theta_derece":
                    # Formuller radyan bekler
                    deger = math.radians(deger)
                bilinen[sym] = (deger, f["vars"][sym][2])

    # Fiziksel SABITLER metinden gelen degerlerle doldurulamaz. Olculdu:
    # "0.05 m3 hacim" ifadesi gaz sabiti R'ye atandi ve ideal gaz
    # problemi cozulemedi. Sabitin degeri zaten asagida dolduruluyor.
    for _s in list(bilinen):
        if _s in units.CONSTANTS and _s in f["vars"]:
            _kayit = units.CONSTANTS[_s]
            _ad = (f["vars"][_s][0] + " " + f["vars"][_s][1]).lower()
            _acik = (_kayit[3] + " " + _kayit[4]).lower()
            if ({w for w in _ad.split() if len(w) > 3}
                    & {w for w in _acik.split() if len(w) > 3}):
                bilinen.pop(_s, None)

    # SI'ye cevir
    sayisal = {}
    for sym, v in bilinen.items():
        if sym not in f["vars"]:
            continue
        deger, birim = (v if isinstance(v, tuple) else (v, ""))
        if deger is None:
            continue
        try:
            if birim:
                cevrim = units.to_si(deger, birim)
                if cevrim and cevrim[0] is not None:
                    deger = cevrim[0]
        except Exception:
            pass
        try:
            sayisal[sym] = float(deger)
        except (TypeError, ValueError):
            continue

    # Sabitleri doldur (g, G, kB...)
    for sym in f["vars"]:
        if sym in sayisal:
            continue
        kayit = units.CONSTANTS.get(sym)
        if kayit:
            ad = (f["vars"][sym][0] + " " + f["vars"][sym][1]).lower()
            aciklama = (kayit[3] + " " + kayit[4]).lower()
            ortak = {w for w in ad.split() if len(w) > 3} & {
                w for w in aciklama.split() if len(w) > 3}
            if ortak or "sabit" in ad or "ivmesi" in ad:
                sayisal[sym] = float(kayit[0])

    # Ayni birimdeki degiskenlerde sirayi fizik belirler (bkz.
    # formulas.SIRALI_DEGISKENLER): "500 K ve 300 K arasinda calisan
    # Carnot makinesi" sorusunda sicak/soguk ayrimi metinden cikmaz.
    _duzeltildi, _notlar = formulas.sirali_duzelt(f, sayisal)

    # Senaryonun ima ettigi degerler ("yukari atiliyor" -> a = -g)
    _sen_degerler, _sen_notlar = senaryo_degerleri(soru)
    _aci, _aci_not = varsayilan_aci(soru, f)
    _sen_degerler.update(_aci)
    _sen_notlar.extend(_aci_not)
    for _s, _v in _sen_degerler.items():
        if _s in f["vars"] and _s != hedef_ipucu:
            sayisal[_s] = _v

    # "Yukari atiliyor" gibi durumlarda verilen hiz ILK hizdir. Olculdu:
    # 20 m/s degeri son hiza (v) atanip soru cozulemez hale geliyordu.
    if any(x.get("hiz_ilk") for x in _sen_notlar):
        if "v0" in f["vars"] and "v" in sayisal and "v0" not in sayisal:
            sayisal["v0"] = sayisal.pop("v")
            hedef_ipucu = "v"
        elif "v0" not in f["vars"] and "v" in sayisal:
            # Verilen hiz ILK hizdir ama bu bagintinin v0'i yok; onu
            # dogrudan "v" diye kullanmak yanlis cevap uretir. Olculdu:
            # "20 m/s ile yukari atiliyor, 3 saniye sonraki kinetik
            # enerjisi" sorusuna 400 J deniyordu (dogrusu 88,7 J).
            # Bu durumda cok adimli cozucuye birakiyoruz.
            return None

    # Sorulan buyukluk yanlislikla doldurulmussa geri al: ayni birimdeki
    # degerler rastgele atanabiliyor.
    if hedef_ipucu and hedef_ipucu in sayisal and len(sayisal) > 1:
        _birim = f["vars"][hedef_ipucu][2]
        _ayni = [x for x in sayisal
                 if x != hedef_ipucu and f["vars"][x][2] == _birim]
        _bos = [x for x in f["vars"]
                if x not in sayisal and f["vars"][x][2] == _birim]
        if _bos:
            sayisal[_bos[0]] = sayisal.pop(hedef_ipucu)
        elif _ayni:
            sayisal.pop(hedef_ipucu)

    # Girdiler fiziksel mi? (negatif kutle, negatif mutlak sicaklik...)
    _girdi_hatasi = girdi_denetle(f, sayisal, lang)
    if _girdi_hatasi:
        return _girdi_hatasi

    eksikler = [s for s in f["vars"] if s not in sayisal]
    if len(eksikler) != 1:
        # Tam bir bilinmeyen yoksa yalnizca karari dondurebiliriz
        return karar_metni
    hedef = eksikler[0]

    sonuc = _sembolik_coz(f, sayisal, hedef)
    if sonuc is None:
        return karar_metni

    # Fiziksel olarak imkansiz bir sonucu CEVAP diye sunmuyoruz.
    _ok, _sebep = makul_mu(f, hedef, sonuc)
    if not _ok:
        uyari = [
            "### " + ("Bu soruyu tek bağıntıyla çözemedim" if tr
                      else "This needs more than one relation"), "",
            ("Denediğim bağıntı `%s` ve çıkan sonuç fiziksel değil "
             "(%s)." % (f["eq"], _sebep)) if tr else
            ("Trying `%s` gives a physically impossible result." % f["eq"]),
            "",
            ("Muhtemelen **iki adımlı** bir soru: önce eşdeğer büyüklüğü, "
             "sonra aradığınızı bulmak gerekiyor. Adımları ayrı sorarsanız "
             "ikisini de hesaplarım." if tr else
             "This is likely a two-step problem; ask the steps separately."),
        ]
        if karar_metni:
            uyari = [karar_metni, ""] + uyari
        return "\n".join(uyari)

    ad = f["tr"] if tr else f["en"]
    hedef_ad = f["vars"][hedef][0] if tr else f["vars"][hedef][1]
    birim = f["vars"][hedef][2]

    lines = ["### " + (("Çözüm — %s" if tr else "Solution — %s") % ad), ""]
    if karar_metni:
        lines.append(karar_metni)
        lines.append("")
    lines.append("**" + ("Verilenler" if tr else "Given") + "**")
    lines.append("")
    for _sn in _sen_notlar:
        lines.append("_%s_" % (_sn["not_tr"] if tr else _sn["not_en"]))
        lines.append("")
    if _duzeltildi:
        for buyuk, kucuk in _notlar:
            lines.append(
                ("_Not: `%s` ile `%s` degerleri fiziksel siraya gore "
                 "yerlestirildi (%s ≥ %s olmalidir)._" if tr else
                 "_Note: `%s` and `%s` were ordered physically "
                 "(%s >= %s)._") % (buyuk, kucuk, buyuk, kucuk))
        lines.append("")
    for sym, deger in sorted(sayisal.items()):
        lines.append("- `%s` = %.6g %s  (%s)"
                     % (sym, deger, f["vars"][sym][2],
                        f["vars"][sym][0] if tr else f["vars"][sym][1]))
    lines.append("")
    lines.append("**" + ("Bağıntı" if tr else "Relation") + "**")
    lines.append("")
    lines.append("`%s`" % f["eq"])
    lines.append("")
    try:
        duzenli = formulas.symbolic_rearrange(f, hedef)
        # symbolic_rearrange liste donebiliyor; ham liste gosterimi
        # ders metninde okunmuyor.
        if isinstance(duzenli, (list, tuple)):
            duzenli = duzenli[0] if duzenli else None
        if duzenli:
            lines.append(("`%s` için düzenlenmiş hâli:" if tr
                          else "Rearranged for `%s`:") % hedef)
            lines.append("")
            lines.append("`%s`" % duzenli)
            lines.append("")
    except Exception:
        pass
    lines.append("**" + ("Sonuç" if tr else "Result") + "**")
    lines.append("")
    # Aci DERECE ile soruldu ise cevabi da derece ile ver. Olculdu:
    # "30 derece ile giren isigin kirilma acisi" sorusuna 0,3398 rad
    # deniyordu — dogru ama ogrencinin bekledigi bicim degil.
    if birim in ("rad", "radyan") and re.search(
            r"\bderece\b|°|\bdegree", nlu.norm(soru or "")):
        import math as _mt
        lines.append("## `%s` = **%s derece**  (%s rad)"
                     % (hedef, _oku_sayi(_mt.degrees(sonuc)),
                        _oku_sayi(sonuc)))
    else:
        lines.append("## `%s` = **%s %s**"
                     % (hedef, _oku_sayi(sonuc), birim))
    lines.append("")
    lines.append(("_Aranan büyüklük: %s. Hesap SymPy ile yapıldı._" if tr
                  else "_Target: %s. Computed symbolically._") % hedef_ad)
    return "\n".join(lines)
