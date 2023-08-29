#### einsatz_monitor
#### copyright by Christian Siebold

Version: 0.9

Voraussetzungen:
- mind. Windows 10
- Python > 3.10
- Admin Rechte

Beid er Ausführung der entsprechenden Auswertungen wird automatisch folgende externe SOftware herunter geladen:
https://sites.google.com/chromium.org/driver/
https://www.xpdfreader.com/download.html


# Installation:
1)  Installiere selenium, PyQt6, requests, psutil und webdriver_manager Modul in deiner Python Umgebung:
pip install selenium, PyQt6, requests, psutil, webdriver_manager, packaging

   
3) Starte das Programm mit "EM_start.ps1", welches automatisch mit Admin-Rechten gestartet wird. Du kannst eine Verknüpfung erstellen, um einen Schnellzugriff auf dem Desktop zu haben.
   
4) Vor Beginn, fülle ALLE Einstellungen auf der Setting Seite aus.


# Updates:
Für ein Update, führe "updates.ps1" mit Adminrechten aus.

Dieser Skript wird die aktuelle Stable Version von GitHub downloaden und die entsprechenden Ordner ersetzen. 
Deine Einstellungen (database und config-Ordner) werden erhalten.
