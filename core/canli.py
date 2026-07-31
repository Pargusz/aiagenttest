# -*- coding: utf-8 -*-
"""Canli arastirma: bilmedigini o anda internetten ogren ve kaynak goster.

Onceden bilinmeyen bir soru geldiginde "arastirma sirama aldim" deniyordu;
kullanici cevabi bir sonraki sefere bekliyordu. Burada arastirma SORU
SORULDUGU ANDA yapilir:

    soru -> Ingilizce fizik terimi -> Wikipedia + arXiv + Crossref
         -> fizik suzgeci -> baglam + kaynakca -> cevap

Uc kural:
  1. Zaman butcesi var; kullanici dakikalarca beklemez.
  2. Bulunan her sey fizik suzgecinden gecer (ressam "Kazimir Malevic"
     ornegi bunu gerektirdi).
  3. Cevabin altina KAYNAKCA eklenir: hangi bilgi nereden geldi, kullanici
     kendi gozuyle dogrulayabilsin.

Bulunanlar ayrica tabana yazilir; ayni soru bir daha sorulursa internete
cikmaya gerek kalmaz.
"""
import time

from . import db, kalite, sources
from .learner import normalize

ZAMAN_BUTCESI = 45.0        # saniye (model cevirisi gerekirse pay birakir)
EN_FAZLA_KAYNAK = 6


def _fizik_mi(metin):
    try:
        return kalite.fizik_ilgili(metin)
    except Exception:
        return True


def _ingilizce_terim(soru, lang):
    """Sorudaki konuyu Ingilizce standart terime cevir (varsa dil modeli)."""
    try:
        from . import dil
        if dil.MODEL.kurulu_mu():
            t = dil.MODEL.ingilizce_terim(soru, lang)
            if t:
                return t
    except Exception:
        pass
    return None


