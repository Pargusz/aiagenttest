"""Sembolik + sayisal hesaplama motoru (SymPy tabanli).

Turev, integral, limit, seri, denklem cozme, diferansiyel denklem, matris,
ozdeger, vektor analizi ve sayisal degerlendirme.
"""
import re
import math

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application,
    convert_xor,
)

TRANSFORMS = standard_transformations + (
    implicit_multiplication_application, convert_xor,
)

# Guvenli isim alani.
# Not: buyuk 'E' bilincli olarak Euler sayisina baglanmadi — fizikte E neredeyse
# her zaman enerji/elektrik alan anlamina gelir. Euler sayisi icin 'e' veya
# exp() kullanilabilir.
LOCALS = {
    "pi": sp.pi, "e": sp.E, "I": sp.I, "oo": sp.oo, "inf": sp.oo,
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "cot": sp.cot,
    "sec": sp.sec, "csc": sp.csc,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan, "atan2": sp.atan2,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "asinh": sp.asinh, "acosh": sp.acosh, "atanh": sp.atanh,
    "exp": sp.exp, "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt,
    "abs": sp.Abs, "Abs": sp.Abs, "sign": sp.sign,
    "factorial": sp.factorial, "gamma": sp.gamma, "binomial": sp.binomial,
    "floor": sp.floor, "ceiling": sp.ceiling,
    "erf": sp.erf, "erfc": sp.erfc, "besselj": sp.besselj, "bessely": sp.bessely,
    "legendre": sp.legendre, "hermite": sp.hermite, "laguerre": sp.laguerre,
    "Sum": sp.Sum, "Product": sp.Product, "Matrix": sp.Matrix,
    "diff": sp.diff, "integrate": sp.integrate, "limit": sp.limit,
    "conjugate": sp.conjugate, "re": sp.re, "im": sp.im, "arg": sp.arg,
}

# Turkce/Ingilizce yazim -> sympy
PREPROCESS = [
    (r"\bkok\s*\(", "sqrt("), (r"\bkarekok\s*\(", "sqrt("),
    (r"\bderece\b", "*pi/180"),
    (r"√", "sqrt"),
    (r"π", "pi"),
    (r"∞", "oo"),
    (r"×", "*"), (r"·", "*"), (r"÷", "/"),
    (r"−", "-"), (r"–", "-"),
    (r"\^", "**"),
]


class SolveError(Exception):
    pass


def preprocess(text):
    s = text.strip()
    for pat, rep in PREPROCESS:
        s = re.sub(pat, rep, s)
    # 3,14 -> 3.14  (ondalik virgul; ama f(a,b) bozulmasin diye sadece rakam-virgul-rakam
    # ve cevresinde parantez yoksa)
    if "(" not in s:
        s = re.sub(r"(?<=\d),(?=\d)", ".", s)
    # 2x -> 2*x zaten implicit multiplication ile hallediliyor
    return s


_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def build_locals(text, symbols=None):
    """Ifadedeki tanimlayicilari onceden sembol olarak kaydet.

    SymPy'nin ortuk carpim donusumu (implicit_multiplication_application)
    icinde `split_symbols` vardir; bu, `Tc` gibi cok karakterli adlari `T*c`
    seklinde parcalar. Fizikte `v0`, `Ek`, `Tc`, `m1`, `eps0` gibi adlar cok
    yaygin oldugu icin bunlari onceden local_dict'e koyuyoruz — boyle
    isimler bolunmez, ama `2x -> 2*x` gibi ortuk carpim calismaya devam eder.
    """
    ld = dict(LOCALS)
    if symbols:
        for name in symbols:
            ld[name] = sp.Symbol(name)
    for m in _IDENT.finditer(text or ""):
        name = m.group(0)
        if name not in ld:
            ld[name] = sp.Symbol(name)
    return ld


def parse(text, symbols=None):
    s = preprocess(text)
    try:
        return parse_expr(s, local_dict=build_locals(s, symbols),
                          transformations=TRANSFORMS, evaluate=True)
    except Exception as ex:
        raise SolveError("Ifade cozumlenemedi: %s" % ex)


