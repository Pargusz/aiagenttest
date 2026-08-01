# -*- coding: utf-8 -*-
"""KOPRU OGRENME: iki kavram arasindaki gecisi KENDI KENDINE ogrenmek.

Kullanicinin istegi net: *"az önce düzelttiğimiz soru var ya, o soruyu ele
alsın, benzer ve yine zor olan soruları kendi kendine öğrensin ... sürekli
yeni veriler geliyor, otomatik olarak onlarla kendini geliştirip cevaplar
üretebilmeli"*.

`gecisler.py` icindeki dort gecis ELLE yazildi. Bu dosya ayni isi kendi
basina yapar: hangi kavram ciftini baglayamadigini fark eder, korpustan o
baglantiyi arar, buldugunu DOGRULAR ve kalici olarak ogrenir. Sonraki
benzer soruda artik cevabi vardir.

Dongü su:

    1. KAPSAM DENETIMI  Bir soru iki kavram adlandirdi ama cevap yalnizca
       birine degdiyse, bu bir KOPRU BOSLUGUDUR; cift olarak kaydedilir.
    2. MADENCILIK       Cift icin korpusta (makale ozetleri, kavram
       tanimlari, ders metinleri) IKI kavrami birden anan ve aralarinda
       tureme/indirgeme bildiren cumleler aranir.
    3. DOGRULAMA        Kabul icin uc sart: en az IKI BAGIMSIZ kaynak,
       cumlenin iki kavrami da anmasi, ve varsa denklemlerin SymPy ile
       ayristirilabilmesi. Sarti gecemeyen aday atilir.
    4. OGRENME          Gecen aday `koprular` tablosuna yazilir; `kopru.py`
       elle yazilmis gecis bulamazsa buraya bakar.
    5. SINAV            Sistem kendi bilgi grafiginden ZOR sorular uretip
       kendini sinar; iki uca da degemedigi her soru 1. adima geri doner.

Boylece her yeni veri partisi, cevaplanamayan sorulari kendiliginden
azaltir. Ilerleme sayiyla izlenir: `sinav()` iki uca degme oranini verir.
"""
import re
import time

from . import db, knowledge, retrieval

# Iki kavram arasinda GECIS bildiren ifadeler. Bir cumle bunlardan birini
# tasiyorsa yalnizca "her ikisi de gecti" degil, "biri otekine baglaniyor"
# demektir. Ayirt edici olan budur.
# DIKKAT: burada gevsek bir kalip kullanmak sistemi kandirir. Olculdu:
# yalniz "derive[sd]" araninca "SI DERIVED unit of impulse" cumlesi
# momentum-Newton koprusu diye ogrenildi. Ize BAG SOZCUGU sart kosuluyor
# ("derived FROM", "reduces TO"), ciplak fiil kabul edilmiyor.
_GECIS_IZI = re.compile(
    r"\b(derived from|derivable from|derivation of|follows from|"
    r"reduces? to|reduced to|is recovered from|recovers the|"
    r"in the (non-?relativistic|classical|low-?(speed|energy)|"
    r"long-?wavelength|continuum|thermodynamic)? ?limit|"
    r"limiting case of|corresponds to|correspondence with|"
    r"generali[sz]ation of|generali[sz]es the|special case of|"
    r"equivalent to|obtained from|obtained by|can be derived|"
    r"is equivalent to|maps onto|analogous to|"
    # OZDESLIK/IFADE kaliplari da birer koprudur: "birinci yasa, enerjinin
    # korunumu yasasi OLARAK DA BILINIR" cumlesi iki kavrami birbirine
    # baglar. Olculdu: yalniz tureme kaliplariyla, iki kavrami birden
    # anan 17 cumlenin ancak 1'i geciyordu; asagidaki kaliplar dogru
    # cumleleri (birinci yasa = enerjinin korunumu) kurtardi.
    r"also known as|also called|is a formulation of|formulation of the|"
    r"is a statement of|statement of the|establish(es|ing) the|"
    r"expresses the|amounts to|is essentially the|is precisely the|"
    r"olarak da bilinir|olarak bilinir|bir ifadesidir|ifadesidir|"
    r"baska bir deyisle|yani |demektir|"
    r"turetilir|turetilebilir|elde edilir|indirgenir|indirgenebilir|"
    r"limitinde|ozel hali|ozel bir hali|karsilik gelir|"
    r"genellemesidir|genellemesi|denktir|yola cikarak)\b", re.I)

