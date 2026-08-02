"""Dogal dil anlama: dil tespiti, niyet siniflandirma, varlik cikarimi.

Kural tabanli ve determinist calisir. Turkce ve Ingilizce destekler.
"""
import re
import unicodedata

# ---------------------------------------------------------------- dil tespiti
TR_CHARS = set("çğıöşüÇĞİÖŞÜ")
TR_WORDS = set("""nedir nasil neden hangi kac kacar bir bu su ve veya ile ama fakat
icin gibi daha cok az en ben sen o biz siz onlar var yok mi mu mı mü degil
hesapla bul goster anlat ornek soru cozum yap yaz olur olsun mudur midir
lutfen tesekkur merhaba selam sagol nasilsin kadar sonra once simdi
formul formulu denklem denklemi birim birimi cevir donustur sabit sabiti
konu konusu ozet ozetle acikla aciklama makale makaleler arastirma
turev integral limit seri matris cozumu enerji kuvvet hiz ivme kutle
zaman uzunluk sicaklik basinc akim gerilim direnc frekans dalga""".split())

EN_WORDS = set("""what how why which the and or but for with from this that
is are was were can could would should will explain show calculate compute
solve find give example problem hello hi thanks please tell about summary
summarize formula equation unit convert constant paper article research
derivative integral limit series matrix energy force velocity acceleration
mass time length temperature pressure current voltage resistance frequency
to into many much meters metres seconds grams degrees convert code write
laws law between using into per each does did""".split())


def detect_lang(text):
    """Metnin dilini tahmin et. 'tr' veya 'en'."""
    t = (text or "").lower()
    if any(ch in TR_CHARS for ch in t):
        return "tr"
    words = set(re.findall(r"[a-zçğıöşü]+", t))
    tr_hits = len(words & TR_WORDS)
    en_hits = len(words & EN_WORDS)
    # Turkce eklerin izleri
    # Turkce cekim ekleri. "seti", "sorusu", "konusu" gibi iyelik ekleri
    # de sayilir; olculdu: "termodinamik problem seti" istegi INGILIZCE
    # sanilip cevap Ingilizce donuyordu ("problem" iki dilde de var).
    tr_suffix = len(re.findall(r"\w+(?:lar|ler|dir|dır|dur|dür|mek|mak|nin|nın|"
                               r"yor|acak|ecek|miş|mis|ları|leri)\b", t))
    # Bagimsiz Turkce kelimeler: "seti", "sorusu", "konusu"... Olculdu:
    # "termodinamik problem seti" istegi INGILIZCE sanilyordu, cunku
    # "problem" iki dilde de var ve ekli kelime yakalanmiyordu.
    tr_suffix += len(re.findall(
        r"\b(seti|sorulari|sorusu|konusu|cozumu|çözümü|alistirma|"
        r"alıştırma|ornekler|örnekler|anlat|ogret|öğret|nedir|nasil|"
        r"nasıl|neden)\b", t))
    tr_hits += tr_suffix
    if tr_hits > en_hits:
        return "tr"
    if en_hits > tr_hits:
        return "en"
    # Berabere: kisa terim sorularinda ("ultraviolet catastrophe",
    # "density of states") ne Turkce harf ne de listelenmis kelime var ve
    # soru sessizce Turkce sayiliyordu; cevap da Turkce donuyordu
    # (olculdu). Karari cekirdek bilgi tabanina sorariz: bu kelimeler
    # anlatimlarin INGILIZCE metninde mi geciyor, TURKCE metninde mi?
    return _cekirdekten_dil(t)


_DIL_SOZLUK = {"en": None, "tr": None}


def _dil_sozlugu():
    """Cekirdek anlatimlardan dile OZGU kelime kumeleri."""
    if _DIL_SOZLUK["en"] is None:
        try:
            from . import knowledge
            en, tr = set(), set()
            for k in knowledge.TOPICS:
                en |= set(re.findall(r"[a-z]{4,}", (k.get("en") or "").lower()))
                tr |= set(re.findall(r"[a-z]{4,}",
                                     norm(k.get("tr") or "").lower()))
            _DIL_SOZLUK["en"] = en - tr
            _DIL_SOZLUK["tr"] = tr - en
        except Exception:
            _DIL_SOZLUK["en"], _DIL_SOZLUK["tr"] = set(), set()
    return _DIL_SOZLUK["en"], _DIL_SOZLUK["tr"]


def _cekirdekten_dil(t):
    en_sozluk, tr_sozluk = _dil_sozlugu()
    if not en_sozluk:
        return "tr"
    kelimeler = set(re.findall(r"[a-z]{4,}", t))
    e, r = len(kelimeler & en_sozluk), len(kelimeler & tr_sozluk)
    if e > r:
        return "en"
    return "tr"


def norm(s):
    s = (s or "").lower()
    for a, b in {"ı": "i", "İ": "i", "ş": "s", "ğ": "g", "ü": "u",
                 "ö": "o", "ç": "c", "â": "a", "î": "i", "û": "u"}.items():
        s = s.replace(a, b)
    return s


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")


