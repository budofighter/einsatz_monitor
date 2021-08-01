# API Übergabe der Fahrzeuge an die Connect API
import json, os, logging, requests
from . import database_class

database = database_class.Database()

# Logger:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "..", "logs", "logfile_EM.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)


class PublicAPI(object):
    def __init__(self, token):
        self._headers = None
        self._headers = {
            "authorization": "bearer {0}".format(token),
            "accept": "application/json",
            "content-type": "application/json",
        }

    def get_operation(self):
        """Receive operation data."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/operation"
        r = requests.get(self._url, headers=self._headers)
        if r.status_code != 200:
            logger.error(
                "API-Call 'get operation' Fehler: {0} {1}".format(
                    r.status_code, r.text
                )
            )
        else:
            logger.info("API-Call 'get operation' erfolgreich")
        return r

    def post_operation(self, start, keyword, update_strategy="none", **kwargs):
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/operation?updateStrategy={0}".format(
            update_strategy
        )
        valid_args = (
            "end",
            "status",
            "alarmenabled",
            "address",
            "position",
            "facts",
            "ric",
            "number",
            "properties",
        )
        data = {"start": start, "keyword": keyword}
        for k, v in kwargs.items():
            if k in valid_args:
                data[k] = v
            else:
                logger.warning(
                    "Invalid argument passed to post_operation: {0}={1}".format(k, v)
                )
        print(json.dumps(data))
        r = requests.post(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 204:
            logger.error(
                "API Fehler bei 'post operation': {0} {1}".format(
                    r.status_code, r.text
                )
            )
        else:
            logger.info("API call 'Einsatz alarmieren' erfolgreich ausgeführt")
        return r

    def get_geocoding(self, address):
        """Receive geo coordinates for a given address."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/geocoding"
        data = {"address": address}
        r = requests.get(self._url, data=json.dumps(data), headers=self._headers)
        if r.status_code != 200:
            logger.error(
                "API call Fehler 'get geocoding': {0} {1}".format(
                    r.status_code, r.text
                )
            )
        else:
            logger.info("API call 'get geocoding' erfolgreich.")
        return r


# Methode zum Fahrzeugstatus posten:
def post_fahrzeug_status(radioid, status):

    headers = {
        "authorization": "bearer {0}".format(database.select_config("connect_api_fahrzeuge")),
        "accept": "application/json",
        "content-type": "application/json",
    }

    url = "https://connectapi.feuersoftware.com/interfaces/public/vehicle/{0}/status".format(radioid)
    data = {"status": status}

    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r
