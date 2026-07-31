# -*- coding: utf-8 -*-
"""Konusmadan ogrenme: bilgi bosluklarini yakala ve kapat.

Bot bugune kadar yalnizca internetten rastgele okuyarak ogreniyordu; ne
sorulduguna bakmiyordu. Oysa en degerli ogrenme sinyali kullanicinin
sorusudur: cevaplayamadigi ya da zayif cevapladigi her soru, tam olarak
neyi ogrenmesi gerektigini soyler.

Dongü:
  1. Her soru icin cevabin guclu mu zayif mi oldugu kaydedilir.
  2. Zayif kalan sorular "bosluk" olarak biriktirilir; ayni konu tekrar
     sorulursa onceligi artar.
  3. Ogrenme motoru bu bosluklari sirayla ele alir ve HEDEFLI arama yapar
     (Wikipedia + arXiv + ders kitabi), sonucu tabana yazar.
  4. Bosluk kapandiginda isaretlenir; kullanici ayni seyi tekrar sordugunda
     artik cevap vardir.

Boylece bot konustukca gercekten guclenir ve neyi bilmedigini bilir.
"""
import re
import time

from . import db
from .learner import normalize

# Bosluk sayilmasi icin gereken en az icerik kelimesi
EN_AZ_KELIME = 2
# Bir bosluk kac kez arastirildiktan sonra birakilir
EN_FAZLA_DENEME = 3

_KURULDU = False


def _kur():
    global _KURULDU
    if _KURULDU:
        return
    c = db.conn()
    c.execute("""CREATE TABLE IF NOT EXISTS gaps(
        id INTEGER PRIMARY KEY,
        norm TEXT UNIQUE,
        soru TEXT,
        terimler TEXT,
        lang TEXT,
        sayac INTEGER DEFAULT 1,
        deneme INTEGER DEFAULT 0,
        durum TEXT DEFAULT 'acik',
        ilk REAL, son REAL, kapanma REAL)""")
    c.execute("CREATE INDEX IF NOT EXISTS gaps_durum ON gaps(durum, sayac)")
    c.commit()
    _KURULDU = True


# Her soruda gecen, arama icin degersiz kelimeler
_DOLGU = set("""
nedir ne nasil neden hangi kac kadar icin ile ve veya bir bu su o ben sen
biz siz bana bize sana mi mu misin musun peki lutfen acaba yani ama fakat
soyle boyle daha cok az iyi kotu var yok olur olmaz gibi kadar sonra once
anlat aciklа acikla ogret goster ver soyle yaz bul hesapla cozer cozum
what how why which when where the a an of to in on for is are do does can
please tell me show explain about
""".split())


def _terimler(soru):
    """Sorudan arama terimlerini cikar."""
    kelimeler = []
    for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{3,}", normalize(soru)):
        if w in _DOLGU or w.isdigit():
            continue
        if w not in kelimeler:
            kelimeler.append(w)
    return kelimeler[:6]


def kaydet(soru, lang="tr", guclu=True):
    """Bir sorunun sonucunu kaydet. Zayif kalanlar bosluk olur."""
    terimler = _terimler(soru)
    if len(terimler) < EN_AZ_KELIME:
        return None            # "merhaba", "tesekkurler" — bosluk degil
    norm = " ".join(sorted(terimler))
    _kur()
    c = db.conn()
    simdi = time.time()
    if guclu:
        # Cevap guclu geldiyse acik bir bosluk varsa kapat
        c.execute("UPDATE gaps SET durum='kapandi', kapanma=? "
                  "WHERE norm=? AND durum='acik'", (simdi, norm))
        c.commit()
        return None
    c.execute(
        "INSERT INTO gaps(norm, soru, terimler, lang, sayac, ilk, son) "
        "VALUES(?,?,?,?,1,?,?) "
        "ON CONFLICT(norm) DO UPDATE SET sayac = gaps.sayac + 1, son = ?, "
        "durum = CASE WHEN gaps.durum='kapandi' THEN 'acik' ELSE gaps.durum END",
        (norm, soru[:300], " ".join(terimler), lang, simdi, simdi, simdi))
    c.commit()
    return norm


def oncelikli(limit=5):
    """En cok sorulan, hala acik bosluklar."""
    _kur()
    c = db.conn()
    return [dict(r) for r in c.execute(
        "SELECT * FROM gaps WHERE durum='acik' AND deneme < ? "
        "ORDER BY sayac DESC, son DESC LIMIT ?",
        (EN_FAZLA_DENEME, limit))]


