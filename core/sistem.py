# -*- coding: utf-8 -*-
"""SISTEM COZUCU: ilgili butun denklemleri birlikte yazip cozmek.

Kullanicinin tespiti: *"sen bu urettigin sorulari nasil cozuyorsan bizim
yapay zekamiz da oyle cozmeli"*.

Bir insan (ya da bir dil modeli) fizik problemini soyle cozer:
    1. Durumu okur.
    2. Hangi ILKELERIN gecerli oldugune karar verir.
    3. Ilgili BUTUN bagintilari yan yana yazar.
    4. Sistemi bilinmeyen icin cozer.
    5. Birim ve buyukluk denetimi yapar.

Mevcut `zincir.py` ise tek bir formul secip geriye dogru adim adim
ilerliyor: "hedefi veren baginti hangisi? onun eksigini veren hangisi?"
Bu ACGOZLU bir aramadir. Tabloya benzeyen soruda calisir; ama:

  * Ayni sembol birden cok bagintida geciyorsa (frekans `f` hem organ
    borusunda hem Doppler'de) yanlis dala girip tukenebilir.
  * Ara buyuklugu once bulup sonra hedefe gecmesi gereken sorularda
    (Carnot: once verim, sonra is) yolun ortasinda durabilir.

Buradaki cozucu farkli calisir: bilinenlerle ve hedefle sembol paylasan
BUTUN bagintilari toplar, hepsini ayni anda SymPy'ye verir ve sistemi
hedef icin cozer. Hangi bagintinin once geldigi onemli degildir —
matematik yolu kendisi bulur.

Bu, zincirin yerine gecmez; zincir cozemediginde devreye girer. Cunku
zincirin urettigi ADIM ADIM anlatim ogretici olarak daha degerlidir.
"""
import re

from . import formulas, problem, units

MAX_DENKLEM = 6          # sistemde en fazla bu kadar baginti
MAX_SEMBOL = 12          # cozulecek bilinmeyen sayisi siniri


def _sayisal(deger):
    try:
        x = float(deger)
    except Exception:
        return None
    if x != x or x in (float("inf"), float("-inf")):
        return None
    return x


def _ilgili_denklemler(adaylar, bilinen, hedef, ana):
    """Bilinenler ve hedefle sembol paylasan bagintilari sec.

    Bir baginti ancak sisteme KATKI yapiyorsa alinir: ya hedefi
    iceriyordur, ya da hedefi iceren bir bagintinin eksigini kapatan bir
    sembolu vardir. Alakasiz bagintilari sisteme katmak cozumu hem
    yavaslatir hem de sahte cozumler dogurur.
    """
    # DIKKAT: hedefi iceren bagintilar BIRLIKTE sisteme konmaz. Olculdu:
    # Doppler denklemi TEK BASINA f = 1096,77 veriyordu; ama ayni sembolu
    # (`f`) iceren organ borusu bagintisi da sisteme katilinca `L`, `n`
    # gibi yeni bilinmeyenler girdi ve sistem cozulemez oldu. Her aday
    # AYRI AYRI denenmeli.
    if ana is None:
        return []
    secili, gorulen = [ana], {ana["id"]}
    eksikler = {sym for sym in ana["vars"]
                if sym != hedef and sym not in bilinen}
    if not eksikler:
        return secili
    # Bu eksikleri URETEBILEN bagintilar
    for _s, f in adaylar:
        if f["id"] in gorulen:
            continue
        if not (set(f["vars"]) & eksikler):
            continue
        # Katkisi olmali: bu baginti eksigi cozebilmeli, yani geri kalan
        # sembollerinin cogu biliniyor olmali
        bilinmeyen = [x for x in f["vars"]
                      if x not in bilinen and x not in eksikler]
        if len(bilinmeyen) > 1:
            continue
        secili.append(f)
        gorulen.add(f["id"])
        if len(secili) >= MAX_DENKLEM:
            break
    return secili


def coz(soru, adaylar, bilinen, hedef, hedef_f, lang="tr"):
    """Sistemi hedef icin coz. (deger, kullanilan_formuller) ya da None."""
    import sympy as sp

    # Hedefi iceren her bagintiyi AYRI AYRI dene; ilk cozuleni al.
    adaylar_ana = []
    if hedef_f is not None and hedef in (hedef_f.get("vars") or {}):
        adaylar_ana.append(hedef_f)
    for _s, f in adaylar:
        if hedef in f["vars"] and f["id"] not in {x["id"] for x in adaylar_ana}:
            adaylar_ana.append(f)
    for ana in adaylar_ana:
        sonuc = _tek_dene(adaylar, bilinen, hedef, ana, hedef_f)
        if sonuc is not None:
            return sonuc
    return None


def _tek_dene(adaylar, bilinen, hedef, ana, hedef_f):
    import sympy as sp
    denklemler = _ilgili_denklemler(adaylar, bilinen, hedef, ana)
    if not denklemler:
        return None

    # Sembol havuzu: sistemdeki tum degiskenler
    semboller = set()
    for f in denklemler:
        semboller |= set(f["vars"])
    if len(semboller) > MAX_SEMBOL:
        return None

    sistem, kullanilan = [], []
    for f in denklemler:
        try:
            eq = formulas.sympy_eq(f)
        except Exception:
            continue
        sistem.append(eq)
        kullanilan.append(f)
    if not sistem:
        return None

    # Bilinen degerleri yerine koy
    yerine = {}
    for sym, veri in (bilinen or {}).items():
        if sym == hedef or sym not in semboller:
            continue
        deger = _sayisal(veri[0] if isinstance(veri, (tuple, list)) else veri)
        if deger is None:
            continue
        yerine[sp.Symbol(sym)] = deger
    # Fiziksel sabitler
    try:
        for sym in semboller:
            if sym in yerine or sym == hedef:
                continue
            sabit = problem.sabit_degeri(sym) if hasattr(
                problem, "sabit_degeri") else None
            if sabit is not None:
                yerine[sp.Symbol(sym)] = float(sabit)
    except Exception:
        pass

    try:
        indirgenmis = [e.subs(yerine) for e in sistem]
    except Exception:
        return None

    hedef_sym = sp.Symbol(hedef)
    bilinmeyenler = set()
    for e in indirgenmis:
        bilinmeyenler |= e.free_symbols
    bilinmeyenler = {s for s in bilinmeyenler if s != hedef_sym}
    if len(bilinmeyenler) > 4:
        return None

    try:
        cozum = sp.solve(indirgenmis, [hedef_sym] + sorted(
            bilinmeyenler, key=str), dict=True)
    except Exception:
        return None
    if not cozum:
        return None

    for c in cozum:
        deger = c.get(hedef_sym)
        if deger is None:
            continue
        try:
            sayi = complex(sp.N(deger))
        except Exception:
            continue
        if abs(sayi.imag) > 1e-9:
            continue
        x = sayi.real
        if x != x:
            continue
        # Fiziksel makullük: negatif kutle/uzunluk/mutlak sicaklik olmaz
        birim = (hedef_f["vars"].get(hedef) or ("", "", ""))[2] if hedef_f \
            else ""
        if x < 0 and birim in ("kg", "m", "K", "s", "Hz", "J/K"):
            continue
        return x, kullanilan
    return None
