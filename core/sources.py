"""Internet kaynaklari: makale ozetleri ve ansiklopedik tanimlar.

Tam metin PDF indirilmez. Sadece baslik + ozet + adres alinir; boylece
yuz binlerce makale birkac yuz MB'lik bir veritabaninda tutulabilir.
Kullanici bir makalenin detayini isterse o an canli olarak okunur.
"""
import json
import re
import time
import urllib.parse
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

from . import config

_last_call = {}
_cooldown = {}          # kaynak -> ne zamana kadar beklenecek


class SourceError(RuntimeError):
    """Kaynaga erisilemedi (ag hatasi, hiz siniri, bicim hatasi)."""


def _polite(source):
    """Kaynaklara nazik davran: istekler arasi minimum bekleme.

    429 alindiginda o kaynak icin genel bir soguma suresi konur; boylece
    sinirli bir API'ye ardi ardina vurup butun turu bosa harcamiyoruz.
    """
    bekle_kadar = _cooldown.get(source, 0)
    if bekle_kadar > time.time():
        raise SourceError("%s: hiz siniri, %d sn soguma"
                          % (source, int(bekle_kadar - time.time())))
    delay = config.POLITE_DELAY.get(source, 1.0)
    last = _last_call.get(source, 0)
    wait = delay - (time.time() - last)
    if wait > 0:
        time.sleep(wait)
    _last_call[source] = time.time()


def sogumaya_al(source, saniye=900):
    _cooldown[source] = time.time() + saniye


def http_get(url, source="generic", accept=None, retries=2):
    _polite(source)
    headers = {"User-Agent": config.USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    last_err = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=config.REQUEST_TIMEOUT) as r:
                raw = r.read()
                enc = r.headers.get_content_charset() or "utf-8"
                return raw.decode(enc, errors="replace")
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (429, 503):
                # Hiz siniri: kademeli bekle, israr etme, kaynagi sogumaya al
                if attempt >= retries - 1:
                    sogumaya_al(source, 900)
                    break
                time.sleep(15 * (attempt + 1))
                continue
            if e.code in (301, 302, 303, 307, 308):
                continue
            break
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    raise last_err if last_err else RuntimeError("istek basarisiz")


