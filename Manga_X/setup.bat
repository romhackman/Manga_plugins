@echo off
echo Creation de l'environnement virtuel...
python -m venv .venv

echo Activation de l'environnement...
call .venv\Scripts\activate

echo Mise a jour de pip...
python -m pip install --upgrade pip

echo Installation des dependances...
pip install -r requirements.txt

echo.
echo ✅ Installation terminee !
pause
