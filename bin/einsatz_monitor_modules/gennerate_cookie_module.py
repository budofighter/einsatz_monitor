import pickle, os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from ..einsatz_monitor_modules import database_class

database = database_class.Database()


def get_cookie():

    # 1. Check ob das VPN läuft und das Wachensidplay erreichbar ist.
    if database.select_error("vpn") == 0 and database.select_error("wachendisplay") == 0:

        # 2. Check ob die Zugangsdaten schon eingetragen sind:
        if not database.select_config("user_wachendisplay") == "" and not database.select_config("passwort_wachendisplay") == "" and not database.select_config("url_wachendisplay") == "":
            try:
                driver = webdriver.Chrome()
                driver.get(database.select_config("url_wachendisplay"))
                wait = WebDriverWait(driver, 60)
                wait.until(expected_conditions.visibility_of_element_located((By.ID, "tfUsername")))
                driver.find_element_by_id("tfUsername").send_keys(database.select_config("user_wachendisplay"))
                driver.find_element_by_id("tfPassword").send_keys(database.select_config("passwort_wachendisplay"))

                driver.find_element_by_id("cbAnmeldungMerken").click()
                driver.find_element_by_id("btnLogin").click()

                wait.until(expected_conditions.visibility_of_element_located((By.ID, "gwt-uid-22")))

                # cookie Datei erstellen:
                pickle.dump(driver.get_cookies(), open(os.path.join(os.path.dirname(__file__), "..", "..", "config", "cookies_wachendisplay.pkl"), "wb"))
                return "erfolgreich"
            except:
                return "nicht erfolgreich"
            finally:
                driver.close()

        else:
            return "fehler config"

    else:
        return "fehler vpn"


get_cookie()