def _sym(name):
    return sp.Symbol(name)


def numeric(expr, subs=None, digits=10):
    """Ifadeyi sayisal degerlendir."""
    try:
        e = expr.subs(subs or {})
        v = sp.N(e, digits)
        return v
    except Exception:
        return None


def fmt_expr(expr):
    """Ifadeyi okunakli metne cevir.

    Denklemler `Eq(a, b)` yerine `a = b` olarak yazilir.
    """
    try:
        if isinstance(expr, sp.Equality):
            return "%s = %s" % (sp.sstr(expr.lhs), sp.sstr(expr.rhs))
        return sp.sstr(expr)
    except Exception:
        return str(expr)


def tidy_ode(text, func="y", var="x"):
    """`Derivative(y(x), (x, 2))` -> `y''`, `y(x)` -> `y`."""
    s = text
    s = re.sub(r"Derivative\(\s*%s\(%s\)\s*,\s*\(\s*%s\s*,\s*(\d+)\s*\)\s*\)"
               % (func, var, var),
               lambda m: func + "'" * int(m.group(1)), s)
    s = re.sub(r"Derivative\(\s*%s\(%s\)\s*,\s*%s\s*\)" % (func, var, var),
               func + "'", s)
    s = re.sub(r"\b%s\(%s\)" % (func, var), func, s)
    return s


def latex(expr):
    try:
        return sp.latex(expr)
    except Exception:
        return ""


def pretty(expr):
    try:
        return sp.pretty(expr, use_unicode=True)
    except Exception:
        return str(expr)


# --- Ana islemler ------------------------------------------------------------

def evaluate(text):
    """Bir ifadeyi sadelestir ve mumkunse sayiya cevir."""
    expr = parse(text)
    simplified = expr
    try:
        simplified = sp.simplify(expr)
    except Exception:
        pass
    out = {"input": text, "expr": fmt_expr(expr), "latex": latex(expr),
           "simplified": fmt_expr(simplified), "simplified_latex": latex(simplified),
           "pretty": pretty(simplified)}
    free = simplified.free_symbols
    if not free:
        v = numeric(simplified)
        if v is not None:
            out["numeric"] = str(v)
            try:
                out["float"] = float(v)
            except Exception:
                pass
    else:
        out["variables"] = sorted([str(s) for s in free])
    return out


def solve_equation(text, var=None):
    """'x^2 - 4 = 0' veya 'x^2 = 4' bicimindeki denklemi coz."""
    t = preprocess(text)
    if "=" in t and "==" not in t:
        left, right = t.split("=", 1)
        eq = sp.Eq(parse(left), parse(right))
    else:
        eq = sp.Eq(parse(t), 0)
    free = sorted(eq.free_symbols, key=lambda s: str(s))
    if not free:
        return {"equation": fmt_expr(eq), "solutions": [],
                "note": "Denklemde bilinmeyen yok."}
    if var:
        target = _sym(var)
        if target not in free:
            target = free[0]
    else:
        pref = [s for s in free if str(s) in ("x", "y", "t", "z")]
        target = pref[0] if pref else free[0]
    try:
        sols = sp.solve(eq, target, dict=False)
    except Exception as ex:
        raise SolveError("Denklem cozulemedi: %s" % ex)
    if not isinstance(sols, (list, tuple)):
        sols = [sols]
    res = []
    for s in sols:
        item = {"expr": fmt_expr(s), "latex": latex(s)}
        if not s.free_symbols:
            v = numeric(s)
            if v is not None:
                item["numeric"] = str(v)
        res.append(item)
    return {"equation": fmt_expr(eq), "variable": str(target),
            "latex": latex(eq), "solutions": res}


