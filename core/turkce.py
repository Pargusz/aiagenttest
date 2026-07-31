# -*- coding: utf-8 -*-
"""Turkce kok bulma — tek bir dogru yerde.

Turkce sondan eklemeli: "termodinamik" kelimesi soruda "termodinamiğin",
"entropi" ise "entropinin" olarak geciyor. Arama motorlari ham kelimeyle
calistigi icin bu sorular konuya ulasamiyordu (olculdu: ogretim kapsami
%78'de kalmisti, dusen dokuz sorunun dokuzu da cekim ekiydi).

Iki tuzak var:

1. **Unsuz yumusamasi.** "termodinamik" + "-in" = "termodinamiğin".
   Eki attiginizda "termodinami" kalir; dogru kok "termodinamik"tir.
   Yumusayan sessizi geri sertlestirmek gerekir (ğ/g -> k, b -> p, d -> t).

2. **Fazla kesme.** "entropi" kelimesinin sonundaki "i" ek degildir.
   Bu yuzden kesme tek bir dogru cevap uretmez; ADAYLAR uretip hepsini
   denemek gerekir.
"""
import re

# Cekim ekleri — uzundan kisaya (once uzun olan denenmeli)
_EKLER = [
    "larinin", "lerinin", "larindan", "lerinden", "lariyla", "leriyle",
    "sinin", "sinin", "ginin", "inin", "unun", "nun", "nin",
    "larin", "lerin", "lari", "leri", "lara", "lere", "larda", "lerde",
    "sini", "sina", "sinda", "sindan",
    "ndan", "nden", "dan", "den", "tan", "ten", "daki", "deki",
    "lar", "ler", "ini", "unu", "ine", "ina", "una", "une",
    "nin", "nun", "in", "un", "im", "um", "de", "da", "te", "ta",
    "yi", "yu", "ye", "ya", "si", "su", "i", "u", "e", "a",
]

# Yumusayan sessizlerin sert karsiliklari
_SERTLESME = {"g": "k", "ğ": "k", "b": "p", "c": "ç", "d": "t"}


def kokler(kelime, en_az=4):
    """Bir kelimenin olasi koklerini uret (en olasidan baslayarak).

    Kesme tek bir dogru cevap vermez ("entropi"nin sonundaki i ek degil),
    bu yuzden adaylar dondurulur ve cagiran hepsini dener.
    """
    k = (kelime or "").lower().strip()
    if len(k) < en_az:
        return [k] if k else []
    adaylar = [k]
    for ek in _EKLER:
        if len(k) - len(ek) >= en_az and k.endswith(ek):
            govde = k[:-len(ek)]
            if govde not in adaylar:
                adaylar.append(govde)
            # Unsuz yumusamasini geri al
            if govde and govde[-1] in _SERTLESME:
                sert = govde[:-1] + _SERTLESME[govde[-1]]
                if sert not in adaylar:
                    adaylar.append(sert)
    return adaylar


def kok(kelime, en_az=4):
    """Tek bir kok tahmini (en kisa makul aday)."""
    a = kokler(kelime, en_az)
    return a[-1] if len(a) > 1 else (a[0] if a else kelime)


def sadelestir(metin, en_az=4):
    """Cumledeki kelimeleri koklerine indir.

    Adaylar arasindan EN KISA olan secilir: en cok ek atilmis bicimdir.
    (Once son aday seciliyordu ve "yasasini" -> "yasasin" gibi yanlis
    sonuclar cikiyordu.)
    """
    parcalar = []
    for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]+", metin or ""):
        if len(w) < en_az:
            parcalar.append(w)
            continue
        adaylar = kokler(w, en_az)
        parcalar.append(min(adaylar, key=len) if adaylar else w)
    return " ".join(parcalar)


def genislet(metin, en_az=4):
    """Sorguyu TUM kok adaylariyla genislet.

    Kesme tek dogru cevap vermedigi icin en iyi strateji adaylarin
    hepsini arama motoruna vermektir: motor hangisini taniyorsa onu bulur.
    "termodinamigin" -> "termodinamigin termodinamig termodinamik"
    """
    parcalar = []
    gorulen = set()
    for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]+", metin or ""):
        for aday in ([w] if len(w) < en_az else kokler(w, en_az)):
            if aday and aday not in gorulen:
                gorulen.add(aday)
                parcalar.append(aday)
    return " ".join(parcalar)


def varyantlar(metin, en_az=4):
    """Sorgunun denenecek biçimleri: ham, sadelestirilmis ve karisik.

    Karisik biçim hem ham hem kok halini icerir; boylece arama motoru
    hangisini taniyorsa onu yakalar.
    """
    ham = (metin or "").strip()
    sade = sadelestir(ham, en_az)
    out = [ham]
    if sade and sade != ham:
        out.append(sade)
        out.append(ham + " " + sade)
    return out


# ── Turkce -> Ingilizce fizik terimleri ─────────────────────────────────────
# Korpusun yaklasik %80'i Ingilizce. Turkce sorulan bir soru bulgulara hic
# ulasamiyordu (olculdu: "kuantum dolanikligi" ve "plazma frekansi" icin
# sifir bulgu). Koprü icin yeni bir sozluk yazmaya gerek yok: formul tabani
# her formulun ve her degiskenin adini ZATEN iki dilde tasiyor.

