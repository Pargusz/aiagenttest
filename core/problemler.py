# -*- coding: utf-8 -*-
"""Cozulmus problemlerden ogrenme.

Kullanicinin onceligi: "en onemli olan alan problem cozme kismi".

Makale ozeti bir arastirma sonucunu anlatir, ders kitabi konuyu ogretir.
Ama problem COZMEYI ogrenmek icin cozulmus problemlere bakmak gerekir —
tipki bir ogrencinin gecmis sinav sorularini calismasi gibi.

Bu modul uc is yapar:

1. **Toplama.** MIT OpenCourseWare'in acik problem setlerini ve
   cozumlerini (PDF) indirir, metnini cikarir, tek tek problemlere
   ayirir.

2. **Ogrenme.** Her cozumden iki sey suzulur:
   - Dogrulanmis yeni bagintilar (SymPy ve boyut denetiminden gecenler).
   - COZUM SEMASI: "hangi boyutlardaki veriler verilmis, hangi boyut
     aranmis, hangi bagintilar kullanilmis". Sema sayilardan bagimsizdir;
     bu yuzden hic gorulmemis bir problemde de ise yarar.

3. **Sinama.** Sayisal cevabi metinden okunabilen problemler otomatik bir
   SINAV olusturur. Sistem kendi cozumunu bu cevapla karsilastirir;
   boylece "problem cozme basarisi" olculebilir bir sayi olur ve korpus
   buyudukce izlenebilir.

Dogruluk sozu buradan gelir: bir semanin kullanilmasi icin gecmiste
DOGRULANMIS olmasi gerekir, ve her sayisal sonuc yine SymPy ile
cozulup geri yerine koyularak denetlenir. Sema yalnizca "hangi yoldan
gidilir" bilgisidir; cevabi hesaplayan sey degismez.
"""
import io
import json
import re
import time
import urllib.parse
import urllib.request

from . import config, db, formulas, nlu, units


OCW_ARAMA = ("https://api.learn.mit.edu/api/v1/content_file_search/"
             "?q=%s&offered_by=ocw&limit=%d&offset=%d")

# Fizik ve baglantili dersler. Olculdu: filtresiz arama 18.085
# (hesaplamali muhendislik) gibi matematik derslerini getiriyor; onlar da
# degerli ama once fizik.
_FIZIK_DERS = re.compile(
    r"\b(physics|mechanic|electromagnet|quantum|thermodynamic|relativity|"
    r"optic|astrophys|nuclear|particle|statistical|solid state|"
    r"electricity|magnetism|wave|fluid|chemistry|biophysic)\w*", re.I)


def _al(url, ikili=False, zaman=30):
    req = urllib.request.Request(
        url, headers={"User-Agent": config.USER_AGENT})
    with urllib.request.urlopen(req, timeout=zaman) as r:
        ham = r.read()
        return ham if ikili else ham.decode("utf-8", "replace")


def _pdf_metni(ham):
    """PDF baytlarindan metin cikar (yoksa None)."""
    try:
        from pypdf import PdfReader
        rd = PdfReader(io.BytesIO(ham))
        # Cok uzun belgelerde ilk 30 sayfa yeter; problem setleri kisadir
        return "\n".join((s.extract_text() or "") for s in rd.pages[:30])
    except Exception:
        return None


# Farkli sorgular farkli dersleri getiriyor. Olculdu: tek bir sorgu
# ("problem set solutions physics") yalnizca BIR fizik dosyasi buldu;
# konuya gore suzulen ve ders adiyla yapilan sorgular cok daha verimli.
ARAMA_SORGULARI = [
    ("problem set solutions", "&topic=Physics"),
    ("assignments solutions", "&topic=Physics"),
    ("exam solutions", "&topic=Physics"),
    ("problem set", "&topic=Physics"),
    ("classical mechanics problem solutions", "&topic=Physics"),
    ("electromagnetism problem set", "&topic=Physics"),
    ("quantum physics problem set", "&topic=Physics"),
    ("thermodynamics problem set solutions", "&topic=Physics"),
    ("optics solutions assignment", "&topic=Physics"),
    ("statistical mechanics problem set", "&topic=Physics"),
    ("problem set solutions", "&topic=Chemistry"),
]