def solve_system(lines):
    """Denklem sistemi coz."""
    eqs = []
    for ln in lines:
        t = preprocess(ln)
        if not t.strip():
            continue
        if "=" in t:
            a, b = t.split("=", 1)
            eqs.append(sp.Eq(parse(a), parse(b)))
        else:
            eqs.append(sp.Eq(parse(t), 0))
    if not eqs:
        raise SolveError("Denklem bulunamadi.")
    syms = sorted(set().union(*[e.free_symbols for e in eqs]), key=lambda s: str(s))
    sol = sp.solve(eqs, syms, dict=True)
    return {"equations": [fmt_expr(e) for e in eqs],
            "variables": [str(s) for s in syms],
            "solutions": [{str(k): fmt_expr(v) for k, v in d.items()} for d in sol]}


def derivative(text, var="x", order=1):
    expr = parse(text)
    x = _sym(var)
    if x not in expr.free_symbols and expr.free_symbols:
        x = sorted(expr.free_symbols, key=lambda s: str(s))[0]
    d = sp.diff(expr, x, order)
    ds = sp.simplify(d)
    return {"input": fmt_expr(expr), "variable": str(x), "order": order,
            "result": fmt_expr(ds), "latex": latex(ds), "pretty": pretty(ds)}


def integral(text, var="x", a=None, b=None):
    expr = parse(text)
    x = _sym(var)
    if x not in expr.free_symbols and expr.free_symbols:
        x = sorted(expr.free_symbols, key=lambda s: str(s))[0]
    if a is not None and b is not None:
        lo = parse(str(a)) if not isinstance(a, sp.Basic) else a
        hi = parse(str(b)) if not isinstance(b, sp.Basic) else b
        r = sp.integrate(expr, (x, lo, hi))
        out = {"input": fmt_expr(expr), "variable": str(x),
               "from": fmt_expr(lo), "to": fmt_expr(hi),
               "result": fmt_expr(r), "latex": latex(r), "definite": True}
        if not r.free_symbols:
            v = numeric(r)
            if v is not None:
                out["numeric"] = str(v)
        return out
    r = sp.integrate(expr, x)
    return {"input": fmt_expr(expr), "variable": str(x), "definite": False,
            "result": fmt_expr(r) + " + C", "latex": latex(r) + " + C",
            "pretty": pretty(r)}


def limit_of(text, var="x", to="0", direction="+"):
    expr = parse(text)
    x = _sym(var)
    pt = parse(str(to))
    try:
        r = sp.limit(expr, x, pt, direction if direction in ("+", "-") else "+")
    except Exception as ex:
        raise SolveError("Limit hesaplanamadi: %s" % ex)
    return {"input": fmt_expr(expr), "variable": str(x), "point": fmt_expr(pt),
            "result": fmt_expr(r), "latex": latex(r)}


def series(text, var="x", about="0", order=6):
    expr = parse(text)
    x = _sym(var)
    pt = parse(str(about))
    r = sp.series(expr, x, pt, order).removeO()
    return {"input": fmt_expr(expr), "variable": str(x), "about": fmt_expr(pt),
            "order": order, "result": fmt_expr(r), "latex": latex(r)}


def ode(text, func="y", var="x"):
    """Diferansiyel denklem coz. y'' + y = 0 gibi."""
    t = preprocess(text)
    x = _sym(var)
    f = sp.Function(func)
    # Ogrenci "4y" yazar, "4*y" degil. Sayi ile fonksiyon adi arasinda
    # kelime siniri olmadigi icin asagidaki \b tabanli degistirmeler bu
    # bicimi kaciriyordu ve "y'' + 4y = 0" cozulemiyordu (olculdu).
    t = re.sub(r"(\d)\s*(%s)\b" % func, r"\1*\2", t)
    # y'' -> Derivative(y(x), x, 2)
    t = re.sub(r"\b%s'''" % func, "Derivative(%s(%s),%s,3)" % (func, var, var), t)
    t = re.sub(r"\b%s''" % func, "Derivative(%s(%s),%s,2)" % (func, var, var), t)
    t = re.sub(r"\b%s'" % func, "Derivative(%s(%s),%s)" % (func, var, var), t)
    t = re.sub(r"\b%s(?!\w|\()" % func, "%s(%s)" % (func, var), t)
    loc = build_locals(t)
    loc[func] = f
    loc[var] = x
    loc["Derivative"] = sp.Derivative
    try:
        if "=" in t:
            a, b = t.split("=", 1)
            eq = sp.Eq(parse_expr(a, local_dict=loc, transformations=TRANSFORMS),
                       parse_expr(b, local_dict=loc, transformations=TRANSFORMS))
        else:
            eq = sp.Eq(parse_expr(t, local_dict=loc, transformations=TRANSFORMS), 0)
        sol = sp.dsolve(eq, f(x))
    except Exception as ex:
        raise SolveError("Diferansiyel denklem cozulemedi: %s" % ex)
    sols = sol if isinstance(sol, list) else [sol]
    return {"equation": tidy_ode(fmt_expr(eq), func, var),
            "function": "%s(%s)" % (func, var),
            "solutions": [{"expr": tidy_ode(fmt_expr(s), func, var),
                           "latex": latex(s)} for s in sols]}


