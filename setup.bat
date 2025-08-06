@echo off
REM Script de setup pour DietTracker sur Windows

echo =========================================
echo 🚀 SETUP DIETTRACKER - WINDOWS
echo =========================================

REM Vérifier Python
echo 📌 Vérification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python n'est pas installé ou pas dans le PATH
    echo Téléchargez Python depuis https://www.python.org
    echo Assurez-vous de cocher "Add Python to PATH" lors de l'installation
    pause
    exit /b 1
)
python --version

REM Créer environnement virtuel
echo 📌 Création de l'environnement virtuel...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Erreur lors de la création de l'environnement virtuel
    pause
    exit /b 1
)

REM Activer environnement virtuel
echo 📌 Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Installer les dépendances
echo 📌 Installation des dépendances Python...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo =========================================
echo ✅ SETUP TERMINÉ AVEC SUCCÈS!
echo =========================================
echo.
echo Prochaines étapes:
echo 1. Activer l'environnement: venv\Scripts\activate.bat
echo 2. Initialiser la DB: python scripts\init_data.py
echo 3. Lancer le serveur: cd src\backend && python main.py
echo.
pause