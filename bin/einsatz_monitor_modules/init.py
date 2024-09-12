# Optimiert 30.03.23
import os
import sys

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..", "..")

def create_directory_and_empty_file(directory, file_name):
    if not os.path.exists(directory):
        os.makedirs(directory)
    open(os.path.join(directory, file_name), "a", encoding="utf-8").close()

logfile_path = os.path.join(basedir, "logs")
config_path = os.path.join(basedir, "config")
tmp_path = os.path.join(basedir, "tmp")

# Erstellen von Verzeichnissen, falls noch nicht vorhanden
if not os.path.exists(config_path):
    os.makedirs(config_path)
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)

# Leere Dateien schreiben, wenn diese noch nicht da sind:
create_directory_and_empty_file(logfile_path, "logfile_main.txt")
create_directory_and_empty_file(logfile_path, "logfile_ovpn.txt")
create_directory_and_empty_file(logfile_path, "logfile_crawler.txt")
create_directory_and_empty_file(logfile_path, "logfile_EM.txt")
create_directory_and_empty_file(logfile_path, "logfile_fireplan.txt")