def _clean(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    s = s.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip()


# ---------------------------------------------------------------- arXiv
ARXIV_API = "http://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"


def arxiv_fetch(category=None, query=None, start=0, max_results=100,
                sort="submittedDate"):
    """arXiv'den makale ozetleri cek."""
    if query:
        sq = query
    else:
        sq = "cat:%s" % category
    params = {
        "search_query": sq,
        "start": str(start),
        "max_results": str(min(max_results, 200)),
        "sortBy": sort,
        "sortOrder": "descending",
    }
    url = ARXIV_API + "?" + urllib.parse.urlencode(params)
    text = http_get(url.replace("http://", "https://"), "arxiv")
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return []
    out = []
    for entry in root.findall(ATOM + "entry"):
        def g(tag):
            el = entry.find(ATOM + tag)
            return _clean(el.text) if el is not None and el.text else ""
        ext_id = g("id").rsplit("/", 1)[-1]
        if not ext_id:
            continue
        authors = "; ".join(
            _clean(a.find(ATOM + "name").text)
            for a in entry.findall(ATOM + "author")
            if a.find(ATOM + "name") is not None)
        cats = " ".join(
            c.get("term", "") for c in entry.findall("{http://arxiv.org/schemas/atom}primary_category"))
        if not cats:
            cats = " ".join(c.get("term", "") for c in entry.findall(ATOM + "category"))
        out.append({
            "source": "arxiv", "ext_id": ext_id,
            "title": g("title"), "abstract": g("summary"),
            "authors": authors[:600], "categories": cats,
            "lang": "en",
            "url": "https://arxiv.org/abs/" + ext_id,
            "published": g("published")[:10],
            "hakemli": 0,          # arXiv onbaski deposudur, hakem sureci yok
            "alan": "Physics and Astronomy",
        })
    return out


# ------------------------------------------------------------- OpenAlex
OPENALEX_API = "https://api.openalex.org/works"


def _openalex_abstract(inv):
    """OpenAlex ters indeksli ozeti duz metne cevir."""
    if not inv:
        return ""
    positions = []
    for word, idxs in inv.items():
        for i in idxs:
            positions.append((i, word))
    positions.sort()
    return " ".join(w for _, w in positions)


# OpenAlex alan kimlikleri: 3100 Physics and Astronomy, 2500 Materials Science
OPENALEX_FIZIK_ALANLARI = "fields/3100|fields/2500"


def openalex_fetch(query=None, page=1, per_page=100, concept="physics",
                   lang=None, from_year=None, yalniz_fizik=True,
                   min_atif=None):
    # Kalite kapisi kaynagin kendisinde: geri cekilmis ve fizik disi
    # makaleler hic indirilmiyor.
    filters = ["type:article", "has_abstract:true", "is_retracted:false",
               "is_paratext:false"]
    if yalniz_fizik:
        filters.append("primary_topic.field.id:" + OPENALEX_FIZIK_ALANLARI)
    if min_atif:
        filters.append("cited_by_count:>%d" % int(min_atif))
    if from_year:
        filters.append("from_publication_date:%d-01-01" % from_year)
    if lang:
        filters.append("language:%s" % lang)
    params = {
        "filter": ",".join(filters),
        "per-page": str(min(per_page, 200)),
        "page": str(page),
        "mailto": "parguszphysics@localhost",
    }
    if query:
        params["search"] = query
    def _cek(f):
        p2 = dict(params)
        p2["filter"] = ",".join(f)
        return json.loads(http_get(OPENALEX_API + "?" + urllib.parse.urlencode(p2),
                                   "openalex", accept="application/json"))

    try:
        data = _cek(filters)
    except SourceError:
        raise
    except Exception as e:
        # Alan filtresi reddedilirse filtresiz dene; kalite kapisi zaten
        # yerelde uygulaniyor, bu yuzden guvenlik kaybi olmuyor.
        if yalniz_fizik:
            try:
                data = _cek([x for x in filters
                             if not x.startswith("primary_topic")])
            except Exception as e2:
                raise SourceError("openalex: %s" % e2)
        else:
            raise SourceError("openalex: %s" % e)
    out = []
    for w in data.get("results", []):
        abstract = _openalex_abstract(w.get("abstract_inverted_index"))
        if not abstract or len(abstract) < 60:
            continue
        concepts = " ".join(c.get("display_name", "")
                            for c in (w.get("concepts") or [])[:8])
        authors = "; ".join(
            (a.get("author") or {}).get("display_name", "")
            for a in (w.get("authorships") or [])[:12])
        konu = w.get("primary_topic") or {}
        alan = ((konu.get("field") or {}).get("display_name") or "")
        kaynak_bilgi = ((w.get("primary_location") or {}).get("source") or {})
        dergi = kaynak_bilgi.get("display_name") or ""
        tur = (kaynak_bilgi.get("type") or "").lower()
        out.append({
            "source": "openalex",
            "ext_id": (w.get("id") or "").rsplit("/", 1)[-1],
            "title": _clean(w.get("title") or w.get("display_name") or ""),
            "abstract": _clean(abstract),
            "authors": authors[:600],
            "categories": (konu.get("display_name") or "") + " " + concepts,
            "lang": (w.get("language") or "en")[:2],
            "url": w.get("doi") or w.get("id") or "",
            "published": (w.get("publication_date") or "")[:10],
            # kalite verisi
            "atif": w.get("cited_by_count", -1),
            "geri_cekik": 1 if w.get("is_retracted") else 0,
            "alan": alan,
            "dergi": dergi[:120],
            # Dergi ve kitap bolumleri hakemli sayilir; depo (repository)
            # kayitlari onbaski olabilir.
            "hakemli": 1 if tur in ("journal", "book series", "conference") else -1,
        })
    return out


# ------------------------------------------------------------ Wikipedia
def wiki_summary(title, lang="en"):
    """Wikipedia ozeti (REST API)."""
    url = "https://%s.wikipedia.org/api/rest_v1/page/summary/%s" % (
        lang, urllib.parse.quote(title.replace(" ", "_"), safe=""))
    try:
        d = json.loads(http_get(url, "wikipedia", accept="application/json"))
    except Exception:
        return None
    if d.get("type") == "disambiguation":
        return None
    return {
        "title": d.get("title", title),
        "extract": _clean(d.get("extract", "")),
        "url": (d.get("content_urls", {}).get("desktop", {}) or {}).get("page", ""),
        "lang": lang,
        "description": _clean(d.get("description", "")),
    }


def wiki_category_members(category, lang="en", limit=200, cmcontinue=None):
    """Bir Wikipedia kategorisindeki sayfalari listele."""
    params = {
        "action": "query", "list": "categorymembers",
        "cmtitle": "Category:" + category, "cmlimit": str(min(limit, 500)),
        "format": "json", "cmtype": "page|subcat",
    }
    if cmcontinue:
        params["cmcontinue"] = cmcontinue
    url = "https://%s.wikipedia.org/w/api.php?%s" % (lang, urllib.parse.urlencode(params))
    try:
        d = json.loads(http_get(url, "wikipedia", accept="application/json"))
    except Exception:
        return [], None
    members = [m["title"] for m in d.get("query", {}).get("categorymembers", [])]
    cont = d.get("continue", {}).get("cmcontinue")
    return members, cont


def wiki_search(query, lang="en", limit=6):
    params = {"action": "query", "list": "search", "srsearch": query,
              "srlimit": str(limit), "format": "json"}
    url = "https://%s.wikipedia.org/w/api.php?%s" % (lang, urllib.parse.urlencode(params))
    try:
        d = json.loads(http_get(url, "wikipedia", accept="application/json"))
    except Exception:
        return []
    return [{"title": r["title"], "snippet": _clean(r.get("snippet", ""))}
            for r in d.get("query", {}).get("search", [])]


def wiki_extract(title, lang="en", chars=6000):
    """Sayfanin daha uzun bir kismini al (canli okuma icin)."""
    params = {"action": "query", "prop": "extracts", "titles": title,
              "explaintext": "1", "exchars": str(chars), "format": "json",
              "redirects": "1"}
    url = "https://%s.wikipedia.org/w/api.php?%s" % (lang, urllib.parse.urlencode(params))
    try:
        d = json.loads(http_get(url, "wikipedia", accept="application/json"))
    except Exception:
        return ""
    pages = d.get("query", {}).get("pages", {})
    for p in pages.values():
        if "extract" in p:
            return _clean(p["extract"])
    return ""


# ------------------------------------------------------------------ DOAJ
def doaj_fetch(query="physics", page=1, per_page=100):
    url = ("https://doaj.org/api/search/articles/%s?page=%d&pageSize=%d"
           % (urllib.parse.quote(query), page, min(per_page, 100)))
    try:
        d = json.loads(http_get(url, "doaj", accept="application/json"))
    except Exception:
        return []
    out = []
    for r in d.get("results", []):
        b = r.get("bibjson", {})
        abstract = _clean(b.get("abstract", ""))
        if len(abstract) < 60:
            continue
        link = ""
        for l in b.get("link", []):
            if l.get("type") == "fulltext":
                link = l.get("url", "")
                break
        out.append({
            "source": "doaj", "ext_id": r.get("id", ""),
            "title": _clean(b.get("title", "")),
            "abstract": abstract,
            "authors": "; ".join(a.get("name", "") for a in b.get("author", []))[:600],
            "categories": " ".join(k for k in (b.get("keywords") or [])),
            "lang": (b.get("journal", {}).get("language") or ["en"])[0][:2].lower(),
            "url": link or ("https://doaj.org/article/" + r.get("id", "")),
            "published": str(b.get("year", ""))[:4],
            # DOAJ yalnizca hakemli acik erisim dergilerini dizinler
            "hakemli": 1,
            "dergi": (b.get("journal", {}) or {}).get("title", "")[:120],
        })
    return out


# ------------------------------------------------------------- DergiPark (TR)
OAI_NS = {"oai": "http://www.openarchives.org/OAI/2.0/",
          "dc": "http://purl.org/dc/elements/1.1/"}


def dergipark_fetch(resumption=None, set_spec=None):
    """DergiPark OAI-PMH ile Turkce akademik makale ozetleri."""
    if resumption:
        url = "%s?verb=ListRecords&resumptionToken=%s" % (
            config.DERGIPARK_OAI, urllib.parse.quote(resumption))
    else:
        url = "%s?verb=ListRecords&metadataPrefix=oai_dc" % config.DERGIPARK_OAI
        if set_spec:
            url += "&set=" + urllib.parse.quote(set_spec)
    try:
        text = http_get(url, "dergipark", accept="application/xml")
        root = ET.fromstring(text)
    except Exception:
        return [], None
    out = []
    for rec in root.findall(".//oai:record", OAI_NS):
        header = rec.find("oai:header", OAI_NS)
        if header is None:
            continue
        ident = header.findtext("oai:identifier", "", OAI_NS)
        md = rec.find(".//oai:metadata", OAI_NS)
        if md is None:
            continue

        def dc(tag):
            vals = [e.text for e in md.iter("{http://purl.org/dc/elements/1.1/}" + tag)
                    if e.text]
            return vals

        titles = dc("title")
        descs = dc("description")
        if not titles or not descs:
            continue
        abstract = _clean(max(descs, key=len))
        if len(abstract) < 80:
            continue
        langs = dc("language")
        lang = "tr"
        for l in langs:
            ll = l.lower()
            if "en" in ll:
                lang = "en"
            if "tr" in ll:
                lang = "tr"
                break
        subj = " ".join(dc("subject"))[:400]
        ids = dc("identifier")
        url_ = next((i for i in ids if i.startswith("http")), "")
        out.append({
            "source": "dergipark", "ext_id": ident,
            "title": _clean(titles[0]), "abstract": abstract,
            "authors": "; ".join(dc("creator"))[:600],
            "categories": subj, "lang": lang, "url": url_,
            "published": (dc("date") or [""])[0][:10],
        })
    token_el = root.find(".//oai:resumptionToken", OAI_NS)
    token = token_el.text if token_el is not None and token_el.text else None
    return out, token


# ----------------------------------------------------------- Canli arama
def live_search(query, lang="tr", limit=6):
    """Kullanici sorusu icin internetten anlik arama (indirmeden)."""
    results = []
    # arXiv tam metin arama
    try:
        q = 'all:"%s"' % query if " " in query else "all:%s" % query
        for p in arxiv_fetch(query=q, max_results=limit, sort="relevance"):
            results.append(p)
    except Exception:
        pass
    # OpenAlex
    try:
        for p in openalex_fetch(query=query, per_page=limit):
            results.append(p)
    except Exception:
        pass
    return results[:limit * 2]


def crossref_search(query, rows=8):
    url = ("https://api.crossref.org/works?query=%s&rows=%d&select=title,abstract,DOI,author,issued,URL"
           % (urllib.parse.quote(query), rows))
    try:
        d = json.loads(http_get(url, "crossref", accept="application/json"))
    except Exception:
        return []
    out = []
    for it in d.get("message", {}).get("items", []):
        out.append({
            "source": "crossref", "ext_id": it.get("DOI", ""),
            "title": _clean((it.get("title") or [""])[0]),
            "abstract": _clean(it.get("abstract", "")),
            "authors": "; ".join(
                "%s %s" % (a.get("given", ""), a.get("family", ""))
                for a in (it.get("author") or [])[:8]),
            "categories": "", "lang": "en",
            "url": it.get("URL", ""),
            "published": "-".join(
                str(x) for x in (it.get("issued", {}).get("date-parts", [[""]])[0])),
        })
    return out


# ── OpenStax ders kitaplari ─────────────────────────────────────────────────
# Makale ozetleri arastirma sonucunu anlatir, KONUYU ogretmez. Bir ogretmen
# icin asil malzeme ders kitabidir: ogrenme hedefi, kavram anlatimi, cozumlu
# ornek. OpenStax kitaplari acik lisanslidir (CC BY) ve tam metin erisilebilir.
#
# YouTube da denendi ve olculdu: video sayfasindan altyazi listesi aliniyor
# ama altyazi icerigi (timedtext) oturum belirteci olmadan bos donuyor —
# denenen dort bicimin dordu de 0 bayt verdi. Guvenilir olmadigi icin
# eklenmedi; yerine ders kitabi ve acik ders malzemesi kullaniliyor.

OPENSTAX_KOK = "https://openstax.org"
_OPENSTAX_ONBELLEK = {}


def _openstax_surum():
    """Arsiv surumunu ve kitap listesini getir (onbellekli)."""
    if _OPENSTAX_ONBELLEK.get("rel"):
        return _OPENSTAX_ONBELLEK["rel"]
    d = json.loads(http_get(OPENSTAX_KOK + "/rex/release.json", "openstax",
                            accept="application/json"))
    _OPENSTAX_ONBELLEK["rel"] = d
    return d


def openstax_kitaplar(konu_kalibi=r"physics|astronomy"):
    """Fizik/astronomi ders kitaplarini listele."""
    d = json.loads(http_get(
        OPENSTAX_KOK + "/apps/cms/api/v2/pages/?type=books.Book&limit=200"
        "&fields=title,book_uuid,book_state", "openstax",
        accept="application/json"))
    out = []
    for it in d.get("items", []):
        baslik = it.get("title") or ""
        if not re.search(konu_kalibi, baslik, re.I):
            continue
        if (it.get("book_state") or "") == "retired":
            continue          # emekli kitaplar guncel degil
        if it.get("book_uuid"):
            out.append({"baslik": baslik, "uuid": it["book_uuid"]})
    return out


def _openstax_metin(html):
    """Kitap sayfasindaki HTML'den okunabilir metin cikar."""
    h = re.sub(r"<style[^>]*>.*?</style>", " ", html or "", flags=re.S | re.I)
    h = re.sub(r"<script[^>]*>.*?</script>", " ", h, flags=re.S | re.I)
    h = re.sub(r"/\*.*?\*/", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    for a, b in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&#x2013;", "–"),
                 ("&nbsp;", " "), ("&quot;", '"'), ("&#8217;", "’")):
        h = h.replace(a, b)
    return re.sub(r"\s+", " ", h).strip()


def openstax_bolumler(uuid, en_fazla=400):
    """Bir kitabin bolum sayfalarini (id, baslik) olarak listele."""
    rel = _openstax_surum()
    arsiv = rel["archiveUrl"]
    ver = (rel.get("books", {}).get(uuid) or {}).get("defaultVersion")
    if not ver:
        raise SourceError("openstax: kitap surumu bulunamadi")
    kitap = json.loads(http_get(
        "%s%s/contents/%s@%s.json" % (OPENSTAX_KOK, arsiv, uuid, ver),
        "openstax", accept="application/json"))

    out = []

    def gez(dugumler):
        for c in dugumler:
            if len(out) >= en_fazla:
                return
            if "contents" in c:
                gez(c["contents"])
            else:
                baslik = re.sub(r"<[^>]+>", "", c.get("title") or "").strip()
                out.append((c["id"].split("@")[0], baslik))

    gez(kitap.get("tree", {}).get("contents", []))
    return out, arsiv, ver, _clean(kitap.get("title") or "")


def openstax_bolum(uuid, ver, arsiv, sayfa_id):
    """Tek bir bolum sayfasinin metnini getir."""
    d = json.loads(http_get(
        "%s%s/contents/%s@%s:%s.json" % (OPENSTAX_KOK, arsiv, uuid, ver, sayfa_id),
        "openstax", accept="application/json"))
    return {
        "baslik": _clean(re.sub(r"<[^>]+>", "", d.get("title") or "")),
        "metin": _openstax_metin(d.get("content", "")),
        "url": "%s/books/%s/pages/%s" % (OPENSTAX_KOK, d.get("slug", ""),
                                         d.get("slug", "")),
    }


def wikibooks_summary(title, proje="wikibooks", lang="en"):
    """Wikibooks / Wikiversity sayfa ozeti."""
    url = "https://%s.%s.org/api/rest_v1/page/summary/%s" % (
        lang, proje, urllib.parse.quote(title.replace(" ", "_"), safe=""))
    try:
        d = json.loads(http_get(url, proje, accept="application/json"))
    except Exception:
        return None
    if d.get("type") == "disambiguation" or not d.get("extract"):
        return None
    return {
        "title": d.get("title", title),
        "extract": _clean(d.get("extract", "")),
        "url": (d.get("content_urls", {}).get("desktop", {}) or {}).get("page", ""),
        "lang": lang,
        "kaynak": proje,
    }


def wiki_langlink(title, from_lang="tr", to_lang="en"):
    """Bir Wikipedia baslığının baska dildeki karsiligini bul.

    Turkce sorulan bir soruyu arXiv'de aramak icin Ingilizce terim gerekir:
    "kuantum dolanikligi" -> "Quantum entanglement". Bu koprü olmadan
    Turkce sorgular hicbir makale getirmiyordu.
    """
    url = ("https://%s.wikipedia.org/w/api.php?action=query&prop=langlinks"
           "&lllang=%s&format=json&titles=%s"
           % (from_lang, to_lang, urllib.parse.quote(title, safe="")))
    try:
        d = json.loads(http_get(url, "wikipedia", accept="application/json"))
    except Exception:
        return None
    for sayfa in (d.get("query", {}).get("pages", {}) or {}).values():
        for bag in sayfa.get("langlinks", []) or []:
            if bag.get("*"):
                return bag["*"]
    return None


# ── Universite depolari ve acik kitaplar ────────────────────────────────────
# Makale ozetleri ve ders kitaplari vardi; eksik olan, universitelerin kendi
# depolarindaki arastirma ciktilariydi. Asagidaki kaynaklar acik erisimlidir
# ve API'leri anahtar istemez (olculdu):
#
#   Zenodo   — CERN'in isletttigi depo; 84.000+ fizik yayini
#   OpenAIRE — Avrupa universite depolarinin toplayicisi
#   HAL      — Fransiz universite ve arastirma kurumlari
#   OAPEN    — acik erisimli akademik KITAPLAR
#
# Not: CORE ve DOAB de denendi; CORE anahtar istiyor, DOAB zaman asimina
# ugruyor. Calismayan kaynagi eklemek yerine calisanlarla ilerliyoruz.

def _metin_al(x):
    """OpenAIRE alanlari kimi zaman str, kimi zaman dict ya da liste doner."""
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        return x.get("$", "")
    if isinstance(x, list):
        for e in x:
            m = _metin_al(e)
            if m:
                return m
    return ""


def zenodo_fetch(query="physics", page=1, size=50):
    """Zenodo (CERN) deposundan yayin cek."""
    # Cok kelimeli sorgu tirnak icinde verilmeli; ayrica Zenodo hiz
    # sinirinda 400 donuyor, bu yuzden istek araligi genis tutuluyor.
    q = query if query.startswith('"') else '"%s"' % query
    url = ("https://zenodo.org/api/records?q=%s&size=%d&page=%d"
           "&sort=mostrecent" % (urllib.parse.quote(q), size, page))
    try:
        d = json.loads(http_get(url, "zenodo", accept="application/json"))
    except Exception as e:
        raise SourceError("zenodo: %s" % e)
    out = []
    for h in d.get("hits", {}).get("hits", []):
        md = h.get("metadata", {}) or {}
        ozet = _clean(re.sub(r"<[^>]+>", " ", md.get("description") or ""))
        baslik = _clean(md.get("title") or "")
        if len(ozet) < 120 or not baslik:
            continue
        yazarlar = "; ".join(
            (a.get("name") or "") for a in (md.get("creators") or [])[:6])
        konular = " ".join(
            (k.get("subject") or k.get("term") or "") if isinstance(k, dict)
            else str(k) for k in (md.get("keywords") or [])[:8])
        out.append({
            "ext_id": str(h.get("id") or h.get("doi") or baslik[:60]),
            "title": baslik,
            "abstract": ozet[:6000],
            "authors": yazarlar,
            "categories": konular or (md.get("resource_type", {}) or {}).get("type", ""),
            "url": h.get("links", {}).get("self_html") or h.get("doi_url") or "",
            "published": (md.get("publication_date") or "")[:10],
            "dergi": (md.get("journal", {}) or {}).get("title", "") or "Zenodo",
            "hakemli": 1 if (md.get("journal") or md.get("doi")) else -1,
        })
    return out


def openaire_fetch(query="physics", page=1, size=50):
    """OpenAIRE — Avrupa universite depolarinin toplayicisi."""
    url = ("https://api.openaire.eu/search/publications?keywords=%s"
           "&size=%d&page=%d&format=json" % (urllib.parse.quote(query),
                                             size, page))
    try:
        j = json.loads(http_get(url, "openaire", accept="application/json"))
    except Exception as e:
        raise SourceError("openaire: %s" % e)
    sonuclar = (j.get("response", {}).get("results", {}) or {}).get("result", [])
    if isinstance(sonuclar, dict):
        sonuclar = [sonuclar]
    out = []
    for r in sonuclar:
        try:
            e = r["metadata"]["oaf:entity"]["oaf:result"]
        except Exception:
            continue
        baslik = _clean(_metin_al(e.get("title")))
        ozet = _clean(re.sub(r"<[^>]+>", " ", _metin_al(e.get("description"))))
        if len(ozet) < 120 or not baslik:
            continue
        konular = e.get("subject")
        if isinstance(konular, dict):
            konular = [konular]
        kategori = " ".join(_metin_al(k) for k in (konular or [])[:8])
        out.append({
            "ext_id": _metin_al(e.get("originalId")) or baslik[:60],
            "title": baslik,
            "abstract": ozet[:6000],
            "authors": "; ".join(
                _metin_al(a) for a in ((e.get("creator") if isinstance(
                    e.get("creator"), list) else [e.get("creator")]) or [])[:6]),
            "categories": kategori,
            "url": "",
            "published": _metin_al(e.get("dateofacceptance"))[:10],
            "dergi": _metin_al(e.get("publisher")) or "OpenAIRE",
            "hakemli": -1,
        })
    return out


def hal_fetch(query="physics", rows=50, start=0):
    """HAL — Fransiz universite ve arastirma kurumlari deposu."""
    url = ("https://api.archives-ouvertes.fr/search/?q=%s&rows=%d&start=%d"
           "&wt=json&fl=title_s,abstract_s,uri_s,authFullName_s,"
           "producedDateY_i,journalTitle_s,domain_s"
           % (urllib.parse.quote(query), rows, start))
    try:
        j = json.loads(http_get(url, "hal", accept="application/json"))
    except Exception as e:
        raise SourceError("hal: %s" % e)
    out = []
    for d in j.get("response", {}).get("docs", []):
        baslik = _clean((d.get("title_s") or [""])[0])
        ozet = _clean((d.get("abstract_s") or [""])[0])
        if len(ozet) < 120 or not baslik:
            continue
        out.append({
            "ext_id": d.get("uri_s") or baslik[:60],
            "title": baslik,
            "abstract": ozet[:6000],
            "authors": "; ".join((d.get("authFullName_s") or [])[:6]),
            "categories": " ".join((d.get("domain_s") or [])[:6]),
            "url": d.get("uri_s") or "",
            "published": str(d.get("producedDateY_i") or ""),
            "dergi": (d.get("journalTitle_s") or "HAL"),
            "hakemli": 1 if d.get("journalTitle_s") else -1,
        })
    return out


def oapen_kitaplar(query="physics", limit=20):
    """OAPEN — acik erisimli akademik kitaplar."""
    url = ("https://library.oapen.org/rest/search?query=%s&expand=metadata"
           "&limit=%d" % (urllib.parse.quote(query), limit))
    try:
        d = json.loads(http_get(url, "oapen", accept="application/json"))
    except Exception as e:
        raise SourceError("oapen: %s" % e)
    out = []
    for k in d if isinstance(d, list) else []:
        ad = _clean(k.get("name") or "")
        if not ad:
            continue
        md = {m.get("key"): m.get("value")
              for m in (k.get("metadata") or []) if isinstance(m, dict)}
        ozet = _clean(re.sub(r"<[^>]+>", " ",
                             md.get("dc.description.abstract") or ""))
        if len(ozet) < 150:
            continue
        out.append({
            "ext_id": k.get("handle") or ad[:60],
            "title": ad,
            "abstract": ozet[:8000],
            "authors": md.get("dc.contributor.author") or "",
            "categories": "acik erisim kitap; " + (md.get("dc.subject.other") or ""),
            "url": "https://library.oapen.org/handle/" + (k.get("handle") or ""),
            "published": (md.get("dc.date.issued") or "")[:10],
            "dergi": md.get("publisher.name") or "OAPEN",
            "hakemli": 1,
        })
    return out


# ── Acik ders videolari (MIT OpenCourseWare) ────────────────────────────────
# Kullanici "youtube videolari ve internetteki her turlu fizik icerigi" ile
# beslenmesini istedi. YouTube'un kendi altyazi ucu bes ayri bicimde
# denendi ve hepsi 0 bayt dondu (oturum belirteci istiyor) — bu yol
# guvenilir degil.
#
# Ama ders videolarinin BUYUK kismi zaten acik lisansli kurslardan geliyor.
# MIT OpenCourseWare her ders videosunu YouTube'da yayimliyor ve ayni
# videonun TAM TRANSKRIPTINI kendi sunucusunda .vtt olarak aciyor
# (CC BY-NC-SA). Yani videonun konusmasini dogrudan, izinli ve eksiksiz
# alabiliyoruz — YouTube'dan kazimaya gerek yok.
#
# Bu, "video ders" malzemesinin dogru yoludur: kaynagi belli, lisansi
# acik, metni tam.

MIT_LEARN_API = "https://api.learn.mit.edu/api/v1"


def ocw_video_dersleri(konu="Physics", limit=40, offset=0):
    """MIT OpenCourseWare video derslerini listele.

    Doner: [{ext_id, baslik, aciklama, url, youtube_id, kurs, ...}]
    """
    url = ("%s/learning_resources_search/?resource_type=video&topic=%s"
           "&offered_by=ocw&limit=%d&offset=%d"
           % (MIT_LEARN_API, urllib.parse.quote(konu), int(limit),
              int(offset)))
    # http_get COZULMUS metin dondurur, bayt degil.
    ham = http_get(url, source="mitlearn", accept="application/json")
    if not ham:
        return []
    try:
        veri = json.loads(ham)
    except Exception:
        return []
    out = []
    for r in veri.get("results") or []:
        if not isinstance(r, dict):
            continue
        baslik = _clean(r.get("title") or "")
        adres = r.get("url") or ""
        if not baslik or not adres:
            continue
        aciklama = _clean(re.sub(r"<[^>]+>", " ", r.get("description") or ""))
        kurs = ""
        for calisma in (r.get("runs") or []):
            if isinstance(calisma, dict) and calisma.get("title"):
                kurs = _clean(calisma["title"])
                break
        out.append({
            "ext_id": str(r.get("id") or r.get("readable_id") or adres),
            "baslik": baslik,
            "aciklama": aciklama,
            "url": adres,
            "youtube_id": r.get("readable_id") or "",
            "kurs": kurs,
            "sure": r.get("duration") or "",
        })
    return out


_VTT_IZ = re.compile(r"^\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->")
_VTT_SES = re.compile(r"^\[[^\]]{1,40}\]$")


def _vtt_metne(vtt):
    """WEBVTT altyazisini duz, okunabilir metne cevir.

    Zaman damgalari, sira numaralari ve [SQUEAKING] gibi ses etiketleri
    atilir. Ardisik ayni satirlar tekrarlanmaz (altyaziler cakisir).
    """
    satirlar = []
    onceki = None
    for ham in (vtt or "").splitlines():
        s = ham.strip()
        if (not s or s.upper().startswith("WEBVTT") or _VTT_IZ.match(s)
                or s.isdigit() or _VTT_SES.match(s)):
            continue
        s = re.sub(r"<[^>]+>", "", s)
        if s == onceki:
            continue
        onceki = s
        satirlar.append(s)
    metin = " ".join(satirlar)
    metin = re.sub(r"\s+", " ", metin).strip()
    # Jenerik/tesekkur bloklari ders icerigi degildir ve cumle
    # ayiklayicisinda her bulgunun basina yapisiyordu (olculdu:
    # "Funding provided by ... MIT (c) 2012 You know gravity as ...").
    for kalip in (
            # Jenerik blogu genelde bir YIL ile biter: "... MIT (c) 2012".
            # Bastan yila kadar olan kismi tumuyle atiyoruz.
            r"(Funding provided by|Developed by the Teaching)[^.]{0,300}?"
            r"\b(19|20)\d{2}\b",
            r"©\s*\d{4}", r"\(c\)\s*\d{4}",
            r"MIT OpenCourseWare[^.]{0,80}?ocw\.mit\.edu",
            r"Support MIT OpenCourseWare[^.]{0,200}\.",
            r"For more information about[^.]{0,200}\.",
            r"PROFESSOR:", r"AUDIENCE:"):
        metin = re.sub(kalip, " ", metin)
    metin = re.sub(r"\s+", " ", metin).strip()
    # Konusmaci etiketi ("MARKUS KLUTE:") cumle basinda kalabilir, sorun degil.
    return metin


def ocw_video_metni(sayfa_url):
    """Ders videosunun tam transkriptini getir (yoksa None).

    OCW video sayfasinda altyazi dosyasi <track ... src="....vtt"> olarak
    duruyor; once sayfayi, sonra o dosyayi aliyoruz.
    """
    if not sayfa_url:
        return None
    sayfa = http_get(sayfa_url, source="ocw", accept="text/html")
    if not sayfa:
        return None
    m = re.search(r'<track[^>]+src="([^"]+\.vtt)"', sayfa)
    if not m:
        return None
    yol = m.group(1)
    if yol.startswith("/"):
        yol = "https://ocw.mit.edu" + yol
    vtt = http_get(yol, source="ocw", accept="text/vtt")
    if not vtt:
        return None
    return _vtt_metne(vtt)
