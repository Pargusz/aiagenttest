# -*- coding: utf-8 -*-
"""FORMUL OGRENME: korpustan baginti cikarip MATEMATIKSEL olarak dogrulamak.

Kullanicinin istegi: *"bu öğrenmeyi formüllerde de dahil olacak şekilde
yapmalıyız ve neredeyse sıfır hata ile gerçekten öğrenip kendini
geliştirmeli"*.

Daha once duz metinden baginti cikarmayi IKI kez denedik ve IKI kez
kapattik (problemler.py `PDF_BAGINTI_CIKAR = False`, kopruogren.py
`PROZ_DENKLEM_CIKAR = False`). Cikan seyler sunlardi: `T = 15`,
`mol = 0`, `int = Q`, MATLAB kod parcalari, OCR kirintilari.

Neden basarisiz oldu? Cunku olcut "SymPy ayristirabiliyor mu" idi. `T = 15`
sorunsuz ayristirilir. Yani dogrulama, denklemin FIZIK olup olmadigini hic
sinamiyordu.

Bu dosya farkli bir olcut kullaniyor — BOYUT TUTARLILIGI:

    Bir denklem, sembollerinin fiziksel anlamlarinin TEK BIR yorumu
    altinda boyutsal olarak tutarliysa fiziktir; degilse degildir.

Ornek: `E = h*f`
  * E enerji (J) + h Planck (J·s) + f frekans (Hz) -> J = J·s/s ✓
  * E elektrik alan (V/m) ile ayni denklem -> ✗
  Tek yorum tutuyor: denklem gecerli VE E'nin burada enerji oldugunu
  ogrenmis oluyoruz. Boylece degisken tablosu da kendiliginden cikiyor.

Ornek: `T = 15`
  Tek sembol, saga sayi. Baginti degil, atama. Elenir.

Ornek: `mol = 0`
  "mol" bilinen bir sembol degil. Elenir.

Kabul icin bir adayin gecmesi gereken kapilar:

  1. Bicim      : iki tarafi var, en az iki AYRI sembol, sag taraf salt
                  sayi degil, uzunluk makul.
  2. Sembol     : her sembol ya bilinen bir fizik simgesi ya da sabit.
  3. Boyut      : sembollerin TEK bir yorumu altinda iki taraf ayni
                  boyutta (belirsizlik varsa reddedilir).
  4. Yenilik    : mevcut bir formulun ayni ya da duz cevrilmis hali degil.
  5. Sayisal    : geri yerine koyma sinavini gecer (dogrulama.py).
  6. Kanit      : en az iki BAGIMSIZ kaynakta gecer.

Alti kapiyi da gecen baginti canli formul tabanina katilir ve cozucude
kullanilir. Gecemeyen sessizce atilir — ogretilmez.
"""
import json
import re
import time

from . import db, dogrulama, formulas, units

# Kac bagimsiz kaynakta gecerse kabul edilir
_EN_AZ_KAYNAK = 2

# Denklem gibi gorunen parcalar. Iki tarafi da olan, makul uzunlukta.
_DENKLEM = re.compile(
    r"(?<![\w=<>!])([A-Za-zΑ-Ωα-ω][A-Za-zΑ-Ωα-ω0-9_]{0,7})\s*=\s*"
    r"([A-Za-zΑ-Ωα-ω0-9_\.\*\/\+\-\(\)\^ ]{2,48})(?![\w=])")

# Fizik disi baglamda gecen "denklemler" (kod, tablo, kunye)
_KOD_IZI = re.compile(
    r"\b(function|return|import|def |var |let |const |print|plot|"
    r"figure|subplot|for |while |if |else|end;|matlab|python|"
    r"doi|isbn|issn|http|www|table|figure \d|eq\.|ref\.)\b", re.I)


