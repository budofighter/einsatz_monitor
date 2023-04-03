# Optimiert 30.03.23
import time
import psutil
import subprocess
import logging
import os
from einsatz_monitor_modules import database_class
from subprocess import DEVNULL

database = database_class.Database()

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "logs", "logfile_main.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)


def check_vpn_service():
    try:
        pid = [item.pid for item in psutil.process_iter() if item.name() == 'openvpn.exe']
        database.update_error("vpn", "0" if pid else "1")
    except:
        logger.error("Monitoring Error: VPN Service")


def check_website_availability():
    try:
        url = database.select_config("url_wachendisplay").split("/")
        eingabe = url[2].split(":")
        response = subprocess.call(["ping", "-n", "1", eingabe[0]], stdout=DEVNULL)
        database.update_error("wachendisplay", "0" if response == 0 else "1")
    except:
        logger.error("Monitoring Error: URL Wachendisplay")


def check_status_evaluation():
    try:
        database.update_error("statusauswertung", "0" if database.select_aktiv_flag("crawler") == 1 else "1")
    except:
        logger.error("Monitoring Error: Status Auswertung")


def check_evaluation_server():
    try:
        response = subprocess.call(["ping", "-n", "1", "28016.whserv.de"], stdout=DEVNULL)
        database.update_error("alarm_server", "0" if response == 0 else "1")
    except:
        logger.error("Monitoring Error: Auswerteserver")


def check_test_mode():
    database.update_error("testmode", "1" if database.select_config("testmode") == "True" else "0")


def check_alarm_evaluation():
    status = database.select_aktiv_flag("auswertung")
    database.update_error("alarm_auswertung", "0" if status == 1 else "2" if status == 2 else "1")


while True:
    check_vpn_service()
    check_website_availability()
    check_status_evaluation()
    check_evaluation_server()
    check_test_mode()
    check_alarm_evaluation()
    time.sleep(3)