# ------------------------------------------------------------- niyet oruntusu
# (niyet, oncelik, desenler)
# ── Yonerge fiilleri ──────────────────────────────────────────────────
# Sinav/odev dilinde "yapilacak isi" bildiren fiiller. Bu liste IKI ayri
# yerde gerekiyor ve ayri ayri yazildiklarinda birbirinden SAPIYORLAR;
# olculen iki ayri kusur da tam olarak bundan cikti:
#
#   * bilesik.py'deki liste "coz" fiilini icermiyordu; "Klasik harmonik
#     osilator denklemini COZ. Daha sonra ..." sorusunda birinci asama
#     komple dusuyordu.
#   * asagidaki "sifirdan" kaliginin istisna listesi "tanit" fiilini
#     icermiyordu; "Dirac gosterimini SIFIRDAN TANIT" sorusu bir
#     ogrenme plani istegi sanilip yol haritasi cevabi aliyordu.
#
# Bu yuzden liste TEK yerde tutulur ve her iki taraf da buradan okur.
# NOT: "et-" yardimci fiili cekimlenirken UNSUZ YUMUSAMASINA ugrar:
# "elde ET" ama "elde EDiniz", "elde EDerek". Duz "elde et" kalibi
# "elde ediniz"i KACIRIYORDU ve 4 asamali soru 3 asama goruluyordu
# (olculdu). Bu yuzden o fiillerde e[dt] siniifi kullanilir.
YONERGE_FIILLERI = (
    "turet", "elde e[dt]", "ispatla", "ispat e[dt]", "kanitla", "goster",
    "acikla", "cikar", "yaz", "kur", "bul", "hesapla", "anlat",
    "tanimla", "coz", "tanit", "incele", "tartis", "degerlendir",
    "karsilastir", "belirle", "ifade e[dt]", "ele al", "uygula", "yorumla",
    "derive", "prove", "show", "obtain", "explain", "find", "solve",
    "compute", "evaluate", "discuss", "compare", "determine", "introduce",
)

# Regex parcasi: "turet\\w*|elde\\s+et\\w*|..."
YONERGE_KALIBI = "|".join(
    f.replace(" ", r"\s+") + r"\w*" for f in YONERGE_FIILLERI)


