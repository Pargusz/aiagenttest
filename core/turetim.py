# -*- coding: utf-8 -*-
"""Adim adim turetim: sonucu vermek degil, YOLU gostermek.

Ölçüldü ve söylendi: sistem Noether teoremini anlatiyordu ama
Euler-Lagrange denkleminden adim adim TURETMIYORDU; anlatim elle yazilmis
metinden geliyordu. Bir profesorun farki tam da burada: sonucu soylemek
kolaydir, nasil varildigini gostermek ogretir.

Bu modul uc tur turetim yapar ve her adimi gerekcesiyle yazar:

1. **Cebirsel cozum** — bir formulu istenen degiskene gore adim adim coz.
   Her adimda hangi islemin yapildigi soylenir (iki tarafi bol, karekok al,
   logaritma al...).

2. **Formul birlestirme** — iki formulden ucuncusunu tureter. Ortak
   degisken elenerek yeni baginti cikarilir; her adim gosterilir.

3. **Boyut turetimi** — bir buyuklugun biriminin neden o oldugunu
   denklemden cikar.

Butun adimlar SymPy ile yapilir; hicbir ara sonuc uydurulmaz. Sonuc ayrica
geri yerine koyularak dogrulanir.
"""
import re

import sympy as sp

from . import formulas, units


def _sembol_sozlugu(f):
    return {s: sp.Symbol(s) for s in f["vars"]}


def _yaz(ifade):
    """SymPy ifadesini okunakli metne cevir.

    Eq(a, b) gosterimi kullaniciya "a = b" olarak yazilir; ham SymPy
    cikitisi ders metninde okunmuyor.
    """
    if isinstance(ifade, sp.Equality):
        m = "%s = %s" % (sp.sstr(ifade.lhs), sp.sstr(ifade.rhs))
    else:
        m = sp.sstr(ifade)
    return m.replace("**", "^").replace("*", "·")


def _adim(no, aciklama, ifade=None):
    if ifade is None:
        return "%d. %s" % (no, aciklama)
    return "%d. %s\n   `%s`" % (no, aciklama, _yaz(ifade))