def matrix_ops(rows, op="det"):
    M = sp.Matrix(rows)
    out = {"matrix": fmt_expr(M), "shape": "%dx%d" % (M.rows, M.cols)}
    if op in ("det", "determinant", "determinant"):
        out["determinant"] = fmt_expr(M.det())
    elif op in ("inv", "inverse", "ters"):
        out["inverse"] = fmt_expr(M.inv())
    elif op in ("eig", "eigen", "ozdeger"):
        ev = M.eigenvals()
        out["eigenvalues"] = {fmt_expr(k): v for k, v in ev.items()}
        try:
            vecs = M.eigenvects()
            out["eigenvectors"] = [
                {"value": fmt_expr(v), "mult": m,
                 "vectors": [fmt_expr(vv.T) for vv in vs]} for v, m, vs in vecs]
        except Exception:
            pass
    elif op in ("rank",):
        out["rank"] = M.rank()
    elif op in ("transpose", "devrik"):
        out["transpose"] = fmt_expr(M.T)
    elif op in ("trace", "iz"):
        out["trace"] = fmt_expr(M.trace())
    else:
        out["determinant"] = fmt_expr(M.det()) if M.rows == M.cols else None
    return out


def vector_calc(components, op, coords=("x", "y", "z")):
    """grad / div / curl / laplacian."""
    X = [_sym(c) for c in coords]
    if op in ("grad", "gradyan", "gradient"):
        f = parse(components) if isinstance(components, str) else components
        g = [sp.simplify(sp.diff(f, xi)) for xi in X]
        return {"operation": "gradient", "result": [fmt_expr(c) for c in g],
                "latex": r"\nabla f = \left(%s\right)" % ",\\ ".join(latex(c) for c in g)}
    F = [parse(c) if isinstance(c, str) else c for c in components]
    if op in ("div", "diverjans", "divergence"):
        d = sp.simplify(sum(sp.diff(F[i], X[i]) for i in range(3)))
        return {"operation": "divergence", "result": fmt_expr(d), "latex": latex(d)}
    if op in ("curl", "rotasyonel", "rot"):
        c1 = sp.simplify(sp.diff(F[2], X[1]) - sp.diff(F[1], X[2]))
        c2 = sp.simplify(sp.diff(F[0], X[2]) - sp.diff(F[2], X[0]))
        c3 = sp.simplify(sp.diff(F[1], X[0]) - sp.diff(F[0], X[1]))
        return {"operation": "curl", "result": [fmt_expr(c1), fmt_expr(c2), fmt_expr(c3)]}
    if op in ("laplacian", "laplas"):
        f = F[0]
        l = sp.simplify(sum(sp.diff(f, xi, 2) for xi in X))
        return {"operation": "laplacian", "result": fmt_expr(l), "latex": latex(l)}
    raise SolveError("Bilinmeyen vektor islemi: %s" % op)


def to_matlab(expr_text):
    """SymPy ifadesini MATLAB soz dizimine cevir."""
    from sympy.printing.octave import octave_code
    expr = parse(expr_text) if isinstance(expr_text, str) else expr_text
    return octave_code(expr)
