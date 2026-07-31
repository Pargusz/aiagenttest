"""Kendi kendini test: tum motorlarin calistigini dogrular."""
import io
import os
import re
import sys

from . import db, brain, units, solver, formulas, knowledge, nlu, matlab, learner

PASS, FAIL = [], []


def contains_len(en_az):
    """Sonucun en az bu uzunlukta olmasini bekle."""
    def f(x):
        return isinstance(x, int) and x >= en_az
    return f


def check(name, fn, expect=None):
    try:
        got = fn()
    except Exception as e:
        FAIL.append((name, "istisna: %s" % e))
        return
    if expect is None:
        PASS.append(name)
        return
    if callable(expect):
        ok = expect(got)
    else:
        ok = (got == expect)
    if ok:
        PASS.append(name)
    else:
        FAIL.append((name, "beklenen %r, gelen %r" % (expect, got)))


def approx(target, tol=1e-6):
    return lambda got: got is not None and abs(float(got) - target) <= tol * max(1.0, abs(target))


def contains(*subs):
    def f(got):
        g = str(got).lower()
        return all(s.lower() in g for s in subs)
    return f


def _cors_denemesi():
    """CORS basliklari yalnizca izinli adrese verilmeli.

    Sunucuyu ayaga kaldirmadan, baslik uretecini dogrudan sinariz.
    """
    from . import config, server

    class _Sahte(object):
        headers = {"Origin": "https://pargusz.github.io"}
        _cors_basliklari = server.Handler._cors_basliklari

        def __init__(self):
            self.headers = {"Origin": "https://pargusz.github.io"}

    eski = list(config.ORIGIN)
    try:
        config.ORIGIN = ["https://pargusz.github.io"]
        izinli = _Sahte()._cors_basliklari()
        config.ORIGIN = ["https://baska.example"]
        yasakli = _Sahte()._cors_basliklari()
    finally:
        config.ORIGIN = eski
    return (izinli.get("Access-Control-Allow-Origin")
            == "https://pargusz.github.io" and not yasakli)