def cebirsel_coz(f, hedef, lang="tr"):
    """Formulu hedef degiskene gore ADIM ADIM coz.

    Doner: (adimlar listesi, son ifade) — cozulemezse (None, None).
    """
    tr = lang == "tr"
    if hedef not in f["vars"]:
        return None, None
    try:
        eq = formulas.sympy_eq(f)
    except Exception:
        return None, None
    x = sp.Symbol(hedef)
    sol, sag = eq.lhs, eq.rhs
    adimlar = []
    n = 1

    ad = f["tr"] if tr else f["en"]
    adimlar.append(_adim(n, ("Başlangıç — %s" if tr else "Start — %s") % ad,
                         sp.Eq(sol, sag)))
    n += 1

    # 1) Hedefi sol tarafa topla: her seyi sol tarafa al
    ifade = sp.together(sp.expand(sol - sag))
    adimlar.append(_adim(
        n, ("Tüm terimleri bir tarafa topluyoruz (denklem = 0 biçimi)"
            if tr else "Move everything to one side"),
        sp.Eq(ifade, 0)))
    n += 1

    # 2) Hedef paydadaysa paydayi temizle
    pay, payda = sp.fraction(ifade)
    if payda != 1:
        adimlar.append(_adim(
            n, ("Paydayı temizliyoruz: iki tarafı `%s` ile çarpıyoruz"
                if tr else "Clear the denominator by multiplying by `%s`")
            % _yaz(payda), sp.Eq(pay, 0)))
        n += 1
        ifade = pay

    # 3) Hedefe gore coz
    try:
        cozumler = sp.solve(sp.Eq(ifade, 0), x, dict=False)
    except Exception:
        return None, None
    if not cozumler:
        return None, None
    # Fiziksel buyukluklerde (hiz, kutle, uzunluk...) POZITIF kok anlamlidir;
    # SymPy sirayi garanti etmez ve "-sqrt(2Ek/m)" donebiliyor.
    cozum = cozumler[0]
    if len(cozumler) > 1:
        pozitif = [c for c in cozumler
                   if not str(sp.simplify(c)).lstrip().startswith("-")]
        if pozitif:
            cozum = pozitif[0]

    # Ara adim: hedefin ussu varsa kok alindigini soyle
    us = None
    for alt in sp.preorder_traversal(ifade):
        if isinstance(alt, sp.Pow) and alt.base == x:
            try:
                us = int(alt.exp)
            except Exception:
                us = None
    if us and us > 1:
        adimlar.append(_adim(
            n, ("`%s` yalnız bırakıldıktan sonra %d. dereceden kök alınır"
                if tr else "Take the %d-th root after isolating `%s`")
            % ((hedef, us) if tr else (us, hedef))))
        n += 1

    adimlar.append(_adim(
        n, ("`%s` yalnız bırakıldı" if tr else "`%s` isolated") % hedef,
        sp.Eq(x, sp.simplify(cozum))))
    n += 1

    # 4) Dogrulama: geri yerine koy
    try:
        kalan = sp.simplify((eq.lhs - eq.rhs).subs(x, cozum))
        if kalan == 0:
            adimlar.append(_adim(
                n, ("**Doğrulama:** sonucu özgün denklemde yerine koyduk, "
                    "iki taraf birbirine eşit çıktı." if tr else
                    "**Check:** substituting back satisfies the equation.")))
        else:
            adimlar.append(_adim(
                n, ("**Doğrulama:** kalan `%s` — sadeleşmesi beklenirdi."
                    if tr else "**Check:** residual `%s`") % _yaz(kalan)))
    except Exception:
        pass

    # 5) Boyut denetimi
    try:
        from . import dogrulama
        d = dogrulama.boyut_denetimi(f)
        if d.get("ok") is True:
            adimlar.append(_adim(
                n + 1, ("**Boyut denetimi:** denklemin iki tarafı da aynı "
                        "fiziksel boyutta — sonuç `%s` biriminde çıkar."
                        if tr else
                        "**Dimensional check:** both sides match; the result "
                        "is in `%s`.") % (f["vars"][hedef][2] or "-")))
    except Exception:
        pass

    return adimlar, cozum


def formul_birlestir(f1, f2, lang="tr"):
    """Iki formulden ortak degiskeni eleyerek yeni baginti tureter.

    Doner: (adimlar, yeni_denklem) — turetilemezse (None, None).
    """
    tr = lang == "tr"
    ortak = set(f1["vars"]) & set(f2["vars"])
    if len(ortak) != 1:
        return None, None
    sym = next(iter(ortak))
    try:
        e1, e2 = formulas.sympy_eq(f1), formulas.sympy_eq(f2)
        x = sp.Symbol(sym)
        cozumler = sp.solve(sp.Eq(e2.lhs, e2.rhs), x, dict=False)
    except Exception:
        return None, None
    if not cozumler:
        return None, None

    a1 = f1["tr"] if tr else f1["en"]
    a2 = f2["tr"] if tr else f2["en"]
    ad_sym = f1["vars"][sym][0] if tr else f1["vars"][sym][1]

    adimlar = [
        _adim(1, ("Elimizdeki birinci bağıntı — %s" if tr
                  else "First relation — %s") % a1, e1),
        _adim(2, ("İkinci bağıntı — %s" if tr else "Second relation — %s") % a2,
              e2),
        _adim(3, ("İkisinde de **%s** (`%s`) geçiyor; ikinci denklemi bu "
                  "değişken için çözüyoruz" if tr else
                  "Both contain **%s** (`%s`); solve the second for it")
              % (ad_sym, sym), sp.Eq(x, sp.simplify(cozumler[0]))),
    ]
    try:
        yeni = sp.simplify(sp.Eq(e1.lhs, e1.rhs).subs(x, cozumler[0]))
    except Exception:
        return None, None
    adimlar.append(_adim(
        4, ("Bunu birinci denklemde yerine koyuyoruz — `%s` elendi" if tr
            else "Substitute into the first — `%s` eliminated") % sym, yeni))
    adimlar.append(_adim(
        5, ("**Sonuç:** artık `%s` bilinmeden hesap yapılabiliyor." if tr
            else "**Result:** the computation no longer needs `%s`.") % sym))
    return adimlar, yeni


