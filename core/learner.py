"""Surekli ogrenme motoru.

Arka planda calisir; internetten fizik makalelerinin ozetlerini ve
ansiklopedik tanimlari ceker, bunlardan:
  - aranabilir tam metin indeksi (FTS5)
  - kavram sozlugu (Wikipedia tanimlariyla)
  - kavramlar arasi birliktelik grafi
  - terim istatistikleri (TF/DF)
  - LaTeX formul havuzu
olusturur. Gunlerce kesintisiz calisacak sekilde tasarlanmistir; her tur
sonunda ilerlemesini veritabanina yazar, bilgisayar kapanip acilsa bile
kaldigi yerden devam eder.
"""
import re
import sqlite3
import time
import threading
import traceback
import itertools

from . import config, db, sources

STOP_TR = set("""ve veya ile ama fakat cunku icin gibi daha cok az en bir bu su o
ki de da mi mu mi ne nasil neden hangi her bazi tum butun olarak uzere ise ancak
yani ayrica hem ya ise diye kadar sonra once simdi burada orada bunlar sunlar
olan olup olmak eden edilen yapilan verilen alinan uzerine iliskin dair
calisma calismada arastirma makale amac yontem sonuc bulgu elde edilmistir
edilmis olmustur yapilmistir incelenmistir gosterilmistir bulunmustur""".split())

STOP_EN = set("""the a an and or but if then than that this these those of in on at
to for with from by as is are was were be been being have has had do does did
we our us it its their they them he she his her which who whom what when where
how why can could may might will would shall should must not no nor so such
also more most much many few less least very both each other another using used
use study paper results result show shows shown present presented propose
proposed method methods approach based data model models new here we report
find found observe observed demonstrate demonstrated investigate investigated
however therefore thus moreover furthermore between among within during""".split())

STOP = STOP_TR | STOP_EN

# Kesif asamasinda ayrica elenen kelimeler: bunlar sik gecer ama bir fizik
# kavrami degildir (akademik dolgu, egitim/yontem sozcukleri, olcu sifatlari).
GENERIC = set("""analysis analyses system systems method methods model models
theory theories problem problems solution solutions result results value values
function functions process processes structure structures property properties
condition conditions parameter parameters equation equations application
applications technique techniques experiment experimental measurement
measurements observation observations simulation simulations calculation
calculations research researches science sciences student students teacher
teachers teaching education educational learning course courses university
school schools course paper papers article journal review chapter section
different various several general specific important significant possible
available recent current previous following particular certain common single
multiple large small high low first second third number numbers case cases
type types form forms level levels state states time times point points
region regions range ranges effect effects factor factors change changes
increase decrease behavior behaviour performance quality control design
development approach approaches framework strategy strategies tool tools
ogrenci ogrenciler ogrencilerin ogretmen ogretmenler ogretim ogrenme
egitim egitimi arastirma arastirmalar calisma calismalar yontem yontemler
sonuc sonuclar deger degerler ornek ornekler durum durumlar ozellik
ozellikler uygulama uygulamalar gelistirme tasarim analiz analizi
sistem sistemler model modeli modelleme kuram kurami olcum olcume
deney deneyler universite fakulte bolum ders dersleri""".split())

_word = re.compile(r"[A-Za-zÀ-ÿğüşıöçĞÜŞİÖÇ][A-Za-zÀ-ÿğüşıöçĞÜŞİÖÇ\-]{2,}")
_latex = re.compile(r"\$([^$]{3,120})\$|\\\[([^\]]{3,160})\\\]|\\begin\{equation\}(.{3,200}?)\\end\{equation\}",
                    re.S)


def normalize(s):
    s = (s or "").lower()
    for a, b in {"ı": "i", "İ": "i", "ş": "s", "ğ": "g", "ü": "u",
                 "ö": "o", "ç": "c", "â": "a", "î": "i", "û": "u"}.items():
        s = s.replace(a, b)
    return s


# Bir Wikipedia maddesinin gercekten fizikle ilgili olup olmadigini anlamak
# icin kullanilan isaretciler. Turkce cekim ekleri yuzunden kelime listesiyle
# eleme yetersiz kaliyor; bu yuzden dogrulama, maddenin kendi metni uzerinden
# yapiliyor.
FIZIK_ISARETCI = (
    # Fransizca (HAL deposu) ve muhendislik-fizigi terimleri. Bunlar
    # olmadan "electromagnetisme", "topological insulator", "heat transfer"
    # gibi mesru fizik kayitlari eleniyordu (olculdu: depo kayitlarinin
    # %21'i yanlislikla fizik disi sayildi).
    "electromagnetisme", "electromagnetique", "quantique", "thermodynamique",
    "optique", "mecanique", "particule", "rayonnement", "magnetique",
    "supraconduct", "conducteur", "onde", "frequence", "cinetique",
    "heat transfer", "thermal conduct", "topological insulator",
    "semiconductor", "superconduct", "spectroscopy", "diffraction",
    "lattice", "phonon", "magnetization", "ferromagnet", "dielectric",
    "plasmonic", "nanostructure", "electromagnetics", "microwave",
    "waveguide", "photonic", "quantum dot", "spintronic",
    "fizik", "physic", "kuantum", "quantum", "enerji", "energy", "manyetik",
    "magnetic", "elektrik", "electric", "elektron", "electron", "atom",
    "molekul", "molecul", "parcacik", "particle", "dalga", "wave", "foton",
    "photon", "nukleer", "nuclear", "termodinamik", "thermodynam", "entropi",
    "entropy", "optik", "optic", "isik", "light", "lazer", "laser",
    "yercekimi", "gravit", "kutle", "mass ", "hiz", "velocity", "ivme",
    "acceleration", "kuvvet", "force", "momentum", "gorelilik", "relativ",
    "spektr", "spectr", "plazma", "plasma", "kristal", "crystal",
    "yariiletken", "semiconduct", "superiletken", "superconduct",
    "astronom", "astrofizik", "astrophys", "kozmol", "cosmolog", "yildiz",
    "galaks", "galax", "radyasyon", "radiation", "izotop", "isotope",
    "cekirdek", "nucleus", "kuark", "quark", "bozon", "boson", "fermiyon",
    "fermion", "akiskan", "fluid", "basinc", "pressure", "sicaklik",
    "temperature", "frekans", "frequency", "genlik", "amplitude", "orbital",
    "matematik", "mathemat", "mekanik", "mechanic", "kimya", "chemi",
    "olcu birimi", "unit of", "sabiti", "constant",
    # Kuramsal / matematiksel fizik sozvarligi. Bunlar olmadan "Cosmological
    # billiards" ve "Virasoro cebirleri" gibi gercek fizik makaleleri
    # "fizik disi" sayiliyordu.
    "lagrangian", "lagranj", "hamiltonian", "hamilton", "gauge", "ayar",
    "soliton", "instanton", "renormaliz", "simetri", "symmetr", "manifold",
    "tensor", "spinor", "fermion", "boson", "vacuum", "vakum",
    "virasoro", "kac-moody", "lie cebir", "lie algebra", "yang-mills",
    "supersymmetr", "susy", "string theory", "sicim kurami", "brane",
    "holograph", "hologra", "ads/cft", "conformal", "konformal",
    "propagator", "feynman", "scattering", "sacilma", "amplitude",
    "eigenvalue", "ozdeger", "eigenstate", "operator", "operator",
    "perturbation", "pertürbasyon", "perturbasyon", "variational",
    "varyasyon", "boltzmann", "hilbert", "schrodinger", "schrödinger",
    "dirac", "maxwell", "navier", "stokes", "reynolds", "turbulen",
    "lattice", "orgu", "monte carlo", "ab initio", "dft", "yogunluk fonksiyon",
    "cosmolog", "kozmoloj", "spacetime", "uzayzaman", "uzay-zaman",
    "curvature", "egrilik", "geodesic", "jeodezik", "metric tensor",
    "phase transition", "faz gecisi", "critical exponent", "kritik us",
    "correlation function", "korelasyon", "partition function",
    "billiard", "bilardo", "chaos", "kaos", "attractor", "cekici",
)


