# Optimiert 30.03.23
import os
import re
import time
import logging
import pickle

from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    StaleElementReferenceException,
    InvalidCookieDomainException,
    WebDriverException,
)
from einsatz_monitor_modules import api_class, database_class
from selenium.webdriver.support.expected_conditions import visibility_of_element_located



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
        if element is None:  # Füge diese Zeile hinzu, um auf None zu überprüfen
            raise TimeoutException()  # Füge diese Zeile hinzu, um einen Timeout-Fehler auszulösen
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
    try:
        # Element des Bereichs der Feuerwehr finden und das Webelement übernehmen: Button Übersicht finden,
        # klick durchführen, warten bis das Element da ist und dann ausführen
        driver.find_element(By.XPATH, "//*[contains(text(),'Ruhedarstellung')]").click()
        content_element = WebDriverWait(driver, 60).until(
            visibility_of_element_located((By.ID, database.select_config("wachendisplay_content_id")))
        )
        output_wachendisplay_webelement = driver.find_element(By.ID, database.select_config("wachendisplay_content_id"))

        # Webelement in String auszulesen und alle Zeilenumbrüche entfernen
        try:
            output_wachendisplay_string = output_wachendisplay_webelement.text.replace("\n", " ")
        except StaleElementReferenceException:
            logger.error("StaleElementReferenceException: kein Zeilenumbruch in der Zwischenablage gefunden")
        except:
            logger.exception("Sonstiger Crawler error.")
            wait_before_retrying(10)


        # ################ 2. Daten parsen und in Dictionary eintragen
        fahrzeuge_list = re.findall(database.select_config("funkrufname") + " [1-4]/[0-9][0-9]/?[0-9]? [1-6]",
                                    output_wachendisplay_string)

        # NeuesDirectory aus der Liste erstellen nach der Syntax: zB FL-BS 1/10 : STATUS
        fahrzeug_dictionary_new_status = {}
        for fahrzeug in fahrzeuge_list:
            fahrzeug_split = fahrzeug.split(" ")
            fahrzeug_dictionary_new_status[fahrzeug_split[0] + " " + fahrzeug_split[1]] = fahrzeug_split[2]

        # wenn ein neuer Status gefunden wurde:
        for fahrzeug, status_new in fahrzeug_dictionary_new_status.items():

            status_old = database.select_status(fahrzeug)

            if not status_new == str(status_old):
                radioid = fahrzeug.replace(" ", "").replace("-", "").replace("/", "")
                # Übergabe an API:
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
        logger.exception("Sonstiger Cralwer error.")
        wait_before_retrying(10)

    WebDriverWait(driver, 60).until(
        element_updated((By.ID, database.select_config("wachendisplay_content_id")), output_wachendisplay_string))
    return True  # Gibt True zurück, wenn der Crawl erfolgreich war, oder False, wenn nicht


def main():
    database = database_class.Database()
    # ################ 1. Seite aufrufen und Daten extrahieren
    # Optionen für den Chrome Browser:
    chrome_options = Options()
    if database.select_config("headless_browser") == "Ja":
        chrome_options.add_argument("--headless")  # Kein GUI Popup

    try:
        driver = webdriver.Chrome(options=chrome_options)

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
        if 'chromedriver' in str(e):
            logger.error("Es wurde kein Chromedriver gefunden. Bitte stellen Sie sicher, dass der Chromedriver in Ihrem Systempfad enthalten ist.")
        else:
            logger.error("Ein unbekannter Fehler ist aufgetreten:", e)

    finally:
        # Schließen Sie die Datenbankverbindung und den Chromedriver in einer try-Anweisung
        try:
            database.close_connection()
        except Exception as e:
            logger.error(f"Datenbankverbindung konnte nicht geschlossen werden: {e}")

        try:
            driver.quit()
        except Exception as e:
            logger.error(f"Chrome-driver konnte nicht abschließend geschlossen werden: {e}")
        else:
            logger.info("Chrome-driver erfolgreich geschlossen")

if __name__ == "__main__":
    main()