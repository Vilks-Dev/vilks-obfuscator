@echo off
title Vilks Obfuscator
cls

echo [1/3] Verification des dossiers...
if not exist "logs" mkdir logs

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] L'environnement virtuel 'venv' est introuvable ou mal installe.
    echo Verifie que le dossier 'venv' est bien a la racine du projet.
    pause
    exit /b 1
)

echo [2/3] Configuration du PYTHONPATH...
set PYTHONPATH="%~dp0"

echo [3/3] Lancement des serveurs en arriere-plan...

start "Vilks-Backend" "venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 > "logs\backend_debug.log" 2>&1

cd frontend
start "Vilks-Frontend" "..\venv\Scripts\python.exe" -m http.server 8080 > "..\logs\frontend_debug.log" 2>&1
cd ..

echo =============================================================
echo               Vilks Obfuscator - Demarre !
echo =============================================================
echo  - Interface Web (Frontend) : http://127.0.0.1:8080
echo  - API (Backend)            : http://127.0.0.1:8000
echo =============================================================
echo.
echo Garde cette fenetre ouverte. Appuie sur une touche pour fermer les serveurs.
pause > nul