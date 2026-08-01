# -*- coding: utf-8 -*-
"""Cok adimli problem cozucu: ILERI ZINCIRLEME.

Olculdu: "12 V kaynaga seri bagli 4 ohm ve 8 ohm direnclerden gecen akim"
sorusu tek bir bagintiyla zorlanip "R2 = -4 ohm" cevabini veriyordu. Tek
tek kalip yazmak (devre, atis, carpisma...) bitmeyen bir istir; ogrenci
her zaman yeni bir birlesim getirir.

Bu modul genel cozumu yapar:

    1. Soruda VERILEN buyuklukleri oku.
    2. Dogrulanmis formul tabaninda, tek bilinmeyeni kalan her bagintiyi
       coz ve sonucu bilinenlere EKLE.
    3. Aranan buyukluk bulunana ya da ilerleme durana kadar tekrarla.

Her adim SymPy ile cozulur ve fiziksel makullugu denetlenir. Boylece
"once esdeger direnci bul, sonra akimi hesapla" gibi zincirler, hicbiri
elle yazilmadan cikar.

Guvenlik: ayni sembol farkli formullerde farkli seyi gosterebilir
("R" hem direnc hem gaz sabiti hem yaricap). Bu yuzden bilinenler
(sembol, BIRIM) ciftiyle saklanir; birimi tutmayan eslesme kabul
edilmez. Zincirin uzunlugu da sinirlidir: rastgele uzun turetmeler
ogrenciye yardim etmez, yaniltir.
"""
import re

from . import formulas, nlu, problem, units


MAX_ADIM = 4          # Bir odev sorusu icin makul ust sinir
MIN_SKOR = 12         # Formulun soruyla en azindan zayif ilgisi olmali
# Baska konudan gelen baginti, en iyi eslesmeyle KIYASLANABILIR guclukte
# olmali. Mutlak esik denendi ve yanlis cikti: 45 puanlik sabit sinir,
# "10 m yuksekten birakilan cismin kinetik enerjisi" sorusunda mesru
# olan kin_v2'yi (39 puan) eledi. Goreli olcut ikisini de dogru ayirir:
#   * dusen cisim : en iyi 71, kin_v2 39  -> %55, kabul
#   * BHH sorusu  : en iyi 155, Torricelli 13 -> %8, ret
KONU_DISI_ORAN = 0.35


def _birim_ayni(a, b):
    """Iki birim ayni fiziksel buyuklugu mu gosteriyor?"""
    if not a or not b:
        return False
    if a == b:
        return True
    try:
        ca, cb = units.to_si(1.0, a), units.to_si(1.0, b)
        return bool(ca and cb and ca[1] and cb[1] and ca[1] == cb[1])
    except Exception:
        return False


def _uyar(bilinen, sym, birim):
    """Bilinenler arasinda bu sembol+birim var mi? Degeri dondur."""
    kayit = bilinen.get(sym)
    if not kayit:
        return None
    deger, kayitli_birim = kayit
    if _birim_ayni(kayitli_birim, birim) or not birim or not kayitli_birim:
        return deger
    return None


def _sabit_doldur(f, bilinen):
    """Formuldeki fiziksel sabitleri gercek degerleriyle doldur."""
    out = {}
    for sym in f["vars"]:
        kayit = units.CONSTANTS.get(sym)
        if not kayit:
            continue
        ad = (f["vars"][sym][0] + " " + f["vars"][sym][1]).lower()
        aciklama = (kayit[3] + " " + kayit[4]).lower()
        ortak = ({w for w in ad.split() if len(w) > 3}
                 & {w for w in aciklama.split() if len(w) > 3})
        if ortak or "sabit" in ad or "constant" in ad:
            out[sym] = float(kayit[0])
    return out


def _ad_ortusuyor(ad, etiket):
    """Degisken adi ile sayinin etiketi ortusuyor mu?"""
    a = set(w for w in nlu.norm(ad or "").split() if len(w) > 3)
    e = set(w for w in nlu.norm(etiket or "").split() if len(w) > 3)
    if not a or not e:
        return False
    for x in a:
        for y in e:
            if x[:5] == y[:5]:
                return True
    return False


def _etiketli_sayilar(soru):
    """Sayilarin metindeki ETIKETLERI: [(deger, birim, etiket), ...].

    "yaricapi 0.5 m" ifadesinde 0,5'in etiketi "yaricapi"dir. Etiketli
    bir sayi, o etiketle ortusen degiskene aittir; baska bir degiskene
    verilirse fizik bozulur. Olculdu: yaricap, ortalama hiz bagintisinin
    YER DEGISTIRME degiskenine atandi ve v = dx/dt = 0,25 m/s cikti
    (dogrusu 2πr/T = 1,57 m/s).
    """
    try:
        ham = nlu.adli_degerler(soru) or []
    except Exception:
        return []
    # Etiket, sayiya KOMSU kelimelerdir. Olculdu: "surtunme katsayisi
    # 0.4 olan 10 kg cisme" ifadesinde 10 kg'in etiketi "surtunme
    # katsayisi 0.4 olan" diye cikiyor, "surtunme katsayisi" baska bir
    # buyuklugu (mu) adlandirdigi icin kutle atamasi reddediliyordu.
    out = []
    for etiket, d, b in ham:
        kelimeler = (etiket or "").split()
        out.append((d, b, " ".join(kelimeler[-3:])))
    return out


