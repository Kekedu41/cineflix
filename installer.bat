@echo off
title Cineflix - Installation et Lancement
cd /d "%~dp0"

echo [1/3] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 goto install_python
goto dependencies

:install_python
echo Python n'est pas detecte. Telechargement en cours (veuillez patienter)...
powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python_installer.exe'"
if errorlevel 1 (
    echo Erreur lors du telechargement. Verifie la connexion Internet.
    goto error
)

echo Installation automatique de Python (sans droit admin requis)...
python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1
del python_installer.exe

:: Ajout temporaire au PATH pour la session en cours
set "PATH=%LocalAppData%\Programs\Python\Python311\;%LocalAppData%\Programs\Python\Python311\Scripts\;%PATH%"

:dependencies
echo.
echo [2/3] Installation des dependances de Cineflix...
if exist requirements.txt (
    pip install -r requirements.txt
)

echo.
echo [3/3] Lancement de Cineflix...
echo Ouvre ton navigateur sur http://127.0.0.1:8000
python main.py
goto end

:error
echo.
echo Une erreur s'est produite.

:end
echo.
pause
