# Optimiert 30.03.23
import os
import sys
import subprocess
import logging
import einsatz_monitor_modules.database_class

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..")

database = einsatz_monitor_modules.database_class.Database()

path_to_openvpn = os.path.join(basedir, "resources", "openvpn", "openvpn.exe")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(basedir, "logs", "logfile_ovpn.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

wachendisplay_config = os.path.join(basedir, "config", database.select_config("openvpn_config"))
wachendisplay_pass = os.path.join(basedir, "config", "pass_ovpn_wachendisplay.txt")

# OpenVPN Prozess wird als Subprozess gestartet
def start_openvpn_process():
    try:
        ovpn_process = subprocess.Popen([path_to_openvpn, "--config", wachendisplay_config, "--auth-user-pass", wachendisplay_pass])
        logger.info("OVPN erfolgreich gestartet")
    except Exception as e:
        logger.exception("OVPN konnte nicht gestartet werden: %s", e)

if __name__ == "__main__":
    start_openvpn_process()