# Sozluk/birim tanimi cumleleri kopru degildir ("SI unit of ...").
_SOZLUK_CUMLESI = re.compile(
    r"\b(si (derived )?unit|unit of measurement|is the unit of|"
    r"named after|abbreviated|symbol is|birimi ?dir|kisaltmasi)\b", re.I)

# Denklem gibi gorunen parcalar
_DENKLEM = re.compile(r"[A-Za-zΑ-Ωα-ω_][A-Za-zΑ-Ωα-ω0-9_^{}\\]*\s*="
                      r"\s*[^.;,]{2,60}")

_EN_AZ_KAYNAK = 2        # bagimsiz kaynak sayisi esigi
_EN_AZ_CUMLE = 2         # kabul icin gereken cumle sayisi
_EN_FAZLA_DENEME = 4     # bu kadar denemeden sonra cift kapatilir

# Duz yazidan DENKLEM cikarimi KAPALI. Olculdu: ideal gaz + termodinamik
# koprusunde cikan "bagintilar" sunlardi — `T = 15`, `cold = 0`, `d = 6`,
# `f = 0`, `int = Q`, `mol = 0`. Hicbiri fiziksel bir baginti degil;
# ozet metnindeki kelime ve sayi kirintilari. SymPy bunlari sorunsuz
# ayristirdigi icin "gecerli" gorunuyorlardi.
#
# Ayni karari daha once PDF'ler icin de vermistik (problemler.py,
# PDF_BAGINTI_CIKAR = False). Koprunun degeri CUMLELERDE; dogrulanmamis
# denklem gostermek ogrenciyi yanlisa goturur. Guvenilir bir cikarim
# yontemi bulunursa buradan acilir.
PROZ_DENKLEM_CIKAR = False


def _kur():
    c = db.conn()
    c.execute("""CREATE TABLE IF NOT EXISTS koprular(
        a           TEXT NOT NULL,
        b           TEXT NOT NULL,
        govde       TEXT,
        denklemler  TEXT,
        kaynaklar   TEXT,
        kanit       INTEGER DEFAULT 0,
        dogrulandi  INTEGER DEFAULT 0,
        at          REAL,
        PRIMARY KEY(a, b)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS kopru_bosluk(
        a       TEXT NOT NULL,
        b       TEXT NOT NULL,
        soru    TEXT,
        sayi    INTEGER DEFAULT 1,
        denendi INTEGER DEFAULT 0,
        at      REAL,
        PRIMARY KEY(a, b)
    )""")
    # Kac kez denendi? Korpusta henuz malzeme yoksa cift KAPATILMAZ; yeni
    # veri geldikce tekrar denenir. Sinirsiz denemeyi onlemek icin sayac.
    try:
        c.execute("ALTER TABLE kopru_bosluk ADD COLUMN deneme INTEGER DEFAULT 0")
    except Exception:
        pass
    c.commit()


def _cift(a, b):
    """Cift her zaman ayni sirada saklanir."""
    return (a, b) if a <= b else (b, a)


# ── 1. Kapsam denetimi ─────────────────────────────────────────────────────

def kapsam_denetle(soru, cevap, lang="tr"):
    """Soru iki kavram andi da cevap yalnizca birine mi degdi?

    Deger dondurmez; eksik varsa bosluk olarak kaydeder. Bu, sistemin
    kendi zayifligini KENDI fark etmesidir — kullanicinin sikayet etmesini
    beklemez.
    """
    try:
        hits = knowledge.search(soru, limit=4) or []
    except Exception:
        return None
    if len(hits) < 2:
        return None
    tepe = hits[0][0]
    # Soruda GERCEKTEN adi gecen kavramlar: tepe puanin yarisindan iyi
    adaylar = [t for s, t in hits if s >= max(30, tepe * 0.5)]
    if len(adaylar) < 2:
        return None
    metin = (cevap or "").lower()
    degen = [t for t in adaylar if _konu_gecti(t, metin)]
    if len(degen) >= 2:
        return None                     # iki uca da degmis, sorun yok
    a, b = adaylar[0]["key"], adaylar[1]["key"]
    if a == b:
        return None
    bosluk_kaydet(a, b, soru)
    return (a, b)


