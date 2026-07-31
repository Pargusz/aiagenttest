# ParguszPhysics

Fizik hesaplamaları, konu anlatımı, formül çözümü, MATLAB kod üretimi ve canlı
literatür taraması yapan yerel bir asistan. Tamamen kendi bilgisayarınızda
çalışır; hiçbir yapay zekâ servisine bağlanmaz, hiçbir API anahtarı istemez.

---

## Çalıştırma

Klasördeki **`ParguszPhysics Baslat.command`** dosyasına çift tıklayın.
Tarayıcı kendiliğinden açılır. Ya da terminalden:

```bash
python3 run.py
```

İlk açılışta macOS "geliştirici doğrulanamadı" derse: dosyaya sağ tıklayıp
**Aç**'ı seçin (bir kez yeterli).

### Diğer çalıştırma biçimleri

```bash
python3 run.py --sadece-ogren
```
Arayüz açmadan yalnızca öğrenir. Bilgisayarı günlerce açık bırakacaksanız bu kip
en verimlisidir.

```bash
python3 run.py --sor "kinetik enerji formulu"
```
Terminalden tek soru sorar.

```bash
python3 run.py --ogrenme-yok
```
Öğrenme motoru kapalı başlatır (internet kullanmaz).

```bash
python3 run.py --test
```
254 testlik kendi kendini denetleme paketini çalıştırır.

`--port 9000` ile farklı bir port, `--tarayici-yok` ile otomatik tarayıcı açmayı
kapatabilirsiniz.

Durdurmak için terminalde **Ctrl+C**.

---

## Ne yapabilir

### Hesaplama
| Yazın | Yapar |
|---|---|
| `2*pi*sqrt(0.5/200)` | sayısal ve sembolik hesap |
| `x^3 - 2x = 5 coz` | denklem çözer |
| `sin(x)*exp(x) turevi` | türev alır |
| `x^2 integrali 0 dan 3 e` | belirli/belirsiz integral |
| `sin(x)/x limiti x->0` | limit |
| `y'' + 4y = 0 diferansiyel denklem` | ODE çözer |
| `[[1,2],[3,4]] ozdegerleri` | determinant, ters, özdeğer, rank |
| `diverjans [x*y, y*z, z*x]` | grad / div / curl / laplasyen |
| `exp(x) taylor serisi` | seri açılımı |

### Fizik
| Yazın | Yapar |
|---|---|
| `kinetik enerji formulu` | formülü ve tüm değişkenlerini gösterir |
| `m=2 kg v=10 m/s kinetik enerji` | **100 J** hesaplar |
| `Ek=100 J m=2 kg kinetik enerji` | tersine çözer, **v = 10 m/s** verir |
| `Tc=300 K Th=500 K carnot verimi` | bilinmeyeni bulur |
| `90 km/h kac m/s` | boyut denetimli birim çevirir |
| `isik hizi nedir` | fiziksel sabitleri verir |

Formüller **her değişken için** çözülebilir; hangi değeri verirseniz kalanı
bulur. Sabitler (`g`, `c`, `h`, `kB`, `G` …) otomatik yerine konur. Verdiğiniz
birimin boyutu formülle uyuşmuyorsa uyarır.

### Konu anlatımı
`kuantum dolanikligi nedir`, `termodinamigin ikinci yasasini anlat`,
`entropi ornek ver`

27 konu için ayrıntılı anlatım, temel bağıntılar ve çözümlü örnekler hazır
bulunur; üzerine internetten öğrendiği tanımlar ve güncel makale özetleri eklenir.

### MATLAB / Octave
`egik atis icin matlab kodu`, `fft analizi kodu yaz`, `kuantum kuyusu simulasyonu`

25 hazır şablon:

- **Mekanik / simülasyon:** eğik atış, sönümlü osilatör, sarkaç, gezegen
  yörüngesi (simplektik), N-cisim hareket denklemi, hareket animasyonu
- **Sayısal yöntemler:** ısı denklemi, dalga denklemi, Laplace denklemi,
  sayısal türev-integral-interpolasyon, optimizasyon ve kök bulma,
  lineer denklem sistemi ve özdeğerler, genel ODE sistemi (durum uzayı)
- **Fizik alanları:** kuantum kuyusu, RLC devresi, alan görselleştirme,
  termodinamik çevrim (P-V diyagramı), ışın izleme (mercek ve prizma)
- **Veri ve analiz:** FFT, eğri uydurma, Monte Carlo, ölçüm dosyası okuma ve
  temizleme, hata yayılımı, sembolik hesap, transfer fonksiyonu ve sistem yanıtı

Ayrıca herhangi bir formül veya ifade için de kod üretir. Şablonların tamamı
her test koşusunda sözdizimi denetiminden geçirilir (parantez, blok ve `end`
dengesi).

Kodlar MATLAB ve ücretsiz **GNU Octave** ile uyumludur. İngilizce konuşurken
yorumlar da İngilizce üretilir.

### Literatür
`superiletkenlik hakkinda makale bul`, `find papers on dark matter`

Önce öğrendiği veritabanında arar; yeterli sonuç yoksa o an internetten çeker
(ve öğrenir). Bulduklarından ortak bir bulgu özeti çıkarır.

### Yol haritası
`matlab ogrenmek istiyorum nereden baslamaliyim`, `fizik yol haritasi`,
`bana ne ogretebilirsin`

