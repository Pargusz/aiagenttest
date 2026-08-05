"""Yuklenen belgeleri okuma, cozumleme ve ogrenme.

Desteklenen turler:
  - PDF  (pypdf ile metin cikarimi)
  - TXT / MD / CSV / TEX / BIB
  - .m / .py / .c gibi kod dosyalari
  - Resimler: saklanir ve gosterilir, ancak bu bilgisayarda OCR motoru
    bulunmadigi icin icindeki metin okunamaz. Bu, cevapta acikca soylenir.

Cozumleme yapay sinir agi kullanmaz: baslik/ozet/bolum tespiti, cikarimsal
ozetleme, terim ve formul cikarimi, bilinen kavramlarla eslestirme.
"""
import hashlib
import os
import re
import time

from . import config, db, retrieval, units
from .learner import tokens, normalize, fizik_ilgili

BELGE_DIR = os.path.join(config.DATA_DIR, "belgeler")
os.makedirs(BELGE_DIR, exist_ok=True)

MAX_METIN = 400000          # cok buyuk PDF'lerde bellegi korumak icin
RESIM_UZANTI = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff"}
METIN_UZANTI = {".txt", ".md", ".markdown", ".csv", ".tsv", ".tex", ".bib",
                ".json", ".log", ".dat"}
KOD_UZANTI = {".m", ".py", ".c", ".cpp", ".h", ".f", ".f90", ".jl", ".r",
              ".mat", ".ipynb"}


class BelgeHatasi(Exception):
    pass


def _guvenli_ad(ad):
    ad = os.path.basename(ad or "belge")
    ad = re.sub(r"[^\w\.\-() ]+", "_", ad, flags=re.UNICODE)
    return ad[:120] or "belge"


def kaydet(dosya_adi, veri):
    """Yuklenen dosyayi diske yaz, yolunu dondur."""
    ad = _guvenli_ad(dosya_adi)
    ozet = hashlib.sha1(veri).hexdigest()[:10]
    kok, uzanti = os.path.splitext(ad)
    hedef = os.path.join(BELGE_DIR, "%s_%s%s" % (kok[:70], ozet, uzanti.lower()))
    if not os.path.exists(hedef):
        with open(hedef, "wb") as f:
            f.write(veri)
    return hedef


# ── metin cikarimi ──────────────────────────────────────────────────────────

