import os, re, logging
from . import database_class

# Einstellungen laden:
database = database_class.Database()

# Logger:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "..", "logs", "logfile_EM.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)


class Einsatz:
    def __init__(self, dateiname):
        self.dateiname = dateiname
        self.path_to_textfile = os.path.join(os.path.dirname(__file__), "..", "..", "tmp", dateiname)
        self.rics = []
        self.clean_rics = []
        self.meldebild = ""
        self.stichwort = "Stichwort"
        self.objekt = ""
        self.bemerkung1 = ""
        self.bemerkung2 = ""
        self.sondersignal = ""
        self.ort = ""
        self.plz = ""
        self.strasse = ""
        self.ortsteil = ""
        self.geo_bw = ""
        self.geo_lw = ""
        self.alarm_ric = ""

    # Methode um die Texte in eine Liste zu packen.
    def get_text_to_list(self):
        inhalt = []
        with open(self.path_to_textfile, "r", encoding="utf-8") as textfile:
            for line in textfile:
                inhalt.append(line.strip())
        logger.debug("Text erfolgreich in Liste gepackt")
        return inhalt

    # Methode um die Inhalte zu parsen
    def parse_alarm(self, inhalt):
        for line in inhalt:
            if "Meldebild" in line:
                self.meldebild = re.sub("\s{2,}", "#", line).strip().split("#")[1]
            elif "Stichwort" in line:
                print(line)
                try:
                    self.stichwort_raw = re.sub("\s{2,}", "#", line).strip().split("#")[1]
                    if "B BMA BMA" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("B BMA BMA", "BMA")
                    elif "B Brand 1 Brand 1" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("B Brand 1 Brand 1", "Brand 1")
                    elif "B Brand 2 Brand 2" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("B Brand 2 Brand 2", "Brand 2")
                    elif "B Brand 3 Brand 3" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("B Brand 3 Brand 3", "Brand 3")
                    elif "H THL 1 THL 1" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("H THL 1 THL 1", "THL 1")
                    elif "H THL 1 THL1" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("H THL 1 THL1", "THL 1")
                    elif "H THL 2 THL 2" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("H THL 2 THL 2", "THL 2")
                    elif "H THL 3 THL 3" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("H THL 3 THL 3", "THL 3")
                    elif "H THL 6 Ölspur THL 6" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("H THL 6 Ölspur THL 6", "THL 6 Ölspur")
                    elif "H THL Person im Wasser THL Person im Wasser" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("H THL Person im Wasser THL Person im Wasser",
                                                                    "THL Person im Wasser")
                    elif "H THL Türöffnung THL Türöffnung" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("H THL Türöffnung THL Türöffnung", "THL Türöffnung")
                    elif "R RTW Notfall+FR RTW Notfall+FR" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("R RTW Notfall+FR RTW Notfall+FR", "RTW Notfall+FR")
                    elif "R RTW Notfalleinsatz RTW Notfalleinsatz" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("R RTW Notfalleinsatz RTW Notfalleinsatz",
                                                                    "RTW Notfalleinsatz")
                    elif "R RTW ohne SoSi RTW ohne SoSi" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("R RTW ohne SoSi RTW ohne SoSi", "RTW ohne SoSi")
                    elif "R RTW+NEF+FR RTW+NEF+FR" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("R RTW+NEF+FR RTW+NEF+FR", "RTW+NEF+FR")
                    elif "R RTW+NEF+FR RTW+NEF+FR" in self.stichwort_raw:
                        self.stichwort = self.stichwort_raw.replace("S Sonstiges Sonstige Einsätze",
                                                                    "Sonstige Einsätze")
                    else:
                        self.stichwort = self.stichwort_raw
                except:
                    pass

            elif "Einsatzstichwort" in line:
                try:
                    self.stichwort = line.strip().split(":")[1]
                except:
                    logger.exception("error")
            elif "Objekt" in line and not "GEO" in line:
                try:
                    self.objekt = re.sub("\s{2,}", "#", line).strip().split("#")[1]
                except:
                    pass
            elif "Bemerkung" in line and not "410" in line:
                try:
                    if self.bemerkung1 == "":
                        self.bemerkung1 = re.sub("\s{2,}", "#", line).strip().split("#")[1]
                    else:
                        self.bemerkung2 = re.sub("\s{2,}", "#", line).strip().split("#")[1]
                except:
                    pass
            elif "Mit Sondersignal" in line or "Ohne Sondersignal" in line:
                try:
                    self.sondersignal = re.sub("\s{2,}", "#", line).strip()
                except:
                    pass
            elif ("Ort" in line) and not ("Ortsteil" in line) and not ("alarmiert" in line) and not (
                    "Transportbericht" in line):
                try:
                    self.ort_raw = re.sub("\s{2,}", "#", line).strip().split("#")[1]
                    self.ort = self.ort_raw.split("[")[0].strip()
                    self.plz = self.ort_raw.split("[")[1].strip("]")
                except:
                    pass
            elif "Straße" in line:
                try:
                    self.strasse_raw = re.sub("\s{2,}", "#", line).strip().split("#")[1]
                    self.strasse = re.sub("(\s?\/\s?)", "-", self.strasse_raw)
                except:
                    pass
            elif "Ortsteil" in line:
                try:
                    self.ortsteil = re.sub("\s{2,}", "#", line).strip().split("#")[1]
                except:
                    pass
            elif "GEO" in line:
                try:
                    self.geo_raw = re.sub("\s{2,}", "#", line).strip().split("#")[1]
                    self.geo1 = self.geo_raw.split("-")[1]
                    self.geo2 = self.geo_raw.split("-")[2]
                    if float(self.geo1) > 40:
                        self.geo_bw = self.geo1
                        self.geo_lw = self.geo2
                    else:
                        self.geo_bw = self.geo2
                        self.geo_lw = self.geo1
                except:
                    pass
            # sobald die Eskalationsstufe erreicht ist, wird die Schleife abgebrochen.
            elif "Eskalationsstufe" in line:
                break

        # Wenn die E-Mail vom Unwetter Modul stammt, wird das Stichwort entsprechend gesetzt:
        if "Unwetter-Einsatzliste" in inhalt:
            self.meldebild = "Unwetter Modul ist aktiv"

        # Sonderbehandlung BMA Tunnel in GEO
        if hasattr(Einsatz, "Objekt"):
            if "Großehrstett Tunnel" in self.objekt:
                self.geo_bw = "47.560964"
                self.geo_lw = "8.030568"
            logger.info("Geoersetzung, da Sonderobjekt")

        logger.debug("Parsing für Einsatz erfolgreich abgeschlossen")

    # Methode um die AAO auszuwerten:
    def parse_aao(self, inhalt):
        for line in inhalt:
            if not database.select_config("dag_alternativ") == "":
                if re.match("((FL[.-]" + database.select_config("fw_kurz") + ")|" + database.select_config(
                        "kdo_alarm") + ").*(DAG|" + database.select_config("dag_alternativ") + ").*", line):
                    self.rics.append(line.strip().split("  ")[0])
            else:
                if re.match("((FL[.-]" + database.select_config("fw_kurz") + ")|" + database.select_config(
                        "kdo_alarm") + ").*(DAG).*", line):
                    self.rics.append(line.strip().split("  ")[0])
        for ric in self.rics:
            # Alle DAG, KLEIN, leerzeichen und Punkte durch - ersetzen.
            clean_ric = re.sub("(([ -]?DAG)|([ -]KLEIN))", "", ric).strip().upper().replace(" ", "-").replace(".", "-")
            self.clean_rics.append(clean_ric)

        self.alarm_ric = " ".join(self.clean_rics)
        logger.debug("Parsing für die AAO erfolgreich abgeschlossen")