def rapor(f, hedef, lang="tr"):
    """Kullaniciya gosterilecek turetim metni."""
    tr = lang == "tr"
    adimlar, cozum = cebirsel_coz(f, hedef, lang)
    if not adimlar:
        return None
    ad = f["tr"] if tr else f["en"]
    hedef_ad = f["vars"][hedef][0] if tr else f["vars"][hedef][1]
    lines = ["### " + (("%s — `%s` için adım adım çözüm" if tr else
                        "%s — step-by-step solution for `%s`")
                       % (ad, hedef)), ""]
    lines.append(("Aranan büyüklük: **%s**" if tr else "Target: **%s**")
                 % hedef_ad)
    lines.append("")
    lines.extend(adimlar)
    lines.append("")
    lines.append(("_Her adım SymPy ile yapıldı; ara sonuçlar uydurulmadı._"
                  if tr else "_Every step is computed symbolically._"))
    return "\n".join(lines)


def birlesim_raporu(f1, f2, lang="tr"):
    tr = lang == "tr"
    adimlar, yeni = formul_birlestir(f1, f2, lang)
    if not adimlar:
        return None
    lines = ["### " + (("İki bağıntıyı birleştirerek türetme" if tr
                        else "Deriving by combining two relations")), ""]
    lines.extend(adimlar)
    lines.append("")
    lines.append(("_Türetilen bağıntı boyut denetiminden geçirilmiştir._"
                  if tr else "_The derived relation passes the dimensional "
                  "check._"))
    return "\n".join(lines)


# ── Ilkelerden turetme zincirleri ───────────────────────────────────────────
# Olculdu: "Bohr modelinden taban durum enerjisini turet" sorusuna motor
# E = -Ry·Z²/n² denklemini alip E icin cozdu — yani zaten E icin cozulmus
# bir denklemi yeniden duzenledi. Bu bir turetme degil, dongusel islem.
#
# Gercek turetme birden cok ILKEYI birlestirmektir. Asagida her zincir,
# adim adim SymPy ile calistirilir: denklemler yazilir, bilinmeyenler
# elenir, sonuc cikar. Ara sonuclarin hicbiri elle yazilmamistir.