def _kur():
    c = db.conn()
    c.execute("""CREATE TABLE IF NOT EXISTS ogrenilen_formul(
        eq          TEXT PRIMARY KEY,
        degiskenler TEXT,
        kaynaklar   TEXT,
        kanit       INTEGER DEFAULT 0,
        dogrulandi  INTEGER DEFAULT 0,
        neden       TEXT,
        at          REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS formul_aday(
        eq      TEXT PRIMARY KEY,
        kaynak  TEXT,
        sayi    INTEGER DEFAULT 1,
        at      REAL
    )""")
    c.commit()


# ── 1. Sembol sozlugu: hangi simge hangi fiziksel buyukluk olabilir ────────

_SEMBOL = {"tablo": None}


def sembol_secenekleri():
    """Her simge icin olasi (birim, boyut, ad) secenekleri.

    Kaynak: dogrulanmis 200+ cekirdek formulun kendi degisken tablolari.
    Bir simge birden fazla buyuklugu gosterebilir (E enerji ya da elektrik
    alan); hepsini secenek olarak tutuyoruz, karari BOYUT verecek.
    """
    if _SEMBOL["tablo"] is not None:
        return _SEMBOL["tablo"]
    tablo = {}
    for f in formulas.FORMULAS:
        if f.get("uretilmis"):
            continue                      # yalnizca cekirdek, dongu olmasin
        for s, (tr, en, u) in (f.get("vars") or {}).items():
            p = units.parse_unit(u or "")
            if not p:
                continue
            boyut = tuple(p[1])
            tablo.setdefault(s, {})
            # Ayni boyut birden cok adla gelebilir; ilk adi saklariz.
            # Turkce VE Ingilizce ad birlikte tutulur: kaynak metinler
            # cogunlukla Ingilizce ve baglam eslesmesi yalniz Turkce adla
            # yapilinca hic tutmuyordu (olculdu: "photon energy ...
            # Planck constant" metni yorumu ayirt edemiyordu).
            tablo[s].setdefault(boyut, (u, tr, en))
    _SEMBOL["tablo"] = tablo
    return tablo


_SABIT_BIRIM = {
    "c": "m/s", "h": "J*s", "hbar": "J*s", "k_B": "J/K", "kB": "J/K",
    "G": "N*m**2/kg**2", "e": "C", "eps0": "F/m", "mu0": "H/m",
    "N_A": "1/mol", "R": "J/(mol*K)", "sigma": "W/(m**2*K**4)",
    "g": "m/s**2",
}


def _sembol_boyutlari(s):
    """Bir simgenin olasi boyutlari: [(boyut, birim, tr_ad, en_ad), ...]"""
    out = []
    tablo = sembol_secenekleri()
    for boyut, (u, tr, en) in (tablo.get(s) or {}).items():
        out.append((boyut, u, tr, en or tr))
    if not out and s in _SABIT_BIRIM:
        p = units.parse_unit(_SABIT_BIRIM[s])
        if p:
            out.append((tuple(p[1]), _SABIT_BIRIM[s], s, s))
    return out


# ── 2. Aday cikarma ────────────────────────────────────────────────────────

def aday_denklemler(metin):
    """Metinden denklem gibi duran parcalari cikar."""
    if not metin or _KOD_IZI.search(metin):
        return []
    out = []
    for sol, sag in _DENKLEM.findall(metin):
        sag = sag.strip().rstrip(".,;:")
        if not sag:
            continue
        eq = "%s = %s" % (sol.strip(), sag)
        if _bicim_uygun(eq):
            out.append(eq)
    return out


def _semboller(ifade):
    return set(re.findall(r"(?<![\w])([A-Za-zΑ-Ωα-ω][A-Za-zΑ-Ωα-ω0-9_]{0,7})",
                          ifade))