def _konu_gecti(t, metin_kucuk):
    """Cevapta bu konunun izi var mi?"""
    for ad in (t.get("tr_title") or "", t.get("en_title") or ""):
        if ad and ad.lower()[:18] in metin_kucuk:
            return True
    # Baslik gecmese de ayirt edici anahtarlari gectiyse degmistir
    for kw in (t.get("kw") or [])[:8]:
        k = (kw or "").strip().lower()
        if len(k) >= 8 and k in metin_kucuk:
            return True
    return False


def bosluk_kaydet(a, b, soru=""):
    _kur()
    a, b = _cift(a, b)
    c = db.conn()
    c.execute("INSERT INTO kopru_bosluk(a, b, soru, sayi, at) "
              "VALUES(?,?,?,1,?) ON CONFLICT(a, b) DO UPDATE SET "
              "sayi = sayi + 1", (a, b, (soru or "")[:300], time.time()))
    c.commit()


# ── 2. Hangi cift uzerinde calisilacak ─────────────────────────────────────

def adaylar(limit=3):
    """Once KULLANICININ takildigi ciftler, sonra korpusun onerdikleri."""
    _kur()
    c = db.conn()
    out = []
    for r in c.execute(
            "SELECT a, b FROM kopru_bosluk WHERE denendi = 0 "
            "ORDER BY sayi DESC, at DESC LIMIT ?", (limit,)):
        out.append((r["a"], r["b"]))
    if len(out) >= limit:
        return out
    # Cekirdekte BIRBIRINE BAGLI ama arasindaki gecis yaziLI olmayan
    # konular: bunlar dogal kopru adaylaridir.
    bilinen = {(r["a"], r["b"]) for r in c.execute("SELECT a, b FROM koprular")}
    denenmis = {(r["a"], r["b"]) for r in c.execute(
        "SELECT a, b FROM kopru_bosluk WHERE denendi = 1")}
    for t in knowledge.TOPICS:
        for k in (t.get("related") or []):
            if not knowledge.get(k):
                continue
            cift = _cift(t["key"], k)
            if cift in bilinen or cift in denenmis or cift in out:
                continue
            out.append(cift)
            if len(out) >= limit:
                return out
    return out


# ── 3. Madencilik + dogrulama ──────────────────────────────────────────────

def _terimler(t):
    """Bir konunun metinde aranacak terimleri."""
    ad = []
    for x in (t.get("tr_title"), t.get("en_title")):
        if x:
            ad.append(x.lower())
    for kw in (t.get("kw") or []):
        k = (kw or "").strip().lower()
        if len(k) >= 5:
            ad.append(k)
    return ad[:14]


def _geciyor(metin_kucuk, terimler):
    return any(t in metin_kucuk for t in terimler)


def _konum(metin_kucuk, terimler):
    """Terimlerden herhangi birinin ilk gectigi yer; yoksa -1."""
    yerler = [metin_kucuk.find(t) for t in terimler]
    yerler = [y for y in yerler if y >= 0]
    return min(yerler) if yerler else -1


def _ayirt_edici(terimler):
    """Genel kelimeleri eleyip AYIRT EDICI terimleri birak.

    "enerji", "newton" gibi tek ve yaygin kelimeler her fizik metninde
    geciyor; bunlara dayanan bir eslesme kopru kaniti sayilmaz.
    """
    return [t for t in terimler if " " in t or len(t) >= 9]