def _pdf_metni(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise BelgeHatasi(
            "PDF okumak icin `pypdf` gerekli. Kurmak icin: "
            "python3 -m pip install --user pypdf")
    try:
        reader = PdfReader(path)
    except Exception as e:
        raise BelgeHatasi("PDF acilamadi: %s" % e)

    meta = {"sayfa": len(reader.pages)}
    try:
        bilgi = reader.metadata or {}
        for anahtar, alan in (("/Title", "baslik"), ("/Author", "yazar"),
                              ("/Subject", "konu"), ("/Keywords", "anahtar")):
            deger = bilgi.get(anahtar)
            if deger:
                meta[alan] = str(deger).strip()[:400]
    except Exception:
        pass

    parcalar = []
    toplam = 0
    for sayfa in reader.pages:
        try:
            t = sayfa.extract_text() or ""
        except Exception:
            t = ""
        parcalar.append(t)
        toplam += len(t)
        if toplam > MAX_METIN:
            meta["kesildi"] = True
            break
    return "\n\n".join(parcalar), meta


def _duz_metin(path):
    for kodlama in ("utf-8", "latin-1"):
        try:
            with open(path, "r", encoding=kodlama) as f:
                return f.read(MAX_METIN), {}
        except (UnicodeDecodeError, ValueError):
            continue
        except OSError as e:
            raise BelgeHatasi("Dosya okunamadi: %s" % e)
    raise BelgeHatasi("Dosyanin kodlamasi cozulemedi.")


def _ocr_mac(path):
    """macOS'un YERLESIK metin tanima motoru (Vision framework).

    Kullanicinin istegi: "gorsel taramasi yapabiliyor olmali."
    Onceden resimden hicbir metin cikarilmiyordu; yalnizca boyut ve
    bicim okunuyordu.

    Neden Vision: macOS'ta hazir gelir, ek bir program KURULMASI
    gerekmez ve Turkce'yi tanir. tesseract secenegi ayrica denenir
    ama o, isletim sistemi duzeyinde ayri bir kurulum ister.

    Basarisiz olursa None doner; cagiran taraf oteki yollari dener.
    """
    try:
        import Vision
        import Quartz
        from Foundation import NSURL
    except Exception:
        return None
    try:
        url = NSURL.fileURLWithPath_(path)
        kaynak = Quartz.CGImageSourceCreateWithURL(url, None)
        if not kaynak:
            return None
        img = Quartz.CGImageSourceCreateImageAtIndex(kaynak, 0, None)
        if not img:
            return None
        istek = Vision.VNRecognizeTextRequest.alloc().init()
        istek.setRecognitionLevel_(0)        # 0 = dogru (yavas), 1 = hizli
        istek.setUsesLanguageCorrection_(True)
        try:
            istek.setRecognitionLanguages_(["tr-TR", "en-US"])
        except Exception:
            pass
        isleyici = Vision.VNImageRequestHandler.alloc()\
            .initWithCGImage_options_(img, None)
        tamam, _hata = isleyici.performRequests_error_([istek], None)
        if not tamam:
            return None
        satirlar = []
        for gozlem in (istek.results() or []):
            adaylar = gozlem.topCandidates_(1)
            if adaylar and len(adaylar):
                satirlar.append(str(adaylar[0].string()))
        return "\n".join(satirlar).strip() or None
    except Exception:
        return None


def _ocr_tesseract(path):
    """tesseract kuruluysa onu kullan (macOS disi sistemler icin)."""
    try:
        import pytesseract
        from PIL import Image
    except Exception:
        return None
    try:
        with Image.open(path) as im:
            return (pytesseract.image_to_string(im, lang="tur+eng")
                    or "").strip() or None
    except Exception:
        return None


def resim_metni(path):
    """Resimden metin oku. Once yerlesik motor, sonra tesseract."""
    for motor in (_ocr_mac, _ocr_tesseract):
        try:
            metin = motor(path)
        except Exception:
            metin = None
        if metin:
            return metin, motor.__name__.replace("_ocr_", "")
    return None, None


def _resim_bilgisi(path):
    meta = {"resim": True}
    try:
        from PIL import Image
        with Image.open(path) as im:
            meta["boyut"] = "%d×%d" % im.size
            meta["bicim"] = im.format
            meta["mod"] = im.mode
    except Exception:
        pass
    metin, motor = resim_metni(path)
    if metin:
        meta["ocr"] = motor
    return (metin or ""), meta


def metin_cikar(path):
    """Dosyadan metin ve ust bilgi cikar. (metin, meta) doner."""
    uzanti = os.path.splitext(path)[1].lower()
    if uzanti == ".pdf":
        return _pdf_metni(path)
    if uzanti in RESIM_UZANTI:
        return _resim_bilgisi(path)
    if uzanti in METIN_UZANTI or uzanti in KOD_UZANTI or uzanti == "":
        metin, meta = _duz_metin(path)
        if uzanti in KOD_UZANTI:
            meta["kod"] = True
        return metin, meta
    # Bilinmeyen tur: metin gibi okumayi dene
    try:
        return _duz_metin(path)
    except BelgeHatasi:
        raise BelgeHatasi("Bu dosya turu okunamiyor: %s" % (uzanti or "?"))


# ── yapisal cozumleme ───────────────────────────────────────────────────────

_DOI = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)
_ARXIV = re.compile(r"arXiv[:\s]*(\d{4}\.\d{4,5}(v\d+)?)", re.I)
_YIL = re.compile(r"\b(19|20)\d{2}\b")
_LATEX = re.compile(r"\$([^$\n]{3,120})\$|\\\[([^\]]{3,160})\\\]")
# Denklem gibi gorunen duz satirlar: "E = mc^2", "F = m a"
_DENKLEM = re.compile(r"^\s*[A-Za-zΑ-Ωα-ω][\w_,()]{0,12}\s*=\s*[^=\n]{2,80}$")

_OZET_BAS = re.compile(r"^\s*(abstract|özet|ozet|summary)\b[\s:.\-]*", re.I | re.M)
_OZET_SON = re.compile(
    r"^\s*(1\.?\s+)?(introduction|giris|giriş|keywords|anahtar kelimeler|"
    r"index terms)\b", re.I | re.M)

