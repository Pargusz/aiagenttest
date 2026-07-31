# -*- coding: utf-8 -*-
"""Euler-Lagrange ile hareket denklemi turetimi.

Olculdu: "lagrange ile sarkacin hareket denklemini turet" sorusu once
alakasiz bir formulun cebirini gosteriyordu, duzeltince de titresim
konusunun anlatimina gidiyordu. Ikisi de ogrencinin istedigi sey degil.
Ikinci sinif bir fizik ogrencisi bunu ister:

    L = T - V  yaz  →  d/dt(∂L/∂q̇) - ∂L/∂q = 0  uygula  →  denklemi al

Buradaki her turev SymPy ile ALINIR; hicbir ara adim elle yazilmaz.
Boylece anlatilan yontem ile uretilen sonuc ayni kaynaktan gelir.

Sistemler elle tanimlanmistir: hangi genellestirilmis koordinatin
secilecegi ve kinetik/potansiyel enerjinin nasil yazilacagi FIZIK
bilgisidir, korpustan cikarilamaz.
"""
import re

import sympy as sp


t = sp.Symbol("t")


def _q(ad="q"):
    return sp.Function(ad)(t)


def _sarkac():
    # Uzunluk icin "L" kullanmak Lagrange fonksiyonunun L'siyle
    # karisiyor; fizik metinlerindeki gibi kucuk l aliyoruz.
    m, l, g = sp.symbols("m l g", positive=True)
    th = _q("theta")
    # Konum: x = l sin(th), y = -l cos(th)
    hiz2 = (l * sp.diff(th, t)) ** 2
    T = sp.Rational(1, 2) * m * hiz2
    V = m * g * l * (1 - sp.cos(th))
    return {
        "ad": "Basit sarkac",
        "koordinat": th,
        "koordinat_adi": "theta",
        "T": T, "V": V,
        "aciklama": ("Genellestirilmis koordinat aci (θ). Kutle ipin "
                     "ucunda, ip uzunlugu l sabit; tek serbestlik "
                     "derecesi vardir."),
        "yorum": ("Kucuk acilarda sin θ ≈ θ alinirsa θ'' + (g/l)θ = 0 "
                  "olur: basit harmonik hareket, ω = √(g/l). Periyodun "
                  "kutleye BAGLI OLMAMASI buradan gelir."),
    }


def _yay_kutle():
    m, k = sp.symbols("m k", positive=True)
    x = _q("x")
    T = sp.Rational(1, 2) * m * sp.diff(x, t) ** 2
    V = sp.Rational(1, 2) * k * x ** 2
    return {
        "ad": "Yay-kutle sistemi",
        "koordinat": x, "koordinat_adi": "x",
        "T": T, "V": V,
        "aciklama": "Tek boyutta yer degistirme x genellestirilmis "
                    "koordinattir.",
        "yorum": "Sonuc m·x'' = -k·x, yani Hooke yasasi. Lagrange "
                 "yontemi Newton ile ayni denklemi verir — vermeliydi de.",
    }


def _serbest_dusme():
    m, g = sp.symbols("m g", positive=True)
    y = _q("y")
    T = sp.Rational(1, 2) * m * sp.diff(y, t) ** 2
    V = m * g * y
    return {
        "ad": "Serbest düşme",
        "koordinat": y, "koordinat_adi": "y",
        "T": T, "V": V,
        "aciklama": "Yukseklik y tek koordinattir; yerçekimi sabit.",
        "yorum": "Sonuc y'' = -g. Kutle sadelesir: agir ve hafif cisim "
                 "ayni ivmeyle duser.",
    }


def _atwood():
    m1, m2, g = sp.symbols("m1 m2 g", positive=True)
    x = _q("x")
    T = sp.Rational(1, 2) * (m1 + m2) * sp.diff(x, t) ** 2
    V = -m1 * g * x + m2 * g * x
    return {
        "ad": "Atwood makinesi",
        "koordinat": x, "koordinat_adi": "x",
        "T": T, "V": V,
        "aciklama": "Ip uzamaz: iki kutle tek bir x koordinatiyla "
                    "baglidir. Kisit boylece koordinat SECIMINE gomulur; "
                    "ip gerilimi hic hesaba girmez.",
        "yorum": "Sonuc (m₁+m₂)x'' = (m₁-m₂)g. Newton ile cozerken "
                 "gerilimi bilinmeyen olarak tasimak gerekirdi; Lagrange "
                 "yonteminin kazanci tam olarak budur.",
    }


def _egik_atis():
    m, g = sp.symbols("m g", positive=True)
    y = _q("y")
    T = sp.Rational(1, 2) * m * sp.diff(y, t) ** 2
    V = m * g * y
    return {
        "ad": "Düşey hareket (eğik atışın düşey bileşeni)",
        "koordinat": y, "koordinat_adi": "y",
        "T": T, "V": V,
        "aciklama": "Yatay yonde kuvvet yok, o yuzden yatay denklem "
                    "asikardir; ilginc olan dusey bilesendir.",
        "yorum": "y'' = -g. Yatayda x'' = 0 oldugu icin yorunge paraboldur.",
    }