def _baglayici_cumle(cumle, terim_a, terim_b):
    """Cumle GERCEKTEN iki kavrami birbirine mi bagliyor?

    Sart: her iki kavramin da AYIRT EDICI bir terimi cumlede gecmeli ve
    gecis izi bu iki anmanin ARASINDA durmali. "SI derived unit of
    impulse ... Newton" cumlesinde 'derived' en basta duruyor, iki anmanin
    arasinda degil — bu yuzden elenir (olculdu).
    """
    ck = cumle.lower()
    if _SOZLUK_CUMLESI.search(cumle):
        return False
    ay_a, ay_b = _ayirt_edici(terim_a), _ayirt_edici(terim_b)
    if not ay_a or not ay_b:
        return False
    pa, pb = _konum(ck, ay_a), _konum(ck, ay_b)
    if pa < 0 or pb < 0 or pa == pb:
        return False
    sol, sag = (pa, pb) if pa < pb else (pb, pa)
    # Iz cogu zaman kavramin hemen ONUNDE durur ("obtained from kinetic
    # theory", "follows from the equipartition theorem"). Bu yuzden tam
    # ARASINDA olmasini sart kosmak dogru cumleleri de eliyordu
    # (olculdu). Iki anmanin komsulugu yeterli; sozluk cumleleri ve
    # ciplak fiiller zaten yukarida elendi.
    for m in _GECIS_IZI.finditer(cumle):
        if sol - 80 <= m.start() <= sag + 40:
            return True
    return False


def _arama_terimleri(t, adet=3):
    """Bir konuyu korpusta ARAMAK icin en ise yarar terimler.

    Uzun Turkce basliklar ("Termodinamigin Yasalari") tam metin
    aramasinda kotu sorgudur; makale ozetleri Ingilizce ve kisa terimler
    kullanir. Onceligi Ingilizce basliga ve cok kelimeli Ingilizce
    anahtarlara veriyoruz (olculdu: basliklarla arayinca kavram cifti
    basina 0 kaynak donuyordu).
    """
    out = []
    en = (t.get("en_title") or "").strip()
    if en:
        out.append(en)
    for kw in (t.get("kw") or []):
        k = (kw or "").strip()
        # Ingilizce ve ayirt edici: bosluk iceren ya da uzun terimler
        if len(k) >= 7 and not re.search(r"[ıİşŞğĞçÇöÖüÜ]", k):
            if k.lower() != en.lower():
                out.append(k)
        if len(out) >= adet:
            break
    return out[:adet]


def _kaynak_metinleri(ta, tb, limit=14):
    """Iki kavrami birden anan kaynaklari getir."""
    sorgular = []
    for x in _arama_terimleri(ta):
        for y in _arama_terimleri(tb):
            sorgular.append("%s %s" % (x, y))
    kayitlar, gorulen = [], set()
    for q in sorgular[:6]:
        try:
            for p in retrieval.search_papers(q, limit=limit) or []:
                anahtar = p.get("url") or ("p%s" % p.get("id"))
                if anahtar in gorulen:
                    continue
                gorulen.add(anahtar)
                kayitlar.append({
                    "metin": (p.get("title") or "") + ". " +
                             (p.get("abstract") or ""),
                    "kaynak": anahtar,
                    "baslik": (p.get("title") or "")[:150]})
        except Exception:
            pass
        try:
            for k in retrieval.search_concepts(q, limit=6) or []:
                anahtar = k.get("url") or ("k%s" % k.get("name"))
                if anahtar in gorulen:
                    continue
                gorulen.add(anahtar)
                kayitlar.append({
                    "metin": (k.get("definition") or "") + " " +
                             (k.get("extract") or ""),
                    "kaynak": anahtar,
                    "baslik": (k.get("name") or "")[:150]})
        except Exception:
            pass
    return kayitlar


def _denklem_saglam_mi(ifade):
    """Denklem SymPy ile ayristirilabiliyor mu?

    Ayristirilamayan bir 'denklem' ya OCR kirintisidir ya da cumle
    parcasi. Ogrenilen bilgiye girmemeli — bu projenin kurali degismedi:
    dogrulanmamis sey ogretilmez.
    """
    try:
        import sympy
        sol, _, sag = ifade.partition("=")
        if not sol.strip() or not sag.strip():
            return False
        for parca in (sol, sag):
            p = parca.strip().replace("^", "**")
            if len(p) > 60 or not re.search(r"[A-Za-z0-9]", p):
                return False
            sympy.sympify(p, evaluate=False)
        return True
    except Exception:
        return False