# Formul tabaninda karsiligi olmayan yaygin kavramlar
EK_CEVIRI = {
    "kuantum dolanikligi": "quantum entanglement",
    "dolaniklik": "entanglement",
    "superpozisyon": "superposition",
    "tunelleme": "quantum tunneling",
    "kara delik": "black hole",
    "solucan deligi": "wormhole",
    "karanlik madde": "dark matter",
    "karanlik enerji": "dark energy",
    "buyuk patlama": "big bang",
    "kutle cekim dalgasi": "gravitational wave",
    "yercekimi dalgasi": "gravitational wave",
    "standart model": "standard model",
    "higgs bozonu": "higgs boson",
    "notrino": "neutrino",
    "antimadde": "antimatter",
    "supersimetri": "supersymmetry",
    "sicim kurami": "string theory",
    "kuantum alan kurami": "quantum field theory",
    "dalga fonksiyonu": "wave function",
    "belirsizlik ilkesi": "uncertainty principle",
    "pauli dislama": "pauli exclusion",
    "bose einstein yogusmasi": "bose einstein condensate",
    "supersiviilik": "superfluidity",
    "superiletkenlik": "superconductivity",
    "yariiletken": "semiconductor",
    "topolojik yalitkan": "topological insulator",
    "grafen": "graphene",
    "nanoyapi": "nanostructure",
    "fuzyon": "nuclear fusion",
    "fisyon": "nuclear fission",
    "radyoaktivite": "radioactivity",
    "isinim": "radiation",
    "spektroskopi": "spectroscopy",
    "kirinim": "diffraction",
    "girisim": "interference",
    "polarizasyon": "polarization",
    "lazer": "laser",
    "optik tuzak": "optical trap",
    "akiskanlar dinamigi": "fluid dynamics",
    "turbulans": "turbulence",
    "kaos": "chaos theory",
    "faz gecisi": "phase transition",
    "kritik nokta": "critical point",
    "istatistiksel mekanik": "statistical mechanics",
    "manyetik rezonans": "magnetic resonance",
    "parcacik hizlandirici": "particle accelerator",
    "kozmik isin": "cosmic ray",
    "kirmizi kayma": "redshift",
    "yildiz evrimi": "stellar evolution",
    "notron yildizi": "neutron star",
    "beyaz cuce": "white dwarf",
    "supernova": "supernova",
    "gunes ruzgari": "solar wind",
    "manyetosfer": "magnetosphere",
    "iyonosfer": "ionosphere",
}

_TR_EN = None


def _sozluk_kur():
    global _TR_EN
    if _TR_EN is not None:
        return _TR_EN
    from . import formulas, knowledge, units
    esleme = {}

    def ekle(tr, en):
        tr, en = (tr or "").strip().lower(), (en or "").strip()
        if len(tr) > 2 and len(en) > 2 and tr != en.lower():
            esleme.setdefault(tr, en)

    for f in formulas.FORMULAS:
        ekle(f.get("tr"), f.get("en"))
        for _s, v in (f.get("vars") or {}).items():
            ekle(v[0], v[1])
        for a, b in zip(f.get("kw_tr") or [], f.get("kw_en") or []):
            ekle(a, b)
    for t in getattr(knowledge, "TOPICS", []):
        ekle(t.get("tr_title"), t.get("en_title"))
    for _k, v in getattr(units, "CONSTANTS", {}).items():
        if len(v) >= 5:
            ekle(v[3], v[4])
    for tr, en in EK_CEVIRI.items():
        ekle(tr, en)
    _TR_EN = esleme
    return _TR_EN


def ingilizce_karsilik(ifade):
    """Turkce bir terimin Ingilizce karsiligi (bilinmiyorsa None)."""
    s = _sozluk_kur()
    k = (ifade or "").strip().lower()
    if k in s:
        return s[k]
    # Kelime kelime dene: "kuantum dolanikligi" -> "quantum"
    for kelime in k.split():
        if len(kelime) > 3 and kelime in s:
            return s[kelime]
    return None


def ceviri_ile_genislet(sorgu, en_fazla=3):
    """Sorguyu Ingilizce karsiliklariyla genislet.

    Doner: (genisletilmis_sorgu, eklenen_terimler)
    """
    s = _sozluk_kur()
    ham = (sorgu or "").strip()
    n = ham.lower()
    ekler = []
    # Once tam ifade, sonra kelime kokleri
    for tr, en in s.items():
        if len(tr) < 4 or en.lower() in n:
            continue
        if tr in n:
            ekler.append(en)
        elif len(tr.split()) == 1:
            for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{4,}", n):
                if w[:5] == tr[:5] and abs(len(w) - len(tr)) <= 3:
                    ekler.append(en)
                    break
        if len(ekler) >= en_fazla:
            break
    if not ekler:
        return ham, []
    return (ham + " " + " ".join(ekler)).strip(), ekler
