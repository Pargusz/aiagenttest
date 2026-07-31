"""ParguszPhysics - merkezi yapilandirma."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("PARGUSZ_VERI") or os.path.join(BASE_DIR, "data")
WEB_DIR = os.path.join(BASE_DIR, "web")
DB_PATH = os.path.join(DATA_DIR, "parguszphysics.db")
LOG_PATH = os.path.join(DATA_DIR, "ogrenme.log")

os.makedirs(DATA_DIR, exist_ok=True)

BOT_NAME = "ParguszPhysics"
VERSION = "1.3"

# Varsayilan olarak YALNIZCA bu bilgisayardan erisilir. Sunucuya
# kurulurken (Hugging Face, Render, kendi VPS'iniz) disaridan erisim
# gerekir; bunun icin PARGUSZ_HOST=0.0.0.0 verilir. Varsayilani
# degistirmiyoruz: bir programin izinsizce ag dinlemeye baslamasi
# dogru degildir.
HOST = os.environ.get("PARGUSZ_HOST", "127.0.0.1")
# Barindirma servisleri portu PORT degiskeniyle bildirir (Render,
# Railway, Fly). Hugging Face Spaces 7860 bekler.
PORT = int(os.environ.get("PARGUSZ_PORT")
           or os.environ.get("PORT")
           or "8777")

# Veri dizini disaridan verilebilsin: sunucuda kalici disk baska yerde
# baglanmis olabilir.

# --- Ogrenme (harvest) ayarlari ---------------------------------------------
USER_AGENT = "ParguszPhysics/1.0 (yerel arastirma araci; iletisim: yerel kullanici)"
REQUEST_TIMEOUT = 30
# Kaynaklara nazik davranmak icin istekler arasi bekleme (saniye)
POLITE_DELAY = {
    "arxiv": 3.5,
    "openalex": 2.5,
    "wikipedia": 0.6,
    "doaj": 1.5,
    "dergipark": 2.5,
    "crossref": 1.2,
}

# Her turda kac kayit cekilecek
BATCH_SIZE = 100
# Tur sonrasi dinlenme (saniye) - gunlerce calisabilmesi icin
CYCLE_REST = 20

# Taranacak arXiv fizik kategorileri
ARXIV_CATEGORIES = [
    "physics.class-ph", "physics.gen-ph", "physics.optics", "physics.flu-dyn",
    "physics.atom-ph", "physics.plasm-ph", "physics.comp-ph", "physics.app-ph",
    "physics.acc-ph", "physics.ao-ph", "physics.bio-ph", "physics.chem-ph",
    "physics.data-an", "physics.ed-ph", "physics.geo-ph", "physics.hist-ph",
    "physics.ins-det", "physics.med-ph", "physics.soc-ph", "physics.space-ph",
    "quant-ph", "gr-qc", "hep-th", "hep-ph", "hep-ex", "hep-lat", "nucl-th",
    "nucl-ex", "astro-ph.CO", "astro-ph.GA", "astro-ph.HE", "astro-ph.SR",
    "astro-ph.EP", "astro-ph.IM", "cond-mat.mes-hall", "cond-mat.mtrl-sci",
    "cond-mat.stat-mech", "cond-mat.str-el", "cond-mat.supr-con",
    "cond-mat.soft", "cond-mat.quant-gas", "cond-mat.dis-nn", "nlin.CD",
    "math-ph",
]

# OpenAlex fizik konu kimlikleri (concept id) ve arama terimleri
OPENALEX_QUERIES = [
    "quantum mechanics", "thermodynamics", "electromagnetism", "optics",
    "classical mechanics", "statistical physics", "condensed matter",
    "nuclear physics", "particle physics", "astrophysics", "cosmology",
    "fluid dynamics", "plasma physics", "relativity", "photonics",
    "semiconductor physics", "superconductivity", "acoustics", "biophysics",
    "computational physics", "geophysics", "atomic physics", "spectroscopy",
    "nonlinear dynamics", "quantum field theory", "solid state physics",
]

# Turkce icerik icin OpenAlex sorgulari (language:tr filtresiyle kullanilir)
TURKISH_QUERIES = [
    "fizik", "kuantum", "termodinamik", "elektromanyetik", "optik",
    "manyetik alan", "yarı iletken", "nükleer", "parçacık fiziği",
    "astrofizik", "plazma", "lazer", "spektroskopi", "akışkanlar mekaniği",
    "malzeme bilimi", "enerji dönüşümü", "ısı transferi", "dalga",
    "atom", "kristal yapı", "süperiletken", "nanoyapı", "radyasyon",
    "görelilik", "istatistiksel mekanik",
]

# Turkce kaynaklar (DergiPark OAI-PMH ve TR Wikipedia)
DERGIPARK_OAI = "https://dergipark.org.tr/api/public/oai"

# Wikipedia'dan cekilecek fizik kategorileri (TR + EN)
WIKI_CATEGORIES = {
    "tr": ["Fizik", "Kuantum_mekaniği", "Termodinamik", "Elektromanyetizma",
           "Optik", "Klasik_mekanik", "Astrofizik", "Nükleer_fizik",
           "Parçacık_fiziği", "Görelilik_kuramı", "Akışkanlar_mekaniği",
           "İstatistiksel_mekanik", "Katıhâl_fiziği", "Fizikçiler"],
    "en": ["Physics", "Quantum_mechanics", "Thermodynamics", "Electromagnetism",
           "Optics", "Classical_mechanics", "Astrophysics", "Nuclear_physics",
           "Particle_physics", "Theory_of_relativity", "Fluid_mechanics",
           "Statistical_mechanics", "Condensed_matter_physics",
           "Physical_quantities", "Physical_constants", "Equations_of_physics"],
}


# ── Uzaktan erisim (GitHub Pages + tunel) ──────────────────────────────────
# On yuz baska bir alan adindan (ornegin kullanici.github.io) sunulup
# API bu bilgisayarda calisabilir. Bunun icin iki sey gerekir:
#
#   1. CORS: tarayici, baska alandan gelen istegi sunucu izin vermedikce
#      engeller.
#   2. ANAHTAR: tunel adresi herkese aciktir. Anahtar verilmezse
#      /api/temizle gibi uc noktalar internete acik kalir. Bu yuzden
#      uzaktan erisimde anahtar ZORUNLU tutuluyor.
#
# PARGUSZ_ORIGIN: izin verilen on yuz adresleri (virgulle ayrilir).
#   Ornek: "https://kullanici.github.io"
#   Bos birakilirsa yalnizca ayni bilgisayardan erisim calisir.
ORIGIN = [x.strip() for x in
          (os.environ.get("PARGUSZ_ORIGIN") or "").split(",") if x.strip()]

# PARGUSZ_ANAHTAR: uzaktan erisim parolasi. Ayarlanmissa /api/ istekleri
# "X-Pargusz-Anahtar" basligini tasimak zorundadir.
ANAHTAR = (os.environ.get("PARGUSZ_ANAHTAR") or "").strip()
