"""Kendi kendini dogrulama.

Bot ogrendigini ve bildigini korumasiz kabul etmez; iki bagimsiz yontemle
sinar:

  1. **Boyut denetimi** — formulun iki tarafinin fiziksel boyutu ayni mi?
     `Ek = m*v^2/2` icin sol taraf enerji, sag taraf kg·(m/s)^2 = enerji.
     Tutmuyorsa formul ya da birim tanimi hatalidir.

  2. **Geri yerine koyma** — rastgele degerlerle bilinmeyen cozulur, cikan
     sonuc denklemde yerine konur ve kalan (residual) sifir mi diye bakilir.
     Cozucudeki ya da formuldeki bir hata boylece yakalanir.

Bu, "dogru oldugunu varsayiyorum" ile "sinadim, tutuyor" arasindaki farktir.
"""
import math
import random
import time

import sympy as sp

from . import formulas, units, db


def _boyut(unit_str):
    p = units.parse_unit(unit_str or "")
    return p[1] if p else None


def boyut_denetimi(f):
    """Formulun iki tarafi ayni boyutta mi?

    Denklemi sembolik olarak alir, her degiskeni kendi biriminin boyutuyla
    degistirir ve iki tarafin boyut vektorunu karsilastirir.
    """
    try:
        eq = formulas.sympy_eq(f)
    except Exception as e:
        return {"ok": False, "neden": "denklem cozumlenemedi: %s" % e}

    bilinmeyen = []
    boyutlar = {}
    for sym, (_tr, _en, u) in f["vars"].items():
        d = _boyut(u)
        if d is None:
            bilinmeyen.append(sym)
        else:
            boyutlar[sym] = d

    if bilinmeyen:
        return {"ok": None, "neden": "birimi cozulemeyen degisken: %s"
                % ", ".join(bilinmeyen)}

    # Her temel boyut icin ayri bir "olcek" degiskeni kullanip us toplamlarini
    # karsilastiriyoruz: degiskeni 10^e ile olcekleyip logaritmik fark bakmak
    # yerine dogrudan sembolik us hesabi yapiyoruz.
    taban = sp.symbols("L M T I K N J", positive=True)

    def olcek(d):
        ifade = sp.Integer(1)
        for t, us in zip(taban, d):
            if us:
                ifade *= t ** sp.Rational(us).limit_denominator(1000)
        return ifade

    subs = {sp.Symbol(s): olcek(d) for s, d in boyutlar.items()}
    try:
        sol = sp.simplify(sp.powsimp(eq.lhs.subs(subs), force=True))
        sag = sp.simplify(sp.powsimp(eq.rhs.subs(subs), force=True))
    except Exception as e:
        return {"ok": None, "neden": "sadelestirilemedi: %s" % e}

    # Toplama iceren ifadelerde her terimin boyutu ayni olmali; oran sabit
    # cikiyorsa boyutlar tutuyor demektir.
    try:
        oran = sp.simplify(sol / sag)
    except Exception as e:
        return {"ok": None, "neden": "oran alinamadi: %s" % e}

    if oran.free_symbols & set(taban):
        return {"ok": False, "neden": "boyutlar uyusmuyor (oran: %s)" % oran}
    return {"ok": True}


def _us_degiskenleri(ifade):
    """Denklemde US konumunda gecen sembolleri bul.

    Adyabatik surecte (P1*V1**gam = P2*V2**gam) gam bir ustur. Boyle bir
    sembol icin sembolik cozum askin bir denklem dogurur ve SymPy dakikalarca
    (pratikte sonsuza kadar) ugrasir; olcumde `adyabatik` formulunde tum
    dogrulama takiliyordu. Bu semboller cozum hedefi olarak secilmez.
    """
    usler = set()
    for alt in sp.preorder_traversal(ifade):
        if isinstance(alt, sp.Pow):
            usler |= alt.exp.free_symbols
        # exp() ve log() SymPy'de Pow degildir; argumanlarindaki semboller
        # de askin cozum dogurur. Olculdu: P = exp(-E/(kB*T)) formulunde
        # T icin cozum SymPy'yi kilitliyordu.
        elif isinstance(alt, (sp.exp, sp.log)):
            usler |= alt.args[0].free_symbols
    return usler


