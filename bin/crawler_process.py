import sys
import time
import multiprocessing
import os
import re
import logging
import pickle
import atexit
import requests
import json
from requests.structures import CaseInsensitiveDict

from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    InvalidCookieDomainException
)

import einsatz_monitor_modules.api_class
import einsatz_monitor_modules.database_class
import einsatz_monitor_modules.chromedriver
import einsatz_monitor_modules.fireplan_api

process = None
driver = None
exception_counter = 0

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..")

chromedriver_path = os.path.join(basedir, "resources", "chromedriver.exe")


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(basedir, "logs", "logfile_crawler.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

def exit_handler():
    global process
    if process is not None and isinstance(process, multiprocessing.Process) and process.is_alive():
        process.terminate()
        process.join()

    if driver is not None:
        try:
            driver.quit()
        except Exception as e:
            logger.error(f"exit_handler: Chrome-driver konnte nicht abschließend geschlossen werden: {e}")
        else:
            logger.info("exit_handler: Chrome-driver erfolgreich geschlossen")

# Main kümmert sich daurm um aus der Datenbank auszulesen, ob der Prozess laufen soll oder nicht.
def main():
    while True:
        try:
            database = einsatz_monitor_modules.database_class.Database()
            aktiv_flag = database.select_aktiv_flag("crawler")

            if aktiv_flag in ["running", "starting"]:
                # Starte den Crawler-Prozess
                process = multiprocessing.Process(target=start_website)
                process.start()
                process.join()

                # Überprüfe den Exitcode des Prozesses
                if process.exitcode == 0:
                    logger.info("main: Crawler-Prozess erfolgreich beendet.")
                elif process.exitcode == 1:
                    raise RuntimeError("Start_website Prozess mit Fehler beendet.")
            
            elif aktiv_flag == "off":
                logger.info("main: Crawler wird beendet, da Aktiv-Flag auf 'off' gesetzt wurde.")
                break  # Beende die Schleife, wenn der Aktiv-Flag auf "off" gesetzt ist
            
        except (Exception, RuntimeError) as e:
            logger.error(f"main: Ein Fehler ist aufgetreten, daher wird der Error-code in die Datenbank geschrieben und der Prozess beendet: {e}")
            database.update_aktiv_flag("crawler", "error")
            break  # Beende die Schleife bei einem Fehler oder wenn process.exitcode == 1
        finally:
            database.close_connection()
            exit_handler()

atexit.register(exit_handler)

# funktion welche für den Webseitenaufbau zuständig ist:
def start_website():
    global driver
    database = einsatz_monitor_modules.database_class.Database()

    # Initialisiere und starte den Crawler-Prozess
    try:
        chrome_options = Options()
        chrome_options.add_argument("--disable-search-engine-choice-screen") # deaktivieren der Suchauswahl zu beginn
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) # deaktiviert USB-Überwachungs Ausgaben
        if database.select_config("headless_browser") == "Ja":
            chrome_options.add_argument("--headless")  # Kein GUI Popup

        # überprüfen, ob der Chromedriver da und aktuell ist:
        einsatz_monitor_modules.chromedriver.is_chromedriver_current()

        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # erst die Webseite aufrufen:
        driver.get(database.select_config("url_wachendisplay"))

        # Cookies laden und einbinden:
        cookie_file_path = os.path.join(basedir, "config", "cookies_wachendisplay.pkl")
        load_cookies(driver, cookie_file_path)

        # Seite neu aufrufen:
        driver.get(database.select_config("url_wachendisplay"))

        # Warten, bis die Webseite komplett geladen ist: (bis der Button "Ruhedarstellung" angezeigt wird)
        try:
            with wait_for_element(driver, 120, By.XPATH, "//*[contains(text(),'Ruhedarstellung')]") as element:
                if not element:
                    raise TimeoutException("Element 'Ruhedarstellung' konnte nicht geladen werden.")
                logger.info("start_website: Wachendisplay erfolgreich geladen")
        except TimeoutException as e:
            logger.error(f"start_website: {str(e)}")
            sys.exit(1)

        if database.select_aktiv_flag("crawler") in ["running", "starting"]:
            try:
                while crawling(driver, database):
                    time.sleep(10)
            except CrawlingFailedException as e:
                logger.error(f"start_website: {str(e)}")
                sys.exit(1)

    except Exception as e:
        logger.error(f"start_website: Ein Fehler ist aufgetreten: {e}")
    finally:
        if driver is not None:
            driver.quit()
        database.close_connection()

