# Optimiert 31.03.23
import json
import logging
import os
import requests

from . import database_class

database = database_class.Database()


class PublicAPI(object):
    def __init__(self, token):
        self._headers = None
        self._headers = {
            "authorization": "bearer {0}".format(token),
            "accept": "application/json",
            "content-type": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self._headers)

        # Logger:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "..",
                                                        "logs", "logfile_EM.txt"), encoding="utf-8")
        file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
        self.logger.addHandler(file_handler)

    def get_operation(self):
        """Receive operation data."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/operation"
        r = self.session.get(self._url)
        if r.status_code != 200:
            self.logger.error(
                "API-Call 'get operation' Fehler: {0} {1}".format(
                    r.status_code, r.text
                )
            )
        else:
            self.logger.info("API-Call 'get operation' erfolgreich")
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
                self.logger.warning(
                    "Invalid argument passed to post_operation: {0}={1}".format(k, v)
                )
        print(json.dumps(data))
        r = self.session.post(self._url, data=json.dumps(data))
        if r.status_code != 204:
            self.logger.error(
                "API Fehler bei 'post operation': {0} {1}".format(
                    r.status_code, r.text
                )
            )
        else:
            self.logger.info("API call 'Einsatz alarmieren' erfolgreich ausgeführt")
        return r

    def get_geocoding(self, address):
        """Receive geo coordinates for a given address."""
        self._url = "https://connectapi.feuersoftware.com/interfaces/public/geocoding"
        params = {"address": address}
        r = self.session.get(self._url, params=params)
        if r.status_code != 200:
            self.logger.error(
                "API call Fehler 'get geocoding': {0} {1}".format(
                    r.status_code, r.text
                )
            )
        else:
            self.logger.info("API call 'get geocoding' erfolgreich.")
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