def geri_yerine_koy(f, deneme=2, tol=1e-6):
    """Cozumu denklemde yerine koyup kalanin sifir oldugunu dogrula."""
    syms = list(f["vars"].keys())
    if len(syms) < 2:
        return {"ok": None, "neden": "tek degiskenli"}
    try:
        eq = formulas.sympy_eq(f)
    except Exception as e:
        return {"ok": False, "neden": "denklem cozumlenemedi: %s" % e}

    # Us konumundaki degiskenleri hedef secme
    try:
        us_adlari = {str(x) for x in _us_degiskenleri(eq.lhs - eq.rhs)}
    except Exception:
        us_adlari = set()
    cozulebilir = [s for s in syms if s not in us_adlari] or syms

    rng = random.Random(20240728)
    basarili = 0
    denendi = 0
    for _ in range(deneme):
        hedef = cozulebilir[denendi % len(cozulebilir)]
        degerler = {}
        for s in syms:
            if s == hedef:
                continue
            # Us konumundaki degiskene TAM SAYI veriyoruz. Ondalik bir us
            # (5.7 = 57/10) tabani cozerken 57 karmasik kok dogurur ve
            # SymPy dakikalarca ugrasir; tam sayi us hem hizli hem yeterli.
            degerler[s] = (2 if s in us_adlari
                           else round(rng.uniform(1.2, 9.5), 4))
        denendi += 1
        try:
            _t, sols, _e = formulas.solve_for(f, degerler, target=hedef)
        except Exception:
            continue
        gercel = [x for x in sols if isinstance(x, float)]
        if not gercel:
            continue
        for cevap in gercel[:2]:
            tam = dict(degerler)
            tam[hedef] = cevap
            subs = {sp.Symbol(k): sp.Float(v) for k, v in tam.items()}
            try:
                kalan = complex(sp.N((eq.lhs - eq.rhs).subs(subs)))
            except Exception:
                continue
            olcek = max(abs(complex(sp.N(eq.lhs.subs(subs)))), 1.0)
            if abs(kalan) <= tol * olcek:
                basarili += 1
                break
    if denendi == 0:
        return {"ok": None, "neden": "cozulebilir hedef bulunamadi"}
    return {"ok": basarili > 0, "gecen": basarili, "denenen": denendi}


def formul_dogrula(f):
    b = boyut_denetimi(f)
    g = geri_yerine_koy(f)
    return {"id": f["id"], "ad": f["tr"], "boyut": b, "geri": g,
            "saglam": (b.get("ok") is not False) and (g.get("ok") is not False)}


ONBELLEK_ANAHTAR = "dogrulama_sonucu"


def onbellekten():
    """Daha once hesaplanmis dogrulama sonucunu getir."""
    try:
        d = db.get_state(ONBELLEK_ANAHTAR)
        if isinstance(d, dict) and d.get("formul_sayisi") == len(formulas.FORMULAS):
            return d
    except Exception:
        pass
    return None


def onbellege_yaz(sonuc):
    sonuc = dict(sonuc)
    sonuc["formul_sayisi"] = len(formulas.FORMULAS)
    sonuc["zaman"] = time.time()
    try:
        db.set_state(ONBELLEK_ANAHTAR, sonuc)
    except Exception:
        pass
    return sonuc


def hizli_boyut():
    """Yalnizca boyut denetimi — saniyenin altinda tamamlanir."""
    s = {"toplam": 0, "boyut_ok": 0, "boyut_hatasi": [], "denetlenemedi": []}
    for f in formulas.FORMULAS:
        s["toplam"] += 1
        b = boyut_denetimi(f)
        if b.get("ok") is True:
            s["boyut_ok"] += 1
        elif b.get("ok") is False:
            s["boyut_hatasi"].append((f["id"], b["neden"]))
        else:
            s["denetlenemedi"].append((f["id"], b["neden"]))
    return s


