@echo off
title Vilks Obfuscator - Setup
cls

echo =============================================================
echo       Vilks Obfuscator - Console d'Installation
echo =============================================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python n'est pas installe.
    pause
    exit /b
)

echo [OK] Python detecte.

if exist venv (
    echo [OK] Environnement virtuel deja existant.
) else (
    echo [INFO] Creation du venv...
    python -m venv venv
)

call venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r backend\requirements.txt pytest httpx

if not exist .env (
    copy .env.example .env
)

echo.
echo Installation terminee.
pause
