import pickle, re, os, logging, time

from einsatz_monitor_modules import api_class, database_class
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import *

database = database_class.Database()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "logs", "logfile_crawler.txt"),
                                   encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

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
    cookies = pickle.load(open(os.path.join(os.path.dirname(__file__), "..", "config", "cookies_wachendisplay.pkl"),
                               "rb"))
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except InvalidCookieDomainException :
            logger.error("Cookie Domain konnte nicht erreicht werden - Verbindungsprobleme mit Wachendisplay")

    # Seite neu aufrufen:
    try:
        driver.get(database.select_config("url_wachendisplay"))
    except WebDriverException:
        logger.error("Webseite konnte nicht geladen werden!")

    # Warten, bis die Webseite komplett geladen ist: (bis der Button "Ruhedarstellung" angezeigt wird)

    wait = WebDriverWait(driver, 60)
    wait.until(expected_conditions.visibility_of_element_located((By.XPATH,"//*[contains(text(),'Ruhedarstellung')]")))
    logger.info("Wachendisplay erfolgreich geladen")

    while database.select_aktiv_flag("crawler") == 1:
        try:
            # Element des Bereichs der Feuerwehr finden und das Webelement übernehmen: Button Übersicht finden,
            # klick durchführen, warten bis das Element da ist und dann ausführen
            driver.find_element(By.XPATH, "//*[contains(text(),'Ruhedarstellung')]").click()
            wait.until(expected_conditions.visibility_of_element_located((By.ID, database.select_config("wachendisplay_content_id"))))
            output_wachendisplay_webelement = driver.find_element(database.select_config("wachendisplay_content_id"))

            # Webelement in String auszulesen und alle Zeilenumbrüche entfernen
            try:
                output_wachendisplay_string = output_wachendisplay_webelement.text.replace("\n", " ")
            except StaleElementReferenceException:
                logger.error("StaleElementReferenceException: kein Zeilenumbruch in der Zwischenablage gefunden")
            except:
                logger.exception("Sonstiger Crawler error.")
                time.sleep(10)
            # ################ 2. Daten parsen und in Dictionary eintragen
            fahrzeuge_list = re.findall(database.select_config("funkrufname") + " [1-4]/[0-9][0-9]/?[0-9]? [1-6]", output_wachendisplay_string)

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
                            "neue Statusänderung erfolgreich übergeben - {0}  Status : {1}".format(radioid, status_new))
                    except:
                        logger.exception("Übergabe an ConnectAPI war nicht möglich.")
        except NoSuchElementException:
            logger.error("Crawler Error, Element konnte nicht geklickt werden.")
            time.sleep(10)
        except TimeoutException:
            logger.error("Crawler Error, Timeout beim Laden des Wachendisplays.")
            time.sleep(10)

        except StaleElementReferenceException:
            logger.error("StaleElementReferenceException: Feld mit Text Ruhedarstellung kann nicht gefunden werden")
        except:
            logger.exception("Sonstiger Cralwer error.")
            time.sleep(10)

        time.sleep(1)

finally:
    # Chromesession wird wieder geschlossen
    try:
        database.close_connection()
        driver.close()
    except:
        logger.error("Chrome-driver konnte nicht abschließend geschlossen werden")