_BOLUM = re.compile(
    r"^\s*(?:(\d+(?:\.\d+)*)\s*[.\)]?\s+)?"
    r"(abstract|özet|ozet|introduction|giri[sş]|related work|background|"
    r"theory|kuram|method(?:s|ology)?|y[oö]ntem|materials and methods|"
    r"experiment(?:al|s)?|deney|results?|bulgular|sonu[cç]lar|"
    r"discussion|tart[iı][sş]ma|conclusions?|sonu[cç]|"
    r"acknowledg(?:e)?ments?|te[sş]ekk[uü]r|references|kaynak[cç]a|"
    r"appendix|ek)\b\s*$", re.I | re.M)


def _baslik_tahmini(metin, meta, dosya_adi):
    if meta.get("baslik") and len(meta["baslik"]) > 8:
        return meta["baslik"]
    for satir in (metin or "").split("\n")[:40]:
        s = satir.strip()
        if 15 <= len(s) <= 200 and not s.lower().startswith(("arxiv", "doi", "http")):
            harf = sum(c.isalpha() for c in s)
            if harf / max(len(s), 1) > 0.6:
                return s
    return os.path.splitext(os.path.basename(dosya_adi))[0]


def _ozet_bul(metin):
    m = _OZET_BAS.search(metin or "")
    if not m:
        return ""
    bas = m.end()
    son = _OZET_SON.search(metin, bas)
    parca = metin[bas:son.start() if son else bas + 2500]
    parca = re.sub(r"\s+", " ", parca).strip()
    return parca[:2500]


def _bolumler(metin):
    bulunan = []
    for m in _BOLUM.finditer(metin or ""):
        ad = m.group(2).strip()
        if ad.lower() not in [b.lower() for b in bulunan]:
            bulunan.append(ad)
    return bulunan[:14]


def _formuller(metin):
    out = []
    for m in _LATEX.finditer(metin or ""):
        t = (m.group(1) or m.group(2) or "").strip()
        if 3 < len(t) < 140:
            out.append(t)
    if len(out) < 4:
        for satir in (metin or "").split("\n"):
            if _DENKLEM.match(satir) and len(satir.strip()) < 90:
                s = satir.strip()
                if s not in out:
                    out.append(s)
            if len(out) >= 12:
                break
    # tekrarlari at
    gorulen, tekil = set(), []
    for f in out:
        k = re.sub(r"\s+", "", f)
        if k not in gorulen:
            gorulen.add(k)
            tekil.append(f)
    return tekil[:12]


def _sayisal_bulgular(metin, limit=8):
    """Birimli sayisal degerleri yakala: '2.7 K', '13.6 eV', '5.5 GPa'."""
    birimler = "|".join(sorted((re.escape(u) for u in units.UNITS
                                if 1 <= len(u) <= 6), key=len, reverse=True))
    rx = re.compile(r"(?<![\w.])([-+]?\d+(?:\.\d+)?(?:\s*[×x]\s*10\^?-?\d+)?)"
                    r"\s*(%s)(?![\w])" % birimler)
    out, gorulen = [], set()
    for m in rx.finditer(metin or ""):
        s = "%s %s" % (m.group(1).strip(), m.group(2))
        if s not in gorulen:
            gorulen.add(s)
            out.append(s)
        if len(out) >= limit:
            break
    return out


def _bilinen_kavramlar(metin, limit=10):
    """Ogrenilmis kavram sozlugunden bu belgede gecenleri bul."""
    n = normalize(metin or "")[:200000]
    try:
        satirlar = db.conn().execute(
            "SELECT norm, name, lang FROM concepts WHERE length(norm) > 5 "
            "ORDER BY freq DESC LIMIT 4000").fetchall()
    except Exception:
        return []
    bulunan = []
    for r in satirlar:
        if r["norm"] in n:
            bulunan.append(r["name"])
            if len(bulunan) >= limit:
                break
    return bulunan