def _bicim_uygun(eq):
    """1. kapi: bicim. Baginti mi, atama mi, cop mu?"""
    sol, _, sag = eq.partition("=")
    sol, sag = sol.strip(), sag.strip()
    if not sol or not sag or len(eq) > 70:
        return False
    # Sag taraf salt sayi ise bu bir baginti degil, bir DEGERDIR.
    # Olculdu: eski cikarim `T = 15`, `mol = 0`, `f = 0` uretiyordu.
    if re.fullmatch(r"[\d\.\,\s\+\-]*", sag):
        return False
    simgeler = _semboller(sol) | _semboller(sag)
    if len(simgeler) < 2:
        return False
    # Fonksiyon adlari denklem degil
    if re.match(r"^(sin|cos|tan|exp|log|ln|max|min|sum|int|lim|def|"
                r"eq|fig|ref|table|no|vs)$", sol, re.I):
        return False
    return True


# ── 3. Boyut kapisi: denklemin TEK tutarli yorumu var mi ──────────────────

def _formul_kaydi(eq, atama):
    """Boyut denetimine verilecek gecici formul kaydi."""
    varlar = {}
    for s, deger in atama.items():
        u, tr, en = deger if len(deger) == 3 else (deger[0], deger[1], deger[1])
        varlar[s] = (tr, en, u)
    return {"id": "_aday", "tr": "aday", "en": "candidate",
            "eq": eq, "vars": varlar, "topic": "aday",
            "kw_tr": "", "kw_en": "", "note_tr": "", "note_en": ""}


_BIRLIKTELIK = {"tablo": None}


def birliktelik_tablosu():
    """Hangi BUYUKLUKLER ayni bagintida birlikte gecer?

    Kullanicinin uyarisi yerinde: bir denklemi simge simge okumak yanlis.
    `E = h*f` denklemi tek basina hem "foton enerjisi" (E enerji, h Planck,
    f frekans) hem de "is = kuvvet x yol" (E enerji, f surtunme kuvveti,
    h yukseklik) olarak okunabilir; ikisi de boyutsal olarak dogrudur.

    Karari BUTUN vermeli: bu uc buyukluk daha once ogrendigim
    bagintilarda birlikte geciyor mu? Enerji-Planck-frekans ucgeni
    cekirdekte defalarca birlikte gecer; enerji-yukseklik-surtunme
    kuvveti ucgeni gecmez. Tablo bunu sayiyla soyler.

    Anahtar: (boyut_a, boyut_b) ciftleri; deger: kac formulde birlikte.
    Simge degil BOYUT kullaniyoruz ki ayni buyukluk farkli harfle
    yazildiginda da tanisin.
    """
    if _BIRLIKTELIK["tablo"] is not None:
        return _BIRLIKTELIK["tablo"]
    tablo = {}
    for f in formulas.FORMULAS:
        boyutlar = []
        for _s, (_tr, _en, u) in (f.get("vars") or {}).items():
            p = units.parse_unit(u or "")
            if p:
                boyutlar.append(tuple(p[1]))
        for i, x in enumerate(boyutlar):
            for y in boyutlar[i + 1:]:
                anahtar = (x, y) if x <= y else (y, x)
                tablo[anahtar] = tablo.get(anahtar, 0) + 1
    _BIRLIKTELIK["tablo"] = tablo
    return tablo


def _yorum_puani(atama, baglam=""):
    """Bir yorumun BUTUN olarak ne kadar tanidik oldugunu puanla.

    Iki kaynak:
      * Birliktelik: bu buyuklukler daha once ogrenilmis bagintilarda
        birlikte geciyor mu?
      * Baglam: kaynak metinde bu buyukluklerin adlari geciyor mu?
    """
    tablo = birliktelik_tablosu()
    boyutlar = []
    for s, deger in atama.items():
        p = units.parse_unit(deger[0] or "")
        if p:
            boyutlar.append(tuple(p[1]))
    puan = 0
    for i, x in enumerate(boyutlar):
        for y in boyutlar[i + 1:]:
            anahtar = (x, y) if x <= y else (y, x)
            puan += tablo.get(anahtar, 0)
    if baglam:
        bk = baglam.lower()
        for _s, deger in atama.items():
            # Turkce ve Ingilizce ad, ikisine de bakilir
            for ad in deger[1:]:
                if ad and len(ad) >= 4 and ad.lower() in bk:
                    puan += 25
                    break
    return puan


