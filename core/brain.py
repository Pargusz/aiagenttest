"""ParguszPhysics beyni: soruyu anlar, dogru motoru calistirir, cevabi yazar.

Akis:
  mesaj -> dil tespiti -> niyet siniflandirma -> ilgili motor
        -> (gerekirse) ogrenilmis bilgi + canli internet aramasi
        -> Turkce/Ingilizce bicimlendirilmis cevap
"""
import json
import random
import re
import time

from . import (bosluk, canli, config, db, nlu, ogretim, problem, turetim, units, solver, formulas, knowledge,
               retrieval, matlab, learner, curriculum, profile, belge,
               anlama, dogrulama, bagintilar, sentez, dil, baglam)


def L(lang, tr, en):
    return tr if lang == "tr" else en


class Response(object):
    def __init__(self, text, kind="text", extra=None):
        self.text = text
        self.kind = kind
        self.extra = extra or {}

    def as_dict(self):
        d = {"text": self.text, "kind": self.kind}
        d.update(self.extra)
        return d


# ============================================================== yardimcilar
def _fmt_sources(items, lang, limit=5):
    if not items:
        return ""
    out = [L(lang, "\n**Kaynaklar:**", "\n**Sources:**")]
    for p in items[:limit]:
        title = (p.get("title") or "").strip()
        if len(title) > 130:
            title = title[:127] + "..."
        url = p.get("url") or ""
        src = p.get("source", "")
        year = (p.get("published") or "")[:4]
        rozet = []
        if p.get("hakemli") == 1:
            rozet.append(L(lang, "hakemli", "peer-reviewed"))
        elif p.get("hakemli") == 0:
            rozet.append(L(lang, "önbaskı", "preprint"))
        if (p.get("atif") or -1) > 0:
            rozet.append(L(lang, "%d atıf", "%d citations") % p["atif"])
        meta = " · ".join(x for x in ([src, year] + rozet) if x)
        if url:
            out.append("- [%s](%s) <span class='meta'>%s</span>" % (title, url, meta))
        else:
            out.append("- %s <span class='meta'>%s</span>" % (title, meta))
    return "\n".join(out)


# "teorisi", "yasasi" gibi sozcukler her baslikta gecer; ortak olmalari
# iki metnin ayni konudan bahsettigini gostermez.
_GENEL_SOZCUK = set("""teori teorisi kuram kurami yasa yasasi kanun kanunu
ilke ilkesi denklem denklemi formul formulu olay olayi etki etkisi
sistem sistemi model modeli analiz analizi fizik fizigi bilim bilimi
theory law equation formula effect system model analysis physics science
principle general genel temel basic""".split())


