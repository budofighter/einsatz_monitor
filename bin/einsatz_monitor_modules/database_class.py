# Optimiert 31.03.23
import os.path
import sqlite3
import logging
from sqlite3 import Error

path_to_database = os.path.join(os.path.dirname(__file__), "..", "..", "database.db")

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), "..", "..", "logs", "logfile_main.txt"),
                                   encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)


class Database:

    def __init__(self):
        self.con = None
        self.cursor_obj = None
        try:
            self.connect()
            self.create_tables()
        except Error as e:
            logger.error(e)
            self.close_connection()

    def connect(self):
        self.con = sqlite3.connect(path_to_database)
        logger.debug("Datenbankverbindung erfolgreich aufgebaut")
        self.cursor_obj = self.con.cursor()

    def create_tables(self):
        try:
            if self.cursor_obj:
                self.cursor_obj.execute("""CREATE TABLE IF NOT EXISTS config_db (einstellung TEXT UNIQUE, wert TEXT);""")
                self.cursor_obj.execute("""CREATE TABLE IF NOT EXISTS error_db (prozess TEXT UNIQUE, error INTEGER);""")
                self.cursor_obj.execute("""CREATE TABLE IF NOT EXISTS pid_db (dienst TEXT UNIQUE, pid INTEGER, aktiv_flag Integer);""")
                self.cursor_obj.execute("""CREATE TABLE IF NOT EXISTS status_db (fahrzeug TEXT UNIQUE, status INTEGER);""")

                config_data = [("connect_api_fahrzeuge", ""), ("url_wachendisplay", ""),("wachendisplay_content_id", ""),("funkrufname",
                ""),("user_wachendisplay", ""),("passwort_wachendisplay", ""),("ovpn_user", ""),("ovpn_passwort", ""),
                ("path_to_openvpn.exe", ""),("openvpn_config", ""),("autostart", ""), ("testmode", "False"),
                ("dag_alternativ", ""), ("fw_kurz",""), ("kdo_alarm",""), ("email_username", "") , ("email_password",
                ""), ("email_server",""), ("token_test", ""), ("token_abt1", ""), ("token_abt2", ""), ("token_abt3", ""),
                ("token_abt4", ""), ("token_abt5", ""), ("token_abt6", ""), ("fahrzeuge_abt2", ""), ("fahrzeuge_abt3", ""),
                ("fahrzeuge_abt4", ""), ("fahrzeuge_abt5", ""), ("fahrzeuge_abt6", ""), ("headless_browser","Ja"), ("path_to_pdftotext.exe", "")]

                self.cursor_obj.executemany("INSERT or IGNORE INTO config_db(einstellung, wert) VALUES (?, ?)",
                                            config_data)

                error_data = [("vpn", "1"), ("wachendisplay", "1"), ("statusauswertung", "1"),
                              ("alarm_server", "1"), ("testmode", "1"), ("alarm_auswertung", "1")]
                self.cursor_obj.executemany("INSERT or IGNORE INTO error_db(prozess, error) VALUES (?, ?)", error_data)

                pid_data = [("monitoring", "0"), ("vpn", "0"), ("crawler", "0"), ("auswertung", "0")]
                self.cursor_obj.executemany("INSERT or IGNORE INTO pid_db(dienst,pid) VALUES (?, ?)", pid_data)

                self.con.commit()

        except Error as e:
            logger.error(e)
            self.con.close()

# Error_DB:
    def update_error(self, error_prozess, error_code):
        try:
            with self.con:
                self.cursor_obj.execute('UPDATE error_db SET error = ? WHERE prozess = ?',
                                        (error_code, error_prozess))
            logger.debug(f"Update Error_DB: {error_prozess} neuer Errorcode: {error_code}")
        except Error as e:
            logger.error(e)

    def select_error(self, prozess):
        try:
            with self.con:
                self.cursor_obj.execute('SELECT error FROM error_db WHERE prozess = ?', (prozess,))
                rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error as e:
            logger.error(e)