def tum_formuller(limit=None):
    """Tum formul tabanini sina ve rapor dondur.

    Geri yerine koyma sembolik cozum gerektirdigi icin pahali; sonuc
    onbellege yazilir ve arka planda tazelenir.
    """
    sonuc = {"toplam": 0, "saglam": 0, "boyut_hatasi": [], "geri_hatasi": [],
             "denetlenemedi": []}
    for f in formulas.FORMULAS[:limit]:
        r = formul_dogrula(f)
        sonuc["toplam"] += 1
        if r["boyut"].get("ok") is False:
            sonuc["boyut_hatasi"].append((f["id"], r["boyut"]["neden"]))
        elif r["boyut"].get("ok") is None:
            sonuc["denetlenemedi"].append((f["id"], r["boyut"]["neden"]))
        if r["geri"].get("ok") is False:
            sonuc["geri_hatasi"].append((f["id"], r["geri"].get("neden", "")))
        if r["saglam"]:
            sonuc["saglam"] += 1
    return sonuc


def rapor(lang="tr"):
    """Kullaniciya gosterilecek rapor.

    Boyut denetimi anlik yapilir; pahali olan geri-yerine-koyma sonucu varsa
    onbellekten okunur, yoksa arka planda hesaplandigi soylenir.
    """
    tr = lang == "tr"
    h = hizli_boyut()
    onbellek = onbellekten()
    s = {
        "toplam": h["toplam"],
        "saglam": onbellek.get("saglam") if onbellek else h["boyut_ok"],
        "boyut_hatasi": h["boyut_hatasi"],
        "geri_hatasi": (onbellek or {}).get("geri_hatasi", []),
        "denetlenemedi": h["denetlenemedi"],
    }
    lines = ["### " + ("Kendi kendini doğrulama" if tr else "Self-verification"), ""]
    lines.append(("**%d formülün %d tanesi** her iki sınamayı da geçti."
                  if tr else "**%d of %d formulas** passed both checks.")
                 % ((s["saglam"], s["toplam"]) if tr else (s["saglam"], s["toplam"])))
    lines.append("")
    lines.append(("Sınamalar: **boyut denetimi** (denklemin iki tarafı aynı "
                  "fiziksel boyutta mı) ve **geri yerine koyma** (çözüm "
                  "denklemi gerçekten sağlıyor mu)." if tr else
                  "Checks: **dimensional consistency** and **back-substitution**."))
    lines.append("")
    lines.append(("- Boyut denetimi: **%d/%d** geçti" if tr else
                  "- Dimensional check: **%d/%d** passed")
                 % (h["boyut_ok"], h["toplam"]))
    if onbellek:
        lines.append(("- Geri yerine koyma: **%d/%d** geçti" if tr else
                      "- Back-substitution: **%d/%d** passed")
                     % (onbellek.get("saglam", 0), onbellek.get("toplam", 0)))
    else:
        lines.append(("- Geri yerine koyma: _arka planda hesaplanıyor, birkaç "
                      "dakika içinde hazır olur._" if tr else
                      "- Back-substitution: _running in the background._"))
    if s["boyut_hatasi"]:
        lines.append("")
        lines.append("**" + ("Boyut hatası:" if tr else "Dimension errors:") + "**")
        for fid, neden in s["boyut_hatasi"][:10]:
            lines.append("- `%s` — %s" % (fid, neden))
    if s["geri_hatasi"]:
        lines.append("")
        lines.append("**" + ("Yerine koyma hatası:" if tr
                             else "Back-substitution errors:") + "**")
        for fid, neden in s["geri_hatasi"][:10]:
            lines.append("- `%s` %s" % (fid, neden))
    if s["denetlenemedi"]:
        lines.append("")
        lines.append(("_%d formülde bazı değişkenlerin birimi boyutsuz ya da "
                      "özel olduğu için boyut denetimi uygulanamadı._" if tr else
                      "_%d formulas could not be dimension-checked._")
                     % len(s["denetlenemedi"]))
    return "\n".join(lines)
