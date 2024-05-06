# Optimiert 30.03.23
import time
import sys
import subprocess
import logging
import os
import shutil
from einsatz_monitor_modules import database_class, mail
from subprocess import DEVNULL

database = database_class.Database()

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..")

python_path = os.path.join(basedir, "EinsatzHandler_venv", "Scripts", "python.exe")
einsatz_process = os.path.join(basedir, "bin", "einsatz_process.py")
crawler_process = os.path.join(basedir, "bin", "crawler_process.py")

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(basedir, "logs", "logfile_main.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

def check_website_wachendisplay():
    try:
        url = database.select_config("url_wachendisplay").split("/")
        eingabe = url[2].split(":")
        response = subprocess.call(["ping", "-n", "1", eingabe[0]], stdout=DEVNULL)
        database.update_aktiv_flag("wachendisplay", "running" if response == 0 else "off")
    except:
        logger.debug("Monitoring Error: URL Wachendisplay")


def check_server_who():
    try:
        response = subprocess.call(["ping", "-n", "1", "28016.whserv.de"], stdout=DEVNULL)
        database.update_aktiv_flag("alarm_server", "running" if response == 0 else "off")
    except:
        logger.debug("Monitoring Error: Auswerteserver")

def check_test_mode():
    database.update_aktiv_flag("testmode", "running" if database.select_config("testmode") == "True" else "off")

#def check_einsatzauswertung():
#    try:
#        status = database.select_aktiv_flag("auswertung")
#        if status == "error":
#            logger.info("Einsatzauswertung ist abgebrochen. Daher wird dieser neu gestartet")
#            mail.send_email("Einsatzhandler Monitoring", "Die Einsatzauswertung wurde neu gestartet", "cs@csiebold.de")
#            # Lösche alle Dateien im Ordner tmp
#            tmp_folder = os.path.abspath(os.path.join(basedir, "tmp"))
#            for filename in os.listdir(tmp_folder):
#                file_path = os.path.join(tmp_folder, filename)
#                try:
#                    if os.path.isfile(file_path) or os.path.islink(file_path):
#                        os.unlink(file_path)
#                    elif os.path.isdir(file_path):
#                        shutil.rmtree(file_path)
#                except Exception as e:
#                    logger.error(f"Failed to delete {file_path}. Reason: {e}")

#           # Setze den Status auf 0
#            database.update_aktiv_flag("auswertung", "off")
#            # Warte 30 Sekunden
#            time.sleep(30)
#
#            # Setze den Status zurück auf 1 und starte
#            database.update_aktiv_flag("auswertung", "running")
#            subprocess.Popen([python_path, einsatz_process])
#
#    except Exception as e:
#        logger.error(f"Error in check_einsatzauswertung: {e}")


def check_statusauswertung():
    try:
        status = database.select_aktiv_flag("crawler")
        if status == "error":
            logger.info("Statusauswertung ist abgebrochen. Daher wird dieser neu gestartet")
            mail.send_email("Einsatzhandler Monitoring", "Die Einsatzauswertung wurde neu gestartet", "cs@csiebold.de")
            # Setze den Status auf 0
            database.update_aktiv_flag("crawler", "off")
            # Warte 20 Sekunden
            time.sleep(20)
            # Setze den Status zurück auf 1 und starte
            database.update_aktiv_flag("crawler", "running")
            subprocess.Popen([python_path, crawler_process])
    except Exception as e:
        logger.error(f"Error beim Neustart in check_statusauswertung: {e}")



while True:
    # Wachendisplay:
    check_website_wachendisplay()
    # Mailserver:
    check_server_who()
    # Testmode:
    check_test_mode()
    # Statusauswertung
    check_statusauswertung()
    # Einsatzauswertung:
#    check_einsatzauswertung()
    time.sleep(3)