Üç aşamalı plan hazır: **MATLAB/Octave**, **fizik** ve **sayısal fizik**. Her
aşamada ne öğrenileceği, *neden* öğrenileceği, bir alıştırma ve bota
yazabileceğiniz bir deneme komutu var. Tek bir aşamayı açmak için
`4. asamayi anlat` yazın.

### Dosya ve belge yükleme
Ataç düğmesine basın, sürükleyip bırakın ya da panodan yapıştırın.

| Tür | Ne yapar |
|---|---|
| **PDF** | Metni çıkarır, bölümleri, özeti, formülleri ve sayısal değerleri bulur |
| **TXT / MD / TEX / CSV** | Aynı çözümlemeyi uygular |
| **.m / .py / kod** | Metin olarak okur ve indeksler |
| **Resim** | Saklar ve gösterir — *içindeki yazıyı okuyamaz* |

Her belge çözümlendikten sonra **kalıcı belleğe eklenir**: sonradan aranabilir,
üzerine soru sorulabilir. Tek seferde en fazla 5 dosya, dosya başına 60 MB.

> **Resimler için dürüst sınır:** bu bilgisayarda OCR (görüntüden yazı tanıma)
> motoru kurulu değil. Resmi kaydeder ve gösteririm ama içindeki metni
> okuyamam. Grafiği yazıyla anlatırsanız üzerinde hesap yapabilirim.

### Anlama katmanı
Mesajınız dört aşamadan geçer: **yazım düzeltme** (`entrpi` → `entropi`),
**eş anlam** (`izafiyet` → `görelilik`, `ısı sığası` → `özgül ısı`),
**soru tipi** ve **varlık çıkarımı**. Düzeltme yaptıysa size söyler.

Soru tipine göre cevap şekli değişir:

| Yazınca | Ne alırsınız |
|---|---|
| `entropi nedir` | tanım + bağıntılar + örnek |
| `entropi neden artar` | nedensel cümleler + kurulan ilişkiler |
| `carnot verimi nasıl hesaplanır` | adım adım yöntem |
| `entropi ile entalpi arasındaki fark` | yan yana karşılaştırma |

Sık kullanılan Türkçe kelimeler (`misin`, `peki`, `biraz`) düzeltmeden korunur;
aksi hâlde fizik terimlerine çevrilip cümleyi bozuyorlardı.

### Dil modeli
Sistemde yerel bir dil modeli çalışır: **Qwen3-8B (Q4, 5,0 GB)**,
llama.cpp üzerinden Apple Silicon GPU'da. Tamamen bu bilgisayarda: API yok,
anahtar yok, internete hiçbir şey gitmez.

**Kritik tasarım kararı — model dil içindir, fizik için değil.** Bir dil
modeli akıcı cümle kurar ama sayı uydurabilir. Bu yüzden:

- Hesap içeren sorularda (`hesap`, `birim`, `formül`, `türev`, `matlab`…)
  model **hiç devreye girmez**; cevap doğrudan SymPy'den gelir.
- Serbest sorularda modele **yalnızca doğrulanmış bağlam** verilir: çekirdek
  konu anlatımları, doğrulanmış formüller, okunmuş makalelerden çıkarılan
  bulgular ve kaynaklar. Bağlam boşsa model çağrılmaz.
- Sistem yönergesi modele "bağlam dışında fizik uydurma, sayıları aynen
  koru, bilmiyorsan bilmediğini söyle" der.

Sınandı: bağlamdaki `100 J` değerini aynen korudu, uydurma bir parçacık
sorulduğunda "bu konuda elimde bilgi yok" dedi.

### Dil modeli ile formül tabanı nasıl uyum içinde çalışır
Kullanıcı formülün adını bilmez. "Bragg yasası" demez, *"kristalde x ışını
hangi açıda yansır"* der. Bu iki dünyayı çakıştırmadan birleştiren üç katman
var:

