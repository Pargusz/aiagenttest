# -*- coding: utf-8 -*-
"""TURETIM MOTORU: sonucu okumak yerine HESAPLAMAK.

Olculdu (genelleme sinavi): hic yazilmamis alti turetimden SIFIRI dogru
cevaplandi. Ehrenfest teoremi "Hamilton fonksiyonu — H icin adim adim
cozum"e, Bloch teoremi "Fotoelektrik olay"a gidiyordu. Sebep acikti:
sistem yazili metni sunuyor, turetim URETMIYOR. Yazili olmayan her
turetim kayip.

Bu modul o boslugu kapatir. Yontem:

    Operatorler, dalga fonksiyonu uzerine etkiyen ISLEMLER olarak
    temsil edilir. x ile carpma, p ile -iħ∂/∂x. Komutator, iki
    islemin sirasini degistirip farki almaktir ve SymPy bunu
    GERCEKTEN hesaplar.

Boylece [x,p] = iħ bir veri degil, bir SONUCTUR. Ayni motor Ehrenfest
teoremini, viryal teoremini ve Heisenberg hareket denkleminin her
ozel hâlini uretir — hicbiri elle yazilmadan.

Sinir durustce: bu motor KOMUTATOR CEBRI yapar. Bloch teoremi (grup
kurami), Berry fazi (diferansiyel geometri) ya da Fermi altin kurali
(zamana bagli perturbasyon) baska matematik ister ve bu motorun
kapsaminda degildir. Kapsamda olani hesaplar, olmayani "hesaplayamam"
der — uydurmaz.
"""
import sympy as sp

# Ortak semboller
x, t, m, hbar = sp.symbols("x t m hbar", real=True, positive=True)
_psi = sp.Function("psi")
_V = sp.Function("V")


# ── Operatorler: dalga fonksiyonuna etkiyen islemler ───────────────────────

def op_x(f):
    """Konum operatoru: x ile carpma."""
    return x * f


def op_p(f):
    """Momentum operatoru: -iħ ∂/∂x."""
    return -sp.I * hbar * sp.diff(f, x)


def op_T(f):
    """Kinetik enerji operatoru: p²/2m = -(ħ²/2m)∂²/∂x²."""
    return -hbar ** 2 / (2 * m) * sp.diff(f, x, 2)


def op_V(f):
    """Potansiyel operatoru: V(x) ile carpma."""
    return _V(x) * f


def op_H(f):
    """Hamilton operatoru: T + V."""
    return op_T(f) + op_V(f)


def op_carp(A, B):
    """Iki operatorun bilesimi: (A∘B)f = A(B(f))."""
    return lambda f: A(B(f))


# ── Komutator: GERCEKTEN hesaplanir ────────────────────────────────────────

def komutator(A, B, f=None):
    """[A,B]f = A(B(f)) − B(A(f)). Sadelestirilmis ifade doner."""
    if f is None:
        f = _psi(x)
    return sp.simplify(sp.expand(A(B(f)) - B(A(f))))


def komutator_katsayisi(A, B):
    """[A,B]ψ ifadesini ψ'nin katsayisi olarak ver (mumkunse).

    [x,p]ψ = iħψ ise katsayi iħ'dir. Bu, komutatorun bir SAYI oldugu
    (operator olmadigi) durumlarda anlamlidir.
    """
    ifade = komutator(A, B)
    try:
        oran = sp.simplify(ifade / _psi(x))
        if not oran.has(sp.Derivative) and not oran.has(_psi):
            return sp.simplify(oran)
    except Exception:
        pass
    return None


# ── Heisenberg hareket denklemi ────────────────────────────────────────────

def heisenberg(A, ad="A"):
    """d⟨A⟩/dt = (1/iħ)⟨[A,H]⟩ — sag tarafi HESAPLA.

    Doner: (ifade, adimlar). ifade, ⟨...⟩ icine girecek operatorun
    ψ uzerindeki etkisidir.
    """
    adimlar = []
    adimlar.append(("Heisenberg hareket denklemi",
                    r"d⟨%s⟩/dt = (1/iħ)·⟨[%s, Ĥ]⟩" % (ad, ad)))
    kom = komutator(A, op_H)
    adimlar.append(("Komütatörü ψ üzerine etkiterek hesapla",
                    "[%s, Ĥ]ψ = %s" % (ad, sp.sstr(kom))))
    sonuc = sp.simplify(kom / (sp.I * hbar))
    adimlar.append(("(1/iħ) ile çarp",
                    "(1/iħ)[%s, Ĥ]ψ = %s" % (ad, sp.sstr(sonuc))))
    return sonuc, adimlar