PATTERNS = [
    ("selam", 100, [
        r"^\s*(merhaba|selam|slm|gunaydin|iyi (gunler|aksamlar|geceler)|"
        r"hello|hi|hey|good (morning|evening|afternoon))\b",
        r"^\s*nasilsin\b", r"^\s*how are you\b",
    ]),
    # Kisa ONAY mesajlari bir soru degildir. Olculdu: "tamam anladim"
    # mesajina "bu konuda henuz yeterli bilgim yok" cevabi geliyordu ve
    # sohbet orada oluyordu — kullanicinin "2-3 mesajdan sonra duruyor"
    # dedigi durumun bir sebebi buydu.
    ("onay", 105, [
        r"^\s*(tamam|tmm|anladim|anladim tamam|tamam anladim|peki tamam|"
        r"oldu|olur|iyi|guzel|harika|super|mukemmel|evet|hmm|ok|okey|okay|"
        r"got it|i see|understood|makes sense|alright)"
        r"[\s.!,]*$",
    ]),
    ("tesekkur", 100, [
        r"\b(tesekkur|tesekkurler|sagol|sag ol|eyvallah|thanks|thank you|thx)\b",
    ]),
    ("yardim", 95, [
        r"^\s*(yardim|help|ne yapabilirsin|neler yapabilirsin|komutlar|"
        r"what can you do|commands|nasil kullanilir)\b",
        r"^/?(help|yardim)\s*$",
    ]),
    # Yol haritasi, "matlab" niyetinden ONCE eslesmeli: "matlab ogrenmek
    # istiyorum" bir kod istegi degil, bir plan istegidir.
    ("yol_haritasi", 110, [
        r"\b(yol haritasi|yol haritas|roadmap|mufredat|curriculum|ogrenme plani|"
        r"calisma plani|learning path|study plan)\b",
        r"\b(nereden|nasil)\s+(baslamali|baslayayim|baslarim|basliyorum|"
        r"ogrenebilirim|ogrenirim)\b",
        r"\bwhere (should|do) i (start|begin)\b", r"\bhow (do|can) i learn\b",
        r"\b(ogrenmek istiyorum|ogrenmeye baslamak|sifirdan ogren|"
        r"yeni basliyorum|yeni baslayan|hic bilmiyorum|acemiyim)\b",
        r"\b(want to learn|just starting|complete beginner|new to)\b",
        r"\b(ne ogretebilirsin|neler ogretebilirsin|bana ogret|"
        r"ogret(ir|ebilir|ebilir m[iı]s[iı]n)|ogretebilir misin|"
        r"what can you teach|teach me|can you teach)\b",
        # "sifirdan TURET/ISPATLA" bir ogrenme plani istegi degildir.
        # Istisna listesi ELLE yaziliydi ve "tanit" eksikti;
        # "Dirac gosterimini sifirdan tanit" ogrenme plani
        # sanildi (olculdu). Artik ortak listeden kuruluyor.
        r"\bsifirdan\b(?!\s*(?:%s))" % YONERGE_KALIBI,
        # "matlab ogrenmek zor mu" bir kod istegi degil: zorluk/sure sorulari
        # da plan tarafina gitmeli.
        r"\b(ogrenmek|ogrenmesi)\s+(zor|kolay|ne kadar surer|zor mu)\b",
        r"\b(nasil ogrenilir|nasil ogrenirim|nereden ogrenirim)\b",
        r"\b(temelden|en bastan|adim adim ogren|bastan sona ogren)\b",
        r"\b(baslangic (rehberi|seviyesi)|beginner('s)? guide)\b",
    ]),
    ("beni_unut", 120, [
        r"\b(beni unut|profilimi sil|hakkimdaki(leri)? sil|bildiklerini sil|"
        r"kisisel verilerimi sil|forget me|forget about me|erase my (profile|data)|"
        r"delete my (profile|data))\b",
    ]),
    ("profil", 115, [
        r"\b(beni taniyor musun|beni biliyor musun|adimi biliyor musun|"
        r"adimi hatirliyor musun|hakkimda ne biliyorsun|benim hakkimda|"
        r"hakkimda neler biliyorsun|kimim ben|beni hatirliyor musun|"
        r"do you (know|remember) me|what do you know about me|"
        r"do you remember my name|who am i)\b",
    ]),
    ("kendini_tanit", 112, [
        # "adim adim turet" bir isim tanitmasi DEGILDIR (olculdu: sistem
        # kullanicinin adini "Adim" sanip kaydediyordu). Ayrica ad olarak
        # gecen kelime bir fizik terimi olmamali.
        # "adim adim GOSTER/ANLAT/HESAPLA" bir ISIM tanitmasi degildir.
        # Olculdu: "...adim adim goster" ile biten bir ISPAT sorusu
        # kendini_tanit niyetine gidiyor ve fizik cevabi hic verilmiyordu.
        r"\b(ad[iı]m\s+(?!ad[iı]m\b)(?!turet)(?!coz)(?!goster)(?!anlat)"
        r"(?!hesapla)(?!yaz)(?!ilerle)\w+|ismim\s+\w+|"
        r"bana\s+\w+\s+(de|diyebilirsin)|my name is|call me)\b",
        # Kendini tanitan duzey ifadeleri: bunlar birer soru degildir, bu yuzden
        # konu aramasina dusup alakasiz bir madde donmemeli.
        r"\b(lise|lisans|yuksek lisans|doktora|universite)\s*(ogrencisi|"
        r"ogrenciyim|ogrencisiyim|mezunu|mezunuyum)?\s*(y[iı]m|[iı]m)?\b"
        r"(?=[^?]*$)",
        r"\b(ogrenciyim|ogrencisiyim|ogretmenim|muhendisim|fizikciyim|"
        r"arastirmaciyim|akademisyenim|meraklisiyim|acemiyim)\b",
        r"\b(i am|i'?m) (a |an )?(student|teacher|engineer|physicist|researcher|"
        r"beginner|undergraduate|phd|graduate)\b",
    ]),
    # "matlab konusunda ne kadar bilgin var" -> kod degil, yetenek anlatimi.
    # 'hakkimda/beni' iceren sorular profil niyetine aittir, buraya dusmez.
    ("yetenek", 108, [
        r"(?<!hakkimda )\b(ne kadar (bilgin var|biliyorsun|bilgiye sahipsin|"
        r"hakimsin|iyisin)|ne kadar bilirsin|bilgin var mi|biliyor musun)\b",
        r"\b(konusunda|hakkinda|alaninda|uzerine)\s+(ne|neler|ne kadar)\s+"
        r"(biliyorsun|bilgin|bilirsin|yapabilirsin)\b",
        r"\bhow (much|well) do you know\b", r"\bwhat do you know about\b",
        r"\bare you good at\b", r"\bhow good are you\b",
    ]),
    ("kendini_dogrula", 118, [
        r"\b(kendini (dogrula|sina|test et)|formullerini (dogrula|sina|kontrol et)|"
        r"bilgilerini kontrol et|dogrulama raporu|self.?(check|verify|test)|"
        r"verify (your|the) formulas)\b",
    ]),
    ("durum", 95, [
        r"\b(ne kadar ogrendin|ogrenme durumu|kac makale|istatistik|durum raporu|"
        r"veritabani durumu|learning status|how much have you learned|stats)\b",
        r"^/?(durum|status|stats)\s*$",
    ]),

    # --- Hesaplama niyetleri ---
    ("turev", 90, [
        r"\b(turev|turevini|turevi|differentiate|derivative)\b",
        r"\bd/d[a-z]\b",
    ]),
    ("integral", 90, [
        r"\b(integral|integralini|integrali|antiturev|integrate|antiderivative)\b",
        r"∫",
    ]),
    ("limit", 90, [
        r"\blimit(ini|i)?\b", r"\blim\s*[\(_]",
    ]),
    ("seri", 88, [
        r"\b(taylor|maclaurin|seri acilimi|series expansion|seriye ac)\b",
    ]),
    ("diferansiyel", 92, [
        r"\b(diferansiyel denklem|dif denklem|ode|differential equation)\b",
        r"\by''|\by'\s*[=+\-]",
    ]),
    ("matris", 88, [
        r"\b(matris|matrix|determinant|determinanti|ozdeger|eigenvalue|"
        r"ters matris|inverse matrix|matrisin)\b",
    ]),
    ("vektor", 86, [
        r"\b(gradyan|gradient|diverjans|divergence|rotasyonel|curl|"
        r"laplasyen|laplacian|nabla)\b",
    ]),
    # DIKKAT: "denklem" niyeti yalnizca gercekten CEBIRSEL bir ifade
    # varsa uygun. Olculdu: "sonsuz kuyuda n=3 enerji duzeyi hesapla"
    # cumlesi denklem sanilip Turkce kelimeler degisken olarak
    # ayristirildi ve "kuyuda*n*sonsuz = 3*duzeyi*enerji" gibi anlamsiz
    # bir cikti uretildi. Asagidaki suzgec `_cebirsel_mi` ile birlikte
    # calisir.
    ("denklem", 85, [
        r"\b(denklemi? coz|coz(um)?|solve|kokleri|kokunu bul|roots|"
        r"denklem sistemi|system of equations)\b",
        r"^[^=]+=[^=]+$",
    ]),
    ("birim", 92, [
        r"\b(cevir|donustur|kac (eder|yapar)|convert|in terms of)\b.*\b(m|km|cm|kg|g|s|"
        r"j|ev|w|n|pa|bar|atm|c|k|f|mph|km/h|m/s)\b",
        # "90 km/h kac m/s", "90 km/h -> m/s", "90 km/h to m/s", "5 J cinsinden eV"
        # Hedef birim degerin hemen ardindan gelmeli. Olculdu: "elektron
        # 100 V ile hizlandirilirsa kazandigi enerji kac joule" cumlesi
        # birim cevrimi sanilyordu; oysa arada bes kelime var ve bu bir
        # FIZIK problemidir.
        r"\d+(?:[.,]\d+)?\s*[a-zµωå°]+[a-zµωå°0-9/^*·\-]*\s*"
        r"(?:->|=>|\bto\b|\bin\b|\bkac\b|\bkacar\b|\bne kadar\b|\bolarak\b|\bcinsinden\b)"
        r"\s*[a-zµωå°]+[a-zµωå°0-9/^*·\-]*(?:\s*(?:eder|yapar|olur)\b)?\s*[?.!]?\s*$",
        # Bu kalip yalnizca KISA bir cevrim isteginde gecerli olmali:
        # "5 J kac eV" evet, "elektron 100 V ile hizlandirilirsa
        # kazandigi enerji kac joule" hayir — ikincisi fizik problemidir
        # (olculdu).
        r"^(?:\s*\S+){0,4}\s*\bkac\s+(metre|kilometre|santimetre|joule|kalori|elektronvolt|watt|"
        r"newton|pascal|kelvin|derece|saniye|dakika|saat|gram|kilogram|litre)\b",
    ]),
    ("selam_gunluk", 101, [
        # "naber", "nbr", "napiyorsun" gunluk sohbettir; bunlar duzeltilmemeli
        # ve hesap sanilmamali.
        r"\b(naber|nbr|nbrs|napiyorsun|napiyon|ne haber|nasil gidiyor|"
        r"iyi misin|keyifler nasil|whats up|what's up|how are you|how's it going)\b",
    ]),
    ("ogrendiklerim", 112, [
        r"\b(ogrendiklerin|ogrendiklerim|neler ogrendin|ne ogrendin|"
        r"bilgi bosluk|bosluklarin|sorularimdan)\b",
        r"\bwhat (have you|did you) learn(ed)?\b",
    ]),
    ("sabit", 90, [
        r"\b(sabiti?|constant)\b.*\b(nedir|kac|degeri|value|what is)\b",
        r"\b(sabitleri|sabitler|constants)\b.*\b(listele|goster|list|show)\b",
        r"^\s*(fiziksel )?(sabitler|sabitleri|constants)\s*$",
        r"\b(isik hizi|speed of light|planck|avogadro|boltzmann|gaz sabiti|"
        r"yercekimi ivmesi|elektron kutlesi|proton kutlesi|coulomb sabiti|"
        r"gravitational constant|elementary charge|bohr yaricapi|rydberg)\b",
    ]),
    ("turetim", 92, [
        # "adim adim", "turet", "nasil cozulur" — sonucu degil YOLU istiyor
        # Turkce ekler: "ispatlar misin", "ispatlayabilir misin", "kanitlar
        # misin". Duz \bispatla\b siniri bunlari tutmuyordu ve soru
        # "formul" niyetine dusup tek kart cevap aliyordu (olculdu:
        # "... hamiltonyan operatorunu ispatlar misin" -> Ek = mv²/2).
        r"\b(adim adim|adimlarla|nasil (cozulur|cozerim|turetilir|elde edilir)|"
        r"turet(imi|ilisi)?|nasil turetilir|cikarimi|ispatla\w*|ispat ed\w*|"
        r"ispat et\w*|kanitla\w*|goster\w* ki|"
        r"step by step|derive|derivation|prove that|show that)\b",
    ]),
    ("formul", 88, [
        r"\b(formul(u|un|unu|u nedir)?|denklemi nedir|bagintisi|equation for|"
        r"formula for|nasil hesaplanir|how (do you |to )?calculate)\b",
    ]),
    ("matlab", 95, [
        # Turkce ekler: "matlabda", "matlabta", "matlabla", "octave'de".
        # Duz \b siniri bunlari tutmuyordu; "matlabda denklem sistemini
        # nasil cozerim" MATLAB degil konu sorusu sayiliyordu.
        r"\b(matlab|octave|m-file|\.m dosyasi|simulink)(['’]?\w{0,4})?\b",
        r"\b(kod (yaz|uret|olustur)|script yaz|program yaz|write (a )?code|"
        r"generate (a )?script|simulasyon (yaz|kodu))\b",
    ]),
    ("hesap", 70, [
        # DIKKAT: bu kalip bir karakter kumesidir. Basinda rakam/islec
        # zorunlulugu olmadan "naber", "entropi", "baron" gibi kelimeler de
        # eslesiyor ve hesap motoruna gidiyordu (olculdu). En az bir rakam
        # ya da islec sart.
        r"^(?=.*[\d+\-*/^()])[\d\s\.\,\+\-\*\/\^\(\)piesqrtlogncoxbfa]+$",
        r"\b(hesapla|kac eder|sonucu|compute|calculate|evaluate)\b",
    ]),

    # --- Bilgi niyetleri ---
    ("makale", 90, [
        r"\b(makale|makaleler|arastirma|yayin|paper|papers|article|articles|"
        r"literatur|literature|preprint|arxiv|son calismalar|recent work)\b",
    ]),
    ("ornek", 85, [
        r"\b(ornek (ver|goster|problem|soru)|problem ver|soru (ver|sor|coz)|"
        r"alistirma|example|give me a problem|practice problem|exercise)\b",
    ]),
    ("konu", 60, [
        r"\b(nedir|ne demek|acikla|anlat|ozetle|ozet|konu anlatimi|"
        r"what is|explain|describe|tell me about|summarize|overview)\b",
    ]),
    ("liste", 80, [
        r"\b(konular(i|in)? (listele|neler)|hangi konular|ne biliyorsun|"
        r"list topics|what topics|what do you know)\b",
    ]),
]


