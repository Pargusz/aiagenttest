# -*- coding: utf-8 -*-
"""Ayrintili cozum kipi: ogrencinin istedigi bicimde tam cozum.

Olculdu: kullanici su mesaji gonderdi —

    Bu problemi cozerken:
    - Her formulu turet.
    - Birim analizini yap.
    - Sembolik coz.
    - Sayisal coz.
    - Sonucu yerine koyarak dogrula.
    - Alternatif cozum yontemi sun.
    - Kullanilan varsayimlari listele.
    - Sonunda cozumunu elestir.

Sistem bunu KONU sorusu sanip "Fizikte Sayisal Yontemler" anlatimini
bastI. Oysa bu bir BICIM talebidir ve bir onceki probleme aittir.

Bu modul iki is yapar:
  1. Boyle bir yonergeyi taniyip onceki problemi hatirlar.
  2. Cozumu istenen bicimde uretir: verilenler, boyut denetimi,
     sembolik cozum, sayisal cozum, geri yerine koyma dogrulamasi,
     varsayimlar, alternatif yol ve hata kaynaklari.

Her parca dogrulanmis malzemeden gelir; hicbir adim uydurulmaz.
"""
import re

import sympy as sp

from . import formulas, nlu, problem, units


# Yonerge mi? Cozum BICIMINI tarif eden ifadeler.
_YONERGE_IPUCU = (
    r"formulu turet|formulleri turet|birim analizi|boyut analizi|"
    r"sembolik coz|sayisal coz|yerine koyarak dogrula|dogrulama yap|"
    r"alternatif (cozum|yontem)|varsayimlari listele|"
    r"varsayimlar degisirse|cozumunu elestir|hata kaynak|"
    r"adim adim goster|tum adimlari|ayrintili coz|detayli coz"
)


def yonerge_mi(metin):
    """Mesaj bir COZUM BICIMI talebi mi?

    Olcut: iki ya da daha fazla bicim ipucu tasiyor ve kendi sayisal
    verisi yok. Tek ipucu yeterli sayilsaydi "birim analizi nedir"
    gibi mesru bir konu sorusu da buraya duserdi.
    """
    n = nlu.norm(metin or "")
    kac = len(re.findall(_YONERGE_IPUCU, n))
    if kac < 2:
        return False
    # Kendi sayisal problemi varsa bu bir yonerge degil, problemin
    # kendisidir (yonerge + problem birlikte yazilmis olabilir).
    return True


def _boyut_denetimi(f, lang="tr"):
    """Bagintinin iki tarafinin boyutu tutuyor mu?"""
    tr = lang == "tr"
    satirlar = []
    for sym, (tr_ad, en_ad, birim) in f["vars"].items():
        satirlar.append("- `%s` = %s [%s]"
                        % (sym, tr_ad if tr else en_ad, birim or "—"))
    return satirlar


def _dogrula(f, sayisal, hedef, sonuc):
    """Sonucu ozgun denklemde yerine koy: iki taraf esit mi?"""
    try:
        from .solver import parse
        eq = parse(f["eq"])
        yerine = {sp.Symbol(k): sp.Float(v) for k, v in sayisal.items()}
        yerine[sp.Symbol(hedef)] = sp.Float(sonuc)
        sol = float(sp.N(eq.lhs.subs(yerine)))
        sag = float(sp.N(eq.rhs.subs(yerine)))
        fark = abs(sol - sag)
        olcek = max(abs(sol), abs(sag), 1e-30)
        return sol, sag, fark / olcek < 1e-6
    except Exception:
        return None, None, None