def yorumla(eq, en_fazla_secenek=64, baglam=""):
    """Denklemin boyutsal olarak tutarli TEK yorumunu bul.

    Doner: (atama, neden). Atama None ise neden aciklar.

    Bu, projenin "neredeyse sifir hata" sartinin kalbi. Bir denklem ancak
    sembollerine fiziksel anlam verilebiliyorsa ve o anlamlar altinda iki
    taraf ayni boyutta cikiyorsa fiziktir. Birden fazla yorum tutuyorsa
    denklem BELIRSIZDIR ve reddedilir — yanlis ogrenmektense hic
    ogrenmemek yeglenir.
    """
    simgeler = sorted(_semboller(eq.partition("=")[0]) |
                      _semboller(eq.partition("=")[2]))
    secenekler = []
    for s in simgeler:
        opts = _sembol_boyutlari(s)
        if not opts:
            return None, "bilinmeyen simge: %s" % s
        secenekler.append((s, opts))
    # Kombinasyon patlamasini onle
    toplam = 1
    for _s, opts in secenekler:
        toplam *= len(opts)
        if toplam > en_fazla_secenek:
            return None, "cok fazla yorum (%d+)" % toplam

    import itertools
    tutan = []
    for secim in itertools.product(*[opts for _s, opts in secenekler]):
        atama = {}
        for (s, _opts), (_boyut, u, tr, en) in zip(secenekler, secim):
            atama[s] = (u, tr, en)
        try:
            sonuc = dogrulama.boyut_denetimi(_formul_kaydi(eq, atama))
        except Exception:
            continue
        if sonuc.get("ok") is True:
            tutan.append(atama)
    if not tutan:
        return None, "boyutlar tutmuyor"
    if len(tutan) == 1:
        return tutan[0], ""

    # Birden fazla yorum boyutsal olarak tutuyor. Simge simge bakarak bunu
    # cozemeyiz; BUTUN bagintiya ve daha once ogrendiklerimize bakariz:
    # bu buyuklukler birlikte ne siklikta geciyor, kaynak metin hangisini
    # anlatiyor? Belirgin bir kazanan yoksa yine reddederiz — yanlis
    # ogrenmektense hic ogrenmemek yeglenir.
    puanli = sorted(((_yorum_puani(a, baglam), a) for a in tutan),
                    key=lambda x: -x[0])
    en_iyi, ikinci = puanli[0], puanli[1]
    if en_iyi[0] <= 0 or en_iyi[0] < ikinci[0] * 1.5 or \
            en_iyi[0] - ikinci[0] < 10:
        return None, "birden fazla yorum tutuyor (belirsiz)"
    return en_iyi[1], ""


# ── 4. Yenilik kapisi ──────────────────────────────────────────────────────

def _eq_nesnesi(eq_metni):
    """'a = b' metnini SymPy denklemine cevir.

    DIKKAT: formulas.parse ile ayni yolu kullanmak SART. Duz sympify,
    varsayimlari farkli semboller uretiyor ve `E - E` bile sifira
    sadelesmiyordu; bu yuzden `E = m*c**2` gibi zaten bilinen bir
    baginti "yeni" sayiliyordu (olculdu).
    """
    import sympy as sp
    sol, _, sag = (eq_metni or "").partition("=")
    if not sol.strip() or not sag.strip():
        return None
    syms = sorted(_semboller(sol) | _semboller(sag))
    return sp.Eq(formulas.parse(sol.replace("^", "**"), symbols=syms),
                 formulas.parse(sag.replace("^", "**"), symbols=syms))


