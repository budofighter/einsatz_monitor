import logging
import requests
import cerberus
import sys
import os
import json

# Schema Definition
ALARM_SCHEMA = {
    "ric": {"type": "string", "nullable": True},
    "subRIC": {"type": "string", "nullable": True},
    "einsatznrlst": {"type": "string", "nullable": True},
    "strasse": {"type": "string", "nullable": True},
    "hausnummer": {"type": "string", "nullable": True},
    "ort": {"type": "string", "nullable": True},
    "ortsteil": {"type": "string", "nullable": True},
    "objektname": {"type": "string", "nullable": True},
    "koordinaten": {"type": "string", "nullable": True},
    "einsatzstichwort": {"type": "string", "nullable": True},
    "zusatzinfo": {"type": "string", "nullable": True}
}

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..")

# Logginginformationen
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(basedir, "logs", "logfile_EM.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)


class Fireplan:

    BASE_URL = "https://data.fireplan.de/api/"

    def __init__(self, secret, division):
        self._secret = secret
        self._division = division
        logger.info(f"Initialisierung mit Registration ID {secret} und Abteilung {division}")
        self.headers = {
            "utoken": None,
            "content-type": "application/json",
        }
        self._get_token(secret)
        self.validator = cerberus.Validator(ALARM_SCHEMA, purge_unknown=True)

    def _get_token(self, secret):
        url = f"{self.BASE_URL}Register/{self._division}"
        headers = {
            "accept": "application/json",
            "API-Key": secret
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            response_json = r.json()
            self.headers['utoken'] = response_json.get('utoken')  # Verwenden Sie den richtigen Schlüssel, um das Token zu extrahieren
        else:
            logger.error(f"Registrierung fehlgeschlagen. Statuscode: {r.status_code}")
            logger.error(r.text)

    def alarm(self, data):
        url = f"{self.BASE_URL}Alarmierung"
        self.validator.validate(data, update=True)
        data = self.validator.document
        self.validator.validate(data)
        for error in self.validator.errors:
            logger.warning(
                f"Fehler in den Alarmdaten, '{error}' ist falsch formatiert und wird daher auf \"\" gesetzt!"
            )
            data[error] = ""
        logger.debug(data)

        headers = {
            "accept": "*/*",
            "API-Token": self.headers['utoken'],
            "Content-Type": "application/json"
        }

        # Ausgabe der kompletten Anfrage
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Data: {json.dumps(data, indent=4)}")

        r = requests.post(url, data=json.dumps(data), headers=headers)
        if r.status_code == 200:
            print(f"Alarm wurde erfolgreich hinzugefügt! Statuscode: {r.status_code}, Antwort: {r.text}")
        else:
            print(f"Alarm senden fehlgeschlagen. Statuscode: {r.status_code}")
            print(r.text)

secret = "byeJoNAy7lPX1GPBt8JN5WBaIqxLZclzQprif13Qh9L"
division = "Wallbach"

fp = Fireplan(secret, division)

alarmdata =  {
    "alarmtext": "Testalarm",
    "einsatznrlst": "1005",
    "strasse": "Steinenstraße",
    "hausnummer": "77",
    "ort": "Bad Säckingen",
    "ortsteil": "Wallbach",
    "objektname": "Daheim",
    "koordinaten": "47.57341408482928, 7.914231622858971",
    "einsatzstichwort": "Brand 2",
    "zusatzinfo": "Zusatzinfo",
    "RIC": "KDO-BAS-DAG",
    "SubRIC": "A"
}

#fp.alarm(alarmdata)