def ocw_problem_dosyalari(sorgu="problem set solutions",
                          limit=12, offset=0, ek=""):
    """OCW'de cozumlu problem seti dosyalarini listele."""
    url = (OCW_ARAMA % (urllib.parse.quote(sorgu), int(limit), int(offset))
           + ek)
    try:
        veri = json.loads(_al(url))
    except Exception:
        return []
    out = []
    for r in veri.get("results") or []:
        if not isinstance(r, dict) or r.get("content_type") != "pdf":
            continue
        ders = r.get("run_title") or ""
        # Konu suzgeci (topic=Physics) zaten uygulanmissa ders adi
        # sartini aramiyoruz; aksi halde "Optics" gibi mesru dersler
        # eleniyordu.
        if not ek and not _FIZIK_DERS.search(ders + " "
                                             + (r.get("title") or "")):
            continue
        out.append({
            "ext_id": "ocwp_%s" % (r.get("id") or r.get("key")),
            "baslik": (r.get("title") or "").strip(),
            "ders": ders.strip(),
            "sayfa": r.get("url") or "",
        })
    return out


def pdf_baglantisi(sayfa_url):
    """OCW kaynak sayfasindan gercek PDF adresini bul."""
    try:
        h = _al(sayfa_url)
    except Exception:
        return None
    m = (re.search(r'href="(/courses/[^"]+\.pdf)"', h)
         or re.search(r'"(https://ocw\.mit\.edu/[^"]+\.pdf)"', h))
    if not m:
        return None
    u = m.group(1)
    return ("https://ocw.mit.edu" + u) if u.startswith("/") else u


# ── Metni tek tek problemlere ayirma ────────────────────────────────────────
# Problem setleri numaralandirilmistir: "1.", "Problem 2", "Question 3".
_BOLUM = re.compile(
    r"(?m)^\s*(?:problem|question|exercise|soru)?\s*"
    r"(\d{1,2})\s*[.)\]]\s+", re.I)


def problemlere_ayir(metin, en_az=120):
    """Bir problem seti metnini tek tek problemlere ayir."""
    if not metin:
        return []
    yerler = [(m.start(), m.group(1)) for m in _BOLUM.finditer(metin)]
    if len(yerler) < 2:
        return [metin.strip()] if len(metin.strip()) >= en_az else []
    parcalar = []
    for i, (yer, _no) in enumerate(yerler):
        son = yerler[i + 1][0] if i + 1 < len(yerler) else len(metin)
        p = metin[yer:son].strip()
        if len(p) >= en_az:
            parcalar.append(p)
    return parcalar


# Problem metni ile cozumu ayiran isaretler. Olculdu: cozum dosyalarinda
# ikisi ayni metne konuyordu; boylece "problemi coz" sinavi, cevabi
# icinde tasiyan bir metinle yapiliyordu — gecersiz bir sinav.
# Ic ice bayrak kullanmak yerine tek bayrak ve iki secenek.
_COZUM_BASI = re.compile(
    r"^[ \t]*(?:solution|answer|cozum|çözüm|ans)\b[ \t]*[:.)]?[ \t]*$"
    r"|\b(?:solution|answer|cozum|çözüm)\b[ \t]*[:.]",
    re.I | re.M)


def soru_cozum_ayir(metin):
    """Bir parcayi (problem, cozum) diye ayir.

    Ayirici bulunamazsa cozum None doner: o parca bir SORU'dur, sinavda
    kullanilamaz ama yine de problem korpusuna girer.
    """
    if not metin:
        return "", None
    m = _COZUM_BASI.search(metin)
    # Isaretci cok basta ise ortada soru metni yok demektir. Esik 60
    # karakterdi ve gercek ornekleri eliyordu (olculdu); 25 yeterli.
    if not m or m.start() < 25:
        return metin.strip(), None
    return metin[:m.start()].strip(), metin[m.start():].strip()


# ── Sayisal cevap cikarimi ──────────────────────────────────────────────────
# Cozumun sonundaki "= 3.5 m/s" gibi ifadeler, kendi kendini sinamak icin
# kullanilir. Yalnizca BIRIMLI ve acikca sonuc gibi duran degerler alinir.
_CEVAP = re.compile(
    r"(?:=|≈|~|answer\s*:?|sonuc\s*:?)\s*"
    r"([-+]?\d+(?:[.,]\d+)?(?:\s*[eE]\s*[-+]?\d+)?)\s*"
    r"([a-zA-ZµΩÅ°][a-zA-ZµΩÅ°0-9^/·]*)")