def _yeni_mi(eq):
    """Mevcut bir formulun ayni ya da duz cevrilmis hali mi?

    DIKKAT: genisleme._ayni_mi SymPy DENKLEM NESNESI bekler, metin degil.
    Metinle cagirinca sessizce hep False donuyordu; yani `p = m*v` gibi
    zaten bilinen bagintilar "yeni" sayilip ogreniliyordu (olculdu).
    """
    from . import genisleme
    try:
        yeni = _eq_nesnesi(eq)
    except Exception:
        return False
    if yeni is None:
        return False
    for f in formulas.FORMULAS:
        try:
            mevcut = formulas.sympy_eq(f)
        except Exception:
            continue
        try:
            if genisleme._ayni_mi(yeni, mevcut):
                return False
        except Exception:
            continue
    return True


# ── 5-6. Tam dogrulama ─────────────────────────────────────────────────────

def dogrula(eq, kanit=0):
    """Alti kapinin hepsi. (kayit, neden) doner; kayit None ise reddedildi."""
    if not _bicim_uygun(eq):
        return None, "bicim uygun degil"
    atama, neden = yorumla(eq)
    if not atama:
        return None, neden
    if not _yeni_mi(eq):
        return None, "zaten bilinen baginti"
    kayit = _formul_kaydi(eq, atama)
    # Sayisal sinav: geri yerine koyma. Cozulemeyen ya da tutarsiz
    # denklem ogretilmez.
    try:
        gy = dogrulama.geri_yerine_koy(kayit)
        if gy.get("ok") is False:
            return None, "sayisal dogrulama basarisiz: %s" % gy.get("neden", "")
    except Exception as e:
        return None, "sayisal dogrulama yapilamadi: %s" % e
    if kanit < _EN_AZ_KAYNAK:
        return None, "yetersiz kaynak (%d)" % kanit
    return kayit, ""


# ── Korpustan ogrenme ──────────────────────────────────────────────────────

def aday_topla(limit=400):
    """Islenmemis makale ozetlerinden aday baginti topla."""
    _kur()
    c = db.conn()
    baslangic = int(db.get_state("formulogren_offset", 0) or 0)
    rows = c.execute(
        "SELECT id, title, abstract, url FROM papers "
        "WHERE abstract IS NOT NULL AND length(abstract) > 120 "
        "ORDER BY id LIMIT ? OFFSET ?", (limit, baslangic)).fetchall()
    if not rows:
        db.set_state("formulogren_offset", 0)      # bastan tara
        return 0
    n = 0
    for r in rows:
        kaynak = r["url"] or ("p%d" % r["id"])
        for eq in aday_denklemler(r["abstract"]):
            c.execute(
                "INSERT INTO formul_aday(eq, kaynak, sayi, at) "
                "VALUES(?,?,1,?) ON CONFLICT(eq) DO UPDATE SET "
                "sayi = sayi + 1, "
                "kaynak = CASE WHEN instr(kaynak, ?) = 0 "
                "THEN kaynak || char(10) || ? ELSE kaynak END",
                (eq, kaynak, time.time(), kaynak, kaynak))
            n += 1
    c.commit()
    db.set_state("formulogren_offset", baslangic + len(rows))
    return n


def _kaynak_sayisi(kaynak_metni):
    return len({x for x in (kaynak_metni or "").split("\n") if x.strip()})


def ogren(en_fazla=25):
    """Adaylari dogrulama kapilarindan gecir. (kabul, red) doner."""
    _kur()
    c = db.conn()
    rows = c.execute(
        "SELECT a.eq, a.kaynak FROM formul_aday a "
        "LEFT JOIN ogrenilen_formul o ON o.eq = a.eq "
        "WHERE o.eq IS NULL ORDER BY a.sayi DESC LIMIT ?",
        (en_fazla,)).fetchall()
    kabul, red = [], 0
    for r in rows:
        kanit = _kaynak_sayisi(r["kaynak"])
        kayit, neden = dogrula(r["eq"], kanit)
        if kayit:
            c.execute(
                "INSERT OR REPLACE INTO ogrenilen_formul"
                "(eq, degiskenler, kaynaklar, kanit, dogrulandi, neden, at) "
                "VALUES(?,?,?,?,1,'',?)",
                (r["eq"], json.dumps(kayit["vars"], ensure_ascii=False),
                 r["kaynak"], kanit, time.time()))
            kabul.append(kayit)
        else:
            red += 1
            c.execute(
                "INSERT OR REPLACE INTO ogrenilen_formul"
                "(eq, degiskenler, kaynaklar, kanit, dogrulandi, neden, at) "
                "VALUES(?,'',?,?,0,?,?)",
                (r["eq"], r["kaynak"], kanit, neden[:120], time.time()))
    c.commit()
    return kabul, red


