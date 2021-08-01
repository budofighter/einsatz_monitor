#### einsatz_monitor
#### copyright by Christian Siebold

Voraussetzungen:
- Windows 10
- Python > 3.8
- Admin Rechte

# Installation:
1)  Installiere selenium, PyQt5, qtpy, requests und psutil Modul in deiner Python Umgebung:
pip install selenium, PyQt5, qtpy, requests, psutil

2) Downloade und entpacke den Scriptordner auf deinem System
    
3) Downloade chromedriver für Selenium: https://sites.google.com/chromium.org/driver/

4) Downloade pdftotext: https://www.xpdfreader.com/download.html

5) Führe den chromedriver in deine PATH Variable in Windows.:
        - "Erweiterte Systemeinstellungen"
        - "Umgeungsvarriablen"
        - Suche und bearbeite "Path in "Systemvarriablen"
        - Füge den Ordner, in welchem deine chromedriver.exe liegt, hinzu.
        - Das System muss neu gestartet werden.
   
6) Starte das Programm mit "EM_start.ps1", welches automatisch mit Admin-Rechten gestartet wird. Du kannst eine Verknüpfung erstellen, um einen Schnellzugriff auf dem Desktop zu haben.
   
7) Vor Beginn, fülle ALLE Einstellungen auf der Setting Seite aus.


# Updates:
Für ein Update, führe "updates.ps1" mit Adminrechten aus.

Dieser Skript wird die aktuelle Stable Version von GitHub downloaden und die entsprechenden Ordner ersetzen. 
Deine Einstellungen (database und config-Ordner) werden erhalten.
