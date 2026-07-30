@echo off
title Asistente Portable - Lanzador Web Dashboard (Localhost:8000)
cls
echo ========================================================
echo     INICIANDO ASISTENTE PORTABLE - WEB DASHBOARD
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

echo [INFO] Abriendo Web Dashboard en http://127.0.0.1:8000 ...
start http://127.0.0.1:8000
python -m core.web_app
pause