# "sabit" kelimesi her zaman fiziksel sabit demek degildir: yay sabiti,
# zaman sabiti, bozunma sabiti birer FORMUL DEGISKENIDIR. Bunlar sabit
# listesini acmamali; "yay sabiti 200 N/m ise ivme nedir" bir hesap sorusu.
_DEGISKEN_SABIT = re.compile(
    r"\b(yay|zaman|bozunma|sonum|denge|hooke|rc|rl|kafes|orgu|kapasite|"
    r"spring|time|decay|damping|equilibrium|lattice)\s+sabit", re.I)

# Sabitin ADI baska bir KAVRAMIN icinde geciyorsa soru sabiti sormuyordur.
# Olculdu: "maxwell boltzmann dagilimi" sorusu "Boltzmann sabiti"
# cevabini aliyordu.
_SABIT_DEGIL = re.compile(
    r"\b(dagilim|dagilimi|istatistigi|denklemi|denklemleri|modeli|"
    r"yasasi|carpani|faktoru|sacilmasi|distribution|statistics)\b", re.I)


def _verili_deger_sorusu(t):
    """Birimli en az iki deger verilip bir buyukluk soruluyor mu?"""
    birimli = re.findall(
        r"\d+(?:[.,]\d+)?\s*(?:[a-zA-Zµ°]+(?:\s*/\s*[a-zA-Z0-9^]+)?)", t)
    if len(birimli) < 2:
        return False
    return bool(re.search(
        r"\b(nedir|kac|kacti|bulunuz|hesapla|ne olur|bul|ne kadar|"
        r"what is|find|calculate|how much)\b", t))


