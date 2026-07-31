#!/bin/bash
# ParguszPhysics — uzaktan erisim sunucusu
#
# Bu dosyaya cift tiklayin ve pencereyi ACIK BIRAKIN.
# Yaptigi is:
#   1. ParguszPhysics motorunu baslatir (veritabaniniz ve ogrendikleri
#      bu bilgisayarda kalir).
#   2. Cloudflare tuneli acar: internetten erisilebilen bir HTTPS adresi
#      verir. Modem ayari, sabit IP, port yonlendirme gerekmez.
#   3. Adresi ekrana yazar. Arkadasiniza o adresi ve anahtari verirsiniz.
#
# Pencere kapanirsa erisim de kapanir; bu kasitlidir.

cd "$(dirname "$0")" || exit 1

# ── Ayarlar ────────────────────────────────────────────────────────────
# Erisim anahtari: tunel adresi herkese aciktir, anahtar olmadan
# calistirmayin. Ilk calistirmada uretilir ve dosyada saklanir.
ANAHTAR_DOSYA="data/erisim_anahtari.txt"
mkdir -p data
if [ ! -f "$ANAHTAR_DOSYA" ]; then
  python3 -c "import secrets; print(secrets.token_urlsafe(18))" > "$ANAHTAR_DOSYA"
  chmod 600 "$ANAHTAR_DOSYA"
fi
ANAHTAR="$(cat "$ANAHTAR_DOSYA")"

# On yuzun sunuldugu adres. GitHub Pages adresiniz:
ONYUZ="https://pargusz.github.io"

PORT="${PARGUSZ_PORT:-8777}"

export PARGUSZ_HOST=127.0.0.1      # disariya yalnizca tunel uzerinden
export PARGUSZ_PORT="$PORT"
export PARGUSZ_ANAHTAR="$ANAHTAR"
export PARGUSZ_ORIGIN="$ONYUZ"

echo ""
echo "  ╔══════════════════════════════════════════════════════════╗"
echo "  ║        ParguszPhysics — uzaktan erisim sunucusu         ║"
echo "  ╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  Erisim anahtari : $ANAHTAR"
echo "  On yuz          : $ONYUZ/aiagenttest/"
echo ""

# ── cloudflared bul ────────────────────────────────────────────────────
# Once proje icindeki kopya (brew gerektirmez), sonra sistemdeki.
if [ -x "araclar/cloudflared" ]; then
  CF="./araclar/cloudflared"
elif command -v cloudflared >/dev/null 2>&1; then
  CF="cloudflared"
else
  CF=""
fi

if [ -z "$CF" ]; then
  echo "  ! cloudflared bulunamadi. Indirmek icin:"
  echo ""
  echo "      mkdir -p araclar && cd araclar && \\"
  echo "      curl -sL -o cf.tgz https://github.com/cloudflare/cloudflared/\\"
  echo "releases/latest/download/cloudflared-darwin-arm64.tgz && \\"
  echo "      tar -xzf cf.tgz && chmod +x cloudflared && rm cf.tgz"
  echo ""
  echo "  Sonra bu dosyayi yeniden calistirin."
  echo ""
  echo "  Simdilik yalnizca bu bilgisayardan erisilebilir:"
  echo "      http://127.0.0.1:$PORT"
  echo ""
  python3 run.py
  exit 0
fi

# ── Motoru baslat ──────────────────────────────────────────────────────
python3 run.py --tarayici-yok > data/sunucu.log 2>&1 &
MOTOR_PID=$!
trap 'kill $MOTOR_PID 2>/dev/null; kill $TUNEL_PID 2>/dev/null; exit 0' INT TERM

echo "  Motor baslatiliyor…"
for i in $(seq 1 40); do
  if curl -s -o /dev/null "http://127.0.0.1:$PORT/"; then break; fi
  sleep 1
done

# ── Tuneli ac ──────────────────────────────────────────────────────────
echo "  Tunel aciliyor…"
"$CF" tunnel --url "http://127.0.0.1:$PORT" \
  --no-autoupdate > data/tunel.log 2>&1 &
TUNEL_PID=$!

ADRES=""
for i in $(seq 1 45); do
  ADRES=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' data/tunel.log \
          | head -1)
  [ -n "$ADRES" ] && break
  sleep 1
done

echo ""
if [ -n "$ADRES" ]; then
  # ── Adresi yayimla ───────────────────────────────────────────────────
  # Ucretsiz tunelde adres her acilista degisir. Kullaniciyi her
  # seferinde yeni adresi elle girmeye zorlamak yerine, guncel adresi
  # depoya yazip gonderiyoruz; arayuz onu kendisi okuyor.
  #
  # DIKKAT: bu dosyaya ANAHTAR yazilmaz. Depo herkese aciktir; anahtar
  # oraya konursa erisim denetimi anlamini yitirir.
  printf '{"adres": "%s", "guncelleme": "%s"}\n' \
    "$ADRES" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > sunucu.json

  if git rev-parse --git-dir >/dev/null 2>&1; then
    git add sunucu.json >/dev/null 2>&1
    if git diff --cached --quiet sunucu.json 2>/dev/null; then
      echo "  Adres degismemis, yayin guncel."
    else
      git commit -q -m "sunucu adresi guncellendi" >/dev/null 2>&1
      if git push -q origin main >/dev/null 2>&1; then
        echo "  Guncel adres GitHub'a yayimlandi."
      else
        echo "  ! Adres yayimlanamadi (GitHub'a erisilemedi)."
        echo "    Arkadasiniz adresi elle girmek zorunda kalabilir."
      fi
    fi
  fi

  echo ""
  echo "  ────────────────────────────────────────────────────────────"
  echo "  ARKADASINIZA VERECEGINIZ TEK BAGLANTI (bir kereye mahsus)"
  echo ""
  echo "    $ONYUZ/aiagenttest/#anahtar=$ANAHTAR"
  echo ""
  echo "  Bu baglantiyi bir kez acar; anahtar tarayicisina kaydedilir."
  echo "  Bundan sonra sadece su adresi kullanmasi yeter:"
  echo ""
  echo "    $ONYUZ/aiagenttest/"
  echo ""
  echo "  Adres her acilista degisse bile arayuz guncelini kendisi bulur;"
  echo "  bir daha hicbir sey girmesi gerekmez."
  echo "  ────────────────────────────────────────────────────────────"
  echo ""
  echo "  (Su anki sunucu adresi: $ADRES)"
else
  echo "  ! Tunel adresi alinamadi. data/tunel.log dosyasina bakin."
fi
echo ""
echo "  Bu pencereyi ACIK BIRAKIN. Kapatmak icin Ctrl+C."
echo ""

wait $MOTOR_PID
