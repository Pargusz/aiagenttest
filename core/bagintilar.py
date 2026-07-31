"""Makalelerden bagintI (denklem) ogrenme.

Onceki surumde ozetlerden `$...$` icindeki her sey "formul" diye toplaniyordu;
sonuc `\\mathcal{N}` ve `, where` gibi yiginlarla dolu, hicbir yerde
kullanilmayan bir tabloydu. Burada uc sey degisiyor:

  1. **Sıkı ayiklama** — bir sey ancak bagintI sayilir: iliski isareti (=, ∝,
     ≈) icerir, en az iki farkli simge barindirir ve cogunlukla LaTeX komutu
     degildir.
  2. **Dogrulama** — SymPy ile ayristirilabiliyor mu? Ayristirilabilenler
     "cozulebilir" olarak isaretlenir.
  3. **Kullanim** — ogrenilen bagintilar cevaplarda gosterilir ve konuya gore
     aranabilir. Yani yeni makale geldikce botun bagintI dagarcigi buyur.
"""
import re

import sympy as sp

from . import db
from .learner import normalize

# Iliski isareti sart: bir denklem ya da orantI olmali
_ILISKI = r"(?:=|≈|\\approx|\\simeq|\\propto|∝|\\sim|≥|≤|\\geq|\\leq|<|>)"

# Atilacak LaTeX ortam/komut kaliplari
_LATEX_COMUT = re.compile(r"\\(?:mathcal|mathbf|mathrm|text|textrm|textit|"
                          r"ensuremath|left|right|begin|end|label|ref|cite|"
                          r"emph|footnote|nonumber|quad|qquad|hspace|vspace)\b")

# Metin parcasi gibi gorunenler (formul degil)
_METIN_GIBI = re.compile(r"^[\s,;:.]*(?:where|and|with|for|the|is|are|"
                         r"burada|ve|ile|icin)\b", re.I)


def _temizle(t):
    t = (t or "").strip()
    t = re.sub(r"\s+", " ", t)
    t = t.strip(" ,;:.")
    return t


def bagintI_mi(t):
    """Bu metin gercekten bir bagintI mi?"""
    t = _temizle(t)
    if not (4 <= len(t) <= 160):
        return False
    if _METIN_GIBI.match(t):
        return False
    if not re.search(_ILISKI, t):
        return False
    # En az iki farkli harf-simge olmali (tek simgelik "N = " gibi seyler degil)
    simgeler = set(re.findall(r"[A-Za-zΑ-Ωα-ω](?![a-z]{3,})", t))
    if len(simgeler) < 2:
        return False
    # Cogunlugu LaTeX komutuysa formul degil, bicimlendirmedir
    komut = len(_LATEX_COMUT.findall(t))
    if komut and komut * 8 > len(t) / 3:
        return False
    # Salt "a = b" gibi bos bir esitlik olmasin: ya bir islec/rakam bulunsun
    # ya da en az uc ayri simge (F = ma gibi).
    if not re.search(r"[\d+\-*/^_{}\\()]", t) and len(simgeler) < 3:
        return False
    return True


# LaTeX -> sade metin (SymPy'nin anlayabilecegi bicime yaklastirma)
_SADE = [
    (r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1)/(\2)"),
    (r"\\sqrt\s*\{([^{}]+)\}", r"sqrt(\1)"),
    (r"\\(?:mathrm|mathbf|mathcal|text|textrm|ensuremath)\s*\{([^{}]+)\}", r"\1"),
    (r"\\left|\\right", ""),
    (r"\\cdot|\\times", "*"),
    (r"\\pi", "pi"), (r"\\alpha", "alpha"), (r"\\beta", "beta"),
    (r"\\gamma", "gamma"), (r"\\delta", "delta"), (r"\\lambda", "lam"),
    (r"\\mu", "mu"), (r"\\nu", "nu"), (r"\\omega", "omega"),
    (r"\\sigma", "sigma"), (r"\\rho", "rho"), (r"\\theta", "theta"),
    (r"\\phi", "phi"), (r"\\epsilon|\\varepsilon", "eps"),
    (r"\\hbar", "hbar"), (r"\\partial", "d"),
    (r"\\,|\\;|\\!|\\ ", " "),
    (r"\^\s*\{([^{}]+)\}", r"**(\1)"),
    (r"_\s*\{([^{}]+)\}", r"_\1"),
    (r"\{|\}", ""),
    (r"\\[a-zA-Z]+", ""),          # kalan komutlari at
]


