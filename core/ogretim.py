# -*- coding: utf-8 -*-
"""Profesor gibi anlatim: yapilandirilmis ders cevabi.

Bir sey "anlatmak" ile "tanimini soylemek" ayni sey degildir. Iyi bir
ogretmen sirasiyla su adimlari izler:

    1. Kisa ve dogru tanim
    2. Sezgi — bunu neden umursuyoruz, gunluk hayatta nerede
    3. Nicel cerceve — hangi formul, degiskenleri ne
    4. Cozumlu ornek — sayilarla
    5. Yaygin hata — ogrencinin tam da burada yanildigi yer
    6. Nereden devam edilir + kaynaklar

Buradaki her parca DOGRULANMIS malzemeden gelir: tanim cekirdek konu
anlatimindan ya da okunmus kaynaktan, formul dogrulanmis tabandan (boyut
denetimi + geri yerine koyma gecmis), ornek SymPy ile hesaplanir. Dil
modeli yalnizca baglayici cumleleri yazar; sayi ve formul uretmez.
"""
import random
import re

from . import formulas, knowledge, units


# Birime gore TIPIK buyuklukler. Rastgele 2-50 arasi sayi vermek cogu
# nicelikte fizik disi ornek uretiyor: "dp = 25 kg·m/s" bir tasin
# momentumu kadar, kuantum belirsizligi icin anlamsiz; "dPhi = 50 Wb"
# devasa bir aki. Ogretmen gercekci mertebe secer.
TIPIK = {
    "m": 2.0, "cm": 20.0, "km": 5.0,
    "kg": 1.5, "g": 200.0,
    "s": 2.0, "ms": 50.0,
    "m/s": 10.0, "m/s^2": 3.0, "km/s": 8.0,
    "n": 20.0, "j": 150.0, "w": 60.0, "pa": 1.0e5, "atm": 1.0,
    "k": 300.0, "°c": 25.0, "c": 25.0,
    "v": 12.0, "a": 2.0, "ohm": 100.0, "ω": 100.0,
    "f": 1.0e-6, "h": 0.1, "t": 0.5, "wb": 0.02,
    "hz": 50.0, "rad/s": 20.0, "rad": 0.5, "derece": 30.0,
    "m^3": 0.02, "m^2": 0.5, "kg/m^3": 1000.0,
    "mol": 1.0, "j/k": 5.0, "j/(kg·k)": 4186.0,
    "kg·m/s": 3.0, "kg·m^2": 0.4, "n·m": 25.0, "n/m": 200.0,
    "1/m": 1.0e6, "1/s": 100.0,
}

# Kuantum olcegi: formulde bu sabitlerden biri geciyorsa mikro degerler
KUANTUM_SABIT = {"hbar", "h", "me", "mp", "e_", "qe", "kB", "Rinf", "a0"}
KUANTUM_TIPIK = {
    "kg": 9.109e-31,        # elektron kutlesi mertebesi
    "kg·m/s": 1.0e-24,      # atom altı momentum
    "m": 1.0e-10,           # atom capi mertebesi
    "j": 1.6e-19,           # elektronvolt mertebesi
    "m/s": 1.0e6,           # atomdaki elektron hizi
}


def _tipik_deger(birim, kuantum, varsayilan):
    b = (birim or "").strip().lower()
    if kuantum and b in KUANTUM_TIPIK:
        return KUANTUM_TIPIK[b]
    return TIPIK.get(b, varsayilan)


def _oku(x):
    """Sayiyi okunakli yaz: kucuk/buyuk mertebelerde bilimsel gosterim."""
    a = abs(x)
    if a and (a < 1e-3 or a >= 1e6):
        us = "%.4e" % x
        taban, kuvvet = us.split("e")
        return "%s×10^%d" % (taban.rstrip("0").rstrip("."), int(kuvvet))
    return "%.4g" % x