def _atama_uygun_mu(f, sym, deger, etiketliler, tum_adlar):
    """Bu deger bu degiskene verilebilir mi?

    Kural: sayinin etiketi BASKA bir buyuklugu adlandiriyorsa, bu
    degiskene verilemez. Hicbir seyi adlandirmiyorsa serbesttir.

    Ilk deneme "etiket bu degiskenin adiyla ortusmeli" idi ve fazla
    katiydi: "2 kg cisim 20 m/s ile yukari atiliyor" cumlesinde 20'nin
    etiketi "kg cisim" gibi gurultu; hicbir seyi adlandirmiyor ama
    atama reddediliyordu (olculdu: iki mesru problem cozulemez oldu).
    """
    ad = (f["vars"][sym][0] or "") + " " + (f["vars"][sym][1] or "")
    for d, _b, etiket in etiketliler:
        if abs(float(d) - float(deger)) > 1e-9:
            continue
        if not etiket:
            return True
        if _ad_ortusuyor(ad, etiket):
            return True          # etiket bu degiskeni adlandiriyor
        # Etiket BASKA bir buyuklugu adlandiriyor mu?
        for baska in tum_adlar:
            if _ad_ortusuyor(baska, etiket):
                return False
        return True              # etiket hicbir seyi adlandirmiyor
    return True


def _ortusme_puani(ad, etiket):
    """Degisken ADI ile sayinin ETIKETI kac anlamli kelimede ortusuyor?"""
    if not ad or not etiket:
        return 0
    onemsiz = {"ile", "olan", "bir", "icin", "gore", "kadar", "the", "of",
               "and", "for", "with", "a", "an"}
    a = {w for w in nlu.norm(ad).split() if len(w) > 2 and w not in onemsiz}
    b = {w for w in nlu.norm(etiket).split() if len(w) > 2 and w not in onemsiz}
    if not a or not b:
        return 0
    ortak = 0
    for x in a:
        for y in b:
            # Turkce cekim eki icin kok karsilastirmasi
            if x == y or (len(x) >= 4 and len(y) >= 4
                          and (x.startswith(y[:4]) or y.startswith(x[:4]))):
                ortak += 1
                break
    return ortak


def _cevre_etiketleri(soru):
    """Her sayinin IKI YANINDAKI kelimeler: [(deger, birim, cevre), ...].

    `_etiketli_sayilar` yalnizca sayinin SOLUNU okur. Turkce'de tanim
    sagda da olabilir: "340 m/s SES HIZINDA 30 m/s ile yaklasan..."
    Olculdu: bu cumlede 340'in etiketi bos cikiyor, "ses hizinda" ise
    30'a yaziliyordu; sonuc olarak ses hizi 30 m/s sanildi.

    Burada sayinin solundaki ve sagindaki kelimeler birlikte alinir;
    sinir, komsu sayilardir.
    """
    try:
        degerler = nlu.extract_number_unit(soru) or []
    except Exception:
        return []
    metin = soru or ""
    out = []
    for i, (deger, birim, bas, son) in enumerate(degerler):
        sol_sinir = degerler[i - 1][3] if i > 0 else 0
        sag_sinir = degerler[i + 1][2] if i + 1 < len(degerler) else len(metin)
        sol = metin[sol_sinir:bas].split()[-3:]
        sag = metin[son:sag_sinir].split()[:3]
        out.append((float(deger), birim, " ".join(sol + sag)))
    return out


def _etikete_gore_esle(f, etiketliler, dolu=None):
    """AYNI BIRIMLI birden fazla deger varsa etikete gore dagit.

    Olculdu: "340 m/s ses hizinda 30 m/s ile yaklasan 1000 Hz kaynak icin
    duyulan frekans" sorusunda Doppler bagintisinin `v` (ses hizi),
    `vo` (gozlemci hizi) ve `vs` (kaynak hizi) degiskenlerinin ucu de
    m/s. Mevcut kural bir VETO kuraliydi ("bu deger bu degiskene
    verilebilir mi?") ve iki deger de vetoyu gectigi icin ilk gelen
    kazaniyordu: 340 ile 30 karisiyor, sonuc yanlis cikiyordu.

    Burada TERCIH kurali var: her (deger, degisken) cifti etiket
    ortusmesiyle puanlanir ve en yuksek puanli ciftten baslanarak
    dagitilir. "ses hizinda" etiketi `ses hizi` degiskenini birebir
    adlandirir; 340 oraya gider, 30'a baska bir degisken kalir.
    """
    if not etiketliler:
        return {}
    # Ayni birimi paylasan degisken var mi?
    birim_sym = {}
    for sym, (_tr, _en, u) in f["vars"].items():
        birim_sym.setdefault((u or "").strip(), []).append(sym)
    ciftler = []
    for deger, birim, etiket in etiketliler:
        for u, symler in birim_sym.items():
            if len(symler) < 2:
                continue          # tek aday varsa zaten karisiklik yok
            if not _birim_ayni(birim, u):
                continue
            for sym in symler:
                ad = ((f["vars"][sym][0] or "") + " "
                      + (f["vars"][sym][1] or ""))
                puan = _ortusme_puani(ad, etiket)
                if puan > 0:
                    ciftler.append((puan, deger, birim, sym))
    dolu = set(dolu or ())
    atanan, kullanilan_sym, kullanilan_deger = {}, set(dolu), set()

    def _yerlestir(deger, birim, sym):
        si = float(deger)
        if birim:
            try:
                cevrim = units.to_si(float(deger), birim)
                if cevrim and cevrim[0] is not None:
                    si = float(cevrim[0])
            except Exception:
                pass
        atanan[sym] = (si, f["vars"][sym][2])
        kullanilan_sym.add(sym)
        kullanilan_deger.add(deger)

    ciftler.sort(key=lambda x: -x[0])
    for puan, deger, birim, sym in ciftler:
        if sym in kullanilan_sym or deger in kullanilan_deger:
            continue
        _yerlestir(deger, birim, sym)

    # ELEME YOLUYLA ATAMA. Etiketle eslesenler yerlestikten ve senaryonun
    # verdigi degerler dolduktan sonra, ayni birimden geriye TEK deger ve
    # TEK degisken kaldiysa bunlar eslesmek zorundadir.
    #
    # Olculdu: Doppler'de "ses hizinda" etiketi 340'i `v`ye baglar,
    # senaryo `vo = 0` der; geriye kalan 30 m/s ile kaynak hizi `vs`
    # basbasa kalir. Etiket ("ile yaklasan") kaynak hizini adlandirmadigi
    # icin puanla baglanamiyordu ve zincir cozumsuz kaliyordu.
    for u, symler in birim_sym.items():
        if len(symler) < 2:
            continue
        bos_sym = [s for s in symler if s not in kullanilan_sym]
        bos_deger = [(d, b) for d, b, _e in etiketliler
                     if d not in kullanilan_deger and _birim_ayni(b, u)]
        if len(bos_sym) == 1 and len(bos_deger) == 1:
            _yerlestir(bos_deger[0][0], bos_deger[0][1], bos_sym[0])
    return atanan


