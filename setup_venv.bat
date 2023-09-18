@echo off
echo Erstelle virtuelle Umgebung...
python -m venv "%~dp0\EinsatzHandler_venv"

echo Aktiviere virtuelle Umgebung...
call "%~dp0\EinsatzHandler_venv\Scripts\activate"

echo Installiere Abhaengigkeiten...
pip install -r "%~dp0\requirements.txt"

echo Deaktiviere virtuelle Umgebung...
deactivate

echo Fertig!
