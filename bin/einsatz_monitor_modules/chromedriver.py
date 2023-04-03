import os
import re
import subprocess
import winreg
from packaging import version
from webdriver_manager.chrome import ChromeDriverManager

def get_chrome_version():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        value = winreg.QueryValueEx(key, "version")
        version_string = value[0]
        version_match = re.search(r"\d+\.", version_string)
        if version_match:
            return version_match.group(0).strip(".")
    except Exception as e:
        print(f"Fehler beim Abrufen der Chrome-Version: {str(e)}")
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
        print("Chromedriver wurde erfolgreich aktualisiert.")
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Chromedrivers: {str(e)}")

def is_chromedriver_current(chromedriver_path=None):
    if chromedriver_path is None:
        chromedriver_path = os.path.join(os.path.dirname(__file__), "..", "..", "resources", "chromedriver.exe")

    # Check if chromedriver.exe exists at the given path
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
    print("Die Hauptversion von chromedriver.exe stimmt mit der Hauptversion von Chrome überein.")
else:
    print("Chromedriver wurde aktualisiert.")
