#Wenn die main() Methode ausgeführt wird, passiert Folgendes:
#Die Funktion monitor_crawler() wird aufgerufen.
#In der Funktion monitor_crawler() wird ein neuer Prozess mit der Funktion run_crawler() erstellt und gestartet.
#In der Funktion run_crawler():
#a. Eine Instanz der Database Klasse wird erstellt.
#b. Die Chrome-Optionen werden basierend auf den Datenbankeinstellungen konfiguriert.
#c. Der Chromedriver wird überprüft und aktualisiert, falls nötig.
#d. Ein neuer Chrome-Browser wird gestartet.
#e. Die Wachendisplay-Webseite wird geladen.
#f. Die Cookies werden geladen und im Browser gesetzt.
#g. Die Webseite wird erneut geladen.
#h. Es wird auf das Vorhandensein des "Ruhedarstellung"-Buttons gewartet.
#Während das Aktiv-Flag "crawler" in der Datenbank auf 1 gesetzt ist, wird die Funktion crawl_wachendisplay() kontinuierlich aufgerufen.
#a. In der Funktion crawl_wachendisplay():
#i. Der Button "Ruhedarstellung" wird geklickt.
#ii. Es wird auf das Laden des Wachendisplay-Textelements gewartet.
#iii. Der Text des Wachendisplays wird extrahiert und verarbeitet.
#iv. Fahrzeugstatus werden extrahiert und geänderte Status werden an die ConnectAPI übergeben.
#v. Es wird auf die Aktualisierung des Wachendisplay-Textelements gewartet.
#Zwischen den Aufrufen der Funktion crawl_wachendisplay() wird überprüft, ob der Crawler reaktiv ist (mittels der Funktion is_crawler_responsive()). Falls nicht, wird der Prozess beendet.
#Wenn der Crawler-Prozess unerwartet beendet wird, startet die monitor_crawler() Funktion nach einer 60-Sekunden-Pause einen neuen Prozess. Dieser Schritt wird wiederholt, bis der Crawler-Prozess erfolgreich beendet wird (mit Exitcode 0).
#Im Allgemeinen durchläuft der Code kontinuierlich das Wachendisplay und überwacht Fahrzeugstatusänderungen. Bei Änderungen werden diese an die ConnectAPI übergeben. Der Crawler wird auch regelmäßig auf seine Reaktivität überprüft und bei Bedarf neu gestartet.

import multiprocessing
import os
import re
import time
import logging
import pickle
import sys

from contextlib import contextmanager

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeDriverService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.expected_conditions import visibility_of_element_located
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    InvalidCookieDomainException,
    WebDriverException,
)
from einsatz_monitor_modules import api_class, database_class, chromedriver


chromedriver_path = os.path.join(os.path.dirname(__file__), "..", "resources", "chromedriver.exe")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "logs", "logfile_crawler.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)


def wait_before_retrying(wait_time):
    logger.info(f"Warte {wait_time} Sekunden vor dem erneuten Versuch...")
    time.sleep(wait_time)


def element_updated(locator, current_text):
    def expected_condition(driver):
        try:
            element = driver.find_element(*locator)
            return element.text != current_text
        except StaleElementReferenceException:
            return False
    return expected_condition


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


