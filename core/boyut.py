# -*- coding: utf-8 -*-
"""Boyut denetimi: toplanamayanı toplamamak.

Olculdu: "1 kg + 30 metre + 22 cm kac eder" sorusuna sistem yalnizca
"1 kg = 1 (SI)" diye birim cevrimi yapti. Oysa dogru cevap sudur:

    Kutle ile uzunluk TOPLANMAZ. Ama 30 m + 22 cm = 30,22 m.

Bu tur sorular bir hesap makinesini degil, FIZIK bilen birini sinar.
Ogrenci de sinavda ayni tuzakla karsilasir: birimleri denetlemeden
toplayan yanilir. Boyut analizi, fizikte cevabin dogrulugunu sinamanin
en ucuz ve en guclu yoludur.

Modul, dogal dildeki bir toplama/cikarma ifadesini okur, terimleri
BOYUTLARINA gore gruplar, toplanabilenleri toplar ve toplanamayanlari
acikca soyler.
"""
import re

from . import units


# "1 kg + 30 metre + 22 cm" bicimindeki terimler
_TERIM = re.compile(
    r"([+-]?)\s*(\d+(?:[.,]\d+)?)\s*"
    r"([a-zA-ZµΩÅ°][a-zA-ZµΩÅ°0-9^/*·]*)")

# Toplama sorusu mu? En az bir arti/eksi ve iki birimli deger gerekir.
_TOPLAMA = re.compile(r"\d\s*[a-zA-ZµΩÅ°][^+\-]*[+\-]\s*\d")


def _boyut_adi(boyut):
    """SI boyut demetini okunakli ada cevir."""
    adlar = {
        (1, 0, 0, 0, 0, 0, 0): "uzunluk",
        (0, 1, 0, 0, 0, 0, 0): "kütle",
        (0, 0, 1, 0, 0, 0, 0): "zaman",
        (0, 0, 0, 1, 0, 0, 0): "akım",
        (0, 0, 0, 0, 1, 0, 0): "sıcaklık",
        (0, 0, 0, 0, 0, 1, 0): "madde miktarı",
        (0, 0, 0, 0, 0, 0, 1): "ışık şiddeti",
        (1, 0, -1, 0, 0, 0, 0): "hız",
        (1, 0, -2, 0, 0, 0, 0): "ivme",
        (1, 1, -2, 0, 0, 0, 0): "kuvvet",
        (2, 1, -2, 0, 0, 0, 0): "enerji",
        (2, 1, -3, 0, 0, 0, 0): "güç",
        (2, 0, 0, 0, 0, 0, 0): "alan",
        (3, 0, 0, 0, 0, 0, 0): "hacim",
    }
    return adlar.get(tuple(int(x) for x in boyut))


def coz(metin, lang="tr"):
    """Boyutlu bir toplama ifadesini degerlendir. Metin ya da None."""
    if not metin or not _TOPLAMA.search(metin):
        return None

    terimler = []
    for isaret, sayi, birim in _TERIM.findall(metin):
        try:
            deger = float(sayi.replace(",", "."))
        except ValueError:
            continue
        cevrim = units.to_si(deger, birim)
        if not cevrim or cevrim[0] is None or not cevrim[1]:
            continue
        si, boyut = cevrim
        if isaret == "-":
            si = -si
        terimler.append({"deger": deger, "birim": birim, "si": si,
                         "boyut": tuple(boyut)})
    if len(terimler) < 2:
        return None

    # Boyutlara gore grupla
    gruplar = {}
    for t in terimler:
        gruplar.setdefault(t["boyut"], []).append(t)
    tr = lang == "tr"
    if len(gruplar) < 2:
        # Hepsi ayni boyutta: toplama GECERLI, hesaplayip verelim.
        # Olculdu: "30 m + 22 cm kac eder" sorusuna "eder birimini
        # tanimiyorum" deniyordu; oysa cevap 30,22 m.
        boyut, liste = next(iter(gruplar.items()))
        ad = _boyut_adi(boyut) or ("aynı boyut" if tr else "same dimension")
        toplam = sum(t["si"] for t in liste)
        ilk = liste[0]
        try:
            kat = units.to_si(1.0, ilk["birim"])[0] or 1.0
        except Exception:
            kat = 1.0
        ifade = " + ".join("%g %s" % (t["deger"], t["birim"])
                           for t in liste)
        return "\n".join([
            "### " + ("Toplama" if tr else "Sum"), "",
            "`%s`" % ifade, "",
            "## **%g %s**" % (toplam / kat, ilk["birim"]), "",
            "_" + (("Tüm terimler aynı boyutta (%s), bu yüzden "
                    "toplanabilir. SI karşılığı: %g." % (ad, toplam))
                   if tr else
                   ("All terms share the dimension %s; SI value %g."
                    % (ad, toplam))) + "_",
        ])

    L = lambda a, b: a if tr else b
    satirlar = [
        "### " + L("Bu toplama yapılamaz", "This sum is not valid"), "",
        L("Farklı **boyutlardaki** nicelikler toplanamaz. Toplama ancak "
          "aynı fiziksel büyüklükler arasında tanımlıdır — bu, birim "
          "seçiminden bağımsız bir kuraldır.",
          "Quantities of different dimensions cannot be added."),
        "",
        "**" + L("Verdiğiniz terimler", "Your terms") + "**", "",
    ]
    for boyut, liste in gruplar.items():
        ad = _boyut_adi(boyut) or L("bilinmeyen boyut", "unknown dimension")
        ifade = ", ".join("`%g %s`" % (t["deger"], t["birim"])
                          for t in liste)
        satirlar.append("- %s → **%s**" % (ifade, ad))
    satirlar.append("")

    # Toplanabilenleri gercekten topla
    toplanan = []
    for boyut, liste in gruplar.items():
        if len(liste) < 2:
            continue
        ad = _boyut_adi(boyut) or L("aynı boyut", "same dimension")
        toplam = sum(t["si"] for t in liste)
        # Grubun ilk teriminin birimiyle geri cevir
        ilk = liste[0]
        try:
            birim_kat = units.to_si(1.0, ilk["birim"])[0]
        except Exception:
            birim_kat = 1.0
        gosterim = toplam / birim_kat if birim_kat else toplam
        toplanan.append((ad, liste, gosterim, ilk["birim"], toplam))

    if toplanan:
        satirlar.append("**" + L("Toplanabilenler", "What can be added")
                        + "**")
        satirlar.append("")
        for ad, liste, gosterim, birim, si in toplanan:
            ifade = " + ".join("%g %s" % (t["deger"], t["birim"])
                               for t in liste)
            satirlar.append("- %s = **%g %s**  (%s)"
                            % (ifade, gosterim, birim, ad))
        satirlar.append("")

    tekler = [(boyut, liste[0]) for boyut, liste in gruplar.items()
              if len(liste) == 1]
    if tekler:
        adlar = [_boyut_adi(b) or "?" for b, _t in tekler]
        satirlar.append(
            L("Geriye kalan %s terimi başka hiçbir terimle toplanamaz; "
              "sonuç ancak ayrı ayrı yazılabilir."
              % " ve ".join("**%s**" % a for a in adlar),
              "The remaining terms cannot be combined."))
        satirlar.append("")

    satirlar.append("_" + L(
        "Boyut denetimi, bir sonucun doğruluğunu sınamanın en ucuz "
        "yoludur: iki tarafın boyutu tutmuyorsa hesap kesinlikle "
        "yanlıştır.",
        "Dimensional analysis is the cheapest correctness check there "
        "is.") + "_")
    return "\n".join(satirlar)
