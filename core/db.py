"""SQLite tabanli bilgi deposu.

Makalelerin tam metnini indirmiyoruz; sadece baslik + ozet (abstract) + adres
saklaniyor. Tam metin gerektiginde canli olarak internetten okunuyor.
FTS5 sayesinde yuz binlerce ozet icinde milisaniyeler icinde arama yapilabilir.
"""
import sqlite3
import threading
import queue
import time
import json
from . import config

_local = threading.local()

# Ogrenme motoru buyuk yazma islemleri yaparken SQLite'in tek yazar kilidi
# sohbet cevaplarini bekletmesin diye, kritik olmayan yazmalar (sohbet
# gecmisi, anlik ogrenilen makaleler) ayri bir is parcaciginda kuyruklanir.
_write_q = queue.Queue(maxsize=5000)
_writer_started = threading.Event()

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS papers (
    id          INTEGER PRIMARY KEY,
    source      TEXT NOT NULL,
    ext_id      TEXT NOT NULL,
    title       TEXT,
    abstract    TEXT,
    authors     TEXT,
    categories  TEXT,
    lang        TEXT,
    url         TEXT,
    published   TEXT,
    fetched_at  REAL,
    -- Kalite verisi: makalenin bilimsel agirligi ve guvenilirligi
    atif        INTEGER DEFAULT -1,   -- -1: bilinmiyor
    hakemli     INTEGER DEFAULT -1,   -- 1 hakemli, 0 onbaski, -1 bilinmiyor
    geri_cekik  INTEGER DEFAULT 0,    -- 1 ise geri cekilmis (asla alinmaz)
    alan        TEXT,                 -- kaynagin kendi alan siniflandirmasi
    dergi       TEXT,
    kalite      REAL DEFAULT 0,       -- hesaplanan kalite puani
    islendi     INTEGER DEFAULT 0,    -- bilgiye donusturuldu mu
    UNIQUE(source, ext_id)
);
CREATE INDEX IF NOT EXISTS idx_papers_kalite ON papers(kalite DESC);
CREATE INDEX IF NOT EXISTS idx_papers_islendi ON papers(islendi);
CREATE INDEX IF NOT EXISTS idx_papers_lang ON papers(lang);
CREATE INDEX IF NOT EXISTS idx_papers_src  ON papers(source);

