import os

logfile_path = os.path.join(os.path.dirname(__file__),"..", "..", "logs")
config_path = os.path.join(os.path.dirname(__file__),"..", "..", "config")
tmp_path = os.path.join(os.path.dirname(__file__),"..", "..", "tmp")

# startdatei, um bei einer neuen Installation die nötigen Ordner zu erstellen:

# Leere Dateien schreiben, wenn diese noch nicht da sind:
if not os.path.exists(logfile_path):
    os.makedirs(logfile_path)
if not os.path.exists(config_path):
    os.makedirs(config_path)
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)
open(os.path.join(logfile_path, "logfile_main.txt"), "a", encoding="utf-8").close()
open(os.path.join(logfile_path, "logfile_ovpn.txt"), "a", encoding="utf-8").close()
open(os.path.join(logfile_path, "logfile_crawler.txt"), "a", encoding="utf-8").close()
open(os.path.join(logfile_path, "logfile_EM.txt"), "a", encoding="utf-8").close()