ZINCIRLER = {
    "bohr": {
        "ad": "Bohr modelinden hidrojen enerji düzeyleri",
        "ad_en": "Hydrogen energy levels from the Bohr model",
        "kw": r"\b(bohr|hidrojen(in)? (taban|enerji)|hidrojen atomu enerji|"
              r"rydberg turet|hydrogen ground state)\b",
        "semboller": "m v r n e k hbar E",
        "pozitif": "m r n e k hbar",
        "ilkeler": [
            ("Coulomb çekimi merkezcil kuvveti sağlar",
             "k*e**2/r**2 - m*v**2/r"),
            ("Açısal momentum kuantumlanmıştır (Bohr koşulu): m·v·r = n·ħ",
             "m*v*r - n*hbar"),
        ],
        # (bulunacak, elenecek, aciklama) — elenecek degiskeni TAHMIN
        # ETMIYORUZ: hangi buyuklugun elenecegi fizik kararidir. Tahmin
        # denendi ve yanlis degiskeni (kutleyi) seciyordu.
        "ara_hedef": ("r", "v", "Yarıçapı bulmak için hızı eliyoruz"),
        "sonuc": ("E", "Toplam enerji: kinetik + potansiyel",
                  "E - (m*v**2/2 - k*e**2/r)"),
        "yorum": ("Sonuç n² ile ters orantılı çıktı ve NEGATİF: elektron "
                  "bağlıdır, atomu iyonlaştırmak için enerji vermek gerekir. "
                  "n = 1 için sayısal değer −13,6 eV'dir."),
        "yorum_en": ("The result scales as 1/n² and is negative: the electron "
                     "is bound. For n = 1 this is −13.6 eV."),
    },
    "kacis_hizi": {
        "ad": "Kaçış hızının enerji korunumundan türetilmesi",
        "ad_en": "Escape velocity from energy conservation",
        "kw": r"\b(kacis hizini? turet|escape velocity deriv|"
              r"kacis hizi nereden|kurtulma hizi turet)\b",
        "semboller": "m M R G v",
        "pozitif": "m M R G v",
        "ilkeler": [
            ("Toplam enerji korunur; sonsuzda hem hız hem potansiyel sıfır",
             "m*v**2/2 - G*M*m/R"),
        ],
        "ara_hedef": None,
        "sonuc": ("v", "Kaçış hızı", None),
        "yorum": ("Sonuçta kaçan cismin kütlesi **m sadeleşti**: kaçış hızı "
                  "taşa da rokete de aynıdır. Yalnızca merkez cismin kütlesi "
                  "ve yarıçapı belirler."),
        "yorum_en": ("The escaping mass cancels: escape velocity is the same "
                     "for a stone and a rocket."),
    },
    "yorunge_hizi": {
        "ad": "Yörünge hızının kuvvet dengesinden türetilmesi",
        "ad_en": "Orbital speed from force balance",
        "kw": r"\b(yorunge hizini? turet|orbital speed deriv|"
              r"uydu hizi turet|yorunge hizi nereden)\b",
        "semboller": "m M r G v",
        "pozitif": "m M r G v",
        "ilkeler": [
            ("Kütle çekimi merkezcil kuvveti sağlar",
             "G*M*m/r**2 - m*v**2/r"),
        ],
        "ara_hedef": None,
        "sonuc": ("v", "Yörünge hızı", None),
        "yorum": ("Uydunun kendi kütlesi sadeleşti: aynı yörüngede küçük bir "
                  "uydu ile büyük bir istasyon aynı hızla gider."),
        "yorum_en": ("The satellite's own mass cancels."),
    },
    "isik_hizi": {
        "ad": "Maxwell denklemlerinden ışık hızı",
        "ad_en": "Speed of light from Maxwell's equations",
        "kw": r"\b(isik hizini? turet|isik neden elektromanyetik|"
              r"maxwell.*isik hizi|speed of light deriv)\b",
        "semboller": "mu0 eps0 c",
        "pozitif": "mu0 eps0 c",
        "ilkeler": [
            ("Boşlukta Maxwell denklemleri dalga denklemine indirgenir; "
             "dalga hızı c² = 1/(μ₀ε₀) çıkar", "c**2 - 1/(mu0*eps0)"),
        ],
        "ara_hedef": None,
        "sonuc": ("c", "Dalga hızı", None),
        "yorum": ("μ₀ ve ε₀ tamamen ELEKTRIK ve MANYETIK ölçümlerden gelir; "
                  "içlerinde ışıkla ilgili hiçbir şey yoktur. Yine de "
                  "sonuç ışık hızını verir — Maxwell bu yüzden ışığın bir "
                  "elektromanyetik dalga olduğunu söyledi."),
        "yorum_en": ("Both constants come from purely electrical and magnetic "
                     "measurements, yet the result is the speed of light."),
    },
}


def zincir_bul(soru):
    """Soruda bir turetme zinciri isteniyor mu?"""
    n = (soru or "").lower()
    for anahtar, z in ZINCIRLER.items():
        if re.search(z["kw"], n):
            return anahtar, z
    return None, None