_CEBIR_HARF = re.compile(r"(?<![a-zA-Z])[a-zA-Z](?![a-zA-Z])")


def _cebirsel_mi(metin):
    """Metin gercekten cozulecek bir CEBIRSEL ifade mi?

    Olcut: "=" isaretinin iki yaninda da matematik var; kelimeler tek
    harfli degisken ya da sayi. Turkce bir cumlede "n=3" gecmesi o
    cumleyi denklem yapmaz.
    """
    t = (metin or "").strip()
    # Komut kelimeleri ifadenin parcasi degildir: "denklemi coz: 3x+1=7"
    # cumlesinde "denklemi" solda kaliyor ve ifade cebirsel sayilmiyordu.
    t = re.sub(r"\b(denklem(?:i|in|ini|ler|leri)?|coz|cozum|cozumu|cozun|hesapla|bul|"
               r"bulunuz|kokleri|kokunu|solve|equation|find|roots)\b",
               " ", t, flags=re.I)
    t = t.replace(":", " ").strip()
    if "=" not in t:
        # "=" yoksa yalnizca komut kelimeleri atildiktan sonra geriye
        # MATEMATIK kalmalidir. Olculdu: "yay kutle sistemini lagrange
        # ile coz" cumlesi yalnizca "coz" yuzunden denklem sanilyordu.
        kalan = re.sub(r"\b(coz|cozum|cozumu|cozun|kokleri|kokunu|bul|"
                       r"bulunuz|denklem|denklemi|denklemini|hesapla|"
                       r"solve|roots|find|equation)\b", " ", t, flags=re.I)
        kalan = re.sub(r"\s+", " ", kalan).strip()
        if not kalan:
            return False
        for w in re.findall(r"[a-zA-ZğüşıöçĞÜŞİÖÇ]+", kalan):
            if len(w) > 4 and w.lower() not in (
                    "sqrt", "exp", "log", "sin", "cos", "tan", "asin",
                    "acos", "atan", "sinh", "cosh", "tanh"):
                return False
        return bool(re.search(r"[\d\+\-\*/\^\(\)]", kalan))
    sol, _, sag = t.partition("=")
    for parca in (sol, sag):
        # Uc harften uzun kelimeler cebirsel degildir (fizik sembolleri
        # kisa olur: x, v0, dT, lam gibi).
        for w in re.findall(r"[a-zA-ZğüşıöçĞÜŞİÖÇ]+", parca):
            if len(w) > 3:
                return False
    return True


def classify(text):
    """Metnin niyetini belirle. (niyet, guven) doner."""
    t = norm(text or "")
    degisken_sabit = bool(_DEGISKEN_SABIT.search(t))
    hits = []
    for intent, prio, pats in PATTERNS:
        if intent == "sabit" and (degisken_sabit or _SABIT_DEGIL.search(t)):
            continue          # formul degiskeni ya da baska bir kavram
        for p in pats:
            if re.search(p, t):
                hits.append((prio, intent))
                break
    if not hits:
        # Sayisal/sembolik ifade gibi gorunuyorsa hesap. AMA uzun bir dogal
        # dil cumlesi icinde gecen "1/2" bunu tetiklememeli: "elektronun
        # spini neden 1/2 olarak olculur" sorusu hesap motoruna gidiyordu
        # (olculdu).
        # Kisa VE soru kelimesi icermeyen ifade hesaptir. "bir elektronun
        # spini neden 1/2 olarak olculur" yedi kelimeydi ve eski esikten
        # geciyordu; soru kelimesi denetimi bunu kesin ayirir.
        _soru_kelimesi = re.search(
            r"\b(neden|nasil|nedir|hangi|nicin|kimdir|misin|musun|"
            r"why|how|what|which|explain|anlat|ogret)\b", t)
        if (len(t.split()) <= 5 and not _soru_kelimesi
                and re.search(r"[\d\)]\s*[\+\-\*\/\^]\s*[\d\(a-z]", t)):
            return "hesap", 55
        if _verili_deger_sorusu(t):
            return "formul", 65
        return "konu", 30
    # "limit" niyeti ancak matematiksel bir limit istegi varsa gecerli:
    # "what is the Chandrasekhar limit" bir fizik kavramidir ve limit
    # cozucusune gidince ham ayristirici hatasi basiliyordu (olculdu).
    if hits and any(i == "limit" for _p, i in hits):
        if not re.search(r"(x|t|n)\s*(->|→|gider|yaklas|approach)|"
                         r"lim\s*[\(_]|sonsuz|infinity", t):
            hits = [(p_, i) for p_, i in hits if i != "limit"]
    hits.sort(reverse=True)
    # "denklem" niyeti ancak GERCEK bir cebirsel ifade varsa gecerlidir.
    # Aksi halde Turkce cumledeki kelimeler degisken sanilyor ve anlamsiz
    # bir "cozum" uretiliyordu (olculdu: "sonsuz kuyuda n=3 enerji
    # duzeyi hesapla" -> "kuyuda*n*sonsuz = 3*duzeyi*enerji").
    hits = [(p, i) for (p, i) in hits
            if i != "denklem" or _cebirsel_mi(text)]
    # TUREV/INTEGRAL/LIMIT niyetleri de ancak ISLENECEK BIR IFADE varsa
    # gecerlidir. Olculdu: "...neden IKINCI TUREV ciktigini ayrintili
    # olarak acikla" cumlesi turev hesaplayicisina gidiyor, hesaplayici
    # Turkce cumleyi matematik sanip cokuyordu:
    #   "Hata: Ifade cozumlenemedi: invalid syntax"
    # Bir kuramsal soruya hesap makinesiyle cevap vermek zaten yanlisti;
    # cokmek daha da kotu.
    # KENDINI TANITMA KISA BIR MESAJDIR. Olculdu (canli sohbet): 40
    # kelimelik bir TURETIM sorusu — "…operatore donustugunu ADIM ADIM
    # ACIKLAMANI ve aradaki fiziksel gecisi yorumlamani istiyorum" —
    # kendini_tanit niyetine gidip "Memnun oldum Adım!" cevabini aldi.
    # Kullanicinin gordugu ILK cevap buydu.
    #
    # Fiil listesi uzatmak (goster, anlat, acikla, hesapla...) bitmeyen
    # bir istir. Yapisal olcut daha saglam: kendini tanitan bir mesaj
    # kisadir ve icinde fizik sorusu olmaz.
    if any(i == "kendini_tanit" for _p, i in hits):
        _uzun = len(t.split()) > 10
        _fizik_sorusu = re.search(
            r"\b(ispatla\w*|turet\w*|kanitla\w*|hesapla\w*|acikla\w*|"
            r"nedir|neden|nasil|goster\w*|denklem\w*|formul\w*|"
            r"operator\w*|bagint\w*|prove|derive|explain)\b", t)
        if _uzun or _fizik_sorusu:
            hits = [(p_, i) for p_, i in hits if i != "kendini_tanit"]
            if not hits:
                return "konu", 30

    if any(i in ("turev", "integral", "limit", "seri") for _p, i in hits):
        if not re.search(r"[\d\^]|[a-zA-Z]\s*\*\*|\bx\b|\bsin\b|\bcos\b|"
                         r"\bexp\b|\blog\b|\bsqrt\b", t) or \
                len(t.split()) > 12:
            hits = [(p_, i) for p_, i in hits
                    if i not in ("turev", "integral", "limit", "seri")]
        if not hits:
            return "konu", 30
    if not hits:
        if _verili_deger_sorusu(t):
            return "formul", 65
        return "konu", 30
    # Birimli iki veya daha fazla deger verilip bir buyukluk soruluyorsa bu
    # bir hesap sorusudur, konu anlatimi degil. "yay sabiti 200 N/m, uzama
    # 0.05 m, kutle 2 kg ise ivme nedir" sorusu "... nedir" kalibina takilip
    # konu anlatimina gidiyordu.
    if hits[0][1] == "konu" and _verili_deger_sorusu(t):
        return "formul", 75
    return hits[0][1], hits[0][0]