def _kimlik(eq):
    """Formul icin kararli bir kimlik uret."""
    sade = re.sub(r"[^A-Za-z0-9]+", "_", eq).strip("_").lower()
    return "ogr_" + sade[:40]


def bagla():
    """Dogrulanan bagintilari canli formul tabanina kat."""
    _kur()
    c = db.conn()
    n = 0
    for r in c.execute("SELECT eq, degiskenler FROM ogrenilen_formul "
                       "WHERE dogrulandi = 1 AND kanit >= ?",
                       (_EN_AZ_KAYNAK,)):
        fid = _kimlik(r["eq"])
        if fid in formulas.BY_ID:
            continue
        try:
            varlar = {k: tuple(v) for k, v in
                      json.loads(r["degiskenler"] or "{}").items()}
        except Exception:
            continue
        if not varlar:
            continue
        ad = " ".join(v[0] for v in varlar.values())[:60]
        f = {"id": fid, "tr": "Ogrenilen baginti: " + ad,
             "en": "Learned relation: " + ad,
             "eq": r["eq"], "vars": varlar, "topic": "ogrenilen",
             "kw_tr": ad, "kw_en": ad,
             "note_tr": "Bu bağıntıyı okuduğum kaynaklardan çıkardım; "
                        "boyut denetimi ve sayısal doğrulamadan geçti.",
             "note_en": "Learned from sources; passed dimensional and "
                        "numerical verification.",
             "uretilmis": True, "ogrenilmis": True}
        formulas.FORMULAS.append(f)
        formulas.BY_ID[fid] = f
        n += 1
    if n:
        formulas._ARAMA_INDEKS = None
    return n


# ── Kendi cevaplarindan ogrenme ────────────────────────────────────────────
# Kullanicinin istegi: *"verdiği cevaplarla bile geliştirsin kendini"*.
#
# Cozucu bir problemi IKI formulu zincirleyerek cozdugunde, o zincir aslinda
# YENI bir bagintidir: "bu iki seyi bilirsen sunu bulursun". Rastgele formul
# ciftleri denemek yerine (genisleme.py bunu yapiyor) GERCEKTEN ise yaramis
# ciftleri birlestirmek cok daha isabetli: ikisi de dogrulanmis, ikisi de
# ayni problemde birlikte kullanilmis.

def zincir_kaydet(formul_idleri):
    """Bir cozumde birlikte kullanilan formulleri kaydet."""
    if not formul_idleri or len(formul_idleri) < 2:
        return 0
    _kur()
    c = db.conn()
    c.execute("""CREATE TABLE IF NOT EXISTS cozum_zinciri(
        idler TEXT PRIMARY KEY, sayi INTEGER DEFAULT 1,
        islendi INTEGER DEFAULT 0, at REAL)""")
    anahtar = "|".join(sorted(set(formul_idleri)))
    c.execute("INSERT INTO cozum_zinciri(idler, sayi, at) VALUES(?,1,?) "
              "ON CONFLICT(idler) DO UPDATE SET sayi = sayi + 1",
              (anahtar, time.time()))
    c.commit()
    return 1