def _aday_cikar(ta, tb, kayitlar):
    """Iki kavrami birden anan ve GECIS bildiren cumleleri topla."""
    terim_a, terim_b = _terimler(ta), _terimler(tb)
    cumleler, kaynaklar, denklemler = [], [], []
    for kayit in kayitlar:
        metin = kayit["metin"] or ""
        if len(metin) < 60:
            continue
        kucuk = metin.lower()
        if not (_geciyor(kucuk, terim_a) and _geciyor(kucuk, terim_b)):
            continue
        try:
            parcalar = retrieval.split_sentences(metin)
        except Exception:
            parcalar = [metin]
        secilen = []
        for c in parcalar:
            if len(c) < 45 or len(c) > 420:
                continue
            # Cumlenin KENDISI iki kavrami da anmali ve gecis izi bu iki
            # anmanin arasinda durmali. Gevsek denetimle alakasiz
            # cumleler kopru diye ogreniliyordu (olculdu).
            if not _baglayici_cumle(c, terim_a, terim_b):
                continue
            secilen.append(c.strip())
        if not secilen:
            continue
        cumleler.extend(secilen[:2])
        kaynaklar.append(kayit["kaynak"])
        if PROZ_DENKLEM_CIKAR:
            for m in _DENKLEM.findall(metin):
                ifade = m if isinstance(m, str) else m[0]
                if _denklem_saglam_mi(ifade):
                    denklemler.append(ifade.strip())
    return cumleler, sorted(set(kaynaklar)), sorted(set(denklemler))[:6]


def ogren(a, b):
    """Bir cift icin kopru ogrenmeyi dene. (durum, kanit) doner."""
    _kur()
    a, b = _cift(a, b)
    ta, tb = knowledge.get(a), knowledge.get(b)
    if not ta or not tb:
        return "konu yok", 0
    kayitlar = _kaynak_metinleri(ta, tb)
    cumleler, kaynaklar, denklemler = _aday_cikar(ta, tb, kayitlar)
    c = db.conn()
    # DOGRULAMA: iki bagimsiz kaynak ve iki cumle sarti.
    if len(kaynaklar) < _EN_AZ_KAYNAK or len(cumleler) < _EN_AZ_CUMLE:
        # Cift KAPATILMAZ: korpusta henuz malzeme olmayabilir. Deneme
        # sayaci artirilir ve ancak _EN_FAZLA_DENEME sonra vazgecilir.
        # Boylece yeni makaleler geldikce ayni cift tekrar denenir —
        # sistemin veri biriktikce kendiliginden gelismesi budur.
        c.execute("INSERT INTO kopru_bosluk(a, b, soru, deneme, denendi, at) "
                  "VALUES(?,?,'',1,0,?) ON CONFLICT(a, b) DO UPDATE SET "
                  "deneme = COALESCE(deneme, 0) + 1, "
                  "denendi = CASE WHEN COALESCE(deneme, 0) + 1 >= ? "
                  "THEN 1 ELSE 0 END",
                  (a, b, time.time(), _EN_FAZLA_DENEME))
        c.commit()
        return "yetersiz kanit", len(kaynaklar)
    c.execute("INSERT INTO kopru_bosluk(a, b, soru, denendi, at) "
              "VALUES(?,?,'',1,?) ON CONFLICT(a, b) DO UPDATE SET "
              "denendi = 1", (a, b, time.time()))
    c.commit()
    # Ayni cumleyi tekrar tekrar yazmayalim
    benzersiz, gorulen = [], set()
    for cm in cumleler:
        imza = re.sub(r"\W+", "", cm.lower())[:80]
        if imza in gorulen:
            continue
        gorulen.add(imza)
        benzersiz.append(cm)
    govde = "\n".join("- " + x for x in benzersiz[:6])
    c.execute("INSERT INTO koprular(a, b, govde, denklemler, kaynaklar, "
              "kanit, dogrulandi, at) VALUES(?,?,?,?,?,?,1,?) "
              "ON CONFLICT(a, b) DO UPDATE SET govde=excluded.govde, "
              "denklemler=excluded.denklemler, kaynaklar=excluded.kaynaklar, "
              "kanit=excluded.kanit, dogrulandi=1, at=excluded.at",
              (a, b, govde, "\n".join(denklemler), "\n".join(kaynaklar[:6]),
               len(kaynaklar), time.time()))
    c.commit()
    return "ogrenildi", len(kaynaklar)


# ── 4. Ogrenilen koprunun kullanimi ────────────────────────────────────────