1. **Günlük dil sözlüğü** (`core/sozluk.py`) — 190 formülün her biri için
   insanların gerçekten kullandığı ifadeler yazılıdır: *"kondansatörün dolması
   ne kadar sürer"* → `rc_zaman`, *"tahta parçası suda neden yüzüyor"* →
   `arsimet`. Türkçe çekim ekleri yüzünden ifade cümleye birebir oturmadığında
   kısmi eşleşme devreye girer (*"havada ne kadar kalır"* ≈ *"havada ne kadar
   kaldığını"*).
2. **Dil modeli terim çevirisi** — sözlük tutmazsa model soruyu *seçmez*,
   yalnızca fizik terimlerine **çevirir** (*"kondansatörün dolması"* →
   "kapasite, direnç, zaman sabiti"). Terimler yine deterministik arama ile
   formüle bağlanır. Böylece anlama işi modelde, doğruluk işi doğrulanmış
   tabanda kalır; ikisi birbirinin alanına girmez.
3. **Kalıcı öğrenme** — model sayesinde bir soru doğru formüle bağlandığında o
   ifade sözlüğe **kalıcı olarak** yazılır; bir dahaki sefere hiçbir modele
   gerek kalmadan, milisaniyeler içinde bulunur. Ekleme yapılmadan önce ifadenin
   gerçekten hedef formüle götürdüğü sınanır ve genel ölçüm tekrar ölçülür;
   ölçüm düşerse ekleme geri alınır. Öğrenme sistemi ancak iyileştirebilir,
   bozamaz.

**Dördüncü katman — fiziksel anlam.** Formül tabanı denklemi biliyordu ama
denklemin *ne anlama geldiğini* bilmiyordu; model bu boşluğu kendi dolduruyor
ve hata yapabiliyordu. Ölçülen örnek: adyabatik sıkıştırmayı anlatırken
"sistemin iç enerjisi değişmez" dedi — oysa Q = 0 olduğu için iç enerji tam da
yapılan iş kadar **değişir** (dU = −W). Artık 61 formülün her biri elle
yazılmış, doğrulanmış bir *fiziksel anlam* notu taşıyor ve bu not modele
bağlamla birlikte veriliyor. Aynı soru tekrar sorulduğunda cevap doğru çıktı.
Notlar `core/notlar.py` içinde ayrı durur ve genişletilebilir.

Bu zincirin ne kadar işlediği ölçülür: gündelik dille sorulmuş 40 soruluk bir
sınama kümesi her test koşusunda çalışır. Sözlük eklenmeden önce **%20**'si
doğru formüle gidiyordu, şimdi **%98**'i gidiyor; ölçüm %90'ın altına düşerse
test paketi hata verir. Arama, 1600 anahtar kelimeye rağmen ön hesaplanmış
indeks sayesinde sorgu başına **1,4 ms** sürer (indeksleme öncesi 128 ms idi).

Yanıt süresi ~15-25 saniye (M4, GPU). Modeli kapatmak için:

```bash
PARGUSZ_DIL=0 python3 run.py
```

Birden fazla model dosyası varsa tercih sırası `qwen3 > qwen2.5-14b >
qwen2.5-7b`. Belirli birini seçmek için:

```bash
PARGUSZ_MODEL=Qwen2.5-7B python3 run.py
```

Qwen3'ün "düşünme kipi" kapatılır: model bizim mimarimizde akıl yürütmüyor,
yalnızca doğrulanmış bağlamı anlatıyor; düşünme adımı yanıtı 2-3 kat
yavaşlatırdı. Yine de bir `<think>` bloğu gelirse temizlenir.

Bu durumda sistem tamamen kural tabanlı çalışır — hiçbir özellik kaybolmaz,
yalnızca serbest sohbet yeteneği gider.

### Makale kalite kapısı
Her makale belleğe girmeden önce denetlenir. Amaç stoklamak değil, yalnızca
işe yarayanı almak.

**Nasıl karar veriliyor —** kaynağın kendi sınıflandırmasına güvenilir:

| Kaynak | Ölçüt |
|---|---|
| arXiv | Kategorinin fizik olması (`quant-ph`, `gr-qc`, `cond-mat`…) |
| OpenAlex | `primary_topic.field` = Physics/Materials + geri çekilmemiş |
| DOAJ | Hakemli açık erişim + fizik içeriği |
| DergiPark | Fizik içeriği doğrulaması + yasaklı konu izi yok |

Anahtar kelimeyle "bu fizik mi" diye bakmak yanıltıcıydı: denetimde
`Cosmological billiards` ve `Virasoro yörüngeleri` gibi **gerçek kuramsal
fizik** makaleleri yanlışlıkla eleniyordu. Artık kesin göstergeler (virasoro,
Yang-Mills, instanton…) tek başına yeterli sayılıyor; zayıf olanlar (enerji,
sistem) iki tanesi gerekiyor.

**Reddedilenler:** geri çekilmiş makaleler (asla alınmaz), özeti 120
karakterden kısa olanlar, felsefe/eğitim/iktisat/sosyal bilim metinleri.

**Kalite puanı (0-100):** atıf sayısı (logaritmik), hakemlilik, alan kesinliği,
özet zenginliği, dergi bilgisi ve yayın yılından hesaplanır. Arama sıralaması
bu puanı hesaba katar — aynı konuda iki kaynak varsa daha sağlamı öne çıkar.
Kaynak listesinde her makalenin yanında **hakemli/önbaskı** ve **atıf sayısı**
görünür.

`durum` raporu şunu gösterir: kaç makalenin **bilgiye dönüştüğü** (%),
hakemli/önbaskı dağılımı, ortalama kalite ve kalite kapısında kaç makalenin
reddedildiği.

### Öğrendikçe gerçekten büyüyen şeyler
Makale sayısının artması tek başına yetenek artışı değildir. Şunlar yeni
makale geldikçe **gerçekten** büyür ve `durum` raporunda sayı olarak görünür:

| Ne | Nasıl büyür |
|---|---|
| **Açıklayabildiği konu** | Bir kavram yeterli bulgu + bağlantı biriktirince ona çekirdek konular gibi yapılandırılmış bir sayfa üretilir |
| **Öğrenilen bağıntı** | Özetlerden çıkarılan denklemler ayıklanır, SymPy ile doğrulanır, cevaplarda gösterilir |
| **Bulgu** | Her özet cümle cümle sınıflandırılır ve kavrama bağlanır |
| **İlişki** | "A, B'ye yol açar" kalıbından kavram bağları kurulur |

Çekirdek (27 konu, 190 formül, 36 sabit) elle yazılmıştır ve sabittir; üstüne
binen bu katman öğrenmeyle büyür. Bir cevap öğrenilenlerden derlendiyse bunu
size söyler.

### Bilmediğini o anda araştırır ve kaynak gösterir
Doğrulanmış bilgisi olmayan bir soru geldiğinde artık beklemez: **soru
sorulduğu anda** internete çıkar (Wikipedia → arXiv → Crossref, ~6-8 saniye),
bulduğu malzemeden cevabı üretir ve **cevabın altına kaynakçayı ekler**.
Bulduklarını tabana yazar, aynı soru bir daha internete çıkmaz.

Kullanıcının yazdığı terim kaynaklardakinden farklıysa dil modeli çevirir:
*"Kazimir etkisi"* → `Casimir effect`. Sonuç doğrudan kullanılmaz — gerçek bir
Wikipedia fizik maddesine karşılık geliyorsa kabul edilir; "Kazimir Maleviç"
(ressam) gibi sonuçlar fizik süzgecinde elenir.

Kaynakça yalnızca canlı araştırmada değil, **korpustan beslenen her cevapta**
görünür. Cevabın kullanıcının dilinde olmayan ham alıntı yığını olması da
zayıflık sayılır ve model bunu Türkçe'de toparlar.

### Adım adım türetme
Bir sonucu söylemek ile nasıl varıldığını göstermek ayrı şeylerdir.
`core/turetim.py` üç tür türetim yapar ve **her adımı SymPy ile** hesaplar —
hiçbir ara sonuç uydurulmaz:

1. **Cebirsel çözüm** — formülü istenen değişkene göre adım adım çöz.
   Hangi işlemin neden yapıldığı yazılır (paydayı temizle, kök al…),
   sonuç geri yerine konarak doğrulanır, boyut denetimi eklenir.
2. **Formül birleştirme** — iki bağıntıdan ortak değişken elenerek üçüncüsü
   türetilir; her adım gösterilir.
3. **Doğrulama** — sonuç özgün denklemi sağlıyor mu, boyutlar tutuyor mu.

`kinetik enerjiden hızı adım adım türet` yazın. Fiziksel büyüklüklerde
pozitif kök seçilir (SymPy sırayı garanti etmiyor ve `-√(2E/m)`
dönebiliyordu).

### Çekirdek bilgi: lisans → lisansüstü
Ölçüldü: sistem *"Noether teoremini türet"* sorusuna **"bu konuda elimde
bilgi yok"** diyordu. Sebebi yapısaldı — 28.000 kaynak *bağlam* katıyor ama
**çekirdeği büyütmüyordu**. Çekirdek üç katmanda genişletildi:

| Katman | Konular |
|---|---|
| **Analitik mekanik** | En küçük etki ilkesi · Lagrange · Hamilton · **Noether** · Simetriler ve korunum · Alan kuramı · İstatistiksel topluluklar |
| **Kilit deneyler** | **Stern-Gerlach** · Çift yarık · Michelson-Morley · Fotoelektrik · Millikan · Rutherford · **Bell testleri** · LIGO · CMB · **Higgs keşfi** |
| **Lisansüstü** | **Maxwell denklemleri** · Kuantum formalizmi · Pertürbasyon kuramı · **Bant kuramı** · **Standart Model** · Matematiksel yöntemler · Ölçüm ve belirsizlik |

Çekirdek **27 → 51 konu**, formül **190 → 195**. Deneyler *"ne soruldu →
ne bekleniyordu → ne çıktı → ne değiştirdi"* yapısında yazıldı; bu, "bunu
deneysel olarak nasıl biliyoruz" sorusunun cevabıdır.

Ölçüm kümesi de dürüstlük için **40'tan 71 soruya** çıkarıldı (ileri kuram,
deneyler ve lisansüstü konular dahil). Sonuç: **71/71**. İlk ölçümde bu
küme %79'du.

