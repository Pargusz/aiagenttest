"""Dil katmani: yerel acik kaynak dil modeli.

Tasarim ilkesi — **model dil icindir, fizik icin degil.**

Bir dil modeli akici cumle kurar ama sayilari uydurabilir. Bu yuzden burada
model asla hesap yapmaz ve asla kendi bilgisinden fizik anlatmaz. Gorevi
yalnizca sudur:

  1. Kullanicinin ne sordugunu anlamak (serbest, dagik, eksik cumleleri de)
  2. Dogrulanmis motorlardan gelen sonucu akici bir dille anlatmak

Sayilar SymPy'den, formuller dogrulanmis tabandan, bilgiler okunmus
makalelerden gelir. Model bunlari yalnizca *ifade eder*. Boylece hem akici
hem guvenilir olur.

Model tamamen bu bilgisayarda calisir: API yok, anahtar yok, internete
hicbir sey gitmez. Model dosyasi yoksa sistem eskisi gibi calismaya devam
eder — dil katmani istege baglidir.
"""
import os
import re
import threading

from . import config

MODEL_DIR = os.path.join(config.DATA_DIR, "model")

# Birden fazla model varsa hangisi kullanilacak. Ustteki kazanir.
# PARGUSZ_MODEL ortam degiskeniyle dosya adi dogrudan verilebilir.
TERCIH_SIRASI = ("qwen3-8b", "qwen3", "qwen2.5-14b", "qwen2.5-7b", "qwen2.5")

# Qwen3 varsayilan olarak <think>...</think> blogu uretir. Bizim isimizde
# model akil yurutmuyor, yalnizca dogrulanmis baglami anlatiyor; bu blok
# hem yavaslatir hem cevaba karisir. Kapatiyor ve yine de gelirse siliyoruz.
_DUSUNME_BLOGU = re.compile(r"<think>.*?</think>\s*", re.S | re.I)

# Sistem yonergesi: modelin sinirlarini net cizer
SISTEM_TR = """Sen ParguszPhysics'sin: fizik konusunda yardimci olan bir asistansin.

KATI KURALLAR:
1. SANA VERILEN BAGLAM DISINDA fizik bilgisi uydurma. Baglamda yoksa
   "bu konuda elimde bilgi yok" de.
2. ASLA kendi kafandan sayisal hesap yapma. Hesap sonuclari sana baglamda
   verilir; sen yalnizca onlari aktarirsin.
3. Baglamdaki sayilari, formulleri ve birimleri AYNEN koru; degistirme.
4. DIL: Duzgun ve dogal Turkce yaz. Baglamda gecen Turkce fizik terimlerini
   AYNEN kullan (entropi, ic enerji, duzensizlik, yalitilmis sistem gibi).
   Ingilizce kelime karistirma ("disorder", "integrate" gibi kelimeler
   kullanma), Turkcesini yaz. Uydurma kelime turetme.
5. Kisa ve net ol. Gereksiz giris cumlesi kurma.
6. Emin olmadigin seyi soylemektense bilmedigini soyle."""

SISTEM_EN = """You are ParguszPhysics, a physics assistant.

STRICT RULES:
1. Do NOT invent physics beyond the CONTEXT you are given. If it is not in
   the context, say you don't have that information.
2. NEVER compute numbers yourself. Calculation results are provided in the
   context; you only relay them.
3. Keep numbers, formulas and units from the context EXACTLY as given.
4. Reply in Turkish if the user wrote Turkish, in English if English.
5. Be concise. No filler openings.
6. Prefer saying you don't know over guessing."""