def all_intents(text):
    t = norm(text or "")
    out = []
    for intent, prio, pats in PATTERNS:
        for p in pats:
            if re.search(p, t):
                out.append((prio, intent))
                break
    out.sort(reverse=True)
    return [i for _, i in out]


# ------------------------------------------------------------ varlik cikarimi
_NUM = r"[-+]?\d+(?:[.,]\d+)?(?:\s*[eE]\s*[-+]?\d+)?"
# Parantezli bilesik birimler de taninmali: J/(kg·K), N·m/(s^2) gibi.
# Onceden yalnizca "J" okunuyordu ve ozgul isi degeri yanlis degiskene
# atanabiliyordu.
# Ogrenci "m^3" degil "m3" yazar. Caret olmadan da us okunmali;
# olculdu: "0.05 m3" ifadesi (0.05, "m") ve (3.0, "hacim") diye iki ayri
# deger olarak okunuyordu ve hacim degeri gaz sabitine atanabiliyordu.
_UNIT = (r"[A-Za-zµΩÅ°_]+\d?(?:\s*[\^/\*·]\s*"
         r"(?:\([A-Za-zµΩÅ°_0-9\s\^/\*··]+\)|[-+]?[A-Za-zµΩÅ°_0-9]+))*")


def extract_number_unit(text):
    """'25 km/h' -> (25.0, 'km/h') listesi."""
    out = []
    for m in re.finditer(r"(%s)\s*(%s)" % (_NUM, _UNIT), text):
        raw_num = m.group(1).replace(" ", "")
        # 3,14 -> 3.14 ama 1,000 gibi durumlar icin basit kural
        if "," in raw_num and "." not in raw_num:
            raw_num = raw_num.replace(",", ".")
        try:
            val = float(raw_num)
        except ValueError:
            continue
        unit = m.group(2).strip()
        if norm(unit) in ("ve", "ile", "de", "da", "ise", "and", "or", "the",
                          "to", "in", "a", "is", "of", "cinsinden", "olarak"):
            continue
        son = m.end()
        # BIRIM ONEKI AYRI YAZILMIS OLABILIR: "10 kilo ohm", "5 mega
        # pascal". Olculdu: "10 kilo ohm direncle" ifadesinde birim
        # "kilo" okunuyor, 10 000 ohm yerine deger tamamen kayboluyordu
        # ve RC devresi sorusunda direnc yanlis (12) atanIyordu.
        if norm(unit) in ("kilo", "mega", "giga", "mili", "milli", "mikro",
                          "micro", "nano", "piko", "pico", "santi", "centi",
                          "desi", "deci", "tera"):
            devam = re.match(r"\s*([A-Za-zΩµ°/\^0-9]+)", text[m.end():])
            if devam:
                from . import units as _u
                birlesik = norm(unit) + devam.group(1)
                try:
                    if _u.to_si(1.0, birlesik)[0] is not None:
                        unit = birlesik
                        son = m.end() + devam.end()
                except Exception:
                    pass
        out.append((val, unit, m.start(), son))
    return out