### Profesör gibi anlatım
Bir şeyi "anlatmak" ile "tanımını söylemek" aynı şey değildir. Konu
sorularında cevap şu yapıda kurulur:

1. **Tanım** — çekirdek konu anlatımından ya da formülün fiziksel anlam notundan
2. **Hangi bağıntıyla çalışırız** — doğrulanmış formül + değişkenleri + notu
3. **Çözümlü örnek** — sayılar SymPy ile hesaplanır, uydurulmaz
4. **Kitaptan örnek** — çekirdek konunun kendi çözümlü örneği
5. **Sık yapılan hata** — öğrencinin tam da orada yanıldığı yer
6. **Buradan nasıl devam edersiniz** — çalışan komutlar

Başlık ile tanım **aynı kaynaktan** gelir; aksi hâlde "Entropi değişimi"
başlığı altında sıfırıncı yasa anlatılıyordu.

### Konuşarak öğrenme
En değerli öğrenme sinyali kullanıcının sorusudur: cevaplayamadığı her soru,
tam olarak neyi öğrenmesi gerektiğini söyler. Döngü:

1. Her soruda cevabın güçlü mü zayıf mı olduğu kaydedilir.
2. Zayıf kalanlar **bilgi boşluğu** olur; aynı şey tekrar sorulursa önceliği
   artar. (Selamlaşma, teşekkür gibi sohbet mesajları boşluk sayılmaz.)
3. Öğrenme motoru boşlukları **hedefli** araştırır: Wikipedia + arXiv +
   ders kitabı. Kullanıcının yazdığı terim kaynaklardakinden farklıysa dil
   modeli çevirir — ölçülen örnek: *"Kazimir etkisi"* → `Casimir effect`.
   Bulunan doğru terim **kalıcı takma ad** olarak saklanır, böylece aynı
   yazımla tekrar sorulduğunda erişim doğru malzemeye gider.
