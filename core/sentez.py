"""Ogrenilen malzemeden konu sayfasi sentezleme.

Cekirdekte elle yazilmis 27 konu var ve bu sayi hic buyumuyordu; yeni makale
gelmesi "aciklayabildigim konu" sayisini artirmiyordu. Burada bir kavram
yeterince malzeme biriktirdiginde ona cekirdek konular gibi yapilandirilmis
bir sayfa uretiliyor:

    tanim → temel bulgular → bagintilar → iliskili kavramlar → kaynaklar

Boylece "aciklayabildigim konu" sayisi makaleler geldikce gercekten artar ve
bu sayi `durum` raporunda gorulebilir.
"""
import re

from . import db, retrieval, bagintilar
from .learner import normalize

# Bir kavramin "aciklanabilir" sayilmasi icin gereken en az malzeme
ESIK_BULGU = 2
ESIK_BAGLANTI = 3


def _kavram_bul(sorgu, lang="tr"):
    """Sorguyla gercekten ortusen kavrami bul.

    FTS her sorguya bir sey dondurur; "gaz isinirsa ne olur" sorusuna
    "Faraday etkisi" gelmesi boyle oluyordu. Ortusme sarti koyuyoruz.
    """
    from .baglam import _ilgili
    adaylar = (retrieval.search_concepts(sorgu, limit=3, lang=lang)
               or retrieval.search_concepts(sorgu, limit=3))
    for k in adaylar:
        metin = (k.get("name") or "") + " " + (k.get("definition") or "")
        if _ilgili(sorgu, metin):
            return k
    return None


def _ilgili_makaleler(konu, makaleler, en_fazla=6):
    """Konusu gercekten bu olan makaleleri sec.

    Bir makalenin govdesinde konunun gecmesi, o makalenin KONUSU oldugu
    anlamina gelmez. Olculdu: "topolojik yalitkanlar" sorusuna, konuyu ayak
    ustu anan bir fraktal egri makalesinden derleme yapiliyordu. Once
    BASLIK eslesmesi aranir; yetmezse ozetten iki kelime ortusmesi.
    """
    from .baglam import _ilgili
    baslikta = [p for p in makaleler
                if _ilgili(konu, p.get("title") or "", gerekli=1)]
    if len(baslikta) >= 2:
        return baslikta[:en_fazla]
    govdede = [p for p in makaleler
               if _ilgili(konu, (p.get("title") or "") + " "
                          + (p.get("abstract") or "")[:400], gerekli=2)]
    return (baslikta + [p for p in govdede if p not in baslikta])[:en_fazla]


def malzeme(sorgu, lang="tr"):
    """Bir konu icin elde ne varsa topla."""
    kavram = _kavram_bul(sorgu, lang)
    ad = (kavram or {}).get("name") or sorgu
    n = normalize(ad)

    bulgular = retrieval.insights(ad, limit=8,
                                  turler=("tanim", "bulgu", "iliski", "sayisal"))
    if len(bulgular) < 2 and ad != sorgu:
        bulgular += [b for b in retrieval.insights(sorgu, limit=4)
                     if b not in bulgular]

    return {
        "ad": ad,
        "norm": n,
        "kavram": kavram,
        "bulgular": bulgular,
        "iliskiler": retrieval.relations(ad, limit=6),
        "baglantilar": [r for r in retrieval.related_concepts(ad, limit=10)
                        if r["weight"] > 1],
        "bagintilar": bagintilar.ara(ad, limit=5),
        "makaleler": _ilgili_makaleler(ad, retrieval.search_papers(ad, limit=12)),
    }


def aciklanabilir_mi(m):
    """Yapilandirilmis bir sayfa uretmeye yetecek malzeme var mi?"""
    if not m:
        return False
    puan = 0
    if m["kavram"] and len(m["kavram"].get("extract") or "") > 120:
        puan += 3
    puan += min(len(m["bulgular"]), 4)
    puan += 1 if len(m["baglantilar"]) >= ESIK_BAGLANTI else 0
    puan += 1 if m["bagintilar"] else 0
    puan += 1 if len(m["makaleler"]) >= 3 else 0
    return puan >= 5