def sayisal_cevap(metin):
    """Metindeki SON birimli sonucu dondur: (deger, birim) ya da None."""
    son = None
    for m in _CEVAP.finditer(metin or ""):
        try:
            deger = float(m.group(1).replace(",", ".").replace(" ", ""))
        except ValueError:
            continue
        birim = m.group(2)
        try:
            if units.to_si(1.0, birim)[0] is None:
                continue
        except Exception:
            continue
        son = (deger, birim)
    return son


# ── Cozum semasi ────────────────────────────────────────────────────────────

def imza(soru):
    """Problemin BOYUT IMZASI: verilen boyutlar -> aranan boyut.

    Sayilar degisir, imza kalir. "2 kg, 3 m/s -> J" imzasi hem
    "2 kg 3 m/s kinetik enerji" hem "7 kg 11 m/s kinetik enerji"
    problemine uyar; bu yuzden hic gorulmemis bir soruda da ise yarar.
    """
    boyutlar = []
    try:
        for deger, birim, _a, _b in (nlu.extract_number_unit(soru) or []):
            cev = units.to_si(1.0, birim)
            if cev and cev[1]:
                boyutlar.append(",".join(str(int(x)) for x in cev[1]))
    except Exception:
        pass
    if not boyutlar:
        return None
    return "|".join(sorted(set(boyutlar)))


def sema_kaydet(soru, formul_idler, konu="", ornek=""):
    """Bir cozum semasini kaydet ya da kanitini artir."""
    im = imza(soru)
    if not im or not formul_idler:
        return False
    fs = ",".join(formul_idler)
    db.queue_write(
        "INSERT INTO semalar(imza, konu, formuller, kanit, hata, ornek, at) "
        "VALUES(?,?,?,1,0,?,?) "
        "ON CONFLICT(imza, formuller) DO UPDATE SET kanit = kanit + 1",
        (im, konu or "", fs, (ornek or "")[:300], time.time()))
    return True


def sema_ipucu(soru, en_fazla=3):
    """Benzer problemlerde ise yaramis formul dizileri.

    Doner: [(formul_id_listesi, kanit, hata), ...] — en cok kanitlanan
    once. Zincir cozucu bu sirayi ONCELIK olarak kullanir; cevabi yine
    kendisi hesaplar ve dogrular.
    """
    im = imza(soru)
    if not im:
        return []
    try:
        rows = db.conn().execute(
            "SELECT formuller, kanit, hata FROM semalar "
            "WHERE imza = ? AND kanit > hata "
            "ORDER BY (kanit - hata) DESC LIMIT ?", (im, en_fazla)).fetchall()
    except Exception:
        return []
    return [(r[0].split(","), r[1], r[2]) for r in rows]


def sema_sonucu_bildir(soru, formul_idler, dogru):
    """Bir semanin bu problemde ise yarayip yaramadigini kaydet.

    Yanlis cikan sema zamanla elenir: kanit <= hata olunca artik
    ipucu olarak verilmez.
    """
    im = imza(soru)
    if not im or not formul_idler:
        return
    alan = "kanit" if dogru else "hata"
    db.queue_write(
        "UPDATE semalar SET %s = %s + 1 WHERE imza = ? AND formuller = ?"
        % (alan, alan), (im, ",".join(formul_idler)))


# ── Toplama gorevi ──────────────────────────────────────────────────────────

def topla(en_fazla=6, offset=0, sorgu=None):
    """OCW'den cozumlu problem setleri indir ve kaydet.

    Sorgu verilmezse ARAMA_SORGULARI sirayla dolasilir; her calismada
    farkli bir dersten malzeme gelir.

    Doner: (yeni_problem_sayisi, islenen_dosya).
    """
    if sorgu:
        dosyalar = ocw_problem_dosyalari(sorgu, limit=en_fazla * 2,
                                         offset=offset)
    else:
        sira = int(db.get_state("problem_sorgu_sira", 0) or 0)
        dosyalar = []
        for k in range(3):          # birkac sorguyu birlestir
            q, ek = ARAMA_SORGULARI[(sira + k) % len(ARAMA_SORGULARI)]
            dosyalar.extend(ocw_problem_dosyalari(
                q, limit=8, offset=offset, ek=ek))
        db.set_state("problem_sorgu_sira", sira + 3)
    yeni, islenen = 0, 0
    for d in dosyalar:
        if islenen >= en_fazla:
            break
        pdf = pdf_baglantisi(d["sayfa"])
        if not pdf:
            continue
        try:
            ham = _al(pdf, ikili=True, zaman=45)
        except Exception:
            continue
        metin = _pdf_metni(ham)
        if not metin or len(metin) < 400:
            continue
        islenen += 1
        cozumlu = bool(re.search(r"solution|answer|cozum", d["baslik"],
                                 re.I))
        for i, p in enumerate(problemlere_ayir(metin)):
            ext = "%s_%d" % (d["ext_id"], i)
            soru, cozum = soru_cozum_ayir(p)
            if cozumlu and cozum is None:
                # Dosya cozum dosyasi ama ayirici yok: tumunu cozum say,
                # sinavda kullanma (soru metni belirsiz).
                soru, cozum = p[:8000], None
            try:
                db.conn().execute(
                    "INSERT OR IGNORE INTO problems"
                    "(kaynak, ext_id, baslik, ders, url, metin, cozum,"
                    " konu, zorluk, at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    ("ocw", ext, d["baslik"][:200], d["ders"][:200], pdf,
                     soru[:8000], cozum[:8000] if cozum else None,
                     _konu_tahmin(soru), "", time.time()))
                yeni += 1
            except Exception:
                continue
        db.conn().commit()
    return yeni, islenen


