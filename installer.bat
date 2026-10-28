@echo off
title Cinéflix - Lancement & Mises a jour
cd /d "%~dp0"

echo [1/3] Verification des mises a jour du site...
git pull
echo.

echo [2/3] Verification des dependances Python...
pip install -r requirements.txt --quiet
echo.

echo [3/3] Lancement de Cineflix...
echo Ouvre ton navigateur sur http://127.0.0.1:8000
python main.py

pause