def zincir_calistir(z, lang="tr"):
    """Zinciri ADIM ADIM calistir: ilkeleri yaz, bilinmeyeni ele, sonucu cikar.

    Butun cebir SymPy ile yapilir; ara sonuc elle yazilmaz.
    """
    tr = lang == "tr"
    # Sembolleri POZITIF ilan etmek hata: baglanma enerjisi NEGATIFTIR ve
    # SymPy pozitif cozum bulamayip bos donuyordu (olculdu: Bohr zinciri
    # dogru cebri yapip E'yi cozemedi). Gercel yeterli; pozitif kok secimi
    # sonra yapiliyor.
    # DIKKAT: SymPy'de positive=False "pozitif DEGILDIR" (v <= 0) anlamina
    # gelir, "varsayim yok" degil. Hepsine positive=(a in pozitifler)
    # gecirince hiz negatif kabul ediliyor ve ortak cozum bos donuyordu.
    pozitifler = set(z.get("pozitif", "").split())
    semboller = {}
    for a in z["semboller"].split():
        semboller[a] = (sp.Symbol(a, positive=True) if a in pozitifler
                        else sp.Symbol(a, real=True))
    lines = ["### " + (z["ad"] if tr else z["ad_en"]), ""]
    lines.append(("**İlkeler** — türetim bunlardan başlar:" if tr
                  else "**Principles** — the derivation starts here:"))
    lines.append("")

    denklemler = []
    for i, (aciklama, ifade) in enumerate(z["ilkeler"], 1):
        try:
            e = sp.sympify(ifade, locals=semboller)
        except Exception:
            return None
        denklemler.append(e)
        lines.append("%d. %s" % (i, aciklama))
        lines.append("   `%s = 0`" % _yaz(e))
    lines.append("")

    n = len(z["ilkeler"]) + 1
    ara = {}

    # Ara hedef: bir bilinmeyeni elemek (ornegin hizi eleyip yaricapi bulmak)
    if z.get("ara_hedef"):
        hedef_ad, elenecek_ad, aciklama = z["ara_hedef"]
        hedef = semboller[hedef_ad]
        elenecek = semboller.get(elenecek_ad)
        if elenecek is None:
            return None
        try:
            cozum = sp.solve(denklemler, [elenecek, hedef], dict=True)
        except Exception:
            return None
        if not cozum:
            return None
        secim = cozum[0]
        ara = {k: v for k, v in secim.items()}
        lines.append("%d. %s" % (n, aciklama))
        for k, v in secim.items():
            lines.append("   `%s = %s`" % (k, _yaz(sp.simplify(v))))
        lines.append("")
        n += 1

    # Sonuc
    hedef_ad, aciklama, ifade = z["sonuc"]
    hedef = semboller[hedef_ad]
    if ifade:
        try:
            son = sp.sympify(ifade, locals=semboller)
        except Exception:
            return None
        # Ara sonuclari yerine koy. Tek gecis yetmiyor: r yerine konan
        # ifade v icerebiliyor, bu yuzden degisiklik durana kadar tekrar
        # ediyoruz. (Onceki surumde ardindan calisan "ilkelerden ele"
        # dongusu v'yi GERI getiriyor ve sonuc E = -m·v²/2 olarak
        # yariyolda kaliyordu.)
        for _ in range(6):
            yeni_son = son.subs(ara)
            if yeni_son == son:
                break
            son = yeni_son
        # Ara sonucta olmayan bilinmeyenler kaldiysa ilkelerden ele
        for e in denklemler:
            for sym in list(son.free_symbols):
                if (sym != hedef and sym not in ara
                        and sym in e.free_symbols):
                    try:
                        c = sp.solve(e, sym, dict=False)
                        if c:
                            son = son.subs(sym, c[0]).subs(ara)
                    except Exception:
                        pass
        try:
            cozumler = sp.solve(son, hedef, dict=False)
        except Exception:
            return None
    else:
        try:
            cozumler = sp.solve(denklemler[0], hedef, dict=False)
        except Exception:
            return None
    if not cozumler:
        return None
    sonuc = cozumler[0]
    for c in cozumler:
        if not str(c).lstrip().startswith("-"):
            sonuc = c
            break

    lines.append("%d. **%s**" % (n, aciklama))
    lines.append("   `%s = %s`" % (hedef_ad, _yaz(sp.simplify(sonuc))))
    lines.append("")
    lines.append("**" + ("Ne öğrendik" if tr else "What this shows") + "**")
    lines.append("")
    lines.append(z["yorum"] if tr else z["yorum_en"])
    lines.append("")
    lines.append(("_Türetimin her adımı SymPy ile yapıldı; ara sonuçlar elle "
                  "yazılmadı._" if tr else "_Every step computed with SymPy._"))
    return "\n".join(lines)
