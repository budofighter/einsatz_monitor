import time, subprocess
from datetime import datetime as dt
from einsatz_monitor_modules import get_email
from einsatz_monitor_modules.api_class import *
from einsatz_monitor_modules.einsatz_auswertung_class import *
from einsatz_monitor_modules.database_class import *
from einsatz_monitor_modules.modul_fwbs import *


# Zugangsdaten:
database = database_class.Database()
tmp_path = os.path.join(os.path.dirname(__file__), ".." , "tmp")


# Logginginformationen
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__),"..", "logs", "logfile_EM.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

while database.select_aktiv_flag("auswertung") == 1:
    if database.select_config("testmode") == "False":
        testmode = False
    else:
        testmode = True

    # E-Mails abholen
    pdfs = get_email.pull_mails()

    # PDFs zu Text verarbeiten und anschließend löschen
    if not pdfs:
        pass
    else:
        for pdf in pdfs:
            inp = os.path.join(tmp_path, pdf)
            try:
                subprocess.run([database.select_config("path_to_pdftotext.exe"), "-enc", "UTF-8", "-simple", inp])
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
                           einsatz.geo_bw, einsatz.geo_lw, einsatz.alarm_ric]
            logger.info("Neuer Alarm: " + alarm_number + "\n\tStichwort: " + einsatz.stichwort + "\n\tMeldebild: " +
                        einsatz.meldebild + "\n\tObjekt: " + einsatz.objekt + "\n\tSondersignal: " + einsatz.sondersignal +
                        "\n\tAdresse: " + einsatz.strasse + ", " + einsatz.ort + " - " + einsatz.ortsteil + " [" +
                        einsatz.plz + "]" + "\n\tGeo (Breite ; Länge): " + einsatz.geo_bw + " ; " + einsatz.geo_lw +
                        "\n\tBemerkung 1: " + einsatz.bemerkung1 + "\n\tBemerkung 2: " + einsatz.bemerkung2 + "\n\tRICs: " +
                        einsatz.alarm_ric)

            # Textdatei wieder löschen:
            try:
                os.remove(tmp_path + "/" + alarm_number + ".txt")
                logger.debug("Textdatei entfernt")
            except:
                logger.error("Textdatei konnte nicht entfernt werden.")

    # Alarmierung:
            token_list = []
            if testmode:
                token_list.append(database.select_config("token_test"))
                logger.info("Testmodus ist an, daher keine Alarmierung zur Live-Api")
            else:
                # Abteilung 1 wird immer alarmiert
                token_list.append(database.select_config("token_abt1"))
                # Listen der jeweiligen Abteilungen erstellen, wenn diese nicht leer sind:
                if not database.select_config("fahrzeuge_abt2") == "":
                    list_abt_2 = database.select_config("fahrzeuge_abt2").split(";")
                    for fahrzeug in list_abt_2:
                        funkrufname = fahrzeug.strip().upper().replace(" ", "-").replace(".", "-")
                        if funkrufname in einsatz.alarm_ric:
                            logger.info("Abteilung 2 wird mit alarmiert.")
                            token_list.append(database.select_config("token_abt2"))

                if not database.select_config("fahrzeuge_abt3") == "":
                    list_abt_3 = database.select_config("fahrzeuge_abt3").split(";")
                    for fahrzeug in list_abt_3:
                        funkrufname = fahrzeug.strip().upper().replace(" ", "-").replace(".", "-")
                        if funkrufname in einsatz.alarm_ric:
                            logger.info("Abteilung 3 wird mit alarmiert.")
                            token_list.append(database.select_config("token_abt3"))

                if not database.select_config("fahrzeuge_abt4") == "":
                    list_abt_4 = database.select_config("fahrzeuge_abt4").split(";")
                    for fahrzeug in list_abt_4:
                        funkrufname = fahrzeug.strip().upper().replace(" ", "-").replace(".", "-")
                        if funkrufname in einsatz.alarm_ric:
                            logger.info("Abteilung 4 wird mit alarmiert.")
                            token_list.append(database.select_config("token_abt4"))

                if not database.select_config("fahrzeuge_abt5") == "":
                    list_abt_5 = database.select_config("fahrzeuge_abt5").split(";")
                    for fahrzeug in list_abt_5:
                        funkrufname = fahrzeug.strip().upper().replace(" ", "-").replace(".", "-")
                        if funkrufname in einsatz.alarm_ric:
                            logger.info("Abteilung 5 wird mit alarmiert.")
                            token_list.append(database.select_config("token_abt5"))

                if not database.select_config("fahrzeuge_abt6") == "":
                    list_abt_6 = database.select_config("fahrzeuge_abt6").split(";")
                    for fahrzeug in list_abt_6:
                        funkrufname = fahrzeug.strip().upper().replace(" ", "-").replace(".", "-")
                        if funkrufname in einsatz.alarm_ric:
                            logger.info("Abteilung 6 wird mit alarmiert.")
                            token_list.append(database.select_config("token_abt6"))

            # Prüfen ob GEO oder nicht
            if einsatz.geo_lw == "":
                for token in token_list:
                    if not token == "":
                        api = PublicAPI(token)
                        r = api.post_operation(
                            start=dt.now().strftime('%Y-%m-%dT%H:%M:%S'),
                            keyword=einsatz.stichwort,
                            status="new",
                            alarmenabled=True,
                            address=f"{einsatz.strasse}, {einsatz.ort} - {einsatz.ortsteil}",
                            facts=einsatz.meldebild,
                            number=alarm_number,
                            properties=[
                                {"key": "Objekt", "value": einsatz.objekt},
                                {"key": "Sondersignal", "value": einsatz.sondersignal},
                                {"key": "Bemerkung", "value": einsatz.bemerkung1},
                                {"key": "Bemerkung", "value": einsatz.bemerkung2}
                            ],
                            ric=einsatz.alarm_ric,
                        )
            else:
                for token in token_list:
                    if not token == "":
                        api = PublicAPI(token)
                        r = api.post_operation(
                            start=dt.now().strftime('%Y-%m-%dT%H:%M:%S'),
                            keyword=einsatz.stichwort,
                            status="new",
                            alarmenabled=True,
                            address=f"{einsatz.strasse}, {einsatz.ort} - {einsatz.ortsteil}",
                            position={"Latitude": einsatz.geo_bw, "Longitude": einsatz.geo_lw},
                            facts=einsatz.meldebild,
                            number=alarm_number,
                            properties=[
                                    {"key": "Objekt", "value": einsatz.objekt},
                                    {"key": "Sondersignal", "value": einsatz.sondersignal},
                                    {"key": "Bemerkung", "value": einsatz.bemerkung1},
                                    {"key": "Bemerkung", "value": einsatz.bemerkung2}
                                ],
                            ric=einsatz.alarm_ric,
                        )

            # Modul FWBS übergabe
            if testmode:
                # logger.info("Testmode, daher keine Übergabe an Modul FWBS")

                print(einsatz.stichwort + einsatz.meldebild + einsatz.strasse + einsatz.ort)
                x= modul_fwbs(einsatz.stichwort, einsatz.meldebild, einsatz.strasse, einsatz.ort)
                logger.info("Übergabe an Modul FWBS:  " + x)
            else:
                x = modul_fwbs(einsatz.stichwort, einsatz.meldebild, einsatz.strasse, einsatz.ort)
                logger.info("Übergabe an Modul FWBS:  " + x)

        logger.info("\n####################################################\n\n")

    time.sleep(2)