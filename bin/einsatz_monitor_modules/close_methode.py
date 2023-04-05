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


def update_database_flag_and_pid(flag_name):
    try:
        database.update_aktiv_flag(flag_name, "0")
        logger.debug(f"Programmende: Aktivdatei der {flag_name} erfolgreich gelöscht.")
        database.update_pid(flag_name, "0")
    except Exception as e:
        logger.exception(f"Programmende: Aktivdatei der {flag_name} konnte nicht gelöscht werden! ({str(e)})")


def close_all():
    # 1. OpenVPN beenden
    terminate_processes('openvpn.exe')

    # 2. statusauswertung beenden
    update_database_flag_and_pid("crawler")

    # 3. Einsatzauswertung beenden
    update_database_flag_and_pid("auswertung")

    # 4. Alle Buttons auf rot setzen
    for button in ["vpn", "wachendisplay", "statusauswertung", "alarm_server", "testmodus", "alarm_auswertung"]:
        database.update_error(button, "1")

    # 5. chromedriver.exe beenden:
    terminate_processes('chromedriver.exe')

    # 6. alle Subprozesse endgültig killen und pids zurücksetzen:
    pids = database.select_all_pids()
    for pid in pids:
        if pid != 0:
            if psutil.pid_exists(pid):
                try:
                    os.kill(pid, signal.SIGTERM)
                    logger.debug(f"Programmende: PID {pid} erfolgreich beendet.")
                except Exception as e:
                    logger.exception(f"Programmende: PID{pid} konnte nicht beendet werden! ({str(e)})")
        else:
            logger.debug("PID ist 0, daher kein Close möglich")

    # 7. Datenbankverbindung beenden
    #with database:
    #    database.close_connection()

    logger.info("alles wurde geschlossen")