# ── Hazir turetimler: hepsi HESAPLANIR, yazili degil ──────────────────────

def turet_xp_komutator(lang="tr"):
    """[x̂, p̂] = iħ — hesaplayarak."""
    tr = lang == "tr"
    kom = komutator(op_x, op_p)
    kat = komutator_katsayisi(op_x, op_p)
    s = ["### " + ("Türetim: [x̂, p̂] = iħ" if tr
                   else "Derivation: [x, p] = i hbar"), ""]
    s.append("**" + ("Tanımlar" if tr else "Definitions") + "**")
    s.append("")
    s.append("- `x̂ψ = x·ψ`")
    s.append("- `p̂ψ = −iħ ∂ψ/∂x`")
    s.append("")
    s.append("**" + ("Hesap" if tr else "Computation") + "**")
    s.append("")
    s.append("`x̂(p̂ψ) = %s`" % sp.sstr(op_x(op_p(_psi(x)))))
    s.append("")
    s.append("`p̂(x̂ψ) = %s`" % sp.sstr(sp.expand(op_p(op_x(_psi(x))))))
    s.append("")
    s.append("`[x̂,p̂]ψ = x̂p̂ψ − p̂x̂ψ = %s`" % sp.sstr(kom))
    s.append("")
    if kat is not None:
        s.append("## `[x̂, p̂] = %s`" % sp.sstr(kat))
    s.append("")
    s.append("_" + ("Bu sonuç yazılı bir metinden alınmadı; operatörler ψ "
                    "üzerine etkitilip fark SymPy ile hesaplandı."
                    if tr else
                    "Computed with SymPy, not read from text.") + "_")
    return "\n".join(s)


def turet_ehrenfest(lang="tr"):
    """Ehrenfest teoremi — komutatorleri hesaplayarak."""
    tr = lang == "tr"
    s = ["### " + ("Türetim: Ehrenfest Teoremi" if tr
                   else "Derivation: Ehrenfest's Theorem"), ""]
    s.append(("Beklenen değerlerin klasik hareket denklemlerine uyduğunu "
              "gösteriyoruz. Tek araç Heisenberg hareket denklemidir:"
              if tr else
              "We show expectation values obey the classical equations."))
    s.append("")
    s.append("`d⟨Â⟩/dt = (1/iħ)·⟨[Â, Ĥ]⟩`")
    s.append("")

    # 1) A = x
    kom_x = komutator(op_x, op_H)
    sag_x = sp.simplify(kom_x / (sp.I * hbar))
    s.append("**1) " + ("Konum için" if tr else "For position") + " (Â = x̂)**")
    s.append("")
    s.append("`[x̂,Ĥ]ψ = %s`" % sp.sstr(kom_x))
    s.append("")
    s.append("`(1/iħ)[x̂,Ĥ]ψ = %s`" % sp.sstr(sag_x))
    s.append("")
    # p̂ψ = -iħ ψ' oldugundan sag taraf p/m'dir; bunu gosterelim
    p_uzeri_m = sp.simplify(op_p(_psi(x)) / m)
    ayni = sp.simplify(sp.expand(sag_x - p_uzeri_m)) == 0
    if ayni:
        s.append("`p̂ψ/m = %s` — " % sp.sstr(p_uzeri_m)
                 + ("aynı ifade" if tr else "the same expression"))
        s.append("")
        s.append("## `d⟨x̂⟩/dt = ⟨p̂⟩/m`")
    s.append("")

    # 2) A = p
    kom_p = komutator(op_p, op_H)
    sag_p = sp.simplify(kom_p / (sp.I * hbar))
    s.append("**2) " + ("Momentum için" if tr else "For momentum")
             + " (Â = p̂)**")
    s.append("")
    s.append("`[p̂,Ĥ]ψ = %s`" % sp.sstr(kom_p))
    s.append("")
    s.append("`(1/iħ)[p̂,Ĥ]ψ = %s`" % sp.sstr(sag_p))
    s.append("")
    kuvvet = sp.simplify(-sp.diff(_V(x), x) * _psi(x))
    if sp.simplify(sp.expand(sag_p - kuvvet)) == 0:
        s.append("## `d⟨p̂⟩/dt = −⟨dV/dx⟩ = ⟨F⟩`")
        s.append("")
        s.append(("Yani dalga paketinin merkezi Newton'un ikinci yasasına "
                  "göre hareket eder. Klasik mekanik, kuantum mekaniğinin "
                  "beklenen değerlerinde görünür."
                  if tr else
                  "The packet centre obeys Newton's second law."))
    s.append("")
    s.append("_" + ("Her iki komütatör de ψ üzerine etkitilerek SymPy ile "
                    "hesaplandı; sonuç yazılı bir metinden alınmadı."
                    if tr else "Both commutators were computed with SymPy.")
             + "_")
    return "\n".join(s)


