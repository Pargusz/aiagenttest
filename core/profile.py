"""Kullanici profili: kisiye dair kalici bellek.

Sohbetler arasinda hatirlananlar: kisinin adi / hitap sekli, kendini
tanimladigi seviye ve zamanla ilgilendigi konular. Bu sayede yeni bir sohbet
acildiginda bot kisiyi tanimaya devam eder.

Her sey yalnizca bu bilgisayardaki veritabaninda durur; disari hicbir sey
gonderilmez. Kullanici "beni unut" diyerek her an silebilir.
"""
import json
import re
import time

from . import db

# ── Ad / hitap cikarimi ─────────────────────────────────────────────────────
# Yakalanan sozcugun gercekten bir ad olup olmadigini denetlemek icin:
# "ben fizik ogrencisiyim" cumlesinde "fizik" bir ad degildir.
_AD_OLMAZ = set("""
fizik matematik kimya biyoloji muhendis muhendisi ogrenci ogrencisi ogretmen
ogretmeni lise universite lisans yuksek doktora master mezun arastirmaci
akademisyen fizikci meraklisi amator profesyonel yeni acemi baslangic
biri birisi burada iyi kotu hasta yorgun mesgul hazir emin memnun
student teacher engineer physicist researcher professor beginner curious
here good fine tired busy ready sure happy interested new
bir bu su o ne kim nasil neden niye hangi cok az daha en ama fakat
and the for with from that this what who how why very much more most
""".split())

_AD_KALIPLARI = [
    r"\b(?:benim\s+)?ad[iı]m\s+([A-Za-zÇĞİÖŞÜçğıöşü]{2,20})",
    r"\bismim\s+([A-Za-zÇĞİÖŞÜçğıöşü]{2,20})",
    r"\bbana\s+([A-Za-zÇĞİÖŞÜçğıöşü]{2,20})\s+(?:de|diyebilirsin|der misin|dersin)\b",
    r"\bben\s+([A-Za-zÇĞİÖŞÜçğıöşü]{2,20})(?:'?[iıuü]m|'?y[iıuü]m)?\s*[,.!]?\s*$",
    r"\bmy name(?:'s| is)\s+([A-Za-z]{2,20})",
    r"\bcall me\s+([A-Za-z]{2,20})",
    r"\bi(?:'m| am)\s+([A-Za-z]{2,20})\s*[,.!]?\s*$",
]

# ── Seviye cikarimi ─────────────────────────────────────────────────────────
_SEVIYELER = [
    ("doktora", r"\b(doktora|phd|ph\.?d|doktorant)\b", "Doktora", "PhD"),
    ("yuksek_lisans", r"\b(yuksek lisans|master|msc|y[uü]ksek lisans)\b",
     "Yüksek lisans", "Master's"),
    ("akademisyen", r"\b(akademisyen|arastirmaci|researcher|professor|"
                    r"ogretim uyesi|hoca)\b", "Akademisyen", "Academic"),
    ("ogretmen", r"\b(ogretmen(im|iyim)?|teacher|eğitmen|egitmen)\b",
     "Öğretmen", "Teacher"),
    ("lisans", r"\b(lisans|universite ogrencisi|university student|"
               r"undergrad(uate)?|fizik bolumu|fizik b[oö]l[uü]m[uü])\b",
     "Lisans öğrencisi", "Undergraduate"),
    ("lise", r"\b(lise|high school|ortaokul|yks|tyt|ayt)\b",
     "Lise düzeyi", "High school"),
    ("baslangic", r"\b(yeni basl[iı]yorum|yeni baslad[iı]m|acemiyim|"
                  r"hic bilmiyorum|sifirdan|just starting|complete beginner|"
                  r"new to (this|physics|matlab)|no experience)\b",
     "Başlangıç", "Beginner"),
    ("meraklı", r"\b(merakl[iı]s[iı]y[iı]m|hobi|amator|hobbyist|enthusiast)\b",
     "Meraklı", "Enthusiast"),
]