def cozumle(path, dosya_adi, lang="tr"):
    """Belgeyi cozumle ve yapilandirilmis sonuc dondur."""
    metin, meta = metin_cikar(path)
    sonuc = {
        "dosya": dosya_adi,
        "yol": path,
        "meta": meta,
        "resim": bool(meta.get("resim")),
        "uzunluk": len(metin or ""),
        "kelime": len((metin or "").split()),
    }
    # RESIMDEN METIN OKUNDUYSA belge gibi cozumlenir.
    # Kullanicinin istegi: "gorselleri de okuyabiliyor, gorebiliyor ve
    # ALGILAYABILIYOR olmali." Onceden resim dali burada erken donuyor
    # ve OCR metni hicbir yerde kullanilmiyordu; formul, kavram ve
    # sayisal bulgu cikarimi hic calismiyordu. Artik metin varsa
    # asagidaki normal cozumleme yolundan geciyor; boylece resimdeki
    # formul uzerinde hesap yapilabiliyor ve icerik ogrenilebiliyor.
    if sonuc["resim"]:
        if not (metin or "").strip():
            return sonuc
        sonuc["metin"] = metin

    if not (metin or "").strip():
        sonuc["bos"] = True
        return sonuc

    sonuc["baslik"] = _baslik_tahmini(metin, meta, dosya_adi)
    sonuc["ozet_metni"] = _ozet_bul(metin)
    sonuc["bolumler"] = _bolumler(metin)
    sonuc["formuller"] = _formuller(metin)
    sonuc["sayisal"] = _sayisal_bulgular(metin)
    sonuc["kavramlar"] = _bilinen_kavramlar(metin)
    sonuc["fizik"] = fizik_ilgili(metin[:4000])

    d = _DOI.search(metin)
    if d:
        sonuc["doi"] = d.group(0).rstrip(".")
    a = _ARXIV.search(metin)
    if a:
        sonuc["arxiv"] = a.group(1)
    yillar = _YIL.findall(metin[:3000])
    if yillar:
        sonuc["yil"] = max("%s%s" % (y, "") for y in
                           re.findall(r"\b((?:19|20)\d{2})\b", metin[:3000]))

    # Ozetleme: once makalenin kendi ozeti, yoksa tum metin
    kaynak = sonuc["ozet_metni"] or metin[:60000]
    sonuc["ozet"] = retrieval.summarize([kaynak], query=sonuc.get("baslik", ""),
                                        max_sentences=6)
    sonuc["terimler"] = retrieval.key_terms([kaynak], top=12)
    sonuc["metin"] = metin
    return sonuc


# ── ogrenme ─────────────────────────────────────────────────────────────────

def ogren(sonuc):
    """Cozumlenen belgeyi kalici belleğe ekle (aranabilir hale getir)."""
    if sonuc.get("resim") or sonuc.get("bos"):
        return False
    metin = sonuc.get("metin") or ""
    ozet = sonuc.get("ozet_metni") or " ".join(sonuc.get("ozet") or [])
    if len(ozet) < 80:
        ozet = re.sub(r"\s+", " ", metin[:2000])
    if len(ozet) < 80:
        return False
    ext = sonuc.get("doi") or sonuc.get("arxiv") or os.path.basename(sonuc["yol"])
    ok, pid = db.add_paper(
        "yuklenen", ext, sonuc.get("baslik", sonuc["dosya"])[:400], ozet,
        (sonuc.get("meta", {}) or {}).get("yazar", ""),
        " ".join(t for t, _ in (sonuc.get("terimler") or []))[:400],
        "tr" if _turkce_mi(ozet) else "en",
        sonuc.get("doi") and ("https://doi.org/" + sonuc["doi"]) or sonuc["yol"],
        sonuc.get("yil", ""))
    try:
        db.conn().commit()
    except Exception:
        pass
    # Formulleri de havuza ekle
    for f in (sonuc.get("formuller") or []):
        db.queue_write(
            "INSERT INTO formulas_learned(latex, context, paper_id) "
            "VALUES(?,?,?) ON CONFLICT(latex) DO UPDATE SET seen = seen + 1",
            (f[:200], sonuc.get("baslik", "")[:200], pid or 0))
    return bool(ok)


def _turkce_mi(metin):
    t = (metin or "").lower()
    if any(c in t for c in "çğışöü"):
        return True
    tr = sum(1 for w in ("ve", "bir", "icin", "olarak", "ile", "bu")
             if (" %s " % w) in t)
    en = sum(1 for w in ("the", "and", "for", "with", "this", "of")
             if (" %s " % w) in t)
    return tr > en


def listele(limit=50):
    try:
        dosyalar = []
        for ad in sorted(os.listdir(BELGE_DIR), reverse=True)[:limit]:
            p = os.path.join(BELGE_DIR, ad)
            if os.path.isfile(p):
                dosyalar.append({"ad": ad, "boyut": os.path.getsize(p),
                                 "zaman": os.path.getmtime(p)})
        return dosyalar
    except OSError:
        return []