4. `öğrendiklerim` yazarak ne öğrendiğini görebilirsiniz.

**Bilmediğinde uydurmaz.** Bu, ölçülerek bulunan gerçek bir hatanın
düzeltilmesidir: Casimir etkisi sorulduğunda model doğrulanmış bilgi
olmadığı hâlde *"iki plaka arasındaki elektriksel potansiyel farkı"* diye
yanlış bir açıklama üretmişti (doğrusu kuantum vakum dalgalanmalarıdır).
Sebep, kural tabanlı cevabın modele bağlam diye verilmesiydi; model onu alıp
kendi belleğinden süslüyordu. Artık **gerçek malzeme ayrı denetleniyor**:
soruyla örtüşen doğrulanmış kaynak yoksa model hiç çağrılmaz, bunun yerine
"doğrulanmış bilgim yok, araştırma sırama aldım" denir. Araştırma bittikten
sonra aynı soru sorulduğunda cevap doğru geliyor.

### Makaleleri birleştirerek yeni bilgi üretme
Tek bir makalenin söylediği şey bir **iddiadır**; birden çok makalenin aynı
şeyi söylemesi **bilgidir**. Öğrenme motoru günde iki kez şunları türetir:

- **Uzlaşma** — aynı kavram hakkında farklı makalelerde tekrarlanan ifadeler
  bir araya getirilir. Kaç bağımsız kaynağın söylediği sayılır ve cevapta
  gösterilir: *"(4 bağımsız makale)"*.
- **Kavram köprüsü** — çok sayıda makalede birlikte geçen ama aralarında
  adlandırılmış ilişki bulunmayan kavramlar bağlanır.

**Kalite kapısı:** bir türetim ancak **en az iki farklı makaleden** destek
alıyorsa kaydedilir. Tek kaynaklı iddia bilgi sayılmaz — bu kural teste
bağlıdır.

### Bulgu çıkarımının genişletilmesi
Ölçüm: 17.700 makalenin **%41'i hiç bulgu üretmemişti** ve 19.199 bulgunun
yalnızca 265'i tanımdı. Sebep, cümle sınıflandırma kalıplarının dar olmasıydı;
"We analyze…", "X is the energy of…", "The law states that…" gibi çok yaygın
biçimler hiçbir kalıba uymuyordu. Kalıplar genişletildi (özellikle **tanım** ve
**yasa** biçimleri) ve korpusun tamamı yeniden işlendi. Ölçüm: daha önce boş
kalan makalelerin **%47'si** artık bulgu üretiyor.

### Kaynaklar
Makale özetleri bir araştırma sonucunu anlatır; **konuyu öğretmez**. Öğretmen
olmak için asıl malzeme ders kitabıdır. Kaynaklar:

| Kaynak | Ne verir |
|---|---|
| **OpenStax** | 7 açık lisanslı fizik/astronomi ders kitabı, **bölüm bölüm tam metin** — öğrenme hedefleri, kavram anlatımı, çözümlü örnekler. Makale özeti bir sonucu bildirir; ders kitabı konuyu öğretir. |
| **Üniversite depoları** | **Zenodo** (CERN), **OpenAIRE** (Avrupa üniversite depolarının toplayıcısı), **HAL** (Fransız üniversiteleri), **OAPEN** (açık erişimli akademik kitaplar). Hepsi açık API sunar, anahtar istemez. |
| arXiv · OpenAlex · DOAJ · DergiPark | güncel araştırma |
| Wikipedia (TR/EN) | kavram tanımları |
| Yüklenen PDF | sizin verdiğiniz belgeler |

**CORE ve DOAB denendi, alınmadı:** CORE API anahtarı istiyor, DOAB zaman
aşımına uğruyor. Çalışmayan kaynağı eklemektense çalışanlarla ilerlendi.

### Türkçe sorgu — İngilizce korpus köprüsü
Korpusun yaklaşık %80'i İngilizce. Ölçüldü: Türkçe sorulan 10 sorudan yalnızca
2'si bulgulara ulaşabiliyordu — veri vardı ama Türkçe kullanıcı ona
erişemiyordu. Köprü için yeni sözlük yazmaya gerek yoktu: **formül tabanı her
formülün ve her değişkenin adını zaten iki dilde taşıyor** (1.005 terim
çifti), üstüne formülde karşılığı olmayan 55 kavram eklendi. Şimdi **10/10**.

Yol boyunca üç ayrı yerde takıldı ve üçü de ölçülerek bulundu: aday toplama
döngüsü ilk (Türkçe) kelimede kotayı doldurup İngilizce terimlere hiç sıra
bırakmıyordu; öbek denetimi "kuantum dolanıklığı quantum" gibi imkânsız bir
dizi arıyordu; son ilgi süzgeci yalnız Türkçe kelimeye bakıp hepsini eliyordu.

### Sahipsiz bulguların bağlanması
Ölçüldü: 50.000 bulgunun yalnızca **%36,8'i** bir kavrama bağlıydı; kalanı
sadece tam metin aramasıyla bulunabiliyor, konu sayfalarında hiç
görünmüyordu — yani veri vardı ama **kullanılmıyordu**. 31.734 sahipsiz bulgu
tarandı, 10.437'si kavramlara bağlandı: **%57,7**.

