#!/bin/bash
echo "========================================================"
echo "       INICIANDO ASISTENTE PERSONAL PORTABLE            "
echo "========================================================"
echo ""

if [ ! -d ".venv" ]; then
    echo "[INFO] Creando entorno virtual portable Python..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "[INFO] Instalando dependencias necesarias..."
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

python3 launcher.py
