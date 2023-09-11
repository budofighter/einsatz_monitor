# Optimiert 30.03.23

import os
import pickle
import sys
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support import expected_conditions as EC

from ..einsatz_monitor_modules import database_class

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..", "..")

database = database_class.Database()

def get_cookie():
    if (database.select_aktiv_flag("vpn") != 0 and
            database.select_aktiv_flag("wachendisplay") == 1 and
            not database.select_config("user_wachendisplay") == "" and
            not database.select_config("passwort_wachendisplay") == "" and
            not database.select_config("url_wachendisplay") == ""):

        try:
            with webdriver.Chrome() as driver:
                driver.get(database.select_config("url_wachendisplay"))
                
                wait = WebDriverWait(driver, 60)

                time.sleep(1)
                wait.until(EC.presence_of_element_located((By.ID, "tfUsername")))
                username_element = driver.find_element(By.ID, "tfUsername")
                username_element.send_keys(database.select_config("user_wachendisplay"))

                wait.until(EC.presence_of_element_located((By.ID, "tfPassword")))
                password_element = driver.find_element(By.ID, "tfPassword")
                password_element.send_keys(database.select_config("passwort_wachendisplay"))

                wait.until(EC.presence_of_element_located((By.ID, "cbAnmeldungMerken")))
                driver.find_element(By.ID, "cbAnmeldungMerken").click()

                wait.until(EC.presence_of_element_located((By.ID, "btnLogin")))
                driver.find_element(By.ID, "btnLogin").click()
                time.sleep(2)

                wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Ruhedarstellung')]")))
                time.sleep(2)

                cookie_file = os.path.join(basedir, "config", "cookies_wachendisplay.pkl")

                with open(cookie_file, "wb") as f:
                    pickle.dump(driver.get_cookies(), f)


                return "erfolgreich"

        except Exception as e:
            print(f"Exception occurred: {e}")
            return "nicht erfolgreich"

    elif database.select_aktiv_flag("vpn") == 0 or database.select_aktiv_flag("wachendisplay") == 0:
        return "fehler vpn"

    else:
        return "fehler config"


if __name__ == "__main__":
    print(get_cookie())