# Status_DB:
    def update_status(self, fahrzeug, status):
        try:
            with self.con:
                self.cursor_obj.execute('UPDATE status_db SET status = ? WHERE fahrzeug = ?',
                                        (status, fahrzeug))
            logger.debug(f"Update Status_DB: {fahrzeug} neuer Status: {status}")
        except Error as e:
            logger.error(e)

    def select_status(self, fahrzeug):
        try:
            with self.con:
                self.cursor_obj.execute('SELECT status FROM status_db WHERE fahrzeug = ?', (fahrzeug,))
                rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error as e:
            logger.error(e)

    def safe_status_fahrzeuge(self, fahrzeuge):
        try:
            with self.con:
                self.cursor_obj.execute('DELETE FROM status_db')
                for i in fahrzeuge:
                    self.cursor_obj.execute('INSERT INTO status_db VALUES( ?, 2)', (i,))
            logger.debug("Statusdatenbank wurde neu mit Fahrzeugen geschrieben")
        except Error as e:
            logger.error(e)

    def select_all_fahrzeuge(self):
        try:
            with self.con:
                self.cursor_obj.execute('SELECT fahrzeug FROM status_db')
                rueckgabe = self.cursor_obj.fetchall()
            fahrzeug_list = [i[0] for i in rueckgabe]
            return fahrzeug_list
        except Error as e:
            logger.error(e)

# Pid_DB
    def update_pid(self, dienst, pid):
        try:
            with self.con:
                self.cursor_obj.execute('UPDATE pid_db SET pid = ? WHERE dienst = ?',
                                        (pid, dienst))
            logger.debug(f"Update Pid_DB: {dienst} neue Pid: {pid}")
        except Error as e:
            logger.error(e)

    def select_pid(self, dienst):
        try:
            with self.con:
                self.cursor_obj.execute('SELECT pid FROM pid_db WHERE dienst = ?', (dienst,))
                rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error as e:
            logger.error(e)

    def select_all_pids(self):
        try:
            with self.con:
                self.cursor_obj.execute('SELECT pid FROM pid_db')
                rueckgabe = self.cursor_obj.fetchall()
            pid_list = [i[0] for i in rueckgabe]
            return pid_list
        except Error as e:
            logger.error(e)

    def select_aktiv_flag(self, dienst):
        try:
            with self.con:
                self.cursor_obj.execute('SELECT aktiv_flag FROM pid_db WHERE dienst = ?', (dienst,))
                rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error as e:
            logger.error(e)

    def update_aktiv_flag(self, dienst, status):
        try:
            with self.con:
                self.cursor_obj.execute('UPDATE pid_db SET aktiv_flag = ? WHERE dienst = ?', (status, dienst))
            logger.debug(f"Update aktiv_flag: {dienst} neuer Status: {status}")
        except Error as e:
            logger.error(e)

    # config_db
    def select_config(self, einstellung):
        try:
            with self.con:
                self.cursor_obj.execute('SELECT wert FROM config_db WHERE einstellung = ?', (einstellung,))
                rueckgabe = self.cursor_obj.fetchone()
            return rueckgabe[0]
        except Error as e:
            logger.error(e)

    def update_config(self, einstellung, wert):
        try:
            with self.con:
                self.cursor_obj.execute(
                    'UPDATE config_db SET wert = ? WHERE einstellung = ?',
                    (wert, einstellung))
            logger.debug(f"Update config_db: {einstellung} neuer Wert: {wert}")
        except Error as e:
            logger.error(e)

# Close:
    def close_connection(self):
        try:
            self.cursor_obj.close()
            self.con.close()
            logger.debug("Die Datenbankverbindung wurde erfolgreich geschlossen")
        except Error as e:
            logger.error("Die Datenbankverbindung konnte nicht erfolgreich geschlossen werden! " + str(e))

    def get_all_configs(self):
        try:
            with self.con:
                self.cursor_obj.execute('SELECT * FROM config_db')
                configs = self.cursor_obj.fetchall()
            config_dict = {config[0]: config[1] for config in configs}
            return config_dict
        except Error as e:
            logger.error(e)
