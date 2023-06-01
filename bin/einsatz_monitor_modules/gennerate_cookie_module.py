# Optimiert 30.03.23

import os
import pickle

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located

from ..einsatz_monitor_modules import database_class

database = database_class.Database()


def get_cookie():
    if (database.select_aktiv_flag("vpn") == 1 and
            database.select_aktiv_flag("wachendisplay") == 1 and
            not database.select_config("user_wachendisplay") == "" and
            not database.select_config("passwort_wachendisplay") == "" and
            not database.select_config("url_wachendisplay") == ""):

        try:
            with webdriver.Chrome() as driver:
                driver.get(database.select_config("url_wachendisplay"))
                wait = WebDriverWait(driver, 60)
                wait.until(visibility_of_element_located((By.ID, "tfUsername")))
                driver.find_element(By.ID, "tfUsername").send_keys(database.select_config("user_wachendisplay"))
                driver.find_element(By.ID, "tfPassword").send_keys(database.select_config("passwort_wachendisplay"))

                driver.find_element(By.ID, "cbAnmeldungMerken").click()
                driver.find_element(By.ID, "btnLogin").click()

                wait.until(visibility_of_element_located((By.ID, "gwt-uid-22")))

                cookie_file = os.path.join(os.path.dirname(__file__), "..", "..", "config", "cookies_wachendisplay.pkl")
                with open(cookie_file, "wb") as f:
                    pickle.dump(driver.get_cookies(), f)

                return "erfolgreich"

        except Exception as e:
            return "nicht erfolgreich"

    elif database.select_aktiv_flag("vpn") != 0 or database.select_aktiv_flag("wachendisplay") != 1:
        return "fehler vpn"

    else:
        return "fehler config"


if __name__ == "__main__":
    print(get_cookie())