def _norm(s):
    s = (s or "").lower()
    for a, b in {"ı": "i", "İ": "i", "ş": "s", "ğ": "g", "ü": "u",
                 "ö": "o", "ç": "c", "â": "a"}.items():
        s = s.replace(a, b)
    return s


# ── Okuma / yazma ───────────────────────────────────────────────────────────

# Profil her mesajda yazildigi icin dogrudan INSERT yapilmiyor: ogrenme motoru
# yazma kilidini tutuyorken bu, istegin "database is locked" ile dusmesine yol
# aciyordu. Degerler once bellege yazilir, diske kuyruk uzerinden gider.
_MEM = {}
_MEM_YUKLU = False


def _yukle():
    global _MEM_YUKLU
    if _MEM_YUKLU:
        return
    for k in ("ad", "seviye", "ilk_gorusme", "soru_sayisi"):
        v = db.get_state("profil_" + k)
        if v is not None:
            _MEM[k] = v
    _MEM_YUKLU = True


_ALANLAR = ("ad", "seviye", "ilk_gorusme", "soru_sayisi")


def get(key, default=None):
    _yukle()
    if key in _MEM:
        # None burada "silindi" demektir; diskteki eski degere donulmez
        # (silme kuyruga alindigi icin disk bir sure daha eski kalabilir).
        v = _MEM[key]
        return default if v is None else v
    return db.get_state("profil_" + key, default)