CREATE VIRTUAL TABLE IF NOT EXISTS papers_fts USING fts5(
    title, abstract, categories,
    content='papers', content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER IF NOT EXISTS papers_ai AFTER INSERT ON papers BEGIN
    INSERT INTO papers_fts(rowid, title, abstract, categories)
    VALUES (new.id, new.title, new.abstract, new.categories);
END;
CREATE TRIGGER IF NOT EXISTS papers_ad AFTER DELETE ON papers BEGIN
    INSERT INTO papers_fts(papers_fts, rowid, title, abstract, categories)
    VALUES ('delete', old.id, old.title, old.abstract, old.categories);
END;

-- Kavramlar: Wikipedia ve ozetlerden ogrenilen fizik kavramlari
CREATE TABLE IF NOT EXISTS concepts (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    norm        TEXT NOT NULL,
    lang        TEXT NOT NULL,
    definition  TEXT,
    extract     TEXT,
    url         TEXT,
    freq        INTEGER DEFAULT 0,
    updated_at  REAL,
    UNIQUE(norm, lang)
);
CREATE INDEX IF NOT EXISTS idx_concepts_norm ON concepts(norm);

CREATE VIRTUAL TABLE IF NOT EXISTS concepts_fts USING fts5(
    name, definition, extract,
    content='concepts', content_rowid='id',
    tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS concepts_ai AFTER INSERT ON concepts BEGIN
    INSERT INTO concepts_fts(rowid, name, definition, extract)
    VALUES (new.id, new.name, new.definition, new.extract);
END;
CREATE TRIGGER IF NOT EXISTS concepts_au AFTER UPDATE ON concepts BEGIN
    INSERT INTO concepts_fts(concepts_fts, rowid, name, definition, extract)
    VALUES ('delete', old.id, old.name, old.definition, old.extract);
    INSERT INTO concepts_fts(rowid, name, definition, extract)
    VALUES (new.id, new.name, new.definition, new.extract);
END;

-- Kavramlar arasi birliktelik grafi (ayni ozette gecme sayisi)
CREATE TABLE IF NOT EXISTS concept_links (
    a       TEXT NOT NULL,
    b       TEXT NOT NULL,
    weight  INTEGER DEFAULT 0,
    PRIMARY KEY (a, b)
);
CREATE INDEX IF NOT EXISTS idx_links_a ON concept_links(a, weight DESC);

-- Terim istatistikleri (TF-IDF benzeri agirliklandirma icin)
CREATE TABLE IF NOT EXISTS terms (
    term    TEXT PRIMARY KEY,
    df      INTEGER DEFAULT 0,
    tf      INTEGER DEFAULT 0
);

-- Ozetlerden cikarilan LaTeX formulleri
CREATE TABLE IF NOT EXISTS formulas_learned (
    id        INTEGER PRIMARY KEY,
    latex     TEXT NOT NULL UNIQUE,
    context   TEXT,
    paper_id  INTEGER,
    seen      INTEGER DEFAULT 1
);

-- Ogrenme durumu / ilerleme
CREATE TABLE IF NOT EXISTS learn_state (
    key    TEXT PRIMARY KEY,
    value  TEXT
);

-- Kendi kendine kesif: arastirilmis terimler (tekrar denenmesin diye)
CREATE TABLE IF NOT EXISTS explored (
    term     TEXT PRIMARY KEY,
    kind     TEXT,
    found    INTEGER DEFAULT 0,
    at       REAL
);

-- Sohbet gecmisi
CREATE TABLE IF NOT EXISTS chat (
    id       INTEGER PRIMARY KEY,
    session  TEXT,
    role     TEXT,
    content  TEXT,
    ts       REAL
);
CREATE INDEX IF NOT EXISTS idx_chat_session ON chat(session, id);

-- Sohbetler (kenar cubugundaki gecmis listesi)
CREATE TABLE IF NOT EXISTS sessions (
    id       TEXT PRIMARY KEY,
    title    TEXT,
    created  REAL,
    updated  REAL
);
CREATE INDEX IF NOT EXISTS idx_sessions_upd ON sessions(updated DESC);

-- Sohbet baglami: "bunu biraz daha acar misin" gibi devam sorularinin
-- neye atifta bulundugunu hatirlamak icin
CREATE TABLE IF NOT EXISTS session_state (
    session  TEXT NOT NULL,
    key      TEXT NOT NULL,
    value    TEXT,
    PRIMARY KEY (session, key)
);

-- Makalelerden cikarilan yapilandirilmis bulgular.
-- Terim sayimi tek basina "inceleme" degildir; burada cumleler turlerine
-- ayrilip ilgili kavrama baglanir, boylece cevaplarda kullanilabilir.
-- ── Cozumlu problemler ────────────────────────────────────────────────────
-- Kullanicinin onceligi: "en onemli alan problem cozme". Makale ozeti bir
-- arastirma sonucunu anlatir, ders kitabi konuyu ogretir; ama problem
-- COZMEYI ancak cozulmus problemlere bakarak ogrenilebilir.
--
-- Burada her kayit bir problem metni ve (varsa) cozumudur. Bunlardan iki
-- sey cikarilir:
--   1. Dogrulanmis yeni bagintilar (SymPy + boyut denetiminden gecenler)
--   2. COZUM SEMASI: hangi turden verilerle hangi buyukluk aranmis ve
--      hangi bagintilar kullanilmis. Yeni bir problem geldiginde benzer
--      semalar ipucu olarak kullanilir.
CREATE TABLE IF NOT EXISTS problems (
    id        INTEGER PRIMARY KEY,
    kaynak    TEXT,          -- ocw | olimpiyat | kitap | yuklenen
    ext_id    TEXT UNIQUE,
    baslik    TEXT,
    ders      TEXT,
    url       TEXT,
    metin     TEXT NOT NULL, -- problemin kendisi
    cozum     TEXT,          -- varsa cozum metni
    konu      TEXT,          -- tahmini fizik konusu
    zorluk    TEXT,
    at        REAL
);
CREATE INDEX IF NOT EXISTS idx_prob_konu ON problems(konu, kaynak);

-- Cozum semalari: bir problemin imzasi -> kullanilan bagintilar.
-- Imza, verilen buyuklukerin ve aranan buyuklugun BOYUTLARINDAN olusur;
-- boylece "kutle + hiz -> enerji" gibi bir kalip, sayilardan bagimsiz
-- olarak eslesir.
CREATE TABLE IF NOT EXISTS semalar (
    id        INTEGER PRIMARY KEY,
    imza      TEXT NOT NULL,   -- "kg,m/s->J" gibi
    konu      TEXT,
    formuller TEXT NOT NULL,   -- virgulle ayrilmis formul id'leri
    kanit     INTEGER DEFAULT 1,  -- kac problemde ise yaradi
    hata      INTEGER DEFAULT 0,  -- kac problemde yanlis cikti
    ornek     TEXT,
    at        REAL,
    UNIQUE(imza, formuller)
);
CREATE INDEX IF NOT EXISTS idx_sema_imza ON semalar(imza, kanit DESC);

CREATE TABLE IF NOT EXISTS insights (
    id        INTEGER PRIMARY KEY,
    norm      TEXT,          -- ilgili kavram (normalize) ya da ''
    tur       TEXT,          -- tanim | bulgu | yontem | sayisal | iliski
    cumle     TEXT NOT NULL UNIQUE,
    paper_id  INTEGER,
    lang      TEXT,
    skor      REAL DEFAULT 0,
    at        REAL
);
CREATE INDEX IF NOT EXISTS idx_ins_norm ON insights(norm, tur, skor DESC);
CREATE INDEX IF NOT EXISTS idx_ins_tur  ON insights(tur, skor DESC);

-- Kavramlar arasi adlandirilmis iliskiler ("A, B'yi artirir")
CREATE TABLE IF NOT EXISTS relations (
    a       TEXT NOT NULL,
    fiil    TEXT NOT NULL,
    b       TEXT NOT NULL,
    sayi    INTEGER DEFAULT 1,
    ornek   TEXT,
    PRIMARY KEY (a, fiil, b)
);
CREATE INDEX IF NOT EXISTS idx_rel_a ON relations(a, sayi DESC);

-- Makalelerden ogrenilen bagintilar (denklemler).
-- Eski `formulas_learned` tablosu her `$...$` parcasini topluyordu ve hicbir
-- yerde kullanilmiyordu; bu tablo ayiklanmis ve dogrulanmis olanlari tutar.
CREATE TABLE IF NOT EXISTS learned_eq (
    id           INTEGER PRIMARY KEY,
    latex        TEXT NOT NULL UNIQUE,
    sade         TEXT,
    simgeler     TEXT,
    cozulebilir  INTEGER DEFAULT 0,
    baglam       TEXT,
    paper_id     INTEGER,
    konu         TEXT,
    seen         INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_leq_coz ON learned_eq(cozulebilir, seen DESC);

-- Kullanicinin ilgi alanlari (sohbetler arasi kalici)
CREATE TABLE IF NOT EXISTS interests (
    norm     TEXT PRIMARY KEY,
    label    TEXT,
    count    INTEGER DEFAULT 0,
    last_at  REAL
);
CREATE INDEX IF NOT EXISTS idx_interests_cnt ON interests(count DESC);
"""


def conn(busy_ms=15000):
    """Her is parcacigi (thread) icin ayri baglanti.

    WAL kipinde okumalar yazmayi beklemez; yalnizca yazmalar sirali olur.
    """
    c = getattr(_local, "conn", None)
    if c is None:
        c = sqlite3.connect(config.DB_PATH, timeout=busy_ms / 1000.0)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA busy_timeout=%d" % busy_ms)
        _local.conn = c
    return c


# --- kuyruklu yazici ---------------------------------------------------------

def _writer_loop():
    c = sqlite3.connect(config.DB_PATH, timeout=120.0)
    c.execute("PRAGMA busy_timeout=120000")
    while True:
        item = _write_q.get()
        if item is None:
            break
        try:
            batch = [item]
            # Ayni anda bekleyenleri tek islemde yaz
            while len(batch) < 200:
                try:
                    nxt = _write_q.get_nowait()
                except queue.Empty:
                    break
                if nxt is None:
                    break
                batch.append(nxt)
            for sql, args in batch:
                try:
                    c.execute(sql, args)
                except sqlite3.Error:
                    pass
            c.commit()
        except sqlite3.Error:
            try:
                c.rollback()
            except sqlite3.Error:
                pass
    try:
        c.close()
    except sqlite3.Error:
        pass


def start_writer():
    if _writer_started.is_set():
        return
    _writer_started.set()
    threading.Thread(target=_writer_loop, name="db-writer", daemon=True).start()


def queue_write(sql, args=()):
    """Cevabi bekletmeden yaz. Kuyruk dolarsa kayit sessizce atlanir."""
    start_writer()
    try:
        _write_q.put_nowait((sql, args))
        return True
    except queue.Full:
        return False


def flush_writes(timeout=5.0):
    """Testler icin: kuyruktaki yazmalarin bitmesini bekle."""
    end = time.time() + timeout
    while not _write_q.empty() and time.time() < end:
        time.sleep(0.02)
    time.sleep(0.08)


def init():
    c = conn()
    c.executescript(SCHEMA)
    c.commit()
    start_writer()


# --- yardimcilar ------------------------------------------------------------

def get_state(key, default=None):
    r = conn().execute("SELECT value FROM learn_state WHERE key=?", (key,)).fetchone()
    if r is None:
        return default
    try:
        return json.loads(r["value"])
    except Exception:
        return r["value"]


def set_state(key, value):
    c = conn()
    c.execute(
        "INSERT INTO learn_state(key,value) VALUES(?,?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, json.dumps(value, ensure_ascii=False)),
    )
    c.commit()


def bump_state(key, delta=1):
    cur = get_state(key, 0) or 0
    try:
        cur = int(cur)
    except Exception:
        cur = 0
    set_state(key, cur + delta)
    return cur + delta


def add_paper(source, ext_id, title, abstract, authors, categories, lang, url,
              published, atif=-1, hakemli=-1, geri_cekik=0, alan=None,
              dergi=None, kalite=0.0):
    c = conn()
    try:
        cur = c.execute(
            "INSERT OR IGNORE INTO papers"
            "(source,ext_id,title,abstract,authors,categories,lang,url,published,"
            " fetched_at,atif,hakemli,geri_cekik,alan,dergi,kalite)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (source, str(ext_id), title, abstract, authors, categories, lang, url,
             published, time.time(), atif, hakemli, geri_cekik, alan, dergi,
             kalite),
        )
        return cur.rowcount > 0, cur.lastrowid
    except sqlite3.Error:
        return False, None


def upsert_concept(name, norm, lang, definition, extract, url):
    c = conn()
    c.execute(
        "INSERT INTO concepts(name,norm,lang,definition,extract,url,freq,updated_at) "
        "VALUES(?,?,?,?,?,?,0,?) "
        "ON CONFLICT(norm,lang) DO UPDATE SET "
        "definition=COALESCE(NULLIF(excluded.definition,''), concepts.definition), "
        "extract=COALESCE(NULLIF(excluded.extract,''), concepts.extract), "
        "url=COALESCE(NULLIF(excluded.url,''), concepts.url), "
        "updated_at=excluded.updated_at",
        (name, norm, lang, definition, extract, url, time.time()),
    )


# --- sohbet oturumlari -------------------------------------------------------

def get_sstate(session, key, default=None):
    r = conn().execute("SELECT value FROM session_state WHERE session=? AND key=?",
                       (session, key)).fetchone()
    if r is None:
        return default
    try:
        return json.loads(r["value"])
    except Exception:
        return r["value"]


def set_sstate(session, key, value):
    c = conn()
    c.execute(
        "INSERT INTO session_state(session,key,value) VALUES(?,?,?) "
        "ON CONFLICT(session,key) DO UPDATE SET value=excluded.value",
        (session, key, json.dumps(value, ensure_ascii=False)))
    c.commit()


def touch_session(session, title=None):
    """Oturumu olustur/guncelle. Baslik yalnizca ilk kez yazilir."""
    c = conn()
    now = time.time()
    row = c.execute("SELECT id, title FROM sessions WHERE id=?", (session,)).fetchone()
    if row is None:
        c.execute("INSERT INTO sessions(id,title,created,updated) VALUES(?,?,?,?)",
                  (session, (title or "")[:90], now, now))
    else:
        if title and not (row["title"] or "").strip():
            c.execute("UPDATE sessions SET title=?, updated=? WHERE id=?",
                      ((title or "")[:90], now, session))
        else:
            c.execute("UPDATE sessions SET updated=? WHERE id=?", (now, session))
    c.commit()


def list_sessions(limit=60, ic_dahil=False):
    """Kullaniciya gosterilecek sohbetler.

    Alt cizgiyle baslayan oturumlar ICSELDIR (test takimi, olcumler,
    otomatik denemeler). Olculdu: test kosusundan sonra kenar cubugunda
    "_test_pr2 / merhaba", "_t_gok / gokyuzu neden mavi" gibi sekiz
    sohbet beliriyordu. Kullanicinin listesi onun konusmalarina aittir.
    """
    c = conn()
    suzgec = "" if ic_dahil else " AND s.id NOT LIKE '\_%' ESCAPE '\\' "
    rows = c.execute(
        "SELECT s.id, s.title, s.updated, "
        "  (SELECT COUNT(*) FROM chat WHERE chat.session = s.id) AS n "
        "FROM sessions s WHERE s.id IN (SELECT DISTINCT session FROM chat) "
        + suzgec +
        "ORDER BY s.updated DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]


def delete_all_sessions(immediate=False):
    """TUM sohbet gecmisini sil — ogrenilen bilgiye dokunmadan.

    Silinen: chat (mesajlar), sessions (sohbet listesi), session_state
    (sohbet basina hatirlanan konu/kisi).

    Silinmeyen: papers, concepts, insights, terms, relations,
    formulas_learned, learned_eq, derived, aliases, gaps, explored,
    concept_links. Yani sistem sohbetlerden ne ogrendiyse KALIR;
    yalnizca gorunen konusma dokumu gider.

    Doner: silinen mesaj ve sohbet sayisi.
    """
    c = conn()
    try:
        mesaj = c.execute("SELECT COUNT(*) FROM chat").fetchone()[0]
        sohbet = c.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    except Exception:
        mesaj = sohbet = 0
    stmts = [("DELETE FROM chat", ()),
             ("DELETE FROM session_state", ()),
             ("DELETE FROM sessions", ())]
    if immediate:
        for sql, args in stmts:
            c.execute(sql, args)
        c.commit()
    else:
        for sql, args in stmts:
            queue_write(sql, args)
    return {"mesaj": mesaj, "sohbet": sohbet}


def delete_session(session, immediate=False):
    """Sohbeti sil.

    Varsayilan olarak yazma kuyruguna verilir: ogrenme motoru buyuk bir yazma
    yapiyorken dogrudan DELETE, arayuzu kilit suresi boyunca bekletirdi.
    Testler icin `immediate=True` ile hemen silinebilir.
    """
    stmts = [("DELETE FROM chat WHERE session=?", (session,)),
             ("DELETE FROM session_state WHERE session=?", (session,)),
             ("DELETE FROM sessions WHERE id=?", (session,))]
    if immediate:
        c = conn()
        for sql, args in stmts:
            c.execute(sql, args)
        c.commit()
        return
    for sql, args in stmts:
        queue_write(sql, args)


def rename_session(session, title):
    c = conn()
    c.execute("UPDATE sessions SET title=? WHERE id=?", ((title or "")[:90], session))
    c.commit()


def stats():
    c = conn()

    def one(q, d=0):
        try:
            r = c.execute(q).fetchone()
            return r[0] if r and r[0] is not None else d
        except sqlite3.Error:
            return d

    return {
        "makale": one("SELECT COUNT(*) FROM papers"),
        "kavram": one("SELECT COUNT(*) FROM concepts"),
        "baglanti": one("SELECT COUNT(*) FROM concept_links"),
        "terim": one("SELECT COUNT(*) FROM terms"),
        "formul": one("SELECT COUNT(*) FROM learned_eq"),
        "cozulebilir_formul": one(
            "SELECT COUNT(*) FROM learned_eq WHERE cozulebilir=1"),
        "bulgu": one("SELECT COUNT(*) FROM insights"),
        "islenmis": one("SELECT COUNT(*) FROM papers WHERE islendi=1"),
        "islenmemis": one("SELECT COUNT(*) FROM papers WHERE islendi=0"),
        "hakemli": one("SELECT COUNT(*) FROM papers WHERE hakemli=1"),
        "onbaski": one("SELECT COUNT(*) FROM papers WHERE hakemli=0"),
        "ort_kalite": one("SELECT ROUND(AVG(kalite),1) FROM papers"),
        "reddedilen": int(get_state("total_rejected", 0) or 0),
        "iliski": one("SELECT COUNT(*) FROM relations"),
        "belge": one("SELECT COUNT(*) FROM papers WHERE source='yuklenen'"),
        "tr_makale": one("SELECT COUNT(*) FROM papers WHERE lang='tr'"),
        "en_makale": one("SELECT COUNT(*) FROM papers WHERE lang='en'"),
        "kaynaklar": [dict(r) for r in c.execute(
            "SELECT source, COUNT(*) n FROM papers GROUP BY source ORDER BY n DESC")],
        "son_guncelleme": get_state("last_cycle_time", 0),
        "tur": get_state("cycles", 0),
        "durum": get_state("learner_status", "beklemede"),
    }
