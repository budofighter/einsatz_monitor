import logging
import requests
import cerberus
import sys
import os
import pytz
from datetime import datetime, timezone


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
file_handler = logging.FileHandler(os.path.join(basedir,"..", "logs", "logfile_fireplan.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

class Fireplan:

    BASE_URL = "https://data.fireplan.de/api/"

    def __init__(self, secret, division):
        self._secret = secret
        self._division = division
        logger.debug(f"Initialisierung mit Registration ID {secret} und Abteilung {division}")
        self.headers = {
            "accept": "application/json",
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
            self.headers['API-Token'] = response_json.get('utoken')  # Verwenden Sie den richtigen Schlüssel, um das Token zu extrahieren
        else:
            logger.error(f"Registrierung fehlgeschlagen. Statuscode: {r.status_code}")
            logger.error(r.text)

    def alarm(self, data):
        url = "https://data.fireplan.de/api/Alarmierung"
        headers = self.headers

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            logger.info(data)
            logger.info("Alarm erfolgreich gesendet.")
        else:
            logger.error(f"Fehler beim Senden des Alarms. Statuscode: {response.status_code}")
            logger.error(response.text)

    def send_fms_status(self, kennung, status):
        url = "https://data.fireplan.de/api/FMSStatus"
        headers = self.headers

        # Aktuelle Zeit in UTC im ISO 8601-Format setzen
        cet = pytz.timezone('Europe/Berlin')
        status_time = datetime.now(cet).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        payload = {
            "fzkennung": kennung,
            "status": status,
            "statusTime": status_time
        }
        logger.debug (headers)
        logger.debug (payload)
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            logger.info(f"FMS Status erfolgreich gesendet: {payload}")
        else:
            logger.info(f"Fehler beim Senden des FMS Status. Statuscode: {response.status_code}")
            logger.info(response.text)