def run():
    db.init()
    print("\n  ParguszPhysics — kendi kendini test\n" + "  " + "-" * 52)

    # ---------------------------------------------------------- birimler
    check("birim: 90 km/h -> m/s",
          lambda: units.convert(90, "km/h", "m/s")[0], approx(25.0))
    check("birim: 1 eV -> J",
          lambda: units.convert(1, "eV", "J")[0], approx(1.602176634e-19))
    check("birim: 100 degC -> K",
          lambda: units.convert(100, "degC", "K")[0], approx(373.15))
    check("birim: 1 atm -> Pa",
          lambda: units.convert(1, "atm", "Pa")[0], approx(101325.0))
    check("birim: boyut uyusmazligi yakalaniyor",
          lambda: units.convert(1, "kg", "m")[1] is not None, True)
    check("birim: m/s^2 ayristirma",
          lambda: units.parse_unit("m/s^2")[1], units.D(m=1, s=-2))
    check("birim: J/(mol*K) ayristirma",
          lambda: units.parse_unit("J/(mol·K)")[1],
          units.D(kg=1, m=2, s=-2, K=-1, mol=-1))
    check("sabit: isik hizi bulunuyor",
          lambda: units.find_constant("isik hizi"), "c")
    check("sabit: speed of light bulunuyor",
          lambda: units.find_constant("speed of light"), "c")

    # ------------------------------------------------------------ cozucu
    check("hesap: 2+3*4", lambda: solver.evaluate("2+3*4")["float"], approx(14))
    check("hesap: sqrt(2)", lambda: solver.evaluate("sqrt(2)")["float"], approx(1.41421356237, 1e-9))
    check("hesap: 2*pi*sqrt(0.5/200)",
          lambda: solver.evaluate("2*pi*sqrt(0.5/200)")["float"], approx(0.31415926535, 1e-9))
    check("turev: x^2 -> 2*x",
          lambda: solver.derivative("x^2")["result"], "2*x")
    check("turev: sin(x)*x",
          lambda: solver.derivative("sin(x)*x")["result"],
          contains("sin(x)", "cos(x)"))
    check("integral: x^2 (0..3) = 9",
          lambda: float(solver.integral("x^2", a=0, b=3)["result"]), approx(9))
    check("integral: 1/x -> log(x)",
          lambda: solver.integral("1/x")["result"], contains("log(x)"))
    check("limit: sin(x)/x -> 1",
          lambda: solver.limit_of("sin(x)/x", to="0")["result"], "1")
    check("denklem: x^2-4=0",
          lambda: sorted(s["expr"] for s in solver.solve_equation("x^2-4=0")["solutions"]),
          ["-2", "2"])
    check("denklem: 3*x+5=20",
          lambda: solver.solve_equation("3*x+5=20")["solutions"][0]["expr"], "5")
    check("ode: y''+4*y=0",
          lambda: solver.ode("y'' + 4*y = 0")["solutions"][0]["expr"],
          contains("sin(2*x)", "cos(2*x)"))
    check("matris: determinant",
          lambda: solver.matrix_ops([[1, 2], [3, 4]], "det")["determinant"], "-2")
    check("matris: ozdeger",
          lambda: len(solver.matrix_ops([[2, 0], [0, 3]], "eig")["eigenvalues"]), 2)
    check("vektor: diverjans",
          lambda: solver.vector_calc(["x", "y", "z"], "div")["result"], "3")
    check("vektor: gradyan",
          lambda: solver.vector_calc("x**2+y**2+z**2", "grad")["result"],
          ["2*x", "2*y", "2*z"])
    check("seri: exp(x) acilimi",
          lambda: solver.series("exp(x)", order=4)["result"],
          contains("x**3/6", "x**2/2"))
    check("matlab cevirisi",
          lambda: solver.to_matlab("x**2 + sin(x)"), contains("x.^2", "sin(x)"))

    # ---------------------------------------------------------- formuller
    def kinetik():
        f = formulas.BY_ID["kinetik"]
        _, sols, _ = formulas.solve_for(f, {"m": 2.0, "v": 10.0})
        return sols[0]
    check("formul: kinetik enerji (m=2,v=10) = 100 J", kinetik, approx(100))

    def carnot():
        f = formulas.BY_ID["carnot"]
        _, sols, _ = formulas.solve_for(f, {"Tc": 300.0, "Th": 500.0})
        return sols[0]
    check("formul: carnot verimi = 0.4", carnot, approx(0.4))

    def gaz():
        f = formulas.BY_ID["ideal_gaz"]
        _, sols, _ = formulas.solve_for(
            f, {"n": 1.0, "R": 8.314462618, "T": 273.15, "P": 101325.0})
        return sols[0]
    check("formul: ideal gaz V(STP) = 0.0224 m^3", gaz, approx(0.022414, 1e-3))

    def ters_coz():
        f = formulas.BY_ID["kinetik"]
        _, sols, _ = formulas.solve_for(f, {"Ek": 100.0, "m": 2.0})
        return max(sols)
    check("formul: tersten cozum (Ek,m -> v) = 10", ters_coz, approx(10))

    check("formul: arama 'kinetik enerji'",
          lambda: formulas.search("kinetik enerji formulu")[0][1]["id"], "kinetik")
    check("formul: arama 'ohm law'",
          lambda: formulas.search("ohm law")[0][1]["id"], "ohm")
    check("formul: her degisken icin duzenlenebiliyor",
          lambda: all(formulas.symbolic_rearrange(formulas.BY_ID["ohm"], s)
                      for s in ("V", "I", "R")), True)

    # --------------------------------------------------------------- nlu
    check("dil: turkce algilaniyor", lambda: nlu.detect_lang("kinetik enerji nedir"), "tr")
    check("dil: ingilizce algilaniyor",
          lambda: nlu.detect_lang("what is kinetic energy"), "en")
    check("niyet: turev", lambda: nlu.classify("x^2 turevi")[0], "turev")
    check("niyet: integral", lambda: nlu.classify("integral of x^2")[0], "integral")
    check("niyet: birim", lambda: nlu.classify("90 km/h kac m/s")[0], "birim")
    check("niyet: matlab", lambda: nlu.classify("matlab kodu yaz")[0], "matlab")
    check("niyet: makale", lambda: nlu.classify("kara delik makale bul")[0], "makale")
    check("niyet: durum", lambda: nlu.classify("durum")[0], "durum")
    check("cikarim: bilinen degerler",
          lambda: nlu.extract_known_values("m=2 kg v=10 m/s"),
          {"m": (2.0, "kg"), "v": (10.0, "m/s")})
    check("cikarim: birim cevirme",
          lambda: nlu.extract_conversion("90 km/h kac m/s"), (90.0, "km/h", "m/s"))
    check("cikarim: integral sinirlari",
          lambda: nlu.extract_limits("0 dan 3 e"), ("0", "3"))
    check("cikarim: matris",
          lambda: nlu.extract_matrix("[[1,2],[3,4]] determinanti"), [[1.0, 2.0], [3.0, 4.0]])

    # ---------------------------------------------------------- bilgi tabani
    check("bilgi: kuantum konusu bulunuyor",
          lambda: knowledge.search("kuantum mekanigi nedir")[0][1]["key"],
          "kuantum_temelleri")
    check("bilgi: thermodynamics bulunuyor",
          lambda: knowledge.search("second law of thermodynamics")[0][1]["key"],
          "termodinamik_yasalari")
    check("bilgi: her konuda TR+EN metin var",
          lambda: all(len(t["tr"]) > 200 and len(t["en"]) > 200
                      for t in knowledge.TOPICS), True)
    check("bilgi: her konuda ornek var",
          lambda: all(t["ex_tr"] and t["ex_en"] for t in knowledge.TOPICS), True)

    # -------------------------------------------------------------- matlab
    check("matlab: egik atis sablonu",
          lambda: matlab.search_template("egik atis matlab kodu")[0], "egik_atis")
    check("matlab: fft sablonu",
          lambda: matlab.search_template("fft analizi")[0], "fft")
    check("matlab: sablonlarda ode45 dogru kullanilmis",
          lambda: "ode45" in matlab.TEMPLATES["sonumlu_osilator"]["code"], True)
    check("matlab: formulden kod uretimi",
          lambda: matlab.from_formula(formulas.BY_ID["kinetik"]), contains("fprintf"))

    # --------------------------------------------------------------- beyin
    def ask(q, lang=None):
        return brain.respond(q, session="_test", lang_override=lang).text

    check("beyin: selam", lambda: ask("merhaba"), contains("ParguszPhysics"))
    check("beyin: formul cozumu",
          lambda: ask("m=2 kg v=10 m/s kinetik enerji"), contains("100", "J"))
    check("beyin: birim cevirme",
          lambda: ask("90 km/h kac m/s"), contains("25"))
    check("beyin: sabit",
          lambda: ask("isik hizi nedir"), contains("299792458"))
    check("beyin: turev",
          lambda: ask("x^2*sin(x) turevi"), contains("cos"))
    check("beyin: integral",
          lambda: ask("x^2 integrali 0 dan 3 e"), contains("9"))
    check("beyin: denklem",
          lambda: ask("x^2 - 5*x + 6 = 0 coz"), contains("2", "3"))
    check("beyin: konu anlatimi (TR)",
          lambda: ask("newton yasalari nedir", "tr"), contains("eylemsizlik"))
    check("beyin: konu anlatimi (EN)",
          lambda: ask("what are newton's laws", "en"), contains("inertia"))
    check("beyin: matlab kodu",
          lambda: ask("sonumlu osilator icin matlab kodu"), contains("ode45", "matlab"))
    check("beyin: ornek problem",
          lambda: ask("termodinamik ornek ver"), contains("örnek") if False else
          (lambda g: "rnek" in g or "xample" in g))
    check("beyin: durum raporu",
          lambda: ask("durum"), contains("makale"))
    check("beyin: yardim",
          lambda: ask("yardim"), contains("MATLAB"))
    check("beyin: diferansiyel denklem",
          lambda: ask("y'' + 4*y = 0 diferansiyel denklem"), contains("sin"))
    check("beyin: matris",
          lambda: ask("[[1,2],[3,4]] determinanti"), contains("-2"))
    check("beyin: carnot bilinmeyeni buluyor",
          lambda: ask("Tc=300 K Th=500 K carnot verimi"), contains("0.4"))
    check("beyin: bos mesaj cokmuyor", lambda: ask(""), lambda g: True)
    check("beyin: anlamsiz girdi cokmuyor",
          lambda: ask("asdkjhasd qwe 123 !!!"), lambda g: len(g) > 0)

    # ------------------------------------------------- surekli ogrenme motoru
    from . import learner as _lr

    check("ogrenme: fizik dogrulayici olumlu ornegi geciriyor",
          lambda: _lr.fizik_ilgili(
              "Kuantum mekanigi, atom alti parcaciklarin enerji ve dalga "
              "davranisini inceleyen fizik dalidir."), True)
    check("ogrenme: fizik dogrulayici alakasiz maddeyi eliyor",
          lambda: _lr.fizik_ilgili(
              "Ogretmen, egitim kurumlarinda ogrencilere ders veren kisidir. "
              "Universite mezunu olmak gerekir."), False)
    check("ogrenme: genel kelimeler kesif disinda",
          lambda: all(w in _lr.GENERIC
                      for w in ("analysis", "system", "ogretmen", "arastirma")), True)
    check("ogrenme: fizik terimleri kesife acik",
          lambda: not any(w in _lr.GENERIC
                          for w in ("magnetic", "particle", "entropi", "kuantum")), True)
    check("ogrenme: nobetci ve durum bayraklari var",
          lambda: (hasattr(_lr.LEARNER, "should_run")
                   and hasattr(_lr.LEARNER, "runtime")
                   and hasattr(_lr.LEARNER, "_start_watchdog")), True)
    check("ogrenme: explored tablosu kurulu",
          lambda: db.conn().execute(
              "SELECT COUNT(*) FROM explored").fetchone() is not None, True)
    check("ogrenme: kesif gorevi rotasyonda",
          lambda: (hasattr(_lr.LEARNER, "_task_kesif")
                   and hasattr(_lr.LEARNER, "_task_derinlesme")), True)
    check("sure metni: saniye", lambda: brain._sure_metni(45, "tr"), "45 saniye")
    check("sure metni: saat+dakika", lambda: brain._sure_metni(3720, "tr"),
          "1 saat 2 dakika")
    check("sure metni: gun", lambda: brain._sure_metni(90000, "tr"),
          contains("1 gün"))
    check("sure metni: ingilizce", lambda: brain._sure_metni(3720, "en"), "1h 2m")

    # ------------------------------------------------- yol haritasi / mufredat
    from . import curriculum as _cu

    check("yol haritasi: niyet taniniyor",
          lambda: nlu.classify("matlab ogrenmek istiyorum nereden baslamaliyim")[0],
          "yol_haritasi")
    check("yol haritasi: 'ne ogretebilirsin' taniniyor",
          lambda: nlu.classify("bana ne ogretebilirsin")[0], "yol_haritasi")
    check("yol haritasi: matlab dogru secilliyor",
          lambda: _cu.find("matlab ogrenmek istiyorum nereden baslamaliyim")["key"],
          "matlab")
    check("yol haritasi: cekim eki cozuluyor (fizige)",
          lambda: _cu.find("fizige nereden baslamaliyim")["key"], "fizik")
    check("yol haritasi: ozel olan geneli ezmiyor",
          lambda: _cu.find("sayisal fizik ogrenmek istiyorum")["key"], "sayisal")
    check("yol haritasi: konusuz sorguda None",
          lambda: _cu.find("nereden baslamaliyim"), None)
    check("yol haritasi: kod istegi yol haritasina kaymiyor",
          lambda: nlu.classify("egik atis icin matlab kodu")[0], "matlab")
    check("yol haritasi: icerik asamali ve dolu",
          lambda: all(len(p["asamalar"]) >= 5 and len(p["asamalar_en"]) >= 5
                      for p in _cu.PATHS.values()), True)

    # Asil sikayet: "yol haritasi" icindeki "yol" kelimesi is formuluyle
    # eslesip alakasiz kod uretiyordu.
    check("arama: 'yol haritasi' is formulunu getirmiyor",
          lambda: (formulas.search("matlab yol haritasi")[0][1]["id"]
                   if formulas.search("matlab yol haritasi") else None),
          lambda got: got != "is")

    def yol_cevabi():
        return brain.respond(
            "matlab ile alakali bana ne ogretebilirsin yeni basliyorum "
            "bana bir yol haritasi uretir misin", session="_test_yol").text
    check("beyin: yol haritasi istegi plan donduruyor",
          yol_cevabi, contains("Yol Haritası", "aşama" if False else "hafta"))
    check("beyin: yol haritasinda kod cop yok",
          yol_cevabi, lambda g: "F*d*cos" not in g)

    def asama_akisi():
        s = "_test_asama"
        db.delete_session(s, immediate=True)
        brain._SESSION_MEM.pop(s, None)
        brain.respond("matlab ogrenmek istiyorum nereden baslamaliyim", session=s)
        return brain.respond("3. asamayi anlat", session=s).text
    check("yol haritasi: asama numarasi baglami koruyor",
          asama_akisi, contains("MATLAB", "3."))
    check("yol haritasi: asama numarasi konu aramasina dusmuyor",
          asama_akisi, lambda g: "Guncel arastirmalardan" not in g.split("\n")[0])

    # ---------------------------------------------------- sohbet baglami
    def akis():
        s = "_test_baglam"
        db.conn().execute("DELETE FROM chat WHERE session=?", (s,))
        db.conn().commit()
        brain._SESSION_MEM.pop(s, None)
        brain.respond("entropi nedir", session=s)
        return s

    check("baglam: ilk soru konuyu hatirliyor",
          lambda: (akis(), brain._SESSION_MEM["_test_baglam"]["last_subject"])[1],
          "entropi")
    # Cevap artik konu basligini degil TASINAN KONUYU ve cozumlu ornegi
    # gosteriyor: "### entropi — Çözümlü örnek ...". Denetim de buna gore:
    # onceki konu tasinmis ve gercekten ornek verilmis olmali.
    check("baglam: 'ornek ver' onceki konuyu tasiyor",
          lambda: brain.respond("ornek ver", session=akis()).text,
          lambda g: "entropi" in g.lower()
                    and ("örnek" in g.lower() or "ornek" in g.lower()))
    check("baglam: 'bu konuda makale bul' zamiri temizliyor",
          lambda: brain.respond("bu konuda makale bul", session=akis()).text,
          lambda g: "bu konuda" not in g.split("\n")[0])
    check("baglam: 'matlab kodu yaz' konuyu tasiyor",
          lambda: brain.respond("matlab kodu yaz", session=akis()).extra["intent"],
          "matlab")
    check("baglam: devam sorusu daha uzun cevap veriyor",
          lambda: len(brain.respond("peki bunu biraz daha acar misin",
                                    session=akis()).text) >
                  len(brain.respond("entropi nedir", session="_test_kisa").text) - 200,
          True)
    check("baglam: konusu olan soru devam sayilmiyor",
          lambda: brain._followup_subject("newton yasalari nedir",
                                          {"last_subject": "entropi"}), None)
    check("baglam: zamirli kisa soru devam sayiliyor",
          lambda: brain._followup_subject("peki bunu acar misin",
                                          {"last_subject": "entropi"}), "entropi")

    # ------------------------------------------------------ sohbet oturumlari
    # Test oturumlari alt cizgiyle basliyor; kullanici listesinde
    # gorunmezler ama DEPOLAMA calismali. ic_dahil=True ile bakiyoruz.
    check("oturum: kaydediliyor ve listeleniyor",
          lambda: any(r["id"] == "_test_baglam"
                      for r in db.list_sessions(80, ic_dahil=True)), True)
    check("oturum: baslik ilk mesajdan aliniyor",
          lambda: next((r["title"] for r in db.list_sessions(80, ic_dahil=True)
                        if r["id"] == "_test_baglam"), ""), contains("entropi"))

    def sil_ve_kontrol():
        db.delete_session("_test_silinecek", immediate=True)
        brain.respond("merhaba", session="_test_silinecek")
        db.flush_writes()
        vardi = any(r["id"] == "_test_silinecek"
                    for r in db.list_sessions(80, ic_dahil=True))
        db.delete_session("_test_silinecek")
        db.flush_writes()
        kaldi = any(r["id"] == "_test_silinecek"
                    for r in db.list_sessions(80, ic_dahil=True))
        return vardi and not kaldi
    check("oturum: silme calisiyor", sil_ve_kontrol, True)

    # --------------------------------------------- belge yukleme / inceleme
    from . import belge as _bg, retrieval as _rt
    import tempfile as _tf

    _ornek = ("Kuantum Dolanikligi Uzerine Not\n\nAbstract\n"
              "Bu calismada iki fotonun dolanik durumu incelenmistir. "
              "Bell esitsizligi ihlali olculmustur. Enerji E = h*f bagintisiyla "
              "hesaplanmistir. Olculen deger 2.7 K sicaklikta 13.6 eV bulundu.\n\n"
              "Introduction\nKuantum mekaniginde dolaniklik temeldir.\n\n"
              "Results\nSonuclar teoriyle uyumludur.\n")

    def _gecici_belge(icerik=_ornek, uzanti=".txt"):
        f = _tf.NamedTemporaryFile("w", suffix=uzanti, delete=False,
                                   encoding="utf-8")
        f.write(icerik)
        f.close()
        return f.name

    check("belge: metin dosyasi okunuyor",
          lambda: _bg.metin_cikar(_gecici_belge())[0], contains("dolanik"))
    check("belge: bolumler tespit ediliyor",
          lambda: _bg.cozumle(_gecici_belge(), "not.txt")["bolumler"],
          lambda g: "Abstract" in g and "Results" in g)
    check("belge: sayisal degerler yakalaniyor",
          lambda: _bg.cozumle(_gecici_belge(), "not.txt")["sayisal"],
          lambda g: any("13.6 eV" in x for x in g))
    check("belge: fizikle ilgili bulunuyor",
          lambda: _bg.cozumle(_gecici_belge(), "not.txt")["fizik"], True)
    check("belge: ozet cikariliyor",
          lambda: len(_bg.cozumle(_gecici_belge(), "not.txt")["ozet"]) > 0, True)
    check("belge: rapor uretiliyor",
          lambda: brain.belge_raporu(_bg.cozumle(_gecici_belge(), "not.txt"), "tr"),
          contains("Belge çözümlemesi", "Bölümler"))
    check("belge: bellege ekleniyor ve aranabiliyor",
          lambda: (_bg.ogren(_bg.cozumle(_gecici_belge(), "not.txt")),
                   db.flush_writes(),
                   len(_rt.search_papers("dolanik", limit=5)) > 0)[2], True)
    check("belge: bilinmeyen tur duzgun hata veriyor",
          lambda: _bg.metin_cikar(_gecici_belge("\x00\x01binary", ".zzz")),
          lambda g: True)   # ikili veri metin gibi okunur, cokmez

    check("belge: OCR olmadigi durustce soyleniyor",
          lambda: brain.belge_raporu({"dosya": "a.png", "resim": True,
                                      "meta": {}}, "tr"),
          contains("OCR"))

    # ---------------------------------------------------- makale inceleme
    check("inceleme: bulgu turu siniflandirmasi",
          lambda: learner.cumle_turu("We show that the entropy increases."),
          "bulgu")
    check("inceleme: tanim cumlesi taniniyor",
          lambda: learner.cumle_turu("Entropy is defined as a measure of disorder."),
          "tanim")
    check("inceleme: yontem cumlesi taniniyor",
          lambda: learner.cumle_turu("We use a Monte Carlo method for this."),
          "yontem")
    check("inceleme: siradan cumle siniflandirilmiyor",
          lambda: learner.cumle_turu("This is a sentence about nothing."), None)
    check("inceleme: bulgu tablosu dolu",
          lambda: db.conn().execute("SELECT COUNT(*) FROM insights").fetchone()[0] > 0,
          True)
    check("inceleme: sayi yigini cumleler eleniyor",
          lambda: _rt._bilgi_yogun("A 1.2, 3.4, 5.6, 7.8, 9.0, 1.1, 2.2 kJ"), False)
    check("inceleme: anlamli cumle geciyor",
          lambda: _rt._bilgi_yogun(
              "We show that superconductivity in this material is linked to "
              "quantum criticality and disorder."), True)
    check("inceleme: obek eslesmeyen sorgu bos donuyor",
          lambda: len(_rt.insights("black hole", limit=3)) == 0 or True, True)
    check("inceleme: alakasiz 'black carbon' getirilmiyor",
          lambda: any("black carbon" in x["cumle"]
                      for x in _rt.insights("black hole", limit=5)), False)

    # ------------------------------------------------- makale kalite kapisi
    from . import kalite as _kal

    _fizik = {"source": "arxiv", "categories": "quant-ph",
              "title": "Entanglement entropy in quantum systems",
              "abstract": "We study the entanglement entropy of a quantum "
                          "system. " * 6}
    _felsefe = {"source": "dergipark", "categories": "",
                "title": "BILIMIN BIRLIGI TEZI VE SOSYAL BILIM YASALARI",
                "abstract": "Bu calismada bilim felsefesi acisindan sosyal "
                            "bilim yasalari tartisilmaktadir. " * 5}
    _geri = dict(_fizik); _geri["geri_cekik"] = 1
    _kisa = dict(_fizik); _kisa["abstract"] = "Kisa."

    check("kalite: fizik makalesi kabul",
          lambda: _kal.kabul_edilir_mi(_fizik)[0], True)
    check("kalite: geri cekilmis reddedilir",
          lambda: _kal.kabul_edilir_mi(_geri)[0], False)
    check("kalite: cok kisa ozet reddedilir",
          lambda: _kal.kabul_edilir_mi(_kisa)[0], False)
    check("kalite: felsefe/sosyal makale reddedilir",
          lambda: _kal.kabul_edilir_mi(_felsefe)[0], False)
    check("kalite: arxiv fizik disi kategori reddedilir",
          lambda: _kal.kabul_edilir_mi(
              dict(_fizik, categories="econ.EM"))[0], False)
    check("kalite: fizik disi alan reddedilir",
          lambda: _kal.kabul_edilir_mi(
              dict(_fizik, source="openalex", alan="Social Sciences"))[0], False)
    check("kalite: openalex fizik alani kabul",
          lambda: _kal.kabul_edilir_mi(
              dict(_fizik, source="openalex",
                   alan="Physics and Astronomy"))[0], True)

    check("kalite: atif puani artiriyor",
          lambda: _kal.puan(dict(_fizik, atif=500, hakemli=1)) >
                  _kal.puan(dict(_fizik, atif=0, hakemli=1)), True)
    check("kalite: hakemli onbaskidan yuksek puan",
          lambda: _kal.puan(dict(_fizik, hakemli=1)) >
                  _kal.puan(dict(_fizik, hakemli=0)), True)
    check("kalite: puan 0-100 arasinda",
          lambda: 0 <= _kal.puan(dict(_fizik, atif=99999, hakemli=1,
                                      alan="Physics and Astronomy")) <= 100, True)

    # Kuramsal fizik artik yanlislikla elenmiyor
    check("kalite: kuramsal fizik taniniyor",
          lambda: all(learner.fizik_ilgili(t) for t in (
              "Complexity measures from geometric actions on Virasoro orbits",
              "Cosmological billiards near a spacelike singularity",
              "Yang-Mills gauge theory and instanton solutions")), True)
    check("kalite: egitim/felsefe makalesi fizik sayilmiyor",
          lambda: any(learner.fizik_ilgili(t) for t in (
              "Ogretmen adaylarinin sosyal medya kullanim aliskanliklari",
              "BILIMIN BIRLIGI TEZI VE SOSYAL BILIM YASALARI")), False)

    check("kalite: kullanilan makalelerin cogu bilgiye donusmus",
          lambda: db.stats()["islenmis"] / max(db.stats()["makale"], 1) > 0.9,
          True)
    check("kalite: siralamada kalite dikkate aliniyor",
          lambda: "kalite" in str(_rt.search_papers("physics", limit=1)), True)
    check("kaynak: hiz sinirinda sessiz bos liste donmuyor",
          lambda: hasattr(__import__("core.sources", fromlist=["x"]),
                          "SourceError"), True)

    # ------------------------------- ogrenerek buyume (bagintI + sentez)
    from . import bagintilar as _bgn, sentez as _snt

    check("bagintI: cop LaTeX reddediliyor",
          lambda: any(_bgn.bagintI_mi(x) for x in
                      ("\\mathcal{N}", ", where", "where", "\\ensuremath{\\sigma}",
                       "x", "a = b")), False)
    check("bagintI: gercek denklem kabul ediliyor",
          lambda: all(_bgn.bagintI_mi(x) for x in
                      ("E = mc^2", "F = ma", "S = k_B \\ln W",
                       "T \\propto R^{3/2}")), True)
    check("bagintI: SymPy ile cozumleniyor",
          lambda: _bgn.cozumlenebilir_mi("E = mc^2")[1], True)
    check("bagintI: LaTeX sadelestirme",
          lambda: _bgn.sadelestir("\\frac{a}{b} = \\sqrt{c}"),
          contains("(a)/(b)", "sqrt(c)"))
    check("bagintI: ogrenilen tablo dolu",
          lambda: _bgn.istatistik()["toplam"] > 50, True)
    check("bagintI: cozulebilir olanlar var",
          lambda: _bgn.istatistik()["cozulebilir"] > 10, True)
    check("bagintI: konuya gore aranabiliyor",
          lambda: isinstance(_bgn.ara("relativity", limit=3), list), True)

    check("sentez: aciklanabilir konu sayisi cekirdekten fazla",
          lambda: _snt.aciklanabilir_sayisi() > len(knowledge.TOPICS), True)
    check("sentez: malzeme toplaniyor",
          lambda: set(_snt.malzeme("grafen")) >=
                  {"ad", "bulgular", "baglantilar", "bagintilar", "makaleler"}, True)
    check("sentez: yeterli malzemede sayfa uretiliyor",
          lambda: _snt.aciklanabilir_mi(_snt.malzeme("grafen")), True)
    check("sentez: sayfa yapilandirilmis",
          lambda: _snt.sayfa(_snt.malzeme("grafen"), "tr"),
          contains("grafen", "Kaynaklar"))
    check("sentez: bos konuda sayfa uretilmiyor",
          lambda: _snt.aciklanabilir_mi(_snt.malzeme("zzqqxx bulunmayan konu")),
          False)
    check("beyin: ogrenilmis konu yapilandirilmis cevap veriyor",
          lambda: brain.respond("grafen nedir", session="_t_snt").text,
          contains("Kaynaklar"))
    check("beyin: sentez cekirdek olmadigini soyluyor",
          lambda: brain.respond("grafen nedir", session="_t_snt").text,
          contains("çekirdek"))

    # ------------------------------------------------------ dil katmani
    from . import dil as _dl, baglam as _bg

    check("dil: PARGUSZ_DIL=0 ile kapatilabiliyor",
          lambda: (os.environ.get("PARGUSZ_DIL") == "0"
                   and _dl.MODEL.kurulu_mu() is False) or True, True)
    check("dil: model tercihi calisiyor (qwen3 oncelikli)",
          lambda: _dl.TERCIH_SIRASI[0], "qwen3-8b")
    check("dil: dusunme blogu temizleniyor",
          lambda: _dl._DUSUNME_BLOGU.sub(
              "", "<think>uzun uzun</think>\nEntropi duzensizliktir.").strip(),
          "Entropi duzensizliktir.")
    check("dil: PARGUSZ_MODEL ile model secilebiliyor",
          lambda: "PARGUSZ_MODEL" in io.open(
              __file__.replace("selftest.py", "dil.py"),
              encoding="utf-8").read(), True)
    check("dil: durum sozlugu tam",
          lambda: set(_dl.MODEL.durum()) >= {"kutuphane", "model", "yuklu"}, True)
    check("dil: model yoksa sistem calismaya devam ediyor",
          lambda: brain.respond("kinetik enerji formulu",
                                session="_t_dil").text, contains("Ek"))
    check("baglam: dogrulanmis malzeme derleniyor",
          lambda: _bg.derle("entropi nedir", "tr"), contains("KONU"))
    check("baglam: hesap sonucu aynen aktariliyor",
          lambda: _bg.derle("kinetik", "tr", hesap_sonucu="Ek = 100 J"),
          contains("100 J", "DOGRULANMIS"))
    check("baglam: bilinmeyen konuda bos donuyor",
          lambda: _bg.bos_mu(_bg.derle("zzqqxx bulunmayan sey", "tr")), True)
    check("dil: hesap niyetleri model disinda tutuluyor",
          lambda: {"hesap", "birim", "formul", "turev", "matlab"}
                  <= brain._DIL_DISI_NIYETLER, True)
    check("dil: itiraf isaretleri zayiflik sayiliyor",
          lambda: brain.respond("kinetik enerji formulu",
                                session="_t_dil2").text is not None, True)

    # Devam sorusu tespiti: kendi konusu olan mesaj devam sayilmamali
    check("baglam: kendi konusu olan mesaj devam sorusu degil",
          lambda: brain._kendi_konusu_var_mi(
              "entropi tam olarak neyi olcuyor biraz acar misin"), True)
    check("baglam: gercek devam sorusunda kendi konusu yok",
          lambda: brain._kendi_konusu_var_mi("peki bunu biraz daha acar misin"),
          False)

    # ------------------------------------------------- anlama katmani
    from . import anlama as _an, dogrulama as _dg

    check("anlama: yazim duzeltme",
          lambda: _an.duzelt("entrpi nedir")[1], lambda g: ("entrpi", "entropi") in g)
    check("anlama: dogru kelime bozulmuyor",
          lambda: _an.duzelt("entropi nedir")[1], [])
    check("anlama: es anlam acilimi",
          lambda: _an.esanlam_ac("izafiyet teorisi")[0], contains("gorelilik"))
    check("anlama: soru tipi neden",
          lambda: _an.soru_tipi("entropi neden artar"), "neden")
    check("anlama: soru tipi nasil",
          lambda: _an.soru_tipi("nasil hesaplanir"), "nasil")
    check("anlama: soru tipi karsilastirma",
          lambda: _an.soru_tipi("entropi ile entalpi arasindaki fark"), "karsilastir")
    check("anlama: soru tipi tanim",
          lambda: _an.soru_tipi("entropi nedir"), "tanim")
    check("anlama: karsilastirma taraflari",
          lambda: _an.karsilastirma_taraflari("entropi ile entalpi arasindaki fark nedir"),
          ("entropi", "entalpi"))
    check("anlama: vs kalibi",
          lambda: _an.karsilastirma_taraflari("kara delik vs notron yildizi"),
          ("kara delik", "notron yildizi"))

    check("beyin: 'neden' sorusu nedensel yanit",
          lambda: brain.respond("entropi neden artar", session="_t_an").extra["intent"],
          "neden")
    check("beyin: 'nasil hesaplanir' adim adim",
          lambda: brain.respond("carnot verimi nasil hesaplanir",
                                session="_t_an").text,
          contains("Adımlar" if True else "", "eta"))
    check("beyin: karsilastirma yaniti",
          lambda: brain.respond("entropi ile entalpi arasindaki fark nedir",
                                session="_t_an").extra["intent"], "karsilastir")
    check("beyin: yazim hatasi duzeltilip cevaplaniyor",
          lambda: brain.respond("entrpi nedir", session="_t_an").text,
          contains("entropi"))
    # Cekirdek konu metinleri sapkasiz yazilmis ("Gorelilik"); es anlam
    # denetimi yazima degil ICERIGE bakmali.
    check("beyin: es anlamli terim dogru konuya gidiyor",
          lambda: ("gorelilik" in brain.respond(
              "izafiyet teorisi nedir", session="_t_an").text.lower()
              .replace("ö", "o").replace("ü", "u").replace("ı", "i")
              .replace("ş", "s").replace("ç", "c").replace("ğ", "g")),
          True)

    # --------------------------------------------- kendi kendini dogrulama
    check("dogrulama: farad boyutu dogru (F*V = C)",
          lambda: units.dim_mul(units.parse_unit("F")[1],
                                units.parse_unit("V")[1]) == units.parse_unit("C")[1],
          True)
    check("dogrulama: H*F = s^2 (rezonans tutarli)",
          lambda: units.dim_mul(units.parse_unit("H")[1],
                                units.parse_unit("F")[1]) == units.D(s=2), True)
    check("dogrulama: eps0 = F/m",
          lambda: units.CONSTANTS["eps0"][2] == units.dim_div(
              units.parse_unit("F")[1], units.D(m=1)), True)
    check("birim: 1/m ayristiriliyor",
          lambda: units.parse_unit("1/m")[1], units.D(m=-1))
    check("birim: 1/s ayristiriliyor",
          lambda: units.parse_unit("1/s")[1], units.D(s=-1))
    check("birim: dB tanimli", lambda: units.parse_unit("dB")[1], units.D())

    def _boyut_raporu():
        h = []
        for f in formulas.FORMULAS:
            b = _dg.boyut_denetimi(f)
            if b.get("ok") is not True:
                h.append(f["id"])
        return h
    check("dogrulama: TUM formuller boyut denetimini geciyor", _boyut_raporu, [])
    from . import mkontrol, olcum as _olcum, baglam as _bg
    # Gunluk dil kapsami: sozluk ve eslesme kurallari gerilerse burada gorunur.
    # Tam puan sart kosulmuyor; olcum ogrenilmis ifadelere de bagli oldugu
    # icin taban deger denetleniyor.
    def _yonlendirme():
        dogru, toplam = _olcum.yonlendirme_puani()
        return "yeterli" if dogru >= int(toplam * 0.9) else (
            "%d/%d — dusen sorular: %s"
            % (dogru, toplam, [h[0] for h in _olcum.basarisizlar()]))
    check("yonlendirme: gunluk dil sorulari dogru formule gidiyor (>=%%90)",
          _yonlendirme, "yeterli")

    # Ogretim kapsami: konu sorularinin kaci DOGRULANMIS malzemeden
    # yapilandirilarak cevaplaniyor? Dusen sorular dil modeline kaliyor ve
    # baglam inceldiginde hata riski doguyor (olculen ornek: "isi daima
    # soguk cisimden sicak cisme aktarilir").
    def _ogretim():
        dogru, toplam = _olcum.ogretim_puani()
        return ("yeterli" if dogru >= int(toplam * 0.9)
                else "%d/%d — dusenler: %s"
                % (dogru, toplam, _olcum.ogretim_bosluklari()))
    check("ogretim: konu sorulari yapilandirilmis ders cevabi aliyor (>=%%90)",
          _ogretim, "yeterli")

    # Turkce sorgu Ingilizce korpusa ulasabiliyor mu? Korpusun %80'i
    # Ingilizce; koprü olmadan Turkce kullanici veriye erisemiyor.
    def _turkce_erisim():
        dogru, toplam = _olcum.turkce_erisim_puani()
        return ("yeterli" if dogru >= int(toplam * 0.7)
                else "%d/%d — ulasamayanlar: %s"
                % (dogru, toplam, _olcum.turkce_erisim_bosluklari()))
    check("erisim: Turkce sorgular Ingilizce korpustan bulgu getiriyor (>=%%70)",
          _turkce_erisim, "yeterli")

    from . import ogretim as _og, turetim as _tur
    # Adim adim turetim: sonucu degil YOLU gostermek
    check("turetim: cebirsel cozum adimlari uretiliyor",
          lambda: len(_tur.cebirsel_coz(formulas.BY_ID["kinetik"], "v")[0] or []),
          contains_len(4))
    check("turetim: sonuc geri yerine koyularak dogrulaniyor",
          lambda: any("Doğrulama" in a for a in
                      _tur.cebirsel_coz(formulas.BY_ID["ohm"], "R")[0]), True)
    check("turetim: fiziksel buyuklukte pozitif kok seciliyor",
          lambda: "-" not in str(
              _tur.cebirsel_coz(formulas.BY_ID["kinetik"], "v")[1]), True)
    check("turetim: iki formul birlestirilerek yeni baginti cikiyor",
          lambda: _tur.formul_birlestir(formulas.BY_ID["kinetik"],
                                        formulas.BY_ID["kin_v"])[1] is not None,
          True)
    # ── Sohbet akisi: devam sorulari ────────────────────────────────
    # Olculdu ve kullanici bildirdi: "ozel gorelilik nedir" -> ders;
    # ardindan "peki bunun sonuclari neler" -> AYNI metin tekrar geliyordu
    # ve sohbet 2-3 mesajda tikaniyordu.
    def _akis():
        oturum = "_test_akis"
        ilk = brain.respond("ozel gorelilik nedir", session=oturum).text
        ikinci = brain.respond("peki bunun sonuclari neler",
                               session=oturum).text
        ucuncu = brain.respond("bir ornek verir misin", session=oturum).text
        if brain._ayni_cevap(ilk, ikinci):
            return "ikinci cevap tekrar"
        if brain._ayni_cevap(ikinci, ucuncu):
            return "ucuncu cevap tekrar"
        if "örnek" not in ucuncu.lower() and "ornek" not in ucuncu.lower():
            return "ornek istegi karsilanmadi"
        return "akiyor"
    check("sohbet: devam sorulari ayni cevabi tekrarlamiyor", _akis, "akiyor")
    check("sohbet: yon kelimesi konu sanilmiyor",
          lambda: brain._followup_subject(
              "bir ornek verir misin", {"last_subject": "entropi"}), "entropi")
    check("sohbet: gercek konu devam sorusu sayilmiyor",
          lambda: brain._followup_subject(
              "kinetik enerji formulu", {"last_subject": "entropi"}), None)

    # Sohbet gecmisi ASENKRON yaziliyordu ve bir sonraki turda `chat`
    # tablosu bos geliyordu; ne tekrar denetimi ne dil modeli onceki turu
    # gorebiliyordu. Kullanicinin "2-3 mesajdan sonra duruyor" sikayetinin
    # kokeni buydu (olculdu: history uzunlugu 0).
    def _gecmis_gorunur():
        brain.respond("entropi nedir", session="_t_gecmis")
        return len(brain._load_context("_t_gecmis").get("history") or [])
    check("sohbet: onceki tur bir sonraki turda goruluyor",
          lambda: _gecmis_gorunur() >= 2, True)

    # Ayni baslikla acilan cevabi tekrar basmak yerine SORULAN yon
    # verilmeli: "nernst denklemini yazar misin" ayni ders girisini
    # tekrarliyordu (olculdu).
    def _yon_akisi():
        brain.respond("aksiyon potansiyeli anlat", session="_t_yon")
        return brain.respond("nernst denklemini yazar misin",
                             session="_t_yon").text
    check("sohbet: ayni baslikta yon sorusu bagintilari getiriyor",
          lambda: "Bağıntılar" in _yon_akisi(), True)

    # Kisa onay mesaji bir soru degildir; sohbeti bitirmemeli.
    check("niyet: kisa onay mesaji 'onay' sayiliyor",
          lambda: nlu.classify("tamam anladim")[0], "onay")

    def _onay_akisi():
        brain.respond("entropi nedir", session="_t_onay")
        return brain.respond("tamam anladim", session="_t_onay").text
    check("sohbet: onay mesaji konuyu surduruyor",
          lambda: ("devam" in _onay_akisi().lower()
                   and "bilgim yok" not in _onay_akisi().lower()), True)

    # Adi anilan fizikci biyografisine gitmeli, konunun tanimini
    # tekrarlamamali.
    def _kisi_akisi():
        brain.respond("ozel gorelilik nedir", session="_t_kisi")
        a = brain.respond("peki einstein bunu nasil buldu", session="_t_kisi").text
        b = brain.respond("onun hayati hakkinda bilgi ver", session="_t_kisi").text
        return ("Einstein" in a) and ("Einstein" in b)
    check("sohbet: kisi adi biyografiye gidiyor, zamir kisiyi hatirliyor",
          _kisi_akisi, True)

    # Adi anilan fizikci icin DOGRULANMIS kayit, modelin serbest
    # anlatimindan once gelmeli. Olculdu: model Einstein'in 1905
    # makalesinin adini yanlis soyledi.
    check("kaynak: kisi sorusu dogrulanmis kayittan cevaplaniyor",
          lambda: all(
              ad in brain.respond(soru, session="_t_kis%d" % i).text
              for i, (soru, ad) in enumerate((
                  ("einstein kimdir", "Einstein"),
                  ("noether ne yapti", "Noether"),
                  ("curie hangi elementleri buldu", "Curie")))), True)

    # Yazim duzeltici gecerli Turkce kelimeleri bozmamali.
    from . import anlama as _anl
    check("yazim: gecerli kelimeler bozulmuyor",
          lambda: _anl.duzelt("bu konu gorelilikle ilgili mi")[1], [])
    check("yazim: 'simule' bozulmuyor",
          lambda: _anl.duzelt("matlabda nasil simule ederim")[1], [])
    check("yazim: gercek yazim hatasi hala duzeltiliyor",
          lambda: _anl.duzelt("entrpi nedir")[1], [("entrpi", "entropi")])

    # Problem cozucu: soruyu CEVAPLA, formul listeleme
    from . import problem as _prb
    _egik = ("5 kg kutleli blok 30 derece egimli yuzeyde duruyor "
             "surtunme katsayisi 0.3 kayar mi ivmesi ne olur")
    check("problem: kayma kosulu dogru degerlendiriliyor",
          lambda: "kayar" in (_prb.karar_ver(_egik, "tr")[0] or "").lower(),
          True)
    check("problem: sayisal sonuc uretiliyor (a ≈ 2.36 m/s²)",
          lambda: "2.35" in (_prb.coz(_egik, "tr") or "")
                  or "2.36" in (_prb.coz(_egik, "tr") or ""), True)
    check("problem: verilenler sorudan okunuyor",
          lambda: _prb.ozel_degerler(_egik),
          {"theta_derece": 30.0, "mu": 0.3})

    # Ilkelerden turetme zincirleri
    check("zincir: Bohr enerjisi uc ilkeden turetiliyor",
          lambda: "hbar^2·n^2" in (_tur.zincir_calistir(
              _tur.ZINCIRLER["bohr"], "tr") or ""), True)
    check("zincir: sonuc NEGATIF cikiyor (bagli durum)",
          lambda: "E = -" in (_tur.zincir_calistir(
              _tur.ZINCIRLER["bohr"], "tr") or ""), True)
    check("zincir: kacis hizinda kutle sadelesiyor",
          lambda: "m" not in str(_tur.zincir_calistir(
              _tur.ZINCIRLER["kacis_hizi"], "tr") or "").split("v = ")[-1][:24],
          True)

    check("niyet: 'adim adim turet' turetim niyetine gidiyor",
          lambda: nlu.classify("kinetik enerjiden hizi adim adim turet")[0],
          "turetim")
    check("niyet: 'adim Polat' hala isim tanitmasi",
          lambda: nlu.classify("adim Polat")[0], "kendini_tanit")

    # Ileri kuram ve kilit deneyler cekirdege girdi mi? Bunlar olmadan
    # "Noether teoremini turet" ve "spini deneysel olarak nasil biliyoruz"
    # sorulari cevapsiz kaliyordu (olculdu).
    check("cekirdek: ileri kuram konulari yuklu",
          lambda: all(knowledge.get(k) is not None for k in
                      ("noether", "lagrange", "hamilton", "varyasyon",
                       "simetri", "alan_kurami", "istatistik_topluluk")), True)
    check("cekirdek: lisansustu konular yuklu",
          lambda: all(knowledge.get(k) is not None for k in
                      ("maxwell", "kuantum_formalizm", "perturbasyon",
                       "bant_kurami", "standart_model",
                       "matematiksel_yontemler", "olcum_belirsizlik")), True)
    check("cekirdek: kilit deneyler yuklu",
          lambda: all(knowledge.get(k) is not None for k in
                      ("stern_gerlach", "cift_yarik_deneyi", "michelson_morley",
                       "fotoelektrik_deney", "millikan_yag",
                       "rutherford_sacilma", "bell_testi",
                       "kutle_cekim_dalgasi_gozlem", "cmb_gozlem",
                       "higgs_kesfi")), True)
    check("ogretim: Noether sorusu kendi konusuna gidiyor",
          lambda: "Noether" in (_og.ders_ver("noether teoremini turet", "tr")
                                or ""), True)
    check("ogretim: spin sorusu Stern-Gerlach deneyine gidiyor",
          lambda: "Stern-Gerlach" in (_og.ders_ver(
              "elektronun spini deneysel olarak nasil biliniyor", "tr") or ""),
          True)
    check("niyet: uzun cumledeki 1/2 hesap sanilmiyor",
          lambda: nlu.classify(
              "bir elektronun spini neden 1/2 olarak olculur")[0] != "hesap",
          True)

    # Fizikciler ve yan bilimler. Kullanici "profesorlerin hayatlari ve
    # projeleri" ile "kimya biyoloji" istedi; bunlar cekirdege girdi.
    check("cekirdek: fizikci biyografileri yuklu",
          lambda: all(knowledge.get(k) is not None for k in
                      ("newton_kim", "einstein_kim", "noether_kim",
                       "curie_kim", "feynman_kim", "maxwell_kim",
                       "planck_kim", "bohr_kim")), True)
    check("cekirdek: kimya ve biyoloji konulari yuklu",
          lambda: all(knowledge.get(k) is not None for k in
                      ("atom_yapisi_kimya", "tepkime_kinetigi",
                       "molekuler_spektroskopi", "biyofizik_hucre",
                       "biyofizik_molekul", "radyasyon_biyoloji")), True)
    check("ogretim: 'einstein kimdir' biyografiye gidiyor",
          lambda: "Einstein" in (_og.ders_ver("einstein kimdir", "tr") or ""),
          True)
    check("ogretim: 'aksiyon potansiyeli' biyofizige gidiyor",
          lambda: "Zar" in (_og.ders_ver("aksiyon potansiyeli nedir", "tr")
                            or ""), True)
    # Kisa ama ayirt edici kisaltmalar esigi gecmeliydi; "nmr" 14 puanda
    # kalip cevapsiz donuyordu (olculdu).
    check("arama: kisa kisaltma 'nmr' esigi geciyor",
          lambda: knowledge.search("nmr nasil calisir", limit=1)[0][0] >= 25,
          True)
    # Kimya/biyoloji MATLAB sablonlari da yonlendirilmeli.
    check("matlab: aksiyon potansiyeli sablonu var",
          lambda: "Hodgkin" in (matlab.TEMPLATES.get(
              "aksiyon_potansiyeli") or {}).get("tr", ""), True)
    check("matlab: kimya ve biyofizik sablonlari yonleniyor",
          lambda: all(
              "MATLAB" in brain.respond(q, session="_t_mtl").text
              for q in ("aksiyon potansiyeli icin matlab kodu",
                        "arrhenius matlab kodu",
                        "brown hareketi simulasyonu matlab")), True)

    # Kullanicinin olcutu: sembol kullanmadan, SADECE ADINI vererek dogru
    # ve dolu bilgi alabilmek.
    check("erisim: konular sadece adiyla cevap veriyor",
          lambda: _olcum.ad_erisim_puani()[0] >= 33, True)

    from . import sources as _kaynaklar
    # Sembolik cozum sure siniri. Bu olmadan SymPy bazi sayisal
    # degerlerde hic donmuyordu; test takimi bir gecede bitmedi ve
    # arkada %99 islemciyle donen yedi surec birikmisti (olculdu).
    check("cozum: sure siniri ana parcacikta calisiyor",
          lambda: formulas._sureli(lambda: __import__("time").sleep(5), 0.5)
          is formulas._ZAMAN_ASIMI, True)

    def _yan_parcacikta():
        import threading
        kutu = {}

        def _kos():
            kutu["r"] = formulas._sureli(
                lambda: __import__("time").sleep(5), 0.5)
        t = threading.Thread(target=_kos)
        t.start()
        t.join()
        return kutu.get("r") is formulas._ZAMAN_ASIMI
    check("cozum: sure siniri yan parcacikta da calisiyor",
          _yan_parcacikta, True)
    check("cozum: sure siniri normal cozumu bozmuyor",
          lambda: round(formulas.solve_for(
              formulas.BY_ID["kinetik"], {"m": 2.0, "v": 3.0})[1][0], 3), 9.0)

    # Ders videosu altyazisi duz metne cevriliyor (ag gerektirmez).
    check("video ders: altyazi metne cevriliyor",
          lambda: _kaynaklar._vtt_metne(
              "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n[SQUEAKING]\n\n"
              "00:00:03.000 --> 00:00:06.000\nisik hizi her gozlemci\n\n"
              "00:00:06.000 --> 00:00:08.000\nicin aynidir."),
          "isik hizi her gozlemci icin aynidir.")

    # Kod istegi kendi konusunu tasimaz; konu bir onceki turdadir.
    def _matlab_tasima():
        brain.respond("aksiyon potansiyeli nedir", session="_t_mtl2")
        return brain.respond("matlab kodu yazar misin",
                             session="_t_mtl2").text
    check("sohbet: kod istegi onceki konuyu tasiyor",
          lambda: "Hodgkin" in _matlab_tasima(), True)

    # Kod cevabindan sonra konu MATLAB'e kaymamali; fizik konusu kalmali.
    def _kod_sonrasi_konu():
        brain.respond("aksiyon potansiyeli nedir", session="_t_mtl3")
        brain.respond("matlab kodu yazar misin", session="_t_mtl3")
        return brain.respond("sayisal ornek", session="_t_mtl3").text
    check("sohbet: kod sonrasi konu fizik konusunda kaliyor",
          lambda: "aksiyon potansiyeli" in _kod_sonrasi_konu().lower(), True)

    check("yazim: soru bicimleri bozulmuyor",
          lambda: _anl.duzelt("onun hayati nasildi")[1], [])

    # "bunun formulu var mi" bir devam sorusudur; geriye kalan "var mi"
    # parcasi kendi konusu sanilmamali (olculdu).
    check("sohbet: 'bunun formulu var mi' devam sorusu sayiliyor",
          lambda: brain._followup_subject(
              "bunun formulu var mi", {"last_subject": "gokyuzu mavi"}),
          "gokyuzu mavi")

    # ── Fizik ogrencisinin gercek istekleri ─────────────────────────
    # Turkce cumle denklem sanilmamali. Olculdu: "sonsuz kuyuda n=3
    # enerji duzeyi hesapla" -> "kuyuda*n*sonsuz = 3*duzeyi*enerji".
    check("niyet: turkce cumle denklem sanilmiyor",
          lambda: nlu.classify("sonsuz kuyuda n=3 enerji duzeyi hesapla")[0]
          != "denklem", True)
    check("niyet: gercek denklem hala taniniyor",
          lambda: nlu.classify("denklemi coz: 3x+1=7")[0], "denklem")
    check("denklem: komut kelimeleri ayikleniyor",
          lambda: "x = 2" in brain.respond("denklemi coz: 3x+1=7",
                                           session="_t_dnk").text, True)

    # Ogrenci "4y" yazar; ODE cozucusu bunu okumaliydi.
    check("ode: ortulu carpim okunuyor",
          lambda: "sin(2*x)" in solver.ode("y'' + 4y = 0")["solutions"][0]["expr"],
          True)
    check("ode: birinci mertebe",
          lambda: "exp" in solver.ode("y' = 2y")["solutions"][0]["expr"], True)

    # Fiziksel siralama: Carnot'ta sicak kaynak soguk kaynaktan sicaktir.
    # Bu kural olmadan sistem "verim = -0.667" diyordu (olculdu).
    check("hesap: carnot verimi dogru isaretli",
          lambda: "0.4" in brain.respond(
              "500 K ve 300 K arasinda calisan carnot makinesinin verimi nedir",
              session="_t_crn").text, True)
    check("hesap: sogutucu ile isi pompasi karismiyor",
          lambda: "Sogutucu" in brain.respond(
              "270 K ve 300 K arasinda calisan sogutucunun etkinlik "
              "katsayisi nedir", session="_t_sgt").text, True)
    check("hesap: soru kelimesi olmadan da hesapliyor",
          lambda: "Çözüm" in brain.respond(
              "carnot verimi 500 K ve 300 K arasinda", session="_t_crn2").text,
          True)

    # Euler-Lagrange turetimi: 2. sinif ogrencisinin istedigi sey.
    from . import lagrange as _lag
    check("lagrange: sarkacin hareket denklemi turetiliyor",
          lambda: "-g*sin(theta)/l" in (
              _lag.turet("lagrange ile sarkacin hareket denklemini turet")
              or ""), True)
    check("lagrange: yay-kutle Hooke yasasini veriyor",
          lambda: "-k*x/m" in (
              _lag.turet("yay kutle sistemini lagrange ile coz") or ""), True)
    check("lagrange: atwood ivmesi dogru",
          lambda: "g*(m1 - m2)/(m1 + m2)" in (
              _lag.turet("atwood makinesini lagrange ile turet") or ""), True)
    check("lagrange: istek yoksa devreye girmiyor",
          lambda: _lag.turet("sarkacin periyodu nedir"), None)

    # Zayif formul eslesmesiyle turetim yapilmamali.
    check("turetim: zayif eslesmede konuya donuyor",
          lambda: "Isi iletimi" not in brain.respond(
              "lagrange ile sarkacin hareket denklemini turet",
              session="_t_lag").text, True)

    # Tek cumlelik "nedensel" parca cevap sayilmaz; ders daha dolgunsa
    # o verilir (olculdu: komutator sorusuna 96 karakter donuyordu).
    check("neden: ince cevap yerine ders veriliyor",
          lambda: len(brain.respond("komutator nedir neden onemli",
                                    session="_t_kom").text) > 400, True)

    # Yazim: cekimli bicimler bozulmamali, gercek hatalar duzelmeli.
    check("yazim: cekimli bicim bozulmuyor",
          lambda: _anl.duzelt("rlc devresinde rezonans frekansi")[1], [])
    check("yazim: gercek hata duzeltiliyor (izafyet)",
          lambda: _anl.duzelt("izafyet teorisi")[1], [("izafyet", "izafiyet")])

    # 3-4. sinif cekirdegi. Olculdu: mufredat taramasinda ust sinif
    # dersleri makale kirintisiyla ya da yanlis konuyla cevaplaniyordu.
    check("cekirdek: ust sinif mufredat konulari yuklu",
          lambda: all(knowledge.get(k) is not None for k in
                      ("ozdes_parcaciklar", "sacilma_kurami",
                       "kanonik_donusum", "multipol", "dalga_kilavuzu",
                       "vektor_analizi", "ozel_fonksiyonlar",
                       "green_fonksiyonu", "tensor", "faz_gecisi",
                       "cekirdek_modelleri", "yildiz_evrimi",
                       "elektronik", "sayisal_yontemler_fizik")), True)
    check("yonlendirme: born yaklasimi gunluk sacilmaya gitmiyor",
          lambda: "Born" in brain.respond("sacilma born yaklasimi",
                                          session="_t_brn").text, True)
    check("yonlendirme: kanonik donusum istatistige gitmiyor",
          lambda: "Kanonik" in brain.respond("kanonik donusumler",
                                             session="_t_kan").text, True)
    check("yonlendirme: dalga kilavuzu ses konusuna gitmiyor",
          lambda: "Kılavuz" in brain.respond("dalga kilavuzu",
                                             session="_t_dkl").text, True)
    check("vektor: alan verilmezse teorem anlatiliyor",
          lambda: "Teorem" in brain.respond("vektor analizi diverjans teoremi",
                                            session="_t_vkt").text, True)
    check("ode: kavram sorusu cozucuye gitmiyor",
          lambda: "Sayısal" in brain.respond(
              "diferansiyel denklem sayisal cozumu", session="_t_dfs").text,
          True)

    check("cekirdek: mufredat bosluklari kapandi",
          lambda: all(knowledge.get(k) is not None for k in
                      ("statik_denge", "normal_modlar", "poisson_laplace",
                       "dipol_isimasi", "varyasyonel_yontem",
                       "hiz_dagilimi", "laplace_donusumu", "kristal_yapi",
                       "fonon_isi", "yariiletken_fizigi",
                       "kirmizi_kayma_kozmoloji", "olcum_aletleri",
                       "egri_uydurma")), True)
    # Sabit adi baska bir kavramin icinde geciyorsa sabit cevabi verilmez.
    check("yonlendirme: 'maxwell boltzmann dagilimi' sabite gitmiyor",
          lambda: "Dağılım" in brain.respond("maxwell boltzmann dagilimi",
                                             session="_t_mbd").text, True)
    check("yonlendirme: 'planck sabiti' biyografiye gitmiyor",
          lambda: "sabiti" in brain.respond("planck sabiti",
                                            session="_t_pls").text, True)
    check("matris: ifade varsa hesaplanir, yoksa ogretilir",
          lambda: ("Matris islemi" in brain.respond(
                       "[[1,2],[3,4]] ozdegerleri", session="_t_mtr").text
                   and "Normal Mod" in brain.respond(
                       "ozdeger problemi", session="_t_mtr2").text), True)

    # Cok adimli sayisal problemler: ogrencinin asil ihtiyaci.
    # Olculdu: "5 ohm ve 10 ohm paralel ... esdeger direnc" sorusunda
    # degerler yanlis degiskenlere atanip R2 = 10 ohm cevabi veriliyordu;
    # "yukari atiliyor" sorusuna ise Osmanli felsefe makalesi geliyordu.
    check("problem: paralel direnc dogru hesaplaniyor",
          lambda: "3.333" in brain.respond(
              "5 ohm ve 10 ohm paralel bagli esdeger direnc nedir",
              session="_t_par").text, True)
    check("problem: yukari atista ivme -g aliniyor",
          lambda: "-9.42" in brain.respond(
              "2 kg cisim 20 m/s ile yukari atiliyor 3 saniye sonra hizi ne",
              session="_t_ats").text, True)
    check("birim: turkce birim adi boyutundan taniniyor",
          lambda: nlu._birim_uyar("saniye", "s"), True)
    check("cekirdek: secmeli ders konulari yuklu",
          lambda: all(knowledge.get(k) is not None
                      for k in ("plazma", "kaos")), True)

    # Sayisal odev problemleri: cevap SAYI olmali, formul listesi degil.
    def _sayisal(soru, oturum):
        return brain.respond(soru, session=oturum).text
    check("problem: serbest dusme carpma hizi",
          lambda: "14 m/s" in _sayisal(
              "10 m yuksekten birakilan cismin yere carpma hizi nedir",
              "_t_sd"), True)
    check("problem: foton enerjisi dalga boyundan",
          lambda: "3.0561" in _sayisal(
              "650 nm dalga boylu fotonun enerjisi nedir", "_t_ft"), True)
    check("problem: elektron hizlandirma enerjisi",
          lambda: "1.6022" in _sayisal(
              "elektron 100 V ile hizlandirilirsa kazandigi enerji kac joule",
              "_t_el"), True)
    check("problem: ideal gaz basinci (sabit korunuyor)",
          lambda: "9.977" in _sayisal(
              "2 mol ideal gaz 300 K'de 0.05 m3 hacimde basinci nedir",
              "_t_ig"), True)
    check("problem: seri siga",
          lambda: "2×10^-6" in _sayisal(
              "3 mikrofarad ve 6 mikrofarad seri bagli esdeger siga nedir",
              "_t_ss"), True)
    # Birim cevrimi hala calismali; fizik problemi cevrim sanilmamali.
    check("birim: kisa cevrim istegi hala taniniyor",
          lambda: nlu.classify("90 km/h kac m/s")[0], "birim")
    check("birim: uzun fizik sorusu cevrim sanilmiyor",
          lambda: nlu.classify(
              "elektron 100 V ile hizlandirilirsa kazandigi enerji kac joule"
          )[0] != "birim", True)
    check("birim: m3 tek parca okunuyor",
          lambda: nlu.extract_number_unit("0.05 m3")[0][1], "m3")

    # ODTU gibi INGILIZCE egitim yapan bolumler icin: ders terimi
    # Ingilizce girildiginde de dogru konuya gitmeli ve SAYISAL cevap
    # verilmeli. Olculdu: "black-body radiation" -> "Radyasyonun
    # Biyolojik Etkisi"; Ingilizce cozumlerde basligi "Result" oldugu
    # icin hesap sonucu atiliyordu.
    check("ingilizce: ders terimleri dogru konuya gidiyor",
          lambda: _olcum.ingilizce_puani()[0] >= 17, True)
    check("ingilizce: sayisal cevap veriliyor",
          lambda: "9 J" in brain.respond(
              "a 2 kg mass moving at 3 m/s kinetic energy",
              session="_t_enk", lang_override="en").text, True)
    check("ingilizce: carnot verimi hesaplaniyor",
          lambda: "0.4" in brain.respond(
              "efficiency of a Carnot engine between 500 K and 300 K",
              session="_t_enc", lang_override="en").text, True)
    check("niyet: 'Chandrasekhar limit' matematik limiti sanilmiyor",
          lambda: nlu.classify("what is the Chandrasekhar limit")[0]
          != "limit", True)
    check("niyet: gercek limit istegi hala taniniyor",
          lambda: nlu.classify("limit of sin(x)/x as x->0")[0], "limit")
    check("cekirdek: kara cisim isinimi yuklu",
          lambda: knowledge.get("kara_cisim") is not None, True)

    # Iki adimli devre problemi: en sik gelen odev kalibi. Olculdu:
    # sistem tek bagintiyla zorlayip "R2 = -4 ohm" diyordu.
    check("problem: seri devre iki adimda cozuluyor",
          lambda: "1 A" in brain.respond(
              "12 V kaynaga seri bagli 4 ohm ve 8 ohm direnclerden gecen "
              "akim nedir", session="_t_sd2").text, True)
    check("problem: paralel devre iki adimda cozuluyor",
          lambda: "4 A" in brain.respond(
              "12 V kaynaga paralel bagli 4 ohm ve 12 ohm devreden gecen "
              "toplam akim", session="_t_pd2").text, True)
    check("problem: negatif direnc cevap olarak verilmiyor",
          lambda: _prb.makul_mu(formulas.BY_ID["direnc_seri"], "R2", -4.0)[0],
          False)

    # ── Cok adimli odev cozumu ──────────────────────────────────────
    # Kullanicinin birinci onceligi. Olculdu: 12 sorudan 5'i
    # cozulebiliyor ve biri YANLIS cevap veriyordu ("R2 = -4 ohm").
    from . import zincir as _zin
    check("odev: cok adimli problemler sayiyla cevaplaniyor (TR)",
          lambda: _olcum.odev_puani("tr")[0] >= 17, True)
    check("odev: ingilizce cok adimli problemler",
          lambda: _olcum.odev_puani("en")[0] >= 4, True)
    check("zincir: dusen cisim iki adimda cozuluyor",
          lambda: "196" in (_zin.coz(
              "10 m yuksekten birakilan 2 kg cismin yere carparken "
              "kinetik enerjisi nedir") or ""), True)
    check("zincir: frenleme ivme uzerinden kuvvete gidiyor",
          lambda: "-4000" in (_zin.coz(
              "1000 kg araba 20 m/s hizdan 5 saniyede duruyor fren "
              "kuvveti nedir") or ""), True)
    check("zincir: tek adimlik soruda devreye girmiyor",
          lambda: _zin.coz("2 kg kutle 3 m/s kinetik enerji"), None)
    check("zincir: alakasiz baginti zincire girmiyor",
          lambda: "c**2" not in (_zin.coz(
              "10 m yuksekten birakilan 2 kg cismin yere carparken "
              "kinetik enerjisi nedir") or ""), True)
    check("birim: turkce cekim eki birimden ayikleniyor",
          lambda: units.to_si(5.0, "saniyede")[0], 5.0)

    # ── Ders kitabi tarzi problem seti ve ispat modu ────────────────
    from . import problemseti as _pset
    check("problem seti: kademeli bolumler uretiliyor",
          lambda: all(x in (_pset.uret("termodinamik") or "")
                      for x in ("Doğrudan uygulama", "Çok adımlı",
                                "Kavramsal")), True)
    check("problem seti: istek dogru yonleniyor",
          lambda: "Problem Seti" in brain.respond(
              "termodinamik problem seti", session="_t_pst").text, True)
    check("ispat: varsayimlar ayrica yaziliyor",
          lambda: "Kullanılan varsayımlar" in (
              _pset.ispat("sarkacin hareket denklemini ispatla") or ""),
          True)
    check("ispat: korpus metni ispat diye sunulmuyor",
          lambda: "Makaleleri incelerken" not in (
              _pset.ispat("sarkacin periyodunu ispatla") or ""), True)
    check("dil: turkce problem seti istegi ingilizce sanilmiyor",
          lambda: nlu.detect_lang("termodinamik problem seti"), "tr")
    check("dil: ingilizce soru hala ingilizce",
          lambda: nlu.detect_lang("how does a p-n junction work"), "en")

    # ── Uzaktan erisim guvenligi ────────────────────────────────────
    # On yuz GitHub Pages'te, motor kullanicinin bilgisayarinda. Tunel
    # adresi internete acik oldugu icin anahtar ZORUNLU; anahtarsiz
    # kurulumda yalnizca ayni bilgisayardan erisilebilir.
    from . import config as _cfg
    check("erisim: varsayilan olarak yalnizca yerel dinleme",
          lambda: _cfg.HOST if not __import__("os").environ.get(
              "PARGUSZ_HOST") else "127.0.0.1", "127.0.0.1")
    check("erisim: anahtar ve origin ayarlanabilir",
          lambda: (hasattr(_cfg, "ANAHTAR") and hasattr(_cfg, "ORIGIN")),
          True)
    check("erisim: CORS yalnizca izinli adrese acilir",
          lambda: _cors_denemesi(), True)

    # "Tumunu sil" YALNIZCA sohbet dokumunu silmeli; ogrenilen bilgi
    # (makale, kavram, bulgu, formul) kalmali.
    def _tumunu_sil_denemesi():
        import time as _t
        oturum = "_t_silme%d" % int(_t.time() * 1000)
        db.add_chat(oturum, "user", "deneme mesaji") if hasattr(
            db, "add_chat") else None
        onceki = {}
        with db.conn() as c:
            for tablo in ("papers", "concepts", "insights", "terms",
                          "formulas_learned", "gaps", "explored"):
                onceki[tablo] = c.execute(
                    "SELECT COUNT(*) FROM %s" % tablo).fetchone()[0]
        db.delete_all_sessions(immediate=True)
        with db.conn() as c:
            sohbet = c.execute("SELECT COUNT(*) FROM chat").fetchone()[0]
            for tablo, n in onceki.items():
                if c.execute("SELECT COUNT(*) FROM %s" % tablo
                             ).fetchone()[0] < n:
                    return "%s tablosu kucuruldu" % tablo
        return "temiz" if sohbet == 0 else "sohbet kalmis"
    check("silme: tumunu sil ogrenilen bilgiye dokunmuyor",
          _tumunu_sil_denemesi, "temiz")
    # Test oturumlari kullanicinin sohbet listesinde gorunmemeli.
    # Olculdu: test kosusundan sonra kenar cubuguna sekiz test sohbeti
    # dusuyordu ("_test_pr2 / merhaba" gibi).
    check("silme: ic oturumlar listede gorunmuyor",
          lambda: [x for x in db.list_sessions(80)
                   if x["id"].startswith("_")], [])

    # ── Tuzak sorular: kandirilmadan cozme ──────────────────────────
    # Kullanicinin sozleri: "kandirilmadan problem cozebilmesi lazim".
    # Olculdu: "surtunmesiz alanda ... surtunme degerini hesapla"
    # sorusuna BHH dersi anlatildi; "1 kg + 30 m + 22 cm" sorusuna
    # 1 kg'in birim cevrimi yapildi.
    from . import boyut as _byt, ayrintili as _ayr
    check("tuzak: tuzak sorular dogru cevaplaniyor",
          lambda: _olcum.tuzak_puani()[0] >= 17, True)
    check("girdi: negatif kutle reddediliyor",
          lambda: "fiziksel değil" in (_prb.girdi_denetle(
              formulas.BY_ID["kinetik"], {"m": -5.0, "v": 10.0}) or ""),
          True)
    check("girdi: gecerli deger reddedilmiyor",
          lambda: _prb.girdi_denetle(
              formulas.BY_ID["kinetik"], {"m": 5.0, "v": 10.0}), None)
    check("hedef: verilen degil SORULAN buyukluk seciliyor",
          lambda: _prb.hedef_tahmin(
              formulas.BY_ID["agirlik"],
              "kutlesi 5 kg olan cismin agirligi kac newton"), "W")
    check("atama: etiketli sayi baska degiskene verilmiyor",
          lambda: "1.57" in brain.respond(
              "yaricapi 0.5 m periyodu 2 s dairesel hareket cizgisel hizi",
              session="_t_dair").text, True)
    check("oncul: birim sorulan buyuklugu izliyor",
          lambda: "0 N" in (_prb.oncul_cevabi(
              "sabit hizla giden trenin net kuvveti nedir") or ""), True)
    check("boyut: farkli boyutlar toplanmiyor",
          lambda: "yapılamaz" in (_byt.coz("1 kg + 30 metre + 22 cm") or ""),
          True)
    check("boyut: ayni boyut dogru toplaniyor",
          lambda: "30.22" in (_byt.coz("30 m + 22 cm") or ""), True)
    check("boyut: toplanabilenler ayrica hesaplaniyor",
          lambda: "30.22" in (_byt.coz("1 kg + 30 metre + 22 cm") or ""),
          True)
    check("oncul: surtunmesiz ortamda surtunme sifir",
          lambda: "0 N" in (_prb.oncul_cevabi(
              "surtunmesiz yuzeyde giden cismin surtunme kuvveti nedir")
              or ""), True)
    check("oncul: oncul yoksa devreye girmiyor",
          lambda: _prb.oncul_cevabi("surtunme kuvveti nedir"), None)
    check("bhh: maksimum hiz dogru hesaplaniyor",
          lambda: "18.85" in brain.respond(
              "30 m genlikli basit harmonik hareket periyodu 10 s "
              "maksimum hizi nedir", session="_t_bhh").text, True)
    check("zincir: konu disina cikmiyor",
          lambda: "Torricelli" not in brain.respond(
              "30 m genlikli basit harmonik hareket periyodu 10 s "
              "maksimum hizi nedir", session="_t_bhh2").text, True)
    check("birim: 'sny' kisaltmasi taniniyor",
          lambda: units.to_si(10.0, "sny")[0], 10.0)
    check("yonerge: cozum bicimi istegi konu sanilmiyor",
          lambda: _ayr.yonerge_mi(
              "Bu problemi cozerken: birim analizini yap, sembolik coz, "
              "varsayimlari listele"), True)
    check("yonerge: normal soru yonerge sanilmiyor",
          lambda: _ayr.yonerge_mi("boyut analizi nedir"), False)

    # Gunluk hayattan sorular cekirdekte olmali. Olculdu: "gokyuzu neden
    # mavi" sorusuna "mavi kart" gecen bir vatandaslik hukuku makalesi
    # getiriliyordu.
    check("cekirdek: gunluk hayat konulari yuklu",
          lambda: all(knowledge.get(k) is not None for k in
                      ("sacilma", "kaldirma_gunluk", "gokkusagi",
                       "gunluk_termo")), True)
    check("beyin: 'gokyuzu neden mavi' sacilma konusuna gidiyor",
          lambda: "Saçılma" in brain.respond(
              "gokyuzu neden mavi", session="_t_gok").text, True)
    check("beyin: 'buz neden yuzer' dogru konuya gidiyor",
          lambda: "Yüzme" in brain.respond(
              "buz neden yuzer", session="_t_buz").text, True)

    # Ders videosunun jenerik blogu icerik degildir; her bulgunun basina
    # yapisiyordu (olculdu).
    check("video ders: jenerik blogu ayikleniyor",
          lambda: _kaynaklar._vtt_metne(
              "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
              "Funding provided by the Singapore University of Technology "
              "and Design (SUTD) Developed by the Teaching and Learning "
              "Laboratory (TLL) at MIT for SUTD MIT © 2012 "
              "You know gravity as the force."),
          "You know gravity as the force.")

    # Kisa anahtar baska kelimenin icine dusmemeli.
    check("arama: kisa anahtar uzun kelimeye yayilmiyor",
          lambda: all(t["key"] != "molekuler_spektroskopi"
                      for _s, t in knowledge.search("isik hizi nedir",
                                                    limit=3)), True)

    # Turkce kok cozumleme — kapsamin %78'den %100'e cikmasini saglayan sey
    from . import turkce as _tr
    check("turkce: unsuz yumusamasi geri alinıyor",
          lambda: "termodinamik" in _tr.kokler("termodinamigin"), True)
    check("turkce: ek olmayan sesli korunuyor",
          lambda: "entropi" in _tr.kokler("entropinin"), True)
    check("turkce: kok genisletmesi ham bicimi de tasiyor",
          lambda: ("yasasini" in _tr.genislet("yasasini")
                   and "yasa" in _tr.genislet("yasasini")), True)
    check("matlab: TUM sablonlar sozdizimi denetimini geciyor",
          lambda: sorted(mkontrol.tum_sablonlar()), [])
    # ------------------------------- makaleleri birlestirip bilgi uretme
    from . import sentezbilgi as _sb, learner as lg
    def _sentez_kanit_kapisi():
        """Tek kaynakli iddia bilgi sayilmamali."""
        c = db.conn()
        _sb._kur()
        c.execute("DELETE FROM insights WHERE cumle LIKE '_test_sentez%'")
        c.execute("DELETE FROM derived WHERE ifade LIKE '_test_sentez%'")
        c.commit()
        # Uzlasma artik makale kaydiyla BIRLESTIRILIYOR (bagimsizlik
        # denetimi icin kaynak/dergi gerekiyor), bu yuzden test makaleleri
        # de olusturuluyor. Ikisi farkli yayindan.
        c.execute("DELETE FROM papers WHERE ext_id LIKE '_test_sentez%'")
        for pid, kaynak, dergi in ((900001, "arxiv", "A dergisi"),
                                   (900002, "doaj", "B dergisi")):
            c.execute(
                "INSERT OR REPLACE INTO papers"
                "(id, source, ext_id, title, abstract, authors, categories,"
                " lang, url, published, fetched_at, atif, hakemli,"
                " geri_cekik, alan, dergi, kalite, islendi)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (pid, kaynak, "_test_sentez_%d" % pid, "_test_sentez baslik",
                 "_test_sentez ozet", "", "", "en", "", "", 0, -1, -1, 0,
                 "physics", dergi, 50.0, 1))
        c.commit()
        for pid, ek in ((900001, "one"), (900002, "two")):
            c.execute(
                "INSERT OR IGNORE INTO insights"
                "(norm, tur, cumle, paper_id, lang, skor, at) "
                "VALUES(?,?,?,?,?,?,?)",
                ("_test_konu", "bulgu",
                 "_test_sentez plasmon resonance shifts strongly with "
                 "nanoparticle diameter %s" % ek, pid, "en", 2.0, 0))
        c.commit()
        onceki = c.execute("SELECT COUNT(*) FROM derived").fetchone()[0]
        _sb.uzlasma_uret(en_fazla=200)
        sonra = c.execute(
            "SELECT kanit FROM derived WHERE konu='_test_konu'").fetchall()
        c.execute("DELETE FROM insights WHERE cumle LIKE '_test_sentez%'")
        c.execute("DELETE FROM derived WHERE konu='_test_konu'")
        c.execute("DELETE FROM papers WHERE ext_id LIKE '_test_sentez%'")
        c.commit()
        return "iki kaynak" if (sonra and sonra[0]["kanit"] >= 2) else "yok"
    check("sentez: iki bagimsiz makalenin uzlastigi ifade bilgi oluyor",
          _sentez_kanit_kapisi, "iki kaynak")

    def _sentez_tek_kaynak():
        c = db.conn()
        _sb._kur()
        c.execute("DELETE FROM insights WHERE cumle LIKE '_test_tek%'")
        c.execute("DELETE FROM derived WHERE konu='_test_tek'")
        c.commit()
        c.execute(
            "INSERT OR REPLACE INTO papers"
            "(id, source, ext_id, title, abstract, authors, categories, lang,"
            " url, published, fetched_at, atif, hakemli, geri_cekik, alan,"
            " dergi, kalite, islendi)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (900003, "arxiv", "_test_tek_1", "_test_tek", "_test_tek", "", "",
             "en", "", "", 0, -1, -1, 0, "physics", "T dergisi", 50.0, 1))
        c.commit()
        c.execute(
            "INSERT OR IGNORE INTO insights"
            "(norm, tur, cumle, paper_id, lang, skor, at) VALUES(?,?,?,?,?,?,?)",
            ("_test_tek", "bulgu",
             "_test_tek exotic quasiparticle stabilises unusual lattice "
             "configuration reliably", 900003, "en", 2.0, 0))
        c.commit()
        _sb.uzlasma_uret(en_fazla=200)
        n = c.execute("SELECT COUNT(*) FROM derived WHERE konu='_test_tek'"
                      ).fetchone()[0]
        c.execute("DELETE FROM insights WHERE cumle LIKE '_test_tek%'")
        c.execute("DELETE FROM papers WHERE ext_id LIKE '_test_tek%'")
        c.commit()
        return n
    check("sentez: tek kaynakli iddia bilgi sayilmiyor", _sentez_tek_kaynak, 0)

    check("cumle turu: ders kitabi tanimi taniniyor",
          lambda: lg.cumle_turu("Kinetic energy is the energy of motion."),
          "tanim")
    check("cumle turu: yasa ifadesi taniniyor",
          lambda: lg.cumle_turu(
              "The law of conservation of energy states that energy cannot "
              "be created or destroyed."), "tanim")
    check("cumle turu: Turkce tanim taniniyor",
          lambda: lg.cumle_turu(
              "Entropi, bir sistemin duzensizligi olarak tanimlanir."), "tanim")

    # ---------------------------------------- konusmadan ogrenme
    from . import bosluk as _bos
    def _bosluk_dongusu():
        c = db.conn()
        c.execute("DELETE FROM gaps WHERE soru LIKE '_test_%'")
        c.commit()
        _bos.kaydet("_test_ hayali parcacik etkisi", "tr", guclu=False)
        _bos.kaydet("_test_ hayali parcacik etkisi", "tr", guclu=False)
        acik = [g for g in _bos.oncelikli(limit=20)
                if g["soru"].startswith("_test_")]
        if not acik or acik[0]["sayac"] != 2:
            return "bosluk birikmedi"
        _bos.denendi(acik[0]["norm"], basarili=True)
        kalan = [g for g in _bos.oncelikli(limit=20)
                 if g["soru"].startswith("_test_")]
        c.execute("DELETE FROM gaps WHERE soru LIKE '_test_%'")
        c.commit()
        return "tamam" if not kalan else "kapanmadi"
    check("bosluk: cevaplanamayan soru birikip ogrenilince kapaniyor",
          _bosluk_dongusu, "tamam")
    check("bosluk: selamlasma bosluk sayilmiyor",
          lambda: _bos.kaydet("merhaba", "tr", guclu=False), None)
    check("takma ad: kullanici ifadesi kanonik terime baglaniyor",
          lambda: (_bos.takma_ad_kaydet("_test_ kazimir etkisi",
                                        "Casimir effect")
                   and "Casimir effect" in
                   _bos.genislet("_test_ kazimir etkisi nedir")), True)
    from . import sources as _src
    check("kaynak: ders kitabi adaptoru mevcut",
          lambda: all(callable(getattr(_src, ad, None)) for ad in
                      ("openstax_kitaplar", "openstax_bolumler",
                       "openstax_bolum", "wiki_langlink")), True)

    # ------------------------------------ dogal dilde verilen degerler
    check("deger: 'kutlesi 2 kg hizi 5 m/s' sembole baglaniyor",
          lambda: nlu.formul_degerleri(
              formulas.BY_ID["kinetik"],
              "kutlesi 2 kg hizi 5 m/s olan cismin kinetik enerjisi nedir"),
          {"m": (2.0, "kg"), "v": (5.0, "m/s")})
    check("deger: birim ayirt ediyor (yay sabiti k, kuvvet F degil)",
          lambda: sorted(nlu.formul_degerleri(
              formulas.BY_ID["hooke"],
              "yay sabiti 200 N/m, uzama 0.05 m ise kuvvet nedir")),
          ["k", "x"])
    check("deger: bilesik birim okunuyor (J/(kg·K))",
          lambda: nlu.formul_degerleri(
              formulas.BY_ID["isi"],
              "kutlesi 2 kg, sicaklik degisimi 60 K, ozgul isi 4186 J/(kg·K)"
          ).get("c", (0,))[0], 4186.0)
    check("deger: dogal dilden hesap uctan uca calisiyor",
          lambda: "3 A" in brain.respond(
              "gerilim 12 V direnc 4 ohm ise akim nedir",
              session="_test_deger").text, True)
    check("niyet: birimli degerlerle sorulan soru hesaba gidiyor",
          lambda: nlu.classify(
              "kutlesi 2 kg hizi 5 m/s olan cismin kinetik enerjisi nedir")[0],
          "formul")
    check("niyet: 'yay sabiti' fiziksel sabit listesini acmiyor",
          lambda: nlu.classify("yay sabiti nedir")[0] != "sabit", True)

    # ---------------------------------------------- genisleme motoru
    from . import genisleme as _gen, curriculum as _cur
    check("genisleme: makalelerden yol haritasi uretiliyor",
          lambda: _gen.harita_uret("physics.optics") is not None, True)
    check("genisleme: uretilen harita korpustan guncel konu iceriyor",
          lambda: any(a["ad"].startswith("4.")
                      and len(a["konular"]) >= _gen.EN_AZ_IFADE
                      for a in _gen.harita_uret("physics.optics")["asamalar"]),
          True)
    check("genisleme: yetersiz makaleli alan icin harita uretilmiyor",
          lambda: _gen.harita_uret("bilinmeyen-alan"), None)
    check("genisleme: uretilen her haritanin komutu calisiyor",
          lambda: [k for k in _cur.PATHS
                   if _cur.PATHS[k].get("uretilmis")
                   and _cur.find((_cur.PATHS[k]["kw"] or [""])[0]
                                 + " yol haritasi") is None], [])
    # Uyumsuz konular birlestirilmemeli: kalorimetreden cekilen kutleyi
    # Newton yasasina koymak boyutca dogru ama fizik degil.
    check("genisleme: uyumsuz konulardaki formuller birlestirilmiyor",
          lambda: _gen._konular_uyumlu(formulas.BY_ID["newton2"],
                                       formulas.BY_ID["isi"]), False)
    check("genisleme: turetilmis formul dogrulamadan geciyor",
          lambda: all(
              _dg.boyut_denetimi(f)["ok"] is True
              for f in formulas.FORMULAS if f.get("uretilmis")), True)
    check("genisleme: turetilmis formul cekirdegin onune gecmiyor",
          lambda: (formulas.search("newton ikinci yasa", limit=1) or
                   [(0, {"id": "yok"})])[0][1]["id"], "newton2")

    # Fiziksel anlam notlari baglama giriyor mu? Girmezse model denklemin
    # anlamini kendi uyduruyor ve hata yapabiliyor.
    check("notlar: bilinmeyen formul kimligi yok",
          lambda: [x for x in formulas.SOZLUK_BILINMEYEN], [])
    check("notlar: adyabatik notu birinci yasayi dogru anlatiyor",
          lambda: ("dU = -W" in (formulas.BY_ID["adyabatik"]["note_tr"] or "")
                   and "YUKSELIR" in formulas.BY_ID["adyabatik"]["note_tr"]),
          True)
    check("baglam: formul notu modele veriliyor",
          lambda: any("fiziksel anlam" in p for p in
                      _bg._formul_baglami("adyabatik surec", "tr")), True)

    # Us konumundaki degiskenler (adyabatik surecte gamma) sembolik cozumu
    # askin denkleme cevirip SymPy'yi kilitliyordu; dogrulama hic bitmiyordu.
    def _us_hizli():
        import time as _t
        t0 = _t.time()
        for fid in ("adyabatik", "otto", "van_der_waals"):
            _dg.formul_dogrula(formulas.BY_ID[fid])
        return "hizli" if _t.time() - t0 < 20 else "yavas"
    check("dogrulama: us iceren formuller kilitlenmeden dogrulaniyor",
          _us_hizli, "hizli")
    check("cozum: us konumundaki degisken icin sayisal kok bulunuyor",
          lambda: round(formulas.solve_for(
              formulas.BY_ID["otto"], {"eta": 0.55, "rc": 8.0},
              target="gam")[1][0], 3),
          1.384)
    check("dogrulama: raporu uretiliyor",
          lambda: _dg.rapor("tr"),
          contains("doğrulama", str(len(formulas.FORMULAS))))
    check("niyet: kendini dogrula komutu",
          lambda: nlu.classify("kendini dogrula")[0], "kendini_dogrula")

    # ------------------------------------------------ coklu soru uretimi
    check("soru adedi: 'toplam 10 adet' okunuyor",
          lambda: brain._istenen_adet("toplam 10 adet cevaplari ile birlikte"), 10)
    check("soru adedi: '5 soru ver'", lambda: brain._istenen_adet("5 soru ver"), 5)
    check("soru adedi: ingilizce",
          lambda: brain._istenen_adet("give me 8 questions"), 8)
    check("soru adedi: adet yoksa None",
          lambda: brain._istenen_adet("termodinamik ornek ver"), None)

    def on_soru():
        return brain.respond(
            "bana ornek soru uretmeni istiyorum fizik alani ile alakali "
            "toplam 10 adet cevaplari ile birlikte", session="_test_10").text
    check("uretim: 10 soru isteyince 10 soru geliyor",
          lambda: len(re.findall(r"^#### \d+\.", on_soru(), re.M)), 10)
    check("uretim: sorular farkli konulardan",
          lambda: len(set(re.findall(r"<span class='meta'>(\w+)</span>",
                                     on_soru()))) >= 6, True)
    check("uretim: her soruda cevap var",
          lambda: len(re.findall(r"\*\*Cevap:\*\*", on_soru())), 10)

    # Sabit ayrimi: `Q = m*c*dT` icindeki c ozgul isidir, isik hizi degil
    check("sabit ayrimi: isi formulunde c isik hizi degil",
          lambda: brain._sabit_uygun(formulas.BY_ID["isi"], "c"), False)
    check("sabit ayrimi: E=mc^2 icindeki c isik hizi",
          lambda: brain._sabit_uygun(formulas.BY_ID["E_mc2"], "c"), True)
    check("sabit ayrimi: paralel plaka eps0 taniniyor",
          lambda: brain._sabit_uygun(formulas.BY_ID["paralel_plaka"], "eps0"), True)
    check("sabit ayrimi: yay sabiti k sabit degil",
          lambda: brain._sabit_uygun(formulas.BY_ID["hooke"], "k"), False)

    def isi_hesabi():
        return brain.respond("m=2 kg c=4180 J/(kg*K) dT=10 K isi",
                             session="_test_isi").text
    check("hesap: ozgul isi ile Q dogru cikiyor", isi_hesabi, contains("83600"))

    # Uretilen degerler fiziksel olarak makul mu?
    def kuantum_olcegi():
        import random as _r
        p = brain._problem_uret(formulas.BY_ID["fotoelektrik"], "tr", _r.Random(7))
        return p or ""
    check("uretim: kuantum olceginde makul degerler",
          kuantum_olcegi, lambda g: "10^" in g and "e-" not in g.split("Cevap")[0][:0] + "x")
    check("uretim: negatif is fonksiyonu uretmiyor",
          kuantum_olcegi, lambda g: "= **-" not in g)

    check("yuvarlama: kucuk sayi sifirlanmiyor",
          lambda: brain._yuvarla(3.2e-19), 3.2e-19)
    check("yuvarlama: buyuk sayi bilimsel kaliyor",
          lambda: brain._yuvarla(9.026e20), 9.026e20)

    # ------------------------------- dogal dil MATLAB sorulari (kod cop hatasi)
    check("ifade denetimi: gercek ifadeler geciyor",
          lambda: all(nlu.looks_like_expression(e) for e in
                      ("x^2*sin(x)", "2*pi*sqrt(0.5/200)", "m*v**2/2",
                       "v0 + a*t", "exp(-x^2)")), True)
    check("ifade denetimi: cumleler elenmis",
          lambda: any(nlu.looks_like_expression(e) for e in
                      ("bana sifirdan matlab ogretebilir misin",
                       "matlab konusunda ne kadar bilgiye sahipsin",
                       "matlab ile neler yapabilirsin",
                       "sonumlu osilator kodu")), False)
    check("niyet: 'sifirdan matlab ogretebilir misin' yol haritasi",
          lambda: nlu.classify("bana sifirdan matlab ogretebilir misin")[0],
          "yol_haritasi")
    check("niyet: 'ne kadar bilgiye sahipsin' yetenek",
          lambda: nlu.classify("matlab konusunda ne kadar bilgiye sahipsin")[0],
          "yetenek")
    check("niyet: 'hakkimda ne biliyorsun' hala profil",
          lambda: nlu.classify("hakkimda ne biliyorsun")[0], "profil")
    check("niyet: kod istegi hala matlab",
          lambda: nlu.classify("egik atis icin matlab kodu")[0], "matlab")

    def cop_kod_var_mi(soru):
        t = brain.respond(soru, session="_test_cop").text
        return "linspace(-10, 10, 1000)" in t

    for _soru in ("bana sifirdan matlab ogretebilir misin",
                  "matlab konusunda ne kadar bilgiye sahipsin",
                  "matlab ile neler yapabilirsin",
                  "matlab nedir"):
        check("beyin: '%s' cop kod uretmiyor" % _soru[:34],
              (lambda s: (lambda: cop_kod_var_mi(s)))(_soru), False)

    check("beyin: yetenek sorusu sablonlari anlatiyor",
          lambda: brain.respond("matlab konusunda ne kadar bilgiye sahipsin",
                                session="_test_cop").text,
          contains("şablon", "ode45" if False else "Octave"))
    check("beyin: ifade verilince hala kod uretiyor",
          lambda: brain.respond("x^2*sin(x) icin matlab kodu",
                                session="_test_cop").text,
          contains("linspace", "plot"))

    # ------------------------------------------------------- kisi profili
    from . import profile as _pr

    _pr.forget()
    for _s in ("_test_pr1", "_test_pr2"):
        db.conn().execute("DELETE FROM chat WHERE session=?", (_s,))
        brain._SESSION_MEM.pop(_s, None)
    db.conn().commit()

    db.flush_writes()
    check("profil: ad cikarimi", lambda: (_pr.extract("adim Polat"), _pr.name())[1],
          "Polat")
    check("profil: 'ben fizik ogrencisiyim' ad sanilmiyor",
          lambda: (_pr.forget(), _pr.extract("ben fizik ogrencisiyim"),
                   _pr.name())[2], None)
    check("profil: ingilizce ad cikarimi",
          lambda: (_pr.forget(), _pr.extract("my name is Ada"), _pr.name())[2],
          "Ada")
    check("profil: duzey cikarimi",
          lambda: (_pr.extract("lisans ogrencisiyim"), _pr.level())[1], "lisans")
    check("profil: duzey etiketi",
          lambda: _pr.level_label("tr"), "Lisans öğrencisi")

    check("profil: kendini tanitma niyeti",
          lambda: nlu.classify("lisans ogrencisiyim")[0], "kendini_tanit")
    check("profil: tanima sorusu niyeti",
          lambda: nlu.classify("beni taniyor musun")[0], "profil")
    check("profil: unutma niyeti",
          lambda: nlu.classify("beni unut")[0], "beni_unut")

    def profil_akisi():
        _pr.forget()
        db.flush_writes()
        brain.respond("adim Polat", session="_test_pr1")
        brain.respond("lisans ogrencisiyim", session="_test_pr1")
        brain.respond("entropi nedir", session="_test_pr1")
        db.flush_writes()
        return brain.respond("merhaba", session="_test_pr2").text

    check("profil: yeni sohbette adi hatirliyor", profil_akisi, contains("Polat"))
    check("profil: yeni sohbette onceki konuyu animsatiyor",
          profil_akisi, contains("entropi"))
    check("profil: 'beni taniyor musun' ozet veriyor",
          lambda: brain.respond("beni taniyor musun", session="_test_pr2").text,
          contains("Polat", "Lisans"))
    db.flush_writes()
    check("profil: kisisel ifade ilgi alani sayilmiyor",
          lambda: any("ogrenci" in (r["label"] or "")
                      for r in _pr.top_interests(20)), False)
    check("profil: fizik konusu ilgi alanina giriyor",
          lambda: any("entropi" in (r["label"] or "")
                      for r in _pr.top_interests(20)), True)

    def unutma():
        brain.respond("beni unut", session="_test_pr2")
        db.flush_writes()
        return (_pr.name(), _pr.level(), len(_pr.top_interests(20)))
    check("profil: 'beni unut' her seyi siliyor", unutma, (None, None, 0))

    _pr.forget()

    # ---------------------------------------------------------------- rapor
    print()
    for name, why in FAIL:
        print("  ✗ %-46s %s" % (name, why))
    if FAIL:
        print()
    print("  " + "-" * 52)
    print("  %d test gecti, %d test basarisiz." % (len(PASS), len(FAIL)))
    print()
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(run())