def kopru_bul(a, b, lang="tr"):
    """Ogrenilmis kopru varsa gosterime hazir metnini dondur."""
    _kur()
    a, b = _cift(a, b)
    c = db.conn()
    r = c.execute("SELECT * FROM koprular WHERE a=? AND b=? AND "
                  "dogrulandi=1 AND kanit >= ?",
                  (a, b, _EN_AZ_KAYNAK)).fetchone()
    if not r or not (r["govde"] or "").strip():
        return None
    ta, tb = knowledge.get(a), knowledge.get(b)
    if not ta or not tb:
        return None
    ad = lambda t: t["tr_title"] if lang == "tr" else t["en_title"]
    bas = ("## %s ile %s arasındaki bağ" if lang == "tr"
           else "## How %s and %s connect")
    satir = [bas % (ad(ta), ad(tb)), ""]
    satir.append(("**Okuduğum kaynaklardan çıkardığım bağlantı:**"
                  if lang == "tr" else
                  "**The connection as I read it in the sources:**"))
    satir.append("")
    satir.append(r["govde"])
    if (r["denklemler"] or "").strip():
        satir.append(L2(lang, "\n**Kaynaklarda geçen bağıntılar:**",
                        "\n**Relations found in the sources:**"))
        for e in r["denklemler"].split("\n"):
            if e.strip():
                satir.append("- `%s`" % e.strip())
    satir.append(L2(lang,
                    "\n_Bu bağlantıyı %d bağımsız kaynaktan kendim "
                    "çıkardım; çekirdek anlatımlarımdan biri değil._"
                    % r["kanit"],
                    "\n_I derived this link myself from %d independent "
                    "sources; it is not one of my built-in topics._"
                    % r["kanit"]))
    return "\n".join(satir)


def L2(lang, tr, en):
    return tr if lang == "tr" else en


# ── 5. Kendi kendini sinama ────────────────────────────────────────────────

_SORU_KALIPLARI_TR = [
    "%s ile %s arasındaki ilişki nedir",
    "%s ile %s arasındaki geçişi açıkla",
    "%s konusundan %s konusuna nasıl geçilir",
]


def zor_sorular(adet=6):
    """Bilgi grafiginden ZOR (iki kavramli) sorular uret."""
    sorular = []
    for t in knowledge.TOPICS:
        for k in (t.get("related") or []):
            o = knowledge.get(k)
            if not o:
                continue
            kalip = _SORU_KALIPLARI_TR[len(sorular) % len(_SORU_KALIPLARI_TR)]
            sorular.append((kalip % (t["tr_title"], o["tr_title"]),
                            t["key"], o["key"]))
            if len(sorular) >= adet:
                return sorular
    return sorular


def sinav(adet=6, kaydet=True):
    """Kendi urettigi zor sorulari cevaplayip IKI UCA degme oranini olc.

    Bu, sistemin kendi ilerlemesini kullaniciya sormadan gormesidir.
    Degemedigi her soru bir kopru boslugu olarak geri doner ve bir
    sonraki ogrenme turunda hedef olur.
    """
    from . import brain
    sorular = zor_sorular(adet)
    if not sorular:
        return 0, 0
    dogru = 0
    for i, (soru, a, b) in enumerate(sorular):
        try:
            cevap = brain.respond(soru, session="_sinav_kopru%d" % i).text
        except Exception:
            cevap = ""
        ta, tb = knowledge.get(a), knowledge.get(b)
        kucuk = (cevap or "").lower()
        if ta and tb and _konu_gecti(ta, kucuk) and _konu_gecti(tb, kucuk):
            dogru += 1
        elif kaydet:
            bosluk_kaydet(a, b, soru)
    try:
        db.set_state("kopru_sinav", "%d/%d" % (dogru, len(sorular)))
    except Exception:
        pass
    return dogru, len(sorular)


def durum():
    """(ogrenilen_kopru, acik_bosluk, son_sinav) doner."""
    _kur()
    c = db.conn()
    try:
        k = c.execute("SELECT COUNT(*) FROM koprular WHERE dogrulandi=1"
                      ).fetchone()[0]
        bo = c.execute("SELECT COUNT(*) FROM kopru_bosluk WHERE denendi=0"
                       ).fetchone()[0]
    except Exception:
        k, bo = 0, 0
    return k, bo, (db.get_state("kopru_sinav", "-") or "-")
