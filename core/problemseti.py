# -*- coding: utf-8 -*-
"""Ders kitabi tarzi PROBLEM SETI ve ispat modu.

Kullanicinin ikinci onceligi: "Griffiths/Sakurai/Serway'in yerini tutmaz —
problem secimi, ispat titizligi, alistirma yogunlugu ayri bir sey."

Bir ders kitabinin bolum sonu, rastgele sorular yigini degildir:

    * Zorluk KADEMELIDIR: once tanim/dogrudan uygulama, sonra cok adimli,
      en sonda kavramsal ya da turetim sorusu.
    * Her soru bir SEYI sinar; sorunun neyi olctugu bellidir.
    * Cozumler tam yazilir, sonuc mertebesiyle birlikte yorumlanir.

Bu modul konudan yola cikip boyle bir set uretir. Sayilar ve cozumler
dogrulanmis formul tabanindan gelir ve SymPy ile hesaplanir; kavramsal
sorular ise konunun kendi anlatimindan turetilir.

Ispat modu ("goster ki", "ispatla") ayri bir bicimdir: verilenler,
varsayimlar, adimlar ve sonucun NEREDE gecerli oldugu ayri ayri yazilir.
Bir turetimde en cok atlanan sey, varsayimlarin ne zaman bozuldugudur.
"""
import random
import re

from . import formulas, knowledge, nlu


ZORLUK = ("kolay", "orta", "zor")


def _konu_bul(sorgu):
    """Sorgudan cekirdek konuyu ve ilgili formulleri bul."""
    kv = knowledge.search(sorgu, limit=1)
    konu = kv[0][1] if kv and kv[0][0] >= 20 else None
    vurus = [f for _s, f in formulas.search(sorgu, limit=12)
             if not f.get("uretilmis")]
    if konu:
        # Konunun kendi bagintilarini da havuza kat
        for eq in (konu.get("eqs") or []):
            for f in formulas.FORMULAS:
                if f["eq"].replace(" ", "") == str(eq).replace(" ", ""):
                    if f not in vurus:
                        vurus.append(f)
    return konu, vurus


def _kavramsal_sorular(konu, lang="tr"):
    """Konunun anlatimindan KAVRAMSAL soru cikar.

    Metinde vurgulanmis (BUYUK harfli ya da **kalin**) ifadeler, yazarin
    "burasi onemli" dedigi yerlerdir; iyi bir kavram sorusu tam da
    oralara dokunur.
    """
    if not konu:
        return []
    govde = konu["tr"] if lang == "tr" else konu["en"]
    sorular = []
    for baslik in re.findall(r"\*\*([^*]{4,60})\*\*", govde):
        b = baslik.strip().rstrip(":")
        # Basindaki numaralandirmayi at: "**2. Yasa:**" -> "Yasa".
        # Olculdu: termodinamik konusunda tum vurgular numarali oldugu
        # icin hicbir kavram sorusu uretilemiyordu.
        b = re.sub(r"^\d+[\.\)]\s*", "", b).strip().rstrip(":")
        if not b or len(b.split()) > 6 or len(b) < 4:
            continue
        if b.lower() in ("yasa", "law", "not", "note", "ornek", "example"):
            continue
        sorular.append(b)
    out = []
    ad = konu["tr_title"] if lang == "tr" else konu["en_title"]
    kaliplar = ([
        "**%s** kavramını kendi cümlelerinizle açıklayın ve %s ile "
        "ilişkisini kurun.",
        "**%s** olmasaydı ne değişirdi? Fiziksel sonucunu tartışın.",
        "**%s** ile ilgili yaygın bir yanlış anlamayı yazıp düzeltin.",
    ] if lang == "tr" else [
        "Explain **%s** in your own words and relate it to %s.",
        "What would change if **%s** did not hold?",
        "State and correct a common misconception about **%s**.",
    ])
    for i, s in enumerate(sorular[:3]):
        kalip = kaliplar[i % len(kaliplar)]
        out.append(kalip % ((s, ad) if kalip.count("%s") == 2 else (s,)))

    # Vurgulanmis kavram cikmadiysa (ornegin tum basliklar "1. Yasa",
    # "2. Yasa" ise) konunun kendi BAGINTILARINDAN kavram sorusu
    # uretiyoruz — olculdu: termodinamikte hic kavramsal soru
    # gelmiyordu.
    if not out:
        eqs = konu.get("eqs") or []
        for eq in eqs[:2]:
            out.append(
                ("`%s` bağıntısında hangi büyüklük artarsa sonuç azalır? "
                 "Fiziksel sebebini açıklayın." % eq) if lang == "tr" else
                ("In `%s`, which quantity decreases the result when "
                 "increased, and why?" % eq))
        out.append(
            ("**%s** konusunun en çok karıştırılan iki kavramını yazıp "
             "aralarındaki farkı bir cümleyle açıklayın." % ad)
            if lang == "tr" else
            ("Name the two most confused concepts in **%s** and "
             "distinguish them." % ad))
        out.append(
            ("**%s** konusundaki bir sonucun günlük hayatta gözlenebildiği "
             "bir örnek verin ve hangi bağıntının işlediğini söyleyin." % ad)
            if lang == "tr" else
            ("Give an everyday observation explained by **%s**." % ad))
    return out


