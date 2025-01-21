import requests
from requests.structures import CaseInsensitiveDict

url = "https://status.fwbs.de/api.php"

# HTTP Basic Auth-Daten
username = "status"
password = "fwbs"

# Header für den API-Aufruf
headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
headers["X-Api-Key"] = "w!VP&Z9blaa00LeX#4bmvtl32U5VZcy#"

# JSON-Daten für die Anfrage
data = '{"opta":"BWFW WT BAS 2LF10       ","status":4}'

# API-Aufruf mit Verzeichnisschutz
resp = requests.post(url, headers=headers, data=data, auth=(username, password))

# Ausgabe von Statuscode und Antwortinhalt
print("Status Code:", resp.status_code)
print("Response:", resp.text)
