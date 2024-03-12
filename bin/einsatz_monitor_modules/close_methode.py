# Optimiert 31.03.23
import os
import sys
import logging
import psutil
from ..einsatz_monitor_modules import database_class

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..", "..")

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(basedir, "logs", "logfile_main.txt"), encoding="utf-8")
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

def terminate_processes(process_name):
    pids = [item.pid for item in psutil.process_iter() if item.name() == process_name]
    if not pids:
        logger.debug(f"Programmende: kein {process_name} Prozess gefunden, um diesen zu beenden")
    else:
        for pid in pids:
            try:
                psutil.Process(pid).terminate()
                logger.debug(f"Programmende: {process_name} Prozess erfolgreich beendet")
            except psutil.NoSuchProcess:
                logger.exception(f"Programmende: {process_name} Prozess konnte nicht beendet werden!")


def update_database_flag(flag_name):
    try:
        database.update_aktiv_flag(flag_name, "off")
        logger.debug(f"Programmende: Aktivdatei der {flag_name} erfolgreich gelöscht.")
    except Exception as e:
        logger.exception(f"Programmende: Aktivdatei der {flag_name} konnte nicht gelöscht werden! ({str(e)})")


def close_all():

    # 1. Alle Buttons auf rot setzen und das schließen der Anwendungen starten
    for button in ["monitoring","vpn", "crawler","auswertung", "wachendisplay",  "alarm_server", "testmode"]:
        update_database_flag(button)

    # 2. OpenVPN beenden
    terminate_processes('openvpn.exe')

    # 3. alle Kindprozesse des Hauptprozesses beenden
    terminate_all_child_processes(os.getpid())

    # 4. sicherstellen, dass VPN 
    with open(os.path.join(basedir,"logs", "logfile_ovpn.txt"), "a") as f:
        f.write("###########\n\n\n")

    logger.info("alles wurde geschlossen")