def turet_viryal(lang="tr"):
    """Viryal teoremi: duragan durumda 2⟨T⟩ = ⟨x dV/dx⟩."""
    tr = lang == "tr"
    op_xp = op_carp(op_x, op_p)          # x̂p̂
    kom = komutator(op_xp, op_H)
    sag = sp.simplify(kom / (sp.I * hbar))
    s = ["### " + ("Türetim: Viryal Teoremi" if tr
                   else "Derivation: the Virial Theorem"), ""]
    s.append(("Â = x̂p̂ seçip Heisenberg denklemini uyguluyoruz. Durağan "
              "bir durumda beklenen değerler zamanla değişmez, yani "
              "d⟨x̂p̂⟩/dt = 0'dır." if tr else
              "Take A = x p in the Heisenberg equation; in a stationary "
              "state d<xp>/dt = 0."))
    s.append("")
    s.append("`d⟨x̂p̂⟩/dt = (1/iħ)·⟨[x̂p̂, Ĥ]⟩ = 0`")
    s.append("")
    s.append("`[x̂p̂,Ĥ]ψ = %s`" % sp.sstr(kom))
    s.append("")
    s.append("`(1/iħ)[x̂p̂,Ĥ]ψ = %s`" % sp.sstr(sag))
    s.append("")
    # Beklenen: (ħ²/m)ψ'' - x V' ψ  →  2T - x dV/dx
    iki_T = sp.simplify(2 * op_T(_psi(x)))
    x_dV = sp.simplify(x * sp.diff(_V(x), x) * _psi(x))
    fark = sp.simplify(sp.expand(sag - (iki_T - x_dV)))
    if fark == 0:
        s.append("`2·T̂ψ − x(dV/dx)ψ = %s` — %s"
                 % (sp.sstr(sp.simplify(iki_T - x_dV)),
                    "aynı ifade" if tr else "the same expression"))
        s.append("")
        s.append("## `2⟨T̂⟩ = ⟨x·dV/dx⟩`")
        s.append("")
        s.append(("Kuvvet yasası V = k·xⁿ ise x·dV/dx = n·V olur ve "
                  "`2⟨T⟩ = n⟨V⟩` çıkar. Harmonik osilatörde (n = 2) "
                  "⟨T⟩ = ⟨V⟩; Coulomb'da (n = −1) `2⟨T⟩ = −⟨V⟩`."
                  if tr else
                  "For V = k x^n one gets 2<T> = n<V>."))
    else:
        s.append("_" + ("Sadeleştirme tamamlanamadı." if tr
                        else "Simplification incomplete.") + "_")
    s.append("")
    s.append("_" + ("[x̂p̂, Ĥ] komütatörü ψ üzerine etkitilerek hesaplandı."
                    if tr else "The commutator was computed with SymPy.")
             + "_")
    return "\n".join(s)


# ── Uc boyut: acisal momentum cebri ───────────────────────────────────────
# Ayni yontem, tek degisiklik: dalga fonksiyonu uc degiskenli.

y, z = sp.symbols("y z", real=True)
_psi3 = sp.Function("psi")


def _f3():
    return _psi3(x, y, z)


def op_px(f):
    return -sp.I * hbar * sp.diff(f, x)


def op_py(f):
    return -sp.I * hbar * sp.diff(f, y)


def op_pz(f):
    return -sp.I * hbar * sp.diff(f, z)


def op_Lx(f):
    """L̂x = ŷp̂z − ẑp̂y"""
    return y * op_pz(f) - z * op_py(f)


def op_Ly(f):
    """L̂y = ẑp̂x − x̂p̂z"""
    return z * op_px(f) - x * op_pz(f)