# Funktion, welche den Inhalt durchsucht:
def crawling(driver, database):
    global exception_counter
    max_attempts = 6

    while database.select_aktiv_flag("crawler") in ["running", "starting"]:
        output_wachendisplay_string = None
        try:
            # Klick auf den Button "Ruhedarstellung"
            driver.find_element(By.XPATH, "//*[contains(text(),'Ruhedarstellung')]").click()
            # Warten, bis das Element mit dem Wachendisplay-Text geladen ist
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, database.select_config("wachendisplay_content_id")))
            )
            # Speichern des Textes im Webelement
            output_wachendisplay_string = driver.find_element(By.ID, database.select_config("wachendisplay_content_id")).text.replace("\n", " ")
            # Extrahieren der Fahrzeug-IDs und deren Status aus dem Text
            fahrzeuge_tulp = re.findall("((([1-9]/[0-9]{2}([/-][0-9])?)|EL) [1-6])", output_wachendisplay_string)
        
            fahrzeuge_list = [tupel[0] for tupel in fahrzeuge_tulp]
            
            fahrzeug_dictionary_new_status = {}
            for fahrzeug in fahrzeuge_list:
                fahrzeug_split = fahrzeug.split(" ")
                fahrzeug_dictionary_new_status[fahrzeug_split[0]] = fahrzeug_split[1]

            # Überprüfen, ob sich der Status eines Fahrzeugs geändert hat
            for fahrzeug, status_new in fahrzeug_dictionary_new_status.items():
                # Überprüfen, ob das Fahrzeug in der Datenbank existiert
                if not database.exists_fahrzeug(fahrzeug):
                    # Wenn das Fahrzeug nicht existiert, fügen Sie es zur Datenbank hinzu
                    database.add_fahrzeug(fahrzeug)
                    logger.info(f"Fahrzeug {fahrzeug} wurde zur Datenbank hinzugefügt")

                # Den alten Status aus der Datenbank abrufen
                status_old = database.select_status(fahrzeug)

                # Überprüfen, ob sich der Status geändert hat
                if not status_new == str(status_old):
                    funkrufname = database.select_config("funkrufname").replace(" ", "").replace("-", "").replace("/", "")
                    radioid = funkrufname + fahrzeug.replace(" ", "").replace("-", "").replace("/", "")
                    if database.select_config("auswertung_feuersoftware") == "Ja":
                        try:
                            r = einsatz_monitor_modules.api_class.post_fahrzeug_status(radioid, status_new)
                            database.update_status(fahrzeug, status_new)
                            logger.info(f"neue Statusänderung erfolgreich an Feuersoftware übergeben {r} - {radioid} Status: {status_new}")
                        except:
                            logger.error(f"crawling: Übergabe an ConnectAPI war nicht möglich. {r}")
                    if database.select_config("auswertung_fireplan") == "Ja":
                        try:
                            secret = database.get_fireplan_config("api_token")
                            division = database.get_fireplan_config("division")
                            fp = einsatz_monitor_modules.fireplan_api.Fireplan(secret, division)
                            opta = database.translate_fireplan_setting(radioid)
                            r = fp.send_fms_status(opta, status_new)
                            logger.info(f"neue Statusänderung erfolgreich an Fireplan übergeben {r} - {opta} Status: {status_new}")
                        except:
                              logger.error(f"crawling: Übergabe an Fireplan API war nicht möglich. {r}")
                    if database.select_config("auswertung_fwbs_api") == "Ja":
                        try:
                            # Konfiguration aus der Datenbank abrufen
                            token = database.select_config("fwbs_token")
                            user = database.select_config("fwbs_user")
                            password = database.select_config("fwbs_password")
                            address = database.select_config("fwbs_api")
                            opta = database.translate_fireplan_setting(radioid)

                            # Header für den API-Aufruf
                            headers = CaseInsensitiveDict()
                            headers["Content-Type"] = "application/json"
                            headers["X-Api-Key"] = token

                            # JSON-Daten für die Anfrage
                            data = json.dumps({
                                "opta": opta,
                                "status": status_new
                            })

                            # API-Aufruf mit Verzeichnisschutz
                            r = requests.post(address, headers=headers, data=data, auth=(user, password))

                            # Antwort prüfen
                            if r.status_code == 200:
                                logger.info(f"Neue Statusänderung erfolgreich an Fwbs_API übergeben: {r.status_code} - {opta} Status: {status_new}")
                            else:
                                logger.error(f"Fwbs_API Fehler: {r.status_code} - {r.text}")

                        except Exception as e:
                            logger.error(f"Crawling: Übergabe an Fwbs_API war nicht möglich. Fehler: {str(e)}")


            # Überprüfen, ob das Element mit dem Wachendisplay-Text aktualisiert wurde, bevor es weiter geht
            WebDriverWait(driver, 60).until(
                element_updated((By.ID, database.select_config("wachendisplay_content_id")),
                                output_wachendisplay_string))

        except (NoSuchElementException, StaleElementReferenceException, TimeoutException, Exception) as e:
            exception_counter += 1
            logger.error(f"Crawling: Exception_Counter: {exception_counter} Fehler beim Crawling: {e}")
            if exception_counter >= max_attempts:
                raise CrawlingFailedException("Maximale Anzahl von Versuchen erreicht.")
            wait_before_retrying(10)  # Wartezeit vor dem erneuten Versuch

        return True  # Verlässt die Schleife nach erfolgreichem Durchlauf

def element_updated(locator, current_text):
    def expected_condition(driver):
        try:
            element = driver.find_element(*locator)
            return element.text != current_text
        except StaleElementReferenceException:
            return False
    return expected_condition

def wait_before_retrying(wait_time):
    logger.info(f"Warte {wait_time} Sekunden vor dem erneuten Versuch...")
    time.sleep(wait_time)

@contextmanager
def wait_for_element(driver, timeout, by, value):
    wait = WebDriverWait(driver, timeout)
    try:
        element = wait.until(visibility_of_element_located((by, value)))
        if element is None:
            raise TimeoutException()
        yield element
    except TimeoutException:
        logger.error(f"Timeout beim Warten auf Element ({by}, {value}).")
        yield None

def load_cookies(driver, cookie_file_path):
    with open(cookie_file_path, "rb") as f:
        cookies = pickle.load(f)

    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except InvalidCookieDomainException:
            logger.error("Cookie Domain konnte nicht erreicht werden - Verbindungsprobleme mit Wachendisplay")

class CrawlingFailedException(Exception):
    pass


if __name__ == "__main__":
    main()