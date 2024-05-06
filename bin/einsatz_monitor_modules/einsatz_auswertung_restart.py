# Datei ist dafür gedacht, dass die Einsatzauswertung jede Minute neu gestartet wird, um bei Fehlern wieder bei 0 zu starten.

import os
import sys
import logging
import subprocess
import time
import shutil
import database_class

# Einstellungen laden:
database = database_class.Database()

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..", "..")

python_path = os.path.join(basedir, "EinsatzHandler_venv", "Scripts", "python.exe")
einsatz_process_datei = os.path.join(basedir, "bin", "einsatz_process.py")

# Logger:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(basedir, "logs", "logfile_EM.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

def neustarten():
    try:
        global prozess
        if prozess is not None and prozess.poll() is None:
            prozess.terminate()
            prozess.wait()

        # Setze den Status auf "off"
        database.update_aktiv_flag("auswertung", "off")  

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

        time.sleep(1)

        prozess = subprocess.Popen([python_path, einsatz_process_datei])
        database.update_aktiv_flag("auswertung", "running")
        logger.debug("Prozess erfolgreich neu gestartet.")

    except Exception as e:
        logger.error(f"Fehler beim Neustart des Prozesses: {e}")

def ueberwachungsprozess():
    while True:
        time.sleep(60) 
        if database.select_aktiv_flag("auswertung") != "processing": 
            if database.select_aktiv_flag("auswertung") == "running":
                neustarten()
        

if __name__ == "__main__":
    prozess = None
    # Starten des Überwachungsprozesses
    ueberwachungsprozess()