# Tek basina kesin karar verdiren isaretciler. "enerji" ya da "sistem" pek cok
# alanda gecer, ama "virasoro" ya da "yang-mills" yalnizca fizikte gecer.
FIZIK_KESIN = frozenset((
    # Tek basina fizik demek olan terimler (Fransizca ve muhendislik dahil)
    "electromagnetisme", "electromagnetique", "electromagnetics",
    "quantique", "thermodynamique", "supraconduct", "superconduct",
    "topological insulator", "phonon", "spintronic", "photonic",
    "quantum dot", "plasmonic", "waveguide",
    "kuantum", "quantum", "virasoro", "kac-moody", "yang-mills", "instanton",
    "soliton", "renormaliz", "supersymmetr", "susy", "ads/cft", "holograph",
    "spinor", "fermion", "boson", "kuark", "quark", "hadron", "lepton",
    "nukleer", "nuclear", "termodinamik", "thermodynam", "entropi", "entropy",
    "elektromanyet", "electromagnet", "astrofizik", "astrophys", "kozmoloj",
    "cosmolog", "gorelilik", "relativ", "schrodinger", "schrödinger",
    "hamiltonian", "lagrangian", "superiletken", "superconduct",
    "yariiletken", "semiconduct", "plazma", "plasma", "foton", "photon",
    "elektron", "electron", "spektroskop", "spectroscop", "difraksiyon",
    "diffraction", "interferomet", "girisim", "fizik", "physic",
))


# Fizik SANILAN ama fizik olmayan alanlar. Yalnizca olumlu isaretci saymak
# yetmiyor: "Physical Activity and Physical Education" metni "physical"
# yuzunden fizik sayiliyordu (olculdu, OAPEN'den kabul edilmisti).
_FIZIK_DISI = re.compile(
    r"\b(physical (activity|education|therapy|fitness|exercise|literacy)|"
    r"sport(s)? (science|medicine|education)|physical therapist|"
    r"beden egitimi|spor bilimleri|fiziksel aktivite|fiziksel uygunluk|"
    r"nursing|dentistry|veterinary|theology|jurisprudence|"
    r"marketing|accounting|tourism management|"
    r"hemsirelik|dis hekimligi|ilahiyat|muhasebe|pazarlama)\b", re.I)


def fizik_ilgili(metin):
    """Metin bir fizik/temel bilim konusundan mi bahsediyor?

    Agirlikli sayim: kesin isaretciler 2, destekleyiciler 1 puan. Esik 2.
    Boylece tek basina "Virasoro" yeterken, tek basina "enerji" yetmez.
    Once fizik DISI alan izleri denetlenir.
    """
    ham = metin or ""
    if _FIZIK_DISI.search(ham):
        return False
    m = normalize(ham)[:1200]
    puan = 0
    for k in FIZIK_ISARETCI:
        if k in m:
            puan += 2 if k in FIZIK_KESIN else 1
            if puan >= 2:
                return True
    return False


# ── Cumle turu siniflandirmasi ──────────────────────────────────────────────
# Makaleyi "incelemek", ozetindeki cumleleri islevlerine gore ayirmak demek:
# hangisi bir tanim, hangisi bir bulgu, hangisi bir yontem. Boylece daha sonra
# "entropi hakkinda ne ogrendin" diye sorulunca terim listesi degil, gercek
# ifadeler gosterilebiliyor.
_TUR_KALIPLARI = [
    # Tanim — en degerli tur. Eskiden yalnizca "is defined as" gibi resmi
    # kaliplari yakaliyordu ve 19.000 bulgunun icinde 265 tanim vardi.
    # Ders kitabi metinlerinde tanim cogunlukla "X is the ..." bicimindedir.
    ("tanim", re.compile(
        r"\b(is defined as|are defined as|is called|are called|refers to|"
        r"is known as|we define|is a measure of|denotes|is given by|"
        r"is the (?:study|theory|branch|process|ratio|amount|rate|measure|"
        r"sum|product|quantity|force|energy|property) of|"
        r"is (?:a|an|the) [a-z ]{3,30} (?:that|which|when|where)|"
        r"can be (?:defined|described|expressed) as|"
        r"olarak tanimlanir|olarak adlandirilir|olarak bilinir|"
        r"demektir|denir|tanimi|su sekilde tanimlanir|"
        r"olarak ifade edilir|anlamina gelir)\b", re.I)),
    # Bulgu — arastirmanin sonucu
    ("bulgu", re.compile(
        r"\b(we (?:show|find|demonstrate|observe|report|prove|conclude|"
        r"obtain|derive|establish|confirm|identify|reveal)|"
        r"results? (?:show|indicate|suggest|reveal|demonstrate|confirm)|"
        r"we have (?:shown|found|derived|obtained)|it is (?:shown|found)|"
        r"it (?:follows|turns out) that|"
        r"this (?:shows|implies|means|indicates|suggests)|"
        r"has been (?:shown|observed|measured|confirmed)|"
        r"experiments? (?:show|indicate|confirm)|"
        r"gosterilmistir|bulunmustur|elde edilmistir|ortaya konmustur|"
        r"sonucuna varilmistir|tespit edilmistir)\b", re.I)),
    # Yontem — nasil yapildigi
    ("yontem", re.compile(
        r"\b(we (?:use|used|apply|applied|propose|develop|present|employ|"
        r"analyze|analyse|investigate|study|calculate|compute|measure|"
        r"simulate|consider|introduce|construct|formulate|outline)|"
        r"using (?:a|an|the)|based on (?:a|an|the)|by means of|the method|"
        r"our approach|simulation|numerically|analytically|"
        r"kullanilarak|yontemiyle|yaklasimiyla|incelenmistir|hesaplanmistir)"
        r"\b", re.I)),
    # Iliski — nedensel ya da nicel bag
    ("iliski", re.compile(
        r"\b(leads? to|results? in|depends? on|is proportional to|"
        r"increases? with|decreases? with|is caused by|gives rise to|"
        r"is related to|scales? (?:as|with)|varies (?:as|with)|"
        r"is equivalent to|corresponds? to|arises? from|"
        r"yol acar|bagli(?:dir)?|orantili(?:dir)?|neden olur|"
        r"artar|azalir|sebep olur|karsilik gelir)\b", re.I)),
    # Yasa / ilke — ders kitaplarinda cok gecer, ogretim degeri yuksek
    ("tanim", re.compile(
        r"\b(the (?:law|principle|theorem|postulate|rule) (?:of|states)|"
        r"according to (?:the )?(?:law|principle|theory)|"
        r"states that|yasasina gore|ilkesine gore|yasasi|ilkesi|"
        r"teoremine gore)\b", re.I)),
]


# Sayisal deger iceren cumle: olculmus bir buyukluk tasir, ogretici degeri
# yuksektir.
_SAYISAL = re.compile(r"\d+(?:[.,]\d+)?\s*(?:[×x]\s*10\^?-?\d+)?\s*"
                      r"(?:%|percent|[a-zA-ZµΩÅ°]{1,6}\b)")

