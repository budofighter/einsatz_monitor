# Optimiert 30.03.23
import subprocess
import sys
import os
import logging
import time
import re
from datetime import datetime as dt
import einsatz_monitor_modules.mail 
import einsatz_monitor_modules.Xpdf
import einsatz_monitor_modules.api_class 
import einsatz_monitor_modules.einsatz_auswertung_class 
import einsatz_monitor_modules.database_class
import einsatz_monitor_modules.fireplan_api

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..")

python_path = os.path.join(basedir, "EinsatzHandler_venv", "Scripts", "python.exe")


# Zugangsdaten:
database = einsatz_monitor_modules.database_class.Database()
tmp_path = os.path.abspath(os.path.join(basedir , "tmp"))
XPDF_PATH = os.path.abspath(os.path.join(basedir, "resources", "pdftotext.exe"))
python_path = os.path.join(basedir, "EinsatzHandler_venv", "Scripts", "python.exe")

# Logginginformationen
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(basedir, "logs", "logfile_EM.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

# xpdf überprüfen:
einsatz_monitor_modules.Xpdf.XpdfHandler()

def get_token_list(einsatz, testmode):
    token_list = []
    if testmode:
        token_list.append(database.select_config("token_test"))
        logger.info("Testmodus ist an, daher keine Alarmierung zur Live-Api")
    else:
        token_list += get_tokens_for_departments(database, einsatz.alarm_ric)
    return token_list


def get_tokens_for_departments(database, alarm_ric):
    tokens = [database.select_config("token_abt1")]
    for abt in range(2, 7):
        fahrzeuge_key = f"fahrzeuge_abt{abt}"
        token_key = f"token_abt{abt}"
        fahrzeuge = database.select_config(fahrzeuge_key)
        if not fahrzeuge:
            continue
        for fahrzeug in fahrzeuge.split(";"):
            funkrufname = fahrzeug.strip().upper().replace(" ", "-").replace(".", "-")
            if funkrufname in alarm_ric:
                logger.info(f"Abteilung {abt} wird mit alarmiert.")
                tokens.append(database.select_config(token_key))
                break
    return tokens

try:
    while database.select_aktiv_flag("auswertung") == "running":

        testmode = database.select_config("testmode") != "False"

        # E-Mails abholen
        pdfs = einsatz_monitor_modules.mail.pull_mails()
        if pdfs:
            if isinstance(pdfs, str):
                pdfs = [pdfs]

        # PDFs zu Text verarbeiten und anschließend löschen


        if not pdfs:
            pass
        else:
            database.update_aktiv_flag("auswertung", "processing")
            for pdf in pdfs:
                inp = os.path.join(tmp_path, pdf)

                try:
                    #print([XPDF_PATH, "-enc", "UTF-8", "-simple", inp])
                    subprocess.run([XPDF_PATH, "-enc", "UTF-8", "-simple", inp])
                    if os.path.exists(inp):
                        os.remove(inp)
                    else:
                        logger.error("Die PDF Datei kann nicht gelöscht werden")
                    logger.debug("PDF2Text ist abgeschlossen")
                except:
                    logger.exception("error bei PDF2Text: " + tmp_path)
                alarm_number = pdf.split(".")[0]

                # Textdatei verarbeiten:
                # EinsatzObjekt erstellen:
                einsatz = einsatz_monitor_modules.einsatz_auswertung_class.Einsatz(alarm_number + ".txt")
                # Textdatei in Liste einlesen:
                einsatz_text = einsatz.get_text_to_list()
                # Parsing:
                einsatz.parse_alarm(einsatz_text)

                einsatz.parse_aao(einsatz_text)

                # Ausgabe:
                alarminhalt = [einsatz.meldebild, einsatz.stichwort, einsatz.objekt, einsatz.bemerkung1, einsatz.bemerkung2,
                            einsatz.sondersignal, einsatz.ort, einsatz.plz, einsatz.strasse, einsatz.ortsteil,
                            einsatz.geo_bw, einsatz.geo_lw, einsatz.alarm_ric, einsatz.einsatznummer]

                logger.info(
                    f"Neuer Alarm: {alarm_number}\n\tStichwort: {einsatz.stichwort}\n\tMeldebild: {einsatz.meldebild}"
                    f"\n\tObjekt: {einsatz.objekt}\n\tSondersignal: {einsatz.sondersignal}\n\tAdresse: {einsatz.strasse}, "
                    f"{einsatz.ort} - {einsatz.ortsteil} [{einsatz.plz}]\n\tGeo (Breite ; Länge): {einsatz.geo_bw} ; "
                    f"{einsatz.geo_lw}\n\tBemerkung 1: {einsatz.bemerkung1}\n\tBemerkung 2: {einsatz.bemerkung2}\n\tRICs: "
                    f"{einsatz.alarm_ric}\n\tEinsatznummer: {einsatz.einsatznummer}")
                
                # Textdatei wieder löschen:
                try:
                    os.remove(os.path.join(tmp_path, alarm_number + ".txt"))
                    logger.debug("Textdatei entfernt")
                except:
                    logger.error("Textdatei konnte nicht entfernt werden.")

        # Alarmierung:
                
                token_list = get_token_list(einsatz, testmode)

                post_operation_args = {
                    'start': dt.now().strftime('%Y-%m-%dT%H:%M:%S'), 
                    'keyword': einsatz.stichwort,
                    'status': 'new',
                    'alarmenabled': True,
                    'address': f"{einsatz.strasse}, {einsatz.ort} - {einsatz.ortsteil}",
                    'facts': einsatz.meldebild,
                    'number': einsatz.einsatznummer,
                    'properties': [
                        {'key': 'Objekt', 'value': einsatz.objekt},
                        {'key': 'Sondersignal', 'value': einsatz.sondersignal},
                        {'key': 'Bemerkung', 'value': einsatz.bemerkung1},
                        {'key': 'Bemerkung', 'value': einsatz.bemerkung2}
                    ],
                    'ric': einsatz.alarm_ric,
                }

                if einsatz.geo_lw != "":
                    post_operation_args['position'] = {'Latitude': einsatz.geo_bw, 'Longitude': einsatz.geo_lw}

                if database.select_config("auswertung_feuersoftware") == "Ja":
                    logger.info("Auswertung Feuersoftware aktiv: Alarmierung start")
                    for token in token_list:
                        if not token:
                            continue
                        api = einsatz_monitor_modules.api_class.PublicAPI(token)
                        r = api.post_operation(**post_operation_args)

                # Alarmierung an FirePlanAPI:
            
                if database.select_config("auswertung_fireplan") == "Ja":
                    logger.info("Auswertung Fireplan aktiv: Alarmierung start")

                    translated_list = []
                    ric_array = einsatz.alarm_ric.split()
                    for item in ric_array:
                        translated_value = database.translate_fireplan_setting(item)
                        translated_list.append(translated_value)
                    
                    # Straße und Hausnummer trennen:
                    match = re.match(r"(.+)\s(\d+\w*([-\/]\d+\w*)?)$", einsatz.strasse)
                    if match:
                        strasse_only = match.group(1)
                        hausnummer = match.group(2)
                    else:
                        strasse_only = "keine Straße übergeben"
                        hausnummer = "keine Nummer übergeben"
                    
                    secret = database.get_fireplan_config("api_token")
                    division = database.get_fireplan_config("division")
                    fp = einsatz_monitor_modules.fireplan_api.Fireplan(secret, division)

                    for item in translated_list:
                        fireplan_alarm_data = {
                            "ric": item,
                            "subRIC": "A",
                            "einsatznrlst": einsatz.einsatznummer if einsatz.einsatznummer else "keine Nummer übergeben",
                            "strasse": strasse_only if strasse_only else "keine Straße übergeben",
                            "hausnummer": hausnummer if hausnummer else "",  
                            "ort": einsatz.ort if einsatz.ort else "",
                            "ortsteil": einsatz.ortsteil if einsatz.ortsteil else "",
                            "objektname": einsatz.objekt if einsatz.objekt else "",
                            "koordinaten": f"{einsatz.geo_bw},{einsatz.geo_lw}" if einsatz.geo_lw else "",
                            "einsatzstichwort": einsatz.stichwort if einsatz.stichwort else "kein Stichwort übergeben",
                            "zusatzinfo": einsatz.meldebild if einsatz.meldebild else "kein Meldebild übergeben"
                        }
                        fp.alarm(data=fireplan_alarm_data)

            database.update_aktiv_flag("auswertung", "running")
        time.sleep(1)
   
except Exception as e:
    logger.exception(f"Ein Fehler im einsatz_process.py ist aufgetreten, wodurch die exception ausgelöst wurde: {e}")
    database.update_aktiv_flag("auswertung", "error")