def sayfa(m, lang="tr", detay=False):
    """Toplanan malzemeden konu sayfasi uret."""
    tr = lang == "tr"
    L = lambda a, b: a if tr else b
    lines = ["### %s" % m["ad"], ""]

    # 1) Tanim
    kav = m["kavram"]
    tanim_bulgu = [b for b in m["bulgular"] if b["tur"] == "tanim"]
    if kav and (kav.get("extract") or "").strip():
        ozet = retrieval.summarize([kav["extract"]], query=m["ad"],
                                   max_sentences=5 if detay else 3)
        lines.append(" ".join(ozet) if ozet else kav["extract"][:600])
    elif tanim_bulgu:
        lines.append(tanim_bulgu[0]["cumle"])
    elif m["makaleler"]:
        # Ansiklopedik tanim yoksa, konuyu en iyi anlatan makale ozetlerinden
        # bir acilis cumlesi cikar — sayfa tanimsiz baslamasin.
        ozetler = [p["abstract"] for p in m["makaleler"][:3] if p.get("abstract")]
        acilis = retrieval.summarize(ozetler, query=m["ad"],
                                     max_sentences=3 if detay else 2)
        if acilis:
            lines.append(" ".join(acilis))
    lines.append("")

    # 2) Makalelerden ogrenilen bulgular (tanim disindakiler)
    diger = [b for b in m["bulgular"] if b["tur"] != "tanim"]
    if diger:
        lines.append("#### " + L("Araştırmalardan öğrendiklerim",
                                 "What I learned from research"))
        lines.append("")
        etiket = {"bulgu": L("bulgu", "finding"),
                  "iliski": L("ilişki", "relation"),
                  "sayisal": L("sayısal", "quantitative")}
        for b in diger[:6 if detay else 4]:
            c = b["cumle"]
            if len(c) > 260:
                c = c[:257].rsplit(" ", 1)[0] + "…"
            lines.append("- <span class='meta'>[%s]</span> %s"
                         % (etiket.get(b["tur"], b["tur"]), c))
        lines.append("")

    # 3) Bagintilar
    if m["bagintilar"]:
        lines.append("#### " + L("Bağıntılar", "Relations"))
        lines.append("")
        for e in m["bagintilar"]:
            isaret = " ✓" if e["cozulebilir"] else ""
            lines.append("- `%s`%s" % (e["latex"], isaret))
        lines.append("")

    # 4) Kavram agi
    if m["iliskiler"]:
        lines.append(L("**Kurduğum bağlar:** ", "**Inferred links:** ")
                     + " · ".join("%s → *%s* → %s" % (r["a"], r["fiil"], r["b"])
                                  for r in m["iliskiler"][:4]))
        lines.append("")
    if m["baglantilar"]:
        lines.append(L("**Sık birlikte geçtiği kavramlar:** ",
                       "**Frequently co-occurring concepts:** ")
                     + ", ".join(r["name"] for r in m["baglantilar"][:8]))
        lines.append("")

    # 5) Kaynaklar
    if m["makaleler"]:
        lines.append("#### " + L("Kaynaklar", "Sources"))
        lines.append("")
        for p in m["makaleler"][:4]:
            baslik = (p.get("title") or "")[:120]
            url = p.get("url") or ""
            yil = (p.get("published") or "")[:4]
            if url:
                lines.append("- [%s](%s) <span class='meta'>%s</span>"
                             % (baslik, url, yil))
            else:
                lines.append("- %s <span class='meta'>%s</span>" % (baslik, yil))
        lines.append("")

    if kav and kav.get("url"):
        lines.append("<span class='meta'>%s</span>" % kav["url"])
    return "\n".join(lines)


def aciklanabilir_sayisi():
    """Kac ogrenilmis kavram icin yapilandirilmis sayfa uretilebiliyor?

    Bu, botun 'aciklayabildigi konu' sayisidir ve makaleler geldikce artar.
    Sayim pahali oldugu icin sonuc onbellege alinir.
    """
    onbellek = db.get_state("aciklanabilir_sayisi")
    makale = db.stats().get("makale", 0)
    if isinstance(onbellek, dict) and onbellek.get("makale") == makale:
        return onbellek.get("sayi", 0)

    c = db.conn()
    try:
        # Yeterince bulgusu ve baglantisi olan kavramlari say
        sayi = c.execute("""
            SELECT COUNT(*) FROM (
                SELECT co.norm
                FROM concepts co
                WHERE (SELECT COUNT(*) FROM insights i WHERE i.norm = co.norm) >= ?
                  AND (SELECT COUNT(*) FROM concept_links cl
                       WHERE cl.a = co.norm AND cl.weight > 1) >= ?
                GROUP BY co.norm
            )""", (ESIK_BULGU, ESIK_BAGLANTI)).fetchone()[0]
    except Exception:
        sayi = 0
    db.set_state("aciklanabilir_sayisi", {"makale": makale, "sayi": sayi})
    return sayi