def _sabit_sembol_mu(sym, adaylar):
    """Bu sembol adaylarin BIRINDE fiziksel sabit olarak mi geciyor?

    Olculdu: "400 nm isik dusurulurse" sorusunda 400 nm degeri `h`
    sembolune yaziliyordu; `h` bazi bagintilarda YUKSEKLIK ama
    fotoelektrikte PLANCK SABITIDIR. Sabitin uzerine soru degeri
    yazilmasi cevabi sessizce mahveder.
    """
    for _s, f in adaylar:
        veri = (f.get("vars") or {}).get(sym)
        if not veri:
            continue
        ad = (veri[0] or "") + " " + (veri[1] or "")
        if re.search(r"\b(sabit|constant|planck|boltzmann|avogadro|"
                     r"isik hizi|speed of light)\b", ad, re.I):
            return True
    return False


def _baslangic_bilinenler(soru, adaylar):
    """Sorudaki degerleri oku: (sembol -> (deger_SI, birim))."""
    bilinen = {}
    # Sembol biciminde yazilmis degerler ("v0 = 5 m/s")
    try:
        for sym, v in (nlu.extract_known_values(soru) or {}).items():
            deger, birim = (v if isinstance(v, tuple) else (v, ""))
            if deger is None:
                continue
            bilinen[sym] = (float(deger), birim or "")
    except Exception:
        pass

    # Dogal dilden: her aday formulun kendi degisken adlariyla.
    #
    # DIKKAT: yalnizca BIRIM tutuyor diye her formulun her degiskenine
    # deger atamak yanlis fizige goturur. Olculdu: "yaricapi 0.5 m"
    # ifadesindeki 0,5 m, ortalama hiz bagintisinin YER DEGISTIRME
    # degiskenine atandi ve v = dx/dt = 0,25 m/s gibi anlamsiz bir cevap
    # cikti. Bu yuzden en iyi eslesme disindaki formuller icin yalnizca
    # ADI da tutan atamalari kabul ediyoruz.
    en_iyi_id = adaylar[0][1]["id"] if adaylar else None
    etiketliler = _etiketli_sayilar(soru)
    # Adaylardaki TUM degisken adlari: bir etiketin baska bir buyuklugu
    # adlandirip adlandirmadigini bilmek icin gerekli.
    tum_adlar = []
    for _s2, f2 in adaylar:
        for sym2 in f2["vars"]:
            tum_adlar.append((f2["vars"][sym2][0] or "") + " "
                             + (f2["vars"][sym2][1] or ""))
    # EN IYI formulde ayni birimli birden fazla degisken varsa, degerleri
    # once ETIKETE gore dagit. Bu, asagidaki genel okumadan ONCE gelmeli:
    # genel okuma sirayla atadigi icin ilk gelen degeri kapiyor.
    if adaylar:
        # SENARYONUN ima ettigi degerler once gelir ("gozlemci durgun"
        # -> vo = 0). Aksi hâlde etiket eslemesi o degiskeni doldurup
        # gercek degeri yanlis yere koyuyordu (olculdu: Doppler'de
        # kaynagin 30 m/s hizi gozlemci hizina yaziliyordu).
        # "0.8c" gibi ISIK HIZI KATLARI. Olculdu: "0.8c hizla giden
        # saatte 1 saniye gecerse" sorusunda `v` degiskenine 1 (saniye)
        # yaziliyordu; dogru deger 2,398×10⁸ m/s. Bu deger metnin KENDI
        # sozunden gelir, birim tahmininden degil — ustune yazar.
        try:
            for sym, deger in (problem.isik_hizi_degerleri(soru) or {}).items():
                for _sk, _f in adaylar:
                    if sym in _f["vars"]:
                        bilinen[sym] = (float(deger), _f["vars"][sym][2])
                        break
        except Exception:
            pass
        try:
            _ima, _ = problem.malzeme_degerleri(soru)
            _semboller = {s for _sk, _f in adaylar for s in _f["vars"]}
            for sym, deger in (_ima or {}).items():
                if sym in _semboller and sym not in bilinen:
                    birim = ""
                    for _sk, _f in adaylar:
                        if sym in _f["vars"]:
                            birim = _f["vars"][sym][2]
                            break
                    bilinen[sym] = (float(deger), birim)
        except Exception:
            pass
        try:
            # SORULAN buyukluk eslesmeye KATILMAZ. Olculdu: Doppler'de
            # "…icin DUYULAN frekans nedir" etiketi 1000 Hz'i `f`ye
            # (duyulan frekans — yani sorulan buyukluge) bagliyordu;
            # oysa 1000 Hz kaynagin frekansidir (`f0`). Sorulan sembolu
            # disarida birakinca eleme dogru sonucu veriyor.
            _sorulan = None
            try:
                _sorulan = problem.hedef_tahmin(adaylar[0][1], soru)
            except Exception:
                pass
            _dolu = set(bilinen)
            if _sorulan:
                _dolu.add(_sorulan)
            # Etiket eslemesi YALNIZCA en iyi formule uygulanIyordu.
            # Olculdu: RC sorusunda kullanilan baginti `rc_gerilim` ama
            # havuzun tepesinde baska bir baginti vardi; 10 kΩ hicbir
            # zaman `R`ye baglanmiyordu. Havuzun ilk birkac bagintisi
            # icin de calistirmak, dogru atamayi kaciran bu bosluğu
            # kapatir (setdefault: once gelen kazanir).
            _cevre = _cevre_etiketleri(soru)
            for _s3, _f3 in adaylar[:5]:
                for sym, veri in _etikete_gore_esle(
                        _f3, _cevre, dolu=_dolu).items():
                    bilinen.setdefault(sym, veri)
        except Exception:
            pass

    for _skor, f in adaylar:
        try:
            okunan = nlu.formul_degerleri(f, soru) or {}
        except Exception:
            continue
        for sym, (deger, birim) in okunan.items():
            if sym in bilinen or deger is None:
                continue
            # Fiziksel SABITIN uzerine soru degeri yazilmaz.
            if _sabit_sembol_mu(sym, adaylar):
                continue
            if (f["id"] != en_iyi_id
                    and not _atama_uygun_mu(f, sym, deger, etiketliler,
                                            tum_adlar)):
                continue
            hedef_birim = f["vars"][sym][2]
            si = float(deger)
            if birim:
                try:
                    cevrim = units.to_si(float(deger), birim)
                    if cevrim and cevrim[0] is not None:
                        si = float(cevrim[0])
                except Exception:
                    pass
            bilinen[sym] = (si, hedef_birim)

    # Senaryolarin ima ettigi degerler ("elektron" -> q = e)
    try:
        sen_degerler, sen_notlar = problem.senaryo_degerleri(soru)
    except Exception:
        sen_degerler, sen_notlar = {}, []
    return bilinen, sen_degerler, sen_notlar


