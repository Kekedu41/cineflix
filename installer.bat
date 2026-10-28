@echo off
title Cineflix - Installation automatique et Lancement
cd /d "%~dp0"

echo [1/3] Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\Python311\python.exe" (
        set "PYTHON_CMD=C:\Program Files\Python311\python.exe"
        set "PIP_CMD=C:\Program Files\Python311\Scripts\pip.exe"
        goto :dependencies
    )

    echo Python n'est pas detecte sur ce PC.
    echo Telechargement automatique de Python en arriere-plan (veuillez patienter)...
    
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python_installer.exe'"
    
    echo Installation de Python (avec ajout au PATH automatique)...
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_launcher=1
    del python_installer.exe
    
    echo Python a ete installe avec succes !
    set "PYTHON_CMD=C:\Program Files\Python311\python.exe"
    set "PIP_CMD=C:\Program Files\Python311\Scripts\pip.exe"
) else (
    set "PYTHON_CMD=python"
    set "PIP_CMD=pip"
)

:dependencies
echo.
echo [2/3] Installation des dependances de Cineflix...
if exist requirements.txt (
    "%PIP_CMD%" install -r requirements.txt --quiet
)

echo.
echo [3/3] Lancement de Cineflix...
echo Ouvre ton navigateur sur http://127.0.0.1:8000
"%PYTHON_CMD%" main.py

pause
