# Optimiert 30.03.23
import subprocess
import sys
import time
from datetime import datetime as dt
from einsatz_monitor_modules import mail, Xpdf
from einsatz_monitor_modules.api_class import *
from einsatz_monitor_modules.einsatz_auswertung_class import *
from einsatz_monitor_modules.database_class import *




python_path = os.path.join(basedir, "EinsatzHandler_venv", "Scripts", "python.exe")

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..")

# Zugangsdaten:
database = database_class.Database()
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
Xpdf.XpdfHandler()

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
        pdfs = mail.pull_mails()
        if pdfs:
            if isinstance(pdfs, str):
                pdfs = [pdfs]

        # PDFs zu Text verarbeiten und anschließend löschen


        if not pdfs:
            pass
        else:
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
                einsatz = Einsatz(alarm_number + ".txt")
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

                for token in token_list:
                    if not token:
                        continue
                    api = PublicAPI(token)
                    r = api.post_operation(**post_operation_args)

                # Modul FWBS übergabe
                if testmode:
                    logger.info("Testmode, daher keine Übergabe an Externes Script")
                else:
                    exScript_path = database.select_config("ex_script")
                    print(exScript_path)
                    if exScript_path != "":
                        args = [python_path] + [exScript_path] + [einsatz.stichwort, einsatz.meldebild, einsatz.strasse, einsatz.ort, einsatz.alarm_ric]
                        subprocess.Popen(args)
                        logger.info("\nExternes Script wurde aufgerufen.\n####################################################\n\n")
        time.sleep(1)
   
except Exception as e:
    logger.exception(f"Ein Fehler im einsatz_process.py ist aufgetreten, wodurch die exception ausgelöst wurde: {e}")
    database.update_aktiv_flag("auswertung", "error")