def _hedef_adaylari(soru, adaylar, bilinen, en_fazla=5):
    """Aranan buyukluk icin SIRALI aday listesi: [(sembol, formul), ...].

    Tek bir hedefe kilitlenmek yanlisti: "fren kuvveti" sorusunda en
    yuksek puanli baginti surtunme kuvvetiydi (f = μN) ve oradan zincir
    kurulamiyordu; oysa Newton'un 2. yasasi uzerinden cozum vardi
    (olculdu).
    """
    out, gorulen = [], set()
    for _skor, f in adaylar:
        # Formulun adi gecen TUM degiskenlerini sirayla dene; bilinen
        # olanlari atla. Olculdu: surtunme sorusunda "katsayi" hedef
        # seciliyor, oysa o verilmis; "kuvvet" ise atlaniyordu.
        try:
            sirali = problem.hedef_siralamasi(f, soru)
        except Exception:
            sirali = []
        if not sirali:
            try:
                h = problem.hedef_tahmin(f, soru)
                sirali = [h] if h else []
            except Exception:
                sirali = []
        for h in sirali:
            if h not in f["vars"]:
                continue
            if _uyar(bilinen, h, f["vars"][h][2]) is not None:
                continue          # zaten biliniyor: hedef olamaz
            anahtar = (h, f["id"])
            if anahtar not in gorulen:
                gorulen.add(anahtar)
                out.append((h, f))
            break
    for _skor, f in adaylar:
        eksik = [s for s in f["vars"]
                 if _uyar(bilinen, s, f["vars"][s][2]) is None]
        if len(eksik) == 1:
            anahtar = (eksik[0], f["id"])
            if anahtar not in gorulen:
                gorulen.add(anahtar)
                out.append((eksik[0], f))
    return out[:en_fazla]


def _adim_coz(f, bilinen, sabitler):
    """Formulde tek bilinmeyen kaldiysa coz: (sembol, deger) ya da None."""
    degerler = dict(sabitler)
    for sym in f["vars"]:
        if sym in degerler:
            continue
        d = _uyar(bilinen, sym, f["vars"][sym][2])
        if d is not None:
            degerler[sym] = d
    eksik = [s for s in f["vars"] if s not in degerler]
    if len(eksik) != 1:
        return None
    hedef = eksik[0]
    try:
        _t, cozumler, _e = formulas.solve_for(f, degerler, target=hedef)
    except Exception:
        return None
    gercel = [x for x in cozumler if isinstance(x, float)]
    if not gercel:
        return None
    deger = problem.kok_sec(f, hedef, gercel)
    ok, _sebep = problem.makul_mu(f, hedef, deger)
    if not ok:
        # Diger kok makul olabilir (ikinci dereceden denklemler)
        for x in gercel:
            if problem.makul_mu(f, hedef, x)[0]:
                deger = x
                break
        else:
            return None
    return hedef, deger, degerler