# "A, B'ye yol acar" gibi kavramlar arasi adlandirilmis iliski
_ILISKI_FIIL = re.compile(
    r"\b(leads? to|results? in|causes?|depends? on|is proportional to|"
    r"gives rise to|yol acar|neden olur|bagli)\b", re.I)


def cumle_turu(cumle):
    """Cumlenin islevini belirle. Hicbirine uymuyorsa None."""
    for tur, rx in _TUR_KALIPLARI:
        if rx.search(cumle):
            return tur
    if _SAYISAL.search(cumle) and len(cumle.split()) > 6:
        return "sayisal"
    return None


def tokens(text):
    for m in _word.finditer(text or ""):
        w = normalize(m.group(0))
        if len(w) > 2 and w not in STOP and not w.isdigit():
            yield w


class Learner(object):
    """Arka planda calisan ogrenme dongusu."""

    def __init__(self):
        self.thread = None
        self.watchdog_thread = None
        self.stop_flag = threading.Event()
        self.should_run = False      # kullanicinin istedigi durum
        self.status = "beklemede"
        self.last_error = None
        self.started_at = 0.0
        self.log_lines = []
        self._lock = threading.Lock()

    # ---------------------------------------------------------------- log
    def log(self, msg):
        line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
        with self._lock:
            self.log_lines.append(line)
            if len(self.log_lines) > 400:
                self.log_lines = self.log_lines[-300:]
        try:
            with open(config.LOG_PATH, "a", encoding="utf-8") as f:
                f.write(time.strftime("%Y-%m-%d ") + line + "\n")
        except Exception:
            pass

    def recent_log(self, n=60):
        with self._lock:
            return list(self.log_lines[-n:])

    # ------------------------------------------------------------ kontrol
    def start(self):
        self.should_run = True
        self._start_watchdog()
        if self.thread and self.thread.is_alive():
            return False
        self.stop_flag.clear()
        self.started_at = time.time()
        self.thread = threading.Thread(target=self._run, name="ogrenme", daemon=True)
        self.thread.start()
        return True

    def stop(self):
        self.should_run = False
        self.stop_flag.set()
        self._add_runtime()
        self.status = "durduruluyor"
        db.set_state("learner_status", "durduruldu")

    def is_running(self):
        return bool(self.thread and self.thread.is_alive())

    def _add_runtime(self):
        """Toplam calisma suresini diske isle (gunlerce calismayi izlemek icin)."""
        if self.started_at:
            db.bump_state("total_runtime", int(time.time() - self.started_at))
            self.started_at = time.time()

    def runtime(self):
        """Simdiye kadarki toplam ogrenme suresi (saniye)."""
        base = int(db.get_state("total_runtime", 0) or 0)
        if self.is_running() and self.started_at:
            base += int(time.time() - self.started_at)
        return base

    def _start_watchdog(self):
        """Motor beklenmedik bir sekilde olurse yeniden ayaga kaldir.

        Gunlerce kesintisiz calismasi istendigi icin, tek bir beklenmeyen
        istisnanin ogrenmeyi sessizce bitirmesine izin verilmiyor.
        """
        if self.watchdog_thread and self.watchdog_thread.is_alive():
            return

        def loop():
            while True:
                time.sleep(20)
                if not self.should_run:
                    continue
                if not self.is_running():
                    self.log("Motor durmus görünüyor; yeniden baslatiliyor.")
                    self.stop_flag.clear()
                    self.started_at = time.time()
                    self.thread = threading.Thread(target=self._run,
                                                   name="ogrenme", daemon=True)
                    self.thread.start()

        self.watchdog_thread = threading.Thread(target=loop, name="nobetci",
                                                daemon=True)
        self.watchdog_thread.start()

    def _sleep(self, seconds):
        """Kesilebilir bekleme."""
        end = time.time() + seconds
        while time.time() < end:
            if self.stop_flag.is_set():
                return False
            time.sleep(min(1.0, end - time.time()))
        return True

    # ------------------------------------------------------------ ana dongu
    def _run(self):
        db.init()
        self.status = "calisiyor"
        db.set_state("learner_status", "calisiyor")
        self.log("Ogrenme motoru basladi.")
        # Her tur farkli bir kaynaga odaklanir; boylece hicbir kaynak
        # asiri yuklenmez ve bilgi dengeli buyur.
        tasks = [
            self._task_arxiv,
            self._task_wikipedia_en,
            self._task_openalex,
            self._task_kesif,          # ogrendiginden yola cikip yeni kavram arar
            self._task_wikipedia_tr,
            self._task_turkce,
            self._task_derinlesme,     # kavram ciftlerini birlestiren yayinlari arar
            self._task_dergipark,
            self._task_doaj,
            self._task_sentez,          # makaleleri birlestirip bilgi uretir
            self._task_bosluk_doldur,   # kullanicinin cevaplanamayan sorulari
            self._task_universite_depolari,  # Zenodo/OpenAIRE/HAL/OAPEN
            self._task_ders_kitabi,     # OpenStax ders kitaplari
            self._task_video_ders,      # MIT OCW ders videolari (transkript)
            self._task_consolidate,
            self._task_kendini_dogrula,
            self._task_genisle,        # okuduklarindan yeni yetenek uretir
        ]
        idx = int(db.get_state("task_index", 0) or 0)
        ard_arda_hata = 0
        while not self.stop_flag.is_set():
            task = tasks[idx % len(tasks)]
            name = task.__name__.replace("_task_", "")
            try:
                self.status = "calisiyor: " + name
                db.set_state("learner_status", self.status)
                task()
                ard_arda_hata = 0
            except Exception as e:
                ard_arda_hata += 1
                self.last_error = str(e)
                self.log("HATA (%s): %s" % (name, e))
                try:
                    with open(config.LOG_PATH, "a", encoding="utf-8") as f:
                        f.write(traceback.format_exc() + "\n")
                except Exception:
                    pass
                # Internet kesildiyse bosuna donup durmasin: kademeli bekleme
                bekle = min(20 * (2 ** min(ard_arda_hata - 1, 5)), 600)
                if ard_arda_hata >= 3:
                    self.status = "baglanti bekleniyor (%d sn)" % bekle
                    db.set_state("learner_status", self.status)
                if not self._sleep(bekle):
                    break
            idx += 1
            db.set_state("task_index", idx)
            db.bump_state("cycles", 1)
            db.set_state("last_cycle_time", time.time())
            self._add_runtime()
            if not self._sleep(config.CYCLE_REST):
                break
        self.status = "durduruldu"
        db.set_state("learner_status", "durduruldu")
        self.log("Ogrenme motoru durdu.")

    # -------------------------------------------------------------- gorevler
    def _task_arxiv(self):
        cats = config.ARXIV_CATEGORIES
        ci = int(db.get_state("arxiv_cat_index", 0) or 0)
        cat = cats[ci % len(cats)]
        start = int(db.get_state("arxiv_start_%s" % cat, 0) or 0)
        self.log("arXiv taraniyor: %s (offset %d)" % (cat, start))
        papers = sources.arxiv_fetch(category=cat, start=start,
                                     max_results=config.BATCH_SIZE)
        n = self._ingest(papers)
        self.log("arXiv %s: %d yeni makale (toplam getirilen %d)" % (cat, n, len(papers)))
        if len(papers) < config.BATCH_SIZE // 2:
            # Bu kategori tukendi, basa don ve sonraki kategoriye gec
            db.set_state("arxiv_start_%s" % cat, 0)
            db.set_state("arxiv_cat_index", ci + 1)
        else:
            db.set_state("arxiv_start_%s" % cat, start + len(papers))
            # Bir kategoride cok derine inip digerlerini ac birakmamak icin
            # belli bir derinlikten sonra siradaki kategoriye gec. Tur bittiginde
            # bastan baslar; arXiv en yeniden siraladigi icin bu, yeni cikan
            # makaleleri de yakalamayi saglar.
            if start > 6000:
                db.set_state("arxiv_cat_index", ci + 1)

    def _task_openalex(self):
        qs = config.OPENALEX_QUERIES
        qi = int(db.get_state("openalex_q_index", 0) or 0)
        q = qs[qi % len(qs)]
        page = int(db.get_state("openalex_page_%s" % q, 1) or 1)
        self.log("OpenAlex taraniyor: '%s' (sayfa %d)" % (q, page))
        try:
            papers = sources.openalex_fetch(query=q, page=page,
                                            per_page=config.BATCH_SIZE)
        except sources.SourceError as e:
            self.log("OpenAlex erisilemedi (%s) — sonraki tura birakiliyor" % e)
            return
        n = self._ingest(papers)
        self.log("OpenAlex '%s': %d yeni kayit" % (q, n))
        if len(papers) < config.BATCH_SIZE // 2 or page >= 20:
            db.set_state("openalex_page_%s" % q, 1)
            db.set_state("openalex_q_index", qi + 1)
        else:
            db.set_state("openalex_page_%s" % q, page + 1)

    def _task_turkce(self):
        """Turkce yayinlari topla (OpenAlex dil filtresiyle)."""
        qs = config.TURKISH_QUERIES
        qi = int(db.get_state("tr_q_index", 0) or 0)
        q = qs[qi % len(qs)]
        page = int(db.get_state("tr_page_%s" % q, 1) or 1)
        self.log("Turkce kaynak taraniyor: '%s' (sayfa %d)" % (q, page))
        try:
            papers = sources.openalex_fetch(query=q, page=page, lang="tr",
                                            per_page=config.BATCH_SIZE)
        except sources.SourceError as e:
            self.log("Turkce kaynak erisilemedi (%s)" % e)
            return
        n = self._ingest(papers)
        self.log("Turkce '%s': %d yeni kayit" % (q, n))
        if len(papers) < config.BATCH_SIZE // 2 or page >= 10:
            db.set_state("tr_page_%s" % q, 1)
            db.set_state("tr_q_index", qi + 1)
        else:
            db.set_state("tr_page_%s" % q, page + 1)

    def _task_kesif(self):
        """Kendi kendine kesif.

        Bu, sabit listeleri taramaktan farklidir: bot okuduklarindan sik gecen
        ama henuz tanimini bilmedigi terimleri secer ve gidip onlari arastirir.
        Boylece ogrendikce nereye bakacagina kendisi karar verir ve bilgisi
        zamanla kendi ilgi alanini genisletir.
        """
        c = db.conn()
        toplam = c.execute("SELECT COUNT(*) n FROM papers").fetchone()["n"] or 1
        # Ayirt edici terimleri sec: cok sik gecen ("analysis", "system") kelimeler
        # bir fizik kavrami degil, sadece akademik dolgu olur. Bu yuzden belge
        # frekansi ustten de sinirlaniyor — klasik TF-IDF sezgisi.
        ust_sinir = max(5, int(toplam * 0.06))
        rows = c.execute(
            "SELECT t.term, t.tf, t.df FROM terms t "
            "LEFT JOIN concepts co ON co.norm = t.term "
            "LEFT JOIN explored e ON e.term = t.term "
            "WHERE co.id IS NULL AND e.term IS NULL "
            "  AND length(t.term) >= 6 AND t.df >= 3 AND t.df <= ? "
            "ORDER BY t.tf DESC LIMIT 40", (ust_sinir,)).fetchall()
        rows = [r for r in rows if r["term"] not in GENERIC][:8]
        if not rows:
            self.log("Kesif: arastirilacak yeni terim yok.")
            return
        bulunan = 0
        for r in rows:
            if self.stop_flag.is_set():
                break
            term = r["term"]
            found = 0
            for lang in ("en", "tr"):
                try:
                    hits = sources.wiki_search(term, lang=lang, limit=1)
                except Exception:
                    continue
                if not hits:
                    continue
                title = hits[0]["title"]
                norm = normalize(title)
                # Basligin terimle gercekten ilgili oldugunu dogrula
                if term not in norm and norm not in term:
                    continue
                if c.execute("SELECT 1 FROM concepts WHERE norm=? AND lang=?",
                             (norm, lang)).fetchone():
                    continue
                s = sources.wiki_summary(title, lang=lang)
                if not s or len(s["extract"]) < 80:
                    continue
                # Maddenin gercekten fizikle ilgili oldugunu dogrula: fizik
                # egitimi makalelerinden gelen "sosyal", "aday" gibi terimler
                # boylece kavram sozlugune girmiyor.
                if not fizik_ilgili(s.get("description", "") + " " + s["extract"]):
                    continue
                db.upsert_concept(s["title"], norm, lang,
                                  s.get("description", ""), s["extract"], s["url"])
                found = 1
                bulunan += 1
            c.execute("INSERT OR REPLACE INTO explored(term, kind, found, at) "
                      "VALUES(?,?,?,?)", (term, "terim", found, time.time()))
            c.commit()
        db.bump_state("kesif_terim", len(rows))
        db.bump_state("kesif_bulunan", bulunan)
        self.log("Kesif: %d terim arastirildi, %d yeni kavram ogrenildi"
                 % (len(rows), bulunan))

    def _task_derinlesme(self):
        """Kavram ciftlerinden yeni arama sorgulari uret.

        Grafikte birlikte siklikla gecen iki kavram, bot icin arastirmaya deger
        bir kesisim demektir; o kesisimi konu alan yayinlari arar.
        """
        c = db.conn()
        rows = c.execute(
            "SELECT cl.a, cl.b, cl.weight, ca.name AS na, cb.name AS nb "
            "FROM concept_links cl "
            "JOIN concepts ca ON ca.norm = cl.a "
            "JOIN concepts cb ON cb.norm = cl.b "
            "LEFT JOIN explored e ON e.term = cl.a || ' + ' || cl.b "
            "WHERE cl.a < cl.b AND cl.weight >= 2 AND e.term IS NULL "
            "ORDER BY cl.weight DESC LIMIT 3").fetchall()
        if not rows:
            self.log("Derinlesme: henuz yeterli kavram baglantisi yok.")
            return
        toplam = 0
        for r in rows:
            if self.stop_flag.is_set():
                break
            q = "%s %s" % (r["na"], r["nb"])
            try:
                papers = sources.openalex_fetch(query=q, per_page=40)
            except Exception as e:
                self.log("Derinlesme sorgusu basarisiz: %s" % e)
                papers = []
            n = self._ingest(papers)
            toplam += n
            c.execute("INSERT OR REPLACE INTO explored(term, kind, found, at) "
                      "VALUES(?,?,?,?)",
                      ("%s + %s" % (r["a"], r["b"]), "cift", n, time.time()))
            c.commit()
            self.log("Derinlesme: '%s' -> %d yeni kayit" % (q, n))
        db.bump_state("derinlesme_sorgu", len(rows))
        return toplam

    def _task_doaj(self):
        page = int(db.get_state("doaj_page", 1) or 1)
        qi = int(db.get_state("doaj_q_index", 0) or 0)
        queries = ["physics", "quantum", "thermodynamics", "optics",
                   "astrophysics", "condensed matter", "fizik"]
        q = queries[qi % len(queries)]
        self.log("DOAJ taraniyor: '%s' (sayfa %d)" % (q, page))
        papers = sources.doaj_fetch(query=q, page=page, per_page=100)
        n = self._ingest(papers)
        self.log("DOAJ '%s': %d yeni kayit" % (q, n))
        if len(papers) < 40 or page >= 15:
            db.set_state("doaj_page", 1)
            db.set_state("doaj_q_index", qi + 1)
        else:
            db.set_state("doaj_page", page + 1)

    def _task_dergipark(self):
        token = db.get_state("dergipark_token", None)
        self.log("DergiPark (Turkce) taraniyor...")
        papers, new_token = sources.dergipark_fetch(resumption=token)
        # sadece fizik/fen ilgili olanlari al
        keep = []
        for p in papers:
            blob = normalize(p["title"] + " " + p["abstract"] + " " + p["categories"])
            if any(k in blob for k in (
                    "fizik", "physic", "kuantum", "quantum", "enerji", "energy",
                    "termodinamik", "thermodynam", "optik", "optic", "manyetik",
                    "magnetic", "elektrik", "electric", "parcacik", "particle",
                    "dalga", "wave", "atom", "nukleer", "nuclear", "spektr",
                    "lazer", "laser", "yariiletken", "semiconductor", "plazma",
                    "plasma", "astronomi", "astro", "malzeme", "material",
                    "isi ", "heat", "mekanik", "mechanic", "akiskan", "fluid")):
                keep.append(p)
        n = self._ingest(keep)
        self.log("DergiPark: %d fizik ilgili kayit alindi (%d tarandi)"
                 % (n, len(papers)))
        db.set_state("dergipark_token", new_token)

    def _task_wikipedia_en(self):
        self._wiki_task("en")

    def _task_wikipedia_tr(self):
        self._wiki_task("tr")

    def _wiki_task(self, lang):
        cats = config.WIKI_CATEGORIES[lang]
        ci = int(db.get_state("wiki_%s_cat" % lang, 0) or 0)
        cat = cats[ci % len(cats)]
        cont = db.get_state("wiki_%s_cont_%s" % (lang, cat), None)
        self.log("Wikipedia(%s) kategori: %s" % (lang, cat))
        members, new_cont = sources.wiki_category_members(cat, lang=lang,
                                                          limit=120, cmcontinue=cont)
        added = 0
        c = db.conn()
        # Zaten bildigimiz kavramlari atla
        for title in members:
            if self.stop_flag.is_set():
                break
            if title.startswith("Category:") or title.startswith("Kategori:"):
                continue
            norm = normalize(title)
            row = c.execute("SELECT id FROM concepts WHERE norm=? AND lang=?",
                            (norm, lang)).fetchone()
            if row:
                continue
            s = sources.wiki_summary(title, lang=lang)
            if not s or len(s["extract"]) < 80:
                continue
            db.upsert_concept(s["title"], norm, lang,
                              s.get("description", ""), s["extract"], s["url"])
            added += 1
            if added % 15 == 0:
                c.commit()
        c.commit()
        self.log("Wikipedia(%s) %s: %d yeni kavram" % (lang, cat, added))
        if new_cont:
            db.set_state("wiki_%s_cont_%s" % (lang, cat), new_cont)
        else:
            db.set_state("wiki_%s_cont_%s" % (lang, cat), None)
            db.set_state("wiki_%s_cat" % lang, ci + 1)

    def _task_consolidate(self):
        """Ogrenilenleri isle: kavram grafi, terim istatistikleri, formuller.

        Bu, botun "dusunme" asamasidir: ham metinlerden iliski cikarir.
        """
        c = db.conn()
        last_id = int(db.get_state("consolidate_last_id", 0) or 0)
        rows = c.execute(
            "SELECT id, title, abstract, lang FROM papers WHERE id > ? "
            "ORDER BY id LIMIT 800", (last_id,)).fetchall()
        if not rows:
            db.set_state("consolidate_last_id", 0)
            self.log("Pekistirme: bastan basliyor.")
            return
        # Bilinen kavram adlari (birliktelik grafi icin)
        concept_names = {}
        for r in c.execute("SELECT norm, name FROM concepts WHERE length(norm) > 4"):
            concept_names[r["norm"]] = r["name"]

        tf = {}
        df_docs = {}
        links = {}
        formulas = 0
        islenen = 0
        bulgu_sayisi = 0
        for pi, r in enumerate(rows):
            if pi and pi % 100 == 0:
                c.commit()   # yazma kilidini uzun sure tutma
            text = (r["title"] or "") + " " + (r["abstract"] or "")
            toks = list(tokens(text))
            seen = set()
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
                seen.add(t)
            for t in seen:
                df_docs[t] = df_docs.get(t, 0) + 1
            # BagintI cikarimi — siki ayiklama ve SymPy dogrulamasi
            from . import bagintilar as _bg
            for m in _latex.finditer(text):
                tex = (m.group(1) or m.group(2) or m.group(3) or "").strip()
                if _bg.kaydet(tex, r["title"] or "", r["id"],
                              (r["lang"] or "")):
                    formulas += 1
            # Duz metindeki "E = mc^2" bicimli bagintilar da yakalanir
            for m in re.finditer(r"(?m)^\s*([A-Za-z][\w_]{0,12}\s*=\s*[^=\n]{3,70})$",
                                 text):
                if _bg.kaydet(m.group(1), r["title"] or "", r["id"], ""):
                    formulas += 1
            # Kavram birliktelik grafi
            norm_text = normalize(text)
            present = [n for n in concept_names
                       if len(n) > 5 and n in norm_text]
            present = present[:14]
            for a, b in itertools.combinations(sorted(present), 2):
                links[(a, b)] = links.get((a, b), 0) + 1
            for n in present:
                c.execute("UPDATE concepts SET freq = freq + 1 WHERE norm = ?", (n,))

            # --- Inceleme: cumleleri islevlerine gore ayir ve kavrama bagla ---
            eklenen_bulgu = self._bulgulari_isle(c, r, present, norm_text)
            bulgu_sayisi += eklenen_bulgu
            # Makale gercekten bilgiye donustu mu? (terim + bulgu/kavram)
            uretti = 1 if (eklenen_bulgu or present or len(toks) >= 12) else 0
            c.execute("UPDATE papers SET islendi=? WHERE id=?", (uretti, r["id"]))

            # Makale dongusu de araliklarla kaydediliyor: 800 makalelik tek bir
            # islem, yazma kilidini uzun sure tutup ayni anda gelen sorulari
            # ("database is locked") bekletiyordu.
            islenen += 1
            if islenen % 100 == 0:
                c.commit()
        c.commit()

        # Terim istatistikleri ve baglantilar kucuk islemler halinde yazilir.
        # Tek dev islem, yazma kilidini saniyelerce tutup kullanicinin
        # sorusuna gelen cevabi bekletirdi.
        written = 0
        for t, n in tf.items():
            c.execute(
                "INSERT INTO terms(term, tf, df) VALUES(?,?,?) "
                "ON CONFLICT(term) DO UPDATE SET tf = tf + ?, df = df + ?",
                (t, n, df_docs.get(t, 0), n, df_docs.get(t, 0)))
            written += 1
            if written % 400 == 0:
                c.commit()
        c.commit()

        written = 0
        for (a, b), w in links.items():
            c.execute(
                "INSERT INTO concept_links(a, b, weight) VALUES(?,?,?) "
                "ON CONFLICT(a, b) DO UPDATE SET weight = weight + ?",
                (a, b, w, w))
            c.execute(
                "INSERT INTO concept_links(a, b, weight) VALUES(?,?,?) "
                "ON CONFLICT(a, b) DO UPDATE SET weight = weight + ?",
                (b, a, w, w))
            written += 1
            if written % 400 == 0:
                c.commit()
        c.commit()
        db.set_state("consolidate_last_id", rows[-1]["id"])
        self.log("Inceleme: %d makale okundu — %d terim, %d baglanti, "
                 "%d formul, %d bulgu"
                 % (len(rows), len(tf), len(links), formulas, bulgu_sayisi))

    def _task_kendini_dogrula(self):
        """Formul tabanini periyodik olarak sina.

        Bot bildigini varsaymaz: boyut denetimi ve geri-yerine-koyma ile
        kendi formullerini dogrular, sonucu saklar. Bir hata olursa kayitta
        gorunur ve `kendini dogrula` komutuyla raporlanir.
        """
        from . import dogrulama
        onceki = dogrulama.onbellekten()
        if onceki and (time.time() - (onceki.get("zaman") or 0)) < 6 * 3600:
            self.log("Dogrulama: onbellek taze, atlaniyor.")
            return
        self.log("Dogrulama: formul tabani sinaniyor...")
        s = dogrulama.tum_formuller()
        dogrulama.onbellege_yaz(s)
        self.log("Dogrulama: %d/%d formul iki sinamayi da gecti"
                 % (s["saglam"], s["toplam"]))
        if s["boyut_hatasi"]:
            self.log("Dogrulama UYARI: boyut hatasi -> %s"
                     % ", ".join(x[0] for x in s["boyut_hatasi"][:5]))

    def _task_sentez(self):
        """Makaleleri birlestirip yeni bilgi uret.

        Tek makalenin soyledigi bir iddiadir; birden cok makalenin ayni
        seyi soylemesi bilgidir. Bu gorev uzlasan ifadeleri ve kavramlar
        arasi koprüleri kanit sayisiyla birlikte kaydeder.
        """
        from . import sentezbilgi
        son = db.get_state("sentez_son") or 0
        if time.time() - son < 12 * 3600:
            return
        try:
            u = sentezbilgi.uzlasma_uret(en_fazla=60)
            k = sentezbilgi.kopru_uret(en_fazla=40)
            if u or k:
                self.log("Sentez: %d uzlasan bilgi, %d kavram koprusu "
                         "turetildi (her biri en az %d makaleden)"
                         % (u, k, sentezbilgi.EN_AZ_KAYNAK))
        except Exception as e:
            self.log("Sentez UYARI: %s" % str(e)[:70])
        db.set_state("sentez_son", time.time())

    def _task_bosluk_doldur(self):
        """Kullanicinin cevaplanamayan sorularini HEDEFLI olarak arastir.

        Rastgele okumak yerine, tam olarak sorulan seyi ogrenmek: bot
        konustukca guclenmesinin yolu bu. Her bosluk icin sirasiyla
        Wikipedia, arXiv ve canli arama denenir; bulunan malzeme tabana
        yazilir ve bosluk 'ogrenildi' olarak isaretlenir.
        """
        from . import bosluk
        acik = bosluk.oncelikli(limit=3)
        if not acik:
            return
        for g in acik:
            if self.stop_flag.is_set():
                break
            # ONEMLI: aramada normalize edilmis terimler degil, kullanicinin
            # YAZDIGI metin kullanilir. "kuantum dolanikligi" hicbir sey
            # bulmuyor, "kuantum dolanıklığı" doğru maddeyi getiriyor.
            sorgu = (g["soru"] or "").strip()
            if len(sorgu) < 4:
                bosluk.denendi(g["norm"])
                continue
            kazanim = 0
            self.log("Bosluk: '%s' arastiriliyor (%d kez soruldu)"
                     % (sorgu, g["sayac"]))

            # 1) Wikipedia — kavram tanimi (kullanicinin dilinde)
            ana_dil = g["lang"] or "tr"
            ingilizce_terim = None
            # Kullanicinin yazdigi terim kaynaklardaki terimden farkli
            # olabilir ("Kazimir etkisi" / "Casimir effect"). Dil modeli
            # bunu cevirir; sonuc gercek bir fizik maddesine denk gelirse
            # kabul edilir.
            try:
                from . import dil as _dil
                if _dil.MODEL.kurulu_mu():
                    ingilizce_terim = _dil.MODEL.ingilizce_terim(sorgu, ana_dil)
            except Exception:
                ingilizce_terim = None

            aramalar = []
            if ingilizce_terim:
                aramalar.append((ingilizce_terim, "en"))
            aramalar.append((sorgu, ana_dil))
            # Kademeli kisaltma: uzun cumle hicbir sey bulmuyor
            kisa = " ".join((g["terimler"] or "").split()[:2])
            if kisa:
                aramalar.append((kisa, ana_dil))

            for arama, dil_kodu in aramalar:
                try:
                    sonuc = sources.wiki_search(arama, lang=dil_kodu, limit=3)
                except Exception:
                    sonuc = []
                for s_ in sonuc:
                    baslik = s_["title"] if isinstance(s_, dict) else s_
                    try:
                        oz = sources.wiki_summary(baslik, lang=dil_kodu)
                    except Exception:
                        oz = None
                    if not oz or len(oz["extract"]) < 120:
                        continue
                    # Fizik disi sonuclari ele: "Kazimir etkisi" aramasi
                    # ressam "Kazimir Malevic"i getiriyordu.
                    try:
                        if not kalite.fizik_ilgili(
                                oz["title"] + " " + oz["extract"]):
                            continue
                    except Exception:
                        pass
                    db.upsert_concept(oz["title"], normalize(oz["title"]),
                                      dil_kodu, oz.get("description", ""),
                                      oz["extract"], oz["url"])
                    kazanim += 1
                    if ingilizce_terim is None:
                        ingilizce_terim = (
                            baslik if dil_kodu == "en" else
                            sources.wiki_langlink(baslik, dil_kodu, "en"))
                if kazanim:
                    break

            # 2) arXiv — konunun guncel arastirmasi (Ingilizce terimle)
            makaleler = []
            if ingilizce_terim:
                try:
                    makaleler = sources.arxiv_fetch(query=ingilizce_terim,
                                                    max_results=8)
                except Exception:
                    makaleler = []
            for m in makaleler:
                try:
                    if not kalite.kabul_edilir_mi(m):
                        continue
                except Exception:
                    pass
                yeni, _ = db.add_paper(
                    source="arxiv", ext_id=m.get("ext_id") or m.get("id"),
                    title=m.get("title", ""), abstract=m.get("abstract", ""),
                    authors=m.get("authors", ""),
                    categories=m.get("categories", ""), lang="en",
                    url=m.get("url", ""), published=m.get("published", ""),
                    kalite=float(m.get("kalite", 0) or 0))
                if yeni:
                    kazanim += 1

            # Dogru terimi ogrendiysek kullanicinin yazdigi bicimle esle:
            # bir dahaki sefere "Kazimir etkisi" sorusu dogrudan "Casimir
            # effect" malzemesini bulsun.
            if kazanim and ingilizce_terim:
                try:
                    bosluk.takma_ad_kaydet(g["soru"], ingilizce_terim)
                    for kelime_dizisi in (" ".join(
                            (g["terimler"] or "").split()[:2]),):
                        if kelime_dizisi:
                            bosluk.takma_ad_kaydet(kelime_dizisi,
                                                   ingilizce_terim)
                except Exception:
                    pass
            bosluk.denendi(g["norm"], basarili=kazanim > 0)
            if kazanim:
                self.log("Bosluk: '%s' icin %d yeni kaynak ogrenildi"
                         % (sorgu, kazanim))
            else:
                self.log("Bosluk: '%s' icin kaynak bulunamadi" % sorgu)

    # Universite depolari: her calismada birinden sayfa cekilir, kaldigi
    # yer saklanir. Konular donusumlu taranir ki tek bir alanda yigilma
    # olmasin.
    DEPO_KONULARI = [
        "quantum mechanics", "thermodynamics", "electromagnetism", "optics",
        "condensed matter", "astrophysics", "nuclear physics", "plasma",
        "fluid dynamics", "relativity", "particle physics", "biophysics",
        "computational physics", "materials science", "photonics",
        "statistical mechanics", "acoustics", "geophysics",
    ]

    def _depo_ekle(self, kayitlar, kaynak):
        """Depodan gelen kayitlari kalite kapisindan gecirip yaz."""
        eklenen, elenen = 0, 0
        for m in kayitlar:
            if self.stop_flag.is_set():
                break
            metin = (m.get("title") or "") + " " + (m.get("abstract") or "")
            try:
                if not kalite.fizik_ilgili(metin):
                    elenen += 1
                    continue
            except Exception:
                pass
            try:
                puan = kalite.puan(m)
            except Exception:
                puan = 40.0
            yeni, _ = db.add_paper(
                source=kaynak, ext_id=m.get("ext_id", ""),
                title=m.get("title", ""), abstract=m.get("abstract", ""),
                authors=m.get("authors", ""),
                categories=m.get("categories", ""), lang="en",
                url=m.get("url", ""), published=m.get("published", ""),
                atif=-1, hakemli=int(m.get("hakemli", -1)), geri_cekik=0,
                alan="physics", dergi=m.get("dergi", ""), kalite=float(puan))
            eklenen += 1 if yeni else 0
        return eklenen, elenen

    def _task_universite_depolari(self):
        """Universite depolarindan ve acik kitaplardan ogren.

        Zenodo (CERN), OpenAIRE (Avrupa universiteleri), HAL (Fransa) ve
        OAPEN (acik erisim kitaplar). Her biri acik API sunar, anahtar
        istemez ve kurumsal arastirma ciktisi tasir — makale ozetinden
        farkli olarak tez, rapor ve kitap da icerir.
        """
        i = int(db.get_state("depo_sira", 0) or 0)
        konu = self.DEPO_KONULARI[i % len(self.DEPO_KONULARI)]
        kaynaklar = [
            ("zenodo", lambda: sources.zenodo_fetch(konu, size=50)),
            ("openaire", lambda: sources.openaire_fetch(konu, size=50)),
            ("hal", lambda: sources.hal_fetch(konu, rows=50)),
            ("oapen", lambda: sources.oapen_kitaplar(konu, limit=25)),
        ]
        k_i = int(db.get_state("depo_kaynak", 0) or 0)
        ad, fn = kaynaklar[k_i % len(kaynaklar)]
        try:
            kayitlar = fn()
        except Exception as e:
            self.log("Depo(%s): alinamadi — %s" % (ad, str(e)[:60]))
            db.set_state("depo_kaynak", k_i + 1)
            return
        eklenen, elenen = self._depo_ekle(kayitlar, ad)
        self.log("Depo(%s) %s: %d yeni, %d fizik disi elendi"
                 % (ad, konu, eklenen, elenen))
        db.set_state("depo_kaynak", k_i + 1)
        if (k_i + 1) % len(kaynaklar) == 0:
            db.set_state("depo_sira", i + 1)

    def _task_ders_kitabi(self):
        """OpenStax ders kitaplarindan bolum bolum ogren.

        Makale ozeti bir arastirma sonucunu anlatir, KONUYU ogretmez.
        Ogretmen olmak icin asil malzeme ders kitabidir: ogrenme hedefleri,
        kavram anlatimi, cozumlu ornek. OpenStax kitaplari acik lisanslidir
        ve tam metin erisilebilir.

        Her calismada bir kitaptan birkac bolum alinir; kaldigi yer
        saklanir, boylece kitaplar zamanla bastan sona okunur.
        """
        try:
            kitaplar = sources.openstax_kitaplar()
        except Exception as e:
            self.log("Ders kitabi: kaynak alinamadi (%s)" % str(e)[:60])
            return
        if not kitaplar:
            return
        ki = int(db.get_state("ders_kitabi_sira", 0) or 0)
        kitap = kitaplar[ki % len(kitaplar)]
        try:
            bolumler, arsiv, ver, kitap_adi = sources.openstax_bolumler(
                kitap["uuid"])
        except Exception as e:
            self.log("Ders kitabi: %s icindekiler alinamadi (%s)"
                     % (kitap["baslik"], str(e)[:50]))
            db.set_state("ders_kitabi_sira", ki + 1)
            return

        anahtar = "ders_kitabi_bolum_%s" % kitap["uuid"]
        bi = int(db.get_state(anahtar, 0) or 0)
        eklenen = 0
        for sayfa_id, baslik in bolumler[bi:bi + 6]:
            if self.stop_flag.is_set():
                break
            bi += 1
            try:
                b = sources.openstax_bolum(kitap["uuid"], ver, arsiv, sayfa_id)
            except Exception:
                continue
            metin = b["metin"]
            # Cok kisa sayfalar (baslik, referans listesi) ogretici degil
            if len(metin) < 900:
                continue
            yeni, _pid = db.add_paper(
                source="openstax", ext_id=sayfa_id,
                title="%s — %s" % (kitap_adi, b["baslik"] or baslik),
                abstract=metin[:20000], authors="OpenStax",
                categories="ders kitabi; %s" % kitap_adi, lang="en",
                url=b["url"], published="", atif=-1, hakemli=1,
                geri_cekik=0, alan="physics", dergi=kitap_adi,
                kalite=85.0)      # ders kitabi: yuksek guvenilirlik
            if yeni:
                eklenen += 1
        db.set_state(anahtar, bi)
        if bi >= len(bolumler):
            db.set_state("ders_kitabi_sira", ki + 1)   # kitap bitti, sonraki
            self.log("Ders kitabi: %s tamamlandi" % kitap_adi)
        if eklenen:
            self.log("Ders kitabi: %s — %d yeni bolum okundu (%d/%d)"
                     % (kitap_adi, eklenen, bi, len(bolumler)))

    def _task_video_ders(self):
        """Acik ders VIDEOLARINDAN ogren (MIT OpenCourseWare).

        Kullanici "youtube videolari ve internetteki fizik icerigi" ile
        beslenmesini istedi. YouTube'un altyazi ucu oturum belirteci
        istiyor ve bes bicimin besi de bos dondu (olculdu). Ama MIT OCW
        ders videolari hem YouTube'da yayinlaniyor hem de tam
        transkriptleri acik lisansla (CC BY-NC-SA) kendi sunucusunda
        duruyor. Videonun KONUSMASINI boylece izinli ve eksiksiz
        aliyoruz.

        Ders anlatimi makale ozetinden farkli bir malzeme: hoca konuyu
        sifirdan kurar, sezgi verir, tahtada ornek cozer. Ogretmen olmak
        icin tam da bu gerekir.
        """
        konular = ["Physics", "Chemistry", "Biology", "Mathematics"]
        ki = int(db.get_state("video_ders_konu", 0) or 0)
        konu = konular[ki % len(konular)]
        offset = int(db.get_state("video_ders_offset_%s" % konu, 0) or 0)
        try:
            dersler = sources.ocw_video_dersleri(konu, limit=12, offset=offset)
        except Exception as e:
            self.log("Video ders: liste alinamadi (%s)" % str(e)[:60])
            return
        if not dersler:
            # Bu konu bitti; bastan basla ve siradaki konuya gec
            db.set_state("video_ders_offset_%s" % konu, 0)
            db.set_state("video_ders_konu", ki + 1)
            return

        eklenen = 0
        for d in dersler:
            if self.stop_flag.is_set():
                break
            offset += 1
            try:
                metin = sources.ocw_video_metni(d["url"])
            except Exception:
                continue
            # Kisa tanitim videolari ders degildir
            if not metin or len(metin) < 1200:
                continue
            baslik = d["baslik"]
            if d.get("kurs"):
                baslik = "%s — %s" % (d["kurs"], baslik)
            kaynakca = d.get("aciklama") or ""
            govde = metin[:20000]
            if kaynakca:
                govde = kaynakca + "\n\n" + govde
            yeni_mi, _pid = db.add_paper(
                source="ocw_video", ext_id="ocwv_%s" % d["ext_id"],
                title=baslik, abstract=govde,
                authors="MIT OpenCourseWare",
                categories="ders videosu; %s" % konu.lower(),
                lang="en", url=d["url"], published="", atif=-1,
                hakemli=1, geri_cekik=0, alan=konu.lower(),
                dergi="MIT OpenCourseWare", kalite=88.0)
            if yeni_mi:
                eklenen += 1
        db.set_state("video_ders_offset_%s" % konu, offset)
        db.set_state("video_ders_konu", ki + 1)
        if eklenen:
            self.log("Video ders: %s — %d yeni ders anlatimi dinlendi"
                     % (konu, eklenen))

    def _task_genisle(self):
        """Okunanlardan yeni YETENEK uret.

        Bot yalnizca makale biriktirmemeli; biriktirdikce yapabildikleri de
        artmali. Bu gorev iki sey yapar:

        1. Yeterli makale biriken her fizik alani icin yol haritasi uretir
           ve mevcut haritalarin "guncel konular" asamasini tazeler.
        2. Dogrulanmis formulleri birlestirerek yeni bagintilar turetir;
           her biri boyut denetimi ve geri yerine koymadan gecmek zorunda.

        Ikisi de pahali oldugu icin gunde bir kez calisir.
        """
        from . import genisleme
        son = db.get_state("genisleme_son") or 0
        if time.time() - son < 24 * 3600:
            return
        try:
            n_harita = genisleme.haritalari_tazele()
            self.log("Genisleme: %d yol haritasi guncel (makalelerden)"
                     % n_harita)
        except Exception as e:
            self.log("Genisleme UYARI: yol haritasi uretilemedi: %s" % e)
        try:
            kabul, denendi = genisleme.formul_uret(en_fazla=15)
            if kabul:
                toplam = genisleme.formulleri_kaydet(kabul)
                genisleme.formulleri_bagla()
                self.log("Genisleme: %d yeni formul turetildi ve dogrulandi "
                         "(%d aday denendi, taban %d formul)"
                         % (len(kabul), denendi, toplam))
            else:
                self.log("Genisleme: dogrulamayi gecen yeni formul cikmadi "
                         "(%d aday denendi)" % denendi)
        except Exception as e:
            self.log("Genisleme UYARI: formul uretilemedi: %s" % e)
        db.set_state("genisleme_son", time.time())

    def _bulgulari_isle(self, c, row, present, norm_text):
        """Bir makalenin ozetini cumle cumle inceleyip bulgulari kaydet."""
        from .retrieval import split_sentences
        metin = (row["abstract"] or "")
        if len(metin) < 60:
            return 0
        lang = row["lang"] or "en"
        eklenen = 0
        for cumle in split_sentences(metin)[:14]:
            c_temiz = re.sub(r"\s+", " ", cumle).strip()
            if not (40 <= len(c_temiz) <= 400):
                continue
            tur = cumle_turu(c_temiz)
            if not tur:
                continue
            # Cumlenin gectigi kavrami bul (yoksa genel bulgu olarak sakla)
            cn = normalize(c_temiz)
            ilgili = ""
            for n in present:
                if n in cn:
                    ilgili = n
                    break
            # Skor: bilgi yogunlugu (uzunluk + sayisal deger + kavram varligi)
            skor = min(len(c_temiz) / 200.0, 1.5)
            if _SAYISAL.search(c_temiz):
                skor += 0.6
            if ilgili:
                skor += 0.8
            try:
                c.execute(
                    "INSERT OR IGNORE INTO insights"
                    "(norm, tur, cumle, paper_id, lang, skor, at) "
                    "VALUES(?,?,?,?,?,?,?)",
                    (ilgili, tur, c_temiz, row["id"], lang, skor, time.time()))
                eklenen += 1
            except sqlite3.Error:
                pass

            # Kavramlar arasi adlandirilmis iliski
            m = _ILISKI_FIIL.search(c_temiz)
            if m and len(present) >= 2:
                once = cn[:m.start()]
                sonra = cn[m.end():]
                a = next((n for n in present if n in once), None)
                b = next((n for n in present if n in sonra), None)
                if a and b and a != b:
                    try:
                        c.execute(
                            "INSERT INTO relations(a, fiil, b, sayi, ornek) "
                            "VALUES(?,?,?,1,?) ON CONFLICT(a, fiil, b) "
                            "DO UPDATE SET sayi = sayi + 1",
                            (a, m.group(1).lower(), b, c_temiz[:300]))
                    except sqlite3.Error:
                        pass
        return eklenen

    # -------------------------------------------------------------- yardimci
    def _ingest(self, papers):
        """Makaleleri kalite kapisindan gecirerek al.

        Stoklamak amac degil: fizik disi, geri cekilmis ya da ozeti bilgi
        tasimayan makaleler hic alinmaz. Reddedilenler sayilir ve kayda gecer.
        """
        from . import kalite as _kal
        c = db.conn()
        n = 0
        red = 0
        nedenler = {}
        for p in papers:
            if not p.get("title") or not p.get("abstract"):
                red += 1
                nedenler["basliksiz/ozetsiz"] = nedenler.get("basliksiz/ozetsiz", 0) + 1
                continue
            kabul, neden = _kal.kabul_edilir_mi(p)
            if not kabul:
                red += 1
                nedenler[neden] = nedenler.get(neden, 0) + 1
                continue
            ok, _ = db.add_paper(
                p["source"], p["ext_id"], p["title"], p["abstract"],
                p.get("authors", ""), p.get("categories", ""),
                p.get("lang", "en"), p.get("url", ""), p.get("published", ""),
                atif=p.get("atif", -1), hakemli=p.get("hakemli", -1),
                geri_cekik=p.get("geri_cekik", 0), alan=p.get("alan"),
                dergi=p.get("dergi"), kalite=_kal.puan(p))
            if ok:
                n += 1
        c.commit()
        db.bump_state("total_ingested", n)
        db.bump_state("total_rejected", red)
        if red:
            enbuyuk = sorted(nedenler.items(), key=lambda kv: -kv[1])[:2]
            self.log("  kalite kapisi: %d kabul, %d red (%s)"
                     % (n, red, ", ".join("%s×%d" % (k, v) for k, v in enbuyuk)))
        return n


LEARNER = Learner()