def _sabit_uyar(f, sym, kayit):
    """Bu sembol gercekten o fiziksel sabit mi?

    "c" hem isik hizi hem ozgul isi olabiliyor; ad/aciklama ortusmesi
    aranmadan sabit degeri kullanilamaz.
    """
    ad = (f["vars"][sym][0] + " " + f["vars"][sym][1]).lower()
    aciklama = (kayit[3] + " " + kayit[4]).lower()
    ortak = {w for w in ad.split() if len(w) > 3} & {
        w for w in aciklama.split() if len(w) > 3}
    return bool(ortak) or "sabit" in ad or "constant" in ad


def _formul_ornegi(f, lang="tr"):
    """Formulden gercekten hesaplanmis bir ornek uret.

    Sayilar SymPy ile cozulur; uydurulmaz.
    """
    syms = list(f["vars"].keys())
    if len(syms) < 2:
        return None
    # Fiziksel SABITLER serbest degisken degildir: hbar'a 10 J·s vermek
    # ogrenciye yanlis fizik ogretir. Sabitler gercek degerini alir ve
    # hedef olarak secilmez.
    sabit_degerler = {}
    for sym in syms:
        kayit = units.CONSTANTS.get(sym)
        if kayit and _sabit_uyar(f, sym, kayit):
            sabit_degerler[sym] = float(kayit[0])
    serbest = [x for x in syms if x not in sabit_degerler]
    if len(serbest) < 2:
        return None
    hedef = serbest[0]
    rng = random.Random(hash(f["id"]) & 0xFFFF)
    kuantum = bool(set(syms) & KUANTUM_SABIT)
    bilinen = dict(sabit_degerler)
    for s in serbest[1:]:
        birim = f["vars"][s][2]
        bilinen[s] = _tipik_deger(
            birim, kuantum, float(rng.choice([2, 3, 5, 10, 20])))
    try:
        _t, cozumler, _e = formulas.solve_for(f, bilinen, target=hedef)
    except Exception:
        return None
    gercel = [x for x in cozumler if isinstance(x, float)]
    if not gercel:
        return None
    deger = gercel[0]
    # Kuantum ve astronomi olcekleri mesrudur: hbar gercek degerini
    # alinca sonuc 10^-35 mertebesine iniyor ve eski suzgec ornegi
    # tamamen eliyordu. Yalnizca gercekten anlamsiz buyuklukler elenir.
    if not (1e-45 < abs(deger) < 1e45):
        return None

    ad = lambda s: (f["vars"][s][0] if lang == "tr" else f["vars"][s][1])
    birim = lambda s: f["vars"][s][2]
    satirlar = []
    satirlar.append("**" + ("Çözümlü örnek" if lang == "tr"
                            else "Worked example") + "**")
    satirlar.append("")
    verilenler = ", ".join(
        "%s = %s %s" % (s, _oku(v), birim(s)) for s, v in bilinen.items())
    satirlar.append(("Diyelim ki %s. O hâlde:" if lang == "tr"
                     else "Suppose %s. Then:") % verilenler)
    satirlar.append("")
    satirlar.append("```")
    satirlar.append("%s" % f["eq"])
    satirlar.append("%s = %s" % (hedef, units.fmt_exact(deger)
                                 if hasattr(units, "fmt_exact") else deger))
    satirlar.append("```")
    satirlar.append("")
    satirlar.append(("Yani %s **%s %s** çıkar." if lang == "tr"
                     else "So %s is **%s %s**.")
                    % (ad(hedef), _oku(deger), birim(hedef)))
    return "\n".join(satirlar)


