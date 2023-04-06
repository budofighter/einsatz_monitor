import os
import re
import subprocess
import winreg
import logging
from packaging import version
from webdriver_manager.chrome import ChromeDriverManager

# Logger initialisieren
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__),"..", "..", "logs", "logfile_crawler.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

CHROMEDRIVER_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "chromedriver.exe")

def get_chrome_version():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon") as key:
            version_string, _ = winreg.QueryValueEx(key, "version")
            version_match = re.search(r"\d+\.", version_string)
            if version_match:
                return version_match.group(0).strip(".")
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Chrome-Version: {str(e)}")
    return None

def get_local_chromedriver_version(chromedriver_path):
    result = subprocess.run([chromedriver_path, "--version"], capture_output=True, text=True)
    output = result.stdout.strip()
    local_version = output.split(" ")[1]
    return local_version

def update_chromedriver(chromedriver_path):
    try:
        updated_driver = ChromeDriverManager().install()
        os.replace(updated_driver, chromedriver_path)
        logger.info("Chromedriver wurde erfolgreich aktualisiert.")
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Chromedrivers: {str(e)}")

def is_chromedriver_current(chromedriver_path=CHROMEDRIVER_PATH):
    if not os.path.exists(chromedriver_path):
        update_chromedriver(chromedriver_path)
        return False

    local_version = get_local_chromedriver_version(chromedriver_path)
    chrome_main_version = get_chrome_version()

    if chrome_main_version is not None and local_version.startswith(chrome_main_version + "."):
        return True
    elif version.parse(local_version) < version.parse(chrome_main_version + ".0"):
        update_chromedriver(chromedriver_path)
        return False
    else:
        return False

if is_chromedriver_current():
    logger.info("Die Hauptversion von chromedriver.exe stimmt mit der Hauptversion von Chrome überein.")
else:
    logger.info("Chromedriver wurde aktualisiert.")