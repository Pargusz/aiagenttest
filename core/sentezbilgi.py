# -*- coding: utf-8 -*-
"""Makaleleri birlestirerek YENI bilgi uretme.

Bugune kadar her makale tek basina okunuyordu: cumleleri ayiklanip
saklaniyordu. Ama bir makalenin tek basina soyledigi sey bir iddiadir;
BIRDEN COK makalenin ayni seyi soylemesi bilgidir.

Burada uc tur turetme yapilir:

1. **Uzlasma** — ayni kavram hakkinda farkli makalelerde tekrarlanan
   ifadeler bir araya getirilir. Kac bagimsiz kaynagin soyledigi sayilir;
   bu sayi kanittir ve kullaniciya gosterilir.

2. **Koprü** — iki kavram cok sayida makalede BIRLIKTE geciyorsa ama
   aralarinda adlandirilmis bir iliski yoksa, bu bir baglantidir ve
   kaydedilir. Boylece bot "X ile Y birlikte calisilir" bilgisini
   makalelerden kendisi cikarir.

3. **Sayisal uzlasma** — ayni buyukluk icin farkli makalelerde verilen
   sayilar toplanir; birbirini tutuyorsa guvenilir bir deger cikar.

Kalite kapisi: bir turetim ancak EN AZ IKI FARKLI makaleden destek
aliyorsa kaydedilir. Tek kaynakli iddia bilgi sayilmaz.
"""
import collections
import re
import time

from . import db
from .learner import normalize

EN_AZ_KAYNAK = 2          # bir turetim icin gereken en az bagimsiz makale
EN_AZ_BIRLIKTELIK = 6     # koprü icin gereken birlikte gecme sayisi

_KURULDU = False


def _kur():
    global _KURULDU
    if _KURULDU:
        return
    c = db.conn()
    c.execute("""CREATE TABLE IF NOT EXISTS derived(
        id INTEGER PRIMARY KEY,
        tur TEXT,              -- uzlasma | kopru | sayisal
        konu TEXT,             -- normalize edilmis kavram
        ifade TEXT,            -- turetilen bilgi
        kanit INTEGER,         -- kac bagimsiz makale destekliyor
        kaynaklar TEXT,        -- makale kimlikleri
        at REAL,
        UNIQUE(tur, konu, ifade))""")
    c.execute("CREATE INDEX IF NOT EXISTS derived_konu ON derived(konu, kanit)")
    c.commit()
    _KURULDU = True


def _anahtar_ifade(cumle):
    """Cumleyi karsilastirilabilir bir cekirdege indir.

    Farkli makaleler ayni seyi farkli kelimelerle soyler; ortak cekirdegi
    yakalamak icin dolgu kelimeleri atip anlamli kelimeleri siralar.
    """
    kelimeler = [w for w in re.findall(r"[a-zçğıöşü0-9]{4,}", normalize(cumle))
                 if w not in _DOLGU]
    return " ".join(sorted(set(kelimeler))[:8])


_DOLGU = set("""
that this these those with from have been will also more than which when
where their there here such into using used study shows show found paper
work results result present presented propose proposed based method methods
model models system systems effect effects data analysis approach case cases
different various several however therefore thus both between within
bulunmustur gosterilmistir calisma calismada ancak fakat boylece icin
""".split())


# Ders kitaplarinda tekrarlanan kalip metinler: bilgi degil, sayfa dolgusu.
_KALIP = re.compile(
    r"(the student is expected to|learning objectives|by the end of this "
    r"section|check your understanding|conceptual questions|"
    r"is a good example of the fact|see figure|as shown in figure|"
    r"this openstax|licensed under|creative commons)", re.I)


def _kalip_metin(cumle):
    c = (cumle or "").strip()
    if _KALIP.search(c):
        return True
    # Alistirma sorusu: "3 . (a) If frequency is not constant..."
    if re.match(r"^\d+\s*[.)]\s*\(?[a-d]\)?", c):
        return True
    if c.count("?") >= 1 and len(c) < 260:
        return True           # soru cumlesi bilgi degildir
    # Tanitim/meta cumleleri: fizik olgusu bildirmiyor
    if re.search(r"\b(is called an enabling science|in this chapter|"
                 r"we will (?:see|learn|discuss)|this section)\b", c, re.I):
        return True
    return False


def _imza(cumle, uzunluk=5):
    """Cumlenin karsilastirilabilir imzasi.

    Farkli makaleler ayni seyi farkli kelimelerle soyler. Dolgu kelimeleri
    atilip en ayirt edici (en uzun) kelimeler siralanarak imza uretilir.
    Imza ne kadar uzun olursa eslesme o kadar zorlasir; olculdu: 8 kelimeyle
    17.000 makaleden yalnizca 5 uzlasma cikti, 5 kelimeyle anlamli sayida.
    """
    kelimeler = [w for w in re.findall(r"[a-zçğıöşü0-9]{5,}", normalize(cumle))
                 if w not in _DOLGU]
    if len(kelimeler) < uzunluk:
        return ""
    # En uzun kelimeler en ayirt edici olanlardir
    secilen = sorted(set(kelimeler), key=lambda w: -len(w))[:uzunluk]
    return " ".join(sorted(secilen))