def op_Lz(f):
    """L̂z = x̂p̂y − ŷp̂x"""
    return x * op_py(f) - y * op_px(f)


def turet_acisal_momentum(lang="tr"):
    """[L̂x, L̂y] = iħL̂z — hesaplayarak.

    Acisal momentum cebri elle yazilmadi; uc boyutlu diferansiyel
    operatorler ψ(x,y,z) uzerine etkitilip fark alindi.
    """
    tr = lang == "tr"
    f = _f3()
    kom = sp.simplify(sp.expand(op_Lx(op_Ly(f)) - op_Ly(op_Lx(f))))
    hedef = sp.simplify(sp.expand(sp.I * hbar * op_Lz(f)))
    uyuyor = sp.simplify(sp.expand(kom - hedef)) == 0

    s = ["### " + ("Türetim: Açısal Momentum Cebri" if tr
                   else "Derivation: the angular momentum algebra"), ""]
    s.append("**" + ("Tanımlar" if tr else "Definitions") + "**")
    s.append("")
    s.append("- `L̂x = ŷp̂z − ẑp̂y`,  `L̂y = ẑp̂x − x̂p̂z`,  `L̂z = x̂p̂y − ŷp̂x`")
    s.append("- `p̂ᵢψ = −iħ ∂ψ/∂xᵢ`")
    s.append("")
    s.append("**" + ("Hesap" if tr else "Computation") + "**")
    s.append("")
    s.append("`[L̂x,L̂y]ψ = L̂x(L̂yψ) − L̂y(L̂xψ)`")
    s.append("")
    s.append("`= %s`" % sp.sstr(kom))
    s.append("")
    s.append("`iħL̂zψ = %s`" % sp.sstr(hedef))
    s.append("")
    if uyuyor:
        s.append("## `[L̂x, L̂y] = iħ L̂z`")
        s.append("")
        s.append(("Döngüsel olarak `[L̂y,L̂z] = iħL̂x` ve `[L̂z,L̂x] = iħL̂y`. "
                  "Bu üç bağıntı açısal momentum cebridir; spin de aynı "
                  "cebri sağlar ama `r̂ × p̂` biçiminde yazılamaz — spinin "
                  "klasik karşılığının olmamasının sebebi budur."
                  if tr else
                  "Cyclic permutations give the full algebra; spin obeys the "
                  "same algebra without being r x p."))
    else:
        s.append("_" + ("Sadeleştirme tamamlanamadı." if tr
                        else "Simplification incomplete.") + "_")
    s.append("")
    s.append("_" + ("Üç boyutlu operatörler ψ(x,y,z) üzerine etkitilip "
                    "fark SymPy ile hesaplandı; yazılı bir metinden "
                    "alınmadı." if tr else
                    "Computed with SymPy in three dimensions.") + "_")
    return "\n".join(s)


def turet_L2_Lz(lang="tr"):
    """[L̂², L̂z] = 0 — hesaplayarak."""
    tr = lang == "tr"
    f = _f3()

    def op_L2(g):
        return (op_Lx(op_Lx(g)) + op_Ly(op_Ly(g)) + op_Lz(op_Lz(g)))

    kom = sp.simplify(sp.expand(op_L2(op_Lz(f)) - op_Lz(op_L2(f))))
    s = ["### " + ("Türetim: [L̂², L̂z] = 0" if tr
                   else "Derivation: [L^2, Lz] = 0"), ""]
    s.append(("`L̂² = L̂x² + L̂y² + L̂z²` tanımlayıp komütatörü hesaplıyoruz."
              if tr else "Define L^2 and compute the commutator."))
    s.append("")
    s.append("`[L̂²,L̂z]ψ = %s`" % sp.sstr(kom))
    s.append("")
    if sp.simplify(kom) == 0:
        s.append("## `[L̂², L̂z] = 0`")
        s.append("")
        s.append(("Sıfır olması şu demektir: `L̂²` ile `L̂z` AYNI ANDA "
                  "keskin ölçülebilir. Kuantum durumlarının `|ℓ,m⟩` diye "
                  "iki sayıyla etiketlenmesinin sebebi budur. Buna karşılık "
                  "`[L̂x,L̂y] ≠ 0` olduğu için iki bileşen aynı anda keskin "
                  "olamaz."
                  if tr else
                  "Zero means L^2 and Lz share eigenstates, which is why "
                  "states are labelled |l,m>."))
    s.append("")
    s.append("_" + ("SymPy ile hesaplandı." if tr
                    else "Computed with SymPy.") + "_")
    return "\n".join(s)