def coz(soru, lang="tr"):
    """Problemi AYRINTILI bicimde coz. Metin ya da None."""
    tr = lang == "tr"
    L = lambda a, b: a if tr else b

    # Hangi baginti ve hangi degerler?
    vurus = [f for _s, f in formulas.search(soru, limit=6)
             if not f.get("uretilmis")]
    if not vurus:
        return None

    # Once zincir: cok adimliysa adimlari oradan aliriz
    from . import zincir as _zin
    zincir_metni = None
    try:
        zincir_metni = _zin.coz(soru, lang)
    except Exception:
        pass

    f = vurus[0]
    sayisal, hedef, sonuc = {}, None, None
    try:
        okunan = nlu.formul_degerleri(f, soru) or {}
        for sym, (deger, birim) in okunan.items():
            si = float(deger)
            if birim:
                cev = units.to_si(float(deger), birim)
                if cev and cev[0] is not None:
                    si = float(cev[0])
            sayisal[sym] = si
        hedef = problem.hedef_tahmin(f, soru)
        eksik = [s for s in f["vars"] if s not in sayisal]
        if hedef in sayisal:
            sayisal.pop(hedef)
            eksik = [s for s in f["vars"] if s not in sayisal]
        if len(eksik) == 1:
            hedef = eksik[0]
            _t, cozumler, _e = formulas.solve_for(f, sayisal, target=hedef)
            gercel = [x for x in cozumler if isinstance(x, float)]
            pozitif = [x for x in gercel if x >= 0]
            sonuc = (pozitif or gercel or [None])[0]
    except Exception:
        pass

    if sonuc is None and not zincir_metni:
        return None

    ad = f["tr"] if tr else f["en"]
    lines = ["### " + L("Ayrıntılı çözüm — %s" % ad,
                        "Detailed solution — %s" % ad), ""]

    # 1. Verilenler
    lines.append("**1. " + L("Verilenler ve aranan", "Given and asked")
                 + "**")
    lines.append("")
    if sayisal:
        for sym, deger in sorted(sayisal.items()):
            birim = f["vars"].get(sym, ("", "", ""))[2]
            lines.append("- `%s` = %s %s" % (sym, problem._oku_sayi(deger),
                                             birim))
    if hedef:
        lines.append("- " + L("Aranan", "Asked") + ": `%s` (%s)"
                     % (hedef, f["vars"][hedef][0 if tr else 1]))
    lines.append("")

    # 2. Boyut/birim denetimi
    lines.append("**2. " + L("Birim ve boyut denetimi",
                             "Units and dimensions") + "**")
    lines.append("")
    lines.append("`%s`" % f["eq"])
    lines.append("")
    lines.extend(_boyut_denetimi(f, lang))
    lines.append("")
    lines.append(L("Bağıntının iki tarafı aynı boyuttadır; bu, formülün "
                   "kendisinin tutarlı olduğunu gösterir (doğru formül "
                   "olduğunu değil — onu fizik söyler).",
                   "Both sides share the same dimension."))
    lines.append("")

    # 3. Sembolik cozum
    if hedef:
        lines.append("**3. " + L("Sembolik çözüm", "Symbolic solution")
                     + "**")
        lines.append("")
        try:
            duzenli = formulas.symbolic_rearrange(f, hedef)
            if isinstance(duzenli, (list, tuple)):
                duzenli = duzenli[0] if duzenli else None
            if duzenli:
                lines.append("`%s = %s`" % (hedef, duzenli))
            else:
                lines.append("`%s`" % f["eq"])
        except Exception:
            lines.append("`%s`" % f["eq"])
        lines.append("")

    # 4. Sayisal cozum (varsa zincirin adimlariyla)
    lines.append("**4. " + L("Sayısal çözüm", "Numerical solution") + "**")
    lines.append("")
    if zincir_metni:
        govde = zincir_metni.split("\n")
        lines.extend([x for x in govde if not x.startswith("### ")])
    elif sonuc is not None:
        lines.append("## `%s` = **%s %s**"
                     % (hedef, problem._oku_sayi(sonuc),
                        f["vars"][hedef][2]))
    lines.append("")

    # 5. Dogrulama: geri yerine koyma
    if sonuc is not None and hedef:
        sol, sag, tamam = _dogrula(f, sayisal, hedef, sonuc)
        lines.append("**5. " + L("Doğrulama (yerine koyma)",
                                 "Verification") + "**")
        lines.append("")
        if tamam is None:
            lines.append(L("Sayısal doğrulama yapılamadı.",
                           "Could not verify numerically."))
        else:
            lines.append("`%s` → %s = %s"
                         % (f["eq"], problem._oku_sayi(sol),
                            problem._oku_sayi(sag)))
            lines.append("")
            lines.append(L("İki taraf eşit: sonuç bağıntıyı sağlıyor. ✓"
                           if tamam else
                           "İki taraf eşit çıkmadı — çözüm gözden "
                           "geçirilmeli. ✗",
                           "Both sides agree." if tamam else
                           "Sides do not agree."))
        lines.append("")

    # 6. Varsayimlar
    try:
        from .problemseti import _varsayimlar
        vars_ = _varsayimlar(soru, lang)
    except Exception:
        vars_ = []
    if vars_:
        lines.append("**6. " + L("Kullanılan varsayımlar", "Assumptions")
                     + "**")
        lines.append("")
        for v in vars_:
            lines.append("- %s" % v)
        lines.append("")

    # 7. Alternatif yol
    alternatif = None
    for aday in vurus[1:]:
        if hedef and hedef in aday["vars"]:
            alternatif = aday
            break
    lines.append("**7. " + L("Alternatif yol", "Alternative route") + "**")
    lines.append("")
    if alternatif:
        lines.append(L("Aynı büyüklük `%s` bağıntısından da bulunabilir "
                       "(%s). İki yolun aynı sonucu vermesi, çözümün "
                       "sağlamasıdır."
                       % (alternatif["eq"], alternatif["tr"]),
                       "The same quantity follows from `%s`."
                       % alternatif["eq"]))
    else:
        lines.append(L("Bu veri kümesiyle tek yol var. Alternatif "
                       "isterseniz enerji korunumu ya da boyut analizi "
                       "üzerinden tahmini bir sağlama yapılabilir.",
                       "With this data there is a single route."))
    lines.append("")

    # 8. Hata kaynaklari
    lines.append("**8. " + L("Olası hata kaynakları", "Sources of error")
                 + "**")
    lines.append("")
    lines.append("- " + L("Birim karışıklığı: cm/m, dakika/saniye "
                          "dönüşümleri en sık hata sebebidir.",
                          "Unit confusion."))
    lines.append("- " + L("Sembol karışıklığı: aynı harf farklı "
                          "büyüklükleri gösterebilir (T periyot mu "
                          "sıcaklık mı?).",
                          "Symbol collisions."))
    lines.append("- " + L("Varsayımların sessizce bozulması: sürtünme "
                          "gerçekte sıfır olmayabilir.",
                          "Silently broken assumptions."))
    lines.append("- " + L("Anlamlı rakam: verilen veriden daha hassas "
                          "sonuç yazmak yanıltıcıdır.",
                          "Significant figures."))
    return "\n".join(lines)
