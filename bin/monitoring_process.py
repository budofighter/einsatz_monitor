# Optimiert 30.03.23
import time
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

def check_website_availability():
    try:
        url = database.select_config("url_wachendisplay").split("/")
        eingabe = url[2].split(":")
        response = subprocess.call(["ping", "-n", "1", eingabe[0]], stdout=DEVNULL)
        database.update_aktiv_flag()("wachendisplay", "1" if response == 0 else "0")
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


while True:
    check_website_availability()
    check_evaluation_server()
    check_test_mode()
    time.sleep(3)