def crawl_wachendisplay(driver, database):
    while True:
        output_wachendisplay_string = None

        try:
            # Klick auf den Button "Ruhedarstellung"
            driver.find_element(By.XPATH, "//*[contains(text(),'Ruhedarstellung')]").click()

            # Warten, bis das Element mit dem Wachendisplay-Text geladen ist
            content_element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.ID, database.select_config("wachendisplay_content_id")))
            )

            # Speichern des Textes im Webelement
            output_wachendisplay_webelement = driver.find_element(By.ID, database.select_config("wachendisplay_content_id"))

            try:
                # Extrahieren des Textes, entfernen der Zeilenumbrüche und speichern in einer Variablen
                output_wachendisplay_string = output_wachendisplay_webelement.text.replace("\n", " ")
            except StaleElementReferenceException:
                logger.error("StaleElementReferenceException: kein Zeilenumbruch in der Zwischenablage gefunden")
            except:
                logger.exception("Sonstiger Crawler error.")
                wait_before_retrying(10)

                # Extrahieren der Fahrzeug-IDs und deren Status aus dem Text
                fahrzeuge_list = re.findall(database.select_config("funkrufname") + " [1-4]/[0-9][0-9]/?[0-9]? [1-6]",
                                            output_wachendisplay_string)

                fahrzeug_dictionary_new_status = {}
                for fahrzeug in fahrzeuge_list:
                    fahrzeug_split = fahrzeug.split(" ")
                    fahrzeug_dictionary_new_status[fahrzeug_split[0] + " " + fahrzeug_split[1]] = fahrzeug_split[2]

                # Überprüfen, ob sich der Status eines Fahrzeugs geändert hat
                for fahrzeug, status_new in fahrzeug_dictionary_new_status.items():

                    status_old = database.select_status(fahrzeug)

                    if not status_new == str(status_old):
                        radioid = fahrzeug.replace(" ", "").replace("-", "").replace("/", "")
                        try:
                            api_class.post_fahrzeug_status(radioid, status_new)
                            database.update_status(fahrzeug, status_new)
                            logger.info(
                                "neue Statusänderung erfolgreich übergeben - {0}  Status : {1}".format(radioid,
                                                                                                       status_new))
                        except:
                            logger.exception("Übergabe an ConnectAPI war nicht möglich.")

        except NoSuchElementException:
            logger.error("Crawler Error, Element konnte nicht geklickt werden.")
            wait_before_retrying(10)

        except TimeoutException:
            logger.error("Crawler Error, Timeout beim Laden des Wachendisplays.")
            wait_before_retrying(10)

        except StaleElementReferenceException:
            logger.error("StaleElementReferenceException: Feld mit Text Ruhedarstellung kann nicht gefunden werden")

        except:
            logger.exception("Sonstiger Crawler error.")
            wait_before_retrying(10)

            # Überprüfen, ob das Element mit dem Wachendisplay-Text aktualisiert wurde
        WebDriverWait(driver, 60).until(
            element_updated((By.ID, database.select_config("wachendisplay_content_id")),
                            output_wachendisplay_string))

        # Überprüfen, ob der Crawler reaktiv ist
        while database.select_aktiv_flag("crawler") == 1:
            if not is_crawler_responsive(driver):
                logger.error("Crawler ist nicht mehr reaktiv. Beende den Prozess...")
                sys.exit(1)

            # Wenn der Crawler reaktiv ist, Wachendisplay erneut durchsuchen
            if not crawl_wachendisplay(driver, database):
                time.sleep(10)

    return True

def is_crawler_responsive(driver, timeout=60):
    try:
        driver.execute_async_script("window.setTimeout(arguments[arguments.length - 1], 0);")
        return True
    except (TimeoutException, WebDriverException):
        return False

def monitor_crawler():
    while True:
        process = multiprocessing.Process(target=run_crawler)
        process.start()
        process.join()

        if process.exitcode == 0:
            break
        else:
            logger.warning(
                f"Crawler-Prozess wurde unerwartet beendet (Exitcode: {process.exitcode}). Neustart in 60 Sekunden...")
            time.sleep(60)

def run_crawler():
    database = database_class.Database()
    # ################ 1. Seite aufrufen und Daten extrahieren
    # Optionen für den Chrome Browser:
    chrome_options = Options()
    if database.select_config("headless_browser") == "Ja":
        chrome_options.add_argument("--headless")  # Kein GUI Popup

    try:
        # überprüfen, ob der Chromedriver da und aktuell ist:
        chromedriver.is_chromedriver_current()

        service = ChromeDriverService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)


        # erst die Webseite aufrufen:
        try:
            driver.get(database.select_config("url_wachendisplay"))
        except WebDriverException:
            logger.exception("Webseite konnte nicht geladen werden!")

        # Cookies laden und einbinden:
        cookie_file_path = os.path.join(os.path.dirname(__file__), "..", "config", "cookies_wachendisplay.pkl")
        load_cookies(driver, cookie_file_path)

        # Seite neu aufrufen:
        try:
            driver.get(database.select_config("url_wachendisplay"))
        except WebDriverException:
            logger.error("Webseite konnte nicht geladen werden!")

        # Warten, bis die Webseite komplett geladen ist: (bis der Button "Ruhedarstellung" angezeigt wird)

        with wait_for_element(driver, 60, By.XPATH, "//*[contains(text(),'Ruhedarstellung')]") as element:
            if element:
                logger.info("Wachendisplay erfolgreich geladen")



        while database.select_aktiv_flag("crawler") == 1:
            if not crawl_wachendisplay(driver, database):
                time.sleep(10)  # Warten Sie 10 Sekunden, bevor Sie erneut versuchen

    except WebDriverException as e:
        logger.error("Ein unbekannter Fehler ist aufgetreten:", e)

    finally:
        try:
            database.close_connection()

        except Exception as e:
            logger.error(f"Datenbankverbindung konnte nicht geschlossen werden: {e}")

        if driver is not None:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Chrome-driver konnte nicht abschließend geschlossen werden: {e}")
            else:
                logger.info("Chrome-driver erfolgreich geschlossen")

def main():
    monitor_crawler()

if __name__ == "__main__":
    main()
