import os
import sys
import requests
import shutil
import logging
from zipfile import ZipFile

from . import database_class

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..", "..")

database = database_class.Database()

XPDF_VERSION = '4.04'
XPDF_PATH = os.path.join(basedir,"resources", "pdftotext.exe")

# Logger initialisieren
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class XpdfHandler:

    def __init__(self):
        self.check_and_download_xpdf()

    def check_and_download_xpdf(self):
        if not self.xpdf_installed():
            self.download_xpdf()
        else:
            logger.info("pdftotext.exe ist vorhanden")

    def xpdf_installed(self):
        return os.path.exists(XPDF_PATH)

    def download_xpdf(self):
        try:
            url = f'https://dl.xpdfreader.com/xpdf-tools-win-{XPDF_VERSION}.zip'
            zip_filename = os.path.join(basedir, "resources", 'xpdf_tools.zip')
            self.download_file(url, zip_filename)

            # Entpacken
            with ZipFile(zip_filename, 'r') as zip_ref:
                extracted_folder = os.path.join(basedir, "resources", f'xpdf-tools-win-{XPDF_VERSION}')
                zip_ref.extractall(extracted_folder)

            # Datei verschieben
            for root, _, files in os.walk(extracted_folder):
                for file in files:
                    if file.endswith("pdftotext.exe"):
                        shutil.move(os.path.join(root, file), XPDF_PATH)
                        logger.debug(f"Datei wurde verschoben")
                        break

            # Löschen des extrahierten Ordners und der ZIP-Datei
            shutil.rmtree(extracted_folder)
            os.remove(zip_filename)
            logger.debug(f"Dateien wurden gelöscht")

        except Exception as e:
            logger.error(f"Fehler beim Download: {str(e)}")

    def download_file(self, url, file_name):
        with requests.Session() as session:
            response = session.get(url)
            with open(file_name, 'wb') as f:
                f.write(response.content)


if __name__ == "__main__":
    with logging.FileHandler(os.path.join(basedir, "logs", "logfile_crawler.txt"),
                             encoding="utf-8") as file_handler:
        file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
        logger.addHandler(file_handler)
        xpdf_handler = XpdfHandler()