class DilModeli(object):
    """Yerel GGUF modelini tembel yukleyen sarmalayici."""

    def __init__(self):
        self._llm = None
        self._kilit = threading.Lock()
        self._hata = None
        self._yol = None

    # ── kullanilabilirlik ──────────────────────────────────────────────
    def model_dosyasi(self):
        """Model klasorundeki ilk .gguf dosyasini bul."""
        if self._yol and os.path.exists(self._yol):
            return self._yol
        try:
            adaylar = [f for f in os.listdir(MODEL_DIR)
                       if f.lower().endswith(".gguf")]
        except OSError:
            return None
        if not adaylar:
            return None

        # 1) Acik secim
        istenen = os.environ.get("PARGUSZ_MODEL", "").strip()
        if istenen:
            tam = [f for f in adaylar if istenen.lower() in f.lower()]
            if tam:
                self._yol = os.path.join(MODEL_DIR, tam[0])
                return self._yol

        # 2) Tercih sirasi
        for anahtar in TERCIH_SIRASI:
            eslesen = [f for f in adaylar if anahtar in f.lower()]
            if eslesen:
                self._yol = os.path.join(MODEL_DIR, eslesen[0])
                return self._yol

        # 3) Son care: en buyuk dosya
        adaylar.sort(key=lambda f: os.path.getsize(os.path.join(MODEL_DIR, f)),
                     reverse=True)
        self._yol = os.path.join(MODEL_DIR, adaylar[0])
        return self._yol

    def kurulu_mu(self):
        """Hem kutuphane hem model dosyasi var mi?

        PARGUSZ_DIL=0 ile kapatilabilir (testler ve dusuk bellekli calisma
        icin); bu durumda sistem tamamen kural tabanli calisir.
        """
        if os.environ.get("PARGUSZ_DIL", "1") == "0":
            return False
        try:
            import llama_cpp  # noqa: F401
        except ImportError:
            return False
        return self.model_dosyasi() is not None

    def durum(self):
        try:
            import llama_cpp  # noqa: F401
            kutuphane = True
        except ImportError:
            kutuphane = False
        dosya = self.model_dosyasi()
        return {
            "kutuphane": kutuphane,
            "model": os.path.basename(dosya) if dosya else None,
            "boyut_mb": round(os.path.getsize(dosya) / 1e6) if dosya else 0,
            "yuklu": self._llm is not None,
            "hata": self._hata,
        }

    # ── yukleme ────────────────────────────────────────────────────────
    def yukle(self):
        """Modeli bellege al. Ilk cagride birkac saniye surer.

        PARGUSZ_DIL=0 burada da onurlandirilmali: bayragi yalnizca
        `kurulu_mu` denetliyordu, bu yuzden modeli dogrudan cagiran
        yardimcilar (terim cikarma, formul secimi) kapaliyken bile 4.7 GB
        modeli yuklemeye calisiyordu.
        """
        if os.environ.get("PARGUSZ_DIL", "1") == "0":
            return None
        if self._llm is not None:
            return self._llm
        with self._kilit:
            if self._llm is not None:
                return self._llm
            yol = self.model_dosyasi()
            if not yol:
                self._hata = "model dosyasi bulunamadi"
                return None
            try:
                from llama_cpp import Llama
            except ImportError as e:
                self._hata = "llama-cpp-python kurulu degil: %s" % e
                return None
            try:
                self._llm = Llama(
                    model_path=yol,
                    n_ctx=4096,          # baglam penceresi
                    n_threads=8,
                    n_gpu_layers=-1,     # Apple Silicon'da Metal ile tumu GPU'ya
                    verbose=False,
                )
                self._hata = None
            except Exception as e:
                self._hata = str(e)
                self._llm = None
            return self._llm

    def bosalt(self):
        with self._kilit:
            self._llm = None

    # ── uretim ─────────────────────────────────────────────────────────
    def yanitla(self, soru, baglam="", lang="tr", gecmis=None, max_token=380):
        """Baglama dayali yanit uret. Model yoksa None doner."""
        llm = self.yukle()
        if llm is None:
            return None

        sistem = SISTEM_TR if lang == "tr" else SISTEM_EN
        # Qwen3 ailesinde dusunme kipini kapatan isaret
        if "qwen3" in (self.model_dosyasi() or "").lower():
            sistem += "\n/no_think"
        mesajlar = [{"role": "system", "content": sistem}]
        for m in (gecmis or [])[-2:]:
            rol = "user" if m.get("role") == "user" else "assistant"
            icerik = (m.get("content") or "")[:600]
            if icerik:
                mesajlar.append({"role": rol, "content": icerik})

        if baglam:
            kullanici = (
                ("BAGLAM (yalnizca bunu kullan):\n%s\n\nSORU: %s"
                 if lang == "tr" else
                 "CONTEXT (use only this):\n%s\n\nQUESTION: %s")
                % (baglam[:5000], soru))
        else:
            kullanici = soru
        mesajlar.append({"role": "user", "content": kullanici})

        try:
            cikti = llm.create_chat_completion(
                messages=mesajlar,
                max_tokens=max_token,
                temperature=0.3,      # dusuk: uydurmayi azaltir
                top_p=0.9,
                repeat_penalty=1.05,
            )
            metin = (cikti["choices"][0]["message"]["content"] or "")
            # Dusunme blogu gelirse kullaniciya gosterme
            metin = _DUSUNME_BLOGU.sub("", metin)
            metin = metin.replace("<think>", "").replace("</think>", "")
            return metin.strip()
        except Exception as e:
            self._hata = str(e)
            return None

    def terim_cikar(self, soru, lang="tr"):
        """Gunluk dildeki soruyu fizik terimlerine cevir.

        Modelin en guclu oldugu is bu: dil. "Topun havada ne kadar kaldigi"
        cumlesini "serbest dusme, ucus suresi, egik atis" terimlerine cevirir;
        formulu SECMEZ, hesap YAPMAZ. Terimler dogrulanmis formul tabaninda
        deterministik olarak aranir. Boylece anlama ile dogruluk ayri kalir.
        """
        llm = self.yukle()
        if llm is None or not (soru or "").strip():
            return []
        sistem = ("Fizik terimi cikaran bir araçsin. Cevap uretmezsin."
                  if lang == "tr" else
                  "You extract physics terms. You do not answer questions.")
        if "qwen3" in (self.model_dosyasi() or "").lower():
            sistem += "\n/no_think"
        ornek = ("Ornek:\nSoru: topun havada ne kadar kaldigini bulurum\n"
                 "Terimler: serbest dusme, ucus suresi, egik atis, dusme zamani\n\n"
                 if lang == "tr" else
                 "Example:\nQuestion: how long does the ball stay in the air\n"
                 "Terms: free fall, time of flight, projectile motion\n\n")
        yonerge = (
            ("Asagidaki sorunun konusunu adlandiran 3-6 fizik terimi yaz. "
             "Sadece terimleri virgulle ayirarak yaz, baska hicbir sey yazma.\n\n"
             "%sSoru: %s\nTerimler:" if lang == "tr" else
             "Write 3-6 physics terms naming the topic of this question. "
             "Only comma-separated terms, nothing else.\n\n"
             "%sQuestion: %s\nTerms:") % (ornek, soru[:400]))
        try:
            cikti = llm.create_chat_completion(
                messages=[{"role": "system", "content": sistem},
                          {"role": "user", "content": yonerge}],
                max_tokens=48, temperature=0.0)
            metin = _DUSUNME_BLOGU.sub(
                "", cikti["choices"][0]["message"]["content"] or "")
            metin = metin.replace("<think>", "").replace("</think>", "")
        except Exception:
            return []
        metin = metin.split("\n")[0]
        terimler = []
        for t in re.split(r"[,;]", metin):
            t = t.strip(" .:-\"'*").lower()
            # Model cevap uretmeye kalkarsa uzun cumleyi ele
            if 2 < len(t) <= 40 and len(t.split()) <= 4:
                terimler.append(t)
        return terimler[:6]

    def sohbet(self, mesaj, lang="tr", gecmis=None, ad=None):
        """Gunluk sohbet: selam, tesekkur, kisisel muhabbet.

        Fizik SORULARI icin kullanilmaz — orada baglam zorunludur. Burada
        amac dogal konusmak: kullanici "merhaba, ben Polat" dediginde
        katalog okumak yerine insan gibi karsilik vermek.
        """
        llm = self.yukle()
        if llm is None:
            return None
        if lang == "tr":
            sistem = (
                "Sen ParguszPhysics'sin: fizik ve MATLAB ogreten bir "
                "asistan. Dogal, sicak ve KISA konus (en fazla 2-3 cumle). "
                "Ozelliklerini listeleme, katalog okuma. Fizik bilgisi "
                "UYDURMA — teknik bir soru gelirse kisaca karsilik ver, "
                "ayrintiyi sistemin dogrulanmis bilgisi verir."
                + (" Kullanicinin adi %s." % ad if ad else ""))
        else:
            sistem = (
                "You are ParguszPhysics, a physics and MATLAB tutor. Be "
                "natural, warm and SHORT (2-3 sentences max). Do not list "
                "your features. Never invent physics facts."
                + (" The user's name is %s." % ad if ad else ""))
        if "qwen3" in (self.model_dosyasi() or "").lower():
            sistem += "\n/no_think"
        mesajlar = [{"role": "system", "content": sistem}]
        for m in (gecmis or [])[-4:]:
            rol = "user" if m.get("role") == "user" else "assistant"
            icerik = (m.get("content") or "")[:400]
            if icerik:
                mesajlar.append({"role": rol, "content": icerik})
        mesajlar.append({"role": "user", "content": mesaj[:600]})
        try:
            cikti = llm.create_chat_completion(
                messages=mesajlar, max_tokens=160, temperature=0.6, top_p=0.9)
            metin = _DUSUNME_BLOGU.sub(
                "", cikti["choices"][0]["message"]["content"] or "")
            return metin.replace("<think>", "").replace("</think>", "").strip()
        except Exception:
            return None

    def ingilizce_terim(self, soru, lang="tr"):
        """Sorudaki fizik konusunu Ingilizce standart terime cevir.

        Kullanici "Kazimir etkisi" yazar; kaynaklarda "Casimir effect"
        geciyor. Bu bir DIL isidir — modelin en guclu oldugu yer. Sonuc
        dogrudan kullanilmaz: gercekten var olan bir Wikipedia fizik
        maddesine karsilik geliyorsa kabul edilir.
        """
        llm = self.yukle()
        if llm is None or not (soru or "").strip():
            return None
        sistem = ("Fizik terimi ceviren bir aracsin. Yalnizca terimi yaz."
                  if lang == "tr" else "You translate physics terms.")
        if "qwen3" in (self.model_dosyasi() or "").lower():
            sistem += "\n/no_think"
        yonerge = (
            "Asagidaki sorunun konusunu Ingilizce STANDART fizik terimiyle "
            "yaz. Yalnizca terimi yaz, 1-4 kelime, baska hicbir sey yazma.\n\n"
            "Ornek:\nSoru: Kazimir etkisi nedir\nTerim: Casimir effect\n\n"
            "Soru: %s\nTerim:" % soru[:200])
        try:
            cikti = llm.create_chat_completion(
                messages=[{"role": "system", "content": sistem},
                          {"role": "user", "content": yonerge}],
                max_tokens=20, temperature=0.0)
            metin = _DUSUNME_BLOGU.sub(
                "", cikti["choices"][0]["message"]["content"] or "")
            metin = metin.replace("<think>", "").replace("</think>", "")
        except Exception:
            return None
        terim = metin.strip().split("\n")[0].strip(" .:\"'*")
        if 2 < len(terim) <= 60 and len(terim.split()) <= 5:
            return terim
        return None

    def formul_esle(self, soru, adaylar, lang="tr"):
        """Serbest bir sorudan dogru formulu sec.

        Anahtar kelime aramasi "topun havada ne kadar kaldigini nasil bulurum"
        gibi bir cumleyi tutamiyor. Burada modele YALNIZCA aday formul
        listesi verilir ve birini secmesi istenir. Model formul uretmez,
        hesap yapmaz — sadece secer. Secilen formul yine SymPy ile cozulur,
        dolayisiyla dogruluk riski yoktur.
        """
        llm = self.yukle()
        if llm is None or not adaylar:
            return None
        liste = "\n".join(
            "%d) %s  [%s]  degiskenler: %s"
            % (i + 1, (f["tr"] if lang == "tr" else f["en"]), f["eq"],
               ", ".join(f["vars"].keys()))
            for i, f in enumerate(adaylar[:12]))
        yonerge = (
            "Asagida numarali fizik formulleri var. Kullanicinin sorusunu "
            "cozmek icin HANGISI kullanilir?\n"
            "YALNIZCA numarayi yaz. Hicbiri uymuyorsa 0 yaz. Baska hicbir "
            "sey yazma.\n\n%s\n\nSoru: %s\nNumara:" % (liste, soru))
        sistem = ("Sen bir fizik asistanisin. Yalnizca istenen numarayi yaz."
                  if lang == "tr" else
                  "You are a physics assistant. Output only the number.")
        if "qwen3" in (self.model_dosyasi() or "").lower():
            sistem += "\n/no_think"
        try:
            cikti = llm.create_chat_completion(
                messages=[{"role": "system", "content": sistem},
                          {"role": "user", "content": yonerge}],
                max_tokens=24, temperature=0.0)
            metin = _DUSUNME_BLOGU.sub(
                "", cikti["choices"][0]["message"]["content"] or "")
            metin = metin.replace("<think>", "").replace("</think>", "")
        except Exception:
            return None
        m = re.search(r"\d+", metin)
        if not m:
            return None
        n = int(m.group(0))
        if 1 <= n <= len(adaylar[:12]):
            return adaylar[n - 1]
        return None

    def niyet_coz(self, mesaj, lang="tr"):
        """Serbest bir cumleden ne istendigini cikar.

        Kural tabanli siniflandirici tanimadiginda devreye girer. Model
        yalnizca etiket uretir; cevabi yine dogrulanmis motorlar verir.
        """
        llm = self.yukle()
        if llm is None:
            return None
        yonerge = (
            "Kullanicinin fizik sorusunu su etiketlerden BIRINE ata ve "
            "yalnizca etiketi yaz, baska hicbir sey yazma:\n"
            "hesap, formul, konu, neden, nasil, karsilastir, makale, matlab, "
            "birim, sabit, ornek, yol_haritasi, sohbet\n\n"
            "Ayrica konuyu iki-uc kelimeyle ozetle.\n"
            "Bicim: ETIKET | konu\n\nSoru: %s" % mesaj)
        try:
            cikti = llm.create_chat_completion(
                messages=[{"role": "user", "content": yonerge}],
                max_tokens=32, temperature=0.0)
            metin = (cikti["choices"][0]["message"]["content"] or "")
            metin = _DUSUNME_BLOGU.sub("", metin).strip()
        except Exception:
            return None
        if "|" in metin:
            etiket, _, konu = metin.partition("|")
            return {"niyet": etiket.strip().lower(), "konu": konu.strip()}
        return {"niyet": metin.split()[0].lower() if metin else "", "konu": ""}


MODEL = DilModeli()