def _relevant(query, text, min_overlap=1):
    """Getirilen metnin sorguyla gercekten ilgili olup olmadigini denetle."""
    qw = set(w for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{3,}", nlu.norm(query)))
    tw = set(w for w in re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]{3,}", nlu.norm(text)))
    # Islev kelimeleri ("bir", "icindeki", "olur") ortusme sayilmamali;
    # yoksa alakasiz bir cevap "ilgili" gorunur.
    from .learner import STOP as _STOP
    qw -= _GENEL_SOZCUK | _STOP
    tw -= _GENEL_SOZCUK | _STOP
    if not qw:
        return False
    # "ozgul isi" sorgusuna "ozgul itici kuvvet" donmemeli: iki anlamli
    # kelimesi olan sorguda tek kelime ortakligi yeterli sayilmaz.
    gerekli = max(min_overlap, 2 if len(qw) >= 2 else 1)
    return len(qw & tw) >= gerekli


def _si_convert(value, unit):
    """Degeri SI'ye cevir; birim yoksa oldugu gibi birak."""
    if not unit:
        return value, None
    v, dim = units.to_si(value, unit)
    if v is None:
        return value, None
    return v, dim


# ============================================================== niyet islevleri
def h_ogrendiklerim(msg, lang, ctx):
    """Kullanicinin sorularindan ne ogrenildigini goster."""
    metin = bosluk.rapor(lang)
    try:
        from . import genisleme as _gen, sentez as _sentez
        g = _gen.durum()
        ek = ("\n\n**Şu ana kadar kazandıklarım:** %d yol haritası "
              "(%d tanesini makalelerden ürettim) · %d konu "
              "(%d çekirdek + %d öğrenilmiş) · %d formül "
              "(%d tanesini kendim türettim)"
              if lang == "tr" else
              "\n\n**Gained so far:** %d roadmaps (%d generated) · "
              "%d topics (%d core + %d learned) · %d formulas (%d derived)")
        turetilmis = _turetilmis_formul()
        try:
            from . import sentezbilgi as _sb
            si = _sb.istatistik()
            if si.get("toplam"):
                uz = si.get("uzlasma") or {}
                ko = si.get("kopru") or {}
                kalip = ("\n\n**Makaleleri birleştirerek ürettiğim bilgi:** "
                         "%d uzlaşan bulgu (ortalama %s bağımsız makale "
                         "desteği) · %d kavram köprüsü"
                         if lang == "tr" else
                         "\n\n**Knowledge derived by combining papers:** "
                         "%d consensus findings (avg %s sources) · %d links")
                metin += kalip % (uz.get("sayi", 0), uz.get("ort_kanit", 0),
                                  ko.get("sayi", 0))
        except Exception:
            pass
        metin += ek % (g["yol_haritasi_toplam"], g["yol_haritasi_uretilmis"],
                       g["cekirdek_konu"] + g["ogrenilen_konu"],
                       g["cekirdek_konu"], g["ogrenilen_konu"],
                       g["formul"], turetilmis)
    except Exception:
        pass
    return Response(metin, kind="status")


def h_selam(msg, lang, ctx):
    # Once dogal karsilik denenir: "merhaba, ben Polat" diyene katalog
    # okumak yerine insan gibi cevap vermek gerekir. Model yoksa asagidaki
    # kural tabanli metin kullanilir.
    #
    # AMA kuru bir "merhaba"ya kendimizi TANITIRIZ: kullanici kiminle
    # konustugunu ve neler yapabildigimi bilmeli. Dogal sohbet, selamin
    # yaninda baska bir sey de soylendiginde devreye girer ("merhaba,
    # ben Polat", "selam nasilsin").
    _kuru_selam = bool(re.match(
        r"^\s*(merhaba|selam|slm|gunaydin|hey|hi|hello|"
        r"iyi (gunler|aksamlar|geceler))[\s!.,]*$", nlu.norm(msg or "")))
    if dil.MODEL.kurulu_mu() and not _kuru_selam:
        try:
            ad = (ctx.get("profil") or {}).get("ad")
            dogal = dil.MODEL.sohbet(msg, lang, ctx.get("history"), ad)
            if dogal and 10 < len(dogal) < 700:
                return Response(dogal, kind="chat")
        except Exception:
            pass
    if lang == "tr":
        t = ("Merhaba! Ben **ParguszPhysics**. Fizik konularinda hesap yapar, "
             "konu anlatir, formul cozer ve MATLAB kodu yazarim.\n\n"
             "Su anda ogrenmis oldugum bilgi: **%(makale)s makale ozeti**, "
             "**%(kavram)s kavram**, **%(baglanti)s kavram baglantisi**.\n\n"
             "Sunlari deneyebilirsin:\n"
             "- `kinetik enerji formulu`\n"
             "- `m=2 kg v=10 m/s kinetik enerji`\n"
             "- `x^2*sin(x) turevi`\n"
             "- `90 km/h kac m/s`\n"
             "- `kuantum dolanikligi nedir`\n"
             "- `sonumlu osilator icin matlab kodu`\n"
             "- `karanlik madde hakkinda makale bul`")
    else:
        t = ("Hello! I'm **ParguszPhysics**. I calculate physics problems, explain "
             "topics, solve formulas and write MATLAB code.\n\n"
             "Currently learned: **%(makale)s paper abstracts**, "
             "**%(kavram)s concepts**, **%(baglanti)s concept links**.\n\n"
             "Try:\n"
             "- `kinetic energy formula`\n"
             "- `m=2 kg v=10 m/s kinetic energy`\n"
             "- `derivative of x^2*sin(x)`\n"
             "- `90 km/h to m/s`\n"
             "- `what is quantum entanglement`\n"
             "- `matlab code for damped oscillator`\n"
             "- `find papers on dark matter`")
    s = db.stats()
    metin = t % {"makale": "{:,}".format(s["makale"]),
                 "kavram": "{:,}".format(s["kavram"]),
                 "baglanti": "{:,}".format(s["baglanti"])}

    # Kisiyi taniyorsak selamlamayi kisisellestir
    kisisel = profile.greeting_line(lang)
    if kisisel:
        ilk_satir = ("Merhaba! Ben **ParguszPhysics**."
                     if lang == "tr" else "Hello! I'm **ParguszPhysics**.")
        yeni_ilk = kisisel + (" Ben **ParguszPhysics**." if lang == "tr"
                              else " I'm **ParguszPhysics**.")
        if profile.name():
            metin = metin.replace(ilk_satir, yeni_ilk, 1)
        else:
            metin = kisisel + "\n\n" + metin
    return Response(metin)


def belge_raporu(s, lang="tr"):
    """Cozumlenen belge icin okunabilir rapor uret."""
    tr = lang == "tr"
    ad = s.get("dosya", "belge")

    if s.get("resim"):
        m = s.get("meta", {})
        satir = ["### " + (("Resim: %s" % ad) if tr else ("Image: %s" % ad)), ""]
        bilgi = []
        if m.get("boyut"):
            bilgi.append(("Boyut: **%s** piksel" if tr else "Size: **%s** px")
                         % m["boyut"])
        if m.get("bicim"):
            bilgi.append(("Biçim: **%s**" if tr else "Format: **%s**") % m["bicim"])
        if bilgi:
            satir.append(" · ".join(bilgi))
            satir.append("")
        satir.append(L(lang,
            "Resmi kaydettim, ancak **içindeki metni okuyamıyorum**: bu "
            "bilgisayarda bir OCR (görüntüden yazı tanıma) motoru kurulu değil. "
            "Grafiğin veya formülün içeriğini yazıyla anlatırsanız üzerinde "
            "hesap yapabilir, yorumlayabilirim.",
            "I've saved the image, but **I can't read text inside it**: no OCR "
            "engine is installed on this machine. Describe the plot or formula "
            "in text and I can compute with it or comment on it."))
        return "\n".join(satir)

    if s.get("bos"):
        return L(lang,
                 "**%s** okundu ama içinden metin çıkaramadım. PDF taranmış "
                 "görüntülerden oluşuyorsa metin katmanı yoktur; bu durumda "
                 "OCR gerekir ve bu bilgisayarda kurulu değil." % ad,
                 "I read **%s** but found no extractable text. If the PDF is a "
                 "scan, it has no text layer and would need OCR, which isn't "
                 "installed here." % ad)

    L_ = lambda a, b: a if tr else b
    baslik = s.get("baslik") or ad
    lines = ["### " + L_("Belge çözümlemesi", "Document analysis"), ""]
    lines.append("**%s**" % baslik)
    lines.append("")

    # Künye
    kunye = []
    m = s.get("meta", {})
    if m.get("sayfa"):
        kunye.append(L_("%d sayfa", "%d pages") % m["sayfa"])
    kunye.append(L_("%s kelime", "%s words") % "{:,}".format(s.get("kelime", 0)))
    if m.get("yazar"):
        kunye.append(L_("Yazar: %s", "Author: %s") % m["yazar"][:120])
    if s.get("yil"):
        kunye.append(L_("Yıl: %s", "Year: %s") % s["yil"])
    if s.get("doi"):
        kunye.append("DOI: [%s](https://doi.org/%s)" % (s["doi"], s["doi"]))
    if s.get("arxiv"):
        kunye.append("[arXiv:%s](https://arxiv.org/abs/%s)"
                     % (s["arxiv"], s["arxiv"]))
    lines.append("<span class='meta'>" + " · ".join(kunye) + "</span>")
    if m.get("kesildi"):
        lines.append("")
        lines.append(L_("_Belge çok uzun olduğu için ilk bölümü işlendi._",
                        "_The document is long; only the first part was processed._"))
    lines.append("")

    if s.get("bolumler"):
        lines.append("**" + L_("Bölümler:", "Sections:") + "** "
                     + " → ".join(s["bolumler"]))
        lines.append("")

    if s.get("ozet"):
        lines.append("#### " + L_("Ne anlatıyor", "What it says"))
        lines.append("")
        for c in s["ozet"]:
            lines.append("- " + c)
        lines.append("")

    if s.get("terimler"):
        lines.append("**" + L_("Öne çıkan terimler:", "Key terms:") + "** "
                     + ", ".join("`%s`" % t for t, _ in s["terimler"][:10]))
        lines.append("")

    if s.get("kavramlar"):
        lines.append("**" + L_("Bildiğim kavramlarla bağlantısı:",
                               "Links to concepts I know:") + "** "
                     + ", ".join(s["kavramlar"]))
        lines.append("")

    if s.get("formuller"):
        lines.append("#### " + L_("Bulunan bağıntılar", "Relations found"))
        lines.append("")
        lines.append("```\n%s\n```" % "\n".join(s["formuller"]))
        lines.append("")

    if s.get("sayisal"):
        lines.append("**" + L_("Geçen sayısal değerler:", "Numerical values:")
                     + "** " + ", ".join("`%s`" % x for x in s["sayisal"]))
        lines.append("")

    if not s.get("fizik"):
        lines.append(L_("> Bu belge fizikle doğrudan ilgili görünmüyor; yine de "
                        "çözümledim ve aranabilir hale getirdim.",
                        "> This document doesn't look directly physics-related; "
                        "I analysed and indexed it anyway."))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(L_(
        "Belgeyi belleğime ekledim — artık `%s` diye arayabilir, içeriği "
        "üzerine soru sorabilirsiniz. Şunları da isteyebilirsiniz: "
        "`bu belgeyi özetle`, `buradaki formülleri açıkla`, "
        "`bu konuda makale bul`." % (baslik[:40]),
        "I've added it to my memory — you can now search `%s` and ask about "
        "its content. You can also ask: `summarise this document`, "
        "`explain the formulas here`, `find papers on this`." % (baslik[:40])))
    return "\n".join(lines)


def belge_isle(path, dosya_adi, lang="tr", session="default"):
    """Yuklenen dosyayi coz, ogren ve rapor dondur."""
    try:
        s = belge.cozumle(path, dosya_adi, lang)
    except belge.BelgeHatasi as e:
        return Response(L(lang, "Belgeyi okuyamadım: %s" % e,
                          "I couldn't read the document: %s" % e),
                        kind="document")
    ogrenildi = False
    try:
        ogrenildi = belge.ogren(s)
    except Exception:
        pass
    rapor = belge_raporu(s, lang)
    konu = s.get("baslik") or dosya_adi
    try:
        profile.note_interest(konu[:60])
    except Exception:
        pass
    _save_turn(session, L(lang, "[belge yüklendi: %s]" % dosya_adi,
                          "[document uploaded: %s]" % dosya_adi),
               rapor, "belge", subject=konu[:80])
    return Response(rapor, kind="document",
                    extra={"ogrenildi": ogrenildi, "dosya": dosya_adi})


def _konu_ozeti(ad, lang, cumle=3):
    """Bir konu icin kisa tanim + temel bagintilar dondur."""
    hits = knowledge.search(ad, limit=1)
    if hits and hits[0][0] >= 20:
        t = hits[0][1]
        govde = t["tr"] if lang == "tr" else t["en"]
        return {
            "baslik": t["tr_title"] if lang == "tr" else t["en_title"],
            "ozet": retrieval.summarize([govde], query=ad, max_sentences=cumle),
            "eqs": t["eqs"][:4],
            "kaynak": "cekirdek",
        }
    kav = retrieval.search_concepts(ad, limit=1, lang=lang) or \
        retrieval.search_concepts(ad, limit=1)
    if kav:
        k = kav[0]
        return {
            "baslik": k["name"],
            "ozet": retrieval.summarize([k.get("extract") or ""], query=ad,
                                        max_sentences=cumle),
            "eqs": [],
            "kaynak": "kavram",
        }
    fh = formulas.search(ad, limit=1)
    if fh and fh[0][0] >= 25:
        f = fh[0][1]
        return {"baslik": f["tr"] if lang == "tr" else f["en"],
                "ozet": [], "eqs": [f["eq"]], "kaynak": "formul"}
    return None


def h_karsilastir(msg, lang, ctx):
    """'X ile Y arasindaki fark nedir' — iki konuyu yan yana koy."""
    taraflar = (ctx.get("anlama") or {}).get("taraflar")
    if not taraflar:
        taraflar = anlama.karsilastirma_taraflari(msg)
    if not taraflar:
        return h_konu(msg, lang, ctx)
    a, b = taraflar
    A, B = _konu_ozeti(a, lang), _konu_ozeti(b, lang)
    if not A and not B:
        return h_konu(msg, lang, ctx)

    tr = lang == "tr"
    lines = ["### " + (("%s ile %s karşılaştırması" % (a, b)) if tr
                       else ("%s vs %s" % (a, b))), ""]

    for ad, X in ((a, A), (b, B)):
        lines.append("#### " + (X["baslik"] if X else ad))
        lines.append("")
        if X and X["ozet"]:
            lines.append(" ".join(X["ozet"]))
        elif X and X["eqs"]:
            lines.append(L(lang, "Bağıntı: `%s`", "Relation: `%s`") % X["eqs"][0])
        else:
            lines.append(L(lang,
                           "_Bu konuda ayrıntılı bilgim yok; öğrenme motoru "
                           "çalıştıkça gelişecek._",
                           "_I don't have detail on this yet; it will improve as "
                           "the learning engine runs._"))
        if X and X["eqs"]:
            lines.append("")
            lines.append(L(lang, "**Bağıntılar:** ", "**Relations:** ")
                         + ", ".join("`%s`" % e for e in X["eqs"]))
        lines.append("")

    # Ortak ve ayirt edici noktalar: kavram grafinden
    ortak = []
    try:
        ra = {r["name"] for r in retrieval.related_concepts(a, limit=12)}
        rb = {r["name"] for r in retrieval.related_concepts(b, limit=12)}
        ortak = sorted(ra & rb)[:6]
    except Exception:
        pass
    if ortak:
        lines.append("---")
        lines.append("")
        lines.append(L(lang, "**Ortak bağlam:** %s", "**Shared context:** %s")
                     % ", ".join(ortak))
        lines.append("")

    lines.append(L(lang,
                   "Tek tek derinleşmek için `%s nedir` ya da `%s nedir` "
                   "yazabilirsiniz." % (a, b),
                   "For depth on either, ask `what is %s` or `what is %s`."
                   % (a, b)))
    return Response("\n".join(lines), kind="compare",
                    extra={"konu_etiketi": "%s / %s" % (a, b)})


def h_neden(msg, lang, ctx):
    """'... neden ...' — nedensel aciklama arar."""
    konu = nlu.strip_command_words(
        re.sub(r"\b(neden|nicin|niye|sebebi|nedeni|why|what causes|"
               r"reason for)\b", " ", msg, flags=re.I))
    konu = re.sub(r"\s+", " ", konu).strip(" ?.!,") or msg

    lines = ["### " + L(lang, "Neden: %s", "Why: %s") % konu[:60], ""]
    bulundu = False

    # 1) Cekirdek anlatimda nedensel cumleler
    # Soru kelimeleri atilinca geriye cok dar bir parca kalabiliyor
    # ("neden 4s 3d'den once doluyor" -> "4s 3d'den once doluyor").
    # Bulamazsak TAM mesajla da ariyoruz.
    hits = knowledge.search(konu, limit=1)
    if not (hits and hits[0][0] >= 20):
        tam = knowledge.search(msg, limit=1)
        if tam and tam[0][0] >= 20:
            hits = tam
    if hits and hits[0][0] >= 20:
        t = hits[0][1]
        govde = t["tr"] if lang == "tr" else t["en"]
        nedensel = [c for c in retrieval.split_sentences(govde)
                    if re.search(r"\b(çünkü|cunku|nedeni|sebebi|yüzünden|"
                                 r"kaynaklan|yol aç|dolayı|sonucu|because|"
                                 r"since|due to|reason|causes|leads to|"
                                 r"arises from|follows from)\b", c, re.I)]
        if len(nedensel) >= 2:
            bulundu = True
            for c in nedensel[:4]:
                lines.append("- " + c)
            lines.append("")
        elif hits[0][0] >= 40:
            # Cekirdekte GUCLU eslesen bir anlatim var ama icinde "cunku"
            # gecen cumle yok. Bag sozcugu aramak yerine anlatimin
            # KENDISINI vermek dogru cevaptir. Olculdu: "kuantum
            # etkilerini neden gunluk hayatta gormuyoruz" sorusuna
            # Karsilik Gelme Ilkesi anlatimindan tek bir cumle
            # cekiliyor, gerisi alakasiz makale alintisi oluyordu.
            bulundu = True
            lines.append("**" + (t["tr_title"] if lang == "tr"
                                 else t["en_title"]) + "**")
            lines.append("")
            lines.append(govde.strip())
            if t.get("eqs"):
                lines.append(L(lang, "\n**Temel bağıntılar:**",
                               "\n**Key relations:**"))
                for e in t["eqs"]:
                    lines.append("- `%s`" % e)
            lines.append("")
        elif nedensel:
            bulundu = True
            for c in nedensel[:4]:
                lines.append("- " + c)
            lines.append("")

    # 2) Ogrenilen iliskiler
    iliskiler = retrieval.relations(konu, limit=5)
    if iliskiler:
        bulundu = True
        lines.append(L(lang, "**Kurduğum nedensel bağlar:**",
                       "**Causal links I inferred:**"))
        for r in iliskiler:
            lines.append("- %s → *%s* → %s" % (r["a"], r["fiil"], r["b"]))
        lines.append("")

    # 3) Makalelerden nedensel bulgular
    b = retrieval.insights(konu, limit=4, turler=("iliski", "bulgu", "tanim"))
    if b:
        bulundu = True
        lines.append(L(lang, "**Makalelerden:**", "**From papers:**"))
        for x in b:
            c = x["cumle"]
            lines.append("- " + (c[:257] + "…" if len(c) > 260 else c))
        lines.append("")

    if not bulundu:
        # Once YAPILANDIRILMIS ders denenir. Olculdu: "tepkime hizi neden
        # sicaklikla artar" sorusunda cekirdek anlatim cevabi tastamam
        # iceriyordu, ama nedensel baglac aramasi tutmadigi icin
        # "dogrudan nedensel bir kaynak bulamadim" diye ozur beyani
        # basiliyordu. Cevap varken ozur dilemek yanlis.
        from . import ogretim as _ogr
        ders = _ogr.ders_ver(msg, lang)
        if ders:
            return Response(ders, kind="why",
                            extra={"ogretim": True, "konu_etiketi": konu[:60]})
        # Nedensel bilgi yoksa duz anlatima dus, ama bunu soyle
        r = h_konu(konu, lang, ctx)
        return Response(
            L(lang,
              "_Bu soruya doğrudan nedensel bir kaynak bulamadım; konuyu "
              "anlatarak yanıtlıyorum._\n\n",
              "_I couldn't find a direct causal source; answering by "
              "explaining the topic._\n\n") + r.text, kind="why")
    _metin = "\n".join(lines)
    # Tek bir cumle bulup kesmek "cevap verdim" saymak degildir.
    # Olculdu: "komutator nedir neden onemli" sorusuna 96 karakterlik
    # bir parca donuyordu; yapilandirilmis ders ise konuyu tam
    # anlatiyor.
    if len(_metin) < 400:
        from . import ogretim as _ogr2
        _ders = _ogr2.ders_ver(msg, lang)
        if _ders and len(_ders) > len(_metin):
            return Response(_ders, kind="why",
                            extra={"ogretim": True,
                                   "konu_etiketi": konu[:60]})
    return Response(_metin, kind="why",
                    extra={"konu_etiketi": konu[:60]})


def h_nasil(msg, lang, ctx):
    """'... nasil ...' — yontem/adim adim yanit."""
    konu = nlu.strip_command_words(
        re.sub(r"\b(nasil|ne sekilde|hangi yolla|adim adim|"
               r"how does|how do|how is|how to|in what way)\b",
               " ", msg, flags=re.I))
    konu = re.sub(r"\s+", " ", konu).strip(" ?.!,") or msg

    # Hesaplama sorusuysa formul yoluna gec: "carnot verimi nasil hesaplanir"
    if re.search(r"\b(hesapla\w*|bulun\w*|olcul\w*|olc\w*|calculat\w*|"
                 r"comput\w*|measur\w*|find|derive\w*|turet\w*)\b", msg, re.I):
        fh = formulas.search(konu, limit=1)
        if fh and fh[0][0] >= 25:
            f = fh[0][1]
            tr = lang == "tr"
            lines = ["### " + (L(lang, "%s nasıl hesaplanır", "How to compute %s")
                               % (f["tr"] if tr else f["en"])), ""]
            lines.append("## `%s`" % f["eq"])
            lines.append("")
            lines.append(L(lang, "**Adımlar**", "**Steps**"))
            lines.append("")
            lines.append("1. " + L(lang, "Bilinenleri belirleyin:",
                                   "Identify what you know:"))
            for sym, (t_, e_, u) in f["vars"].items():
                lines.append("   - `%s` — %s%s" % (sym, t_ if tr else e_,
                                                   (" [%s]" % u) if u else ""))
            lines.append("2. " + L(lang,
                                   "Birimleri SI'ye çevirin (ben otomatik çeviririm).",
                                   "Convert units to SI (I do this automatically)."))
            lines.append("3. " + L(lang, "Bilinmeyen için düzenleyin:",
                                   "Rearrange for the unknown:"))
            try:
                for sym in list(f["vars"])[:4]:
                    rr = formulas.symbolic_rearrange(f, sym)
                    if rr:
                        lines.append("   - `%s = %s`" % (sym, rr[0]))
            except Exception:
                pass
            lines.append("4. " + L(lang, "Değerleri yerine koyun.",
                                   "Substitute the values."))
            lines.append("")
            lines.append(L(lang, "Değerleri yazarsanız hesaplarım — örnek: `%s`",
                           "Give me values and I'll compute — e.g. `%s`")
                         % _example_query(f, lang))
            return Response("\n".join(lines), kind="howto",
                            extra={"konu_etiketi": f["tr"] if tr else f["en"]})

    lines = ["### " + L(lang, "Nasıl: %s", "How: %s") % konu[:60], ""]
    bulundu = False
    y = retrieval.insights(konu, limit=5, turler=("yontem", "bulgu"))
    if y:
        bulundu = True
        lines.append(L(lang, "**Makalelerde kullanılan yöntemler:**",
                       "**Methods used in the papers:**"))
        for x in y:
            c = x["cumle"]
            lines.append("- " + (c[:257] + "…" if len(c) > 260 else c))
        lines.append("")
    if not bulundu:
        return h_konu(konu, lang, ctx)
    lines.append(L(lang, "Konunun kendisini `%s nedir` ile alabilirsiniz." % konu,
                   "Ask `what is %s` for the topic itself." % konu))
    return Response("\n".join(lines), kind="howto",
                    extra={"konu_etiketi": konu[:60]})


def h_kendini_dogrula(msg, lang, ctx):
    """Formul tabanini iki bagimsiz sinamayla denetle ve raporla."""
    return Response(dogrulama.rapor(lang), kind="verify")


def _yabanci_alinti_yigini(metin, lang):
    """Cevap, kullanicinin dilinde olmayan ham alintilardan mi ibaret?

    "Aharonov-Bohm etkisi nedir" sorusuna madde madde Ingilizce makale
    cumleleri donuyordu. Bu bir cevap degil, malzeme yigini; dil modeli
    bunu kullanicinin dilinde toparlamali.
    """
    if lang != "tr":
        return False
    # Yalnizca DUZ YAZI madde isaretleri sayilir. Verilenler listesi
    # ("- m = 3 kg", "- v₀ = 12 m/s") bir alinti degildir; sayilinca
    # uretilmis problem sayfasi "yabanci yigin" sanilip dil modeline
    # yeniden yazdiriliyordu ve dogrulanmis sayilar kayboluyordu
    # (olculdu: "10 soru uret" istegi 10 yerine 0 yapilandirilmis soru).
    alintilar = []
    for s in metin.split("\n"):
        s = s.strip()
        if not s.startswith("- "):
            continue
        govde_s = s[2:]
        if "=" in govde_s or govde_s.startswith("`"):
            continue                      # baginti/deger satiri, cumle degil
        kelimeler = [w for w in re.findall(r"[A-Za-zçğıöşüÇĞİÖŞÜ]+", govde_s)
                     if len(w) >= 3]
        if len(kelimeler) >= 5:
            alintilar.append(s)
    if len(alintilar) < 2:
        return False
    govde = " ".join(alintilar)
    if len(govde) < 200:
        return False
    # Turkce'ye ozgu harfler ve sik kelimeler yoksa metin Turkce degildir
    turkce_iz = sum(govde.lower().count(h) for h in "çğıöşü")
    turkce_kelime = sum(1 for k in (" bir ", " ve ", " icin ", " ile ",
                                    " olarak ", " bu ", " daha ")
                        if k in govde.lower())
    return turkce_iz < 3 and turkce_kelime < 2


def _kaynak_ekle(resp, sorgu, lang):
    """Cevap korpustan beslendiyse altina kaynakca ekle."""
    if "Kaynaklar" in resp.text or "Sources" in resp.text:
        return
    try:
        kaynaklar = []
        for p in retrieval.search_papers(sorgu, limit=6):
            metin = (p.get("title") or "") + " " + (p.get("abstract") or "")[:400]
            if not p.get("url") or not baglam._ilgili(sorgu, metin):
                continue
            kaynaklar.append({"baslik": (p.get("title") or "")[:160],
                              "url": p["url"],
                              "tur": p.get("source") or "makale"})
            if len(kaynaklar) >= 4:
                break
        if kaynaklar:
            resp.text += canli.kaynakca(kaynaklar, lang)
            resp.extra["kaynaklar"] = kaynaklar
    except Exception:
        pass


def _arastirmaya_alindi(soru, lang="tr"):
    """Dogrulanmis bilgi yokken verilecek durust cevap."""
    konu = (nlu.strip_command_words(soru) or soru).strip()[:70]
    if lang == "tr":
        return (
            "Bu konuda **doğrulanmış bilgim yok**, o yüzden tahmin yürütmek "
            "istemiyorum — yanlış bilgi vermektense bilmediğimi söylerim.\n\n"
            "**«%s»** konusunu araştırma sırama aldım. Öğrenme motoru "
            "çalışırken bu konuyu hedefli olarak arayacak (Wikipedia, arXiv, "
            "ders kitapları). Birazdan tekrar sorarsanız cevabım hazır olur.\n\n"
            "Bu arada isterseniz:\n"
            "- Konuyla ilgili bir PDF yükleyin, birlikte inceleyelim\n"
            "- Daha dar bir soru sorun (formül, hesap, tanım)\n"
            "- `öğrendiklerim` yazarak sorularınızdan ne öğrendiğimi görün"
            % konu)
    return (
        "I have **no verified information** on this, and I would rather say "
        "so than guess.\n\nI have queued **«%s»** for targeted research "
        "(Wikipedia, arXiv, textbooks). Ask me again shortly and I should "
        "have an answer." % konu)


def _turetilmis_formul():
    """Cekirdekten turetilip dogrulanmis formul sayisi."""
    return sum(1 for f in formulas.FORMULAS if f.get("uretilmis"))


def _ogrenilen_konu():
    """Makalelerden ogrenilip yapilandirilmis bicimde anlatilabilen kavram."""
    try:
        return sentez.aciklanabilir_sayisi()
    except Exception:
        return 0


def h_yetenek(msg, lang, ctx):
    """'... konusunda ne kadar bilgin var' — o alanda ne yapabildigini anlat."""
    konu = nlu.strip_command_words(
        re.sub(r"\b(ne kadar|bilgin|biliyorsun|bilgiye|sahipsin|hakimsin|"
               r"bilirsin|var mi|konusunda|hakkinda|alaninda|uzerine|iyisin|"
               r"how much|how well|do you know|what do you know|about|"
               r"are you good at)\b", " ", msg, flags=re.I)) or msg
    tr = lang == "tr"

    # 1) Bir yol haritasi konusu mu? (matlab, fizik, sayisal)
    path = curriculum.find(konu)
    if path and path["key"] == "matlab":
        sablonlar = sorted(t["tr"] if tr else t["en"]
                           for t in matlab.TEMPLATES.values())
        lines = ["### " + ("MATLAB / Octave konusunda neler yapabilirim"
                           if tr else "What I can do with MATLAB / Octave")]
        lines.append("")
        lines.append(L(lang,
            "**%d hazır simülasyon şablonum** var; hepsi çalışır durumda, "
            "yorumlu ve MATLAB ile ücretsiz GNU Octave'da aynı şekilde çalışır:"
            % len(matlab.TEMPLATES),
            "I have **%d ready simulation templates**, all runnable, commented, "
            "and working identically in MATLAB and the free GNU Octave:"
            % len(matlab.TEMPLATES)))
        lines.append("")
        for s in sablonlar:
            lines.append("- " + s)
        lines.append("")
        lines.append(L(lang, "**Bunların dışında:**", "**Beyond those:**"))
        lines.append("")
        lines.append(L(lang,
            "- **%d fizik formülünün** herhangi biri için hesap kodu üretirim\n"
            "- Herhangi bir matematiksel ifadeyi MATLAB sözdizimine çeviririm\n"
            "- 5 aşamalı bir **öğrenme yol haritası** çıkarırım\n"
            "- `ode45`, `fft`, `eig`, `polyfit`, sonlu farklar, simplektik "
            "integratörler gibi konuları anlatırım"
            % len(formulas.FORMULAS),
            "- Generate calculation code for any of **%d physics formulas**\n"
            "- Translate any mathematical expression into MATLAB syntax\n"
            "- Lay out a 5-stage **learning roadmap**\n"
            "- Explain `ode45`, `fft`, `eig`, `polyfit`, finite differences and "
            "symplectic integrators" % len(formulas.FORMULAS)))
        lines.append("")
        lines.append(L(lang,
            "Dürüst sınırım: MATLAB kurulumu, araç kutuları (toolbox) ve "
            "Simulink konusunda bilgim yok — ürettiğim kodlar temel MATLAB ve "
            "Octave ile sınırlı.",
            "An honest limit: I don't cover MATLAB installation, toolboxes or "
            "Simulink — my code sticks to base MATLAB and Octave."))
        lines.append("")
        lines.append(L(lang, "Başlamak için: `matlab yol haritası`",
                       "To begin: `matlab roadmap`"))
        return Response("\n".join(lines), kind="capability",
                        extra={"konu_etiketi": "MATLAB"})

    # 2) Cekirdek bilgi tabanindaki bir konu mu?
    hits = knowledge.search(konu, limit=1)
    if hits and hits[0][0] >= 20:
        t = hits[0][1]
        baslik = t["tr_title"] if tr else t["en_title"]
        n_makale = len(retrieval.search_papers(konu, limit=40))
        lines = ["### " + L(lang, "%s konusunda bildiklerim" % baslik,
                            "What I know about %s" % baslik), ""]
        lines.append(L(lang,
            "Bu konu **çekirdek bilgimde** var: ayrıntılı anlatım, %d temel "
            "bağıntı ve %d çözümlü örnek hazır."
            % (len(t["eqs"]), len(t["ex_tr"] if tr else t["ex_en"])),
            "This topic is in my **core knowledge**: a full explanation, %d key "
            "relations and %d worked examples."
            % (len(t["eqs"]), len(t["ex_en"]))))
        if n_makale:
            lines.append("")
            lines.append(L(lang,
                "Ayrıca öğrendiğim makale özetlerinde bu konuda **%d+ kayıt** "
                "bulabiliyorum." % n_makale,
                "I can also find **%d+ records** on it among the abstracts I've "
                "learned." % n_makale))
        lines.append("")
        lines.append(L(lang,
            "Deneyin: `%s nedir` · `%s örnek ver` · `%s makale bul`"
            % (konu, konu, konu),
            "Try: `what is %s` · `%s example` · `find papers on %s`"
            % (konu, konu, konu)))
        return Response("\n".join(lines), kind="capability",
                        extra={"konu_etiketi": baslik})

    # 3) Genel: ogrenilmis veriden ne kadar bilgi oldugunu soyle
    papers = retrieval.search_papers(konu, limit=40)
    concepts = retrieval.search_concepts(konu, limit=10)
    if papers or concepts:
        lines = ["### " + L(lang, "'%s' konusunda elimdekiler" % konu,
                            "What I have on '%s'" % konu), ""]
        lines.append(L(lang,
            "Çekirdek bilgimde ayrı bir konu anlatımı yok, ama öğrendiklerimde "
            "**%d makale özeti** ve **%d kavram** eşleşiyor."
            % (len(papers), len(concepts)),
            "There's no dedicated topic in my core knowledge, but I match "
            "**%d abstracts** and **%d concepts** in what I've learned."
            % (len(papers), len(concepts))))
        # Malzeme VARSA kullaniciyi baska bicimde sormaya yonlendirmek
        # kotu bir cevaptir: "9 makale esleşiyor, `... nedir` yazarsaniz
        # anlatirim" demek yerine DOGRUDAN anlatiyoruz.
        try:
            m = sentez.malzeme(konu, lang)
            if sentez.aciklanabilir_mi(m):
                return Response(sentez.sayfa(m, lang), kind="topic",
                                extra={"konu_etiketi": m.get("ad") or konu})
        except Exception:
            pass
        # Sentez yetmiyorsa en azindan bulunan malzemeyi ozetle
        # Yalnizca SORUYLA ORTUSEN makaleler ozetlenir. Aksi halde konuyu
        # ayak ustu anan alakasiz bir makaleden derleme yapiliyordu
        # (olculdu: "topolojik yalitkanlar" sorusuna fraktal egri makalesi).
        # BASLIK eslesmesi sart: bir makalenin govdesinde konunun gecmesi,
        # o makalenin KONUSU oldugu anlamina gelmez. "topolojik yalitkanlar"
        # sorusuna, konuyu ayak ustu anan bir fraktal egri makalesinden
        # derleme yapiliyordu (olculdu).
        ilgili_makaleler = [
            p for p in papers
            if baglam._ilgili(konu, p.get("title") or "", gerekli=1)]
        if len(ilgili_makaleler) < 2:
            ilgili_makaleler = [
                p for p in papers
                if baglam._ilgili(konu, (p.get("title") or "") + " "
                                  + (p.get("abstract") or "")[:400],
                                  gerekli=2)]
        ozetler = [p.get("abstract") or "" for p in ilgili_makaleler[:5]
                   if len(p.get("abstract") or "") > 150]
        if ozetler:
            cumleler = retrieval.summarize(ozetler, query=konu,
                                           max_sentences=5)
            if cumleler:
                lines.append("")
                lines.append(" ".join(cumleler))
                kaynaklar = [{"baslik": (p.get("title") or "")[:150],
                              "url": p.get("url") or "",
                              "tur": p.get("source") or "makale"}
                             for p in ilgili_makaleler[:4] if p.get("url")]
                if kaynaklar:
                    lines.append(canli.kaynakca(kaynaklar, lang))
                return Response("\n".join(lines), kind="topic",
                                extra={"konu_etiketi": konu})
        # Odakli malzeme yoksa kullaniciyi baska bicimde sormaya gondermek
        # bir cevap degildir. Ogretmen gibi davran: bilmiyorsan BAK.
        try:
            arastirma = canli.arastir(konu, lang)
        except Exception:
            arastirma = None
        if arastirma and arastirma["baglam"] and dil.MODEL.kurulu_mu():
            akici = dil.MODEL.yanitla(konu, baglam=arastirma["baglam"],
                                      lang=lang)
            if akici and len(akici) > 40:
                return Response(
                    akici + canli.kaynakca(arastirma["kaynaklar"], lang),
                    kind="topic",
                    extra={"canli": True, "konu_etiketi": konu,
                           "kaynaklar": arastirma["kaynaklar"]})
        lines.append("")
        lines.append(L(lang, "`%s nedir` yazarsanız bunları derleyip anlatırım."
                       % konu,
                       "Ask `what is %s` and I'll synthesise them." % konu))
        return Response("\n".join(lines), kind="capability")

    return h_yardim(msg, lang, ctx)


def h_profil(msg, lang, ctx):
    return Response(profile.summary(lang), kind="profile")


def h_beni_unut(msg, lang, ctx):
    ad = profile.name()
    profile.forget()
    if lang == "tr":
        t = ("Sizinle ilgili tuttuğum her şeyi sildim: ad, düzey ve ilgi "
             "alanları. Sohbet geçmişiniz duruyor — onu kenar çubuğundan tek "
             "tek silebilirsiniz.")
        if ad:
            t = ("Tamam%s, sildim. Ad, düzey ve ilgi alanları gitti. Sohbet "
                 "geçmişiniz duruyor — onu kenar çubuğundan silebilirsiniz."
                 % (" " + ad if ad else ""))
    else:
        t = ("I've erased everything I kept about you: name, level and "
             "interests. Your chat history is untouched — you can delete those "
             "individually from the sidebar.")
    return Response(t, kind="profile")


def h_kendini_tanit(msg, lang, ctx):
    """Kullanici kendini tanittiginda ("adim ...", "lisans ogrencisiyim")."""
    ad = profile.name()
    lab = profile.level_label(lang)
    tr = lang == "tr"

    if not ad and not lab:
        return Response(
            L(lang,
              "Anlayamadım — adınızı `adım Polat`, düzeyinizi `lisans "
              "öğrencisiyim` gibi yazarsanız aklımda tutarım.",
              "I couldn't catch that — write your name as `my name is Polat` "
              "or your level as `I'm an undergraduate` and I'll remember."),
            kind="profile")

    if ad and lab:
        t = L(lang, "Memnun oldum **%s**! Düzeyinizi de **%s** olarak not ettim."
                    % (ad, lab),
              "Nice to meet you, **%s**! I've noted your level as **%s**."
              % (ad, lab))
    elif ad:
        t = L(lang, "Memnun oldum **%s**! Adınızı aklımda tutuyorum." % ad,
              "Nice to meet you, **%s**! I'll remember your name." % ad)
    else:
        t = L(lang, "Not ettim: **%s**." % lab,
              "Noted: **%s**." % lab)

    # Duzeyi biliyorsak somut bir sonraki adim oner
    oneri = {
        "baslangic": L(lang, "`fizik yol haritası`", "`physics roadmap`"),
        "lise": L(lang, "`fizik yol haritası`", "`physics roadmap`"),
        "lisans": L(lang, "`sayısal fizik yol haritası`",
                    "`computational physics roadmap`"),
        "yuksek_lisans": L(lang, "`sayısal fizik yol haritası`",
                           "`computational physics roadmap`"),
        "doktora": L(lang, "`kuantum alan kuramı nedir`",
                     "`what is quantum field theory`"),
        "ogretmen": L(lang, "`termodinamik örnek ver`",
                      "`give a thermodynamics example`"),
    }.get(profile.level())

    t += L(lang,
           "\n\nBundan sonra yeni sohbet açsanız da sizi tanıyacağım; "
           "silmek isterseniz `beni unut` yazmanız yeterli.",
           "\n\nI'll still know you in a new chat; type `forget me` to erase it.")
    if oneri:
        t += L(lang, "\n\nDüzeyinize uygun bir başlangıç: %s" % oneri,
               "\n\nA good starting point for your level: %s" % oneri)
    else:
        t += L(lang,
               "\n\nNe yapmak istersiniz? Yol haritası çıkarabilir, konu "
               "anlatabilir ya da hesap yapabilirim.",
               "\n\nWhat would you like to do? I can lay out a roadmap, "
               "explain a topic, or run a calculation.")
    return Response(t, kind="profile")


def h_tesekkur(msg, lang, ctx):
    if dil.MODEL.kurulu_mu():
        try:
            ad = (ctx.get("profil") or {}).get("ad")
            dogal = dil.MODEL.sohbet(msg, lang, ctx.get("history"), ad)
            if dogal and 5 < len(dogal) < 500:
                return Response(dogal, kind="chat")
        except Exception:
            pass
    return Response(L(lang, "Rica ederim. Baska bir sorun olursa buradayim.",
                      "You're welcome. Ask me anything else."))


def h_onay(msg, lang, ctx):
    """"tamam", "anladim", "peki" — soru degil, onay.

    Bunlara "bilgim yok" demek sohbeti bitiriyordu. Dogrusu kisa bir
    karsilik verip konuyu SURDURMEK: ogrenci nereden devam edebilecegini
    gorsun.
    """
    konu = (ctx.get("last_subject") or "").strip()
    tr = lang == "tr"
    if not konu:
        return Response(L(lang, "Ne zaman istersen devam edelim.",
                          "Happy to continue whenever you like."),
                        kind="chat")
    kt = knowledge.search(konu, limit=1)
    baslik = konu
    if kt and kt[0][0] >= 20:
        baslik = kt[0][1]["tr_title"] if tr else kt[0][1]["en_title"]
    satirlar = [L(lang, "Güzel. **%s** konusunda istersen şuradan devam edebiliriz:",
                  "Good. We can continue with **%s** from here:") % baslik, ""]
    for a, b in ((L(lang, "çözümlü örnek", "worked example"),
                  L(lang, "sayılarla bir örnek çözerim", "I solve one with numbers")),
                 (L(lang, "deneysel dayanağı", "experimental evidence"),
                  L(lang, "bunu hangi deney gösterdi", "which experiment showed it")),
                 (L(lang, "bağıntıları", "the relations"),
                  L(lang, "formüller ve değişkenleri", "formulas and variables")),
                 (L(lang, "matlab kodu", "matlab code"),
                  L(lang, "simülasyonunu yazarım", "I write the simulation"))):
        satirlar.append("- `%s %s` — %s" % (baslik.lower()[:40], a, b))
    return Response("\n".join(satirlar), kind="chat")


def h_yardim(msg, lang, ctx):
    if lang == "tr":
        t = """### Neler yapabilirim

**Hesaplama**
- `2*pi*sqrt(0.5/200)` — sayisal/sembolik hesap
- `x^3 - 2x = 5 coz` — denklem cozme
- `sin(x)*exp(x) turevi` — turev
- `x^2 integrali 0 dan 3 e` — belirli/belirsiz integral
- `sin(x)/x limiti x->0` — limit
- `y'' + 4y = 0 diferansiyel denklem` — ODE cozumu
- `[[1,2],[3,4]] determinanti` — matris islemleri
- `gradyan x^2+y^2+z^2` — vektor analizi

**Fizik**
- `kinetik enerji formulu` — formul ve degiskenleri
- `m=2 kg v=10 m/s kinetik enerji` — formulu cozer
- `T=500 K Th=300 K carnot verimi` — bilinmeyeni bulur
- `isik hizi nedir` — fiziksel sabitler
- `90 km/h kac m/s` — birim cevirme (boyut kontrollu)

**Konu anlatimi**
- `kuantum dolanikligi nedir`
- `termodinamigin ikinci yasasini anlat`
- `entropi ornek ver`

**MATLAB / Octave**
- `egik atis icin matlab kodu`
- `fft analizi kodu yaz`
- `kuantum kuyusu simulasyonu`

**Literatur**
- `superiletkenlik hakkinda makale bul`
- `son arxiv calismalari kozmoloji`

**Sistem**
- `durum` — ne kadar ogrendigimi gosterir
- `konulari listele` — bildigim ana konular"""
    else:
        t = """### What I can do

**Computation**
- `2*pi*sqrt(0.5/200)` — numeric/symbolic evaluation
- `solve x^3 - 2x = 5` — equation solving
- `derivative of sin(x)*exp(x)`
- `integral of x^2 from 0 to 3`
- `limit of sin(x)/x as x->0`
- `solve ODE y'' + 4y = 0`
- `determinant of [[1,2],[3,4]]`
- `gradient of x^2+y^2+z^2`

**Physics**
- `kinetic energy formula` — formula and its variables
- `m=2 kg v=10 m/s kinetic energy` — solves the formula
- `Th=500 K Tc=300 K carnot efficiency`
- `what is the speed of light` — physical constants
- `90 km/h to m/s` — dimension-checked unit conversion

**Explanations**
- `what is quantum entanglement`
- `explain the second law of thermodynamics`
- `give an example of entropy`

**MATLAB / Octave**
- `matlab code for projectile motion`
- `write an fft analysis script`
- `quantum well simulation`

**Literature**
- `find papers on superconductivity`
- `recent arxiv work on cosmology`

**System**
- `status` — how much I have learned
- `list topics` — main topics I know"""
    return Response(t)


def _sure_metni(saniye, lang):
    saniye = int(saniye or 0)
    g, kalan = divmod(saniye, 86400)
    sa, kalan = divmod(kalan, 3600)
    dk = kalan // 60
    if saniye < 60:
        return L(lang, "%d saniye" % saniye, "%ds" % saniye)
    if lang == "tr":
        parcalar = []
        if g:
            parcalar.append("%d gün" % g)
        if sa:
            parcalar.append("%d saat" % sa)
        parcalar.append("%d dakika" % dk)
        return " ".join(parcalar)
    parts = []
    if g:
        parts.append("%dd" % g)
    if sa:
        parts.append("%dh" % sa)
    parts.append("%dm" % dk)
    return " ".join(parts)


def h_durum(msg, lang, ctx):
    s = db.stats()
    lg = learner.LEARNER
    running = lg.is_running()
    kesif = db.get_state("kesif_bulunan", 0) or 0
    sorgu = db.get_state("derinlesme_sorgu", 0) or 0
    lines = []
    if lang == "tr":
        lines.append("### Ogrenme Durumu\n")
        lines.append("| | |")
        lines.append("|---|---|")
        lines.append("| Makale ozeti | **%s** |" % "{:,}".format(s["makale"]))
        _isl = s.get("islenmis", 0)
        _top = max(s["makale"], 1)
        lines.append("| — bilgiye donusen | **%s** (%%%d) |"
                     % ("{:,}".format(_isl), round(100 * _isl / _top)))
        lines.append("| — hakemli / onbaski | %s / %s |"
                     % ("{:,}".format(s.get("hakemli", 0)),
                        "{:,}".format(s.get("onbaski", 0))))
        lines.append("| — ortalama kalite | %s / 100 |" % s.get("ort_kalite", 0))
        lines.append("| Kalite kapisinda reddedilen | %s |"
                     % "{:,}".format(s.get("reddedilen", 0)))
        lines.append("| — Ingilizce | %s |" % "{:,}".format(s["en_makale"]))
        lines.append("| — Turkce | %s |" % "{:,}".format(s["tr_makale"]))
        lines.append("| Kavram (Wikipedia) | **%s** |" % "{:,}".format(s["kavram"]))
        lines.append("| Kavram baglantisi | **%s** |" % "{:,}".format(s["baglanti"]))
        lines.append("| Ogrenilen terim | %s |" % "{:,}".format(s["terim"]))
        lines.append("| Ogrenilen bagintI | %s (%s cozulebilir) |"
                     % ("{:,}".format(s["formul"]),
                        "{:,}".format(s.get("cozulebilir_formul", 0))))
        lines.append("| **Incelenen bulgu** | **%s** |" % "{:,}".format(s.get("bulgu", 0)))
        lines.append("| Kurulan iliski | %s |" % "{:,}".format(s.get("iliski", 0)))
        lines.append("| Yuklenen belge | %s |" % "{:,}".format(s.get("belge", 0)))
        lines.append("| Tamamlanan tur | %s |" % "{:,}".format(int(s["tur"] or 0)))
        lines.append("| Toplam ogrenme suresi | **%s** |"
                     % _sure_metni(lg.runtime(), "tr"))
        lines.append("| Kendi buldugu kavram | %s |" % "{:,}".format(int(kesif)))
        lines.append("| Kendi urettigi sorgu | %s |" % "{:,}".format(int(sorgu)))
        # Kendi kendine ogrendigi KAVRAMLAR ARASI BAGLAR. Elle konu
        # yazmadan, korpustan cikarilip iki bagimsiz kaynakla dogrulanan
        # gecisler. Kullanicinin gormek istedigi ilerleme bu.
        try:
            from . import kopruogren as _koo
            _kb, _khedef, _ksinav = _koo.durum()
            lines.append("| **Kendi cikardigi bag** | **%s** |"
                         % "{:,}".format(int(_kb)))
            lines.append("| — ogrenmeye calistigi bag | %s |"
                         % "{:,}".format(int(_khedef)))
            lines.append("| — kendi sinavi (zor soru) | %s |" % _ksinav)
        except Exception:
            pass
        # Kendi ogrendigi BAGINTILAR: boyut denetimi, yorum tekligi ve
        # sayisal sinavdan gecenler. Reddedilen sayisi da gosterilir;
        # ogrenmenin ne kadar SECICI oldugu gorunsun.
        try:
            from . import formulogren as _fo
            _fok, _fred, _faday = _fo.durum()
            lines.append("| **Kendi ogrendigi baginti** | **%s** |"
                         % "{:,}".format(int(_fok)))
            lines.append("| — dogrulamada elenen | %s |"
                         % "{:,}".format(int(_fred)))
        except Exception:
            pass
        lines.append("| Motor | %s |" % ("**calisiyor** ✅" if running else "durdu ⏸"))
        _d = dil.MODEL.durum()
        if _d["model"]:
            lines.append("| Dil modeli | **%s** (%s MB) %s |"
                         % (_d["model"].replace(".gguf", ""), "{:,}".format(_d["boyut_mb"]),
                            "· bellekte" if _d["yuklu"] else ""))
        elif _d["kutuphane"]:
            lines.append("| Dil modeli | kutuphane hazir, model dosyasi yok |")
        else:
            lines.append("| Dil modeli | kurulu degil (kural tabanli calisiyor) |")
        if s["kaynaklar"]:
            lines.append("\n**Kaynak dagilimi:**")
            for r in s["kaynaklar"]:
                lines.append("- %s: %s" % (r["source"], "{:,}".format(r["n"])))
        lines.append("\n**Cekirdek bilgi (her zaman hazir):** %d konu anlatimi, "
                     "%d cozulebilir formul, %d fiziksel sabit."
                     % (len(knowledge.TOPICS), len(formulas.FORMULAS),
                        len(units.CONSTANTS)))
        try:
            ek = sentez.aciklanabilir_sayisi()
        except Exception:
            ek = 0
        lines.append("\n**Ogrenerek kazandigi:** %s konuyu artik yapilandirilmis "
                     "bicimde anlatabiliyor (cekirdek disinda). Bu sayi yeni "
                     "makaleler geldikce artar." % "{:,}".format(ek))
        try:
            from . import genisleme as _gen
            g = _gen.durum()
            lines.append(
                "\n**Kendi urettikleri:** %d yol haritasi (okudugu "
                "makalelerden), %d turetilmis formul (hepsi boyut denetimi "
                "ve geri yerine koymadan gecti). Bu sayilar her gun yeniden "
                "hesaplanir."
                % (g["yol_haritasi_uretilmis"], _turetilmis_formul()))
        except Exception:
            pass
        log = lg.recent_log(8)
        if log:
            lines.append("\n**Son islemler:**\n```\n%s\n```" % "\n".join(log))
    else:
        lines.append("### Learning Status\n")
        lines.append("| | |")
        lines.append("|---|---|")
        lines.append("| Paper abstracts | **%s** |" % "{:,}".format(s["makale"]))
        _isl = s.get("islenmis", 0)
        _top = max(s["makale"], 1)
        lines.append("| — turned into knowledge | **%s** (%d%%) |"
                     % ("{:,}".format(_isl), round(100 * _isl / _top)))
        lines.append("| — peer-reviewed / preprint | %s / %s |"
                     % ("{:,}".format(s.get("hakemli", 0)),
                        "{:,}".format(s.get("onbaski", 0))))
        lines.append("| — mean quality | %s / 100 |" % s.get("ort_kalite", 0))
        lines.append("| Rejected at quality gate | %s |"
                     % "{:,}".format(s.get("reddedilen", 0)))
        lines.append("| — English | %s |" % "{:,}".format(s["en_makale"]))
        lines.append("| — Turkish | %s |" % "{:,}".format(s["tr_makale"]))
        lines.append("| Concepts (Wikipedia) | **%s** |" % "{:,}".format(s["kavram"]))
        lines.append("| Concept links | **%s** |" % "{:,}".format(s["baglanti"]))
        lines.append("| Terms learned | %s |" % "{:,}".format(s["terim"]))
        lines.append("| Relations learned | %s (%s parseable) |"
                     % ("{:,}".format(s["formul"]),
                        "{:,}".format(s.get("cozulebilir_formul", 0))))
        lines.append("| **Insights studied** | **%s** |" % "{:,}".format(s.get("bulgu", 0)))
        lines.append("| Relations inferred | %s |" % "{:,}".format(s.get("iliski", 0)))
        lines.append("| Documents uploaded | %s |" % "{:,}".format(s.get("belge", 0)))
        lines.append("| Cycles completed | %s |" % "{:,}".format(int(s["tur"] or 0)))
        lines.append("| Total learning time | **%s** |"
                     % _sure_metni(lg.runtime(), "en"))
        lines.append("| Concepts it found itself | %s |" % "{:,}".format(int(kesif)))
        lines.append("| Self-generated queries | %s |" % "{:,}".format(int(sorgu)))
        lines.append("| Engine | %s |" % ("**running** ✅" if running else "stopped ⏸"))
        _d = dil.MODEL.durum()
        if _d["model"]:
            lines.append("| Language model | **%s** (%s MB) %s |"
                         % (_d["model"].replace(".gguf", ""), "{:,}".format(_d["boyut_mb"]),
                            "· loaded" if _d["yuklu"] else ""))
        else:
            lines.append("| Language model | not installed (rule-based mode) |")
        if s["kaynaklar"]:
            lines.append("\n**By source:**")
            for r in s["kaynaklar"]:
                lines.append("- %s: %s" % (r["source"], "{:,}".format(r["n"])))
        lines.append("\n**Core knowledge (always available):** %d topic explanations, "
                     "%d solvable formulas, %d physical constants."
                     % (len(knowledge.TOPICS), len(formulas.FORMULAS),
                        len(units.CONSTANTS)))
        try:
            ek = sentez.aciklanabilir_sayisi()
        except Exception:
            ek = 0
        lines.append("\n**Gained by learning:** it can now explain %s further "
                     "topics in structured form. This grows with new papers."
                     % "{:,}".format(ek))
        log = lg.recent_log(8)
        if log:
            lines.append("\n**Recent activity:**\n```\n%s\n```" % "\n".join(log))
    return Response("\n".join(lines), kind="status")


def h_liste(msg, lang, ctx):
    lines = [L(lang, "### Bildigim ana konular\n", "### Main topics I know\n")]
    for key, title in knowledge.list_topics(lang):
        lines.append("- **%s**" % title)
    lines.append(L(lang,
                   "\nAyrica **%d cozulebilir formul** (%s) ve **%d fiziksel sabit** var. "
                   "Bunlarin otesinde ogrenilmis %s makale ozetinde arama yapabilirim."
                   % (len(formulas.FORMULAS), ", ".join(formulas.TOPICS),
                      len(units.CONSTANTS), "{:,}".format(db.stats()["makale"])),
                   "\nPlus **%d solvable formulas** (%s) and **%d physical constants**. "
                   "Beyond that I can search %s learned paper abstracts."
                   % (len(formulas.FORMULAS), ", ".join(formulas.TOPICS),
                      len(units.CONSTANTS), "{:,}".format(db.stats()["makale"]))))
    return Response("\n".join(lines))


# ------------------------------------------------------------------ hesaplama
def h_hesap(msg, lang, ctx):
    expr = nlu.extract_expression(msg)
    # Dogal dil cumlesi sembolik ifade sanilmamali: "entropi acar misin"
    # ifadesi `acar*entropi*isin` gibi anlamsiz bir carpima donusuyordu.
    if expr and not nlu.looks_like_expression(expr):
        return h_konu(msg, lang, ctx)
    if not expr:
        return Response(L(lang, "Hesaplanacak bir ifade bulamadim.",
                          "I couldn't find an expression to evaluate."))
    try:
        r = solver.evaluate(expr)
    except solver.SolveError as e:
        return Response(L(lang, "Ifadeyi cozumleyemedim: %s" % e,
                          "I couldn't parse the expression: %s" % e))
    lines = ["```\n%s\n```" % r["pretty"]]
    if "numeric" in r:
        val = r.get("float")
        lines.insert(0, L(lang, "**Sonuc:** `%s`", "**Result:** `%s`")
                     % (units.fmt(val, 10) if val is not None else r["numeric"]))
        if val is not None and r["simplified"] != r["numeric"]:
            lines.append(L(lang, "\nTam deger: `%s`", "\nExact: `%s`") % r["simplified"])
    else:
        lines.insert(0, L(lang, "**Sadelestirilmis:** `%s`",
                          "**Simplified:** `%s`") % r["simplified"])
        if r.get("variables"):
            lines.append(L(lang, "\nDegiskenler: %s", "\nVariables: %s")
                         % ", ".join("`%s`" % v for v in r["variables"]))
    return Response("\n".join(lines), kind="calc",
                    extra={"latex": r.get("simplified_latex", "")})


def h_denklem(msg, lang, ctx):
    # Komut kelimeleri ifadenin parcasi degil. Olculdu: "denklemi coz:
    # 3x+1=7" istegi ayristiriciya oldugu gibi gidiyordu ve "invalid
    # syntax" hatasi veriyordu.
    text = re.sub(r"\b(denklem(?:i|in|ini|ler|leri)?|coz|cozum|cozumu|"
                  r"cozun|cozer misin|bul|bulunuz|kokleri|kokunu|"
                  r"solve|equation|find|roots|lutfen|please)\b",
                  " ", msg, flags=re.I)
    text = re.sub(r"\s+", " ", text.replace(":", " ")).strip() or msg
    # Sistem mi?
    parts = [p.strip() for p in re.split(r"[;\n]|(?:\s+ve\s+)|(?:\s+and\s+)", text)
             if "=" in p]
    parts = [nlu.extract_expression(p) or p for p in parts]
    parts = [p for p in parts if p and "=" in p]
    try:
        if len(parts) > 1:
            r = solver.solve_system(parts)
            lines = [L(lang, "### Denklem sistemi", "### System of equations")]
            lines.append("```\n%s\n```" % "\n".join(r["equations"]))
            if not r["solutions"]:
                lines.append(L(lang, "Cozum bulunamadi.", "No solution found."))
            for i, sol in enumerate(r["solutions"], 1):
                lines.append(L(lang, "**Cozum %d:**", "**Solution %d:**") % i)
                for k, v in sol.items():
                    lines.append("- `%s = %s`" % (k, v))
            return Response("\n".join(lines), kind="calc")

        expr = nlu.extract_expression(text) or text
        var = None
        m = re.search(r"\b([a-zA-Z])\s*(?:'?(?:yi|yı|i|ı|u|ü)\s*)?(?:icin|için|for)\b",
                      text)
        if m:
            var = m.group(1)
        r = solver.solve_equation(expr, var=var)
        lines = [L(lang, "### Denklem cozumu", "### Equation solution")]
        lines.append("`%s`  →  **%s**" % (r["equation"], r["variable"]))
        if not r["solutions"]:
            lines.append(L(lang, "\nGercel cozum bulunamadi.", "\nNo solution found."))
        else:
            lines.append("")
            for i, s in enumerate(r["solutions"], 1):
                if "numeric" in s:
                    lines.append("%d. `%s = %s`  ≈ `%s`"
                                 % (i, r["variable"], s["expr"], s["numeric"]))
                else:
                    lines.append("%d. `%s = %s`" % (i, r["variable"], s["expr"]))
        return Response("\n".join(lines), kind="calc")
    except solver.SolveError as e:
        return Response(L(lang, "Denklemi cozemedim: %s" % e,
                          "I couldn't solve the equation: %s" % e))
    except Exception as e:
        return Response(L(lang, "Denklemi cozerken hata olustu: %s" % e,
                          "Error while solving: %s" % e))


def h_turev(msg, lang, ctx):
    expr = nlu.extract_expression(msg)
    var = nlu.extract_variable(msg)
    order = 1
    m = re.search(r"(\d+)\s*\.?\s*(?:mertebe|derece|kez|order|nd|rd|th)", msg, re.I)
    if m:
        order = max(1, min(6, int(m.group(1))))
    elif re.search(r"\bikinci|second\b", msg, re.I):
        order = 2
    if not expr:
        return Response(L(lang, "Turevi alinacak ifadeyi bulamadim.",
                          "I couldn't find the expression to differentiate."))
    try:
        r = solver.derivative(expr, var=var, order=order)
    except solver.SolveError as e:
        return Response(L(lang, "Hata: %s" % e, "Error: %s" % e))
    lines = [L(lang, "### Turev", "### Derivative")]
    d = "d/d%s" % r["variable"] if order == 1 else "d^%d/d%s^%d" % (order, r["variable"], order)
    lines.append("`%s [ %s ]`" % (d, r["input"]))
    lines.append("\n**=** `%s`" % r["result"])
    lines.append("\n```\n%s\n```" % r["pretty"])
    return Response("\n".join(lines), kind="calc", extra={"latex": r.get("latex", "")})


def h_integral(msg, lang, ctx):
    expr = nlu.extract_expression(msg)
    var = nlu.extract_variable(msg)
    lim = nlu.extract_limits(msg)
    if not expr:
        return Response(L(lang, "Integrali alinacak ifadeyi bulamadim.",
                          "I couldn't find the expression to integrate."))
    # Sinirlari ifadeden temizle
    if lim:
        expr = re.sub(r"(?:from\s+\S+\s+to\s+\S+)|(?:\S+\s*(?:dan|den)\s*\S+\s*(?:a|e|ya|ye))",
                      " ", expr, flags=re.I).strip()
        expr = re.sub(r"\[\s*\S+\s*,\s*\S+\s*\]", " ", expr).strip()
    try:
        r = solver.integral(expr, var=var,
                            a=lim[0] if lim else None, b=lim[1] if lim else None)
    except solver.SolveError as e:
        return Response(L(lang, "Hata: %s" % e, "Error: %s" % e))
    except Exception as e:
        return Response(L(lang, "Integral hesaplanamadi: %s" % e,
                          "Could not compute the integral: %s" % e))
    lines = [L(lang, "### Integral", "### Integral")]
    if r.get("definite"):
        lines.append("`∫[%s..%s] %s d%s`" % (r["from"], r["to"], r["input"], r["variable"]))
        lines.append("\n**=** `%s`" % r["result"])
        if "numeric" in r:
            lines.append("**≈** `%s`" % r["numeric"])
    else:
        lines.append("`∫ %s d%s`" % (r["input"], r["variable"]))
        lines.append("\n**=** `%s`" % r["result"])
        if r.get("pretty"):
            lines.append("\n```\n%s\n```" % r["pretty"])
    return Response("\n".join(lines), kind="calc", extra={"latex": r.get("latex", "")})


def h_limit(msg, lang, ctx):
    expr = nlu.extract_expression(msg)
    var = nlu.extract_variable(msg)
    to = "0"
    m = re.search(r"(?:->|→|yaklasirken|as\s+\w+\s*->)\s*([^\s,;]+)", msg)
    if m:
        to = m.group(1)
    else:
        m = re.search(r"\b([a-zA-Z])\s*(?:->|→)\s*([^\s,;]+)", msg)
        if m:
            var, to = m.group(1), m.group(2)
    to = to.replace("sonsuz", "oo").replace("infinity", "oo").replace("inf", "oo")
    if expr:
        expr = re.sub(r"[a-zA-Z]\s*(?:->|→)\s*\S+", " ", expr).strip()
    if not expr:
        return Response(L(lang, "Limiti alinacak ifadeyi bulamadim.",
                          "I couldn't find the expression."))
    try:
        r = solver.limit_of(expr, var=var, to=to)
    except solver.SolveError as e:
        return Response(L(lang, "Hata: %s" % e, "Error: %s" % e))
    return Response(L(lang, "### Limit\n\n`lim(%s→%s) %s`\n\n**=** `%s`",
                      "### Limit\n\n`lim(%s→%s) %s`\n\n**=** `%s`")
                    % (r["variable"], r["point"], r["input"], r["result"]),
                    kind="calc", extra={"latex": r.get("latex", "")})


def h_seri(msg, lang, ctx):
    expr = nlu.extract_expression(msg)
    var = nlu.extract_variable(msg)
    order = 6
    m = re.search(r"(\d+)\s*(?:terim|mertebe|order|terms)", msg, re.I)
    if m:
        order = max(2, min(15, int(m.group(1))))
    about = "0"
    m = re.search(r"(?:etrafinda|around|about|civarinda)\s*([^\s,;]+)", msg, re.I)
    if m:
        about = m.group(1)
    if not expr:
        return Response(L(lang, "Ifadeyi bulamadim.", "I couldn't find the expression."))
    expr = re.sub(r"\b(taylor|maclaurin|seri|serisi|acilimi|series|expansion)\b",
                  " ", expr, flags=re.I).strip()
    try:
        r = solver.series(expr, var=var, about=about, order=order)
    except Exception as e:
        return Response(L(lang, "Seri acilimi yapilamadi: %s" % e,
                          "Series expansion failed: %s" % e))
    return Response(L(lang,
                      "### Taylor serisi\n\n`%s` fonksiyonunun `%s = %s` "
                      "etrafinda %d. mertebeye kadar acilimi:\n\n**=** `%s`",
                      "### Taylor series\n\nExpansion of `%s` about `%s = %s` "
                      "to order %d:\n\n**=** `%s`")
                    % (r["input"], r["variable"], r["about"], order, r["result"]),
                    kind="calc")


def h_diferansiyel(msg, lang, ctx):
    # Ortada cozulecek bir denklem yoksa bu bir OGRENME sorusudur.
    # Olculdu: "diferansiyel denklem sayisal cozumu" istegi
    # "cozemedim" hatasi aliyordu; ogrenci yontemi ogrenmek istiyor.
    if not re.search(r"'|=|d\s*[yx]\s*/\s*d|derivative", msg or ""):
        return h_konu(msg, lang, ctx)
    expr = nlu.extract_expression(msg) or msg
    expr = re.sub(r"\b(diferansiyel|denklem|denklemi|denklemini|denklemin|"
                  r"coz|cozumu|cozer|cozun|ode|"
                  r"differential|equation|solve)\b", " ", expr,
                  flags=re.I).strip()
    func = "y"
    m = re.search(r"\b([a-zA-Z])\s*''", expr) or re.search(r"\b([a-zA-Z])\s*'", expr)
    if m:
        func = m.group(1)
    var = "x"
    if re.search(r"\bt\b", expr) and not re.search(r"\bx\b", expr):
        var = "t"
    try:
        r = solver.ode(expr, func=func, var=var)
    except solver.SolveError as e:
        return Response(L(lang,
                          "Diferansiyel denklemi cozemedim: %s\n\n"
                          "Ipucu: `y'' + 4*y = 0` bicimini kullanmayi deneyin." % e,
                          "Could not solve the ODE: %s\n\n"
                          "Hint: try the form `y'' + 4*y = 0`." % e))
    lines = [L(lang, "### Diferansiyel denklem cozumu", "### ODE solution")]
    lines.append("`%s`" % r["equation"])
    lines.append("")
    for s in r["solutions"]:
        lines.append("**%s**" % s["expr"])
    lines.append(L(lang, "\n> `C1`, `C2` baslangic/sinir kosullarindan belirlenen sabitlerdir.",
                   "\n> `C1`, `C2` are constants fixed by initial/boundary conditions."))
    return Response("\n".join(lines), kind="calc")


def h_matris(msg, lang, ctx):
    rows = nlu.extract_matrix(msg)
    if not rows:
        # Matris verilmediyse bu bir OGRENME sorusudur, hesap degil.
        # Olculdu: "ozdeger problemi" sorusu "Matrisi [[1,2],[3,4]]
        # bicimde yazar misiniz?" cevabini aliyordu.
        if "[" not in (msg or ""):
            ders = h_konu(msg, lang, ctx)
            if ders and len(ders.text) > 300:
                return ders
        return Response(L(lang,
                          "Matrisi `[[1,2],[3,4]]` bicimde yazar misiniz?",
                          "Please write the matrix as `[[1,2],[3,4]]`."))
    t = nlu.norm(msg)
    op = "det"
    if "ozdeger" in t or "eigen" in t:
        op = "eig"
    elif "ters" in t or "inverse" in t or "inv" in t:
        op = "inv"
    elif "rank" in t or "rutbe" in t:
        op = "rank"
    elif "devrik" in t or "transpose" in t:
        op = "transpose"
    elif "iz" in t.split() or "trace" in t:
        op = "trace"
    try:
        r = solver.matrix_ops(rows, op=op)
    except Exception as e:
        return Response(L(lang, "Matris islemi basarisiz: %s" % e,
                          "Matrix operation failed: %s" % e))
    lines = [L(lang, "### Matris islemi", "### Matrix operation")]
    lines.append("`%s`  (%s)" % (r["matrix"], r["shape"]))
    lines.append("")
    for k, v in r.items():
        if k in ("matrix", "shape"):
            continue
        if k == "eigenvectors":
            lines.append(L(lang, "**Ozvektorler:**", "**Eigenvectors:**"))
            for ev in v:
                lines.append("- λ = `%s` (kat %d): %s"
                             % (ev["value"], ev["mult"], ", ".join("`%s`" % x for x in ev["vectors"])))
        elif k == "eigenvalues":
            lines.append(L(lang, "**Ozdegerler:**", "**Eigenvalues:**"))
            for val, mult in v.items():
                lines.append("- `λ = %s` (katlilik %d)" % (val, mult))
        else:
            lines.append("**%s:** `%s`" % (k, v))
    return Response("\n".join(lines), kind="calc")


def h_vektor(msg, lang, ctx):
    t = nlu.norm(msg)
    # Hesap makinesi ancak GERCEK bir vektor/ifade verilmisse calisir.
    # Olculdu: "vektor analizi diverjans teoremi" sorusu "Vektor alanini
    # [Fx,Fy,Fz] bicimde verin" uyarisi aliyordu; oysa ogrenci teoremi
    # ogrenmek istiyor.
    if not re.search(r"[\[\(]|[a-zA-Z]\s*\^|\d", msg or ""):
        return h_konu(msg, lang, ctx)
    if "gradyan" in t or "gradient" in t or "grad" in t:
        op = "grad"
    elif "diverjans" in t or "divergence" in t or "div" in t:
        op = "div"
    elif "rotasyonel" in t or "curl" in t or "rot" in t:
        op = "curl"
    else:
        op = "laplacian"
    expr = nlu.extract_expression(msg) or msg
    expr = re.sub(r"\b(gradyan|gradient|grad|diverjans|divergence|div|"
                  r"rotasyonel|curl|rot|laplasyen|laplacian|of|nin|nun)\b",
                  " ", expr, flags=re.I).strip()
    # Gradyan SKALER alana uygulanir. Ogrenci vektor verdiyse bu bir
    # kavram hatasidir; ogretmen bunu soyler, kriptik bir SymPy hatasi
    # dondurmez (olculdu: "Cannot represent derivative of...").
    if op == "grad" and re.search(r"[\[,;]", expr):
        return Response(L(
            lang,
            "### Gradyan skaler alana uygulanır\n\n"
            "`∇f` bir **skaler** fonksiyondan vektör üretir; siz vektör "
            "verdiniz. Vektör alanı için üç seçenek var:\n\n"
            "- `diverjans %s` — kaynak var mı? (skaler döner)\n"
            "- `rotasyonel %s` — dönme var mı? (vektör döner)\n"
            "- Skaler bir alan içinse tek ifade yazın: `gradyan x^2+y^2`"
            % (expr, expr),
            "### The gradient acts on a scalar field\n\n"
            "You supplied a vector. Use `divergence %s` or `curl %s`, or "
            "give a single scalar expression." % (expr, expr)),
            kind="calc")
    try:
        if op in ("grad", "laplacian"):
            r = solver.vector_calc(expr, op)
        else:
            comps = [c.strip() for c in re.split(r"[,;]", expr.strip("[]() ")) if c.strip()]
            if len(comps) != 3:
                return Response(L(lang,
                                  "Vektor alanini `[Fx, Fy, Fz]` bicimde verin. Ornek: "
                                  "`diverjans [x*y, y*z, z*x]`",
                                  "Give the field as `[Fx, Fy, Fz]`, e.g. "
                                  "`divergence [x*y, y*z, z*x]`"))
            r = solver.vector_calc(comps, op)
    except Exception as e:
        return Response(L(lang, "Vektor islemi basarisiz: %s" % e,
                          "Vector operation failed: %s" % e))
    lines = [L(lang, "### Vektor analizi", "### Vector calculus")]
    lines.append("**%s**" % r["operation"])
    res = r["result"]
    if isinstance(res, list):
        lines.append("`( %s )`" % ",  ".join(res))
    else:
        lines.append("`%s`" % res)
    return Response("\n".join(lines), kind="calc")


# --------------------------------------------------------------- birim/sabit
def h_birim(msg, lang, ctx):
    conv = nlu.extract_conversion(msg)
    if not conv:
        nus = nlu.extract_number_unit(msg)
        if nus:
            val, unit = nus[0][0], nus[0][1]
            si, dim = units.to_si(val, unit)
            if si is not None:
                sug = units.suggest_units(dim)
                return Response(L(lang,
                                  "`%g %s` = **%s** (SI)\n\nBoyut: **%s**\n\n"
                                  "Bu boyuttaki birimler: %s\n\n"
                                  "Cevirmek icin: `%g %s kac <birim>`",
                                  "`%g %s` = **%s** (SI)\n\nDimension: **%s**\n\n"
                                  "Units with this dimension: %s\n\n"
                                  "To convert: `%g %s to <unit>`")
                                % (val, unit, units.fmt(si), units.dim_label(dim),
                                   ", ".join("`%s`" % u for u in sug), val, unit))
        return Response(L(lang,
                          "Cevirmek istediginiz degeri ve birimleri yazin. "
                          "Ornek: `90 km/h kac m/s`",
                          "Give the value and units, e.g. `90 km/h to m/s`"))
    val, frm, to = conv
    out, err = units.convert(val, frm, to)
    if err:
        kind, detail = err
        if kind == "bilinmeyen":
            return Response(L(lang,
                              "`%s` birimini tanimiyorum.\n\n"
                              "Tanidiğim birimlerden bazilari: m, km, cm, kg, g, s, "
                              "saat, N, J, eV, cal, W, Pa, bar, atm, Hz, V, A, ohm, "
                              "T, K, degC, L, mol, mph, km/h, m/s." % detail,
                              "I don't recognise the unit `%s`.\n\n"
                              "Some units I know: m, km, cm, kg, g, s, hour, N, J, "
                              "eV, cal, W, Pa, bar, atm, Hz, V, A, ohm, T, K, degC, "
                              "L, mol, mph, km/h, m/s." % detail))
        f_u, f_d, t_u, t_d = detail
        return Response(L(lang,
                          "Bu iki birim ayni fiziksel buyuklugu olcmuyor:\n\n"
                          "- `%s` → **%s**\n- `%s` → **%s**\n\n"
                          "Aralarinda cevrim yapilamaz."
                          % (f_u, f_d, t_u, t_d),
                          "These two units measure different quantities:\n\n"
                          "- `%s` → **%s**\n- `%s` → **%s**\n\n"
                          "No conversion exists between them."
                          % (f_u, f_d, t_u, t_d)))
    a = units.parse_unit(frm)
    lines = [L(lang, "### Birim cevirme", "### Unit conversion")]
    lines.append("## `%g %s` = `%s %s`" % (val, frm, units.fmt(out, 8), to))
    lines.append("")
    si, dim = units.to_si(val, frm)
    lines.append(L(lang, "SI karsiligi: `%s` · Boyut: **%s**",
                   "In SI: `%s` · Dimension: **%s**")
                 % (units.fmt(si), units.dim_label(a[1] if a else dim)))
    return Response("\n".join(lines), kind="calc")


def h_sabit(msg, lang, ctx):
    q = nlu.strip_command_words(msg)
    key = units.find_constant(q) or units.find_constant(msg)
    if not key:
        # tum sabitleri listele
        lines = [L(lang, "### Fiziksel sabitler", "### Physical constants")]
        lines.append("| " + L(lang, "Sembol | Deger | Birim | Aciklama",
                              "Symbol | Value | Unit | Description") + " |")
        lines.append("|---|---|---|---|")
        for k, (v, u, d, tr, en) in sorted(units.CONSTANTS.items()):
            lines.append("| `%s` | %s | %s | %s |"
                         % (k, units.fmt(v, 8), u or "—", tr if lang == "tr" else en))
        return Response("\n".join(lines))
    v, u, dim, tr, en = units.CONSTANTS[key]
    lines = [L(lang, "### %s", "### %s") % (tr if lang == "tr" else en)]
    lines.append("## `%s` = %s %s" % (key, units.fmt_exact(v), u))
    exp_form = units.fmt(v, 10)
    if exp_form != units.fmt_exact(v):
        lines.append(L(lang, "≈ `%s %s`", "≈ `%s %s`") % (exp_form, u))
    lines.append("")
    if dim != units.DIMENSIONLESS:
        lines.append(L(lang, "Boyut: **%s**", "Dimension: **%s**") % units.dim_label(dim))

    # Bu sabiti gercekten kullanan formuller: sembol eslesmesi tek basina
    # yeterli degil (ornegin 'c' hem isik hizi hem ozgul isi olabilir),
    # bu yuzden degiskenin adi da sabitin adiyla ortusmeli.
    cname = nlu.norm(tr)
    rel = []
    for f in formulas.FORMULAS:
        if key not in f["vars"]:
            continue
        vlabel = nlu.norm(f["vars"][key][0])
        if vlabel and (vlabel in cname or cname.split("(")[0].strip() in vlabel):
            rel.append(f)
    if rel:
        lines.append(L(lang, "\n**Bu sabitin gectigi formuller:**",
                       "\n**Formulas using this constant:**"))
        for f in rel[:6]:
            lines.append("- %s: `%s`" % (f["tr"] if lang == "tr" else f["en"], f["eq"]))

    # Tek kelimelik bir sorgu ("planck") hem sabiti hem kisiyi hem de
    # konuyu isaret edebilir. Ogrenci hangisini istedigini bilmeyebilir;
    # ogretmen secenekleri gosterir.
    # Esik burada dusuk tutulur (12): bu bir CEVAP degil, yonlendirme.
    # "planck" tek basina hicbir anahtar obegi tam tutmaz ama baslik
    # eslesmesi kisiyi bulmaya yeter.
    yakin = []
    for _s, t in knowledge.search(msg, limit=4):
        if _s >= 12:
            yakin.append(t["tr_title"] if lang == "tr" else t["en_title"])
    if yakin:
        lines.append(L(lang, "\n**Bu adla ilgili konular:**",
                       "\n**Related topics under this name:**"))
        for y in yakin[:3]:
            lines.append("- `%s`" % y.lower())
    return Response("\n".join(lines), kind="calc")


# ------------------------------------------------------------------- formul
def _formul_sec(msg, lang, hits):
    """Anahtar kelime aramasi zayifsa dil modeline sectir.

    Model yalnizca aday listesinden secim yapar; formulu kendisi uretmez ve
    hesabi yapmaz. Secilen formul SymPy ile cozuldugu icin sonuc yine
    dogrulanmis olur. Boylece anlama (model) ile dogruluk (SymPy) ayri
    kalir ve birbirine karismaz.
    """
    if hits and hits[0][0] >= 45:
        return hits           # eslesme zaten guclu
    if not dil.MODEL.kurulu_mu():
        return hits

    # 1. asama — dil modeli soruyu fizik terimlerine cevirir (secim yapmaz)
    try:
        terimler = dil.MODEL.terim_cikar(msg, lang)
    except Exception:
        terimler = []
    genisletilmis = list(hits)
    var = {h[1]["id"] for h in genisletilmis}
    # Terimler tek tek degil BIRLIKTE aranir: "kapasite" tek basina molar isi
    # kapasitesini getiriyor, ama "kapasite direnc zaman sabiti" birlikte
    # arandiginda RC zaman sabiti one cikiyor. Birden fazla terimin ayni
    # formule vurmasi dogru esleşmenin en guvenilir isareti.
    if terimler:
        birlesik = " ".join(terimler)
        for skor, f in formulas.search(birlesik, limit=5):
            if skor >= 30 and f["id"] not in var:
                # Terim modelden geldigi icin skor bir miktar kirpilir;
                # dogrudan sorudan gelen eslesme her zaman oncelikli.
                genisletilmis.append((int(skor * 0.9), f))
                var.add(f["id"])
        for terim in terimler:
            if len(terim.split()) < 2:
                continue          # tek genel kelime tek basina yaniltici
            for skor, f in formulas.search(terim, limit=2):
                if skor >= 45 and f["id"] not in var:
                    genisletilmis.append((int(skor * 0.8), f))
                    var.add(f["id"])
    # Turetilmis formuller ALTERNATIF bicimlerdir; sorunun birincil cevabi
    # cekirdek formuldur. Genisletme sonrasi siralamada one gecebiliyorlardi:
    # "kutlesi 3 kg, 12 N kuvvet, ivme nedir" sorusu F = m*(v-v0)/t
    # bilesimine gidiyordu ve degerler eslesmedigi icin hesap yapilamiyordu.
    cekirdek_var = any(not f.get("uretilmis") for _s, f in genisletilmis)
    if cekirdek_var:
        genisletilmis.sort(key=lambda x: (x[1].get("uretilmis") and 1 or 0,
                                          -x[0]))
    else:
        genisletilmis.sort(key=lambda x: -x[0])
    if genisletilmis and genisletilmis[0][0] >= 40:
        # Dil modeli sayesinde bulundu: ifadeyi ogren ki bir dahaki sefere
        # deterministik arama modele ihtiyac duymadan bulsun.
        if terimler:
            try:
                formulas.ifade_ogren(genisletilmis[0][1]["id"], msg)
            except Exception:
                pass
        return genisletilmis[:5]

    # 2. asama — deterministik arama hicbir sey bulamadiysa son care olarak
    # modele kisa bir aday listesi sunulur. Olcum: model 8 adayli listede
    # ~%40 dogru seciyor, bu yuzden deterministik sonucun onune GECMEZ;
    # yalnizca elde hicbir sey yokken devreye girer.
    # Model secimine YALNIZCA cekirdek formuller girer. Turetilmisler
    # alternatif bicimlerdir; model bunlardan birini secince cevap
    # "F = m*(v-v0)/t" ya da kutle cekim bilesimi gibi alakasiz bir
    # formule gidiyordu (olculdu).
    adaylar = [f for _s, f in formulas.genis_ara(msg, limit=8)
               if not f.get("uretilmis")][:5]
    if len(adaylar) < 2:
        return genisletilmis or hits
    try:
        secilen = dil.MODEL.formul_esle(msg, adaylar, lang)
    except Exception:
        secilen = None
    if secilen and not secilen.get("uretilmis"):
        try:
            formulas.ifade_ogren(secilen["id"], msg)
        except Exception:
            pass
        return [(100, secilen)] + [h for h in genisletilmis
                                   if h[1] is not secilen]
    return genisletilmis or hits


def h_turetim(msg, lang, ctx):
    """Adim adim turetim: sonucu degil YOLU goster."""
    # Lagrange yontemiyle hareket denklemi istendiyse once o. Olculdu:
    # "lagrange ile sarkacin hareket denklemini turet" sorusu alakasiz
    # bir formulun cebirini gosteriyordu; ikinci sinif bir ogrencinin
    # istedigi sey L = T - V ve Euler-Lagrange uygulamasidir.
    try:
        from . import lagrange as _lag
        _met = _lag.turet(msg, lang)
        if _met:
            return Response(_met, kind="derivation",
                            extra={"konu_etiketi": "lagrange"})
    except Exception:
        pass

    # Once ILKELERDEN turetme zinciri var mi? Bohr enerjisini tek formulu
    # yeniden duzenleyerek "turetmek" dongusel bir islemdi (olculdu);
    # gercek turetim birden cok ilkeyi birlestirir.
    try:
        _anahtar, zincir = turetim.zincir_bul(msg)
        if zincir:
            metin = turetim.zincir_calistir(zincir, lang)
            if metin:
                return Response(metin, kind="derivation",
                                extra={"konu_etiketi": zincir["ad"]})
    except Exception:
        pass

    hits = _formul_sec(msg, lang, formulas.search(msg, limit=5))
    # ZAYIF formul eslesmesiyle turetim yapmak, alakasiz bir formulun
    # cebirini gostermek demektir. Olculdu: "lagrange ile sarkacin
    # hareket denklemini turet" sorusu "Isi iletimi (Fourier)"
    # formulunun adim adim cozumunu getirdi — 17 puanlik bir eslesme,
    # oysa konu aramasi 54 puanla titresimleri buluyordu.
    _konu_vurus = knowledge.search(msg, limit=1)
    _konu_skor = _konu_vurus[0][0] if _konu_vurus else 0
    if hits and hits[0][0] < 25 and _konu_skor >= 25:
        return h_konu(msg, lang, ctx)
    if not hits:
        return h_konu(msg, lang, ctx)
    _skor, f = hits[0]

    # Hangi degisken icin? Once kullanicinin adiyla andigi degiskeni ara.
    hedef = None
    n = nlu.norm(msg)
    for sym, (tr_ad, en_ad, _u) in f["vars"].items():
        adaylar = []
        for ad in (tr_ad, en_ad):
            for kelime in nlu.norm(ad or "").split():
                # Esik 3'tu: "hiz" (3 harf) eleniyor ve "hizi adim adim
                # turet" sorusunda yanlis degisken seciliyordu (olculdu).
                if len(kelime) >= 3:
                    adaylar.append(kelime)
        for kok in adaylar:
            if re.search(r"(?<!\w)%s\w{0,4}(?!\w)" % re.escape(kok), n):
                hedef = sym
                break
        if hedef:
            break
    if hedef is None:
        # Belirtilmediyse denklemin sol tarafindaki buyukluk
        hedef = (f["eq"].split("=")[0].strip()
                 if "=" in f["eq"] else list(f["vars"])[0])
        if hedef not in f["vars"]:
            hedef = list(f["vars"])[0]

    metin = turetim.rapor(f, hedef, lang)
    if not metin:
        return h_formul(msg, lang, ctx)

    # Ilgili ikinci bir formul varsa birlestirme turetimini de ekle
    if len(hits) > 1:
        ikinci = hits[1][1]
        ek = turetim.birlesim_raporu(f, ikinci, lang)
        if ek:
            metin += "\n\n---\n\n" + ek
    return Response(metin, kind="derivation",
                    extra={"konu_etiketi": f["tr"] if lang == "tr" else f["en"]})


def h_formul(msg, lang, ctx):
    # Once TAM PROBLEM cozumunu dene: soruda karar olcutu ("kayar mi") ve
    # yeterli veri varsa cevabi dogrudan uret. Formul listeleyip "degerleri
    # verirseniz hesaplarim" demek, degerler soruda varken bir cevap
    # degildir (olculdu).
    try:
        tam = problem.coz(msg, lang)
    except Exception:
        tam = None
    # DIKKAT: denetim iki dilde de calismali. Olculdu: Ingilizce
    # oturumda cozum uretiliyor ama basligi "Result" oldugu icin
    # "Sonuç" araniyor ve cozum atiliyordu — ODTU gibi Ingilizce
    # egitim yapan bir bolumde ogrenci hicbir sayisal cevap alamiyordu.
    # Denetim, cozumun BICIMINE degil VARLIGINA bakmali: iki adimli
    # devre cozumunde "Sonuç" basligi yok ama "## `I` = ..." satiri var
    # ve cevap tam olarak budur (olculdu: cozum uretildigi halde
    # atiliyor, yerine yanlis isaretli tek-baginti sonucu basiliyordu).
    # Cozucunun KASITLI reddi de bir cevaptir: "negatif kutle olmaz",
    # "bu toplama yapilamaz", "tek bagintiyla cozemedim". Olculdu:
    # "-5 kg kutleli cismin kinetik enerjisi" sorusunda cozucu dogru
    # uyariyi uretti ama sonuc satiri olmadigi icin atildi ve yerine
    # formul listesi basildi.
    _kasitli_ret = tam and any(x in tam for x in (
        "fiziksel değil", "not physical", "yapılamaz", "not valid",
        "tek bağıntıyla çözemedim", "more than one relation"))
    if tam and ("Sonuç" in tam or "Result" in tam
                or re.search(r"^## `", tam, re.M) or _kasitli_ret):
        return Response(tam, kind="solution")

    # Tek baginti yetmediyse COK ADIMLI zincirlemeyi dene: aranan
    # buyuklugu veren bagintiyi bul, onun eksiklerini de ureterek geri
    # git. Olculdu: "10 m yuksekten birakilan 2 kg cismin yere carparken
    # kinetik enerjisi" tek bagintiyla cozulemiyordu.
    try:
        from . import zincir as _zin
        _cok = _zin.coz(msg, lang)
    except Exception:
        _cok = None
    if _cok:
        # KENDI COZDUGUNDEN OGREN. Zincir bir problemi adim adim cozup
        # her adimi dogruladiysa, izledigi yol bir COZUM SEMASIDIR.
        # Ayni boyut imzasina sahip yeni bir problem geldiginde bu yol
        # once denenir. Kullanicinin istegi buydu: "aralarinda baglanti
        # kurarak daha once hic gormedigi sorulari da cozebilsin".
        try:
            from . import problemler as _prb2, zincir as _zn2
            _yol = []
            for _f in formulas.FORMULAS:
                if _f["tr"] and _f["tr"] in _cok:
                    _yol.append(_f["id"])
            if len(_yol) >= 2:
                _prb2.sema_kaydet(msg, _yol, _f.get("topic", ""), msg[:200])
        except Exception:
            pass
        return Response(_cok, kind="solution")

    knowns_raw = nlu.extract_known_values(msg)
    hits = _formul_sec(msg, lang, formulas.search(msg, limit=5))
    # Kullanici "m=2 kg" yazmaz, "kutlesi 2 kg" yazar. Sembol biciminde bir
    # deger bulunamadiysa, secilen formulun kendi degisken adlariyla dogal
    # dilden okumayi deniyoruz.
    if not knowns_raw and hits:
        try:
            knowns_raw = nlu.formul_degerleri(hits[0][1], msg)
        except Exception:
            knowns_raw = {}
    if not hits:
        # bilinen degiskenlerden formul tahmin et
        if knowns_raw:
            hits = formulas.search(" ".join(knowns_raw.keys()), limit=3)
    if not hits:
        return h_konu(msg, lang, ctx)

    score, f = hits[0]

    # Bilinen degerleri SI'ye cevir
    knowns = {}
    unit_notes = []
    for name, (val, unit) in knowns_raw.items():
        if name not in f["vars"]:
            continue
        if unit:
            si, dim = units.to_si(val, unit)
            if si is not None:
                target_unit = f["vars"][name][2]
                tu = units.parse_unit(target_unit) if target_unit else None
                if tu and tu[1] != dim:
                    unit_notes.append(L(lang,
                                        "`%s` icin verdiginiz birim (%s, %s) formulun "
                                        "bekledigi boyutla (%s) uyusmuyor."
                                        % (name, unit, units.dim_label(dim),
                                           units.dim_label(tu[1])),
                                        "The unit you gave for `%s` (%s, %s) does not "
                                        "match the expected dimension (%s)."
                                        % (name, unit, units.dim_label(dim),
                                           units.dim_label(tu[1]))))
                knowns[name] = si
            else:
                knowns[name] = val
        else:
            knowns[name] = val

    # Sabitleri otomatik doldur. Yalnizca sembolun o sabiti gosterdigi
    # dogrulanirsa: `Q = m*c*dT` formulundeki `c` ozgul isidir, isik hizi
    # degil — sembol eslesmesine guvenmek yanlis hesap uretiyordu.
    auto = []
    for sym in f["vars"]:
        if sym in knowns:
            continue
        if _sabit_uygun(f, sym):
            knowns[sym] = units.CONSTANTS[sym][0]
            auto.append(sym)

    lines = [("### " + (f["tr"] if lang == "tr" else f["en"]))]
    lines.append("## `%s`" % f["eq"])
    lines.append("")

    unknown = [s for s in f["vars"] if s not in knowns]

    if len(unknown) == 1 and len(knowns) >= 1 and knowns_raw:
        target = unknown[0]
        try:
            tvar, sols, eq = formulas.solve_for(f, knowns, target=target)
        except Exception as e:
            sols = None
        if sols:
            tname, tname_en, tunit = f["vars"][target]
            label = tname if lang == "tr" else tname_en
            lines.append(L(lang, "**Verilenler:**", "**Given:**"))
            for k in sorted(knowns):
                if k in auto:
                    continue
                nm = f["vars"][k][0] if lang == "tr" else f["vars"][k][1]
                lines.append("- `%s` = %s %s  (%s)"
                             % (k, units.fmt(knowns[k]), f["vars"][k][2], nm))
            if auto:
                lines.append(L(lang, "\n_Otomatik kullanilan sabitler: %s_",
                               "\n_Constants filled automatically: %s_")
                             % ", ".join("`%s = %s`" % (a, units.fmt(units.CONSTANTS[a][0]))
                                         for a in auto))
            # Sembolik duzenleme
            try:
                rearr = formulas.symbolic_rearrange(f, target)
                if rearr:
                    lines.append(L(lang, "\n**Bilinmeyen icin duzenlenmis hali:**",
                                   "\n**Rearranged for the unknown:**"))
                    for rr in rearr[:2]:
                        lines.append("`%s = %s`" % (target, rr))
            except Exception:
                pass
            lines.append("")
            real = [s for s in sols if isinstance(s, float)]
            if real:
                for s in real:
                    shown = units.fmt(s, 8) + ((" " + tunit) if tunit else "")
                    lines.append("## `%s` = **%s**" % (target, shown))
                    # Alternatif birimler
                    if tunit:
                        pu = units.parse_unit(tunit)
                        if pu:
                            alts = []
                            for cand in units.suggest_units(pu[1]):
                                if cand == tunit:
                                    continue
                                cv, err = units.convert(s, tunit, cand)
                                if cv is not None and 1e-3 < abs(cv) < 1e6:
                                    alts.append("`%s %s`" % (units.fmt(cv, 5), cand))
                                if len(alts) >= 4:
                                    break
                            if alts:
                                lines.append(L(lang, "= %s", "= %s") % " = ".join(alts))
                    lines.append("")
                lines.append(L(lang, "_Aranan buyukluk: %s_", "_Quantity solved for: %s_")
                             % label)
            else:
                lines.append(L(lang, "Cozum: %s", "Solution: %s")
                             % ", ".join(str(s) for s in sols))
            if unit_notes:
                lines.append(L(lang, "\n⚠️ **Birim uyarisi:**", "\n⚠️ **Unit warning:**"))
                for n in unit_notes:
                    lines.append("- " + n)
            return Response("\n".join(lines), kind="formula")

    # Sadece formulu tanit
    lines.append(L(lang, "**Degiskenler:**", "**Variables:**"))
    for sym, (t, e, u) in f["vars"].items():
        lines.append("- `%s` — %s%s" % (sym, t if lang == "tr" else e,
                                        (" *[%s]*" % u) if u else ""))
    note = f.get("note_tr" if lang == "tr" else "note_en")
    if note:
        lines.append("\n> " + note)

    # Her degisken icin duzenlenmis hali
    try:
        lines.append(L(lang, "\n**Her bilinmeyen icin duzenlenmis hali:**",
                       "\n**Rearranged for each variable:**"))
        for sym in list(f["vars"])[:6]:
            try:
                rr = formulas.symbolic_rearrange(f, sym)
                if rr:
                    lines.append("- `%s = %s`" % (sym, rr[0]))
            except Exception:
                continue
    except Exception:
        pass

    lines.append(L(lang,
                   "\n💡 Degerleri verirseniz hesaplarim. Ornek: `%s`",
                   "\n💡 Give values and I'll compute. Example: `%s`")
                 % _example_query(f, lang))

    if len(hits) > 1:
        lines.append(L(lang, "\n**Ilgili formuller:**", "\n**Related formulas:**"))
        for _, g in hits[1:4]:
            lines.append("- %s: `%s`" % (g["tr"] if lang == "tr" else g["en"], g["eq"]))
    return Response("\n".join(lines), kind="formula")


def _example_query(f, lang):
    syms = list(f["vars"].keys())
    parts = []
    for s in syms[:-1]:
        u = f["vars"][s][2]
        parts.append("%s=2%s" % (s, (" " + u) if u else ""))
    return " ".join(parts) + " " + (f["tr"] if lang == "tr" else f["en"]).lower()


# -------------------------------------------------------------------- konu
def h_konu(msg, lang, ctx):
    query = nlu.strip_command_words(msg) or msg
    detay = bool(ctx.get("detay"))
    lines = []
    used_any = False

    # 1) Cekirdek bilgi tabani
    cekirdek_skor = 0
    hits = knowledge.search(query, limit=3)
    if hits and hits[0][0] >= 20:
        score, t = hits[0]
        cekirdek_skor = score
        used_any = True
        lines.append("### " + (t["tr_title"] if lang == "tr" else t["en_title"]))
        lines.append("")
        lines.append(t["tr"] if lang == "tr" else t["en"])
        if t["eqs"]:
            lines.append(L(lang, "\n**Temel bagintilar:**", "\n**Key relations:**"))
            for e in t["eqs"]:
                lines.append("- `%s`" % e)
        ex = t["ex_tr"] if lang == "tr" else t["ex_en"]
        if ex:
            lines.append(L(lang, "\n**Ornekler:**", "\n**Worked examples:**"))
            for i, e in enumerate(ex, 1):
                lines.append("%d. %s" % (i, e))
        if t["related"]:
            rel = [knowledge.get(k) for k in t["related"]]
            rel = [r for r in rel if r]
            if rel:
                lines.append(L(lang, "\n**Ilgili konular:** %s", "\n**Related topics:** %s")
                             % ", ".join("*%s*" % (r["tr_title"] if lang == "tr"
                                                   else r["en_title"]) for r in rel))

    # 2a) Cekirdek konu yoksa, ogrenilenlerden yapilandirilmis sayfa uret.
    #     Bu sayede "aciklayabildigim konu" sayisi makaleler geldikce artar.
    if not used_any:
        m = sentez.malzeme(query, lang)
        if sentez.aciklanabilir_mi(m):
            metin = sentez.sayfa(m, lang, detay=detay)
            metin += L(lang,
                       "\n\n_Bu sayfayı okuduğum makalelerden ve kavram "
                       "ağımdan derledim; çekirdek anlatımlarımdan biri değil._",
                       "\n\n_I assembled this page from papers I've read and my "
                       "concept graph; it is not one of my built-in topics._")
            # "sentez" isareti: bu sayfa cekirdek anlatim DEGIL, okunan
            # makalelerden derlendi. Dil modeli metni yeniden yazsa bile
            # bu durustluk notu cevabin sonunda kalmali (olculdu: model
            # rewrite'i notu siliyordu ve sayfa cekirdek bilgi gibi
            # gorunuyordu).
            return Response(metin, kind="topic",
                            extra={"konu_etiketi": m["ad"][:60],
                                   "sentez": True})

    # 2) Ogrenilmis kavramlar (Wikipedia)
    concepts = retrieval.search_concepts(query, limit=3, lang=lang)
    if not concepts:
        concepts = retrieval.search_concepts(query, limit=3)
    # FTS her sorguya bir sey dondurur; "izafiyet teorisi" sorgusuna gelen
    # "Efektif alan teorisi" gibi yalnizca ortak genel sozcuk tasiyan
    # eslesmeleri eliyoruz.
    concepts = [k for k in concepts
                if _relevant(query, (k.get("name") or "") + " " +
                             (k.get("definition") or ""))]
    if not concepts:
        w = retrieval.wiki_lookup(query, lang=lang)
        # Wikipedia arama motoru her sorguya bir sey dondurur; alakasiz
        # sonuclari (ornegin bir birim cevirme sorusuna gelen bir ulke maddesi)
        # elemek icin baslik ile sorgunun ortak kelimesi olmasini sart kosuyoruz.
        if w and _relevant(query, w["title"] + " " + w.get("extract", "")[:200]):
            concepts = [{"name": w["title"], "definition": w.get("description", ""),
                         "extract": w["extract"], "url": w["url"], "lang": lang}]

    if concepts:
        top = concepts[0]
        if not used_any:
            lines.append("### %s" % top["name"])
            lines.append("")
            body = top.get("extract") or top.get("definition") or ""
            sents = retrieval.summarize([body], query=query, max_sentences=6)
            lines.append(" ".join(sents) if sents else body)
            used_any = True
        else:
            body = top.get("extract") or ""
            sents = retrieval.summarize([body], query=query, max_sentences=2)
            if sents:
                lines.append(L(lang, "\n**Ansiklopedik tanim:** ",
                               "\n**Encyclopedic definition:** ") + " ".join(sents))
        if top.get("url"):
            lines.append("\n<span class='meta'>%s</span>" % top["url"])

        rel = retrieval.related_concepts(top["name"], limit=6)
        rel = [r for r in rel if r["weight"] > 1]
        if rel:
            lines.append(L(lang, "\n**Ogrendigim baglantilar:** %s",
                           "\n**Learned associations:** %s")
                         % ", ".join("%s" % r["name"] for r in rel[:6]))

        # "Biraz daha ac" dendiyse maddenin tamamini canli okuyup, ozette
        # gecmeyen ek bolumleri getiriyoruz — ayni metni tekrarlamak yerine.
        if detay:
            uzun = retrieval.deep_read(top["name"], lang=top.get("lang") or lang,
                                       chars=7000)
            if uzun and len(uzun) > len(top.get("extract") or "") + 200:
                ek = uzun[len(top.get("extract") or ""):]
                sents = retrieval.summarize([ek], query=query, max_sentences=7)
                if sents:
                    lines.append(L(lang, "\n### Ayrıntılar", "\n### Further detail"))
                    for s in sents:
                        lines.append("- " + s)

    # 3) Makaleleri inceleyerek cikardigim bulgular
    bulgular = retrieval.insights(query, limit=6 if detay else 4,
                                  turler=("tanim", "bulgu", "iliski", "sayisal"))
    if bulgular:
        used_any = True
        etiket = {"tanim": L(lang, "tanım", "definition"),
                  "bulgu": L(lang, "bulgu", "finding"),
                  "yontem": L(lang, "yöntem", "method"),
                  "sayisal": L(lang, "sayısal", "quantitative"),
                  "iliski": L(lang, "ilişki", "relation")}
        lines.append(L(lang, "\n### Makaleleri incelerken öğrendiklerim",
                       "\n### What I learned from studying papers"))
        # Once tanimlar, sonra bulgular
        sira = {"tanim": 0, "bulgu": 1, "iliski": 2, "sayisal": 3, "yontem": 4}
        for b in sorted(bulgular, key=lambda x: sira.get(x["tur"], 9)):
            c = b["cumle"]
            if len(c) > 260:
                c = c[:257].rsplit(" ", 1)[0] + "…"
            lines.append("- <span class='meta'>[%s]</span> %s"
                         % (etiket.get(b["tur"], b["tur"]), c))

    # Makalelerden ogrenilen bagintilar — cekirdek formul tabaninda olmayan,
    # yalnizca literaturden gelen denklemler
    eqs = bagintilar.ara(query, limit=5)
    if eqs:
        used_any = True
        lines.append(L(lang, "\n### Makalelerden öğrendiğim bağıntılar",
                       "\n### Relations learned from papers"))
        for e in eqs:
            isaret = " ✓" if e["cozulebilir"] else ""
            lines.append("- `%s`%s <span class='meta'>%s</span>"
                         % (e["latex"], isaret, (e["baglam"] or "")[:70]))
        lines.append(L(lang,
                       "_✓ işaretliler sembolik olarak çözümlenebiliyor._",
                       "_✓ marked ones can be parsed symbolically._"))

    iliskiler = retrieval.relations(query, limit=5)
    if iliskiler:
        lines.append(L(lang, "\n**Kurduğum ilişkiler:** %s",
                       "\n**Relations I inferred:** %s")
                     % " · ".join("%s → *%s* → %s" % (r["a"], r["fiil"], r["b"])
                                  for r in iliskiler))

    # 4) Guncel arastirmadan destek
    papers = retrieval.search_papers(query, limit=10 if detay else 6)
    if len(papers) < 2:
        live = retrieval.live_lookup(query, lang=lang, limit=5)
        papers = (papers + live)[:6]
    # ALAN SUZGECI. Olculdu: "gokyuzu neden mavi" sorusuna icinde "mavi
    # kart" gecen bir vatandaslik hukuku makalesi getirildi. Tek bir
    # ortak kelime, alakasiz bir kaynagi cevaba sokabiliyor. Kaynak
    # metni fizik/kimya/biyoloji ile ilgili degilse kullanilmaz.
    from .learner import fizik_ilgili as _alan
    _suzulmus = []
    for _p in papers:
        _m = (_p.get("title") or "") + " " + (_p.get("abstract") or "")
        try:
            if _alan(_m):
                _suzulmus.append(_p)
        except Exception:
            _suzulmus.append(_p)
    if _suzulmus:
        papers = _suzulmus
    elif papers:
        papers = []          # hicbiri alanla ilgili degil: hic kullanma
    if papers:
        n_ab = 7 if detay else 4
        abstracts = [p["abstract"] for p in papers[:n_ab] if p.get("abstract")]
        sents = retrieval.summarize(abstracts, query=query,
                                    max_sentences=6 if detay else 3)
        if sents:
            used_any = True
            lines.append(L(lang, "\n### Guncel arastirmalardan",
                           "\n### From current research"))
            for s in sents:
                lines.append("- " + s)
        lines.append(_fmt_sources(papers, lang, limit=6 if detay else 4))

    if not used_any:
        # Cekirdek konu ve kavram yoksa formul tabani hala yardimci olabilir:
        # "ozgul isi" bir konu basligi degil ama bir formulun degiskeni.
        fh = formulas.search(query, limit=1)
        if fh and fh[0][0] >= 25:
            return h_formul(query, lang, ctx)
        return Response(L(lang,
                          "Bu konuda henuz yeterli bilgim yok. Ogrenme motoru "
                          "calisiyorsa zamanla ogrenecegim.\n\n"
                          "Su an sunlari deneyebilirsiniz: `konulari listele`, "
                          "`yardim`, ya da daha genel bir terim.",
                          "I don't have enough on this yet. If the learning engine "
                          "is running I'll pick it up over time.\n\n"
                          "Try `list topics`, `help`, or a broader term."))

    lines.append(L(lang,
                   "\n💡 `%s ornek ver` yazarak cozumlu problem isteyebilir, "
                   "`%s matlab kodu` ile simulasyon alabilirsiniz."
                   % (query[:40], query[:40]),
                   "\n💡 Ask `%s example` for a worked problem, or `%s matlab code` "
                   "for a simulation." % (query[:40], query[:40])))
    # Cekirdek anlatim guclu eslesmisse bunu isaretle: dil modeli boyle bir
    # cevabi "serbest" sayip yeniden yazmamali. Olculdu: "density of
    # states" sorusu Istatistiksel Mekanik konusuyla eslesiyordu ama
    # cevap yerine model "The context provided does not include
    # information..." yaziyordu.
    return Response("\n".join(lines), kind="topic",
                    extra={"cekirdek_skor": cekirdek_skor})


_PROBLEM_SETI = re.compile(
    r"\b(problem seti|soru seti|alistirma|alıştırma|calisma sorulari|"
    r"bolum sonu|odev seti|problem set|exercises|practice problems)\b",
    re.I)


def h_problem_seti(msg, lang, ctx):
    """Ders kitabi tarzi kademeli problem seti."""
    from . import problemseti as _pset
    konu = nlu.strip_command_words(
        _PROBLEM_SETI.sub(" ", msg)).strip(" ?.!,")
    if not konu and ctx.get("last_subject"):
        konu = ctx["last_subject"]
    metin = _pset.uret(konu or msg, lang)
    if not metin:
        return h_ornek(msg, lang, ctx)
    return Response(metin, kind="problem_set",
                    extra={"konu_etiketi": konu[:60] if konu else None})


def h_ornek(msg, lang, ctx):
    adet = _istenen_adet(msg)
    query = nlu.strip_command_words(
        re.sub(r"\b(ornek|ver|goster|uret|uretmeni|istiyorum|problem|soru|coz|"
               r"alistirma|toplam|adet|tane|cevap|cevaplari|cevaplariyla|"
               r"cozum|cozumleri|birlikte|ile|alani|alaninda|alakali|"
               r"example|give|me|a|problem|practice|exercise|show|generate|"
               r"with|answers|solutions|total|about|related|field|please|"
               r"\d+)\b", " ", msg, flags=re.I))
    query = re.sub(r"\s+", " ", query).strip(" ?.!,")

    # "10 adet soru" gibi bir istek varsa cok sayida problem uret
    if adet:
        cok = _coklu_problem(adet, query, lang)
        if cok:
            return Response(cok, kind="example",
                            extra={"konu_etiketi": query[:60] if query else
                                   ("fizik problemleri" if lang == "tr"
                                    else "physics problems")})

    query = query or (ctx.get("last_topic") or "")
    if not query:
        return Response(L(lang, "Hangi konuda ornek istersiniz?",
                          "Which topic would you like an example on?"))

    hits = knowledge.search(query, limit=2)
    lines = []
    if hits:
        t = hits[0][1]
        ex = t["ex_tr"] if lang == "tr" else t["ex_en"]
        lines.append("### " + L(lang, "Ornek: ", "Example: ")
                     + (t["tr_title"] if lang == "tr" else t["en_title"]))
        lines.append("")
        for i, e in enumerate(ex, 1):
            lines.append("**%d.** %s\n" % (i, e))
        if t["eqs"]:
            lines.append(L(lang, "**Kullanilan bagintilar:** %s",
                           "**Relations used:** %s")
                         % ", ".join("`%s`" % e for e in t["eqs"][:4]))

    # Formul tabanindan sayisal ornek uret
    fhits = formulas.search(query, limit=1)
    if fhits:
        f = fhits[0][1]
        gen = _problem_uret(f, lang, random.Random())
        if gen:
            lines.append("\n---\n")
            lines.append(gen)

    if not lines:
        return Response(L(lang, "Bu konuda hazir ornegim yok, ama formul verirseniz "
                                "hesaplayabilirim.",
                          "I don't have a ready example, but give me a formula and "
                          "I can compute."))
    return Response("\n".join(lines), kind="example")


# Buyuklugun boyutuna gore makul deger araligi. Her seye 1-50 arasi sayi
# vermek "kesit alani = 22.86 m^2" gibi fiziksel olarak sacma sorular
# uretiyordu.
_ARALIKLAR = {
    units.D(m=1): (0.2, 25),                  # uzunluk
    units.D(kg=1): (0.5, 20),                 # kutle
    units.D(s=1): (0.5, 60),                  # zaman
    units.D(m=2): (0.01, 5),                  # alan
    units.D(m=3): (0.001, 2),                 # hacim
    units.D(m=1, s=-1): (2, 60),              # hiz
    units.D(m=1, s=-2): (1, 20),              # ivme
    units.D(kg=1, m=1, s=-2): (5, 500),       # kuvvet
    units.D(kg=1, m=2, s=-2): (10, 5000),     # enerji
    units.D(kg=1, m=2, s=-3): (10, 2000),     # guc
    units.D(kg=1, m=-1, s=-2): (1e4, 5e5),    # basinc
    units.D(K=1): (250, 600),                 # sicaklik
    units.D(s=-1): (1, 500),                  # frekans
    units.D(A=1): (0.1, 10),                  # akim
    units.D(A=1, s=1): (1e-6, 1e-3),          # yuk
    units.D(kg=1, m=2, s=-3, A=-1): (1.5, 240),      # gerilim
    units.D(kg=1, m=2, s=-3, A=-2): (1, 1000),       # direnc
    units.D(kg=-1, m=-3, s=4, A=2): (1e-9, 1e-3),    # sigma
    units.D(kg=1, m=2, s=-2, A=-2): (1e-3, 1.0),     # induktans
    units.D(kg=1, s=-2, A=-1): (0.01, 2),            # manyetik alan
    units.D(kg=1, m=-3): (500, 8000),                # yogunluk
    units.D(kg=1, m=1, s=-1): (1, 200),              # momentum
    units.D(mol=1): (0.1, 5),                        # mol
}


# Boyut tabanli genel araliklar atom/cekirdek/gorelilik olceginde cokuyor:
# foton frekansi 38 Hz, is fonksiyonu kilojoule cikinca soru anlamsizlasiyor.
# Bu formuller icin degiskene ozel aralik veriliyor. (lo, hi) ya da
# (lo, hi, "int") biciminde.
_ME = 9.1093837139e-31
_OZEL_ARALIK = {
    # --- kuantum ---
    ("foton", "f"): (3e14, 3e16), ("foton", "E"): (1e-19, 1e-17),
    ("foton_lam", "lam"): (2e-7, 9e-7), ("foton_lam", "E"): (2e-19, 1e-18),
    ("fotoelektrik", "f"): (5e14, 3e15),
    ("fotoelektrik", "W"): (2e-19, 9e-19),
    ("fotoelektrik", "Ek"): (1e-20, 5e-19),
    ("debroglie", "m"): (_ME, _ME), ("debroglie", "v"): (1e5, 5e7),
    ("debroglie", "lam"): (1e-11, 1e-9),
    ("belirsizlik", "dx"): (1e-12, 1e-9),
    ("belirsizlik", "dp"): (1e-26, 1e-22),
    ("kutu_enerji", "n"): (1, 5, "int"), ("kutu_enerji", "m"): (_ME, _ME),
    ("kutu_enerji", "L"): (5e-10, 5e-9), ("kutu_enerji", "E"): (1e-20, 1e-17),
    ("bohr_E", "Z"): (1, 3, "int"), ("bohr_E", "n"): (1, 5, "int"),
    ("bohr_E", "E"): (-13.6, -0.5),
    ("rydberg", "Z"): (1, 2, "int"), ("rydberg", "n1"): (1, 3, "int"),
    ("rydberg", "n2"): (4, 8, "int"), ("rydberg", "lam"): (1e-7, 2e-6),
    # --- cekirdek ---
    ("yari_omur", "N0"): (1e18, 1e22), ("yari_omur", "N"): (1e16, 1e20),
    ("yari_omur", "t"): (1e2, 1e9), ("yari_omur", "T"): (1e2, 1e9),
    ("bozunma_sabiti", "T"): (1e2, 1e9),
    ("bozunma_sabiti", "lambda_"): (1e-9, 1e-2),
    ("aktivite", "lambda_"): (1e-9, 1e-2), ("aktivite", "N"): (1e18, 1e22),
    ("kutle_kusuru", "dm"): (1e-29, 1e-27),
    # --- gorelilik: hiz isik hizina yakin olmali ---
    ("lorentz_gama", "v"): (3e7, 2.9e8),
    ("zaman_genlesme", "v"): (3e7, 2.9e8),
    ("zaman_genlesme", "dt0"): (1, 100),
    ("boy_kisalma", "v"): (3e7, 2.9e8), ("boy_kisalma", "L0"): (1, 100),
    ("rel_enerji", "v"): (3e7, 2.9e8), ("rel_enerji", "m"): (1e-27, 5),
    ("enerji_momentum", "m"): (1e-27, 5),
    ("enerji_momentum", "p"): (1e-19, 1e-16),
    # --- gok mekanigi ---
    ("yorunge_hiz", "M"): (1e22, 2e30), ("yorunge_hiz", "r"): (1e6, 1e12),
    ("kacis_hiz", "M"): (1e22, 2e30), ("kacis_hiz", "r"): (1e6, 1e9),
    ("kepler3", "a"): (1e9, 1e13), ("kepler3", "M"): (1e29, 2e30),
    ("schwarzschild", "M"): (1e24, 1e32),
    # --- boyutsuz oranlar: 0-1 arasi olmali ---
    ("surtunme", "mu"): (0.05, 0.9), ("stefan", "eps"): (0.1, 1.0),
    ("carnot", "eta"): (0.15, 0.65), ("verim", "eta"): (0.2, 0.9),
    ("verim", "Pout"): (10, 800), ("verim", "Pin"): (900, 2000),
    ("snell", "n1"): (1.0, 1.6), ("snell", "n2"): (1.0, 2.4),
    ("paralel_plaka", "epsr"): (1.0, 10.0),
    # --- malzeme / devre buyuklukleri ---
    ("isi", "c"): (120, 4200), ("gizli_isi", "L"): (2e4, 2.5e6),
    ("isi_iletim", "k"): (0.1, 400), ("isi_iletim", "L"): (1e-3, 0.5),
    ("isi_iletim", "A"): (0.01, 2), ("isi_iletim", "dT"): (5, 100),
    ("isi_iletim", "t"): (10, 3600),
    ("hooke", "k"): (10, 2000), ("hooke", "x"): (0.01, 0.5),
    ("yay_enerji", "k"): (10, 2000), ("yay_enerji", "x"): (0.01, 0.5),
    ("yay_sarkac", "k"): (10, 2000), ("sarkac", "L"): (0.1, 3),
    ("telde_hiz", "T"): (5, 500), ("telde_hiz", "mu"): (1e-4, 0.1),
    ("solenoid", "n"): (100, 5000), ("tel_B", "r"): (0.01, 1),
    ("rlc", "L"): (1e-6, 1), ("rlc", "C"): (1e-12, 1e-3),
    ("direnc_tel", "rho"): (1e-8, 1e-6), ("direnc_tel", "A"): (1e-8, 1e-4),
    ("direnc_tel", "L"): (0.1, 100),
    ("cift_yarik", "d"): (2e-6, 5e-5), ("cift_yarik", "lam"): (4e-7, 7e-7),
    ("cift_yarik", "m"): (1, 3, "int"),
    ("cift_yarik", "theta"): (0.01, 0.15),
    ("kirinim", "a"): (2e-6, 5e-5), ("kirinim", "lam"): (4e-7, 7e-7),
    ("kirinim", "m"): (1, 3, "int"),
    ("kirinim", "theta"): (0.01, 0.15),
    ("ses_siddet", "I"): (1e-8, 1e-2), ("ses_siddet", "I0"): (1e-12, 1e-12),
    ("reynolds", "mu"): (1e-5, 0.1),
    ("rms_hiz", "m"): (1e-27, 1e-25), ("rms_hiz", "T"): (200, 1000),
    ("cyclotron", "m"): (1e-30, 1e-26), ("cyclotron", "B"): (0.01, 2),
    ("kutu_enerji", "h"): None,   # sabit olarak doldurulur
}
_OZEL_ARALIK = {k: v for k, v in _OZEL_ARALIK.items() if v is not None}

# Negatif cikamayacak buyuklukler (boyutlarina gore)
_POZITIF_BOYUTLAR = {
    units.D(m=1), units.D(kg=1), units.D(s=1), units.D(m=2), units.D(m=3),
    units.D(K=1), units.D(s=-1), units.D(kg=1, m=-3), units.D(mol=1),
    units.D(kg=1, m=2, s=-3, A=-2),
}


def _sabit_uygun(f, sym):
    """`sym` bu formulde gercekten o fiziksel sabiti mi gosteriyor?

    Sembol eslesmesi tek basina yeterli degil: `Q = m*c*dT` formulundeki `c`
    ozgul isidir, isik hizi degil. Degiskenin adiyla sabitin tanimi ortusmeli.
    """
    if sym not in units.CONSTANTS:
        return False
    etiket = nlu.norm(f["vars"][sym][0] or "")
    aciklama = nlu.norm(units.CONSTANTS[sym][3] or "")
    if not etiket or not aciklama:
        return False
    if etiket in aciklama or aciklama in etiket:
        return True
    a = set(w for w in etiket.split() if len(w) > 3)
    b = set(w for w in aciklama.split() if len(w) > 3)
    return len(a & b) >= 2


def _yuvarla(v):
    """Anlamli basamakla yuvarla.

    Duz ondalik yuvarlama iki ucta da bozuluyordu: 3.2e-19 sifira iniyor,
    9e20 ise 21 haneli bir tam sayi olarak yaziliyordu.
    """
    if v == 0:
        return 0.0
    a = abs(v)
    if a >= 1e6 or a < 1e-3:
        return float("%.4g" % v)
    if a >= 100:
        return round(v)
    if a >= 1:
        return round(v, 3)
    return float("%.4g" % v)


def _makul_deger(unit_str, rng, fid=None, sym=None):
    """Birime uygun, gerceklige yakin bir deger uret."""
    ozel = _OZEL_ARALIK.get((fid, sym)) if fid else None
    if ozel:
        lo, hi = ozel[0], ozel[1]
        if len(ozel) > 2 and ozel[2] == "int":
            return rng.randint(int(lo), int(hi))
        if lo == hi:
            return lo
        if lo > 0 and hi / lo > 500:
            import math as _m
            return _yuvarla(_m.exp(rng.uniform(_m.log(lo), _m.log(hi))))
        return _yuvarla(rng.uniform(lo, hi))

    u = (unit_str or "").strip()
    if u in ("rad", "radyan"):
        return round(rng.uniform(0.2, 1.4), 3)
    if not u:
        return round(rng.uniform(0.2, 5), 2)
    p = units.parse_unit(u)
    aralik = _ARALIKLAR.get(p[1]) if p else None
    if aralik is None:
        aralik = (1, 50)
    lo, hi = aralik
    if hi / max(lo, 1e-30) > 500:      # cok genis aralik -> logaritmik sec
        import math as _m
        v = _m.exp(rng.uniform(_m.log(lo), _m.log(hi)))
    else:
        v = rng.uniform(lo, hi)
    return _yuvarla(v)


def _iliskilendir(f, knowns, rng):
    """Birbirine bagli buyuklukleri tutarli hale getir.

    Bagimsiz uretilen degerler bazi formullerde anlamsiz sonuc veriyordu:
    yari omru 6e8 s olan bir ornekte 9e7 s degil de 9e14 s beklemek, kalan
    cekirdek sayisini sifira indiriyordu.
    """
    fid = f["id"]
    if fid in ("yari_omur",):
        if "T" in knowns and "t" in knowns:
            knowns["t"] = _yuvarla(knowns["T"] * rng.uniform(0.5, 4))
        if "N0" in knowns and "N" in knowns:
            knowns["N"] = _yuvarla(knowns["N0"] * rng.uniform(0.1, 0.8))
    elif fid == "verim":
        if "Pin" in knowns and "Pout" in knowns:
            knowns["Pout"] = _yuvarla(knowns["Pin"] * rng.uniform(0.2, 0.9))
    elif fid == "carnot":
        if "Th" in knowns and "Tc" in knowns:
            knowns["Tc"] = _yuvarla(knowns["Th"] * rng.uniform(0.3, 0.85))
    elif fid == "sureklilik":
        pass
    elif fid in ("zaman_genlesme",):
        if "dt" in knowns and "dt0" in knowns:
            knowns["dt"] = _yuvarla(knowns["dt0"] * rng.uniform(1.2, 5))
    elif fid == "boy_kisalma":
        if "L0" in knowns and "L" in knowns:
            knowns["L"] = _yuvarla(knowns["L0"] * rng.uniform(0.2, 0.9))
    return knowns


def _problem_uret(f, lang, rng, numara=None, deneme=5):
    """Mantik denetimine takilirsa farkli degerlerle yeniden dener.

    Ornegin Carnot formulunde soguk kaynak hedef secilir ve verim 1'den buyuk
    uretilirse sicaklik negatif cikar; boyle bir soruyu vermek yerine
    degerleri yeniliyoruz.
    """
    for _ in range(deneme):
        p = _generate_problem(f, lang, seed=rng.randrange(10 ** 6), numara=numara)
        if p:
            return p
    return None


def _generate_problem(f, lang, seed=None, numara=None):
    """Formulden rastgele ama makul sayilarla cozumlu problem uret."""
    # Gercekten sabit olan degiskenler soru metninde "verilen" degil "sabit"
    # olarak gosterilir; digerleri (ornegin ozgul isi `c`) normal degiskendir.
    syms = [s for s in f["vars"] if not _sabit_uygun(f, s)]
    if len(syms) < 2:
        return None
    rng = random.Random(seed if seed is not None else random.randrange(10 ** 9))
    # Hedef degisken donusumlu secilir: hep sonuncusu olsaydi sorular
    # birbirinin ayni kaliba dokulmus hali olurdu. Kuantum sayilari gibi tam
    # sayili buyuklukler hedef olamaz — cozum kesirli cikip anlamsizlasir.
    adaylar = [s for s in syms
               if not (_OZEL_ARALIK.get((f["id"], s), ()) or ())[2:3] == ("int",)]
    if not adaylar:
        adaylar = syms
    target = adaylar[(seed or 0) % len(adaylar)]
    knowns = {}
    for s in syms:
        if s == target:
            continue
        knowns[s] = _makul_deger(f["vars"][s][2], rng, f["id"], s)
    for s in f["vars"]:
        if s not in knowns and s != target and _sabit_uygun(f, s):
            knowns[s] = units.CONSTANTS[s][0]
    # Sabit sayilmayan ama hala eksik olan degiskenleri de doldur
    for s in f["vars"]:
        if s not in knowns and s != target:
            knowns[s] = _makul_deger(f["vars"][s][2], rng, f["id"], s)
    _iliskilendir(f, knowns, rng)
    try:
        _, sols, _ = formulas.solve_for(f, knowns, target=target)
    except Exception:
        return None
    real = [s for s in sols if isinstance(s, float)]
    if not real:
        return None
    # Ikinci dereceden denklemlerde hem +v hem -v cikar; fiziksel olani pozitif
    pozitif = [s for s in real if s > 0]
    cevap = pozitif[0] if pozitif else real[0]
    # Mantik denetimi: fiziksel olarak imkansiz bir cevap ureten soruyu
    # kullaniciya vermiyoruz (negatif kutle, negatif sure, sonsuz deger ...).
    if cevap != cevap or cevap in (float("inf"), float("-inf")):
        return None
    if abs(cevap) > 1e40 or (cevap != 0 and abs(cevap) < 1e-40):
        return None
    hedef_birim = units.parse_unit(f["vars"][target][2] or "")
    if cevap < 0 and hedef_birim and hedef_birim[1] in _POZITIF_BOYUTLAR:
        return None
    # sin/cos icin cozulen acilar [-1,1] disina cikmis olabilir
    if "aci" in (f["vars"][target][0] or "").lower() and abs(cevap) > 6.3:
        return None

    name = f["tr"] if lang == "tr" else f["en"]
    hedef_ad = f["vars"][target][0] if lang == "tr" else f["vars"][target][1]

    if numara:
        lines = ["#### %d. %s  <span class='meta'>%s</span>"
                 % (numara, name, f["topic"])]
    else:
        lines = [L(lang, "### Uretilen problem: %s",
                   "### Generated problem: %s") % name]
    lines.append("")
    lines.append(L(lang,
                   "**Soru.** Aşağıdaki değerler verildiğine göre %s (`%s`) "
                   "değerini bulun." % (hedef_ad, target),
                   "**Question.** Given the values below, find the %s (`%s`)."
                   % (hedef_ad, target)))
    lines.append("")
    for s in syms:
        if s == target:
            continue
        nm = f["vars"][s][0] if lang == "tr" else f["vars"][s][1]
        u = f["vars"][s][2]
        lines.append("- %s (`%s`) = %s%s" % (nm, s, knowns[s],
                                             (" " + u) if u else ""))
    sabitler = [s for s in f["vars"] if _sabit_uygun(f, s)]
    if sabitler:
        lines.append("- " + L(lang, "_sabitler:_ ", "_constants:_ ")
                     + ", ".join("`%s = %s %s`"
                                 % (s, units.fmt(units.CONSTANTS[s][0], 5),
                                    units.CONSTANTS[s][1])
                                 for s in sabitler))
    lines.append("")
    lines.append(L(lang, "**Çözüm.**", "**Solution.**"))
    lines.append("")
    lines.append("1. " + L(lang, "Kullanılacak bağıntı: ", "Relation to use: ")
                 + "`%s`" % f["eq"])
    try:
        rr = formulas.symbolic_rearrange(f, target)
        if rr:
            lines.append("2. " + L(lang, "`%s` için düzenle: ",
                                   "Rearrange for `%s`: ")
                         % target + "`%s = %s`" % (target, rr[0]))
    except Exception:
        pass
    lines.append("3. " + L(lang, "Değerleri yerine koy ve hesapla.",
                           "Substitute and compute."))
    lines.append("")
    birim = f["vars"][target][2]
    lines.append(L(lang, "**Cevap:** `%s` = **%s%s**", "**Answer:** `%s` = **%s%s**")
                 % (target, units.fmt(cevap, 6), (" " + birim) if birim else ""))
    return "\n".join(lines)


# ---------------------------------------------------- coklu soru uretimi
_ADET_RE = [
    re.compile(r"(\d{1,2})\s*(?:adet|tane)?\s*(?:soru|problem|ornek|question|"
               r"alistirma|exercise)"),
    re.compile(r"(?:soru|problem|ornek|question)\s*(?:sayisi)?\s*[:=]?\s*(\d{1,2})"),
    re.compile(r"(\d{1,2})\s*(?:adet|tane)"),
]


def _istenen_adet(msg):
    """'toplam 10 adet' -> 10. Istenmemisse None."""
    t = nlu.norm(msg)
    for rx in _ADET_RE:
        m = rx.search(t)
        if m:
            try:
                n = int(m.group(1))
            except (TypeError, ValueError):
                continue
            if n >= 2:
                return min(n, 25)      # makul bir ust sinir
    return None


def _problem_havuzu(query, rng):
    """Soru uretilecek formulleri sec; konu belirtilmemisse alanlara yay."""
    hits = formulas.search(query, limit=10) if query else []
    if hits and hits[0][0] >= 30:
        havuz = [f for _, f in hits]
    else:
        havuz = []
    # Konulara gore dengeli dagit: 10 soru istendiginde hepsi kinematikten
    # gelmesin.
    konulara = {}
    for f in formulas.FORMULAS:
        konulara.setdefault(f["topic"], []).append(f)
    for lst in konulara.values():
        rng.shuffle(lst)
    konular = sorted(konulara)
    rng.shuffle(konular)
    i = 0
    while any(konulara.values()) and i < 2000:
        t = konular[i % len(konular)]
        if konulara[t]:
            f = konulara[t].pop()
            if f not in havuz:
                havuz.append(f)
        i += 1
    return havuz


def _coklu_problem(n, query, lang):
    rng = random.Random()
    havuz = _problem_havuzu(query, rng)
    parcalar = []
    for f in havuz:
        if len(parcalar) >= n:
            break
        p = _problem_uret(f, lang, rng, numara=len(parcalar) + 1)
        if p:
            parcalar.append(p)
    if not parcalar:
        return None
    tr = lang == "tr"
    bas = ["### " + (("%d fizik sorusu ve çözümleri" % len(parcalar)) if tr
                     else ("%d physics problems with solutions" % len(parcalar)))]
    if len(parcalar) < n:
        bas.append("")
        bas.append(("_İstediğiniz %d sorudan %d tanesini üretebildim._"
                    % (n, len(parcalar))) if tr else
                   ("_I could generate %d of the %d requested._"
                    % (len(parcalar), n)))
    bas.append("")
    bas.append(("Değerler her seferinde yeniden üretilir; aynı soruyu tekrar "
                "isterseniz farklı sayılarla gelir." if tr else
                "Values are regenerated each time; ask again for a fresh set."))
    bas.append("")
    return "\n\n---\n\n".join(["\n".join(bas)] + parcalar)


# ------------------------------------------------------------------ makale
def h_makale(msg, lang, ctx):
    query = nlu.strip_command_words(
        re.sub(r"\b(makale|makaleler|makalede|arastirma|arastirmalar|yayin|"
               r"yayinlar|calisma|calismalar|bul|bulur musun|ara|tara|goster|"
               r"hakkinda|konusunda|ile ilgili|uzerine|dair|neler|ne|diyor|"
               r"diyorlar|yaziyor|var|soyluyor|son|guncel|yeni|literatur|"
               r"paper|papers|article|articles|study|studies|find|search|"
               r"show|about|on|recent|latest|say|says|literature|"
               r"what do|what does|tell)\b", " ", msg, flags=re.I))
    query = re.sub(r"\s+", " ", query).strip(" ?.!,")
    if not query:
        return Response(L(lang, "Hangi konuda makale arayayim?",
                          "What topic should I search for?"))

    papers = retrieval.search_papers(query, limit=10)
    live = []
    if len(papers) < 5:
        live = retrieval.live_lookup(query, lang=lang, limit=8)
        seen = set(p.get("ext_id") for p in papers)
        papers = papers + [p for p in live if p.get("ext_id") not in seen]

    if not papers:
        return Response(L(lang,
                          "Bu konuda makale bulamadim. Farkli/daha genel bir terim "
                          "deneyin ya da Ingilizce arayin.",
                          "I couldn't find papers on this. Try a different or broader "
                          "term."))

    lines = [L(lang, "### '%s' konusunda %d makale",
               "### %d papers on '%s'") % ((query, len(papers)) if lang == "tr"
                                           else (len(papers), query))]
    if live:
        lines.append(L(lang, "_(%d tanesi az once internetten cekildi ve ogrenildi)_",
                       "_(%d of these were just fetched from the internet and learned)_")
                     % len(live))
    lines.append("")

    abstracts = [p["abstract"] for p in papers[:5] if p.get("abstract")]
    sents = retrieval.summarize(abstracts, query=query, max_sentences=4)
    if sents:
        lines.append(L(lang, "**Ortak bulgu ozeti:**", "**Synthesis of findings:**"))
        for s in sents:
            lines.append("- " + s)
        lines.append("")

    terms = retrieval.key_terms(abstracts, top=8, query=query)
    if terms:
        lines.append(L(lang, "**One cikan terimler:** %s", "**Key terms:** %s")
                     % ", ".join("`%s`" % t for t, _ in terms))
        lines.append("")

    lines.append(L(lang, "**Makaleler:**", "**Papers:**"))
    for i, p in enumerate(papers[:8], 1):
        title = (p.get("title") or "").strip()
        url = p.get("url") or ""
        auth = (p.get("authors") or "").split(";")[0].strip()
        year = (p.get("published") or "")[:4]
        meta = " · ".join(x for x in (auth, year, p.get("source", "")) if x)
        head = "[%s](%s)" % (title, url) if url else title
        lines.append("%d. **%s**  \n   <span class='meta'>%s</span>" % (i, head, meta))
        ab = (p.get("abstract") or "")
        if ab:
            one = retrieval.summarize([ab], query=query, max_sentences=1)
            if one:
                snip = one[0]
                lines.append("   > %s" % (snip[:280] + ("..." if len(snip) > 280 else "")))
    return Response("\n".join(lines), kind="papers")


# ------------------------------------------------------------------ matlab
def h_matlab(msg, lang, ctx):
    # "matlab kodu yazar misin" cumlesinin kendi konusu yoktur; konu bir
    # onceki turdadir. Olculdu: aksiyon potansiyeli anlatildiktan sonra
    # gelen bu istek "isin izleme" sablonunu getiriyordu. Yalnizca mesaj
    # SADECE bir kod istegiyse onceki konuyu basa ekliyoruz.
    _tasinan = (ctx.get("carried_subject") or ctx.get("last_subject") or "").strip()
    if _tasinan:
        _ic = re.sub(r"\b(matlab|octave|kod|kodu|kodunu|yaz|yazar|yazsana|"
                     r"misin|musun|bunun|bunu|bana|lutfen|simulasyon|"
                     r"simule|simulasyonu|goster|code|write|please)\b",
                     " ", nlu.norm(msg))
        _ic = re.sub(r"\s+", " ", nlu.strip_command_words(_ic)).strip()
        if len(_ic) < 4:
            msg = "%s %s" % (_tasinan, msg)
            # Konu etiketi FIZIK konusu kalmali. Aksi halde bir sonraki
            # "sayisal ornek" istegi "Fizikte MATLAB Kullanimi" konusuna
            # gidiyordu (olculdu).
            ctx["kod_konusu"] = _tasinan

    hit = matlab.search_template(msg)
    if hit:
        key, t = hit
        title = t["tr"] if lang == "tr" else t["en"]
        notes = t["notes_tr"] if lang == "tr" else t["notes_en"]
        lines = ["### MATLAB / Octave — %s" % title]
        lines.append("")
        lines.append("```matlab\n%s```" % matlab.localize(t["code"], lang))
        if notes:
            lines.append("\n> **%s** %s" % (L(lang, "Not:", "Note:"), notes))
        # Kodun ne yaptigini anlat: kullanici "sadece kod veriyor" demisti.
        # Anlatim kodun kendi bolum basliklarindan turetilir.
        ack = matlab.aciklama(key, lang)
        if ack:
            lines.append("")
            lines.append(ack)
        lines.append(L(lang,
                       "\n_Kodu kopyalayip MATLAB veya GNU Octave'a yapistirin._",
                       "\n_Copy into MATLAB or GNU Octave._"))
        _ek = {"language": "matlab"}
        if ctx.get("kod_konusu"):
            _ek["konu_etiketi"] = ctx["kod_konusu"][:60]
        return Response("\n".join(lines), kind="code", extra=_ek)

    # Formule dayali kod — yalnizca guclu bir eslesme varsa. Zayif eslesmede
    # kod uretmek, alakasiz bir formulun kodunu vermek demektir.
    fhits = formulas.search(msg, limit=1)
    if fhits and fhits[0][0] >= 45:
        f = fhits[0][1]
        code = matlab.from_formula(f, lang)
        return Response("### MATLAB / Octave — %s\n\n```matlab\n%s\n```"
                        % (f["tr"] if lang == "tr" else f["en"], code),
                        kind="code", extra={"language": "matlab"})

    # Genel ifade
    expr = nlu.extract_expression(
        re.sub(r"\b(matlab|octave|kod|kodu|yaz|uret|olustur|script|program|"
               r"code|write|generate|for|icin)\b", " ", msg, flags=re.I))
    # Yalnizca gercekten bir matematik ifadesiyse koda cevir. Aksi halde
    # "bana sifirdan matlab ogretebilir misin" gibi bir cumle, anlamsiz bir
    # MATLAB satirina donusuyordu.
    if expr and nlu.looks_like_expression(expr):
        try:
            code = matlab.generic_from_expression(expr, lang=lang)
            return Response(L(lang, "### MATLAB / Octave kodu",
                              "### MATLAB / Octave code")
                            + "\n\n```matlab\n%s\n```" % code,
                            kind="code", extra={"language": "matlab"})
        except Exception:
            pass

    # Somut bir kod istegi cikmadi. Buraya "matlab nedir", "bana matlab anlat"
    # gibi sorular duser; bunlara sablon listesi degil, ne yapabildigimi
    # anlatan bir cevap dogru olan.
    return h_yetenek(msg, lang, ctx)


# ============================================================== yonlendirici
def h_yol_haritasi(msg, lang, ctx):
    """'Nereden baslamaliyim', 'yol haritasi cikar', 'ne ogretebilirsin'."""
    path = curriculum.find(msg)
    if path:
        # "4. asamayi biraz daha acar misin" -> tum haritayi tekrar basmak
        # yerine yalnizca o asamayi genisleterek anlat
        n = curriculum.stage_number(msg)
        if n:
            tek = curriculum.render_stage(path, n, lang)
            if tek:
                return Response(tek, kind="roadmap",
                                extra={"remember": {"last_stage": n},
                                       "konu_etiketi": path["tr"] if lang == "tr"
                                       else path["en"]})
        text = curriculum.render(path, lang)
        text += L(lang,
                  "\n\n---\n\nBir aşamayı derinleştirmek isterseniz o aşamanın "
                  "adını yazmanız yeterli; ayrıca `%s` diyerek başka bir yol "
                  "haritası isteyebilirsiniz.",
                  "\n\n---\n\nTo go deeper into a stage, just name it. You can "
                  "also ask for another roadmap with `%s`.") % L(
            lang, "yol haritaları", "roadmaps")
        return Response(text, kind="roadmap",
                        extra={"konu_etiketi": path["tr"] if lang == "tr"
                               else path["en"]})

    # Hangi konuda olduğu belli değil: ne öğretebileceğini anlat
    lines = [L(lang, "### Size ne öğretebilirim", "### What I can teach you")]
    lines.append("")
    # Yol haritasi sayisi sabit degil: genisleme motoru yeterli makale
    # biriken her fizik alani icin yenisini uretiyor.
    yollar = curriculum.list_paths(lang)
    uretilmis = sum(1 for pth in curriculum.PATHS.values()
                    if pth.get("uretilmis"))
    lines.append(L(lang,
                   "**%d yol haritam** var (%d tanesini okuduğum "
                   "makalelerden kendim oluşturdum). Hangisini istediğinizi "
                   "yazın, aşama aşama planı çıkarayım:"
                   % (len(yollar), uretilmis),
                   "I have **%d roadmaps** (%d of them built from the papers "
                   "I have read). Say which one you want:"
                   % (len(yollar), uretilmis)))
    lines.append("")
    for key, ad in yollar:
        # Cagri etiketi olarak haritanin ilk anahtar kelimesini kullaniyoruz:
        # "kuantum yol haritasi" yazmak "kuantum mekaniği yol haritasi"
        # yazmaktan kolay ve find() ikisini de buluyor.
        pth = curriculum.PATHS.get(key, {})
        cagri = (pth.get("kw") or [key])[0] if key.startswith("uretilmis:") \
            else key
        lines.append("- **%s** — `%s yol haritasi`" % (ad, cagri) if lang == "tr"
                     else "- **%s** — `%s roadmap`" % (ad, cagri))
    lines.append("")
    lines.append(L(lang, "**Bunların dışında şunları yapabilirim:**",
                   "**Beyond those I can:**"))
    lines.append("")
    lines.append(L(lang,
        "- **%d konuyu** ayrıntılı anlatırım (%d çekirdek + %s makalelerden "
        "öğrendiğim), çözümlü örnek veririm\n"
        "- **%d fizik formülünü** herhangi bir değişkeni için çözerim "
        "(%d çekirdek + %d kendi türettiğim, hepsi doğrulanmış)\n"
        "- Türev, integral, limit, diferansiyel denklem, matris hesaplarım\n"
        "- Birim çevirir, boyut denetimi yaparım\n"
        "- MATLAB/Octave kodu üretirim\n"
        "- Öğrendiğim **%s makale özetinde** literatür taraması yaparım"
        % (len(knowledge.TOPICS) + _ogrenilen_konu(), len(knowledge.TOPICS),
           "{:,}".format(_ogrenilen_konu()), len(formulas.FORMULAS),
           len(formulas.FORMULAS) - _turetilmis_formul(), _turetilmis_formul(),
           "{:,}".format(db.stats()["makale"])),
        "- Explain **%d topics** in depth (%d core + %s learned from papers)\n"
        "- Solve **%d physics formulas** for any variable "
        "(%d core + %d I derived myself, all verified)\n"
        "- Do derivatives, integrals, limits, ODEs and matrices\n"
        "- Convert units with dimensional checking\n"
        "- Generate MATLAB/Octave code\n"
        "- Search literature across **%s** learned abstracts"
        % (len(knowledge.TOPICS) + _ogrenilen_konu(), len(knowledge.TOPICS),
           "{:,}".format(_ogrenilen_konu()), len(formulas.FORMULAS),
           len(formulas.FORMULAS) - _turetilmis_formul(), _turetilmis_formul(),
           "{:,}".format(db.stats()["makale"]))))
    return Response("\n".join(lines), kind="roadmap")


# Bu niyetlerde cevap dogrudan dogrulanmis motordan gelir; dil modeli
# araya girip sayilari yeniden yazmamali.
_DIL_DISI_NIYETLER = frozenset((
    "hesap", "denklem", "turev", "integral", "limit", "seri", "diferansiyel",
    "matris", "vektor", "birim", "sabit", "formul", "matlab", "durum",
    "kendini_dogrula", "beni_unut", "profil", "kendini_tanit", "yol_haritasi",
))


def h_kopru(msg, lang, ctx):
    """Iki kavram arasindaki iliskiyi soran sorular.

    Olculdu: "klasik kinetik enerji formulunden cikarak Hamiltonyan
    operatorunun kinetik enerji kismini ispatlar misin" sorusuna
    yalnizca `Ek = mv²/2` karti donuyordu — cumlenin geri kalani hic
    okunmuyordu. Soru BUTUN olarak okunmali; bkz. kopru.py.
    """
    from . import kopru as _kopru
    metin = ctx.get("kopru_metin") or _kopru.coz(msg, lang)
    if not metin:
        return h_konu(msg, lang, ctx)

    # OGRENILMIS kopru (korpustan cikarilmis) govdesi ham alintilardan
    # olusur ve cogu Ingilizcedir. Bunu oldugu gibi basmak Turkce soran
    # ogrenciye bir cevap degil, malzeme yigini vermektir; dil katmani da
    # bunu "yabanci alinti yigini" sayip metni tamamen atiyor ve kendi
    # bilgisinden yaziyordu (olculdu: cevap dogruydu ama kaynaklar
    # iklimlendirme makaleleriydi).
    #
    # Dogrusu bu projenin kurali: MODEL DILI KURAR, OLGULARI KAYNAK VERIR.
    # Modele YALNIZCA dogrulanmis kopru metnini baglam olarak veriyoruz.
    ogrenilmis = ("bağımsız kaynaktan kendim" in metin
                  or "independent sources" in metin)
    if ogrenilmis and dil.MODEL.kurulu_mu():
        try:
            akici = dil.MODEL.yanitla(msg, baglam=metin, lang=lang)
            if akici and len(akici) > 80:
                # Durustluk notu her hâlukârda kalir.
                not_ = [s for s in metin.split("\n") if s.startswith("_")]
                metin = akici + ("\n\n" + not_[-1] if not_ else "")
        except Exception:
            pass
    return Response(metin, kind="topic",
                    extra={"konu_etiketi": nlu.strip_command_words(msg)[:60],
                           "dil_modeli": True if ogrenilmis else None})


HANDLERS = {
    "kopru": h_kopru,
    "yol_haritasi": h_yol_haritasi,
    "yetenek": h_yetenek, "kendini_dogrula": h_kendini_dogrula,
    "karsilastir": h_karsilastir, "neden": h_neden, "nasil": h_nasil,
    "profil": h_profil, "beni_unut": h_beni_unut,
    "kendini_tanit": h_kendini_tanit,
    "turetim": h_turetim,
    "ogrendiklerim": h_ogrendiklerim,
    "selam_gunluk": h_selam, "selam": h_selam, "tesekkur": h_tesekkur,
    "onay": h_onay, "yardim": h_yardim,
    "problem_seti": h_problem_seti,
    "durum": h_durum, "liste": h_liste,
    "hesap": h_hesap, "denklem": h_denklem, "turev": h_turev,
    "integral": h_integral, "limit": h_limit, "seri": h_seri,
    "diferansiyel": h_diferansiyel, "matris": h_matris, "vektor": h_vektor,
    "birim": h_birim, "sabit": h_sabit, "formul": h_formul,
    "konu": h_konu, "ornek": h_ornek, "makale": h_makale, "matlab": h_matlab,
}


# Bir sonraki soruda hemen okunabilmesi icin oturum baglami bellekte tutulur;
# kalicilik icin ayrica kuyruk uzerinden diske yazilir.
_SESSION_MEM = {}

# "Bunu biraz daha acar misin", "peki ya o", "ornek ver" gibi devam sorulari
_ANAPHORA = re.compile(
    r"\b(bunu|bunun|buna|bundan|bu|sunu|sunun|suna|su|onu|onun|ona|ondan|o|"
    r"bunlar|onlar|peki|ayrica|devam|devamini|daha|biraz|tekrar|yine|ayni|"
    r"bahsettigin|dedigin|soyledigin|yukaridaki|onceki|az once|konuyu|konuda|"
    r"it|this|that|these|those|more|further|continue|again|above|previous|same)\b")

# Devam sorusunu tek basina olusturabilen komutlar ("matlab kodu yaz",
# "ornek ver", "kaynak goster" ...). Sonda gelen emir fiili istege baglidir.
_BARE_FOLLOWUP = re.compile(
    r"^(ornek|detay(li)?|devam|daha( fazla)?|acikla|anlat|ozetle|ozet|"
    r"matlab( kodu)?|kod(u)?|formul(u)?|kaynak(lar)?|makale(ler)?|"
    r"example|more|continue|detail(s)?|explain|code|source(s)?|paper(s)?|"
    r"summary|summarize)"
    r"(\s+(ver|yaz|goster|olustur|uret|bul|ara|it|me|please|lutfen))*\.?\??$")

# Daha derin anlatim isteyen ifadeler
_DEEPEN = re.compile(
    r"\b(daha (fazla|detayli|ayrintili)|biraz daha|detaylandir|genislet|ac(ar|sana)|"
    r"derinlestir|uzun uzun|ayrintili anlat|in more detail|elaborate|expand|"
    r"go deeper|tell me more)\b")


def _kendi_konusu_var_mi(message):
    """Mesajin kendine ait bir fizik konusu var mi?

    "entropi tam olarak neyi olcuyor biraz acar misin" cumlesi zamir
    tasidigi icin devam sorusu saniliyordu; oysa kendi konusu (entropi) var.
    """
    kalan = _ANAPHORA.sub(" ", nlu.norm(message))
    kalan = nlu.strip_command_words(kalan)
    kalan = re.sub(r"\b(olcuyor|olcer|anlamadim|anlamiyorum|acar|acsana|"
                   r"misin|miyim|nedir|neyi|nasil|neden|tam|olarak|biraz|"
                   r"means|measure|understand)\b", " ", kalan)
    # YON kelimeleri bir KONU degildir. "bir ornek verir misin" cumlesinde
    # "ornek" konu sanilyordu ve devam sorusu reddediliyordu; sohbet
    # boylece konudan sapiyordu (olculdu).
    kalan = re.sub(r"\b(ornek|ornegi|ornekle|formul|formulu|denklem|"
                   r"denklemi|baginti|bagintisi|sonuc|sonuclari|kanit|"
                   r"deney|deneysel|tarih|kesif|detay|ayrinti|"
                   r"verir|ver|neydi|nelerdir|hangileri|"
                   r"sayisal|sayilarla|hesapli|"
                   r"var|yok|midir|mi|mu|hangi|kac|"
                   r"example|formula|equation|result|evidence)\b",
                   " ", kalan)
    kalan = re.sub(r"\s+", " ", kalan).strip()
    # Geriye anlamli bir sey kalmadiysa mesajin kendi konusu yoktur.
    # Olculdu: "bunun formulu var mi" cumlesinden geriye "var mi"
    # kaliyor, bu da ogrenilmis bir kavrama eslesip mesaji "kendi
    # konusu var" saydiriyordu; devam sorusu boylece kaciriliyordu.
    if len(kalan) < 4:
        return False
    if knowledge.search(kalan, limit=1) and knowledge.search(kalan, limit=1)[0][0] >= 20:
        return True
    if formulas.search(kalan, limit=1) and formulas.search(kalan, limit=1)[0][0] >= 30:
        return True
    if units.find_constant(kalan):
        return True
    try:
        if retrieval.search_concepts(kalan, limit=1):
            return True
    except Exception:
        pass
    return False


# Devam sorusunun hangi YONU sordugunu belirleyen ipuclari
_YON_IPUCU = [
    ("sonuc", r"\b(sonuc|sonuclari|neye yol acar|ne demek oluyor|"
              r"consequence|implication)\w*"),
    ("ornek", r"\b(ornek|ornekle|gunluk hayat|nerede kullanilir|example)\w*"),
    ("formul", r"\b(formul|denklem|baginti|nasil hesaplanir|equation)\w*"),
    ("kanit", r"\b(kanit|deney|nasil biliyoruz|nasil olculur|evidence)\w*"),
    ("tarih", r"\b(kim buldu|nasil buldu|nasil bulundu|nasil kesfedildi|"
              r"kim gelistirdi|hangi yil|tarih|ne zaman|kesif|history|"
              r"who found|how was it discovered)\w*"),
    # Kisi yonu: "onun hayati", "kimdir", "projeleri" — fizikci
    # biyografilerine gider. Olculdu: "onun hayati hakkinda bilgi ver"
    # sorusu konunun tanimini birebir tekrar ediyordu.
    ("kisi", r"\b(hayati|hayatini|yasami|biyografi|kimdir|kim bu|"
             r"projeleri|calismalari|biography|who is)\w*"),
    ("neden", r"\b(neden|nicin|sebebi|why)\w*"),
    ("detay", r"\b(daha da|biraz daha|detay|ayrintili|derinlemesine)\w*"),
]


def _kisi_konusu(metin):
    """Metinde adi gecen fizikcinin biyografi konusunu bul (yoksa None).

    Biyografi konularinin anahtari "_kim" ile biter; baslikta gecen soyadi
    ("einstein", "noether") sorguda geciyorsa o kisi kastediliyordur.
    """
    if not metin:
        return None
    n = nlu.norm(metin)
    for t in knowledge.TOPICS:
        if not t["key"].endswith("_kim"):
            continue
        adlar = [w for w in nlu.norm(t["en_title"]).split() if len(w) > 3]
        if any(re.search(r"(?<!\w)%s\w{0,3}(?!\w)" % re.escape(a), n)
               for a in adlar):
            return t
    return None


_KISI_IPUCU = re.compile(
    r"\b(kim|kimdir|kimdi|hayati|hayatini|yasami|biyografi|projeleri|"
    r"calismalari|ne yapti|neler yapti|nasil buldu|nasil bulmus|"
    r"kesfetti|hangi elementleri|who is|biography|life of)\w*")


def _kisi_sorusu(metin):
    """Mesaj gercekten O KISI hakkinda mi?

    Yalnizca soyadinin gecmesi yetmez: "newton yasalari" Newton'un
    hayatini degil, yasalari sorar (olculdu — biyografi donuyordu).
    Ya acik bir kisi ipucu olmali ("kimdir", "hayati", "ne yapti"),
    ya da konu aramasinin ilk siradaki sonucu zaten o biyografi olmali.
    """
    kt = _kisi_konusu(metin)
    if not kt:
        return None
    if _KISI_IPUCU.search(nlu.norm(metin or "")):
        return kt
    # Adi bir SABITTE ya da formulde geciyorsa soru kisiyi sormuyordur.
    # Olculdu: "planck sabiti" sorusu Max Planck'in biyografisine
    # gidiyordu.
    try:
        if units.find_constant(metin):
            return None
    except Exception:
        pass
    fv = formulas.search(metin, limit=1)
    if fv and fv[0][0] >= 45:
        return None
    vurus = knowledge.search(metin, limit=1)
    if vurus and vurus[0][1]["key"] == kt["key"]:
        return kt
    return None


def _ayni_cevap(a, b, esik=0.85):
    """Iki cevap pratikte ayni mi?

    Iki olcut birden: kelime ortusmesi ve ONEK icerme. Yalnizca ortusme
    bakmak yetmiyordu — ayni ders metninin kisaltilmis hali %84'te kalip
    "farkli cevap" sayiliyor, kullanici ise ayni metni tekrar goruyordu
    (olculdu).
    """
    na, nb = nlu.norm(a or ""), nlu.norm(b or "")
    if not na or not nb:
        return False
    kisa, uzun = (na, nb) if len(na) <= len(nb) else (nb, na)
    if len(kisa) >= 120 and kisa[:120] in uzun:
        return True
    ka, kb = set(na.split()), set(nb.split())
    ortak = len(ka & kb)
    return ortak / float(min(len(ka), len(kb))) >= esik


def _konu_notu(konu_kayit, konu, lang):
    """Malzemenin hangi cekirdek konudan geldigini yazan kisa satir.

    Baslikta kullanicinin kendi terimi duruyor ("gokyuzu mavi"); govde
    ise cekirdek konudan geliyor ("Isigin Sacilmasi"). Ogrenci nereye
    bakacagini bilmeli.
    """
    if not konu_kayit:
        return ""
    ad = (konu_kayit["tr_title"] if lang == "tr"
          else konu_kayit["en_title"])
    if nlu.norm(ad) == nlu.norm(konu or ""):
        return ""
    return ("\n\n_%s: **%s**_" % ("Kaynak konu" if lang == "tr"
                                   else "Source topic", ad))


def _yon_cevabi(message, konu, onceki_metin, lang, ctx):
    """Devam sorusunun sordugu YONU cevapla.

    Ayni dersi tekrar basmak yerine, sorulan yone (sonuclari, ornek,
    formul, kanit...) karsilik gelen bolumu getiriyoruz.
    """
    n = nlu.norm(message)
    yon = None
    for ad, kalip in _YON_IPUCU:
        if re.search(kalip, n):
            yon = ad
            break

    # Konu govdesinden ilgili paragrafi sec
    kv = knowledge.search(konu, limit=1)
    govde = ""
    konu_kayit = None
    if kv and kv[0][0] >= 20:
        konu_kayit = kv[0][1]
        govde = konu_kayit["tr"] if lang == "tr" else konu_kayit["en"]
        # Baslikta ham SORU CUMLESI gorunmesin. Olculdu: "### nernst
        # denklemini yazar misin — Cozumlu ornek" basligi cikiyordu.
        # Ama kullanicinin kendi terimi kisa ve duzgunse ("entropi") onu
        # koruyoruz; genis konu basligina cevirmek konu degistirilmis
        # izlenimi veriyor.
        _ham = konu.strip()
        _soru_gibi = (len(_ham.split()) > 3
                      or re.search(r"\b(nedir|misin|mi|nasil|neden|yazar|"
                                   r"verir|anlat)\b", nlu.norm(_ham)))
        if _soru_gibi:
            konu = (konu_kayit["tr_title"] if lang == "tr"
                    else konu_kayit["en_title"])

    # "Formul" istegi: konunun DOGRULANMIS bagintilari dogrudan verilir.
    # Paragraf secmek burada calismiyordu, cunku metin normalizasyonu
    # "=" isaretini atiyor ve denklem iceren paragraf bulunamiyordu
    # (olculdu: "nernst denklemini yazar misin" ayni ders metnini
    # tekrar bastiriyordu).
    if yon == "formul" and konu_kayit and konu_kayit.get("eqs"):
        baslik = "Bağıntılar" if lang == "tr" else "Relations"
        satirlar = ["### %s — %s" % (konu, baslik), ""]
        for e in konu_kayit["eqs"][:6]:
            satirlar.append("`%s`" % e)
            satirlar.append("")
        ornekler = (konu_kayit["ex_tr"] if lang == "tr"
                    else konu_kayit["ex_en"])
        if ornekler:
            satirlar.append("**%s**" % ("Sayılarla" if lang == "tr"
                                        else "With numbers"))
            satirlar.append("")
            satirlar.append(ornekler[0][:700])
        return "\n".join(satirlar)

    # Mesajda bir fizikcinin adi geciyorsa cevap ONCE o kisinin
    # kaydindan gelir: "peki einstein bunu nasil buldu" sorusuna konunun
    # tanimini tekrar etmek yerine Einstein'in nasil vardigini anlatmak
    # gerekir (olculdu).
    _adli = _kisi_sorusu(message)
    if _adli and yon in (None, "tarih", "kisi", "neden", "detay"):
        _gk = (_adli["tr"] if lang == "tr" else _adli["en"]).strip()
        _bas = _adli["tr_title"] if lang == "tr" else _adli["en_title"]
        if yon == "tarih":
            _par = [p.strip() for p in _gk.split("\n\n") if p.strip()]
            _sec = [p for p in _par if any(
                a in nlu.norm(p) for a in
                ("cozdugu problem", "yontemi", "problem", "18", "19", "20"))]
            if _sec:
                return "### %s — %s\n\n%s" % (
                    _bas, "Nasıl vardı" if lang == "tr" else "How he got there",
                    "\n\n".join(_sec[:3])[:2200])
        return "### %s\n\n%s" % (_bas, _gk[:2200])

    # "Kisi" yonu: "onun hayati", "projeleri neler" — once mesajda adi
    # gecen fizikci, yoksa konuyla anilan kisi, o da yoksa sohbette en
    # son konusulan kisi.
    if yon == "kisi":
        kt = (_kisi_konusu(message) or _kisi_konusu(konu)
              or _kisi_konusu(ctx.get("son_kisi") or ""))
        if kt:
            govde_k = (kt["tr"] if lang == "tr" else kt["en"]).strip()
            return "### %s\n\n%s" % (
                kt["tr_title"] if lang == "tr" else kt["en_title"],
                govde_k[:2200])

    # "Ornek" istegi: konunun KENDI cozumlu ornegi varsa once o gelir.
    # Makale baglamindan ornek derlemek konudan sapiyordu (olculdu:
    # ozel gorelilik ornegi yerine axion modelleri anlatildi).
    if yon == "ornek" and kv and kv[0][0] >= 20:
        t = kv[0][1]
        ornekler = t["ex_tr"] if lang == "tr" else t["ex_en"]
        if ornekler:
            baslik = "Çözümlü örnek" if lang == "tr" else "Worked example"
            return ("### %s — %s\n\n%s" % (konu, baslik, ornekler[0][:900])
                    + _konu_notu(t, konu, lang))

    if govde and yon:
        anahtar = {
            "sonuc": ("sonuc", "consequence", "yol acar"),
            "ornek": ("ornek", "example", "gunluk"),
            "formul": ("formul", "denklem", "="),
            "kanit": ("deney", "olcum", "gozlem"),
            "tarih": ("yil", "kesif", "einstein", "18", "19", "20"),
            "neden": ("cunku", "sebebi", "neden"),
            "kisi": ("dogdu", "hayat", "yil"),
        }.get(yon, ())
        paragraflar = [p.strip() for p in govde.split("\n\n") if p.strip()]
        secili = [p for p in paragraflar
                  if any(a in nlu.norm(p) for a in anahtar)]
        if secili:
            baslik = {"sonuc": "Sonuçları", "ornek": "Örnek",
                      "formul": "Bağıntılar", "kanit": "Deneysel dayanak",
                      "tarih": "Tarihçe", "neden": "Nedeni",
                      "kisi": "Kim",
                      "detay": "Ayrıntı"}.get(yon, "Devamı")
            return ("### %s — %s\n\n%s" % (konu, baslik,
                                            "\n\n".join(secili[:3]))
                    + _konu_notu(konu_kayit, konu, lang))

    # Paragraf secilemediyse dil modeline SORUYU ve konuyu ver
    if dil.MODEL.kurulu_mu():
        try:
            # Baglam once KONU GOVDESINDEN kurulur; makale aramasi
            # konudan sapabiliyor.
            bg = ("KONU: %s\n%s" % (konu, govde[:2500])) if govde else ""
            if not bg:
                bg = baglam.derle(konu + " " + message, lang)
            if bg and not baglam.bos_mu(bg):
                akici = dil.MODEL.yanitla(message, baglam=bg, lang=lang,
                                          gecmis=ctx.get("history"))
                # Modelin "elimde bu bilgi yok" demesi, dogrulanmis
                # anlatimi tekrar etmekten DAHA KOTUDUR. Olculdu:
                # "density of states" sorusunda yapilandirilmis
                # Istatistiksel Mekanik anlatimi yerine "The context
                # provided does not include information about the density
                # of states" donuyordu. Boyle bir cevap kabul edilmez.
                _bilmiyorum = ("context provided does not",
                               "does not include information",
                               "i don't have", "i do not have",
                               "no information", "bilgim yok",
                               "bilgi bulunmuyor", "yer almiyor",
                               "yer almıyor", "bulunmamaktadir",
                               "bulunmamaktadır")
                if akici and any(x in akici.lower() for x in _bilmiyorum):
                    akici = ""
                if akici and len(akici) > 40 and not _ayni_cevap(
                        onceki_metin, akici):
                    return akici
        except Exception:
            pass
    return None


def _followup_subject(message, ctx):
    """Devam sorusuysa onceki konuyu dondur, degilse None."""
    subj = (ctx.get("last_subject") or "").strip()
    if not subj:
        return None
    t = nlu.norm(message)
    if len(t.split()) > 14:
        return None
    # Icinde CEBIRSEL bir ifade olan mesaja onceki konuyu eklemek ifadeyi
    # bozuyor. Olculdu: onceki konu "entropi" iken "denklemi coz: 3x+1=7"
    # istegi "entropi denklemi coz 3x+1=7" olarak ayristirilip
    # "invalid syntax" veriyordu.
    if re.search(r"\d", t) and ("=" in message
                                or re.search(r"[+\-*/^]", message)):
        return None
    # Zamir sart degil: "bir ornek verir misin", "formulu neydi",
    # "deneysel olarak nasil biliyoruz" — hicbirinde zamir yok ama hepsi
    # onceki konunun DEVAMIDIR. Olculdu: bunlar bagimsiz soru sayilip
    # konudan sapiyordu (ozel gorelilik sorulurken axion anlatildi).
    _yon_ipuclu = (len(t.split()) <= 9
                   and any(re.search(kalip, t) for _ad, kalip in _YON_IPUCU))
    if not (_BARE_FOLLOWUP.match(t.strip()) or _ANAPHORA.search(t)
            or _yon_ipuclu):
        return None
    # Kendi konusu varsa bu bir devam sorusu degil, yeni bir sorudur
    if _kendi_konusu_var_mi(message):
        return None
    return subj


def respond(message, session="default", lang_override=None):
    """Bir mesaja cevap uret."""
    message = (message or "").strip()
    if not message:
        return Response("...")

    lang = lang_override or nlu.detect_lang(message)
    ctx = _load_context(session)

    # Kisisel bilgi ("adim ...", "lisans ogrencisiyim") her mesajda taranir;
    # boylece kullanici bunu ayrica bildirmek zorunda kalmaz.
    yeni_bilgi = profile.extract(message)
    profile.set_("soru_sayisi", int(profile.get("soru_sayisi", 0) or 0) + 1)
    ctx["profil"] = {"ad": profile.name(), "seviye": profile.level()}

    # Devam sorusu mu? "peki bunu biraz daha acar misin" gibi bir mesajin kendi
    # basina konusu yoktur; onceki konuyu basa ekleyip oyle siniflandiriyoruz.
    onceki = _followup_subject(message, ctx)
    etkin = message
    if onceki:
        # Zamirleri atip yalnizca komut kismini birakiyoruz; aksi halde
        # "bu konuda makale bul" sorgusu "entropi bu konuda" olarak aranirdi.
        kalan = re.sub(r"\s+", " ", _ANAPHORA.sub(" ", nlu.norm(message))).strip()
        etkin = (onceki + " " + kalan).strip()
        ctx["followup"] = True
        ctx["carried_subject"] = onceki
    if _DEEPEN.search(nlu.norm(message)):
        ctx["detay"] = True

    # --- Anlama katmani: yazim duzeltme, es anlam, soru tipi -----------------
    # Kullanicinin yazdigi bicim degil, ne demek istedigi uzerinden karar
    # veriyoruz: "entrpi neden artar" -> konu entropi, tip nedensel.
    coz = anlama.coz(etkin)
    ctx["anlama"] = coz
    if coz["esanlamlar"]:
        etkin = coz["genis"]        # "izafiyet" -> "gorelilik" karsiligiyla ara
    elif coz["duzeltmeler"]:
        etkin = coz["duzeltilmis"]

    intent, conf = nlu.classify(etkin)

    # Soru tipi, anahtar kelime siniflandirmasinin ustune biner: hesap/kod gibi
    # kesin niyetler korunur, ama genel bir "konu" sorusu ise tipe gore
    # ozellesir (neden / nasil / karsilastirma).
    if intent in ("konu", "genel") and conf < 80:
        tip = coz["tip"]
        if tip == "karsilastir" and coz["taraflar"]:
            intent = "karsilastir"
        elif tip == "neden":
            intent = "neden"
        elif tip == "nasil":
            intent = "nasil"
    elif (intent == "formul" and coz["tip"] == "nasil"
            and not nlu.extract_known_values(message)):
        # "carnot verimi nasil hesaplanir" bir deger sorusu degil, yontem
        # sorusudur: formulu basmak yerine adim adim anlatiyoruz.
        intent = "nasil"

    # "3. asamayi anlat": bir yol haritasi anlatildiktan sonra gelen asama
    # numarasi, konu aramasi degil o haritanin ilgili asamasi demektir.
    if (ctx.get("last_intent") == "yol_haritasi"
            and curriculum.stage_number(message)
            and intent not in ("beni_unut", "profil", "durum")):
        intent = "yol_haritasi"
        onceki = onceki or ctx.get("last_subject")
        if onceki:
            etkin = onceki + " " + message

    # Devam sorusu yalnizca zamirlerden olusuyorsa, onceki niyeti surdur
    if onceki and intent == "konu" and ctx.get("last_intent") in (
            "makale", "matlab", "formul", "ornek", "yol_haritasi"):
        if not nlu.classify(message)[1] >= 80:
            intent = ctx["last_intent"]

    # Formul niyeti: icinde sayi+degisken varsa hesaplamaya yonel
    if intent in ("konu", "hesap") and nlu.extract_known_values(message):
        if formulas.search(etkin, limit=1):
            intent = "formul"

    # ISPAT istegi ("goster ki", "ispatla", "turetiniz") turetim
    # yolundan gecer ama VARSAYIMLARI ayrica yazar. Bir turetimde en cok
    # atlanan sey, sonucun nerede gecerli oldugudur.
    try:
        from . import problemseti as _pset
        if _pset.ispat_istegi_mi(etkin):
            _isp = _pset.ispat(etkin, lang)
            if _isp:
                resp = Response(_isp, kind="derivation",
                                extra={"intent": "turetim"})
                _save_turn(session, message, resp.text, "turetim",
                           subject=nlu.strip_command_words(etkin)[:60])
                resp.extra["lang"] = lang
                return resp
    except Exception:
        pass

    # AYRINTILI COZUM yonergesi: "Her formulu turet, birim analizini
    # yap, sembolik coz, ... varsayimlari listele" gibi bir mesaj bir
    # KONU sorusu degil, bir onceki problem icin BICIM talebidir.
    # Olculdu: sistem bunu "Fizikte Sayisal Yontemler" konusu sanip
    # ders anlatti.
    try:
        from . import ayrintili as _ayr
        if _ayr.yonerge_mi(message):
            _hedef_soru = message
            if not re.search(r"\d", message):
                # Yonergenin kendi sayisi yok: onceki problemi cozuyoruz
                _onceki_soru = ""
                for _m in reversed(ctx.get("history") or []):
                    if _m.get("role") == "user" and re.search(
                            r"\d", _m.get("content") or ""):
                        _onceki_soru = _m["content"]
                        break
                _hedef_soru = _onceki_soru or (ctx.get("last_subject") or "")
            if _hedef_soru:
                _det = _ayr.coz(_hedef_soru, lang)
                if _det:
                    resp = Response(_det, kind="solution")
                    _save_turn(session, message, resp.text, "formul",
                               subject=nlu.strip_command_words(
                                   _hedef_soru)[:60])
                    resp.extra["intent"] = "formul"
                    resp.extra["lang"] = lang
                    return resp
            # Problem bulunamadiysa durustce sor
            resp = Response(L(lang,
                "Hangi problemi bu ayrıntıda çözmemi istiyorsunuz? "
                "Problemi yazarsanız her adımı istediğiniz biçimde "
                "yaparım: birim analizi, sembolik çözüm, sayısal çözüm, "
                "yerine koyarak doğrulama, varsayımlar ve hata "
                "kaynakları.",
                "Which problem should I solve in that detail?"),
                kind="chat")
            _save_turn(session, message, resp.text, "sohbet")
            resp.extra["intent"] = "sohbet"
            resp.extra["lang"] = lang
            return resp
    except Exception:
        pass

    # BOYUT denetimi: "1 kg + 30 metre + 22 cm" gibi bir ifade
    # toplanamaz. Olculdu: sistem yalnizca "1 kg = 1 (SI)" diye birim
    # cevrimi yapiyordu; oysa asil cevap toplamanin gecersiz oldugudur.
    try:
        from . import boyut as _byt
        _bd = _byt.coz(etkin, lang)
        if _bd:
            resp = Response(_bd, kind="calc")
            _save_turn(session, message, resp.text, "hesap")
            resp.extra["intent"] = "hesap"
            resp.extra["lang"] = lang
            return resp
    except Exception:
        pass

    # ONCUL cevabi: sorunun kendi ifadesi cevabi veriyorsa ("surtunmesiz
    # ... surtunme degeri") formule hic gitmeden soyle. Niyet ne olursa
    # olsun gecerlidir; boyle sorular cogu zaman "konu" diye siniflaniyor.
    try:
        _onc = problem.oncul_cevabi(etkin, lang)
        if _onc:
            # Soruda AYRICA hesaplanabilir bir buyukluk varsa onu da ver:
            # ogrenci "peki hiz neydi" diye tekrar sormak zorunda kalmasin.
            try:
                from . import zincir as _zn
                # Sorulan buyukluk oncul yuzunden sifir; DIGER buyuklugu
                # bulmak icin o ifadeyi metinden cikariyoruz. Aksi hâlde
                # hedef tespiti yine sifirlanan buyuklugu secer.
                _sade = problem.oncul_sadelestir(etkin) or etkin
                _ek = _zn.coz(_sade, lang)
            except Exception:
                _ek = None
            if _ek and "## `" in _ek:
                _onc += ("\n\n---\n\n" +
                         L(lang, "**Sorudaki diğer büyüklük**",
                           "**The other quantity in the problem**") +
                         "\n\n" + _ek)
            resp = Response(_onc, kind="solution")
            _save_turn(session, message, resp.text, "formul",
                       subject=nlu.strip_command_words(etkin)[:60])
            resp.extra["intent"] = "formul"
            resp.extra["lang"] = lang
            return resp
    except Exception:
        pass

    # Lagrange ile hareket denklemi istegi, niyet ne cikarsa ciksin
    # dogrudan turetime gider: "yay kutle sistemini lagrange ile coz"
    # cumlesi "konu" niyetiyle geliyordu ve ders anlatimina dusuyordu
    # (olculdu).
    try:
        from . import lagrange as _lag0
        if _lag0.istek_mi(etkin) and _lag0.sistem_bul(etkin):
            _lm = _lag0.turet(etkin, lang)
            if _lm:
                intent = "turetim"
    except Exception:
        pass

    # SAYILAR VARSA HESAPLA. "carnot verimi 500 K ve 300 K arasinda"
    # cumlesinde soru kelimesi yok, bu yuzden niyet "konu" cikiyor ve
    # ogrenciye ders anlatiliyordu; oysa iki deger de verilmis ve
    # formul birebir adlandirilmis. Ogrenci sayilari verdiyse sayi
    # bekler (olculdu).
    # Cok adimli bilinen kaliplar (ornegin seri/paralel devre + Ohm)
    # niyet ne olursa olsun cozucuye ugrar.
    if intent in ("konu", "nasil", "neden"):
        try:
            _zin = problem.devre_zinciri(etkin, lang)
            if _zin:
                intent = "formul"
        except Exception:
            pass

    if _PROBLEM_SETI.search(etkin or ""):
        intent = "problem_seti"

    # Mesajda gercek bir MATRIS varsa hesap yapilir. Olculdu:
    # "[[1,2],[3,4]] ozdegerleri" istegi konu anlatimina dusuyordu,
    # cunku "ozdeger" kelimesi matris niyeti kaliplarinda yoktu.
    if intent == "konu":
        try:
            if nlu.extract_matrix(etkin):
                intent = "matris"
        except Exception:
            pass

    if intent == "konu":
        try:
            _degerler = nlu.extract_number_unit(etkin) or []
            _fv = formulas.search(etkin, limit=1)
            _guclu = bool(_fv) and not _fv[0][1].get("uretilmis")
            # Iki deger + makul eslesme, ya da TEK deger + cok guclu
            # eslesme. Olculdu: "650 nm dalga boylu fotonun enerjisi"
            # sorusunda tek deger var ama formul 178 puanla eslesiyor
            # ve cevap hesaplanabilir durumda.
            if _guclu and ((len(_degerler) >= 2 and _fv[0][0] >= 45)
                           or (len(_degerler) >= 1 and _fv[0][0] >= 70)):
                intent = "formul"
            elif not _degerler and _guclu and _fv[0][0] >= 60:
                # SORUDA RAKAM YOK ama degerler BILINIYOR olabilir:
                # "dunyadan kacis hizi nedir" sorusunda M ve R malzeme
                # tablosundan geliyor ve cozum cikiyor. Olculdu: soru
                # rakam icermedigi icin cozucuye hic ugramiyor, formul
                # karti basiliyordu; oysa cevap 1,119×10⁴ m/s.
                try:
                    if problem.coz(etkin, lang):
                        intent = "formul"
                except Exception:
                    pass
            elif _degerler and _guclu:
                # Zayif eslesmede bile SAYISAL bir cozum cikiyorsa
                # ogrencinin istedigi odur. Olculdu: "100 m yuksekten
                # birakilan cisim kac saniyede yere duser" sorusu, icinde
                # "cisim" gectigi icin "Kara Cisim Isimasi" konusuna
                # gidiyordu; oysa cozum (4,52 s) hesaplanabiliyordu.
                try:
                    if problem.coz(etkin, lang):
                        intent = "formul"
                except Exception:
                    pass
        except Exception:
            pass

    # ── SORUYU BUTUN OLARAK OKU ────────────────────────────────────────
    # Olculdu (canli kayit): "klasik kinetik enerji formulunden cikarak
    # Hamiltonyan operatorundeki kinetik enerji formulunu ispatlar misin"
    # sorusu, icinde "formulu" gectigi icin "formul" niyetine gidiyor ve
    # cumleden yalnizca "kinetik enerji" cekilip Ek = mv²/2 karti
    # basiliyordu. Soruda IKI kavram ve aralarindaki GECIS isteniyordu.
    # Iliski sorusu tek bir formul karti ile cevaplanamaz.
    if intent in ("formul", "konu", "turetim", "nasil", "neden", "ornek",
                  "makale"):
        try:
            from . import kopru as _kopru
            # Sonuc bir kez hesaplanir ve isleyiciye tasinir: iki kez
            # cagirmak hem bosuna is hem de ogrenme hedefi sayacini
            # iki katina cikariyordu.
            _km = _kopru.coz(etkin, lang) if _kopru.istek_mi(etkin) else None
            if _km:
                ctx["kopru_metin"] = _km
                intent = "kopru"
            elif _kopru.konu_bicimli_mi(etkin):
                # Tek kavram bulundu ama soru yine de ILISKI soruyor:
                # cevap formul karti degil, konu anlatimi olmali.
                intent = "kopru"
        except Exception:
            pass

    handler = HANDLERS.get(intent, h_konu)
    try:
        resp = handler(etkin, lang, ctx)
    except Exception as e:
        import traceback
        traceback.print_exc()
        resp = Response(L(lang,
                          "Bir hata olustu: `%s`\n\nFarkli bir sekilde sorabilir "
                          "misiniz?" % e,
                          "An error occurred: `%s`\n\nCould you rephrase?" % e))

    # ── Dil katmani ────────────────────────────────────────────────────
    # Model kuruluysa iki yerde devreye girer:
    #   1) Kural tabanli siniflandirici soruyu taniyamadiysa (konu/genel)
    #   2) Cevap zayif kaldiysa (kisa ya da "bilgim yok")
    # Her iki durumda da modele YALNIZCA dogrulanmis baglam verilir; sayilari
    # ve formulleri uydurmasi engellenir.
    # Ogretim modu: "anlat", "ogret", "nedir" gibi konu sorularinda
    # yapilandirilmis ders cevabi (tanim -> baginti -> cozumlu ornek ->
    # yaygin hata -> devam). Parcalarin hepsi dogrulanmis malzemeden gelir.
    # Soru/problem uretme istegi bir DERS istegi degildir: "entropi
    # hakkinda 10 soru uret" niyet olarak "konu" gorunuyor ama cevabi
    # sorular olmali. Ders modu bunu eziyordu.
    _soru_istegi = re.search(
        r"\b(soru|problem|alistirma|test|question|exercise)\w*\s*"
        r"(uret|olustur|ver|yaz|haz[ıi]rla|generate|create|give)|"
        r"\b\d+\s*(adet|tane)?\s*(soru|problem|question)", nlu.norm(message))
    if (intent == "konu" and not _soru_istegi
            and not resp.extra.get("dil_modeli")):
        try:
            # Es anlam genisletmesi uygulanmis metni ver: "izafiyet teorisi"
            # -> "gorelilik teorisi". Ham metinle konu eslesmesi tutmuyordu.
            ders_sorgusu = (ctx.get("anlama") or {}).get("genis") or etkin
            ders = ogretim.ders_ver(ders_sorgusu, lang,
                                    detay=bool(ctx.get("detay")))
            # Olcut uzunluk degil YAPI: cozumlu ornek ya da yaygin hata
            # bolumu varsa bu anlatim kural tabanli duz metinden iyidir.
            yapili = ders and any(im in ders for im in (
                "Çözümlü örnek", "Worked example",
                "Sık yapılan hata", "Common mistake"))
            if yapili:
                resp.text = ders
                resp.kind = "topic"
                resp.extra["ogretim"] = True
                # Yapilandirilmis ders dogrulanmis parcalardan kuruldu
                # (formul + fiziksel anlam notu + SymPy ile hesaplanmis
                # ornek). Dil modelinin bunu yeniden yazmasi kaliteyi
                # dusuruyor ve hata riski getiriyor.
                resp.extra["dil_modeli"] = True
        except Exception:
            pass

    # Sohbet niyetleri (selam, tesekkur, yardim, durum...) fizik sorusu
    # degildir: ne bilgi bosluğu sayilir ne de "dogrulanmis bilgim yok"
    # cevabini hak eder. Bunlar kendi isleyicilerinde zaten dogal cevap
    # veriyor.
    _SOHBET_NIYETLERI = {"selam", "selam_gunluk", "tesekkur", "onay",
                         "yardim", "durum", "liste",
                         "yetenek", "profil", "kendini_dogrula", "oneri",
                         "yol_haritasi", "ogrendiklerim"}
    # Yapilandirilmis ders DOKUNULMAZDIR. Parcalari dogrulanmis kaynaktan
    # geliyor (formul + fiziksel anlam notu + SymPy ile hesaplanmis ornek).
    # Model bunu yeniden yazinca yon bildiren ifadeleri ters cevirebiliyor;
    # olculen ornek: "isi akisinin sadece soguktan sicaga olabilecegini
    # belirtir" (dogrusu tam tersi). Ders varsa model hic cagrilmaz.
    if (dil.MODEL.kurulu_mu() and intent not in _DIL_DISI_NIYETLER
            and intent not in _SOHBET_NIYETLERI
            and not resp.extra.get("ogretim")):
        # Isleyicinin kendi itiraflari en guvenilir zayiflik isaretidir:
        # metin benzerligine bakmaktansa "bulamadim" demesini dinliyoruz.
        _ITIRAF = ("yeterli bilgim yok", "don't have enough",
                   "nedensel bir kaynak bulamad", "couldn't find a direct causal",
                   "hazir ornegim yok", "don't have a ready example",
                   "tam anlayamadim", "couldn't tell which")
        zayif = (len(resp.text) < 260
                 or any(x in resp.text for x in _ITIRAF)
                 or _yabanci_alinti_yigini(resp.text, lang))
        # Cekirdekte GUCLU eslesen bir anlatim varsa cevap serbest degildir:
        # dogrulanmis metni modele yeniden yazdirmak kayiptir.
        serbest = (intent in ("konu", "genel") and conf < 60
                   and resp.extra.get("cekirdek_skor", 0) < 40)
        # Uretilen cevap soruyla ortusmuyorsa (alakasiz konu getirilmisse)
        # kural tabanli yanit yerine baglamdan yanit uretilir.
        # Alakasizlik denetimi metin ortusmesine bakar; uzun bir cekirdek
        # anlatimda aranan terim ilk 400 karakterde gecmeyebilir. Olculdu:
        # "ultraviolet catastrophe" sorusu dogru konuya (Kara Cisim, 57
        # puan) gidiyordu ama basligin ilk paragrafinda terim gecmedigi
        # icin "alakasiz" sayilip modele devrediliyordu. Cekirdek zaten
        # anahtar kelime eslesmesiyle karar veriyor; guclu eslesmede bu
        # sezgisel denetim devre disi.
        alakasiz = (intent in ("konu", "neden", "nasil", "genel")
                    and resp.extra.get("cekirdek_skor", 0) < 40
                    and not _relevant(message, resp.text[:1200]))
        # Konusmadan ogrenme: cevabin zayif kaldigi her soru bir bilgi
        # bosluktur ve ogrenme motoruna hedef olur. En degerli ogrenme
        # sinyali budur — bot ne sorulduguna gore gelisir.
        try:
            bosluk.kaydet(etkin, lang, guclu=not (zayif or alakasiz))
        except Exception:
            pass
        if zayif or serbest or alakasiz:
            try:
                # ONCE gercek malzeme var mi diye bak. Hesap sonucunu baglama
                # katarsak baglam her zaman dolu gorunur — model de kural
                # tabanli cevabi alip etrafini kendi bilgisiyle susler ve
                # fizik uydurur. Olculen ornek: "Kazimir etkisi nedir"
                # sorusuna "iki plaka arasindaki elektriksel potansiyel
                # farki" dedi; oysa neden kuantum vakum dalgalanmalaridir.
                malzeme = baglam.derle(etkin, lang)
                if malzeme and not baglam._ilgili(etkin, malzeme[:1500],
                                                  gerekli=1):
                    malzeme = ""      # dolu ama soruyla ilgisiz
                # Yalnizca "ogrenilen baginti" parcalarindan olusan baglam
                # ACIKLAYICI degildir: LaTeX kirintilari konuyu anlatmaz.
                # Olculdu: "Berry fazi nedir" sorusunda baglam 1971 karakter
                # doluydu ama tamami Berry-Keating makalesinden gelen
                # denklem parcalariydi; sistem bilgi var sanip canli
                # arastirmayi hic calistirmadi.
                if malzeme:
                    aciklayici = [p for p in malzeme.split("\n\n")
                                  if not p.startswith("OGRENILEN BAGINTI")]
                    if not aciklayici:
                        malzeme = ""
                bg, bg_kaynaklar = "", []
                if malzeme:
                    bg, bg_kaynaklar = baglam.derle_kaynakli(
                        etkin, lang,
                        hesap_sonucu=None if zayif else resp.text)
                if not baglam.bos_mu(bg):
                    akici = dil.MODEL.yanitla(
                        message, baglam=bg, lang=lang,
                        gecmis=ctx.get("history"))
                    # Model "bilmiyorum" derse bile bunu gosteriyoruz:
                    # kural tabanli cevap zaten alakasizdi, yanlis bilgi
                    # vermektense bilmedigimizi soylemek dogrusu.
                    if akici and len(akici) > 15:
                        # Kaynakca: bilginin nereden geldigi gorunsun.
                        resp.text = akici + canli.kaynakca(bg_kaynaklar, lang)
                        resp.extra["dil_modeli"] = True
                        if bg_kaynaklar:
                            resp.extra["kaynaklar"] = bg_kaynaklar
                elif zayif or alakasiz:
                    # Dogrulanmis bilgi yok. Once CANLI ARASTIRMA: soru
                    # sorulduğu anda internete cikip kaynak topla, cevabi
                    # o kaynaklardan uret ve altina kaynakcayi ekle.
                    # Boylece kullanici bir sonraki sefere beklemez ve
                    # bilginin nereden geldigini kendi gozuyle gorur.
                    arastirma = None
                    try:
                        arastirma = canli.arastir(etkin, lang)
                    except Exception:
                        arastirma = None
                    if arastirma and arastirma["baglam"]:
                        akici = dil.MODEL.yanitla(
                            message, baglam=arastirma["baglam"], lang=lang,
                            gecmis=ctx.get("history"))
                        if akici and len(akici) > 15:
                            resp.text = (akici + "\n" +
                                         canli.kaynakca(arastirma["kaynaklar"],
                                                        lang))
                            resp.extra["dil_modeli"] = True
                            resp.extra["canli"] = True
                            resp.extra["kaynaklar"] = arastirma["kaynaklar"]
                        else:
                            resp.text = _arastirmaya_alindi(message, lang)
                            resp.extra["bosluk"] = True
                    else:
                        # Internette de bulunamadi: durustce soyle
                        resp.text = _arastirmaya_alindi(message, lang)
                        resp.extra["bosluk"] = True
            except Exception:
                pass      # model sorun cikarirsa kural tabanli cevap kalir

    # ── Devam sorusu ayni cevabi getirmesin ────────────────────────────
    # Olculdu: "ozel gorelilik nedir" -> ders; ardindan "peki bunun
    # sonuclari neler" -> AYNI ders metni birebir tekrar geldi. Kullanici
    # icin sohbet burada tikaniyor ("2-3 mesajdan sonra duruyor").
    # Son UC bot cevabina bakiyoruz: kullanici araya bir soru sikistirinca
    # "iki tur once verilen metin" yeniden basiliyordu ve denetim bunu
    # kaciriyordu (olculdu: 1. turdaki gorelilik dersi 4. turda aynen
    # tekrar geldi).
    _son_botlar = []
    for _m in reversed(ctx.get("history") or []):
        if _m.get("role") != "user" and _m.get("content"):
            _son_botlar.append(_m["content"])
            if len(_son_botlar) >= 3:
                break
    _bellek_son = ctx.get("son_cevap")
    if _bellek_son and _bellek_son not in _son_botlar:
        _son_botlar.insert(0, _bellek_son)
    _son_bot = _son_botlar[0] if _son_botlar else ''
    # Yon ipucu varsa (sonuclari, ornek, formul, kanit, kisi...) HER ZAMAN
    # yon cevabi denenir. Yalnizca "cevap tekrar ediyorsa" denemek
    # yetmiyordu: "bir ornek verir misin" sorusu tekrar degildi ama
    # konudan sapip alakasiz makale metnine gidiyordu (olculdu).
    #
    # Denetim devam sorulariyla SINIRLI DEGIL: "nernst denklemini yazar
    # misin" kendi konusunu tasidigi icin devam sorusu sayilmiyor, ama
    # cevabi yine ayni ders metniydi. Kullanicinin "2-3 mesajdan sonra
    # duruyor" dedigi durum tam olarak buydu.
    _yon_var = any(re.search(kalip, nlu.norm(message))
                   for _ad, kalip in _YON_IPUCU)
    _tekrar = any(_ayni_cevap(x, resp.text) for x in _son_botlar)

    # AYNI BASLIK denetimi. Bir onceki cevapla ayni baslikla aciliyorsak
    # ve kullanici belirli bir yon sormussa, dersin girisini bastan
    # anlatmak "tekrar" hissi veriyor — kullanicinin sikayeti tam olarak
    # buydu. Metinler birebir ayni olmasa da yon cevabina geciyoruz.
    def _baslik(t):
        for satir in (t or "").splitlines():
            if satir.startswith("### "):
                return nlu.norm(satir[4:].split("—")[0])
        return ""

    _ayni_baslik = bool(_son_botlar) and _baslik(resp.text) and \
        _baslik(resp.text) == _baslik(_son_botlar[0])
    _konu_adi = onceki or resp.extra.get("konu_etiketi") or \
        (ctx.get("last_subject") or "")
    # Mesajda DOGRULANMIS kaydi olan bir fizikcinin adi geciyorsa, o kayit
    # dil modelinin serbest anlatimindan once gelir. Olculdu: model
    # "Einstein 1905'te 'Relativistik Mekanik' adli makalesinde" dedi —
    # makalenin gercek adi "Hareketli Cisimlerin Elektrodinamigi Uzerine".
    # Bu projenin kurali degismedi: model dili kurar, olgulari kaynak verir.
    _kisi_kaydi = _kisi_sorusu(message)
    # Yon/devam cevabi yalnizca KONU anlatimlarinda anlamlidir. Sohbet
    # niyetleri (yetenek, selam...) ve URETIM istekleri buraya girmemeli:
    # olculdu, "10 soru uret" ikinci kez istendiginde uretilen sayfa bir
    # oncekine benzedigi icin "tekrar" sayilip modele yeniden yazdiriliyor
    # ve dogrulanmis 10 sorunun 9'u kayboluyordu. Ayni sekilde MATLAB
    # yetenek anlatimi da model metnine donusuyordu.
    #
    # SAYISAL COZUM de asla ezilmemeli: ayni problemi ikinci kez soran
    # ogrenciye sayi yerine "sunlardan devam edebiliriz" listesi
    # donuyordu (olculdu: odev olcumu 18/18'den 12/18'e dusuyordu, cunku
    # olcum oturumlarinda ayni soru daha once sorulmustu). Bir problemin
    # cevabi kac kez sorulursa sorulsun aynidir.
    _YON_DISI = _SOHBET_NIYETLERI | {"ornek", "matlab", "hesap", "denklem",
                                     "problem_seti", "kopru", "formul",
                                     "turetim", "turev", "integral",
                                     "limit", "seri", "diferansiyel",
                                     "matris", "vektor", "birim", "sabit"}
    if intent in _YON_DISI:
        _kisi_kaydi = None
        _konu_adi = ""
    if _kisi_kaydi or (_konu_adi and
                       ((_yon_var and (onceki or _ayni_baslik)) or _tekrar)):
        _hedef_konu = _konu_adi or (
            _kisi_kaydi["tr_title"] if lang == "tr"
            else _kisi_kaydi["en_title"])
        _yon = _yon_cevabi(message, _hedef_konu, resp.text, lang, ctx)
        if _yon:
            # Yon cevabi bir CEKIRDEK anlatimin yerine geciyorsa, hangi
            # konudan geldigi yazili kalmali; ogrenci kaynagi gormeli
            # (olculdu: "ultraviolet catastrophe" dogru konuya gidiyordu
            # ama yon cevabinda konu adi kayboluyordu).
            _cek = resp.extra.get("cekirdek_skor", 0)
            if _cek >= 40:
                try:
                    _h = knowledge.search(etkin, limit=1)
                    if _h:
                        _yon += _konu_notu(_h[0][1], "", lang)
                except Exception:
                    pass
            resp.text = _yon
            resp.kind = "topic"
            resp.extra["devam"] = True

    # Kaynakca: bilginin nereden geldigi her zaman gorunsun.
    # Kaynakca yalnizca ICERIKLI cevaba eklenir. "Bu konuda elimde bilgi
    # yok" diyen bir cevabin altina kaynak listelemek yaniltici oluyordu.
    # Sentez sayfasinin durustluk notu, dil modeli metni yeniden yazdiysa
    # kaybolmus olabilir. Bilginin NEREDEN geldigi her zaman gorunmeli.
    if resp.extra.get("sentez") and resp.extra.get("dil_modeli"):
        if "çekirdek" not in resp.text and "built-in" not in resp.text:
            resp.text += L(lang,
                           "\n\n_Bu sayfayı okuduğum makalelerden ve kavram "
                           "ağımdan derledim; çekirdek anlatımlarımdan biri "
                           "değil._",
                           "\n\n_I assembled this page from papers I've read "
                           "and my concept graph; it is not one of my "
                           "built-in topics._")

    _bos_cevap = (resp.extra.get("bosluk")
                  or any(x in resp.text[:200] for x in
                         ("elimde bilgi yok", "bilgim yok",
                          "no verified information", "don't have")))
    if (intent in ("konu", "nasil", "neden", "makale", "ornek", "karsilastir")
            and not _bos_cevap):
        _kaynak_ekle(resp, etkin, lang)

    resp.extra["intent"] = intent
    resp.extra["lang"] = lang
    # Duzeltme yaptiysak sessiz kalmayalim; kullanici ne anladigimi gorsun
    dz = (ctx.get("anlama") or {}).get("duzeltmeler") or []
    if dz and intent not in ("hesap", "denklem", "turev", "integral"):
        not_ = L(lang, "_%s olarak anladım._", "_I read this as %s._") % ", ".join(
            "**%s** → **%s**" % (a, b) for a, b in dz[:3])
        resp.text = not_ + "\n\n" + resp.text

    # Bu turun konusunu hatirla (devam sorusuysa eskisini koru).
    # DIKKAT: devam sorusunda konu ETIKETI degismemeli. Aksi halde her
    # turda soru kelimeleri konuya ekleniyor ve konu kayiyor
    # ("ozel gorelilik" -> "ozel gorelilik deneysel olarak biliyoruz").
    konu = onceki
    if not onceki and intent not in ("selam", "tesekkur", "onay", "yardim", "durum",
                                     "liste", "hesap"):
        aday = nlu.strip_command_words(message)
        if len(aday) >= 3:
            konu = aday[:80]
    # Isleyici daha temiz bir baslik verdiyse onu tercih et: ham soru cumlesi
    # ("matlab ogrenmek istiyorum nereden baslamaliyim") ilgi alani etiketi
    # olarak kotu gorunur.
    etiket = resp.extra.get("konu_etiketi")
    if etiket and not onceki:
        konu = etiket
    # Ilgi alani bir KONU olmali, soru parcasi degil: "kutlesi 3 kg olan
    # cisim..." ilgi alani olarak kaydediliyordu. Sayi/birim iceren ya da
    # cok uzun ifadeler elenir.
    if konu and intent in ("konu", "formul", "ornek", "makale", "matlab",
                           "yol_haritasi", "sabit"):
        aday_konu = konu.strip()
        # Tek kelimelik konular gecerlidir ("entropi"); elenen sey sayi
        # iceren ya da cumle uzunlugundaki soru parcalaridir.
        uygun = (1 <= len(aday_konu.split()) <= 5
                 and not re.search(r"\d", aday_konu)
                 and len(aday_konu) <= 48)
        if uygun or resp.extra.get("konu_etiketi"):
            profile.note_interest(aday_konu[:48])
    # Sohbette en son ANILAN KISI'yi hatirla; "onun hayati", "projeleri
    # neler" gibi sorular buna dayanir.
    _hatirla = dict(resp.extra.get("remember") or {})
    _kt = _kisi_konusu(message) or _kisi_konusu(resp.text[:400])
    if _kt:
        _hatirla["son_kisi"] = _kt["en_title"]

    # ── KENDI COZUMUNDEN OGREN ─────────────────────────────────────────
    # Bir problemi iki formulu zincirleyerek cozduysek, o zincir yeni bir
    # bagintinin adayidir. Rastgele formul cifti denemek yerine GERCEKTEN
    # birlikte ise yaramis ciftleri isaretliyoruz; ogrenme motoru bunlari
    # birlestirip dogrulama kapilarindan geciriyor (bkz. formulogren.py).
    if intent == "formul" and resp.kind == "solution":
        try:
            from . import formulogren as _fo, zincir as _zn
            _idler = _zn.kullanilan_formuller(etkin)
            if len(_idler) >= 2:
                _fo.zincir_kaydet(_idler)
        except Exception:
            pass

    # ── KENDI ZAYIFLIGINI FARK ET ──────────────────────────────────────
    # Soru iki kavram adlandirdi ama cevap yalnizca birine degdiyse bu bir
    # KOPRU BOSLUGUDUR. Kullanicinin sikayet etmesini beklemeden kaydedilir;
    # ogrenme motoru bir sonraki turunda o cifti korpusta arayip baglantiyi
    # ogrenmeye calisir (bkz. kopruogren.py). Kullanicinin istegi buydu:
    # "benzer ve yine zor olan soruları kendi kendine öğrensin".
    if intent in ("konu", "kopru", "neden", "nasil", "formul", "turetim"):
        try:
            from . import kopruogren as _koo
            _koo.kapsam_denetle(etkin, resp.text, lang)
        except Exception:
            pass

    _save_turn(session, message, resp.text, intent, subject=konu,
               extra=_hatirla or None)
    return resp


def _load_context(session):
    c = db.conn()
    try:
        rows = c.execute("SELECT role, content FROM chat WHERE session=? "
                         "ORDER BY id DESC LIMIT 8", (session,)).fetchall()
    except Exception:
        rows = []
    ctx = {"history": [dict(r) for r in reversed(rows)]}
    mem = _SESSION_MEM.get(session)
    if mem is None:
        mem = {}
        for k in ("last_subject", "last_intent", "last_topic_key",
                  "last_formula_id", "son_kisi", "son_cevap"):
            v = db.get_sstate(session, k)
            if v is not None:
                mem[k] = v
        _SESSION_MEM[session] = mem
    ctx.update(mem)
    # Tablodan gelen gecmis kuyruk yuzunden bos olabilir; bellekteki
    # daha uzunsa onu kullaniyoruz.
    if len(mem.get("gecmis") or []) > len(ctx["history"]):
        ctx["history"] = list(mem["gecmis"])
    ctx["last_topic"] = mem.get("last_subject")
    return ctx


def _save_turn(session, user_msg, bot_msg, intent, subject=None, extra=None):
    """Sohbeti kaydet — kuyruk uzerinden, cevabi hic bekletmeden.

    Ogrenme motoru buyuk bir yazma islemi yapiyorsa dogrudan INSERT saniyelerce
    bloke olabilirdi; gecmis kaydi cevaptan daha az onemli oldugu icin arka
    plandaki yaziciya devrediliyor.

    Baglam (son konu, son niyet) once bellege yazilir; boylece bir sonraki soru
    kuyruk henuz bosalmamis olsa bile dogru konuyu gorur.
    """
    now = time.time()
    sql = "INSERT INTO chat(session, role, content, ts) VALUES(?,?,?,?)"
    db.queue_write(sql, (session, "user", user_msg, now))
    db.queue_write(sql, (session, "assistant", bot_msg, now))

    mem = _SESSION_MEM.setdefault(session, {})
    mem["last_intent"] = intent
    if subject:
        mem["last_subject"] = subject
    # Sohbet gecmisi ASENKRON yaziliyor; bir sonraki mesajda `chat`
    # tablosu cogu zaman hala bos oluyordu (olculdu: history uzunlugu 0).
    # Yani ne tekrar denetimi ne de dil modeli onceki turu goruyordu —
    # kullanicinin "kafasi karisiyor, konusmayi surdurmuyor" dedigi
    # davranisin buyuk kismi buradan geliyor. Kisa gecmisi bellekte,
    # yazma kuyrugundan bagimsiz tutuyoruz.
    mem["son_cevap"] = (bot_msg or "")[:4000]
    _g = list(mem.get("gecmis") or [])
    _g.append({"role": "user", "content": (user_msg or "")[:1500]})
    _g.append({"role": "assistant", "content": (bot_msg or "")[:1500]})
    mem["gecmis"] = _g[-8:]
    for k, v in (extra or {}).items():
        mem[k] = v

    # Kalicilik + kenar cubugundaki sohbet listesi
    db.queue_write(
        "INSERT INTO sessions(id,title,created,updated) VALUES(?,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET updated=excluded.updated, "
        "title=CASE WHEN COALESCE(TRIM(sessions.title),'')='' "
        "           THEN excluded.title ELSE sessions.title END",
        (session, user_msg.strip()[:90], now, now))
    for k, v in mem.items():
        db.queue_write(
            "INSERT INTO session_state(session,key,value) VALUES(?,?,?) "
            "ON CONFLICT(session,key) DO UPDATE SET value=excluded.value",
            (session, k, json.dumps(v, ensure_ascii=False)))