# Sorunun GUNLUK olcekte oldugunu gosteren isaretler. Bunlar varsa ve
# gorelilik/astronomi/kuantum isareti yoksa, cevap da gunluk olcekte
# olmalidir.
_GUNLUK_IZ = re.compile(
    r"\b(araba|otomobil|arac|kamyon|bisiklet|motosiklet|viraj|donemec|"
    r"yol|kavsak|asansor|top|taş|tas|kutu|sandik|cisim|blok|kizak|"
    r"sarkac|yay|makara|ip|halat|kopru|bina|pencere|masa|araba"
    r"|car|vehicle|curve|road|elevator|ball|box|block|sled|pendulum)\b",
    re.I)

_EVREN_IZ = re.compile(
    r"\b(gorelilik|goreli|isik hizi|foton|kuantum|atom|elektron|proton|"
    r"notron|cekirdek|galaksi|yildiz|gezegen|uydu|yorunge|kara delik|"
    r"schwarzschild|evren|kozmik|nukleer|parcacik|relativi|photon|"
    r"quantum|galaxy|star|planet|orbit|black hole|cosmic|nuclear)\b",
    re.I)

# Isik hizinin bu kadarini asan bir "gunluk" hiz fizik degildir.
_HIZ_SINIRI = 0.1 * 2.99792458e8


def _olcek_makul(soru, hedef_f, hedef, deger):
    """Sonuc, sorunun OLCEGINE uygun mu?

    Gunluk olcekli bir problemde (araba, viraj, top, sarkac) gorelilik ya
    da astronomi isareti yoksa; isik hizina yakin bir hiz ya da yildiz
    kutlesi buyuklugunde bir kutle cikiyorsa zincir yanlis yoldan
    gitmistir. Boyle bir cevabi basmak yerine cozumsuz kalmak dogrudur.
    """
    try:
        buyukluk = abs(float(deger))
    except Exception:
        return True
    if not _GUNLUK_IZ.search(soru or "") or _EVREN_IZ.search(soru or ""):
        return True
    birim = (hedef_f.get("vars", {}).get(hedef) or ("", "", ""))[2] or ""
    if birim in ("m/s", "m/sn") and buyukluk > _HIZ_SINIRI:
        return False
    if birim == "kg" and buyukluk > 1e12:
        return False
    if birim in ("J", "N") and buyukluk > 1e15:
        return False
    return True


def _aday_havuzu(soru):
    """Zincirin kullanabilecegi bagintilar — KONUDA KALARAK.

    Olculdu: "30 m genlikli, periyodu 10 s olan basit harmonik hareketin
    maksimum hizi" sorusunda dogru baginti (v = A·ω) birinci sirada
    geliyordu, ama ω'yi uretecek baginti aday listesine girmemisti.
    Zincir cikmaza girince listedeki BASKA bir "v" bagintisina kaydi ve
    Torricelli akis hizi + kacis hizi zincirleyip 24,26 m/s dedi.
    Dogru cevap 18,85 m/s. Alakasiz konudan formul secmek, cevapsiz
    kalmaktan kotudur.

    Iki kural:
      1. Sorunun konusu, en yuksek puanli bagintinin konusudur. Zincir
         o konunun disina yalnizca COK guclu bir eslesmeyle cikabilir.
      2. Konunun butun bagintilari havuza girer — puani dusuk olsa bile.
         Ara adimi uretecek baginti cogu zaman soruda adi gecmeyendir
         (ω = 2π/T gibi).
    """
    vurus = [(s, f) for s, f in formulas.search(soru, limit=14)
             if s >= MIN_SKOR and not f.get("uretilmis")]
    if not vurus:
        return []
    ana_konu = vurus[0][1].get("topic")
    en_iyi = vurus[0][0] or 1
    esik = en_iyi * KONU_DISI_ORAN
    havuz, gorulen = [], set()
    for skor, f in vurus:
        if f["topic"] == ana_konu or skor >= esik:
            havuz.append((skor, f))
            gorulen.add(f["id"])
    # Ayni konunun geri kalan bagintilari: ara adim uretebilirler
    for f in formulas.FORMULAS:
        if (f.get("topic") == ana_konu and f["id"] not in gorulen
                and not f.get("uretilmis")):
            havuz.append((MIN_SKOR - 1, f))
            gorulen.add(f["id"])
    return havuz


def kullanilan_formuller(soru, max_adim=MAX_ADIM):
    """Bu problemi cozerken hangi bagintilar kullanilir? (id listesi)

    Cozum SEMASI cikarmak icin: metni degil, YOLU dondurur.
    """
    metin = coz(soru, "tr", max_adim)
    if not metin:
        return []
    idler = []
    for f in formulas.FORMULAS:
        ad = f["tr"]
        if ad and ("**%s**" % ad) not in metin and ad not in metin:
            continue
        if ad and ad in metin and f["id"] not in idler:
            idler.append(f["id"])
    return idler