def extract_conversion(text):
    """'25 km/h kac m/s' -> (25.0, 'km/h', 'm/s')."""
    t = text.strip()
    # Acik ok / anahtar kelime
    m = re.search(r"(%s)\s*(%s)\s*(?:->|=>|to|olarak|cinsinden|icinde|in)\s+(%s)"
                  % (_NUM, _UNIT, _UNIT), t, re.I)
    if m:
        num = m.group(1).replace(" ", "").replace(",", ".")
        try:
            return float(num), m.group(2).strip(), m.group(3).strip()
        except ValueError:
            pass
    # '25 km/h kac m/s eder'
    m = re.search(r"(%s)\s*(%s)\s*(?:kac|ne kadar|how many|how much)\s+(%s)"
                  % (_NUM, _UNIT, _UNIT), t, re.I)
    if m:
        num = m.group(1).replace(" ", "").replace(",", ".")
        try:
            return float(num), m.group(2).strip(), m.group(3).strip()
        except ValueError:
            pass
    # iki birimli genel durum: ilk sayi+birim, sonra baska bir birim
    nus = extract_number_unit(t)
    if len(nus) == 1:
        rest = t[nus[0][3]:]
        m2 = re.search(r"\b(%s)\b" % _UNIT, rest)
        if m2:
            cand = m2.group(1).strip()
            if norm(cand) not in ("kac", "ne", "kadar", "eder", "yapar", "olur",
                                  "how", "many", "much", "is", "in", "to"):
                return nus[0][0], nus[0][1], cand
    return None


def extract_expression(text):
    """Metinden matematiksel ifadeyi ayikla."""
    t = text
    # Komut kelimelerini temizle
    t = re.sub(r"\b(hesapla|bul|coz|goster|lutfen|nedir|kac eder|sonucu|"
               r"turevini?|turevi|integralini?|integrali|limitini?|"
               r"calculate|compute|evaluate|solve|find|show|please|what is|"
               r"the |derivative of|integral of|limit of)\b", " ", t, flags=re.I)
    t = re.sub(r"\b(gore|according to|with respect to|wrt|icin|for)\s+[a-z]\b",
               " ", t, flags=re.I)
    # Backtick veya $ icindeki ifadeyi tercih et
    m = re.search(r"`([^`]+)`", text) or re.search(r"\$([^$]+)\$", text)
    if m:
        return m.group(1).strip()
    t = t.strip(" .?!,:;")
    return t if t else None


def extract_variable(text, default="x"):
    """'x'e gore turev' -> 'x'."""
    m = re.search(r"\b([a-zA-Z])\s*(?:'ye|'ya|'e|'a|ye|ya)\s*gore\b", text)
    if m:
        return m.group(1)
    m = re.search(r"(?:with respect to|wrt|respect to)\s+([a-zA-Z])\b", text, re.I)
    if m:
        return m.group(1)
    m = re.search(r"\bd\s*/\s*d\s*([a-zA-Z])\b", text)
    if m:
        return m.group(1)
    m = re.search(r"\bd([a-zA-Z])\b", text)
    if m:
        return m.group(1)
    return default


def extract_limits(text):
    """Belirli integral sinirlarini bul: '0 dan 1 e', 'from 0 to 1'."""
    m = re.search(r"(%s)\s*(?:dan|den|'dan|'den)\s*(%s)\s*(?:a|e|ya|ye|'a|'e)"
                  % (_NUM, _NUM), text, re.I)
    if m:
        return m.group(1).replace(",", "."), m.group(2).replace(",", ".")
    m = re.search(r"from\s+(\S+)\s+to\s+(\S+)", text, re.I)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r"\[\s*(\S+)\s*,\s*(\S+)\s*\]", text)
    if m:
        return m.group(1), m.group(2)
    m = re.search(r"(%s)\s*(?:ile|-)\s*(%s)\s*(?:arasinda|araliginda|between)"
                  % (_NUM, _NUM), text, re.I)
    if m:
        return m.group(1).replace(",", "."), m.group(2).replace(",", ".")
    return None


def extract_matrix(text):
    """'[[1,2],[3,4]]' veya '1 2; 3 4' bicimindeki matrisi ayikla."""
    m = re.search(r"\[\s*\[.*?\]\s*\]", text, re.S)
    if m:
        try:
            body = m.group(0)
            rows = re.findall(r"\[([^\[\]]+)\]", body)
            return [[float(x.strip()) for x in r.split(",") if x.strip()]
                    for r in rows]
        except ValueError:
            pass
    m = re.search(r"\[([^\[\]]+;[^\[\]]+)\]", text)
    if m:
        try:
            rows = m.group(1).split(";")
            return [[float(x) for x in re.split(r"[,\s]+", r.strip()) if x]
                    for r in rows]
        except ValueError:
            pass
    return None


def extract_known_values(text):
    """'m=2 kg, v=10 m/s' bicimindeki bilinen degerleri ayikla."""
    out = {}
    for m in re.finditer(r"\b([A-Za-z][A-Za-z0-9_]{0,7})\s*=\s*(%s)\s*(%s)?"
                         % (_NUM, _UNIT), text):
        name = m.group(1)
        raw = m.group(2).replace(" ", "")
        if "," in raw and "." not in raw:
            raw = raw.replace(",", ".")
        try:
            val = float(raw)
        except ValueError:
            continue
        unit = (m.group(3) or "").strip()
        if norm(unit) in ("ve", "ile", "and", "or", "de", "da", "icin", "for"):
            unit = ""
        out[name] = (val, unit)
    return out


