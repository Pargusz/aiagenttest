# ParguszPhysics

Fizik, MATLAB, kimya ve biyoloji için çalışan bir asistan. Konu anlatır,
çok adımlı problem çözer, formül türetir, MATLAB kodu yazar ve okuduğu
yayınlardan kendini geliştirir.

- **99 çekirdek konu**, **277 doğrulanmış formül**, **29 MATLAB şablonu**
- Çok adımlı ödev problemlerini zincirleyerek çözer (SymPy ile, her adım
  fiziksel olarak denetlenir)
- Türkçe ve İngilizce
- 375 otomatik test

## Nasıl çalışır: iki parça

Bu proje ikiye ayrılmıştır, çünkü **hesaplamayı yapan motor bir Python
sunucusudur** ve GitHub Pages yalnızca statik dosya sunabilir.

| Parça | Nerede çalışır | İçerik |
|---|---|---|
| **Ön yüz** (arayüz) | GitHub Pages | `docs/` — HTML, CSS, JS |
| **Motor** (beyin) | Sizin bilgisayarınız | `core/`, `run.py` + veritabanı |

Veritabanı (öğrendiği 30.000+ yayın, kavramlar, bağlantılar) **sizin
bilgisayarınızda kalır**; GitHub'a gitmez. Hem 100 MB dosya sınırını
aşar hem de sürekli değişir.

---

## Kurulum

### 1. Ön yüzü yayına alın (bir kez)

Bu depoyu GitHub'a gönderdikten sonra:

**Settings → Pages → Source: Deploy from a branch → Branch: `main` /
`docs`** seçin ve kaydedin.

Birkaç dakika içinde arayüz şurada olur:

```
https://pargusz.github.io/aiagenttest/
```

### 2. Motoru kendi bilgisayarınızda çalıştırın

Tünel aracını bir kereye mahsus kurun:

```bash
brew install cloudflared
```

Sonra `ParguszPhysics Sunucu (uzaktan erisim).command` dosyasına çift
tıklayın. Pencere şunları yazar:

```
    1. Sayfa   : https://pargusz.github.io/aiagenttest/
    2. Sunucu  : https://xxxx-yyyy.trycloudflare.com
    3. Anahtar : Kx8vQ2mR...
```

**Pencereyi açık bırakın.** Kapanırsa erişim de kapanır.

### 3. Bağlanın

Arkadaşınız sayfayı telefondan veya bilgisayardan açar; bir kez sunucu
adresini ve anahtarı girer. Tarayıcı bunları hatırlar.

Ayarı sonradan değiştirmek için sayfa adresinin sonuna `#baglanti`
ekleyin.

---

## Güvenlik

Tünel adresi internete açıktır, bu yüzden **erişim anahtarı zorunludur**.
Anahtar ilk çalıştırmada üretilir ve `data/erisim_anahtari.txt` içinde
saklanır (bu dosya GitHub'a gitmez).

- Anahtarsız istek `403` alır.
- Yalnızca `PARGUSZ_ORIGIN` içinde yazılı adresten gelen tarayıcı
  isteklerine izin verilir.
- Anahtar ayarlanmamışsa sunucu yalnızca kendi bilgisayarınızdan
  erişilebilir olur — kazayla internete açılmaz.

Anahtarı değiştirmek isterseniz `data/erisim_anahtari.txt` dosyasını
silin; bir sonraki açılışta yenisi üretilir.

---

## Yerel kullanım (tünelsiz)

Kendi bilgisayarınızda kullanmak için `ParguszPhysics Baslat.command`
yeterlidir. Hiçbir ayar gerekmez, arayüz `http://127.0.0.1:8777`
adresinde açılır.

---

## Ortam değişkenleri

| Değişken | Varsayılan | Ne işe yarar |
|---|---|---|
| `PARGUSZ_HOST` | `127.0.0.1` | Dinlenecek adres. Tünel kullanıyorsanız değiştirmeyin. |
| `PARGUSZ_PORT` | `8777` | Port |
| `PARGUSZ_ANAHTAR` | yok | Uzaktan erişim anahtarı |
| `PARGUSZ_ORIGIN` | yok | İzin verilen ön yüz adresi |
| `PARGUSZ_VERI` | `./data` | Veritabanı dizini |
| `PARGUSZ_DIL` | açık | `0` verilirse dil modeli yüklenmez (daha hızlı, daha az bellek) |

---

## Gereksinimler

- Python 3.9+
- `sympy`
- İsteğe bağlı: `llama-cpp-python` ve bir GGUF model (`data/model/`).
  Model olmadan da her şey çalışır; yalnızca serbest sohbet dili
  sadeleşir.

```bash
pip3 install sympy
```

## Testler

```bash
python3 -c "import sys; sys.path.insert(0,'.'); from core import db, formulas, genisleme, selftest; db.init(); formulas.ogrenilenleri_bagla(); genisleme.formulleri_bagla(); selftest.run()"
```