def coz(soru, lang="tr", max_adim=MAX_ADIM):
    """Cok adimli problemi zincirleyerek coz. Metin ya da None."""
    tr = lang == "tr"
    adaylar = _aday_havuzu(soru)
    if not adaylar:
        return None

    # GECMIS DENEYIM. Benzer imzali problemlerde ise yaramis baginti
    # dizileri varsa onlari one aliyoruz. Bu, cevabi degistirmez —
    # cevabi yine SymPy hesaplar ve fiziksel makullugu denetlenir —
    # yalnizca DOGRU YOLU daha cabuk bulmayi saglar. Ogrencinin
    # "benzer soruyu daha once cozmustum" demesiyle ayni sey.
    try:
        from . import problemler as _prb
        oncelik = []
        for idler, _kanit, _hata in _prb.sema_ipucu(soru):
            oncelik.extend(idler)
        if oncelik:
            sirali, kalan = [], []
            for skor, f in adaylar:
                (sirali if f["id"] in oncelik else kalan).append((skor, f))
            if sirali:
                adaylar = sirali + kalan
    except Exception:
        pass

    bilinen, sen_degerler, sen_notlar = _baslangic_bilinenler(soru, adaylar)
    if len(bilinen) < 2:
        return None            # tek deger varsa zincire gerek yok

    # SORULAN BUYUKLUK BILINEN SAYILMAZ. Olculdu: "340 m/s ses hizinda
    # 30 m/s ile yaklasan 1000 Hz kaynak icin DUYULAN FREKANS nedir"
    # sorusunda 1000 Hz hem `f0` (kaynak frekansi) hem `f` (duyulan
    # frekans) degiskenine yaziliyordu; `f` dolu oldugu icin hedef
    # listesine hic girmiyor ve cozulecek bilinmeyen kalmiyordu.
    # Sorunun ACIKCA sordugu sembol, birim eslemesiyle tahmin edilmis
    # olsa bile bilinenlerden cikarilmalidir.
    # DIKKAT: bu kural DAR tutulmali. Genis hâli ("sorulan sembolu her
    # zaman cikar") olculdu ve gerileme yaptI: "surtunme katsayisi 0.4
    # olan 10 kg cisme etkiyen surtunme kuvveti" sorusunda `f` cikarilinca
    # cozum bozuldu (sayisal 39/39 -> 38/39). Yalnizca AYNI DEGER baska
    # bir degiskene de yazilmissa — yani deger gercekten paylasilmissa —
    # sorulan sembol serbest birakilir.
    try:
        _sorulan = problem.hedef_tahmin(adaylar[0][1], soru)
        if _sorulan and _sorulan in bilinen:
            _deger = bilinen[_sorulan][0]
            _paylasan = [s for s, (d, _u) in bilinen.items()
                         if s != _sorulan and abs(d - _deger) < 1e-9]
            _acik = set((nlu.extract_known_values(soru) or {}).keys())
            if _paylasan and _sorulan not in _acik:
                bilinen.pop(_sorulan, None)
    except Exception:
        pass

    hedef_listesi = _hedef_adaylari(soru, adaylar, bilinen)
    if not hedef_listesi:
        return None

    # Atis senaryosunda verilen hiz ILK hizdir. problem.coz icinde ayni
    # kural var; zincirde de gecerli olmali (olculdu: "yukari atiliyor
    # 3 saniye sonraki kinetik enerjisi" cozulemiyordu).
    if any(x.get("hiz_ilk") for x in (sen_notlar or [])):
        if "v" in bilinen and "v0" not in bilinen:
            bilinen["v0"] = bilinen.pop("v")

    # Senaryo degerlerini uygun formullerin birimiyle ekle. Hedef
    # adaylari birden fazla oldugu icin burada hedefe gore eleme
    # yapmiyoruz; zincir zaten bilineni yeniden uretmeye calismaz.
    # Senaryo degerleri metnin KENDI sozunden gelir ("duruyor" demek
    # son hiz sifir demektir); birim eslemesiyle tahmin edilen degerin
    # UZERINE yazarlar. Olculdu: frenleme sorusunda hem v hem v0 20 m/s
    # okunmus, senaryonun v = 0 degeri yazilamamis ve ivme sifir
    # cikmisti — yani "fren kuvveti 0 N" gibi acikca yanlis bir cevap.
    _hedef_semboller = {h for h, _f in hedef_listesi}
    for sym, deger in (sen_degerler or {}).items():
        if sym in _hedef_semboller:
            continue
        for _s, f in adaylar:
            if sym in f["vars"]:
                bilinen[sym] = (float(deger), f["vars"][sym][2])
                break

    # ── Hedefe yonelik (geri) zincirleme ───────────────────────────────
    # Ileri zincirleme denendi ve BASIBOS kaldi: dusen bir cisim
    # sorusundan yay sabiti ve kutle-enerji esdegerligi turetti
    # (olculdu). Ogrenciye yardim etmeyen, yaniltan bir davranis.
    # Dogrusu hedeften geriye gitmek: aranan buyuklugu veren bagintiyi
    # bul, onun eksiklerini de ayni sekilde tamamla.
    #
    # Iki sinir birlikte calisir:
    #   * Aday formul soruyla gercekten ilgili olmali (skor esigi).
    #   * Zincir KISA olmali; uzun turetme odev cozumu degil, gurultudur.
    baslangic_bilinen = dict(bilinen)
    adimlar = []
    kullanilan = set()

    def _uret(sym, birim, derinlik):
        """sym degerini uretmeye calis; basarirsa True."""
        if _uyar(bilinen, sym, birim) is not None:
            return True
        if derinlik <= 0:
            return False
        for skor, f in adaylar:
            if f["id"] in kullanilan or sym not in f["vars"]:
                continue
            if not _birim_ayni(f["vars"][sym][2], birim):
                continue
            sabitler = _sabit_doldur(f, bilinen)
            # Bu bagintinin diger eksiklerini once uretmeyi dene
            eksikler = [v for v in f["vars"]
                        if v != sym and v not in sabitler
                        and _uyar(bilinen, v, f["vars"][v][2]) is None]
            if len(eksikler) > 2:
                continue        # cok bilinmeyenli dal: odev sorusu degil
            kullanilan.add(f["id"])
            tamam = all(_uret(v, f["vars"][v][2], derinlik - 1)
                        for v in eksikler)
            if tamam:
                sonuc = _adim_coz(f, bilinen, _sabit_doldur(f, bilinen))
                if sonuc and sonuc[0] == sym:
                    _s, deger, girdiler = sonuc
                    bilinen[sym] = (deger, f["vars"][sym][2])
                    adimlar.append((f, sym, deger, girdiler))
                    return True
            kullanilan.discard(f["id"])

        # Havuz tukendi. Son care: TUM tabanda, bu sembolu veren ve
        # DIGER butun degiskenleri zaten bilinen bir baginti var mi?
        # Bu genisleme guvenlidir: hicbir sey tahmin etmez, yalnizca
        # elde olan degerlerle tek adimda sonuc veren bir baginti arar.
        # Olculdu: "10 m yuksekten birakilan 2 kg cismin kinetik
        # enerjisi" sorusunda hizi veren v = sqrt(2gh) bagintisi havuza
        # girmiyordu (soru kinetik enerji soruyor) ve zincir kuruluyordu.
        if derinlik > 0:
            for f in formulas.FORMULAS:
                if f["id"] in kullanilan or sym not in f["vars"]:
                    continue
                if f.get("uretilmis"):
                    continue
                if not _birim_ayni(f["vars"][sym][2], birim):
                    continue
                sabitler = _sabit_doldur(f, bilinen)
                eksikler = [v for v in f["vars"]
                            if v != sym and v not in sabitler
                            and _uyar(bilinen, v, f["vars"][v][2]) is None]
                if eksikler:
                    continue          # tahmin yok: hepsi bilinmeli
                sonuc = _adim_coz(f, bilinen, sabitler)
                if sonuc and sonuc[0] == sym:
                    _s, deger, girdiler = sonuc
                    bilinen[sym] = (deger, f["vars"][sym][2])
                    kullanilan.add(f["id"])
                    adimlar.append((f, sym, deger, girdiler))
                    return True
        return False

    son, hedef, hedef_f = None, None, None
    for _h, _hf in hedef_listesi:
        bilinen.clear()
        bilinen.update(baslangic_bilinen)
        del adimlar[:]
        kullanilan.clear()
        _uret(_h, _hf["vars"][_h][2], max_adim)
        _d = _uyar(bilinen, _h, _hf["vars"][_h][2])
        if _d is not None and len(adimlar) >= 2:
            son, hedef, hedef_f = _d, _h, _hf
            break
    if son is None:
        # ACGOZLU ZINCIR TIKANDI — SISTEMI BIRLIKTE COZ.
        # Kullanicinin tespiti: bir insan problemi tek tek formul
        # secerek degil, ilgili BUTUN bagintilari yan yana yazip sistemi
        # cozerek halleder. Olculdu: Doppler'de `f` sembolu organ
        # borusu, dalga ve Doppler bagintilarinda birden geciyor; zincir
        # yanlis dala girip tukeniyordu. Sistem cozucude hangi
        # bagintinin once geldigi onemli degildir.
        try:
            from . import sistem as _sis
            # DIKKAT: `L` yardimcisi bu noktadan SONRA tanimlaniyor;
            # burada kullanilirsa NameError atar ve disaridaki
            # `except Exception: pass` bunu sessizce yutar. Olculdu:
            # sistem cozucu Doppler'i 1096,77 diye dogru cozuyordu ama
            # metin kurulurken atilan NameError yuzunden cevap
            # "cozulemedi" olarak donuyordu.
            _L = lambda a, b: a if tr else b
            # Hedefleri, bagintinin SORUYLA ESLESME SKORUNA gore sirala.
            # Olculdu: `f` sembolu organ borusu, dalga ve Doppler'de
            # birden geciyor; liste sirasiyla gidince once organ
            # borusundan 0.0 donuyordu. Soruya en cok uyan baginti
            # once denenmeli.
            _skor = {f["id"]: s for s, f in adaylar}
            _liste = list(hedef_listesi)
            # SORULAN sembolu iceren HER bagintiyi da dene. Olculdu:
            # fotoelektrikte `Ek` sembolu hedef listesinde vardi ama
            # yalnizca birkac baginti ile; dalga boyu bicimindeki
            # (`Ek = h*c/lam - W`) baginti listeye hic girmiyordu ve
            # cozum kaciyordu. Sistem cozucu dogru bagintiyla
            # cagrildiginda 1,281×10⁻¹⁹ J'yi dogru veriyor.
            try:
                _sorulan2 = problem.hedef_tahmin(adaylar[0][1], soru)
            except Exception:
                _sorulan2 = None
            if _sorulan2:
                # Sorulan sembol hâlâ bilinenler arasindaysa serbest
                # birak: fallback'e gelindiyse zincir zaten cozememis
                # demektir ve o deger baska bir buyuklukten tahminle
                # gelmistir. Olculdu: cift yarikta `dy` (sorulan sacak
                # araligi) 1e-4 ile doluydu — o aslinda yarik araligi
                # `d`nin degeri; serbest birakilinca sonuc 0,012 m
                # dogru cikiyor.
                bilinen.pop(_sorulan2, None)
                _var = {(h, f["id"]) for h, f in _liste}
                for _s2, f2 in adaylar:
                    if _sorulan2 in f2["vars"] and \
                            (_sorulan2, f2["id"]) not in _var:
                        _liste.append((_sorulan2, f2))
            _sirali = sorted(_liste,
                             key=lambda x: -_skor.get(x[1]["id"], 0))
            for _h, _hf in _sirali:
                sonuc = _sis.coz(soru, adaylar, bilinen, _h, _hf, lang)
                if not sonuc:
                    continue
                _deger, _kullanilan = sonuc
                # Sifir sonuc, cogu zaman dejenere bir sistemin isaretidir
                # (organ borusu bagintisi bilinmeyen uzunlukla 0 veriyordu).
                if abs(_deger) < 1e-12 and not (sen_degerler or {}):
                    continue
                if not _olcek_makul(soru, _hf, _h, _deger):
                    continue
                satir = ["### " + _L("Çözüm — denklem sistemi",
                                    "Solution — system of equations"), ""]
                satir.append(_L("**Birlikte çözülen bağıntılar**",
                               "**Equations solved together**"))
                satir.append("")
                for f in _kullanilan:
                    satir.append("- `%s`  —  %s"
                                 % (f["eq"], f["tr"] if tr else f["en"]))
                satir.append("")
                satir.append("**" + _L("Verilenler", "Given") + "**")
                satir.append("")
                for sym, veri in sorted(bilinen.items()):
                    if sym == _h:
                        continue
                    if not any(sym in f["vars"] for f in _kullanilan):
                        continue
                    satir.append("- `%s` = %s %s"
                                 % (sym, problem._oku_sayi(veri[0]),
                                    veri[1] or ""))
                satir.append("")
                satir.append("## `%s` = **%s %s**"
                             % (_h, problem._oku_sayi(_deger),
                                _hf["vars"][_h][2]))
                satir.append("")
                satir.append("_" + _L(
                    "İlgili bağıntılar birlikte yazılıp sistem SymPy ile "
                    "çözüldü; sonuç fiziksel olarak denetlendi.",
                    "The relevant equations were solved as a system with "
                    "SymPy and the result was checked for plausibility.")
                    + "_")
                return "\n".join(satir)
        except Exception:
            pass
        return None            # tek adimliysa normal cozucu zaten yeter
    # Adimlar geri zincirlemede TERS sirada birikir; ogrenciye ilerleyen
    # sirada gosterilmeli.
    adimlar = list(adimlar)

    # ── Metni yaz ──────────────────────────────────────────────────────
    L = lambda a, b: a if tr else b
    lines = ["### " + L("Çözüm — %d adımlı" % len(adimlar),
                        "Solution — %d steps" % len(adimlar)), ""]
    for n in sen_notlar:
        lines.append("_%s_" % (n["not_tr"] if tr else n["not_en"]))
        lines.append("")

    # Yalnizca adimlarda GERCEKTEN kullanilan girdiler listelenir.
    # Olculdu: ayni 10 m degeri dx, h, x diye uc kez, 2 kg ise m, m1,
    # dm diye uc kez listeleniyordu — ogrenci icin kafa karistirici.
    uretilen = {a[1] for a in adimlar}
    kullanilan_girdiler = {}
    for f, sym, _d, girdiler in adimlar:
        for k, v in girdiler.items():
            if k != sym and k not in uretilen:
                kullanilan_girdiler[k] = (v, f["vars"][k][2])
    if kullanilan_girdiler:
        lines.append("**" + L("Verilenler", "Given") + "**")
        lines.append("")
        for sym, (deger, birim) in sorted(kullanilan_girdiler.items()):
            lines.append("- `%s` = %s %s"
                         % (sym, problem._oku_sayi(deger), birim))
        lines.append("")

    for i, (f, sym, deger, girdiler) in enumerate(adimlar, 1):
        ad = f["tr"] if tr else f["en"]
        lines.append("**%d. %s**" % (i, ad))
        lines.append("")
        lines.append("`%s`" % f["eq"])
        lines.append("")
        kullanilan_girdi = ", ".join(
            "%s = %s" % (k, problem._oku_sayi(v))
            for k, v in sorted(girdiler.items()) if k != sym)
        if kullanilan_girdi:
            lines.append("%s %s" % (L("Yerine koyarsak:", "Substituting:"),
                                    kullanilan_girdi))
            lines.append("")
        isaret = "→ **%s = %s %s**" % (sym, problem._oku_sayi(deger),
                                       f["vars"][sym][2])
        lines.append(isaret)
        lines.append("")

    # OLCEK DENETIMI: gunluk olcekli bir soruya kozmik bir cevap
    # verilmemeli. Olculdu: "surtunme katsayisi 0.5 olan 50 m yaricapli
    # virajda maksimum hiz" sorusunda zincir `r = 50 m`i SCHWARZSCHILD
    # yaricapi sanip 3,4×10²⁸ kg'lik bir kutle uydurdu ve arabaya
    # 2,1×10⁸ m/s (0,7c) dedi. Boyle bir cevap, cevapsiz kalmaktan
    # kotudur — ogrenciyi yanlisa goturur.
    if not _olcek_makul(soru, hedef_f, hedef, son):
        return None

    lines.append("## `%s` = **%s %s**"
                 % (hedef, problem._oku_sayi(son),
                    hedef_f["vars"][hedef][2]))
    lines.append("")
    lines.append("_" + L(
        "Her adım SymPy ile çözüldü ve fiziksel olarak denetlendi.",
        "Every step was solved symbolically and checked for plausibility.")
        + "_")
    return "\n".join(lines)
