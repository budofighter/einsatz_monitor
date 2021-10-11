import time, psutil, subprocess, logging, os
from einsatz_monitor_modules import database_class
from subprocess import DEVNULL

database = database_class.Database()


# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__),"..","logs", "logfile_main.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

while True:

    # 1. Überprüfen, ob das VPN-Service läuft
    try:
        pid = list(item.pid for item in psutil.process_iter() if item.name() == 'openvpn.exe')
        if pid:
            database.update_error("vpn", "0")
        else:
            database.update_error("vpn", "1")
    except:
        logger.error("Monitoring Error: VPN Service")

    # 2. Überprüfen ob die Webseite erreichbar ist
    try:
        url = database.select_config("url_wachendisplay").split("/")
        eingabe = url[2].split(":")
        response = subprocess.call(["ping", "-n", "1", eingabe[0]], stdout=DEVNULL)
        if response == 0:
            database.update_error("wachendisplay", "0")
        else:
            database.update_error("wachendisplay", "1")
    except:
        logger.error("Monitoring Error: URL Wachendisplay")

    # 3. Überprüfen ob die Status auswertung läuft
    try:
        if database.select_aktiv_flag("crawler") == 1:
            database.update_error("statusauswertung", "0")
        else:
            database.update_error("statusauswertung", "1")
    except:
        logger.error("Monitoring Error: Status Auswertung")

    # 4. Überprüfen ob der Auswerteserver erreichbar ist
    try:
        response = subprocess.call(["ping", "-n", "1", "28016.whserv.de"], stdout=DEVNULL)
        if response == 0:
            database.update_error("alarm_server", "0")
        else:
            database.update_error("alarm_server", "1")
    except:
        logger.error("Monitoring Error: Auswerteserver")

    # 5. Überprüfen ob der Testmodus an ist:
    if database.select_config("testmode") == "True":
        database.update_error("testmode", "1")
    else:
        database.update_error("testmode", "0")

    # 6. Überprüfen ob der Einsatz-Auswertescript läuft
    if database.select_aktiv_flag("auswertung") == 1:
        database.update_error("alarm_auswertung", "0")
    elif database.select_aktiv_flag("auswertung") == 2:
        database.update_error("alarm_auswertung", "2")
    else:
        database.update_error("alarm_auswertung", "1")


    time.sleep(3)
