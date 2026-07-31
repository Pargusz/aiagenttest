#!/bin/bash
# Arayuzu duzenledikten sonra bunu calistirin.
#
# Yaptigi is:
#   1. app.js / style.css baglantilarindaki surum damgasini yeniler.
#      Bu olmadan tarayici eski dosyayi onbellekten sunar ve yaptiginiz
#      degisiklik hicbir kullaniciya ulasmaz (olculdu).
#   2. web/ icindekileri depo kokune kopyalar (Pages kokten yayinliyor).
#   3. GitHub'a gonderir.
cd "$(dirname "$0")" || exit 1

DAMGA=$(date -u +%Y%m%d%H%M)
python3 - "$DAMGA" <<'PY'
import io, re, sys
damga = sys.argv[1]
p = "web/index.html"
s = io.open(p, encoding="utf-8").read()
s = re.sub(r'app\.js\?v=[^"\']*', 'app.js?v=' + damga, s)
s = re.sub(r'style\.css\?v=[^"\']*', 'style.css?v=' + damga, s)
io.open(p, "w", encoding="utf-8").write(s)
print("surum damgasi:", damga)
PY

cp web/index.html web/app.js web/style.css . || exit 1
git add -A && git commit -m "arayuz guncellendi ($DAMGA)" && git push
