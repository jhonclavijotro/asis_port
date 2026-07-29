@echo off
title Asistente Portable - Lanzador Windows
cls
echo ========================================================
echo        INICIANDO ASISTENTE PERSONAL PORTABLE
echo ========================================================
echo.

if not exist ".venv" (
    echo [INFO] Creando entorno virtual portable Python...
    python -m venv .venv
    call .\.venv\Scripts\activate.bat
    echo [INFO] Instalando dependencias necesarias...
    pip install -r requirements.txt
) else (
    call .\.venv\Scripts\activate.bat
)

python launcher.py
pause
