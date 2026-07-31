#!/bin/bash
# ParguszPhysics — cift tiklayarak baslatin.
cd "$(dirname "$0")" || exit 1

echo ""
echo "  ParguszPhysics baslatiliyor..."
echo ""

# Gerekli paketleri ilk calistirmada kur
python3 - <<'PY' 2>/dev/null
import importlib, subprocess, sys
eksik = [m for m in ("sympy", "numpy") if not importlib.util.find_spec(m)]
if eksik:
    print("  Eksik paketler kuruluyor: " + ", ".join(eksik))
    subprocess.call([sys.executable, "-m", "pip", "install", "--user", "--quiet"] + eksik)
PY

python3 run.py "$@"

echo ""
echo "  Pencereyi kapatabilirsiniz."
read -r -p "  Kapatmak icin Enter'a basin..." _
