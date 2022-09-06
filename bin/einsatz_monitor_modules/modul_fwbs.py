import urllib.parse
import requests


def modul_fwbs(stichwort, sachverhalt, strasse, ort):
    try:
        value = urllib.parse.quote_plus(stichwort + "," + strasse + "," + ort + "," + sachverhalt)
        url = "https://XXX.XXXXX.XX:8087/set/0_userdata.0.Alarm/?value="
        headers = {'Content-Type': 'text/html'}
        api_url = url + value
        payload = {}
        response = requests.get(api_url, headers=headers, data=payload, verify=False)

        if "200" in str(response):
            return "alles ok"
        else:
            return response
    except:
        return "Fehler beim Modul FWBS"
