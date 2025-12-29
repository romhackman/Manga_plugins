@echo off
cd /d "%~dp0"

REM Vérification du python du venv
if not exist ".venv\Scripts\python.exe" exit /b

REM Vérification du script python
if not exist "HH_image.py" exit /b

REM Lancement avec le python du venv (PAS besoin d'activation)
".venv\Scripts\python.exe" "HH_image.py"
exit /b
