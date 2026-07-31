#!/bin/bash
# Arayuzu duzenledikten sonra bunu calistirin: web/ icindeki dosyalari
# depo kokune kopyalar ve GitHub'a gonderir. Pages kokten yayinladigi
# icin arayuz birkac dakika icinde guncellenir.
cd "$(dirname "$0")" || exit 1
cp web/index.html web/app.js web/style.css . || exit 1
git add -A && git commit -m "arayuz guncellendi" && git push