def arastir(soru, lang="tr", butce=ZAMAN_BUTCESI):
    """Soruyu canli olarak arastir.

    Doner: {"baglam": str, "kaynaklar": [{"baslik","url","tur"}], "terim": str}
    Hicbir sey bulunamazsa baglam bos doner.
    """
    baslangic = time.time()
    kalan = lambda: butce - (time.time() - baslangic)

    parcalar, kaynaklar = [], []
    gorulen_url = set()
    terim = None

    def ekle_kaynak(baslik, url, tur):
        if not url or url in gorulen_url:
            return
        gorulen_url.add(url)
        kaynaklar.append({"baslik": baslik[:160], "url": url, "tur": tur})

    # 1) Wikipedia — ONCE hizli yollar (model cagrisi saniyeler suruyor ve
    # butun butceyi yiyordu; olculdu: terim cevirisi 20 sn, aramaya sira
    # kalmiyordu). Once dogrudan arama denenir, tutmazsa model devreye girer.
    aramalar = [(soru, lang)]
    if lang != "en":
        aramalar.append((soru, "en"))

    for arama, dil_kodu in aramalar:
        if kalan() < 6 or len(parcalar) >= 3:
            break
        try:
            sonuc = sources.wiki_search(arama, lang=dil_kodu, limit=3)
        except Exception:
            continue
        for s in sonuc:
            if kalan() < 4 or len(parcalar) >= 3:
                break
            baslik = s["title"] if isinstance(s, dict) else s
            try:
                oz = sources.wiki_summary(baslik, lang=dil_kodu)
            except Exception:
                continue
            if not oz or len(oz["extract"]) < 120:
                continue
            if not _fizik_mi(oz["title"] + " " + oz["extract"]):
                continue
            parcalar.append("ANSIKLOPEDI: %s\n%s"
                            % (oz["title"], oz["extract"][:1400]))
            ekle_kaynak(oz["title"], oz["url"], "Wikipedia")
            # Kalici ogren: ayni soru bir daha internete cikmasin
            try:
                db.upsert_concept(oz["title"], normalize(oz["title"]),
                                  dil_kodu, oz.get("description", ""),
                                  oz["extract"], oz["url"])
            except Exception:
                pass
        if parcalar:
            break

    # Hizli yol tutmadiysa dil modeliyle Ingilizce terime cevir ve tekrar ara
    if not parcalar:
        terim = _ingilizce_terim(soru, lang)
        if terim:
            try:
                sonuc = sources.wiki_search(terim, lang="en", limit=3)
            except Exception:
                sonuc = []
            for s in sonuc[:3]:
                baslik = s["title"] if isinstance(s, dict) else s
                try:
                    oz = sources.wiki_summary(baslik, lang="en")
                except Exception:
                    continue
                if not oz or len(oz["extract"]) < 120:
                    continue
                if not _fizik_mi(oz["title"] + " " + oz["extract"]):
                    continue
                parcalar.append("ANSIKLOPEDI: %s\n%s"
                                % (oz["title"], oz["extract"][:1400]))
                ekle_kaynak(oz["title"], oz["url"], "Wikipedia")
                try:
                    db.upsert_concept(oz["title"], normalize(oz["title"]),
                                      "en", oz.get("description", ""),
                                      oz["extract"], oz["url"])
                except Exception:
                    pass
    elif not terim:
        # Kaynak bulundu; arXiv icin Ingilizce terimi ilk basliktan al
        terim = kaynaklar[0]["baslik"] if kaynaklar else None

    # 2) arXiv — guncel arastirma (Ingilizce terim gerekir)
    if terim and kalan() > 4:
        try:
            makaleler = sources.arxiv_fetch(query=terim, max_results=5)
        except Exception:
            makaleler = []
        for m in makaleler[:3]:
            ozet = (m.get("abstract") or "").strip()
            if len(ozet) < 150:
                continue
            parcalar.append("MAKALE: %s\n%s"
                            % ((m.get("title") or "")[:160], ozet[:900]))
            ekle_kaynak(m.get("title") or "", m.get("url") or "", "arXiv")
            try:
                db.add_paper(source="arxiv",
                             ext_id=m.get("ext_id") or m.get("id"),
                             title=m.get("title", ""), abstract=ozet,
                             authors=m.get("authors", ""),
                             categories=m.get("categories", ""), lang="en",
                             url=m.get("url", ""),
                             published=m.get("published", ""),
                             kalite=float(m.get("kalite", 0) or 0))
            except Exception:
                pass

    # 3) Crossref — hakemli yayin kunyesi (ozet cogu zaman yok, kaynak olarak
    #    yine de degerli)
    if terim and kalan() > 3 and len(kaynaklar) < EN_FAZLA_KAYNAK:
        try:
            for it in (sources.crossref_search(terim, rows=3) or [])[:2]:
                ekle_kaynak(it.get("title") or "", it.get("url") or "",
                            it.get("dergi") or "Crossref")
        except Exception:
            pass

    return {
        "baglam": "\n\n".join(parcalar),
        "kaynaklar": kaynaklar[:EN_FAZLA_KAYNAK],
        "terim": terim or "",
        "sure": round(time.time() - baslangic, 1),
    }


def kaynakca(kaynaklar, lang="tr"):
    """Kaynak listesini cevabin altina eklenecek metne cevir."""
    if not kaynaklar:
        return ""
    baslik = "Kaynaklar" if lang == "tr" else "Sources"
    satirlar = ["", "---", "**%s**" % baslik, ""]
    for k in kaynaklar:
        ad = (k.get("baslik") or k.get("url") or "").strip()
        url = k.get("url") or ""
        tur = k.get("tur") or ""
        if url:
            satirlar.append("- [%s](%s) <span class='meta'>%s</span>"
                            % (ad[:110], url, tur))
        else:
            satirlar.append("- %s <span class='meta'>%s</span>" % (ad[:110], tur))
    return "\n".join(satirlar)
