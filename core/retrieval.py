"""Bilgi getirme ve ozetleme.

Ogrenilmis veritabaninda (FTS5 + BM25) arama yapar, gerektiginde canli olarak
internetten ceker ve cikarimsal (extractive) ozetleme uygular.
Ozetleme yapay sinir agi kullanmaz; TF-IDF agirlikli cumle skorlama,
konum sezgileri ve MMR benzeri cesitlilik secimi ile calisir.
"""
import math
import re
import time

from . import db, sources
from .learner import tokens, normalize, STOP

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ0-9])")


def fts_escape(q):
    """FTS5 sorgusu icin guvenli hale getir."""
    words = re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]+", q)
    words = [w for w in words if len(w) > 2 and normalize(w) not in STOP]
    if not words:
        words = re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]+", q)
    if not words:
        return None
    return " OR ".join('"%s"' % w.replace('"', '') for w in words[:12])


def search_papers(query, limit=8, lang=None, min_kalite=0):
    """Ogrenilmis makale ozetlerinde ara.

    Siralama yalnizca metin benzerligine (BM25) degil, makalenin kalite
    puanina da bakar: hakemli, atif almis ve alani kesin olan makaleler one
    cikar. Boylece ayni konuda iki kaynak varsa daha saglam olani gosterilir.
    """
    m = fts_escape(query)
    if not m:
        return []
    c = db.conn()
    sql = ("SELECT p.id, p.title, p.abstract, p.authors, p.url, p.source, "
           "p.lang, p.published, p.categories, p.kalite, p.atif, p.hakemli, "
           "p.dergi, bm25(papers_fts) AS score "
           "FROM papers_fts JOIN papers p ON p.id = papers_fts.rowid "
           "WHERE papers_fts MATCH ? ")
    args = [m]
    if lang:
        sql += "AND p.lang = ? "
        args.append(lang)
    if min_kalite:
        sql += "AND p.kalite >= ? "
        args.append(min_kalite)
    # bm25 dusukse daha iyi; kalite yuksekse daha iyi. Ikisini birlestiriyoruz.
    sql += "ORDER BY (score - COALESCE(p.kalite, 0) / 25.0) LIMIT ?"
    args.append(limit)
    try:
        return [dict(r) for r in c.execute(sql, args)]
    except Exception:
        return []


def search_concepts(query, limit=6, lang=None):
    m = fts_escape(query)
    if not m:
        return []
    c = db.conn()
    sql = ("SELECT co.id, co.name, co.definition, co.extract, co.url, co.lang, "
           "co.freq, bm25(concepts_fts) AS score "
           "FROM concepts_fts JOIN concepts co ON co.id = concepts_fts.rowid "
           "WHERE concepts_fts MATCH ? ")
    args = [m]
    if lang:
        sql += "AND co.lang = ? "
        args.append(lang)
    sql += "ORDER BY score LIMIT ?"
    args.append(limit)
    try:
        return [dict(r) for r in c.execute(sql, args)]
    except Exception:
        return []


def related_concepts(name, limit=8):
    """Kavram grafinden iliskili kavramlari getir."""
    c = db.conn()
    n = normalize(name)
    rows = c.execute(
        "SELECT cl.b AS other, cl.weight, co.name FROM concept_links cl "
        "LEFT JOIN concepts co ON co.norm = cl.b "
        "WHERE cl.a = ? ORDER BY cl.weight DESC LIMIT ?", (n, limit)).fetchall()
    return [{"norm": r["other"], "name": r["name"] or r["other"],
             "weight": r["weight"]} for r in rows]


# Belge sayisi bellekte tutuluyor: her cumle skorlamasinda veritabanina
# yazmak, ogrenme motoru calisirken cevaplari bekletirdi.
_doc_count = {"n": 0, "at": 0.0}


def doc_count(max_age=120.0):
    now = time.time()
    if _doc_count["n"] and (now - _doc_count["at"]) < max_age:
        return _doc_count["n"]
    try:
        r = db.conn().execute("SELECT COUNT(*) n FROM papers").fetchone()
        _doc_count["n"] = (r["n"] if r else 0) or 1
    except Exception:
        _doc_count["n"] = _doc_count["n"] or 1
    _doc_count["at"] = now
    return _doc_count["n"]


def idf(term):
    """Ogrenilmis korpustan ters dokuman frekansi."""
    total = doc_count()
    try:
        row = db.conn().execute("SELECT df FROM terms WHERE term = ?",
                                (term,)).fetchone()
        d = row["df"] if row else 0
    except Exception:
        d = 0
    return math.log((total + 1.0) / (d + 1.0)) + 1.0