**YouTube denendi ve olmadı.** Video sayfasından altyazı listesi alınabiliyor
(26 dil görünüyor) ama altyazı içeriğini veren uç (`timedtext`) oturum
belirteci olmadan boş dönüyor — denenen dört biçimin dördü de 0 bayt verdi.
Sessizce hiç çalışmayacak bir kaynak eklemektense bunu söylemeyi tercih
ettim; yerine ders kitapları eklendi.

### Kendi kendini genişletme
Sistem yalnızca makale biriktirmez; biriktirdikçe **yapabildikleri de artar**.
Öğrenme motoru günde bir kez `genisleme` görevini çalıştırır:

**Yol haritaları — makalelerden.** Yeterli makale biriken her fizik alt alanı
için yol haritası üretilir. Ön koşullar ve çekirdek kavramlar alanın standart
müfredatındandır (bunlar korpustan çıkarılamaz, çıkarılsa güvenilir olmaz);
**4. aşama doğrudan korpustan gelir**: o alanın makale başlıklarında en çok
geçen konu ifadeleri. Yeni makaleler geldikçe bu aşama kendiliğinden
güncellenir ve yeni alan eşiği geçtiğinde yeni bir harita açılır.
3 elle yazılmış harita vardı; şu an **17 harita** var, 14'ü üretilmiş.

**Formüller — doğrulanmış çekirdekten türetilerek.** Önce makale metninden
formül çıkarmak denendi ve ölçüldü: 4.000 özette bulunan 279 "eşitliğin"
neredeyse tamamı `q=5/3` gibi parçalardı — bunları formüle çevirmek daha önce
temizlenen çöp birikimini geri getirirdi. Bunun yerine ortak değişkeni olan
iki doğrulanmış formül birleştirilir: `Ek = ½mv²` ile `v² = v₀² + 2a·Δx`
birleşince kuvvet doğrudan hız ve yoldan hesaplanabilir hâle gelir. Üretilen
her bağıntı üç kapıdan geçmek zorundadır:

1. **Konu uyumu** — yalnızca komşu alanlar birleştirilir. Kalorimetre
   formülünden çekilen kütleyi Newton yasasına koymak boyutça doğru ama fizik
   değildir (`F = Q·a/(c·ΔT)`); bu tür bileşimler reddedilir.
2. **Boyut denetimi ve geri yerine koyma** — geçemeyen atılır.
3. **Özgünlük** — denklemler ortak biçime indirgenip karşılaştırılır, böylece
   `F = W·a/g` ile `W = F·g/a` aynı bağıntı sayılır ve iki kez eklenmez.

Türetilmiş formüller aramada çekirdeğin **arkasında** sıralanır: bunlar
alternatif biçimlerdir, bir sorunun birincil cevabı değil.

### Kendi kendini doğrulama
`kendini doğrula` yazın. Formül tabanı **iki bağımsız sınamadan** geçirilir:

1. **Boyut denetimi** — denklemin iki tarafı aynı fiziksel boyutta mı?
2. **Geri yerine koyma** — çözüm denklemi gerçekten sağlıyor mu?

Şu an **190/190 formül her iki sınamayı da geçiyor** (boyut denetimi 190/190,
geri yerine koyma 190/190; tam tarama ~4 dakika sürer). Öğrenme motoru bu
sınamayı 6 saatte bir arka planda tekrarlar.

Bu sınama iki gerçek hata yakaladı:

1. Birim tablosunda farad'ın boyutu `A²s⁴kg⁻¹m⁻³` yazılmıştı (bu ε₀'ın
   birimi), doğrusu `A²s⁴kg⁻¹m⁻²`. Kondansatör ve RLC hesapları bundan
   etkileniyordu.
2. Bir değişken **üs konumundaysa** (adyabatik süreçte `P₁V₁^γ = P₂V₂^γ`
   denklemindeki γ gibi) sembolik çözüm aşkın bir denkleme dönüşüyor ve SymPy
   pratikte hiç dönmüyordu. Doğrulamanın tamamı bu yüzden hiç
   bitmiyordu — ve kullanıcı γ için çözüm isteseydi uygulama kilitlenirdi.
   Artık böyle hedefler sayısal kök bulmaya yönlendiriliyor: `γ` 0,1 saniyede
   bulunuyor ve sonuç denklemi tam olarak sağlıyor.

### Sistem
`durum` — ne kadar öğrendiğini gösterir · `konulari listele` · `yardim`
`beni taniyor musun` — sizin hakkınızda bildiklerini gösterir · `beni unut`
`matlab konusunda ne kadar bilgin var` — bir alanda ne yapabildiğini anlatır

### Önemli: güncelleme sonrası
Uygulamayı çalışırken güncellerseniz **terminalde Ctrl+C yapıp yeniden
başlatın**. Eski süreç eski davranışı sürdürür. Arayüz, sunucu sürümünün
kendisinden yeni olduğunu görürse sayfayı bir kez otomatik yeniler.

---

## Öğrenme motoru nasıl çalışıyor

Program açık kaldığı sürece arka planda kesintisiz çalışır ve on görevi sırayla
döndürür:

1. **arXiv** — 44 fizik kategorisi
2. **Wikipedia (İngilizce)** — fizik kategorileri
3. **OpenAlex** — 26 fizik konusu
4. **Keşif** — *kendi seçtiği* terimleri araştırır (aşağıya bakın)
5. **Wikipedia (Türkçe)** — fizik kategorileri
6. **Türkçe yayınlar** — OpenAlex dil filtresiyle 25 Türkçe fizik terimi
7. **Derinleşme** — *kendi ürettiği* sorgularla arama yapar
8. **DergiPark** — Türk akademik dergileri (fizik süzgeciyle)
9. **DOAJ** — açık erişim dergiler
10. **Pekiştirme** — topladıklarını işler

Onuncu adım işin özüdür — ve artık sadece sayım yapmıyor, **makaleleri
gerçekten inceliyor**:

- Terim istatistikleri (TF/DF) ve kavram birliktelik grafiği
- LaTeX formüllerinin çıkarılması
- **Cümle sınıflandırma:** her özet cümle cümle okunur ve işlevine ayrılır —
  *tanım*, *bulgu*, *yöntem*, *sayısal*, *ilişki*. Her cümle ilgili kavrama
  bağlanır.
- **İlişki çıkarımı:** "A, B'ye yol açar" kalıbındaki ifadelerden kavramlar
  arası adlandırılmış bağlar kurulur.

Bir konu sorduğunuzda cevabın içinde **"Makaleleri incelerken öğrendiklerim"**
başlığı çıkar; burada terim listesi değil, makalelerden çıkarılmış gerçek
ifadeler yer alır. Sayı yığını cümleler ve konuyla ilgisiz eşleşmeler elenir
(öbek eşleşmesi aranır: "black hole" sorgusu "black carbon" cümlesini getirmez).

### Kendi kendini yönlendirmesi

4. ve 7. adımlar sabit listeleri taramaz; **öğrendiklerine bakarak nereye
bakacağına kendisi karar verir**:

- **Keşif:** Okuduğu makalelerde sık geçen ama tanımını henüz bilmediği
  terimleri seçer ve Wikipedia'da araştırır. Seçerken belge frekansını üstten de
  sınırlar — "analysis", "system" gibi her yerde geçen kelimeler bir fizik
  kavramı değil, akademik dolgudur. Bulduğu maddenin gerçekten fizikle ilgili
  olduğunu metninden doğrular; fizik *eğitimi* makalelerinden gelen "öğretmen",
  "sosyal" gibi terimler böylece kavram sözlüğüne girmez.
- **Derinleşme:** Kavram grafiğinde sık birlikte geçen iki kavramı alır ve o
  kesişimi konu alan yayınları arar. Yani öğrendikçe kendi ilgi alanını genişletir.

Bu iki adımın kaç kavram bulduğunu ve kaç sorgu ürettiğini `durum` yazarak
görebilirsiniz.

**Makalelerin tam metni indirilmez** — yalnızca başlık, özet ve adres saklanır.
Makale başına yaklaşık 4,4 KB yer kaplar; yani 1 milyon makale ≈ 4,4 GB.
Bir makalenin ayrıntısını istediğinizde o an canlı olarak okunur.

İlerleme her turda diske yazılır. Bilgisayarı kapatıp açsanız da kaldığı yerden
devam eder. Kaynaklara nazik davranmak için istekler arasında bekleme uygular.

Günlerce kesintisiz çalışması için iki koruma var: bir **nöbetçi** iş parçacığı
motor beklenmedik şekilde durursa 20 saniye içinde yeniden ayağa kaldırır;
internet kesilirse kademeli bekleme (20 sn → 10 dk) devreye girer, boşuna
dönmez. Toplam öğrenme süresi kaydedilir ve `durum` raporunda gösterilir.

Motoru kenar çubuğundaki **Durdur / Başlat** düğmesiyle yönetebilir, **Kayıt**
ile ne yaptığını canlı izleyebilirsiniz.

---

## Sohbet belleği

Bot iki ayrı düzeyde hatırlar.

**Sohbet içinde** — önceki cevabını hatırlar, devam sorularını anlar. "Entropi
nedir" dedikten sonra şunları yazabilirsiniz:

| Yazın | Anladığı |
|---|---|
| `peki bunu biraz daha acar misin` | entropiyi daha ayrıntılı anlat |
| `ornek ver` | entropi örneği |
| `bu konuda makale bul` | entropi makaleleri |
| `matlab kodu yaz` | entropi hesabı için kod |

Devam sorularında zamirler ("bunu", "o", "bu konuda") temizlenip yalnızca
komut kısmı önceki konuyla birleştirilir. Kendi konusu olan bir soru
("newton yasaları nedir") devam sorusu sayılmaz.

**Sohbetler arasında** — adınızı, kendinizi tanımladığınız düzeyi ve zamanla
neyle ilgilendiğinizi tutar. `adım Polat` ya da `lisans öğrencisiyim` demeniz
yeterli; ayrıca bir ayar yapmanız gerekmez. Yeni sohbet açtığınızda sizi
tanımaya devam eder ve son konuştuğunuz konuları hatırlatır.

`beni taniyor musun` ile ne bildiğini görebilir, `beni unut` ile hepsini
silebilirsiniz. Bunların tamamı yalnızca bu bilgisayardaki veritabanında
durur; hiçbir yere gönderilmez.

---

## Arayüz

