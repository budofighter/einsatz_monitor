import urllib.parse

import urllib.parse
import requests


# Vorlage für API Übergabe

def modul_fwbs(stichwort, sachverhalt, strasse, ort, aao_ric):

    try:
        value = urllib.parse.quote_plus(stichwort + "," + strasse + "," + ort + "," + sachverhalt)
        url = "https://syn1.siebold.cloud:8087/set/0_userdata.0.Alarm/?value="
        headers = {'Content-Type': 'text/html'}
        api_url = url + value
        payload = {}
        response = requests.get(api_url, headers=headers, data=payload, verify=False)

        if "200" in str(response):
            return "Wallbacher AAO gefunden - ausgelöst!"
        else:
            return response
    except:
        return "Fehler beim Modul FWBS"