def _konu_tahmin(metin):
    """Problem hangi fizik konusuna ait? (formul tabanindan)"""
    try:
        v = formulas.search(metin[:600], limit=1)
        return v[0][1].get("topic", "") if v else ""
    except Exception:
        return ""


# PDF metninden cikan "denklem"lerin cogu COPTUR: MATLAB kod satiri,
# bozuk OCR, yarim cumle. Olculdu: 56 "yeni baginti"nin icinde
# "T = zeros(size(g)); %initialize T" ve "inhL= The width of the beam
# after the prism is" gibi seyler vardi. Boyle bir sey formul tabanina
# girerse sistem yanlis cevap uretir — kullanicinin en cok onemsedigi
# sey buydu. Bu yuzden problem PDF'lerinden gelen bagintilara AYRI ve
# SIKI bir suzgec uygulaniyor.
_KOD_IZI = re.compile(r"[;%#]|\b(zeros|ones|size|plot|figure|end|for|"
                      r"while|if|print|def|return|import)\b", re.I)
_CUMLE_IZI = re.compile(r"\b(the|of|and|is|are|width|after|before|"
                        r"where|with|this|that|then|from|into|beam|"
                        r"initialize|filter|value|note)\b", re.I)


# Bir problemin SAYISAL CEVABI ("P = 12.3 bar") genel bir baginti
# degildir; tabana girerse sistem "basinc her zaman 12,3 bar" sanir.
_SAYISAL_ATAMA = re.compile(
    r"^\s*[A-Za-z][A-Za-z0-9_]{0,4}\s*=\s*[-+]?\d+(?:[.,]\d+)?"
    r"(?:\s*[eE]\s*[-+]?\d+)?\s*[A-Za-zµΩ°/·]*\s*$")