Sol sütunda **Sohbetler** listesi vardır. Yeni sohbet açmak eskisini silmez;
listedeki bir sohbete tıklayarak geri dönebilir, üzerine gelince çıkan **×**
ile tek tek silebilirsiniz.

Cevaplar ChatGPT'deki gibi kademeli olarak yazılır. Efekti kenar çubuğundaki
**Yazma efekti** düğmesiyle kapatabilirsiniz; tercihiniz hatırlanır. Yazma
sırasında **Esc**'e basmak ya da mesaja tıklamak cevabı anında tamamlar.

Efekt yalnızca görsel bir katmandır: cevap sunucudan tek parça gelir, arayüz onu
kademeli açar. Markdown yeniden ayrıştırılmadığı için kod vurgulaması, tablolar
ve bağlantılar yazma sırasında bozulmaz. Geçmiş sohbetler efektsiz, anında
yüklenir.

---

## Dürüst sınırlar

Bunu bilerek almanız için açıkça yazıyorum:

- **Bu bir dil modeli değil.** İstediğiniz gibi "hiçbir yapay zekâ altyapısı"
  kullanılmadı. Sonuç olarak serbest sohbet edemez; belirli soru kalıplarını
  tanır ve doğru motora yönlendirir. Tanımadığı bir kalıpta konu anlatımına
  düşer.
- **Özetleme çıkarımsaldır.** Makale özetlerinden en bilgilendirici cümleleri
  seçer; kendi cümlesiyle yeniden yazmaz. Bu yüzden özetler doğrudur ama
  kaynağın diliyle gelir.
- **Konu anlatımları elle yazıldı.** 27 konu ayrıntılıdır ve sayısal örneklerin
  tümü doğrulanmıştır. Bu 27 konunun dışında kalan bir başlıkta anlatım,
  Wikipedia tanımı + makale özeti derlemesine dayanır — daha yüzeysel olur.
- **Öğrenme, arama kalitesini artırır; anlatım yeteneğini değil.** Motor günlerce
  çalıştıkça daha çok makale bulur, kavram grafiği zenginleşir, özetler daha
  isabetli olur. Ama sistem "kendiliğinden fizikçi olmaz".
- **Çeviri yapmaz.** İngilizce makalelerin özet cümleleri İngilizce gösterilir.
  Arayüz, formüller, konu anlatımları ve MATLAB yorumları iki dilde de tamdır.

---

## Dosya düzeni

```
parguszphysics/
├── ParguszPhysics Baslat.command   çift tıkla çalıştır
├── run.py                          başlatıcı
├── core/
│   ├── brain.py       soruyu anlar, doğru motora yönlendirir
│   ├── nlu.py         dil tespiti + niyet sınıflandırma (TR/EN)
│   ├── solver.py      sembolik/sayısal matematik (SymPy)
│   ├── formulas.py    190 çözülebilir fizik formülü
│   ├── sozluk.py      formüller için günlük dil sözlüğü (soru → formül)
│   ├── notlar.py      formüllerin fiziksel anlamı (modele verilen açıklama)
│   ├── knowledge.py   27 konu anlatımı, TR + EN
│   ├── units.py       birim sistemi, boyut analizi, 36 sabit
│   ├── matlab.py      MATLAB/Octave kod üretimi (25 şablon)
│   ├── mkontrol.py    üretilen MATLAB kodunun sözdizimi denetimi
│   ├── sources.py     internet kaynakları
│   ├── dil.py         yerel dil modeli (llama.cpp + GGUF)
│   ├── baglam.py      dil modeline verilecek doğrulanmış bağlam (RAG)
│   ├── anlama.py      yazım düzeltme, eş anlam, soru tipi
│   ├── kalite.py      makale kalite kapısı (fizik mi, hakemli mi, geri çekilmiş mi)
│   ├── bagintilar.py  makalelerden denklem öğrenme + doğrulama
│   ├── sentez.py      öğrenilenlerden konu sayfası üretme
│   ├── dogrulama.py   formülleri boyut + geri-yerine-koyma ile sınar
│   ├── belge.py       PDF/metin okuma ve çözümleme
│   ├── curriculum.py  yol haritaları (MATLAB, fizik, sayısal)
│   ├── profile.py     kişiye dair kalıcı bellek
│   ├── learner.py     sürekli öğrenme motoru
│   ├── retrieval.py   arama + çıkarımsal özetleme
│   ├── db.py          SQLite + FTS5 tam metin indeksi
│   ├── server.py      yerel web sunucusu
│   ├── olcum.py       günlük dil → formül yönlendirme ölçümü
│   ├── genisleme.py   makalelerden yeni yetenek üretimi
│   ├── bosluk.py      konuşmadan öğrenme (bilgi boşlukları, takma adlar)
│   ├── canli.py       canlı internet araştırması + kaynakça
│   ├── ogretim.py     profesör düzeyi yapılandırılmış anlatım
│   ├── sentezbilgi.py makaleleri birleştirip yeni bilgi üretme
│   └── selftest.py    254 test
├── web/               arayüz (HTML/CSS/JS, harici bağımlılık yok)
└── data/              veritabanı ve öğrenme kaydı
```

Gereksinimler: Python 3.8+, `sympy`, `numpy`. Başlatıcı bunları ilk açılışta
kendi kurar.

Sunucu yalnızca `127.0.0.1` üzerinde dinler; dışarıdan erişilemez.