def denendi(norm, basarili=False):
    _kur()
    c = db.conn()
    if basarili:
        c.execute("UPDATE gaps SET durum='ogrenildi', deneme = deneme + 1, "
                  "kapanma=? WHERE norm=?", (time.time(), norm))
    else:
        c.execute("UPDATE gaps SET deneme = deneme + 1 WHERE norm=?", (norm,))
    c.commit()


def istatistik():
    _kur()
    c = db.conn()
    say = {}
    for r in c.execute("SELECT durum, COUNT(*) n FROM gaps GROUP BY durum"):
        say[r["durum"]] = r["n"]
    toplam = sum(say.values())
    return {
        "toplam": toplam,
        "acik": say.get("acik", 0),
        "ogrenildi": say.get("ogrenildi", 0),
        "kapandi": say.get("kapandi", 0),
    }


def rapor(lang="tr"):
    """Kullaniciya gosterilecek ozet."""
    s = istatistik()
    tr = lang == "tr"
    if not s["toplam"]:
        return ("Henüz cevaplayamadığım bir soru olmadı."
                if tr else "No unanswered questions yet.")
    acik = oncelikli(limit=5)
    lines = ["### " + ("Sorularınızdan öğrendiklerim"
                       if tr else "What your questions taught me"), ""]
    lines.append(
        ("Cevabımın zayıf kaldığı **%d soru** yakaladım; bunların **%d tanesini** "
         "sonradan araştırıp öğrendim. **%d tanesi** hâlâ araştırma sırasında."
         if tr else
         "I caught **%d** questions where my answer was weak; I researched and "
         "learned **%d** of them. **%d** are still queued.")
        % (s["toplam"], s["ogrenildi"] + s["kapandi"], s["acik"]))
    if acik:
        lines.append("")
        lines.append("**" + ("Şu an araştırma sıramda:" if tr
                             else "Currently queued:") + "**")
        for g in acik:
            lines.append("- %s <span class='meta'>(%d kez soruldu)</span>"
                         % (g["soru"][:90], g["sayac"]))
    return "\n".join(lines)


# ── Takma adlar ─────────────────────────────────────────────────────────────
# Kullanicinin yazdigi terim kaynaklardaki terimden farkli olabilir:
# "Kazimir etkisi" / "Casimir effect". Bosluk arastirilirken dogru terim
# bulundugunda bu esleme kalici olarak saklanir; boylece kullanici ayni
# bicimde tekrar sordugunda erisim dogru kavrama gider.

def _takma_kur():
    c = db.conn()
    c.execute("""CREATE TABLE IF NOT EXISTS aliases(
        ifade TEXT PRIMARY KEY, kanonik TEXT, kaynak TEXT, at REAL)""")
    c.commit()


def takma_ad_kaydet(ifade, kanonik, kaynak="bosluk"):
    """Kullanici ifadesini kanonik terime bagla."""
    ifade = (ifade or "").strip()
    kanonik = (kanonik or "").strip()
    if not ifade or not kanonik or normalize(ifade) == normalize(kanonik):
        return False
    _takma_kur()
    c = db.conn()
    c.execute("INSERT OR REPLACE INTO aliases(ifade, kanonik, kaynak, at) "
              "VALUES(?,?,?,?)",
              (normalize(ifade), kanonik, kaynak, time.time()))
    c.commit()
    return True


def takma_adlar():
    """{normalize edilmis ifade: kanonik terim}"""
    _takma_kur()
    c = db.conn()
    try:
        return {r["ifade"]: r["kanonik"]
                for r in c.execute("SELECT ifade, kanonik FROM aliases")}
    except Exception:
        return {}


def genislet(sorgu):
    """Sorguyu bilinen takma adlarla genislet.

    "Kazimir etkisi nedir" -> "Kazimir etkisi nedir Casimir effect"
    Boylece hem kullanicinin yazdigi hem kaynaklardaki terim aranir.
    """
    n = normalize(sorgu or "")
    if not n:
        return sorgu
    ekler = []
    for ifade, kanonik in takma_adlar().items():
        if ifade and ifade in n and kanonik.lower() not in n:
            ekler.append(kanonik)
    return (sorgu + " " + " ".join(ekler[:3])).strip() if ekler else sorgu
