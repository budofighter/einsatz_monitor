import os.path, sqlite3, logging
from sqlite3 import Error

path_to_database = os.path.join(os.path.dirname(__file__), "../..", "database.db")

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "..", "logs", "logfile_main.txt"),
                                   encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)


# Datenbankverbindung aufbauen:

class Database:
    def __init__(self):
        try:
            self.con = sqlite3.connect(path_to_database)
            logger.debug("Datenbankverbindung erfolgreich aufgebaut")
            self.cursor_obj = self.con.cursor()

            #Tabellenstruktur aufbauen, wenn noch keine Tabelle da ist:
            self.cursor_obj.execute(""" CREATE TABLE IF NOT EXISTS config_db (einstellung TEXT UNIQUE, wert TEXT); """)
            self.cursor_obj.execute(""" CREATE TABLE IF NOT EXISTS error_db (  prozess TEXT UNIQUE, error INTEGER); """)
            self.cursor_obj.execute(""" CREATE TABLE IF NOT EXISTS pid_db (
                                        dienst TEXT UNIQUE, pid INTEGER, aktiv_flag Integer ); """)
            self.cursor_obj.execute("""CREATE TABLE IF NOT EXISTS status_db ( fahrzeug TEXT UNIQUE, status INTEGER );
            """)

            self.cursor_obj.execute("""INSERT or IGNORE INTO config_db(einstellung, wert) VALUES ( 
            "connect_api_fahrzeuge", ""),("url_wachendisplay", ""),("wachendisplay_content_id", ""),("funkrufname", 
            ""),("user_wachendisplay", ""),("passwort_wachendisplay", ""),("ovpn_user", ""),("ovpn_passwort", ""), 
            ("path_to_openvpn.exe", ""),("openvpn_config", ""),("autostart", ""), ("testmode", "False"), 
            ("dag_alternativ", ""), ("fw_kurz",""), ("kdo_alarm",""), ("email_username", "") , ("email_password", 
            ""), ("email_server",""), ("token_test", ""), ("token_abt1", ""), ("token_abt2", ""), ("token_abt3", ""), 
            ("token_abt4", ""), ("fahrzeuge_abt2", ""), ("fahrzeuge_abt3", ""), ("fahrzeuge_abt4", ""), 
            ("headless_browser","Ja"), ("path_to_pdftotext.exe", "");  """)

            self.cursor_obj.execute("""INSERT or IGNORE INTO error_db(prozess, error) VALUES ("vpn", "1"),
            ("wachendisplay", "1"),("statusauswertung","1"),("alarm_server", "1"),("testmode", "1"), 
            ("alarm_auswertung","1"); """)

            self.cursor_obj.execute("""INSERT or IGNORE INTO pid_db(dienst,pid) VALUES ("monitoring", "0"),
                        ("vpn", "0"),("crawler","0"), ("auswertung", "0");  """)

            self.con.commit()

        except Error:
            logger.error(Error)
            self.con.close()

# Error_DB:
    def update_error(self, error_prozess, error_code):
        try:
            self.cursor_obj.execute(
                'UPDATE error_db SET error = "' + error_code + '" WHERE prozess = "' + error_prozess + '"')
            self.con.commit()
            logger.debug("Update Error_DB: " + error_prozess + " neuer Errorcode: " + error_code)
        except Error:
            logger.error(Error)

    def select_error(self, prozess):
        try:
            self.cursor_obj.execute('SELECT error FROM error_db WHERE prozess = "' + prozess + '"')
            self.con.commit()
            rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error:
            logger.error(Error)

# Status_DB:
    def update_status(self, fahrzeug, status):
        try:
            self.cursor_obj.execute(
                'UPDATE status_db SET status = "' + status + '" WHERE fahrzeug = "' + fahrzeug + '"')
            self.con.commit()
            logger.debug("Update Status_DB: " + fahrzeug + " neuer Status: " + status)
        except Error:
            logger.error(Error)

    def select_status(self, fahrzeug):
        try:
            self.cursor_obj.execute('SELECT status FROM status_db WHERE fahrzeug = "' + fahrzeug + '"')
            self.con.commit()
            rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error:
            logger.error(Error)

    def safe_status_fahrzeuge(self, fahrzeuge):
        try:
            self.cursor_obj.execute('DELETE FROM status_db')
            self.con.commit()
            for i in fahrzeuge:
                print(i)
                self.cursor_obj.execute('INSERT INTO status_db VALUES( "' + i + '", 2)')
                self.con.commit()
            logger.debug("Statusdatenbank wurde neu mit Fahrzeugen geschrieben")
        except Error:
            logger.error(Error)

    def select_all_fahrzeuge(self):
        try:
            self.cursor_obj.execute('SELECT fahrzeug FROM status_db')
            self.con.commit()
            rueckgabe = self.cursor_obj.fetchall()
            fahrzeug_list = []
            for i in rueckgabe:
                fahrzeug_list.append(i[0])
            return fahrzeug_list
        except Error:
            logger.error(Error)

# Pid_DB
    def update_pid(self, dienst, pid):
        try:
            self.cursor_obj.execute('UPDATE pid_db SET pid = "' + pid + '" WHERE dienst = "' + dienst + '"')
            self.con.commit()
            logger.debug("Update Pid_DB: " + dienst + " neue Pid: " + pid)
        except Error:
            logger.error(Error)

    def select_pid(self, dienst):
        try:
            self.cursor_obj.execute('SELECT pid FROM pid_db WHERE dienst = "' + dienst + '"')
            self.con.commit()
            rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error:
            logger.error(Error)

    def select_all_pids(self):
        try:
            self.cursor_obj.execute('SELECT pid FROM pid_db')
            self.con.commit()
            rueckgabe = self.cursor_obj.fetchall()
            pid_list = []
            for i in rueckgabe:
                pid_list.append(i[0])
            return pid_list
        except Error:
            logger.error(Error)

    def select_aktiv_flag(self, dienst):
        try:
            self.cursor_obj.execute('SELECT aktiv_flag FROM pid_db WHERE dienst = "' + dienst + '"')
            self.con.commit()
            rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error:
            logger.error(Error)

    def update_aktiv_flag(self, dienst, status):
        try:
            self.cursor_obj.execute('UPDATE pid_db SET aktiv_flag = "' + status + '" WHERE dienst = "' + dienst + '"')
            self.con.commit()
        except Error:
            logger.error(Error)

# config_db
    def select_config(self, einstellung):
        try:
            self.cursor_obj.execute('SELECT wert FROM config_db WHERE einstellung = "' + einstellung + '"')
            self.con.commit()
            rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error:
            logger.error(Error)

    def update_config(self, einstellung, wert):

        try:
            self.cursor_obj.execute(
                'UPDATE config_db SET wert = "' + wert + '" WHERE einstellung = "' + einstellung + '"')
            self.con.commit()
        except Error:
            logger.error(Error)

# Close:
    def close_connection(self):
        try:
            self.cursor_obj.close()
            self.con.close()
            logger.debug("Die Datenbankverbindung wurde erfolgreich geschlossen")
        except Error:
            logger.error("Die Datenbankverbindung konnte nicht erfolgreich geschlossen werden! " + str(Error))