def adli_degerler(text):
    """Dogal dildeki 'buyukluk deger birim' uclulerini cikar.

    Kullanici "m=2 kg" yazmaz; "kutlesi 2 kg, hizi 5 m/s" yazar. Sayidan
    onceki 1-4 kelime o sayinin ETIKETIDIR. Etiketi formulun kendi degisken
    aciklamalariyla eslestirecegiz.

    Doner: [(etiket, deger, birim), ...]
    """
    out = []
    for m in re.finditer(r"(%s)\s*(%s)?" % (_NUM, _UNIT), text):
        ham = m.group(1).replace(" ", "")
        if "," in ham and "." not in ham:
            ham = ham.replace(",", ".")
        try:
            deger = float(ham)
        except ValueError:
            continue
        birim = (m.group(2) or "").strip()
        if norm(birim) in ("ve", "ile", "and", "or", "de", "da", "icin",
                           "for", "ise", "olan", "ne"):
            birim = ""
        onceki = text[:m.start()]
        # Sayidan onceki son kelimeler etiket adayidir
        kelimeler = re.findall(r"[\wÀ-ÿğüşıöçĞÜŞİÖÇ]+", onceki)[-4:]
        etiket = " ".join(kelimeler)
        out.append((etiket, deger, birim))
    return out


def _onek_uyar(a, b, en_az=3):
    """Iki kelime ayni koke mi isaret ediyor? (onek karsilastirmasi)

    Turkce ekleri kesin bicimde ayirmak zor: "kutle" kelimesinden sondaki
    'e' ek sanilip atilinca "kutlesi" ile eslesmiyordu. Onek karsilastirmasi
    hem basit hem dayanikli.
    """
    a, b = norm(a), norm(b)
    n = min(len(a), len(b))
    if n < en_az:
        return False
    return a[:n] == b[:n]


def _birim_uyar(verilen, beklenen):
    """Verilen birim degiskenin birimiyle ayni mi?

    Once duz karsilastirma; tutmazsa BOYUT karsilastirmasi yapilir.
    Olculdu: ogrenci "3 saniye" yazdiginda degiskenin birimi "s"
    oldugu icin eslesme olmuyor ve zaman degeri hic okunmuyordu."""
    t = lambda u: re.sub(r"[\s\^·*]", "", (u or "").lower()).replace("**", "")
    v, b = t(verilen), t(beklenen)
    if not v or not b:
        return False
    if v == b or v.replace("/", "") == b.replace("/", ""):
        return True
    try:
        from . import units as _U
        cv = _U.to_si(1.0, verilen)
        cb = _U.to_si(1.0, beklenen)
        if cv and cb and cv[1] and cb[1] and cv[1] == cb[1]:
            return True
    except Exception:
        pass
    return False


def formul_degerleri(f, text):
    """Formulun degiskenlerini dogal dildeki etiketlerle eslestir.

    Formul zaten her degiskenin Turkce ve Ingilizce adini ve BIRIMINI
    biliyor ("k = yay sabiti [N/m]"); metindeki "yay sabiti 200 N/m"
    ifadesini buradan tanir. Birim en guclu isarettir: "yay sabiti" hem
    F (yay kuvveti) hem k (yay sabiti) ile ortak kelime tasiyor, ama
    N/m yalnizca k'nin birimi.
    """
    ucluler = adli_degerler(text)
    if not ucluler:
        return {}

    adaylar = []
    for sym, (tr, en, birim) in f["vars"].items():
        ad_kelimeleri = [w for w in (norm(tr) + " " + norm(en)).split()
                         if len(w) > 2]
        for i, (etiket, deger, verilen_birim) in enumerate(ucluler):
            etiket_kelimeleri = [w for w in norm(etiket).split() if len(w) > 2]
            ortak = sum(1 for a in ad_kelimeleri
                        if any(_onek_uyar(a, b) for b in etiket_kelimeleri))
            puan = ortak
            if _birim_uyar(verilen_birim, birim):
                puan += 3           # birim eslesmesi belirleyicidir
            if puan > 0:
                adaylar.append((puan, sym, i, deger, verilen_birim))

    # En yuksek puanli eslesmeden basla; her degisken ve her deger bir kez
    adaylar.sort(key=lambda x: -x[0])
    bulunan, kullanilan_sym, kullanilan_deger = {}, set(), set()
    for puan, sym, i, deger, birim in adaylar:
        if sym in kullanilan_sym or i in kullanilan_deger:
            continue
        bulunan[sym] = (deger, birim)
        kullanilan_sym.add(sym)
        kullanilan_deger.add(i)
    return bulunan


# Matematiksel ifadede gecmesi normal olan adlar (fonksiyonlar, sabitler)
_MATH_ADLARI = set("""
sin cos tan cot sec csc asin acos atan atan2 sinh cosh tanh asinh acosh atanh
exp log ln lg sqrt kok karekok abs sign floor ceil ceiling round factorial
gamma binomial erf erfc besselj bessely legendre hermite laguerre conjugate
re im arg pi inf oo nan sum prod int diff limit matrix det inv
""".split())


def looks_like_expression(text):
    """Metin gercekten matematiksel bir ifade mi?

    'bana sifirdan matlab ogretebilir misin' bir cumledir; bunu MATLAB ifadesi
    sanip koda cevirmek anlamsiz cikti uretiyordu. Kural: uc harften uzun ve
    matematik adi olmayan bir kelime varsa bu bir ifade degil, cumledir.
    """
    t = (text or "").strip()
    if not t or len(t) > 140:
        return False
    for w in re.findall(r"[A-Za-zÀ-ÿğüşıöçĞÜŞİÖÇ]+", t):
        if len(w) <= 2:          # degisken adlari: x, y, v0, Ek, dt
            continue
        if w.lower() in _MATH_ADLARI:
            continue
        return False
    # En az bir sayi ya da islec bulunmali
    return bool(re.search(r"[\d+\-*/^()=]", t))


def strip_command_words(text):
    """Konu sorgusu icin gereksiz kelimeleri temizle."""
    t = text
    t = re.sub(r"\b(nedir|ne demek|acikla|aciklar misin|anlat|anlatir misin|"
               r"ozetle|ozet gec|hakkinda|konusunda|bilgi ver|ogret|"
               r"what is|whats|what are|explain|describe|tell me about|"
               r"summarize|give me|info on|information about|can you|please|"
               r"lutfen|bana|bir|the|a|an)\b", " ", t, flags=re.I)
    t = re.sub(r"[?!.]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()
