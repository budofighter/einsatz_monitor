# Optimiert 30.03.23
import time
import sys
import subprocess
import logging
import os
import shutil
from einsatz_monitor_modules import database_class
from subprocess import DEVNULL




database = database_class.Database()

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..")

python_path = os.path.join(basedir, "EinsatzHandler_venv", "Scripts", "python.exe")
einsatz_process = os.path.join(basedir, "bin", "einsatz_process.py")

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(basedir, "logs", "logfile_main.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

def check_website_availability():
    try:
        url = database.select_config("url_wachendisplay").split("/")
        eingabe = url[2].split(":")
        response = subprocess.call(["ping", "-n", "1", eingabe[0]], stdout=DEVNULL)
        database.update_aktiv_flag("wachendisplay", "1" if response == 0 else "0")
    except:
        logger.debug("Monitoring Error: URL Wachendisplay")


def check_evaluation_server():
    try:
        response = subprocess.call(["ping", "-n", "1", "28016.whserv.de"], stdout=DEVNULL)
        database.update_aktiv_flag("alarm_server", "1" if response == 0 else "0")
    except:
        logger.debug("Monitoring Error: Auswerteserver")

def check_test_mode():
    database.update_aktiv_flag("testmode", "1" if database.select_config("testmode") == "True" else "0")

def check_evaluation_status_and_reset():
    try:
        status = database.select_aktiv_flag("auswertung")
        if status == 2:
            # Lösche alle Dateien im Ordner tmp
            tmp_folder = os.path.abspath(os.path.join(basedir, "tmp"))
            for filename in os.listdir(tmp_folder):
                file_path = os.path.join(tmp_folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}. Reason: {e}")

            # Setze den Status auf 0
            database.update_aktiv_flag("auswertung", "0")

            # Warte 30 Sekunden
            time.sleep(30)

            # Setze den Status zurück auf 1 und starte
            database.update_aktiv_flag("auswertung", "1")
            subprocess.Popen([python_path, einsatz_process])

    except Exception as e:
        logger.error(f"Error in check_evaluation_status_and_reset: {e}")


while True:
    check_website_availability()
    check_evaluation_server()
    check_test_mode()
    check_evaluation_status_and_reset()
    time.sleep(3)