# Konuya gore yaygin hatalar. Elle yazilmis: bir ogrencinin nerede
# yanildigini korpustan cikaramayiz, ama ogretmen bilir.
YAYGIN_HATA = {
    "kinematik": ("Hız ile ivmeyi karıştırmak. Hız sıfırken ivme sıfır "
                  "olmak zorunda değildir — yukarı atılan topun en tepe "
                  "noktasında hızı sıfırdır ama ivmesi hâlâ g'dir.",
                  "Confusing velocity with acceleration."),
    "dinamik": ("Kuvveti hızın sebebi sanmak. Kuvvet **ivmenin** sebebidir; "
                "sabit hızla giden cisme etkiyen net kuvvet sıfırdır.",
                "Thinking force causes velocity rather than acceleration."),
    "enerji": ("Enerjiyi kuvvetle karıştırmak. Kuvvet bir etkileşimdir, "
               "enerji ise iş yapabilme kapasitesidir; birimleri bile "
               "farklıdır (N ve J).",
               "Confusing force with energy."),
    "termodinamik": ("Isı ile sıcaklığı aynı sanmak. Isı **aktarılan "
                     "enerjidir**, sıcaklık ise moleküllerin ortalama "
                     "kinetik enerjisinin ölçüsüdür. Hal değişimi "
                     "sırasında ısı verilir ama sıcaklık değişmez.",
                     "Confusing heat with temperature."),
    "elektrik": ("Akım ile gerilimi karıştırmak. Gerilim bir potansiyel "
                 "farkıdır (itici sebep), akım ise akan yük miktarıdır "
                 "(sonuç).",
                 "Confusing current with voltage."),
    "dalga": ("Dalga hızını parçacık hızıyla karıştırmak. Suda dalga "
              "ilerlerken su molekülleri ilerlemez, yerinde salınır.",
              "Confusing wave speed with particle speed."),
    "optik": ("Görüntünün merceğin 'içinde' oluştuğunu sanmak. Görüntü "
              "ışınların kesiştiği yerde oluşur; gerçek görüntü perdeye "
              "düşürülebilir, sanal görüntü düşürülemez.",
              "Assuming the image forms inside the lens."),
    "kuantum": ("Belirsizlik ilkesini 'ölçüm aletimiz yetersiz' diye "
                "anlamak. Bu bir alet sorunu değil, doğanın kendi "
                "sınırıdır.",
                "Reading the uncertainty principle as a measurement flaw."),
    "gorelilik": ("Zaman genlemesini 'saat bozuluyor' sanmak. Bozulan saat "
                  "değil, zamanın kendisi gözlemciye göre farklı akıyor.",
                  "Thinking clocks malfunction rather than time differing."),
    "akiskan": ("Bernoulli denklemini her yerde geçerli sanmak. Yalnızca "
                "sürtünmesiz, sıkıştırılamaz akışta ve **tek bir akım "
                "çizgisi boyunca** geçerlidir.",
                "Applying Bernoulli outside a single streamline."),
    "nukleer": ("Yarı ömrün değiştirilebileceğini sanmak. Sıcaklık, basınç "
                "veya kimyasal işlem bozunma hızını etkilemez.",
                "Thinking half-life can be altered."),
    "astro": ("Işık yılını zaman birimi sanmak. Işık yılı bir **uzaklık** "
              "birimidir.", "Treating the light-year as a unit of time."),
    "katihal": ("Yarıiletkenin direncinin metal gibi davrandığını sanmak. "
                "Metalde sıcaklık artınca direnç artar, yarıiletkende "
                "azalır.",
                "Assuming semiconductors behave like metals."),
    "plazma": ("Plazmayı 'çok sıcak gaz' sanmak. Belirleyici olan sıcaklık "
               "değil, iyonlaşma ve kolektif davranıştır.",
               "Treating plasma as merely a hot gas."),
}


