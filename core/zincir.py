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
        return [(d, b, e) for e, d, b in (nlu.adli_degerler(soru) or [])]
    except Exception:
        return []


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
    for _skor, f in adaylar:
        try:
            okunan = nlu.formul_degerleri(f, soru) or {}
        except Exception:
            continue
        for sym, (deger, birim) in okunan.items():
            if sym in bilinen or deger is None:
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
        try:
            h = problem.hedef_tahmin(f, soru)
        except Exception:
            h = None
        if h and _uyar(bilinen, h, f["vars"][h][2]) is None:
            anahtar = (h, f["id"])
            if anahtar not in gorulen:
                gorulen.add(anahtar)
                out.append((h, f))
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
    pozitif = [x for x in gercel if x >= 0]
    deger = (pozitif or gercel)[0]
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

    lines.append("## `%s` = **%s %s**"
                 % (hedef, problem._oku_sayi(son),
                    hedef_f["vars"][hedef][2]))
    lines.append("")
    lines.append("_" + L(
        "Her adım SymPy ile çözüldü ve fiziksel olarak denetlendi.",
        "Every step was solved symbolically and checked for plausibility.")
        + "_")
    return "\n".join(lines)
