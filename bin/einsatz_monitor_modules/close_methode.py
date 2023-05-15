# Optimiert 31.03.23
import signal
import os
import logging
import psutil
from ..einsatz_monitor_modules import database_class

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "..", "logs",
                                                "logfile_main.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

database = database_class.Database()

def terminate_all_child_processes(parent_pid):
    parent = psutil.Process(parent_pid)
    for child in parent.children(recursive=True):  # für jeden Kindprozess
        try:
            child.terminate()  # versuche, den Prozess zu beenden
            child.wait()  # wartet, bis der Prozess tatsächlich beendet ist
        except psutil.NoSuchProcess:
            pass  # der Prozess ist bereits beendet


def update_database_flag(flag_name):
    try:
        database.update_aktiv_flag(flag_name, "0")
        logger.debug(f"Programmende: Aktivdatei der {flag_name} erfolgreich gelöscht.")
        #database.update_pid(flag_name, "0")
    except Exception as e:
        logger.exception(f"Programmende: Aktivdatei der {flag_name} konnte nicht gelöscht werden! ({str(e)})")


def close_all():

    # 2. statusauswertung beenden
    update_database_flag("crawler")

    # 3. Einsatzauswertung beenden
    update_database_flag("auswertung")

    # 4. Alle Buttons auf rot setzen
    for button in ["vpn", "wachendisplay", "statusauswertung", "alarm_server", "testmodus", "alarm_auswertung"]:
        database.update_error(button, "1")

    # 7. alle Kindprozesse des Hauptprozesses beenden
    terminate_all_child_processes(os.getpid())

    logger.info("alles wurde geschlossen")