def ders_ver(sorgu, lang="tr", detay=False):
    """Konuyu profesor gibi, yapilandirilmis bicimde anlat.

    Malzeme bulunamazsa None doner (cagiran normal yola devam eder).
    """
    tr = lang == "tr"
    L = lambda a, b: a if tr else b

    # Turkce cekim eki aramayi bozuyor: "termodinamigin ikinci yasasini
    # anlat" hicbir konuya ulasmiyordu (olculdu: ogretim kapsami %78).
    # Sorgunun kok adaylariyla genisletilmis bicimini de deniyoruz.
    from . import turkce as _tr_kok
    # Genel kelimeler ("teori", "yasa", "kavram") genisletilirse sorgu
    # anlamini kaybediyor: "izafiyet teorisi nedir" -> "teori" koku
    # "Ideal Gaz ve Kinetik Teori" konusunu one cikariyordu (olculdu).
    # Yalnizca ayirt edici kelimeler genisletilir.
    _GENEL_KELIME = {"teori", "teorisi", "teorik", "yasa", "yasasi",
                     "yasalari", "ilke", "ilkesi", "kavram", "kavrami",
                     "nedir", "anlat", "ogret", "aciklar", "misin",
                     "nasil", "neden", "konu", "konusu", "hakkinda",
                     "temelleri", "temel"}
    import re as _re_kok
    _parcalar = []
    for _w in _re_kok.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]+", sorgu):
        _parcalar.append(_w)
        if _w.lower() in _GENEL_KELIME or len(_w) < 6:
            continue
        for _aday in _tr_kok.kokler(_w):
            if _aday not in _parcalar:
                _parcalar.append(_aday)
    genis_sorgu = " ".join(_parcalar)

    def _en_iyi(arama_fn, esik=25):
        """Once HAM sorgu; yetersizse kok-genisletilmis bicim.

        Genisletilmis bicim yedektir, rakip degil: "izafiyet teorisi nedir"
        sorgusunda genisletme "teori" kokunu ekliyor ve "Ideal Gaz ve
        Kinetik Teori" konusunu one cikariyordu (olculdu). Ham sorgu
        yeterince iyiyse ona dokunmuyoruz.
        """
        ham = arama_fn(sorgu, limit=4)
        if ham and ham[0][0] >= esik:
            return ham
        genis = arama_fn(genis_sorgu, limit=4)
        if genis and (not ham or genis[0][0] > ham[0][0]):
            return genis
        return ham or []

    # 1) Cekirdek konu anlatimi
    konu_vurusu = _en_iyi(knowledge.search)
    # Konu ADI sorguda gectiyse o konu one alinir: "Noether teoremini
    # turet" sorusunda "Simetriler ve Korunum" konusu daha yuksek puan
    # aliyordu, oysa kullanici Noether'i adiyla sordu.
    if konu_vurusu:
        from .learner import normalize as _nn
        _q = _nn(sorgu)
        _qs = [w for w in _q.split() if len(w) > 3]
        for _s, _k in knowledge.search(sorgu, limit=5):
            _ad = [w for w in _nn(_k["tr_title"]).split() if len(w) > 4]
            if not _ad:
                continue
            # Olculdu: eski olcut "baslik kelimelerinden BIRI sorguda
            # geciyorsa" idi ve iki ayri hata uretiyordu. (a) "Enerjinin
            # Korunumu" basligi "kinetik enerji nedir" sorgusunda
            # tutmuyordu, cunku "enerjinin" duz alt dizi olarak sorguda
            # yok. (b) Tek kelime yetince "Ideal Gaz ve Kinetik Teori"
            # yalnizca "kinetik" yuzunden one cikiyordu. Simdi kok
            # karsilastirmasi yapiliyor ve baslugun AYIRT EDICI tum
            # kelimeleri sorguda adiyla geciyorsa one aliniyor —
            # yani kullanici konuyu gercekten adiyla sormussa.
            tutan = sum(1 for w in _ad
                        if any(w[:5] == x[:5] for x in _qs))
            if tutan == len(_ad):
                konu_vurusu = [(max(_s, konu_vurusu[0][0] + 1), _k)]
                break
    konu_skoru = konu_vurusu[0][0] if konu_vurusu else 0
    konu_ham = konu_vurusu[0][1] if konu_vurusu else None
    konu = konu_ham if konu_skoru >= 25 else None

    # 2) Ilgili dogrulanmis formuller
    formul_ham = _en_iyi(formulas.search)
    formul_skoru = formul_ham[0][0] if formul_ham else 0
    # Esik 30'du; "tork nedir nasil hesaplanir" (23) ve "basit harmonik
    # hareket" (26) gibi mesru sorular formulsuz kaliyor, ders de
    # uretilemiyordu. 20 hala gercek bir anahtar kelime eslesmesi demek.
    formul_vuruslari = [f for skor, f in formul_ham
                        if skor >= 20 and not f.get("uretilmis")]
    if not konu and not formul_vuruslari:
        return None

    # BASLIK ile TANIM ayni kaynaktan gelmeli. Cekirdek konular genis
    # ("Termodinamigin Yasalari"), soru ise dar olabiliyor ("entropi nedir").
    # Genis konunun govdesini dar bir baslikla birlestirmek uyumsuz metin
    # uretiyordu: "Entropi degisimi" basligi altinda sifirinci yasa anlatimi.
    # Cozum: cekirdek konu ancak SORULAN sey oysa kullanilir.
    from .learner import normalize as _n
    _qk = [w for w in _n(sorgu).split() if len(w) > 3]
    _bk = ([w for w in _n(konu_ham["tr_title"] + " "
                          + konu_ham["en_title"]).split()
            if len(w) > 3] if konu_ham else [])
    # Baslik eslesmesi ESIKTEN BAGIMSIZ degerlendirilir: "gorelilik teorisi
    # nedir" sorusunda konu skoru 12'de kaliyor ama baslik ("Ozel Gorelilik")
    # birebir tutuyor. Bu durumda sorulan sey konudur, formul degil.
    konu_uygun = bool(_bk) and any(w[:5] == q[:5] for w in _bk for q in _qk)
    # Kismi baslik eslesmesi tek basina yetmez: "kinetik enerji nedir"
    # sorusu "Enerjinin Korunumu" konusunu yalnizca "enerji" yuzunden
    # tutuyor, oysa sorulan sey dogrulanmis "Kinetik enerji" formulunun
    # ta kendisi. Olcut PUAN DEGIL, ADLANDIRMA: kullanici formulun adini
    # tam olarak yazdiysa ve konunun adini yalnizca kismen yazdiysa,
    # sorulan sey dar buyukluktur.
    #
    # Puan orani denendi ve yanlis cikti: "izafiyet teorisi nedir"
    # sorusunda "Lorentz carpani" formulu daha yuksek puan aliyor ama
    # kullanici Lorentz'i hic anmamis; dogru cevap Ozel Gorelilik
    # konusudur (olculdu).
    if konu_uygun and konu_ham and formul_vuruslari:
        _bd = [w for w in _n(konu_ham["tr_title"] if tr
                             else konu_ham["en_title"]).split() if len(w) > 3]
        _konu_tam = bool(_bd) and all(
            any(w[:5] == q[:5] for q in _qk) for w in _bd)
        _f0 = formul_vuruslari[0]
        _fd = [w for w in _n(_f0["tr"] if tr else _f0["en"]).split()
               if len(w) > 3]
        _formul_tam = bool(_fd) and all(
            any(w[:5] == q[:5] for q in _qk) for w in _fd)
        if _formul_tam and not _konu_tam:
            konu_uygun = False

    # Baslik tutmasa bile kullanici konunun KENDI cok kelimeli anahtarini
    # yazmis olabilir. Olculdu: "aksiyon potansiyeli nedir" sorusu
    # "Elektrik potansiyeli" formulune gidiyordu — formul yalnizca
    # "potansiyeli" kelimesini tutuyor, "aksiyon"u hic karsilamiyordu.
    # Olcut: konunun anahtar OBEGI sorguda birebir geciyorsa ve o obekte
    # formulun karsilamadigi ayirt edici bir kelime varsa, sorulan sey
    # konudur. "kinetik enerji nedir" gibi durumlarda formul obegin tum
    # kelimelerini karsiladigi icin bu kural devreye girmez.
    if not konu_uygun and konu_ham and konu_skoru >= 25:
        _fkeliem = set()
        if formul_vuruslari:
            _f0 = formul_vuruslari[0]
            _fmetin = " ".join([_f0["tr"], _f0["en"]]
                               + list(_f0.get("kw_tr", []))
                               + list(_f0.get("kw_en", [])))
            _fkeliem = set(_n(_fmetin).split())
        # Tire, kelime ayiraci sayilmali: "Bose-Einstein condensation"
        # sorgusu "bose einstein condensation" anahtarina oturmuyordu ve
        # cevap "Kutle-enerji esdegerligi" formulune gidiyordu (olculdu).
        _qn = re.sub(r"[-–—/]", " ", _n(sorgu))
        _qn = re.sub(r"\s+", " ", _qn)
        for _kw in konu_ham["kw"]:
            _k = _n(_kw).strip()
            if " " not in _k:
                continue
            if not re.search(r"(?<!\w)%s\w{0,3}(?!\w)" % re.escape(_k), _qn):
                continue
            # Uzunluk esigi 3'tu; "zar potansiyeli" obeginde ayirt edici
            # kelime tam da "zar" oldugu icin obek elenip soru "Elektrik
            # potansiyeli" formuluine gidiyordu (olculdu).
            if any(w not in _fkeliem for w in _k.split() if len(w) > 2):
                konu_uygun = True
                break

    if konu_uygun:
        konu = konu_ham

    lines = []
    if konu_uygun:
        baslik = konu["tr_title"] if tr else konu["en_title"]
    elif formul_vuruslari:
        baslik = formul_vuruslari[0]["tr"] if tr else formul_vuruslari[0]["en"]
        konu = None                  # genis konu govdesini kullanma
    else:
        baslik = konu["tr_title"] if tr else konu["en_title"]
    lines.append("### %s" % baslik)
    lines.append("")

    # ── 1. Tanim ────────────────────────────────────────────────────────
    if not konu and formul_vuruslari:
        # Konu govdesi yoksa tanimi formulun fiziksel anlam notu verir;
        # bu notlar elle yazilmis ve dogrulanmistir.
        ilk = formul_vuruslari[0]
        not_ = ilk.get("note_tr" if tr else "note_en")
        if not_:
            lines.append(not_)
            lines.append("")
    if konu:
        govde = (konu["tr"] if tr else konu["en"]).strip()
        # Tanim konunun BASINDADIR. Cumle bolucu markdown basliklarini
        # ortadan kesiyordu ("**0. Yasa:**" -> "Yasa:** A ile B..."), bu
        # yuzden paragraf duzeyinde aliyoruz.
        paragraflar = [x.strip() for x in govde.split("\n\n") if x.strip()]
        acilis = []
        for par in paragraflar:
            acilis.append(par)
            if sum(len(x) for x in acilis) > (700 if detay else 420):
                break
        lines.append("\n\n".join(acilis) if acilis else govde[:600])
        lines.append("")

    # ── 2. Nicel cerceve ────────────────────────────────────────────────
    # Formul tabaninda karsiligi olmayan konularin (Noether, Stern-Gerlach,
    # alan kurami...) KENDI bagintilari ve ornekleri vardir; ders anlatimi
    # bunlari kullanmiyordu ve o konularda yapisiz kaliyordu (olculdu:
    # kapsam 58 soruda %79).
    if konu and not formul_vuruslari and konu.get("eqs"):
        lines.append("**" + L("Bağıntılar", "Relations") + "**")
        lines.append("")
        for e in konu["eqs"][:5]:
            lines.append("- `%s`" % e)
        lines.append("")

    if formul_vuruslari:
        lines.append("**" + L("Hangi bağıntıyla çalışırız",
                              "The relation we work with") + "**")
        lines.append("")
        for f in formul_vuruslari[:2]:
            lines.append("`%s`  —  %s" % (f["eq"], f["tr"] if tr else f["en"]))
            for sym, (t, e, u) in f["vars"].items():
                lines.append("- `%s` = %s%s" % (sym, t if tr else e,
                                                (" [%s]" % u) if u else ""))
            not_ = f.get("note_tr" if tr else "note_en")
            # Not zaten tanim olarak yazildiysa tekrar etme
            if not_ and not_ not in "\n".join(lines):
                lines.append("")
                lines.append("> %s" % not_)
            lines.append("")

    # ── 3. Cozumlu ornek ────────────────────────────────────────────────
    if formul_vuruslari:
        ornek = _formul_ornegi(formul_vuruslari[0], lang)
        if ornek:
            lines.append(ornek)
            lines.append("")

    # Cekirdek konunun kendi cozumlu ornegi varsa o daha degerlidir
    if konu:
        ornekler = konu["ex_tr"] if tr else konu["ex_en"]
        if ornekler:
            # Baslik "Çözümlü örnek": bu bolum de sayilarla calisan bir
            # ornektir ve ogretim yapisinin parcasidir.
            lines.append("**" + L("Çözümlü örnek", "Worked example") + "**")
            lines.append("")
            lines.append(ornekler[0][:900])
            lines.append("")

    # ── Makalelerden turetilmis bilgi ───────────────────────────────────
    # Tek makalenin iddiasi degil, birden cok makalenin uzlastigi bilgi.
    # Kanit sayisi gosterilir ki kullanici agirligini bilsin.
    try:
        from . import sentezbilgi
        turetilmis = sentezbilgi.ara(sorgu, limit=3)
    except Exception:
        turetilmis = []
    if turetilmis:
        lines.append("**" + L("Okuduğum makalelerden çıkardığım",
                              "What I derived from the papers") + "**")
        lines.append("")
        for d in turetilmis:
            lines.append("- %s <span class='meta'>(%d bağımsız makale)</span>"
                         % ((d["ifade"] or "")[:260], d["kanit"]))
        lines.append("")

    # ── 4. Yaygin hata ──────────────────────────────────────────────────
    konu_etiketi = formul_vuruslari[0]["topic"] if formul_vuruslari else None
    hata = YAYGIN_HATA.get(konu_etiketi)
    # Formulun kendi notu zaten bir yanlis anlamayi duzeltiyorsa konu
    # genelindeki hatayi eklemek konuyu dagitiyor: Faraday yasasi
    # anlatiminda "akim ile gerilimi karistirmak" uyarisi alakasizdi.
    _not_var = any(f.get("note_tr" if tr else "note_en")
                   for f in formul_vuruslari[:1])
    if hata and not _not_var:
        lines.append("**" + L("Sık yapılan hata", "Common mistake") + "**")
        lines.append("")
        lines.append("⚠️ " + (hata[0] if tr else hata[1]))
        lines.append("")

    # ── 5. Nereden devam ────────────────────────────────────────────────
    devam = []
    if formul_vuruslari:
        devam.append(L("`%s` yazıp değerlerinizle hesaplatın"
                       % (formul_vuruslari[0]["tr"].lower() if tr
                          else formul_vuruslari[0]["en"].lower()),
                       "Ask me to compute it with your own numbers"))
        devam.append(L("`%s için matlab kodu` ile simülasyonunu görün"
                       % baslik.lower(), "Ask for MATLAB code"))
    devam.append(L("`%s hakkinda 10 soru uret` ile kendinizi sınayın" % baslik.lower(),
                   "Ask for practice problems"))
    lines.append("**" + L("Buradan nasıl devam edersiniz",
                          "Where to go next") + "**")
    lines.append("")
    for d in devam:
        lines.append("- " + d)

    return "\n".join(lines)
