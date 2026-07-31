"""Yerel HTTP sunucusu ve JSON API.

Sadece Python standart kutuphanesi kullanir; ek bagimlilik yoktur.
Sunucu yalnizca 127.0.0.1 uzerinde dinler, yani disaridan erisilemez.
"""
import json
import os
import re
import mimetypes
import posixpath
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import config, db, brain, learner, knowledge, formulas, units, belge


class Handler(BaseHTTPRequestHandler):
    server_version = "ParguszPhysics/" + config.VERSION
    protocol_version = "HTTP/1.1"

    # --- log gurultusunu kis
    def log_message(self, fmt, *args):
        if "/api/" in (self.path or "") and "durum" not in (self.path or ""):
            return
        return

    # ------------------------------------------------------------ yardimci
    def _send(self, code, body, ctype="application/json; charset=utf-8",
              extra_headers=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in self._cors_basliklari().items():
            self.send_header(k, v)
        for k, v in (extra_headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _cors_basliklari(self):
        """Baska bir alandan (GitHub Pages) gelen istege izin ver.

        Yalnizca ACIKCA izin verilen adreslere. Joker (*) kullanmiyoruz:
        anahtar basligi tasiyan istekte joker zaten gecersizdir ve
        herkese acik bir API dogru degildir.
        """
        origin = (self.headers.get("Origin") or "").strip()
        if not origin or not config.ORIGIN:
            return {}
        if origin not in config.ORIGIN:
            return {}
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Headers": "Content-Type, X-Pargusz-Anahtar",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Max-Age": "86400",
            "Vary": "Origin",
        }

    def _anahtar_gecerli(self):
        """Uzaktan erisim anahtari dogru mu?

        Anahtar ayarlanmamissa yalnizca AYNI bilgisayardan gelen
        istekler kabul edilir. Tunel adresi herkese acik oldugu icin
        bu ayrim onemlidir: anahtarsiz bir kurulumda internetten gelen
        istek /api/temizle cagirabilirdi.
        """
        if not config.ANAHTAR:
            adres = (self.client_address or ["?"])[0]
            return adres in ("127.0.0.1", "::1", "localhost")
        verilen = (self.headers.get("X-Pargusz-Anahtar") or "").strip()
        if not verilen:
            # Tarayicidan kolay denemek icin sorgu dizesi de kabul edilir
            try:
                q = urllib.parse.parse_qs(
                    urllib.parse.urlparse(self.path).query)
                verilen = (q.get("anahtar") or [""])[0].strip()
            except Exception:
                verilen = ""
        # Sabit surede karsilastirma
        import hmac
        return hmac.compare_digest(verilen, config.ANAHTAR)

    def do_OPTIONS(self):
        """CORS on kontrolu."""
        self._send(204, b"", ctype="text/plain")

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False))

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = 0
        if n <= 0:
            return {}
        raw = self.rfile.read(n)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    # ---------------------------------------------------------------- GET
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        # API uc noktalari uzaktan erisim denetiminden gecer. Statik
        # dosyalar (arayuz) serbesttir; zaten GitHub Pages'ten de
        # sunulabiliyor.
        if path.startswith("/api/") and not self._anahtar_gecerli():
            return self._json({"hata": "erisim reddedildi",
                               "ipucu": "X-Pargusz-Anahtar basligi gerekli"},
                              403)

        if path == "/api/durum":
            s = db.stats()
            s["calisiyor"] = learner.LEARNER.is_running()
            s["log"] = learner.LEARNER.recent_log(25)
            s["konu_sayisi"] = len(knowledge.TOPICS)
            s["formul_sayisi"] = len(formulas.FORMULAS)
            s["sabit_sayisi"] = len(units.CONSTANTS)
            # Ogrenerek kazanilan konu ve bosluk ozeti: arayuzdeki tek
            # satirlik durum bunlari gosteriyor.
            try:
                from . import sentez as _sentez
                s["ogrenilen_konu"] = _sentez.aciklanabilir_sayisi()
            except Exception:
                s["ogrenilen_konu"] = 0
            try:
                from . import bosluk as _bosluk
                s["bosluk"] = _bosluk.istatistik()
            except Exception:
                s["bosluk"] = {}
            from . import dil as _dil
            s["dil_modeli"] = _dil.MODEL.durum()
            return self._json(s)

        if path == "/api/gecmis":
            session = (qs.get("oturum") or ["default"])[0]
            rows = db.conn().execute(
                "SELECT role, content, ts FROM chat WHERE session=? "
                "ORDER BY id LIMIT 400", (session,)).fetchall()
            return self._json({"mesajlar": [dict(r) for r in rows]})

        if path == "/api/surum":
            return self._json({"surum": config.VERSION})

        if path == "/api/oturumlar":
            return self._json({"oturumlar": db.list_sessions(80)})

        if path == "/api/oneriler":
            return self._json({"oneriler": SUGGESTIONS})

        if path == "/api/konular":
            lang = (qs.get("dil") or ["tr"])[0]
            return self._json({
                "konular": [{"anahtar": k, "baslik": t}
                            for k, t in knowledge.list_topics(lang)],
                "formuller": [{"id": f["id"],
                               "ad": f["tr"] if lang == "tr" else f["en"],
                               "denklem": f["eq"], "konu": f["topic"]}
                              for f in formulas.FORMULAS],
            })

        # statik dosyalar
        return self._serve_static(path)

    def _serve_static(self, path):
        if path in ("/", ""):
            path = "/index.html"
        path = posixpath.normpath(urllib.parse.unquote(path)).lstrip("/")
        if path.startswith(".."):
            return self._send(403, "yasak", "text/plain; charset=utf-8")
        full = os.path.join(config.WEB_DIR, path)
        if not os.path.isfile(full):
            return self._send(404, "bulunamadi", "text/plain; charset=utf-8")
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript",):
            ctype += "; charset=utf-8"
        with open(full, "rb") as f:
            data = f.read()
        return self._send(200, data, ctype)

    # ------------------------------------------------------- dosya yukleme
    MAX_YUKLEME = 60 * 1024 * 1024      # 60 MB

    def _multipart_ayristir(self):
        """multipart/form-data govdesini coz. (alanlar, dosyalar) doner.

        Yalnizca standart kutuphane kullaniliyor; `cgi` modulu Python 3.13'te
        kaldirildigi icin bilerek tercih edilmedi.
        """
        ctype = self.headers.get("Content-Type", "")
        m = re.search(r'boundary="?([^";]+)"?', ctype)
        if not m:
            raise ValueError("boundary bulunamadi")
        sinir = ("--" + m.group(1)).encode("utf-8")
        try:
            n = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            n = 0
        if n <= 0:
            raise ValueError("bos govde")
        if n > self.MAX_YUKLEME:
            raise ValueError("dosya cok buyuk (en fazla %d MB)"
                             % (self.MAX_YUKLEME // (1024 * 1024)))
        govde = self.rfile.read(n)

        alanlar, dosyalar = {}, []
        for parca in govde.split(sinir):
            if parca in (b"", b"--", b"--\r\n", b"\r\n"):
                continue
            parca = parca.lstrip(b"\r\n")
            if parca.startswith(b"--"):
                continue
            bas, _, icerik = parca.partition(b"\r\n\r\n")
            if not _:
                continue
            icerik = icerik[:-2] if icerik.endswith(b"\r\n") else icerik
            basliklar = bas.decode("utf-8", "replace")
            ad_m = re.search(r'name="([^"]*)"', basliklar)
            dosya_m = re.search(r'filename="([^"]*)"', basliklar)
            if dosya_m and dosya_m.group(1):
                dosyalar.append((dosya_m.group(1), icerik))
            elif ad_m:
                alanlar[ad_m.group(1)] = icerik.decode("utf-8", "replace")
        return alanlar, dosyalar

    def _dosya_yukle(self):
        try:
            alanlar, dosyalar = self._multipart_ayristir()
        except ValueError as e:
            return self._json({"hata": str(e)}, 400)
        except Exception as e:
            return self._json({"hata": "yukleme cozulemedi: %s" % e}, 400)

        if not dosyalar:
            return self._json({"hata": "dosya bulunamadi"}, 400)

        oturum = alanlar.get("oturum") or "default"
        dil = alanlar.get("dil") if alanlar.get("dil") in ("tr", "en") else "tr"

        cevaplar = []
        for ad, veri in dosyalar[:5]:          # tek seferde en fazla 5 dosya
            if not veri:
                continue
            try:
                yol = belge.kaydet(ad, veri)
                r = brain.belge_isle(yol, ad, lang=dil, session=oturum)
                cevaplar.append(r.as_dict())
            except Exception as e:
                cevaplar.append({"text": "**%s** işlenemedi: %s" % (ad, e),
                                 "kind": "document"})
        return self._json({"sonuclar": cevaplar})

    # --------------------------------------------------------------- POST
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/") and not self._anahtar_gecerli():
            return self._json({"hata": "erisim reddedildi",
                               "ipucu": "X-Pargusz-Anahtar basligi gerekli"},
                              403)

        # Dosya yukleme govdeyi kendisi okur; burada _body() cagrilirsa
        # multipart verisi JSON sanilip tuketilir ve yukleme bos gorunur.
        if path == "/api/yukle":
            return self._dosya_yukle()

        data = self._body()

        if path == "/api/sohbet":
            msg = (data.get("mesaj") or "").strip()
            session = data.get("oturum") or "default"
            lang = data.get("dil") or None
            if lang not in ("tr", "en"):
                lang = None
            if not msg:
                return self._json({"hata": "bos mesaj"}, 400)
            resp = brain.respond(msg, session=session, lang_override=lang)
            return self._json(resp.as_dict())

        if path == "/api/ogrenme":
            action = data.get("islem")
            if action == "basla":
                started = learner.LEARNER.start()
                return self._json({"calisiyor": learner.LEARNER.is_running(),
                                   "baslatildi": started})
            if action == "dur":
                learner.LEARNER.stop()
                return self._json({"calisiyor": False})
            return self._json({"calisiyor": learner.LEARNER.is_running()})

        if path == "/api/oturum-sil":
            session = data.get("oturum")
            if not session:
                return self._json({"hata": "oturum belirtilmedi"}, 400)
            db.delete_session(session)
            brain._SESSION_MEM.pop(session, None)
            # Silme kuyruga alindi; listeden hemen dusurup donuyoruz ki
            # arayuz silinen sohbeti bir an daha gostermesin.
            kalan = [s for s in db.list_sessions(80) if s["id"] != session]
            return self._json({"ok": True, "oturumlar": kalan})

        if path == "/api/oturum-adlandir":
            session = data.get("oturum")
            baslik = (data.get("baslik") or "").strip()
            if not session or not baslik:
                return self._json({"hata": "eksik parametre"}, 400)
            db.rename_session(session, baslik)
            return self._json({"ok": True, "oturumlar": db.list_sessions(80)})

        # Geriye donuk uyumluluk: eski arayuz bu ucu "sohbeti sil" icin kullaniyordu
        if path == "/api/tum-sohbetleri-sil":
            # Yalnizca gorunen sohbet dokumu silinir; ogrenilen bilgi
            # (makaleler, kavramlar, bulgular, formuller) yerinde kalir.
            sayim = db.delete_all_sessions()
            brain._SESSION_MEM.clear()
            return self._json({"ok": True, "silinen": sayim,
                               "oturumlar": []})

        if path == "/api/temizle":
            session = data.get("oturum") or "default"
            db.delete_session(session)
            brain._SESSION_MEM.pop(session, None)
            return self._json({"ok": True})

        return self._json({"hata": "bilinmeyen uc nokta"}, 404)


SUGGESTIONS = {
    "tr": [
        {"baslik": "Formul coz", "metin": "m=2 kg v=10 m/s kinetik enerji"},
        {"baslik": "Konu anlat", "metin": "kuantum dolanikligi nedir"},
        {"baslik": "Turev al", "metin": "x^2*sin(x) turevi"},
        {"baslik": "Birim cevir", "metin": "90 km/h kac m/s"},
        {"baslik": "MATLAB kodu", "metin": "sonumlu osilator icin matlab kodu"},
        {"baslik": "Makale bul", "metin": "kara delik hakkinda makale bul"},
        {"baslik": "Ornek problem", "metin": "termodinamik ornek ver"},
        {"baslik": "Sabit sor", "metin": "planck sabiti nedir"},
    ],
    "en": [
        {"baslik": "Solve formula", "metin": "m=2 kg v=10 m/s kinetic energy"},
        {"baslik": "Explain topic", "metin": "what is quantum entanglement"},
        {"baslik": "Differentiate", "metin": "derivative of x^2*sin(x)"},
        {"baslik": "Convert units", "metin": "90 km/h to m/s"},
        {"baslik": "MATLAB code", "metin": "matlab code for damped oscillator"},
        {"baslik": "Find papers", "metin": "find papers on black holes"},
        {"baslik": "Example problem", "metin": "give a thermodynamics example"},
        {"baslik": "Constant", "metin": "what is the planck constant"},
    ],
}


def _bizim_sunucu_mu(host, port, zaman_asimi=1.5):
    """Portu tutan sey bizim sunucumuz mu?"""
    import json
    import urllib.request
    try:
        with urllib.request.urlopen(
                "http://%s:%d/api/surum" % (host, port),
                timeout=zaman_asimi) as r:
            return "surum" in json.loads(r.read().decode("utf-8"))
    except Exception:
        return False


def _tarayici_ac(url):
    import threading
    import webbrowser

    def _ac():
        try:
            webbrowser.open(url)
        except Exception:
            pass
    threading.Thread(target=_ac, daemon=True).start()


def serve(host=None, port=None, open_browser=True, start_learning=True):
    db.init()
    host = host or config.HOST
    port = port or config.PORT

    # Port dolu olabilir: ya ParguszPhysics zaten aciktir (o zaman yenisini
    # baslatmaya gerek yok, tarayiciyi ona yonlendiririz) ya da baska bir
    # program tutuyordur (o zaman bir sonraki bos porta geceriz). Onceden
    # bu durumda program cokuyordu.
    httpd = None
    ilk_port = port
    for deneme in range(12):
        try:
            httpd = ThreadingHTTPServer((host, port), Handler)
            break
        except OSError as e:
            if e.errno not in (48, 98):        # yalnizca "adres kullanimda"
                raise
            if deneme == 0 and _bizim_sunucu_mu(host, port):
                url = "http://%s:%d/" % (host, port)
                print("")
                print("  ParguszPhysics zaten calisiyor: %s" % url)
                print("  Tarayicida acmak icin bu adrese gidin.")
                print("")
                if open_browser:
                    _tarayici_ac(url)
                return 0
            port += 1
    if httpd is None:
        print("  %d-%d araligindaki portlarin hepsi dolu." % (ilk_port, port))
        return 1
    if port != ilk_port:
        print("  Not: %d portu doluydu, %d kullaniliyor." % (ilk_port, port))
    httpd.daemon_threads = True

    if start_learning:
        learner.LEARNER.start()

    url = "http://%s:%d/" % (host, port)
    print("")
    print("  ╔═══════════════════════════════════════════════════════╗")
    print("  ║              P A R G U S Z P H Y S I C S              ║")
    print("  ║        Fizik · Hesaplama · MATLAB · Literatur         ║")
    print("  ╚═══════════════════════════════════════════════════════╝")
    print("")
    print("   Arayuz : %s" % url)
    print("   Veri   : %s" % config.DB_PATH)
    print("   Kayit  : %s" % config.LOG_PATH)
    print("")
    print("   Ogrenme motoru arka planda calisiyor.")
    print("   Bilgisayari acik biraktiginiz surece ogrenmeye devam eder.")
    print("   Durdurmak icin: Ctrl+C")
    print("")

    if open_browser:
        def _open():
            import webbrowser
            import time
            time.sleep(1.2)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        threading.Thread(target=_open, daemon=True).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Kapatiliyor...")
        learner.LEARNER.stop()
        httpd.shutdown()
        print("  Gorusmek uzere.\n")
