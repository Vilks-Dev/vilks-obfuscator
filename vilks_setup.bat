@echo off
title Vilks Obfuscator - Setup
cls

echo =============================================================
echo       Vilks Obfuscator - Console d'Installation
echo =============================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python n'est pas installe ou n'est pas dans le PATH.
    echo         Veuillez installer Python 3.11+ avant de continuer.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detecte avec succes.

if not exist "venv\" (
    echo [INFO] Creation de l'environnement virtuel (venv)...
    python -m venv venv
) else (
    echo [OK] Environnement virtuel deja existant.
)

echo [INFO] Activation du venv et installation des dependances...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r backend/requirements.txt pytest httpx >nul 2>&1

if not exist ".env" (
    echo [INFO] Creation du fichier de configuration .env...
    copy .env.example .env >nul
    powershell -Command "(Get-Content .env) -replace 'APP_ENV=production', 'APP_ENV=development' | Set-Content .env"
)

echo.
echo =============================================================
echo  [OK] Installation terminee avec succes.
echo  Vous pouvez maintenant executer vilks_start.bat pour lancer.
echo =============================================================
echo.
pause
exit