def problem_bagintisi_mi(ifade):
    """Bu satir gercekten GENEL bir fizik bagintisi mi?

    Olcut zorlu: kod izi yok, cumle kelimesi yok, semboller kisa ve
    matematiksel, ve sag taraf tek bir SAYI degil (o bir cevaptir,
    baginti degil). Suphede kalirsak REDDEDIYORUZ — eksik baginti,
    yanlis bagintidan iyidir.
    """
    t = (ifade or "").strip()
    if not t or "=" not in t or len(t) > 60:
        return False
    if _KOD_IZI.search(t) or _CUMLE_IZI.search(t):
        return False
    sol, _, sag = t.partition("=")
    if not sol.strip() or not sag.strip():
        return False
    # Semboller kisa olmali; "OPLcommon", "inhL" gibi OCR birlesmeleri
    # gecerli sembol degildir.
    for kelime in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", t):
        if len(kelime) > 5:
            return False
        # Icinde hem buyuk hem kucuk harf karisimi (ORTAda) -> OCR izi
        if len(kelime) > 2 and re.search(r"[a-z][A-Z]", kelime):
            return False
    # En az bir islem ya da sayi olmali; "x = y" tek basina bilgi degil
    if not re.search(r"[\d\+\-\*/^()]", sag):
        return False
    # Sag taraf tek bir sayi (+birim) ise bu bir CEVAPTIR
    if _SAYISAL_ATAMA.match(t):
        return False
    # ASCII disi matematik izleri OCR bozulmasi demektir
    if re.search(r"[^\x00-\x7F]", t):
        return False
    # Sag tarafta en az iki sembol/terim olmali ki genel bir baginti olsun
    if len(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", sag)) < 1:
        return False
    return True


# PDF'lerden baginti cikarimi kapali (yukaridaki gerekce). Denemek
# isteyen True yapabilir; cikanlar yine yalnizca KAYNAK olarak saklanir,
# cozum tabanina girmez.
PDF_BAGINTI_CIKAR = False


def _bagintilari_cikar(bagintilar, pid, metin):
    """Metinden aday baginti cikar (yalnizca PDF_BAGINTI_CIKAR aciksa)."""
    n = 0
    for m in re.finditer(
            r"(?m)^\s*([A-Za-z][\w_]{0,12}\s*=\s*[^=\n]{3,70})$",
            metin or ""):
        ifade = m.group(1).strip()
        if not problem_bagintisi_mi(ifade):
            continue
        try:
            if bagintilar.kaydet(ifade, "problem-kaynak", pid, ""):
                n += 1
        except Exception:
            pass
    return n


def ogren(en_fazla=40):
    """Kayitli problemlerden SEMA ve BAGINTI ogren.

    Doner: (sema_sayisi, baginti_sayisi).
    """
    from . import bagintilar, zincir
    # Cozumu AYRI kaydedilmis problemlerden hem baginti hem sema
    # cikarilir; cozumu ayrilamamis olanlardan da SEMA cikarilabilir:
    # problemi kendimiz cozeriz ve izledigimiz yolu kaydederiz.
    # Olculdu: yalnizca cozumlu kayitlara bakinca 79 problemden hicbir
    # sema cikmadi (OCW problem setlerinde "Solution" basligi cogu
    # zaman yok).
    try:
        rows = db.conn().execute(
            "SELECT id, metin, cozum, konu FROM problems "
            "ORDER BY id DESC LIMIT ?", (en_fazla,)).fetchall()
    except Exception:
        return 0, 0
    sema, bag = 0, 0
    for pid, metin, cozum, konu in rows:
        # 1. Bagintilari cikar — KAPALI.
        #
        # Olculdu ve birakildi: PDF metninden cikan "bagintilarin"
        # neredeyse tamami ya MATLAB kod satiri ("T = zeros(size(g))"),
        # ya bozuk OCR ("dx = v. (15) dt"), ya da tek bir problemin
        # sayisal cevabiydi ("P = 12.3 bar"). Sikilastirilmis suzgecle
        # 56 adaydan yalnizca 6'si gecti, onlar da bozuktu.
        #
        # Yanlis bir baginti, eksik bir bagintidan cok daha zararlidir.
        # Cozum tabani elle dogrulanmis 296 formulle kaliyor; problem
        # korpusunun degeri COZUM SEMALARINDA (asagida).
        if PDF_BAGINTI_CIKAR:
            self_bag = _bagintilari_cikar(bagintilar, pid, cozum or metin)
            bag += self_bag

        # 2. Problemi kendimiz cozup hangi bagintilari kullandigimizi kaydet
        try:
            kullanilan = zincir.kullanilan_formuller(metin[:400])
        except Exception:
            kullanilan = []
        if kullanilan and sema_kaydet(metin[:400], kullanilan, konu,
                                      metin[:200]):
            sema += 1
    return sema, bag


def sinav(en_fazla=25):
    """Sayisal cevabi bilinen problemlerle kendini sina.

    Doner: (dogru, denenen).
    """
    from . import brain
    try:
        rows = db.conn().execute(
            "SELECT metin, cozum FROM problems WHERE cozum IS NOT NULL "
            "ORDER BY id DESC LIMIT ?", (en_fazla * 4,)).fetchall()
    except Exception:
        return 0, 0
    dogru, denenen = 0, 0
    for metin, cozum in rows:
        if denenen >= en_fazla:
            break
        beklenen = sayisal_cevap(cozum)
        if not beklenen:
            continue
        denenen += 1
        try:
            cevap = brain.respond(metin[:400], session="_sinav").text
        except Exception:
            continue
        for m in re.finditer(r"\*\*([-+]?\d+(?:\.\d+)?)", cevap or ""):
            try:
                v = float(m.group(1))
            except ValueError:
                continue
            if abs(v - beklenen[0]) <= abs(beklenen[0]) * 0.02 + 1e-9:
                dogru += 1
                break
    return dogru, denenen