def set_(key, value):
    _yukle()
    _MEM[key] = value
    db.queue_write(
        "INSERT INTO learn_state(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        ("profil_" + key, json.dumps(value, ensure_ascii=False)))


def name():
    return get("ad")


def level():
    return get("seviye")


def level_label(lang="tr"):
    key = get("seviye")
    for k, _pat, tr, en in _SEVIYELER:
        if k == key:
            return tr if lang == "tr" else en
    return None


def note_interest(subject, limit_len=60):
    """Konusulan konuyu ilgi alanlarina isle."""
    if not subject:
        return
    s = subject.strip()[:limit_len]
    if len(s) < 3:
        return
    n = _norm(s)
    db.queue_write(
        "INSERT INTO interests(norm, label, count, last_at) VALUES(?,?,1,?) "
        "ON CONFLICT(norm) DO UPDATE SET count = count + 1, "
        "label = excluded.label, last_at = excluded.last_at",
        (n, s, time.time()))


def top_interests(limit=5, min_count=1):
    try:
        rows = db.conn().execute(
            "SELECT label, count, last_at FROM interests "
            "WHERE count >= ? ORDER BY count DESC, last_at DESC LIMIT ?",
            (min_count, limit)).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def recent_interests(limit=4):
    try:
        rows = db.conn().execute(
            "SELECT label, count, last_at FROM interests "
            "ORDER BY last_at DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def stats():
    c = db.conn()

    def one(q, d=0):
        try:
            r = c.execute(q).fetchone()
            return (r[0] if r and r[0] is not None else d)
        except Exception:
            return d

    return {
        "ad": name(),
        "seviye": get("seviye"),
        "ilk_gorusme": get("ilk_gorusme"),
        "soru_sayisi": int(get("soru_sayisi", 0) or 0),
        "sohbet_sayisi": one("SELECT COUNT(*) FROM sessions"),
        "ilgi_sayisi": one("SELECT COUNT(*) FROM interests"),
    }


def forget():
    """Kisiye dair her seyi sil (sohbet gecmisi haric)."""
    global _MEM_YUKLU
    _MEM.clear()
    # Her alani acikca "silindi" olarak isaretle; yoksa get() diskteki
    # (henuz silinmemis) eski degeri okurdu.
    for k in _ALANLAR:
        _MEM[k] = None
    _MEM_YUKLU = True
    db.queue_write("DELETE FROM learn_state WHERE key LIKE 'profil_%'", ())
    db.queue_write("DELETE FROM interests", ())
    return True


# ── Cikarim ─────────────────────────────────────────────────────────────────

def extract(message):
    """Mesajdan kisisel bilgi cikar ve kaydet. Bulunanlari dondurur."""
    bulunan = {}
    if not message:
        return bulunan

    raw = message.strip()
    low = _norm(raw)

    # Ad
    if not name():
        for pat in _AD_KALIPLARI:
            m = re.search(pat, raw, re.I)
            if not m:
                continue
            aday = m.group(1).strip(" .,!?'\"")
            if _norm(aday) in _AD_OLMAZ or len(aday) < 2:
                continue
            if not re.match(r"^[A-Za-zÇĞİÖŞÜçğıöşü]+$", aday):
                continue
            duzgun = aday[0].upper() + aday[1:]
            set_("ad", duzgun)
            bulunan["ad"] = duzgun
            break

    # Seviye
    for key, pat, _tr, _en in _SEVIYELER:
        if re.search(pat, low):
            if get("seviye") != key:
                set_("seviye", key)
                bulunan["seviye"] = key
            break

    if not get("ilk_gorusme"):
        set_("ilk_gorusme", time.strftime("%Y-%m-%d"))
    return bulunan


def greeting_line(lang="tr"):
    """Selamlamaya eklenecek kisisel satir."""
    ad = name()
    son = recent_interests(3)
    parts = []
    if ad:
        parts.append(("Merhaba %s!" % ad) if lang == "tr" else ("Hello %s!" % ad))
    if son:
        konular = ", ".join("**%s**" % r["label"] for r in son)
        if lang == "tr":
            parts.append("Geçen sefer %s konuşmuştuk." % konular)
        else:
            parts.append("Last time we talked about %s." % konular)
    return " ".join(parts)


def summary(lang="tr"):
    """'Beni taniyor musun' sorusuna verilecek yanit."""
    s = stats()
    ilgi = top_interests(6)
    tr = lang == "tr"
    lines = ["### " + ("Sizin hakkınızda bildiklerim" if tr
                       else "What I remember about you"), ""]
    bir_sey = False
    if s["ad"]:
        lines.append(("- **Adınız:** %s" if tr else "- **Name:** %s") % s["ad"])
        bir_sey = True
    lab = level_label(lang)
    if lab:
        lines.append(("- **Düzeyiniz:** %s" if tr else "- **Level:** %s") % lab)
        bir_sey = True
    if s["ilk_gorusme"]:
        lines.append(("- **İlk görüşmemiz:** %s" if tr else "- **First met:** %s")
                     % s["ilk_gorusme"])
        bir_sey = True
    if s["soru_sayisi"]:
        lines.append(("- **Sorduğunuz soru:** %d" if tr else "- **Questions asked:** %d")
                     % s["soru_sayisi"])
        bir_sey = True
    if s["sohbet_sayisi"]:
        lines.append(("- **Sohbet sayısı:** %d" if tr else "- **Conversations:** %d")
                     % s["sohbet_sayisi"])
        bir_sey = True
    if ilgi:
        bir_sey = True
        lines.append("")
        lines.append("**" + ("En çok konuştuğumuz konular:" if tr
                             else "Topics we discuss most:") + "**")
        lines.append("")
        for r in ilgi:
            lines.append("- %s <span class='meta'>%d %s</span>"
                         % (r["label"], r["count"], "kez" if tr else "times"))
    if not bir_sey:
        return ("Sizin hakkınızda henüz bir şey bilmiyorum. Adınızı söylerseniz "
                "(`adım ...`) ve neyle ilgilendiğinizi konuşursak zamanla "
                "tanırım." if tr else
                "I don't know anything about you yet. Tell me your name "
                "(`my name is ...`) and we'll build it up as we talk.")
    lines.append("")
    lines.append("_" + ("Bunların hepsi yalnızca bu bilgisayarda saklanır. "
                        "Silmek için `beni unut` yazın." if tr else
                        "All of this is stored only on this computer. "
                        "Type `forget me` to erase it.") + "_")
    return "\n".join(lines)
