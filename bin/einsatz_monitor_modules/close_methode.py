import signal, os, logging, psutil
from ..einsatz_monitor_modules import database_class

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "..", "logs", "logfile_main.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

database = database_class.Database()

def close_all():
    # 1. OpenVPN beenden
    pid = list(item.pid for item in psutil.process_iter() if item.name() == 'openvpn.exe')
    if not pid:
        logger.debug("Programmende: kein OVPN Prozess gefunden, um diesen zu beenden")
    else:
        try:
            for i in pid:
                psutil.Process(i).terminate()
                logger.debug("Programmende: OVPN Prozess erfolgreich beendet")
        except:
            logger.exception("Programmende: OVPN Prozess konnte nicht beendet werden!")

    # 2. statusauswertung beenden
    try:
        database.update_aktiv_flag("crawler", "0")
        logger.debug("Programmende: Aktivdatei der Auswertung erfolgreich gelöscht.")
        database.update_pid("crawler", "0")
    except:
        logger.exception("Programmende: Aktivdatei der Auswertung konnte nicht gelöscht werden!")

    # 3. Einsatzauswertung beenden
    try:
        database.update_aktiv_flag("auswertung", "0")
        logger.debug("Programmende: Aktivdatei der Einsatzauswertung erfolgreich gelöscht.")
        database.update_pid("auswertung", "0")
    except:
        logger.exception("Programmende: Aktivdatei der Auswertung konnte nicht gelöscht werden!")


    # 4. Alle Buttons auf rot setzen

    database.update_error("vpn", "1")
    database.update_error("wachendisplay", "1")
    database.update_error("statusauswertung", "1")
    database.update_error("alarm_server", "1")
    database.update_error("testmodus", "1")
    database.update_error("alarm_auswertung", "1")

    # 5. chromedriver.exe beenden:
    pid = list(item.pid for item in psutil.process_iter() if item.name() == 'chromedriver.exe')
    if not pid:
        logger.debug("Programmende: kein chromedriver Prozess gefunden, um diesen zu beenden")
    else:
        try:
            for i in pid:
                psutil.Process(i).terminate()
                logger.debug("Programmende: chromedriver Prozess erfolgreich beendet")
        except:
            logger.exception("Programmende: Chromedriver Prozess konnte nicht beendet werden!")

    # 6. alle Subprozesse endgültig killen und pids zurücksetzen:

    pids = database.select_all_pids()

    for pid in pids:
        if not pid == 0:
            if psutil.pid_exists(pid):
                try:
                    os.kill(pid, signal.SIGTERM)
                    logger.debug("Programmende: PID " + str(pid) + " erfolgreich beendet.")
                except:
                    logger.exception("Programmende: PID " + str(pid) + " konnte nicht beendet werden.")
        else:
            logger.debug("PID ist 0, daher kein Close möglich")

    # 7. Datenbankverbindung beenden
    database.close_connection()

    logger.info("alles wurde geschlossen")