def split_sentences(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    parts = _SENT_SPLIT.split(text)
    out = []
    for p in parts:
        p = p.strip()
        if len(p) > 25:
            out.append(p)
        elif out:
            out[-1] += " " + p
    return out or ([text] if text else [])


def summarize(texts, query="", max_sentences=5, use_corpus_idf=True):
    """Cikarimsal ozetleme.

    Cumleleri TF-IDF benzeri agirlikla puanlar, sorgu terimleriyle ortusmeyi
    odullendirir ve birbirine cok benzeyen cumleleri elemek icin MMR uygular.
    """
    if isinstance(texts, str):
        texts = [texts]
    sents = []
    for t in texts:
        sents.extend(split_sentences(t))
    if not sents:
        return []
    if len(sents) <= max_sentences:
        return sents

    qterms = set(tokens(query)) if query else set()
    # Yerel terim frekansi
    local_tf = {}
    sent_toks = []
    for s in sents:
        tk = list(tokens(s))
        sent_toks.append(tk)
        for t in set(tk):
            local_tf[t] = local_tf.get(t, 0) + 1

    idf_cache = {}

    def w(t):
        if t not in idf_cache:
            if use_corpus_idf:
                try:
                    idf_cache[t] = idf(t)
                except Exception:
                    idf_cache[t] = math.log(len(sents) / (local_tf.get(t, 1) + 0.5))
            else:
                idf_cache[t] = math.log(len(sents) / (local_tf.get(t, 1) + 0.5))
        return idf_cache[t]

    scores = []
    for i, (s, tk) in enumerate(zip(sents, sent_toks)):
        if not tk:
            scores.append(0.0)
            continue
        base = sum(w(t) for t in set(tk)) / (len(set(tk)) ** 0.5)
        # Sorgu ortusmesi bonusu
        overlap = len(qterms & set(tk))
        base *= (1.0 + 0.45 * overlap)
        # Ilk cumleler genellikle daha bilgilendirici (ozetlerde tez cumlesi)
        base *= (1.25 if i == 0 else (1.10 if i == 1 else 1.0))
        # Cok kisa/uzun cumleleri hafifce cezalandir
        L = len(s.split())
        if L < 8:
            base *= 0.6
        elif L > 55:
            base *= 0.85
        scores.append(base)

    chosen = []
    chosen_toks = []
    order = sorted(range(len(sents)), key=lambda i: -scores[i])
    for i in order:
        if len(chosen) >= max_sentences:
            break
        tk = set(sent_toks[i])
        if not tk:
            continue
        # Cesitlilik: onceden secilenlerle asiri ortusuyorsa atla
        redundant = False
        for ct in chosen_toks:
            inter = len(tk & ct)
            union = len(tk | ct) or 1
            if inter / union > 0.55:
                redundant = True
                break
        if redundant:
            continue
        chosen.append(i)
        chosen_toks.append(tk)
    chosen.sort()
    return [sents[i] for i in chosen]


def key_terms(texts, top=10, query=""):
    """Metinlerden en ayirt edici terimleri cikar."""
    if isinstance(texts, str):
        texts = [texts]
    tf = {}
    for t in texts:
        for w in tokens(t):
            tf[w] = tf.get(w, 0) + 1
    scored = []
    for t, n in tf.items():
        if len(t) < 4:
            continue
        try:
            scored.append((n * idf(t), t, n))
        except Exception:
            scored.append((n, t, n))
    scored.sort(reverse=True)
    return [(t, n) for _, t, n in scored[:top]]


_TUR_ONCELIK = {"tanim": 0, "bulgu": 1, "iliski": 2, "sayisal": 3, "yontem": 4}


def _bilgi_yogun(cumle):
    """Sayi/simge yigini cumleleri ele.

    'ΔG° 3.1 kJ mol-1, -55.52 kJ mol-1, -0.2 kJ ...' gibi tablo dokumleri
    okuyana bir sey anlatmiyor; bunlari kullaniciya gostermiyoruz.
    """
    if not cumle:
        return False
    rakam = sum(1 for ch in cumle if ch.isdigit())
    if rakam / max(len(cumle), 1) > 0.16:
        return False
    virgul = cumle.count(",")
    if virgul >= 6 and rakam > 12:
        return False
    kelime = [w for w in re.findall(r"[A-Za-zÀ-ÿğüşıöçĞÜŞİÖÇ]{3,}", cumle)]
    return len(kelime) >= 8


def insights(query, limit=6, turler=None):
    """Makalelerden cikarilmis bulgulari getir.

    Once kavrama bagli olanlar, sonra tam metin eslesmesi denenir. Boylece
    "entropi nedir" sorusunda terim listesi degil, gercek ifadeler gosterilir.
    """
    c = db.conn()
    # Korpusun buyuk cogunlugu Ingilizce; Turkce sorgu bulgulara hic
    # ulasamiyordu (olculdu: "kuantum dolanikligi" -> 0 bulgu). Sorgu
    # Ingilizce karsiliklariyla genisletiliyor.
    try:
        from . import turkce as _tr
        _genis, _ekler = _tr.ceviri_ile_genislet(query or "")
    except Exception:
        _genis, _ekler = (query or ""), []
    n = normalize(query or "").strip()
    tur_kosul = ""
    args = []
    if turler:
        tur_kosul = " AND tur IN (%s)" % ",".join("?" * len(turler))
        args.extend(turler)

    out = []
    if n:
        try:
            rows = c.execute(
                "SELECT tur, cumle, norm, paper_id, lang FROM insights "
                "WHERE norm = ?" + tur_kosul +
                " ORDER BY skor DESC LIMIT ?", [n] + args + [limit]).fetchall()
            out = [dict(r) for r in rows]
        except Exception:
            out = []
    if len(out) < limit and n:
        kelimeler = [w for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{4,}", n)][:3]
        # Ingilizce karsiliklar da aranir
        for _e in _ekler[:2]:
            for _w in re.findall(r"[a-zA-Z]{4,}", _e)[:2]:
                if _w.lower() not in kelimeler:
                    kelimeler.append(_w.lower())
        for w in kelimeler:
            # ONEMLI: burada `limit` ile durmuyoruz. Ilk kelime (Turkce)
            # kotayi doldurunca Ingilizce karsiliklara hic sira gelmiyordu
            # ve sonrasindaki ilgi suzgeci hepsini eliyordu. Aday havuzu
            # genis tutulur, eleme sonra yapilir.
            if len(out) >= limit * 6:
                break
            try:
                rows = c.execute(
                    "SELECT tur, cumle, norm, paper_id, lang FROM insights "
                    "WHERE cumle LIKE ?" + tur_kosul +
                    " ORDER BY skor DESC LIMIT ?",
                    ["%" + w + "%"] + args + [limit]).fetchall()
            except Exception:
                rows = []
            var = set(o["cumle"] for o in out)
            for r in rows:
                if r["cumle"] not in var:
                    out.append(dict(r))
                    var.add(r["cumle"])
                if len(out) >= limit * 3:
                    break
    # Bilgi yogunlugu dusuk olanlari at, sonra tur onceligine gore sirala:
    # tanim ve bulgu, yontem/sayisal dokumunden once gelmeli.
    out = [o for o in out if _bilgi_yogun(o["cumle"])]

    # Kelime siniri: LIKE '%black%' sorgusu "blackbody" ve "black carbon"
    # cumlelerini de getiriyordu. Sorgunun kelimeleri tam olarak gecmeli.
    q_kelime = [w for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{4,}", n)
                if w not in STOP][:4]
    # Ingilizce karsiliklar AYRI bir eslesme yolu olarak tutulur; q_kelime
    # icine katilirsa obek denetimi "kuantum dolanikligi quantum" gibi
    # imkansiz bir dizi arar ve her seyi eler (olculdu: korpusta 146
    # "entanglement" bulgusu varken sonuc sifirdi).
    q_ceviri = []
    for _e in _ekler[:3]:
        kelimeleri = [w for w in re.findall(r"[a-zA-Z]{4,}", normalize(_e))]
        if kelimeleri:
            q_ceviri.append(kelimeleri[:3])
    if q_kelime:
        def ortusme(o):
            c = normalize(o["cumle"])
            # Sondaki \w{0,3}, Turkce cekim eklerine ("entropinin") izin verir
            # ama "black" ile "blackbody" eslesmesini engeller.
            return sum(1 for w in q_kelime
                       if re.search(r"(?<!\w)%s\w{0,3}(?!\w)" % re.escape(w), c))
        # Tek kelime tutmasi her zaman yeterli degil: "black hole" sorgusu
        # "black carbon" cumlesini getirmemeli. Ama iki kelime sart kosmak da
        # fazla kati — cozum kelimenin ayirt ediciligine bakmak: yaygin
        # kelimeler (black) tek basina yetmez, nadir olanlar (entanglement) yeter.
        def ceviri_tutuyor(o):
            """Ingilizce karsiliklardan biri cumlede geciyor mu?"""
            c = normalize(o["cumle"])
            for grup in q_ceviri:
                if all(re.search(r"(?<!\w)%s\w{0,3}(?!\w)" % re.escape(w), c)
                       for w in grup):
                    return True
            return False

        def eslesenler(o):
            c = normalize(o["cumle"])
            return [w for w in q_kelime
                    if re.search(r"(?<!\w)%s\w{0,3}(?!\w)" % re.escape(w), c)]

        # Cok kelimeli sorguda once ÖBEK eslesmesi aranir. "black hole" ile
        # "black carbon" arasindaki farki ayirt eden sey kelime nadirligi
        # degil, kelimelerin yan yana gelmesidir.
        if len(q_kelime) >= 2:
            obek = re.compile(r"(?<!\w)%s" % r"\w{0,3}\W+".join(
                re.escape(w) for w in q_kelime[:3]))
            obekli = [o for o in out
                      if o.get("norm") == n or obek.search(normalize(o["cumle"]))
                      or ceviri_tutuyor(o)]
            if obekli:
                out = obekli
            else:
                out = [o for o in out
                       if o.get("norm") == n or len(eslesenler(o)) >= 2
                       or ceviri_tutuyor(o)]
        else:
            out = [o for o in out
                   if o.get("norm") == n or len(eslesenler(o)) >= 1
                   or ceviri_tutuyor(o)]
        out.sort(key=lambda o: (-len(eslesenler(o)),
                                _TUR_ONCELIK.get(o["tur"], 9)))
    else:
        out.sort(key=lambda o: (_TUR_ONCELIK.get(o["tur"], 9),
                                -len(o.get("norm") or "")))
    return out[:limit]


def relations(query, limit=6):
    """Ogrenilen adlandirilmis iliskiler: 'A, B'ye yol acar'."""
    n = normalize(query or "").strip()
    if not n:
        return []
    try:
        rows = db.conn().execute(
            "SELECT r.a, r.fiil, r.b, r.sayi, ca.name na, cb.name nb "
            "FROM relations r "
            "LEFT JOIN concepts ca ON ca.norm = r.a "
            "LEFT JOIN concepts cb ON cb.norm = r.b "
            "WHERE r.a = ? OR r.b = ? ORDER BY r.sayi DESC LIMIT ?",
            (n, n, limit)).fetchall()
        return [{"a": r["na"] or r["a"], "fiil": r["fiil"],
                 "b": r["nb"] or r["b"], "sayi": r["sayi"]} for r in rows]
    except Exception:
        return []


def live_lookup(query, lang="tr", limit=6):
    """Veritabaninda yeterli sonuc yoksa internetten anlik ara.

    Bulunanlar ayni zamanda kaliciya yazilir; yani her soru botu biraz daha
    ogrenmis hale getirir.
    """
    found = []
    try:
        found = sources.live_search(query, lang=lang, limit=limit)
    except Exception:
        found = []
    # Kaliciya yazma kuyruk uzerinden yapilir; cevap bunu beklemez.
    sql = ("INSERT OR IGNORE INTO papers"
           "(source,ext_id,title,abstract,authors,categories,lang,url,"
           "published,fetched_at) VALUES(?,?,?,?,?,?,?,?,?,?)")
    now = time.time()
    for p in found:
        db.queue_write(sql, (p["source"], str(p["ext_id"]), p["title"],
                             p["abstract"], p.get("authors", ""),
                             p.get("categories", ""), p.get("lang", "en"),
                             p.get("url", ""), p.get("published", ""), now))
    return found


def wiki_lookup(query, lang="tr"):
    """Wikipedia'dan canli tanim getir ve ogren."""
    try:
        hits = sources.wiki_search(query, lang=lang, limit=3)
    except Exception:
        return None
    if not hits:
        return None
    title = hits[0]["title"]
    s = sources.wiki_summary(title, lang=lang)
    if not s:
        return None
    db.queue_write(
        "INSERT INTO concepts(name,norm,lang,definition,extract,url,freq,updated_at)"
        " VALUES(?,?,?,?,?,?,0,?) ON CONFLICT(norm,lang) DO UPDATE SET"
        " definition=COALESCE(NULLIF(excluded.definition,''), concepts.definition),"
        " extract=COALESCE(NULLIF(excluded.extract,''), concepts.extract),"
        " url=COALESCE(NULLIF(excluded.url,''), concepts.url),"
        " updated_at=excluded.updated_at",
        (s["title"], normalize(s["title"]), lang, s.get("description", ""),
         s["extract"], s["url"], time.time()))
    return s


def deep_read(title, lang="tr", chars=6000):
    """Bir konunun daha uzun metnini canli oku (indirmeden)."""
    try:
        return sources.wiki_extract(title, lang=lang, chars=chars)
    except Exception:
        return ""