# ── Uc yeni yetenek: hepsi HESAPLANIR ─────────────────────────────────────

def turet_degiskenlere_ayirma(lang="tr"):
    """Zamana bagli denklemden zamandan bagimsiz denklemi cikar."""
    tr = lang == "tr"
    fi = sp.Function("phi")(x)
    g = sp.Function("f")(t)
    E = sp.Symbol("E", real=True)
    # Psi = phi(x)*f(t) yerine konur
    Psi = fi * g
    sol = sp.I * hbar * sp.diff(Psi, t)
    sag = -hbar ** 2 / (2 * m) * sp.diff(Psi, x, 2) + _V(x) * Psi
    # Iki tarafi da Psi'ye bolersek degiskenler ayrilir
    solb = sp.simplify(sol / Psi)
    sagb = sp.simplify(sag / Psi)
    s = ["### " + ("Türetim: Değişkenlere Ayırma" if tr
                   else "Derivation: separation of variables"), ""]
    s.append(("Zamana bağlı Schrödinger denkleminde `Ψ(x,t) = φ(x)·f(t)` "
              "deneriz — yani çözümün ayrılabilir olduğunu VARSAYARIZ."
              if tr else "Try Psi = phi(x) f(t)."))
    s.append("")
    s.append("`iħ ∂Ψ/∂t = %s`" % sp.sstr(sol))
    s.append("")
    s.append("`ĤΨ = %s`" % sp.sstr(sag))
    s.append("")
    s.append(("**Her iki tarafı da Ψ'ye bölelim:**" if tr
              else "**Divide both sides by Psi:**"))
    s.append("")
    s.append("`sol/Ψ = %s`   (yalnızca t'ye bağlı)" % sp.sstr(solb))
    s.append("")
    s.append("`sağ/Ψ = %s`   (yalnızca x'e bağlı)" % sp.sstr(sagb))
    s.append("")
    s.append(("Sol taraf yalnızca `t`'ye, sağ taraf yalnızca `x`'e bağlı. "
              "İki bağımsız değişkenin fonksiyonları her yerde eşitse, "
              "ikisi de aynı **SABİTE** eşittir. Bu sabite `E` diyoruz "
              "(boyutu enerjidir)." if tr else
              "Both sides must equal the same constant E."))
    s.append("")
    s.append("**" + ("Zaman kısmı" if tr else "Time part") + ":** "
             "`iħ df/dt = E·f`  ⇒  `f(t) = e^(−iEt/ħ)`")
    s.append("")
    s.append("**" + ("Uzay kısmı" if tr else "Space part") + ":** "
             "`−(ħ²/2m)φ'' + Vφ = Eφ`")
    s.append("")
    s.append("## `Ĥφ = Eφ`  " + ("(zamandan bağımsız Schrödinger denklemi)"
                                 if tr else "(time-independent equation)"))
    s.append("")
    s.append(("Zaman çarpanının modülü `|e^(−iEt/ħ)| = 1` olduğu için "
              "`|Ψ|² = |φ|²` zamanla değişmez — bu yüzden bu çözümlere "
              "**durağan durum** denir." if tr else
              "The time factor has unit modulus, hence stationary states."))
    s.append("")
    s.append("_" + ("Yerine koyma ve bölme SymPy ile yapıldı." if tr
                    else "Computed with SymPy.") + "_")
    return "\n".join(s)


