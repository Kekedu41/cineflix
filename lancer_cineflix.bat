@echo off
title Cineflix - Lancement Serveur et Tunnel Permanent
color 0a

echo ========================================================
echo          DEMARRAGE DE CINEFLIX EN COURS...
echo ========================================================

cd /d "C:\cineflix"

echo [1/2] Lancement du serveur Python...
start /min cmd /k "python main.py"

timeout /t 3 >nul

echo [2/2] Lancement du tunnel Ngrok permanent...
ngrok http 8000 --url https://unsure-stir-regular.ngrok-free.dev --pooling-enabled

pause