def uret(sorgu, lang="tr", adet=6):
    """Kademeli problem seti uret. Metin ya da None."""
    from . import brain          # dairesel ice aktarmayi geciktiriyoruz
    tr = lang == "tr"
    konu, havuz = _konu_bul(sorgu)
    if not havuz and not konu:
        return None

    rng = random.Random()
    ad = (konu["tr_title"] if tr else konu["en_title"]) if konu else sorgu
    lines = ["### %s — %s" % (ad, "Problem Seti" if tr else "Problem Set"),
             ""]
    lines.append(("Kademeli düzenlenmiştir: önce doğrudan uygulama, sonra "
                  "çok adımlı, en sonda kavramsal. Sayılar her üretimde "
                  "değişir." if tr else
                  "Graded: direct application, then multi-step, then "
                  "conceptual. Numbers change on each run."))
    lines.append("")

    numara = 0
    # ── 1. Dogrudan uygulama: tek baginti ──────────────────────────────
    lines.append("#### " + ("A. Doğrudan uygulama" if tr
                            else "A. Direct application"))
    lines.append("")
    basit = 0
    for f in havuz:
        if basit >= max(2, adet // 3):
            break
        p = brain._problem_uret(f, lang, rng, numara=numara + 1)
        if p:
            numara += 1
            basit += 1
            lines.append(p)
            lines.append("")
    if not basit:
        lines.append("_" + ("Bu konuda sayısal problem üretilemedi." if tr
                            else "No numeric problems available.") + "_")
        lines.append("")

    # ── 2. Cok adimli ──────────────────────────────────────────────────
    lines.append("#### " + ("B. Çok adımlı" if tr else "B. Multi-step"))
    lines.append("")
    if len(havuz) >= 2:
        f1, f2 = havuz[0], havuz[1]
        ortak = set(f1["vars"]) & set(f2["vars"])
        numara += 1
        if ortak:
            k = sorted(ortak)[0]
            lines.append(
                ("**%d.** `%s` ve `%s` bağıntılarını birlikte kullanın: "
                 "birinden `%s` büyüklüğünü bulup diğerinde yerine koyun. "
                 "Ara sonucun birimini de yazın." % (
                     numara, f1["eq"], f2["eq"], k)) if tr else
                ("**%d.** Combine `%s` and `%s` through `%s`."
                 % (numara, f1["eq"], f2["eq"], k)))
        else:
            lines.append(
                ("**%d.** `%s` bağıntısındaki her değişkeni iki katına "
                 "çıkarırsanız sonuç kaç katına çıkar? Her değişken için "
                 "ayrı ayrı yanıtlayın." % (numara, f1["eq"])) if tr else
                ("**%d.** How does `%s` scale when each variable doubles?"
                 % (numara, f1["eq"])))
        lines.append("")
        numara += 1
        lines.append(
            ("**%d.** `%s` bağıntısını boyut analiziyle denetleyin: iki "
             "tarafın boyutu tutuyor mu? Tutmasaydı ne anlama gelirdi?"
             % (numara, f1["eq"])) if tr else
            ("**%d.** Check `%s` by dimensional analysis."
             % (numara, f1["eq"])))
        lines.append("")

    # ── 3. Kavramsal ───────────────────────────────────────────────────
    kavramsal = _kavramsal_sorular(konu, lang)
    if kavramsal:
        lines.append("#### " + ("C. Kavramsal" if tr else "C. Conceptual"))
        lines.append("")
        for s in kavramsal:
            numara += 1
            lines.append("**%d.** %s" % (numara, s))
            lines.append("")
        lines.append("_" + (
            "Kavramsal soruların tek bir doğru cevabı yoktur; yanıtınızı "
            "yazıp `%s anlat` ile karşılaştırın." % ad.lower()
            if tr else
            "Conceptual questions have no single answer; compare with the "
            "topic explanation.") + "_")

    if numara == 0:
        return None
    return "\n".join(lines)


# ── Ispat / "goster ki" modu ────────────────────────────────────────────────

_ISPAT = re.compile(
    r"\b(ispatla|ispat et|kanitla|goster ki|gosteriniz|turetiniz|"
    r"elde ediniz|prove|show that|derive that|demonstrate)\b", re.I)


def ispat_istegi_mi(soru):
    return bool(_ISPAT.search(soru or ""))


def ispat(soru, lang="tr"):
    """Turetimi ISPAT bicimiyle sun: varsayimlar ayri yazilir.

    Bir turetimde en cok atlanan sey varsayimlardir; sonuc dogru
    gorunur ama nerede gecerli oldugu bilinmez. Burada varsayimlar
    ayri bir baslikta durur.
    """
    if not ispat_istegi_mi(soru):
        return None
    from . import brain, turetim, lagrange
    tr = lang == "tr"

    govde = None
    # Once bilinen turetim zincirleri, sonra Lagrange, sonra cebirsel
    try:
        _a, zincir = turetim.zincir_bul(soru)
        if zincir:
            govde = turetim.zincir_calistir(zincir, lang)
    except Exception:
        pass
    if not govde:
        # Ispat isteniyorsa "lagrange" kelimesi gecmese de Lagrange
        # yontemi mesrudur: sistem tanidik ise hareket denklemini oradan
        # turetiriz. Olculdu: "sarkacin periyodunu ispatla" sorusu
        # fotonik kristal makalesine dusuyordu.
        try:
            sis = lagrange.sistem_bul(soru)
            if sis:
                govde = lagrange.turet("lagrange " + soru, lang)
        except Exception:
            govde = None
    if not govde:
        try:
            resp = brain.h_turetim(soru, lang, {})
            aday = resp.text if resp else None
            # Korpus metni ISPAT degildir. Turetim gorunumlu olmali.
            if aday and not any(x in aday for x in (
                    "Makaleleri incelerken", "Guncel arastirmalardan",
                    "Makalelerden ogrendigim", "From current research")):
                govde = aday
        except Exception:
            govde = None
    if not govde:
        return None

    varsayim = _varsayimlar(soru, lang)
    lines = [govde, ""]
    if varsayim:
        lines.append("**" + ("Kullanılan varsayımlar" if tr
                             else "Assumptions used") + "**")
        lines.append("")
        for v in varsayim:
            lines.append("- %s" % v)
        lines.append("")
        lines.append("_" + (
            "Bir türetim, ancak varsayımları geçerli olduğu yerde "
            "geçerlidir. Sınav sorusunda hangi varsayımın bozulduğunu "
            "sormak yaygındır." if tr else
            "A derivation holds only where its assumptions hold.") + "_")
    return "\n".join(lines)


# Hangi ifade hangi varsayimi ima eder? Bu FIZIK bilgisidir.
_VARSAYIM_TABLOSU = [
    (r"sarkac|pendulum",
     ["Salınım genliği küçük (sin θ ≈ θ), aksi hâlde periyot genliğe bağlı olur",
      "İp esnemez ve kütlesiz",
      "Hava sürtünmesi yok"]),
    (r"serbest dus|free fall|dusen cisim",
     ["Hava direnci ihmal ediliyor",
      "g sabit kabul ediliyor (yükseklik, Dünya yarıçapına göre küçük)"]),
    (r"ideal gaz|ideal gas",
     ["Moleküller arası çekim yok",
      "Molekül hacmi kap hacmine göre ihmal edilebilir",
      "Çarpışmalar esnek"]),
    (r"carnot|isi makinesi|heat engine",
     ["Tüm süreçler tersinir",
      "Çalışma maddesi ideal gaz",
      "Kaynak sıcaklıkları sabit"]),
    (r"bohr|hidrojen atomu",
     ["Tek elektron (çok elektronlu atomlarda geçersiz)",
      "Çekirdek sonsuz kütleli kabul ediliyor",
      "Yörünge klasik, açısal momentum kuantalı — tam kuantum kuramı değil"]),
    (r"kacis hizi|escape velocity",
     ["Atmosfer sürtünmesi yok",
      "Cisim yalnızca tek gök cisminin çekimi altında",
      "Dönme etkisi ihmal ediliyor"]),
    (r"lagrange|euler",
     ["Kısıtlar holonom (koordinatlarla ifade edilebilir)",
      "Sürtünme gibi korunumsuz kuvvetler yok",
      "Küçük salınım varsayılıyorsa ayrıca belirtilmeli"]),
    (r"esnek carpisma|elastic collision",
     ["Hem momentum hem kinetik enerji korunuyor",
      "Dış kuvvet yok (çarpışma süresi çok kısa)"]),
    (r"ohm|devre|circuit",
     ["İletken ohmik (direnç sıcaklıkla değişmiyor)",
      "Bağlantı kabloları dirençsiz",
      "Kaynak iç direnci ihmal ediliyor"]),
]


def _varsayimlar(soru, lang="tr"):
    n = nlu.norm(soru or "")
    out = []
    for kalip, liste in _VARSAYIM_TABLOSU:
        if re.search(kalip, n):
            out.extend(liste)
    if not out:
        out = ["Sürtünme ve enerji kaybı ihmal ediliyor",
               "Büyüklükler klasik mertebede (göreli ve kuantum "
               "düzeltmeler gerekmez)"]
    return out[:5]