def turet_superpozisyon(lang="tr"):
    """Superpozisyon ilkesi: denklemin DOGRUSALLIGINDAN cikar."""
    tr = lang == "tr"
    p1 = sp.Function("psi1")(x, t)
    p2 = sp.Function("psi2")(x, t)
    c1, c2 = sp.symbols("c1 c2")

    def _S(psi):
        """Schrodinger operatorunun psi'ye etkisi (sifira esit olmali)."""
        return (sp.I * hbar * sp.diff(psi, t)
                + hbar ** 2 / (2 * m) * sp.diff(psi, x, 2) - _V(x) * psi)

    toplam = sp.expand(_S(c1 * p1 + c2 * p2))
    ayri = sp.expand(c1 * _S(p1) + c2 * _S(p2))
    ayni = sp.simplify(toplam - ayri) == 0
    s = ["### " + ("Türetim: Süperpozisyon İlkesi" if tr
                   else "Derivation: the superposition principle"), ""]
    s.append(("Schrödinger denklemini `Ŝψ = 0` biçiminde yazalım: "
              "`Ŝψ ≡ iħ∂ψ/∂t + (ħ²/2m)∂²ψ/∂x² − Vψ`." if tr else
              "Write the equation as S psi = 0."))
    s.append("")
    s.append("`Ŝ(c₁ψ₁ + c₂ψ₂) = %s`" % sp.sstr(toplam))
    s.append("")
    s.append("`c₁·Ŝψ₁ + c₂·Ŝψ₂ = %s`" % sp.sstr(ayri))
    s.append("")
    if ayni:
        s.append(("**İki ifade özdeştir.** Yani `Ŝ` DOĞRUSAL bir "
                  "operatördür: türev almak ve bir fonksiyonla çarpmak "
                  "doğrusal işlemlerdir." if tr else
                  "The two are identical, so S is linear."))
        s.append("")
        s.append(("`ψ₁` ve `ψ₂` çözümse (`Ŝψ₁ = Ŝψ₂ = 0`), o hâlde"
                  if tr else "If both are solutions, then"))
        s.append("")
        s.append("## `Ŝ(c₁ψ₁ + c₂ψ₂) = c₁·0 + c₂·0 = 0`")
        s.append("")
        s.append(("Yani **çözümlerin her doğrusal birleşimi de çözümdür**. "
                  "Süperpozisyon bir postülat değil, denklemin "
                  "doğrusallığının doğrudan sonucudur. Girişim, "
                  "dolanıklık ve kuantum bilgisayarların çalışma ilkesi "
                  "buradan gelir." if tr else
                  "Any linear combination of solutions is a solution."))
    s.append("")
    s.append("_" + ("Doğrusallık SymPy ile açılıp karşılaştırıldı."
                    if tr else "Linearity verified with SymPy.") + "_")
    return "\n".join(s)


def turet_indirgenmis_kutle(lang="tr"):
    """Iki cisim problemi -> tek cisim, indirgenmis kutle ile."""
    tr = lang == "tr"
    m1, m2 = sp.symbols("m1 m2", positive=True)
    r1 = sp.Function("r1")(t)
    r2 = sp.Function("r2")(t)
    R = (m1 * r1 + m2 * r2) / (m1 + m2)          # kutle merkezi
    r = r1 - r2                                   # goreli konum
    # Toplam kinetik enerji
    T = sp.Rational(1, 2) * m1 * sp.diff(r1, t) ** 2 + \
        sp.Rational(1, 2) * m2 * sp.diff(r2, t) ** 2
    # r1, r2'yi R ve r cinsinden yaz
    r1_yeni = R + m2 / (m1 + m2) * r
    r2_yeni = R - m1 / (m1 + m2) * r
    T_yeni = sp.simplify(sp.expand(
        T.subs({r1: r1_yeni, r2: r2_yeni}).doit()))
    mu = sp.simplify(m1 * m2 / (m1 + m2))
    T_bekl = sp.simplify(
        sp.Rational(1, 2) * (m1 + m2) * sp.diff(R, t) ** 2
        + sp.Rational(1, 2) * mu * sp.diff(r, t) ** 2)
    T_bekl = sp.simplify(sp.expand(
        T_bekl.subs({r1: r1_yeni, r2: r2_yeni}).doit()))
    ayni = sp.simplify(T_yeni - T_bekl) == 0
    s = ["### " + ("Türetim: İndirgenmiş Kütle" if tr
                   else "Derivation: reduced mass"), ""]
    s.append(("İki cisim problemi, doğru koordinatlarda TEK cisim "
              "problemine dönüşür." if tr else
              "The two-body problem becomes a one-body problem."))
    s.append("")
    s.append("**" + ("Koordinat değişimi" if tr else "New coordinates")
             + ":**")
    s.append("")
    s.append("- Kütle merkezi: `R = (m₁r₁ + m₂r₂)/(m₁+m₂)`")
    s.append("- Göreli konum: `r = r₁ − r₂`")
    s.append("")
    s.append(("Ters çevirince `r₁ = R + (m₂/M)r`, `r₂ = R − (m₁/M)r` "
              "(M = m₁+m₂). Kinetik enerjiye koyalım:" if tr else
              "Substituting into the kinetic energy:"))
    s.append("")
    if ayni:
        s.append("## `T = ½M·Ṙ² + ½μ·ṙ²`,  `μ = m₁m₂/(m₁+m₂)`")
        s.append("")
        s.append(("**Çapraz terimler birbirini götürür** — SymPy ile "
                  "açıp doğruladık. Sonuç iki BAĞIMSIZ parçadır: kütle "
                  "merkezinin serbest hareketi ve `μ` kütleli tek bir "
                  "parçacığın göreli hareketi.\n\n"
                  "Potansiyel yalnızca `|r|`'ye bağlıysa (merkezî kuvvet) "
                  "kütle merkezi hiç görünmez ve geriye **tek cisim "
                  "problemi** kalır. Hidrojen atomunda çekirdek sonsuz "
                  "ağır sayılmazsa `μ = mₑM/(mₑ+M)` kullanılır; bu, "
                  "döteryum ile hidrojenin tayflarının neden biraz farklı "
                  "olduğunu açıklar." if tr else
                  "Cross terms cancel; the motion splits into free CM "
                  "motion and a one-body problem with reduced mass."))
    else:
        s.append("_" + ("Sadeleştirme tamamlanamadı." if tr
                        else "Simplification incomplete.") + "_")
    s.append("")
    s.append("_" + ("Koordinat değişimi ve sadeleştirme SymPy ile yapıldı."
                    if tr else "Computed with SymPy.") + "_")
    return "\n".join(s)


