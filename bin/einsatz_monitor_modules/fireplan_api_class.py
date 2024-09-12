import requests
import json

class FirePlanAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key
        self.token = None

    def register(self, standort):
        url = f"{self.base_url}/api/Register/{standort}"
        headers = {
            "accept": "application/json",
            "API-Key": self.api_key
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            response_json = response.json()
            self.token = response_json.get('utoken')  # Verwenden Sie den richtigen Schlüssel, um das Token zu extrahieren
        else:
            print(f"Registrierung fehlgeschlagen. Statuscode: {response.status_code}")
            print(response.text)

    def send_alarm(self, ric, subRIC, einsatznrlst, objektname, strasse, hausnummer, ortsteil, ort, koordinaten, einsatzstichwort, zusatzinfo):
        if not self.token:
            print("Kein Token verfügbar. Bitte zuerst registrieren.")
            return

        url = f"{self.base_url}/api/Alarmierung"
        headers = {
            "accept": "application/json",
            "API-Token": self.token,
            "Content-Type": "application/json"
        }
        daten = {
            "ric": str(ric),
            "subRIC": str(subRIC),
            "einsatznrlst": str(einsatznrlst),
            "strasse": str(strasse),
            "hausnummer": str(hausnummer),
            "ort": str(ort),
            "ortsteil": str(ortsteil),
            "objektname": str(objektname),
            "koordinaten": str(koordinaten),
            "einsatzstichwort": str(einsatzstichwort),
            "zusatzinfo": str(zusatzinfo)
        }

        response = requests.post(url, headers=headers, data=json.dumps(daten))
        if response.status_code == 200:
            print(f"Alarm wurde erfolgreich hinzugefügt! Statuscode: {response.status_code}, Antwort: {response.text}")
        else:
            print(f"Alarm senden fehlgeschlagen. Statuscode: {response.status_code}")
            print(response.text)

    def send_fms(self, fzKennung, status, statusTime):
        if not self.token:
            print("Kein Token verfügbar. Bitte zuerst registrieren.")
            return

        url = f"{self.base_url}/api/FMSStatus"
        headers = {
            "accept": "application/json",
            "API-Token": self.token,
            "Content-Type": "application/json"
        }
        daten = {
            "fzKennung": str(fzKennung),
            "status": str(status),
            "statusTime": str(statusTime)
        }
        response = requests.post(url, headers=headers, json=daten)
        if response.status_code == 200:
            print("FMS wurde erfolgreich hinzugefügt!")
        else:
            print(f"FMS senden fehlgeschlagen. Statuscode: {response.status_code}")
            print(response.text)

# Beispielanwendung:
api = FirePlanAPI("https://data.fireplan.de", "byeJoNAy7lPX1GPBt8JN5WBaIqxLZclzQprif13Qh9L")
api.register("Wallbach")


api.send_alarm(
    ric="20345",
    subRIC="A",
    einsatznrlst="1005",
    strasse="Steinenstrasse",
    hausnummer="77",
    ort="Bad Saeckingen",
    ortsteil="Wallbach",
    objektname="Daheim",
    koordinaten="",
    einsatzstichwort="Brand 2",
    zusatzinfo="unklare Rauchentwicklung"
)