def cevaptan_ogren(en_fazla=8):
    """Gercek cozumlerde birlikte kullanilan formulleri birlestir.

    Uretilen her baginti, korpustan gelenlerle AYNI kapilardan gecer:
    boyut denetimi, yenilik ve sayisal dogrulama. Kaynak sarti aranmaz —
    burada kanit, iki dogrulanmis formulun matematiksel bilesimidir.
    """
    from . import genisleme
    _kur()
    c = db.conn()
    try:
        rows = c.execute(
            "SELECT idler FROM cozum_zinciri WHERE islendi = 0 "
            "ORDER BY sayi DESC LIMIT ?", (en_fazla,)).fetchall()
    except Exception:
        return [], 0
    kabul, denendi = [], 0
    for r in rows:
        idler = [x for x in r["idler"].split("|") if x in formulas.BY_ID]
        c.execute("UPDATE cozum_zinciri SET islendi = 1 WHERE idler = ?",
                  (r["idler"],))
        for i, ida in enumerate(idler):
            for idb in idler[i + 1:]:
                a, b = formulas.BY_ID[ida], formulas.BY_ID[idb]
                ortak = set(a["vars"]) & set(b["vars"])
                for sym in ortak:
                    denendi += 1
                    try:
                        yeni = genisleme._bilesim_dene(a, b, sym)
                    except Exception:
                        yeni = None
                    if not yeni:
                        continue
                    kayit, neden = dogrula(yeni["eq"], kanit=_EN_AZ_KAYNAK)
                    if not kayit:
                        continue
                    c.execute(
                        "INSERT OR REPLACE INTO ogrenilen_formul"
                        "(eq, degiskenler, kaynaklar, kanit, dogrulandi, "
                        "neden, at) VALUES(?,?,?,?,1,'',?)",
                        (yeni["eq"],
                         json.dumps(kayit["vars"], ensure_ascii=False),
                         "cozum:%s+%s" % (ida, idb), _EN_AZ_KAYNAK,
                         time.time()))
                    kabul.append(kayit)
    c.commit()
    return kabul, denendi


def denetle():
    """Ogrenilen bagintilari YENIDEN dogrula; gecemeyeni dusur.

    Cekirdek formuller ya da birim tablosu degistiginde eski bir kabul
    gecersizlesebilir. Ogrenilmis bilgi de denetimden muaf degildir.
    """
    _kur()
    c = db.conn()
    dusen = 0
    for r in c.execute("SELECT eq, kanit FROM ogrenilen_formul "
                       "WHERE dogrulandi = 1").fetchall():
        kayit, neden = dogrula(r["eq"], r["kanit"] or 0)
        if kayit:
            continue
        # "zaten bilinen baginti" bir HATA degil: cekirdege sonradan
        # eklenmis olabilir. Yine de servisten cikariyoruz.
        c.execute("UPDATE ogrenilen_formul SET dogrulandi = 0, neden = ? "
                  "WHERE eq = ?", (("yeniden denetim: " + neden)[:120],
                                   r["eq"]))
        dusen += 1
    c.commit()
    return dusen


def durum():
    """(dogrulanan, reddedilen, bekleyen_aday) doner."""
    _kur()
    c = db.conn()
    try:
        ok = c.execute("SELECT COUNT(*) FROM ogrenilen_formul "
                       "WHERE dogrulandi = 1").fetchone()[0]
        red = c.execute("SELECT COUNT(*) FROM ogrenilen_formul "
                        "WHERE dogrulandi = 0").fetchone()[0]
        aday = c.execute(
            "SELECT COUNT(*) FROM formul_aday a LEFT JOIN ogrenilen_formul o "
            "ON o.eq = a.eq WHERE o.eq IS NULL").fetchone()[0]
    except Exception:
        ok = red = aday = 0
    return ok, red, aday


def red_nedenleri(limit=8):
    """Neden reddedildi? Ogrenmenin nerede takildigini gosterir."""
    _kur()
    c = db.conn()
    try:
        return [(r["neden"], r["n"]) for r in c.execute(
            "SELECT neden, COUNT(*) AS n FROM ogrenilen_formul "
            "WHERE dogrulandi = 0 AND neden <> '' "
            "GROUP BY neden ORDER BY n DESC LIMIT ?", (limit,))]
    except Exception:
        return []