def sadelestir(t):
    s = _temizle(t)
    for pat, rep in _SADE:
        s = re.sub(pat, rep, s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def cozumlenebilir_mi(t):
    """SymPy bu bagintiyi ayristirabiliyor mu? (simgeler, ok) doner."""
    s = sadelestir(t)
    if "=" not in s:
        return [], False
    sol, _, sag = s.partition("=")
    if not sol.strip() or not sag.strip():
        return [], False
    try:
        from .solver import parse
        a = parse(sol)
        b = parse(sag)
    except Exception:
        return [], False
    # "a, b" gibi girdiler demet olarak ayristirilabiliyor; bunlar denklem degil
    if not (hasattr(a, "free_symbols") and hasattr(b, "free_symbols")):
        return [], False
    simgeler = sorted({str(x) for x in (a.free_symbols | b.free_symbols)})
    if not (2 <= len(simgeler) <= 8):
        return simgeler, False
    return simgeler, True


def kaydet(latex, baglam, paper_id, konu=""):
    """Bir bagintiyi ayikla, dogrula ve sakla. Kabul edildiyse True."""
    t = _temizle(latex)
    if not bagintI_mi(t):
        return False
    simgeler, ok = cozumlenebilir_mi(t)
    db.queue_write(
        "INSERT INTO learned_eq(latex, sade, simgeler, cozulebilir, baglam, "
        "paper_id, konu, seen) VALUES(?,?,?,?,?,?,?,1) "
        "ON CONFLICT(latex) DO UPDATE SET seen = seen + 1",
        (t[:200], sadelestir(t)[:200], ",".join(simgeler)[:120],
         1 if ok else 0, (baglam or "")[:200], paper_id or 0, konu[:60]))
    return True


def ara(sorgu, limit=6, yalniz_cozulebilir=False):
    """Konuya gore ogrenilmis bagintilari getir."""
    n = normalize(sorgu or "").strip()
    if not n:
        return []
    kelimeler = [w for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{4,}", n)][:3]
    if not kelimeler:
        return []
    c = db.conn()
    kosul = " OR ".join(["LOWER(baglam) LIKE ?"] * len(kelimeler))
    args = ["%" + w + "%" for w in kelimeler]
    sql = ("SELECT latex, sade, simgeler, cozulebilir, baglam, seen "
           "FROM learned_eq WHERE (%s)" % kosul)
    if yalniz_cozulebilir:
        sql += " AND cozulebilir = 1"
    sql += " ORDER BY cozulebilir DESC, seen DESC LIMIT ?"
    args.append(limit)
    try:
        return [dict(r) for r in c.execute(sql, args)]
    except Exception:
        return []


def istatistik():
    c = db.conn()

    def one(q):
        try:
            r = c.execute(q).fetchone()
            return (r[0] if r and r[0] is not None else 0)
        except Exception:
            return 0

    return {
        "toplam": one("SELECT COUNT(*) FROM learned_eq"),
        "cozulebilir": one("SELECT COUNT(*) FROM learned_eq WHERE cozulebilir=1"),
    }


def temizle_eski():
    """Eski, ayiklanmamis formul yiginini sil."""
    try:
        c = db.conn()
        c.execute("DELETE FROM formulas_learned")
        c.commit()
        return True
    except Exception:
        return False