SISTEMLER = [
    (r"sarkac|pendul|salinim yapan|ipin ucunda", _sarkac),
    (r"yay|hooke|harmonik osilator|spring", _yay_kutle),
    (r"atwood|makara|iki kutle ip", _atwood),
    (r"serbest dusme|dusen cisim|free fall", _serbest_dusme),
    (r"egik atis|projektil|atis hareketi", _egik_atis),
]

_ISTEK = re.compile(
    r"(lagrange|lagranj|euler-?lagrange|en kucuk etki|varyasyon)", re.I)


def istek_mi(soru):
    """Soru gercekten Lagrange yontemiyle turetim istiyor mu?"""
    return bool(_ISTEK.search(soru or ""))


def sistem_bul(soru):
    n = (soru or "").lower()
    for kalip, fn in SISTEMLER:
        if re.search(kalip, n):
            return fn()
    return None


def turet(soru, lang="tr"):
    """Euler-Lagrange denklemini adim adim uygula.

    Doner: metin ya da None.
    """
    if not istek_mi(soru):
        return None
    sis = sistem_bul(soru)
    if sis is None:
        return None
    tr = lang == "tr"

    q = sis["koordinat"]
    qd = sp.diff(q, t)
    T, V = sis["T"], sis["V"]
    L = sp.simplify(T - V)

    # Euler-Lagrange: d/dt(dL/dq') - dL/dq = 0
    dL_dqd = sp.simplify(sp.diff(L, qd))
    ddt = sp.simplify(sp.diff(dL_dqd, t))
    dL_dq = sp.simplify(sp.diff(L, q))
    denklem = sp.simplify(ddt - dL_dq)

    # Ivme icin coz
    qdd = sp.diff(q, t, 2)
    try:
        cozum = sp.solve(sp.Eq(denklem, 0), qdd, dict=False)
        ivme = sp.simplify(cozum[0]) if cozum else None
    except Exception:
        ivme = None

    def g(e):
        m_ = sp.sstr(e)
        # Derivative(theta(t), (t, 2)) -> theta''  ;  Derivative(x(t), t) -> x'
        m_ = re.sub(r"Derivative\(([A-Za-z_]\w*)\(t\),\s*\(t,\s*2\)\)",
                    r"\1''", m_)
        m_ = re.sub(r"Derivative\(([A-Za-z_]\w*)\(t\),\s*t\)", r"\1'", m_)
        return m_.replace("(t)", "")

    ad = sis["koordinat_adi"]
    satirlar = []
    satirlar.append("### %s — %s" % (
        sis["ad"], "Lagrange ile hareket denklemi" if tr
        else "Equation of motion via Lagrange"))
    satirlar.append("")
    satirlar.append("**1. %s**" % ("Genelleştirilmiş koordinat" if tr
                                   else "Generalised coordinate"))
    satirlar.append("")
    satirlar.append("`%s`  —  %s" % (ad, sis["aciklama"]))
    satirlar.append("")
    satirlar.append("**2. %s**" % ("Kinetik ve potansiyel enerji" if tr
                                   else "Kinetic and potential energy"))
    satirlar.append("")
    satirlar.append("`T = %s`" % g(T))
    satirlar.append("")
    satirlar.append("`V = %s`" % g(V))
    satirlar.append("")
    satirlar.append("**3. %s**" % ("Lagrange fonksiyonu L = T − V" if tr
                                   else "Lagrangian L = T − V"))
    satirlar.append("")
    satirlar.append("`L = %s`" % g(L))
    satirlar.append("")
    satirlar.append("**4. %s**" % ("Euler-Lagrange denklemini uygula" if tr
                                   else "Apply the Euler-Lagrange equation"))
    satirlar.append("")
    satirlar.append("`d/dt(∂L/∂%s') − ∂L/∂%s = 0`" % (ad, ad))
    satirlar.append("")
    satirlar.append("- `∂L/∂%s' = %s`" % (ad, g(dL_dqd)))
    satirlar.append("- `d/dt(∂L/∂%s') = %s`" % (ad, g(ddt)))
    satirlar.append("- `∂L/∂%s = %s`" % (ad, g(dL_dq)))
    satirlar.append("")
    satirlar.append("**5. %s**" % ("Hareket denklemi" if tr
                                  else "Equation of motion"))
    satirlar.append("")
    satirlar.append("`%s = 0`" % g(denklem))
    if ivme is not None:
        satirlar.append("")
        satirlar.append("## `%s'' = %s`" % (ad, g(ivme)))
    satirlar.append("")
    satirlar.append("> %s" % sis["yorum"])
    satirlar.append("")
    satirlar.append("_%s_" % (
        "Her türev SymPy ile alındı; ara adımlar elle yazılmadı."
        if tr else "Every derivative was computed with SymPy."))
    return "\n".join(satirlar)