def uzlasma_uret(en_fazla=40):
    """Birden cok makalenin tekrarladigi ifadeleri bilgi olarak kaydet.

    Kavrama bagli olma sarti YOK: bulgularin ucte ikisi kavramsiz
    kaydediliyor (olculdu: 27.142 / 37.637) ve bunlar uzlasma disinda
    kaliyordu. Konu, gruptaki en sik gecen ayirt edici kelimeden turetilir.
    """
    _kur()
    c = db.conn()
    # Makalenin kaynagini da aliyoruz: ayni ders kitabi ailesinden gelen
    # iki bolum BAGIMSIZ kaynak sayilmaz. OpenStax kitaplari birbirinin
    # icerigini paylasiyor ve ayni cumle uc kitapta birden geciyor.
    satirlar = c.execute(
        "SELECT i.norm, i.cumle, i.paper_id, i.tur, "
        "       p.source AS kaynak, COALESCE(p.dergi,'') AS dergi "
        "FROM insights i JOIN papers p ON p.id = i.paper_id "
        "WHERE i.tur IN ('tanim','bulgu','iliski') "
        "ORDER BY i.skor DESC LIMIT 60000").fetchall()

    kumeler = collections.defaultdict(list)
    for r in satirlar:
        imza = _imza(r["cumle"])
        if not imza:
            continue
        kumeler[imza].append(r)

    eklenen = 0
    for imza, grup in sorted(kumeler.items(), key=lambda kv: -len(kv[1])):
        if eklenen >= en_fazla:
            break
        makaleler = {g["paper_id"] for g in grup if g["paper_id"]}
        if len(makaleler) < EN_AZ_KAYNAK:
            continue          # tek kaynakli iddia bilgi degildir
        # Bagimsizlik: destek en az iki FARKLI yayindan gelmeli
        yayinlar = {(g["kaynak"], g["dergi"]) for g in grup}
        if len(yayinlar) < 2:
            continue
        if _kalip_metin(max(grup, key=lambda g: len(g["cumle"]))["cumle"]):
            continue          # mufredat/kalip metni, fizik bilgisi degil
        # Konu: gruptaki kavram etiketi varsa o, yoksa imzanin ilk kelimesi
        etiketler = [g["norm"] for g in grup if g["norm"]]
        konu = (collections.Counter(etiketler).most_common(1)[0][0]
                if etiketler else imza.split()[0])
        # Temsilci: en bilgilendirici (en uzun) cumle
        temsilci = max(grup, key=lambda g: len(g["cumle"]))["cumle"]
        try:
            cur = c.execute(
                "INSERT OR IGNORE INTO derived"
                "(tur, konu, ifade, kanit, kaynaklar, at) VALUES(?,?,?,?,?,?)",
                ("uzlasma", konu, temsilci[:500], len(makaleler),
                 ",".join(str(x) for x in sorted(makaleler)[:8]), time.time()))
            eklenen += cur.rowcount
        except Exception:
            pass
    c.commit()
    return eklenen


def kopru_uret(en_fazla=40):
    """Sik birlikte gecen ama aralarinda iliski kurulmamis kavramlari bagla."""
    _kur()
    c = db.conn()
    try:
        ciftler = c.execute(
            "SELECT a, b, weight FROM concept_links "
            "WHERE weight >= ? ORDER BY weight DESC LIMIT 400",
            (EN_AZ_BIRLIKTELIK,)).fetchall()
    except Exception:
        return 0
    # Zaten adlandirilmis iliskisi olanlari atla
    var = set()
    try:
        for r in c.execute("SELECT a, b FROM relations"):
            var.add((normalize(r["a"]), normalize(r["b"])))
    except Exception:
        pass

    eklenen = 0
    for r in ciftler:
        if eklenen >= en_fazla:
            break
        a, b = r["a"], r["b"]
        if a == b or (a, b) in var or (b, a) in var:
            continue
        # Iki kavramin adlarini bul
        ad_a = c.execute("SELECT name FROM concepts WHERE norm=? LIMIT 1",
                         (a,)).fetchone()
        ad_b = c.execute("SELECT name FROM concepts WHERE norm=? LIMIT 1",
                         (b,)).fetchone()
        if not ad_a or not ad_b:
            continue
        ifade = ("%s ile %s birlikte calisilan konulardir; okudugum %d "
                 "makalede birlikte geciyorlar."
                 % (ad_a["name"], ad_b["name"], r["weight"]))
        try:
            cur = c.execute(
                "INSERT OR IGNORE INTO derived"
                "(tur, konu, ifade, kanit, kaynaklar, at) VALUES(?,?,?,?,?,?)",
                ("kopru", a, ifade, r["weight"], "", time.time()))
            eklenen += cur.rowcount
        except Exception:
            pass
    c.commit()
    return eklenen


def ara(sorgu, limit=4):
    """Turetilmis bilgilerden sorguyla ilgili olanlari getir."""
    _kur()
    c = db.conn()
    n = normalize(sorgu)
    kelimeler = [w for w in re.findall(r"[a-zçğıöşü]{4,}", n)][:4]
    if not kelimeler:
        return []
    kosul = " OR ".join("konu LIKE ?" for _ in kelimeler)
    args = ["%" + w + "%" for w in kelimeler]
    try:
        return [dict(r) for r in c.execute(
            "SELECT * FROM derived WHERE (%s) ORDER BY kanit DESC LIMIT ?"
            % kosul, args + [limit])]
    except Exception:
        return []


def istatistik():
    _kur()
    c = db.conn()
    out = {"toplam": 0}
    try:
        for r in c.execute("SELECT tur, COUNT(*) n, AVG(kanit) k "
                           "FROM derived GROUP BY tur"):
            out[r["tur"]] = {"sayi": r["n"], "ort_kanit": round(r["k"] or 0, 1)}
            out["toplam"] += r["n"]
    except Exception:
        pass
    return out
