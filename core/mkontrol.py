# -*- coding: utf-8 -*-
"""MATLAB kodu icin kaba sozdizimi denetimi.

Octave kurulu olmadigi icin kodu calistiramiyoruz. Bunun yerine satir
satir tarayarak yorumlari ve metin sabitlerini DOGRU sekilde ayiklayip
parantez / blok dengesini olcuyoruz. Onceki olcum yanlisti: bicim
dizgelerindeki %% isaretini yorum baslangici sanip satiri kesiyordu.
"""
import re

ACICI = re.compile(r"(?<![\w.])(for|if|while|switch|parfor|function|try)\b")
KAPAT = re.compile(r"(?<![\w.])end(for|if|while|switch|function|try)?\b")


def kod_ayikla(satir):
    """Metin sabitlerini ve yorumu at, geriye kod kalsin."""
    out = []
    i = 0
    n = len(satir)
    while i < n:
        c = satir[i]
        if c == "'":
            # transpoz mu metin mi? Onceki karakter tanimlayici/kapatan ise transpoz
            onceki = out[-1] if out else ""
            if onceki and (onceki.isalnum() or onceki in ")]}._'"):
                out.append("'")
                i += 1
                continue
            i += 1                      # metin sabiti: kapanana kadar atla
            while i < n:
                if satir[i] == "'":
                    if i + 1 < n and satir[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            out.append("''")
            continue
        if c == '"':
            i += 1
            while i < n and satir[i] != '"':
                i += 1
            i += 1
            out.append('""')
            continue
        if c == "%":
            break                        # buradan sonrasi yorum
        out.append(c)
        i += 1
    return "".join(out)


def denetle(kod):
    hatalar = []
    derinlik = {"(": 0, "[": 0, "{": 0}
    es = {")": "(", "]": "[", "}": "{"}
    blok = 0
    for no, satir in enumerate(kod.split("\n"), 1):
        k = kod_ayikla(satir)
        # Parantez disinda kalan kismi ayri topluyoruz: MATLAB'de `end`
        # hem blok kapatir hem dizi indisidir (x(end), y(2:end-1)).
        # Sadece parantez derinligi sifirken gecen `end` blok kapatir.
        duz = []
        for ch in k:
            if ch in derinlik:
                derinlik[ch] += 1
            elif ch in es:
                derinlik[es[ch]] -= 1
                if derinlik[es[ch]] < 0:
                    hatalar.append("satir %d: fazla '%s'" % (no, ch))
                    derinlik[es[ch]] = 0
            if sum(derinlik.values()) == 0 and ch not in es:
                duz.append(ch)
        duz = "".join(duz)
        blok += len(ACICI.findall(duz)) - len(KAPAT.findall(duz))
    for ch, d in derinlik.items():
        if d:
            hatalar.append("kapanmamis '%s' x%d" % (ch, d))
    if blok:
        hatalar.append("blok dengesizligi: %+d (for/if/while/function vs end)" % blok)
    return hatalar


def tum_sablonlar():
    """Tum sablonlari denetle. {sablon: [hata, ...]} doner."""
    from . import matlab
    return {k: h for k, h in
            ((k, denetle(v["code"])) for k, v in matlab.TEMPLATES.items()) if h}