# ── Disariya acilan yuz: soruyu tanı ve turet ─────────────────────────────

import re

_ISTEKLER = [
    (r"\behrenfest\b", turet_ehrenfest),
    (r"\bviry?al\b|\bvirial\b|2\s*⟨?t⟩?\s*=", turet_viryal),
    (r"\[\s*x\s*,\s*p|komutator.*x.*p|x.*p.*komutator|"
     r"\bkanonik komutasyon\b", turet_xp_komutator),
    (r"\bl\s*kare\b|\[\s*l.?2\s*,|l2.*lz|lz.*l2|"
     r"acisal momentum.*ayni anda|ayni anda.*acisal momentum",
     turet_L2_Lz),
    (r"degiskenlere ayir|degiskenine ayir|ayirma yontemi|"
     r"zamandan bagimsiz.*zamana bagli|zamana bagli.*zamandan bagimsiz",
     turet_degiskenlere_ayirma),
    (r"superpozisyon|super pozisyon|dogrusallig|dogrusalligindan|"
     r"cozumlerin toplami da cozum", turet_superpozisyon),
    (r"indirgenmis kutle|iki cisim problemi|reduced mass|two.body",
     turet_indirgenmis_kutle),
    (r"acisal momentum.*(cebir|komutator|bagint)|"
     r"(cebir|komutator|bagint).*acisal momentum|"
     r"\[\s*lx\s*,\s*ly|lx.*ly.*komutator|"
     r"acisal momentum bilesenleri", turet_acisal_momentum),
]


def istek_mi(metin):
    """Bu soru, motorun HESAPLAYABILECEGI bir turetim mi?"""
    n = (metin or "").lower()
    n = n.replace("ı", "i").replace("ş", "s").replace("ğ", "g")
    n = n.replace("ü", "u").replace("ö", "o").replace("ç", "c")
    return any(re.search(k, n) for k, _f in _ISTEKLER)


def coz(metin, lang="tr"):
    """Soruyu tanı ve turetimi HESAPLAYARAK uret; tanimazsa None."""
    n = (metin or "").lower()
    n = n.replace("ı", "i").replace("ş", "s").replace("ğ", "g")
    n = n.replace("ü", "u").replace("ö", "o").replace("ç", "c")
    for kalip, fonk in _ISTEKLER:
        if re.search(kalip, n):
            try:
                return fonk(lang)
            except Exception:
                return None
    return None


def kapsam():
    """Motorun HESAPLAYABILDIGI turetimler (durustluk icin acikca)."""
    return ["[x̂,p̂] = iħ", "Ehrenfest teoremi", "Viryal teoremi",
            "[L̂x,L̂y] = iħL̂z (acisal momentum cebri)", "[L̂²,L̂z] = 0",
            "Degiskenlere ayirma", "Superpozisyon ilkesi",
            "Indirgenmis kutle"]
