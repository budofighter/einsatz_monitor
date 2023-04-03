# Optimiert 30.03.23
import os
import subprocess
import logging
from einsatz_monitor_modules import database_class

database = database_class.Database()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "logs", "logfile_ovpn.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

wachendisplay_config = os.path.join(os.path.dirname(__file__), "../config", database.select_config("openvpn_config"))
wachendisplay_pass = os.path.join(os.path.dirname(__file__), "../config", "pass_ovpn_wachendisplay.txt")

# OpenVPN Prozess wird als Subprozess gestartet
def start_openvpn_process():
    try:
        ovpn_process = subprocess.Popen([database.select_config("path_to_openvpn.exe"), "--config", wachendisplay_config, "--auth-user-pass", wachendisplay_pass])
        logger.info("OVPN erfolgreich gestartet")
    except Exception as e:
        logger.exception("OVPN konnte nicht gestartet werden: %s", e)

if __name__ == "__main__":
    start_openvpn_process()