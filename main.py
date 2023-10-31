import ctypes
import logging
import os
import psutil
import re
import shutil
import subprocess
import sys
import time

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import QFileDialog, QApplication, QStyle, QDialog, QTextEdit, QVBoxLayout, QLineEdit

from bin.einsatz_monitor_modules import init, close_methode, database_class, gennerate_cookie_module, wizard_class, validation_utils # init wird benötigt!
from bin.einsatz_monitor_modules.help_settings_methoden import *
from ui.mainwindow import Ui_MainWindow


# Konfigurationen importieren:
database = database_class.Database()

# Variablen und Pfade setzen:
if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.dirname(__file__)
    
monitoring_file = os.path.join(basedir, "bin", "monitoring_process.py")
vpn_file = os.path.join(basedir, "bin", "ovpn_process.py")
crawler_file = os.path.join(basedir, "bin", "crawler_process.py")
resources = os.path.join(basedir, "resources")
logfile_path = os.path.join(basedir, "logs")
config_path = os.path.join(basedir, "config")
pass_file_vpn = os.path.join(basedir, "config", "pass_ovpn_wachendisplay.txt")
einsatz_process_file = os.path.join(basedir, "bin", "einsatz_process.py" )
python_path = os.path.join(basedir, "EinsatzHandler_venv", "Scripts", "python.exe")
rc_file_path = os.path.join(basedir, "versioninfo.rc")

# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(logfile_path, "logfile_main.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EinsatzHandlerNew")
app = QtWidgets.QApplication(sys.argv)
icon = QtGui.QIcon(os.path.join(resources, "fwsignet.ico"))
app.setWindowIcon(icon)

# Bei schließen des Programms wird die close methode ausgeführt:
app.aboutToQuit.connect(close_methode.close_all)
app.aboutToQuit.connect(database.close_connection)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Einsatz Handler")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        logger.info("Programm gestartet.")

        # erst mal alle Error, PIDS und Status auf rot serten
        database.reset_active_flag()


        # Subprozess, um das Monitoring-Prozess zu generieren:
        p = subprocess.Popen([python_path, monitoring_file])

        # wiederholender Timer um die Statusanzeige zu aktualisieren (monitoring-Funktion (self)):
        timer_status = QTimer(self)
        timer_status.timeout.connect(self.monitoring)
        timer_status.start(1000)

        # # timer um die Logs anzuzeigen
        timer_logs = QTimer(self)
        timer_logs.timeout.connect(self.log_reload)
        timer_logs.start(800)


        # Icon und Taskbar:
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(resources, "fwsignet.ico")), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        self.setWindowIcon(icon)

        #self.actionGrundeinrichtung_starten.triggered.connect(self.wizard)

        # Fwbs Logo einbinden:
        logo_fwbs = QPixmap(resources + "/logo_fwbs.png")
        self.ui.logo_fwbs.setPixmap(logo_fwbs)

        help_logo = QIcon(resources + "/information.png")
        button_names = [
            "pushButton_help_settings_funkrufname",
            "pushButton_help_autostart",
            "pushButton_help_settings_vpn_user",
            "pushButton_help_settings_vpn_password",
            "pushButton_help_settings_vpn_config",
            "pushButton_help_settings_wachendisplay_url",
            "pushButton_help_wachendisplay_contend_id",
            "pushButton_help_settings_wachendisplay_user",
            "pushButton_help_wachendisplay_password",
            "pushButton_settings_help_email_user",
            "pushButton_settings_help_email_password",
            "pushButton_settings_help_email_server",
            "pushButton_settings_help_kdo_alarm",
            "pushButton_settings_help_dag_alternative",
            "pushButton_help_settings_token",
            "pushButton_5_help_settings_connect_tokens_all"
        ]
        for button_name in button_names:
            button = getattr(self.ui, button_name)
            button.setIcon(help_logo)


        # Version Info:
        version_nr = self.read_version_from_rc(rc_file_path)
        
        if version_nr:
            self.ui.label_status_versionnr.setText(version_nr)
        else:
            self.ui.label_status_versionnr.setText("Version nicht verfügbar")

        # Einstellungen zu Beginn einlesen:


        # Verwenden Sie die neue Funktion, um die Einstellungen zu Beginn einzulesen:

        self.set_ui_elements_from_database(self.ui)

        # Autostart:
        if self.ui.comboBox.currentText() == "Ja":
            self.autostart()


        # Logs zu Beginn auslesen:
        self.log_reload()


        # Wizard anzeigen, wenn die Datenbank noch leer ist
        if (database.select_config("funkrufname") == "" and
            database.select_config("wachendisplay_content_id") == "" and
            database.select_config("ovpn_user") == "" and
            database.select_config("email_username") == ""):
            self.wizard()

### Menüaufbau und aktionen

        def connect_buttons_to_methods(ui, button_connections):
            for button_name, method in button_connections:
                button = getattr(ui, button_name)
                button.clicked.connect(method)

        # Liste der Button-Verbindungen:
        button_connections = [
            ('pushButton_start_vpn', self.start_vpn),
            ('pushButton_start_auswretung', self.start_status_auswertung_local),
            ('pushButton_start_einsatzauswertung', self.start_einsatzauswertung),
            ('pushButton_testmode', self.activate_testmode),
            ('pushButton_save_settings_allgemein', self.save_settings_allgemein),
            ('pushButton_save_settings_vpn', self.save_settings_vpn),
            ('pushButton_save_settings_wachendisplay', self.settings_wachendisplay),
            ('pushButton_save_settings_email', self.save_settings_email),
            ('pushButton_save_settings_alltokens', self.save_settings_alltokens),
            ('pushButton_settings_gennerat_cookie', self.generate_cookie),
            ('pushButton_browse_settings_vpn_config', self.browse_settings_vpn_config),
            ('pushButton_help_settings_funkrufname', help_settings_funkrufname),
            ('pushButton_help_settings_token', help_settings_token),
            ('pushButton_help_settings_vpn_user', help_settings_vpn_user),
            ('pushButton_help_settings_vpn_password', help_settings_vpn_password),
            ('pushButton_help_settings_vpn_config', help_settings_vpn_config),
            ('pushButton_help_settings_wachendisplay_url', help_settings_wachendisplay_url),
            ('pushButton_help_wachendisplay_contend_id', help_wachendisplay_contend_id),
            ('pushButton_help_settings_wachendisplay_user', help_settings_wachendisplay_user),
            ('pushButton_help_wachendisplay_password', help_wachendisplay_password),
            ('pushButton_help_autostart', help_autostart),
            ('pushButton_settings_help_email_user', help_email_user),
            ('pushButton_settings_help_email_password', help_email_passwort),
            ('pushButton_settings_help_email_server', help_email_Server),
            ('pushButton_settings_help_kdo_alarm', help_kdo_alarm),
            ('pushButton_settings_help_dag_alternative', help_dag_alternativ),
            ('pushButton_5_help_settings_connect_tokens_all', help_connect_tokens_all),
            ('pushButton_logs_reset_mainlog', self.reset_log_main),
            ('pushButton_logs_reset_vpnlog', self.reset_log_vpn),
            ('pushButton_logs_reset_crawlerlog', self.reset_log_crawler),
            ('pushButton_logs_reset_emlog', self.reset_log_em),
            ('pushButton_open_log_main', self.open_main_log),
            ('pushButton_open_log_crawler', self.open_crawler_log),
            ('pushButton_open_log_vpn', self.open_ovpn_log),
            ('pushButton_open_log_em', self.open_em_log),
            ('pushButton_logs_fahrzeugliste', self.pushButton_logs_fahrzeugliste),
        ]

        # Verbinde die Buttons mit ihren Methoden
        connect_buttons_to_methods(self.ui, button_connections)

        # Menüeintrag Grundeinrichtung starten:
        grundeinrichtung_action = QAction('Grundeinrichtung starten', self)
        grundeinrichtung_action.setStatusTip('Startet die Grundeinrichtung')
        grundeinrichtung_action.triggered[bool].connect(self.wizard)
        self.ui.menu.addAction(grundeinrichtung_action)


        # Exit:
        exit_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton), '&Exit', self)
        exit_action.setStatusTip('Exit application')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered[bool].connect(QApplication.instance().quit)
        self.ui.menu.addAction(exit_action)





    # ####### Methoden auf der Statusseite:
    # Methode, um das OpenVPN modul zu starten,  bzw. zu stoppen, wenn der openvpn Prozess schon ausgeführt wird.
    def start_vpn(self):
        if self.check_prozess("openvpn.exe"):
            # prüfen ob die Auswertung noch läuft:
            if database.select_aktiv_flag("crawler") in [1, 3]:
                msg = QMessageBox()
                msg.setWindowTitle("Fehler - Auswertung noch aktiv")
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Bitte zuerst die Auswertung beenden!")
                msg.exec()
            else:
                pid = list(item.pid for item in psutil.process_iter() if item.name() == 'openvpn.exe')
                for i in pid:
                    psutil.Process(i).terminate()
                    database.update_aktiv_flag("vpn", "0")
                    with open(os.path.join(basedir,"logs", self.LOG_FILES["vpn"]), "a") as f:
                        f.write("###########\nVPN wird beendet \n\n\n")
        else:
            with open(os.path.join(basedir,"logs", self.LOG_FILES["vpn"]), "a") as f:
                p = subprocess.Popen([python_path, vpn_file], stdout=f, stderr=f)
            database.update_aktiv_flag("vpn", p.pid)


    # Methode um die Crawler Methode zu starten/stoppen
    def start_status_auswertung_local(self):
        if database.select_aktiv_flag("crawler") in [1, 3]:
            database.update_aktiv_flag("crawler", "0")

        else:
            # Testen ob das VPN schon steht
            if database.select_aktiv_flag("vpn") != 0:
                database.update_aktiv_flag("crawler", "3")
                subprocess.Popen([python_path, crawler_file])

            else:
                msg = QMessageBox()
                msg.setWindowTitle("Fehler - VPN nicht aktiv")
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Bitte zuerst das VPN starten!")
                msg.exec()

    # Methode um die Einsatzauswertung zu starten:
    def start_einsatzauswertung(self):
        if database.select_aktiv_flag("auswertung") == 1:
            database.update_aktiv_flag("auswertung", "0")
        else:
            database.update_aktiv_flag("auswertung", "1")
            subprocess.Popen([python_path, einsatz_process_file])

    # Methode um den Testmodus zu aktivieren:
    def activate_testmode(self):
        if database.select_config("testmode") == "True":
            database.update_config("testmode", "False")
            logger.info("Testmodus wird beendet.")
        else:
            database.update_config("testmode", "True")
            logger.info("Testmodus wird aktiviert.")

# ####### Methoden auf der Einstellungsseite:

    def save_settings(self, key, value):
        try:
            database.update_config(key, value)
            logger.info(f"Einstellung {key} wurde erfolgreich auf {value} gesetzt.")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Einstellung {key}: {e}")

    def validate_and_save(self, key, input_value, validation_type, error_message, widget=None):            
        if input_value == "":
            self.save_settings(key, input_value)
            return True
        else:
            is_valid = validation_utils.validate_input(input_value, validation_type)

            # hier ist der Ablauf, wenn die Synthay falsch ist, um den Ursprungswert wieder zu setzen.
            if not is_valid:
                self.show_error_message("Fehler - falsche Syntax!", error_message)
                if widget:  # Wenn ein Widget angegeben ist:
                    config_value = database.select_config(key)  # Wert aus der Datenbank holen
                    if config_value is not None:  # Wenn der Wert nicht None ist
                        widget.setText(str(config_value))  # Setzen Sie den Wert im Widget
                    else:
                        logger.error(f"Konnte den Wert für {key} nicht aus der Datenbank abrufen.")
            else:
                #und schlussendlich speichern
                if key == "openvpn_config":
                    pass
                else:
                    self.save_settings(key, input_value)  # Wenn die Validierung erfolgreich ist, speichern Sie die Einstellung

            return is_valid

    def show_error_message(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.exec()

    def save_success(self, einstellung):
        msg = QMessageBox()
        msg.setWindowTitle("Erfolgreich gespeichert")
        msg.setText(f"Die Einstellung der korrekt ausgefüllten {einstellung} wurde erfolgreich gespeichert!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def save_settings_allgemein(self):
        # Speichern der allgemeinen Einstellungen für Autostart
        autostart_input = self.ui.comboBox.currentText()
        self.save_settings("autostart", autostart_input)

        # Spezielle Validierung für Funkrufname
        input_to_save  = self.ui.lineEdit_settings_funkrufname.text()
        self.validate_and_save( "funkrufname", input_to_save , "funkrufname", "Bitte die richtige Schreibweise von <b>Funkrufnamen</b> beachten", self.ui.lineEdit_settings_funkrufname)

        self.save_success("Allgemeine Einstellungen")


    def save_settings_vpn(self):
        settings_mapping = {
            "ovpn_user": self.ui.lineEdit_settings_vpn_user,
            "ovpn_passwort": self.ui.lineEdit_settings_vpn_password,
        }

        # Allgemeine Einstellungen
        for key, ui_element in settings_mapping.items():
            input_to_save = ui_element.text()
            self.save_settings(key, input_to_save)
        with open(pass_file_vpn, "w", encoding="utf-8") as file:
            file.write(database.select_config("ovpn_user") + "\n" + database.select_config("ovpn_passwort"))

        # Spezielle Validierung für die VPN-Konfigurationsdatei
        vpn_config_path = self.ui.lineEdit_settings_vpn_config.text()
        _, filename = os.path.split(vpn_config_path)
        _, file_ext = os.path.splitext(filename)

        if file_ext.lower() == '.ovpn':
            if os.path.isabs(vpn_config_path):
                try:
                    self.validate_and_save("openvpn_config", vpn_config_path, "openvpn_config", "Die Einstellung konnte nicht gespeichert werden.", self.ui.lineEdit_settings_vpn_config)
                    shutil.copy2(vpn_config_path, config_path)
                    database.update_config("openvpn_config", filename)
                    self.ui.lineEdit_settings_vpn_config.setText(filename)
                except Exception as e:
                    self.ui.lineEdit_settings_vpn_config.setText(database.select_config("openvpn_config"))
                    self.show_error_message("Fehler", f"Die Einstellung konnte nicht gespeichert werden: {e}")
            else:
                self.ui.lineEdit_settings_vpn_config.setText(database.select_config("openvpn_config"))
                self.show_error_message("Fehler", "Der Pfad ist nicht absolut.")
        else:
            self.ui.lineEdit_settings_vpn_config.setText(database.select_config("openvpn_config"))
            self.show_error_message("Fehler", "Die Einstellung konnte nicht gespeichert werden, da der Dateiname nicht auf .ovpn endet.")

        self.save_success("VPN Einstellungen")
        

    def browse_settings_vpn_config(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Öffne Datei', '', 'All files ()')
        if filepath:
            self.ui.lineEdit_settings_vpn_config.setText(filepath)

    def settings_wachendisplay(self):
        settings_mapping = {
            "wachendisplay_content_id": self.ui.lineEdit_wachendisplay_contend_id,
            "user_wachendisplay": self.ui.lineEdit_settings_wachendisplay_user,
            "passwort_wachendisplay": self.ui.lineEdit_wachendisplay_password,
            "headless_browser": self.ui.comboBox_settings_headless_browser,
        }

        # Spezielle Validierung für die URL
        wachendisplay_url = self.ui.lineEdit_settings_wachendisplay_url.text()
        self.validate_and_save("url_wachendisplay", wachendisplay_url, "url_wachendisplay", "Bitte die richtige Schreibweise von <b>URL Wachendisplay</b> beachten", self.ui.lineEdit_settings_wachendisplay_url)

        # Allgemeine Einstellungen
        for key, ui_element in settings_mapping.items():
            input_to_save = ui_element.text() if hasattr(ui_element, 'text') else ui_element.currentText()
            
            if key == "wachendisplay_content_id":
                self.validate_and_save("wachendisplay_content_id", input_to_save, "wachendisplay_content_id", "Bitte die richtige Schreibweise von <b>ContentID</b> beachten", self.ui.lineEdit_wachendisplay_contend_id)
            else:
                self.save_settings(key, input_to_save)

        self.save_success("Wachendisplay Einstellungen")

    def save_settings_email(self):
        settings_mapping = {
            "email_username": self.ui.lineEdit_setting_email_user,
            "email_password": self.ui.lineEdit_settings_email_password,
            "email_server": self.ui.lineEdit_setings_email_server,
            "kdo_alarm": self.ui.lineEdit_settings_kdo_alarm,
            "dag_alternativ": self.ui.lineEdit_settings_dag_alternative,
        }

        for key, line_edit in settings_mapping.items():
            input_to_save = line_edit.text()

            if key == "email_server":
                self.validate_and_save("email_server", input_to_save, "email_server", "Bitte die richtige Schreibweise von <b>URL E-Mail Server</b> beachten", self.ui.lineEdit_setings_email_server)
            
            elif key == "kdo_alarm":
                self.validate_and_save("kdo_alarm", input_to_save, "kdo_alarm", "Bitte die richtige Schreibweise von <b>KDO-Alarm RIC</b> beachten", self.ui.lineEdit_settings_kdo_alarm)
            
            else:
                self.save_settings(key, input_to_save)

        self.save_success("E-Mail Einstellungen")


    def save_settings_alltokens(self):
        settings_mapping = {
            "connect_api_fahrzeuge": self.ui.lineEdit_settings_token,
            "token_test": self.ui.lineEdit_settings_token_test,
        }

        # Dynamisch generierte Schlüssel und Widgets hinzufügen
        for i in range(1, 7):
            token_widget = getattr(self.ui, f"lineEdit_settings_token_abt{i}", None)
            fahrzeuge_widget = getattr(self.ui, f"lineEdit_settings_fahrzeuge_abt{i}", None)
            if token_widget is not None:
                settings_mapping[f"token_abt{i}"] = token_widget
            if fahrzeuge_widget is not None:
                settings_mapping[f"fahrzeuge_abt{i}"] = fahrzeuge_widget

        for key, widget in settings_mapping.items():
            if widget is None:
                continue  # Überspringen, wenn das Widget nicht existiert
            if isinstance(widget, QLineEdit):
                input_to_save = widget.text()
            elif isinstance(widget, QTextEdit):
                input_to_save = widget.toPlainText()
            else:
                continue  # Überspringen, wenn der Widget-Typ nicht unterstützt wird

            # Der leere String wird jetzt auch gespeichert
            if "fahrzeuge_abt" in key:
                self.validate_and_save(key, input_to_save, "fahrzeuge_abt", "Bitte die richtige Schreibweise von <b>Fahrzeuge Abteilung</b> beachten", widget)
            else:
                database.update_config(key, input_to_save)

        self.save_success("Tokens")



    # methode um die Cookies zu gennerieren:
    def generate_cookie(self):
        r = gennerate_cookie_module.get_cookie()
        title = None
        icon = None
        message = None

        if r == "fehler vpn":
            title = "Fehler - VPN nicht aktiv"
            icon = QMessageBox.Icon.Critical
            message = "Bitte zuerst das VPN starten!"
        elif r == "fehler config":
            title = "Fehler - Wachendisplay Configuration nicht erledigt"
            icon = QMessageBox.Icon.Critical
            message = "Bitte zuerst die Wachendisplay Config durchführen!"
        elif r == "erfolgreich":
            title = "Erfolgreich!"
            icon = QMessageBox.Icon.Information
            message = "Cookies erfolgreich erstellt!"
        else:
            title = "Fehler - Cookie konnte nicht erstellt werden"
            icon = QMessageBox.Icon.Critical
            message = f"Fehler - Cookie konnte nicht erstellt werden - Unbekannter Fehler: {r}"


        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(icon)
        msg.setText(message)
        msg.exec()

# ##### Methoden auf der Logseite:
    LOG_FILES = {
        "main": "logfile_main.txt",
        "vpn": "logfile_ovpn.txt",
        "crawler": "logfile_crawler.txt",
        "em": "logfile_EM.txt",
    }

    def log_reload(self):
        for log_name, log_file in self.LOG_FILES.items():
            self.read_last_five_lines(log_file)

    def read_last_five_lines(self, log_file):
        with open(os.path.join(logfile_path, log_file), "r", encoding="utf-8") as file:
            last_lines = file.readlines()[-50:]
            change_sort = reversed(last_lines)

        if log_file == self.LOG_FILES["main"]:
            self.ui.textEdit_log_main.setText("".join(change_sort))
        elif log_file == self.LOG_FILES["vpn"]:
            self.ui.textEdit_log_vpn.setText("".join(change_sort))
        elif log_file == self.LOG_FILES["crawler"]:
            self.ui.textEdit_log_crawler.setText("".join(change_sort))
        elif log_file == self.LOG_FILES["em"]:
            self.ui.textEdit_log_EM.setText("".join(change_sort))

    def read_log(self, logfile):
        with open(os.path.join(logfile_path, logfile), "r", encoding="utf-8") as file:
            return file.read()

    def reset_log(self, log_file):
        with open(os.path.join(logfile_path, log_file), "w", encoding="utf-8"):
            pass
        self.read_last_five_lines(log_file)

    def reset_log_main(self):
        self.reset_log(self.LOG_FILES["main"])

    def reset_log_vpn(self):
        self.reset_log(self.LOG_FILES["vpn"])

    def reset_log_crawler(self):
        self.reset_log(self.LOG_FILES["crawler"])

    def reset_log_em(self):
        self.reset_log(self.LOG_FILES["em"])

    def open_log_file(self, log_file):
        # Erstelle das Fenster
        dialog = QDialog()
        dialog.setWindowTitle(f"Logfile: {log_file}")

        text_edit = QTextEdit()
        with open(os.path.join(logfile_path, log_file), "r", encoding="utf-8") as f:
            log_content = f.read()
            text_edit.setPlainText(log_content)
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        dialog.setLayout(layout)

        # Zeige den Dialog an
        dialog.exec()

    def open_main_log(self):
        self.open_log_file(self.LOG_FILES["main"])


    def open_crawler_log(self):
        self.open_log_file(self.LOG_FILES["crawler"])


    def open_ovpn_log(self):
        self.open_log_file(self.LOG_FILES["vpn"])


    def open_em_log(self):
        self.open_log_file(self.LOG_FILES["em"])

    def pushButton_logs_fahrzeugliste(self):
        dialog = QDialog()
        dialog.setWindowTitle(f"Fahrzeugliste")

        text_edit = QTextEdit()
        # Fahrzeugliste zu Beginn einlesen:
        fahrzeuge = database.select_all_fahrzeuge()
        fahrzeug_str = ";".join(fahrzeuge)
        fahrzeugliste = fahrzeug_str.replace(";", "\n")

        text_edit.setPlainText(fahrzeugliste)
        
        # Füge den Texteditor dem Dialog hinzu
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        dialog.setLayout(layout)

        # Zeige den Dialog an
        dialog.exec()

# ####### Sonstige Methoden:

    # Methode im zu prüfen, ob ein bestimmter Prozess ausgeführt wird. Return: True/False
    def check_prozess(self, prozessname):
        return any(proc.name() == prozessname for proc in psutil.process_iter())


    def set_led(self, button, status):
        if status == 'loading':
            movie = QMovie(resources + "/spinner.gif")
            button.setMovie(movie)
            movie.start()
            button.repaint()  # Erzwingt eine Neumalung des Widgets
        else:
            status_to_image = {
                'green': resources + "/led-green.png",
                'red': resources + "/led-red.png",
                'attention': resources + "/attention.png"
            }
            button_image = QPixmap(status_to_image[status])
            button.setPixmap(button_image)

    def monitoring(self):
        try:
            STATUS_WIDGETS = [
                (self.ui.status_vpn, "vpn"),
                (self.ui.status_Wachendisplay, "wachendisplay"),
                (self.ui.status_auswertung, "crawler"),
                (self.ui.status_server, "alarm_server"),
                (self.ui.status_alarmscript, "auswertung")
            ]

            for status_widget, application_type in STATUS_WIDGETS:
                active_flag = database.select_aktiv_flag(application_type)

                # Spezielle Routine für VPN
                if application_type == 'vpn' and active_flag not in [0, 1, 2]:
                    with open(os.path.join(basedir, "logs", self.LOG_FILES["vpn"]), "r") as f:
                        last_lines = f.readlines()[-1:]  # Lesen der letzte Zeilen
                        if any("Initialization Sequence Completed" in line for line in last_lines):
                            self.set_led(status_widget, 'green')
                            database.update_aktiv_flag(application_type, "1")
                        else:
                            self.set_led(status_widget, 'loading')
                    continue  # Überspringen Sie den Rest der Schleife für diesen Fall

                # Allgemeine Routine
                if active_flag == 0:
                    self.set_led(status_widget, 'red')
                elif active_flag == 2:
                    self.set_led(status_widget, 'attention')
                elif active_flag == 3:
                    log_file = self.LOG_FILES.get(application_type)
                    if log_file:
                        with open(os.path.join(basedir, "logs", log_file), "r") as f:
                            last_lines = f.readlines()[-1:]  # Letzte 1 Zeilen
                            if application_type == 'crawler':
                                keyword = "Wachendisplay erfolgreich geladen"
                            else:
                                keyword = None

                            if keyword and any(keyword in line for line in last_lines):
                                self.set_led(status_widget, 'green')
                                database.update_aktiv_flag(application_type, "1")
                            else:
                                self.set_led(status_widget, 'loading')
                else:
                    self.set_led(status_widget, 'green')

            if database.select_aktiv_flag('testmode') == 1:
                self.set_led(self.ui.status_testmodus, 'attention')
            else:
                self.set_led(self.ui.status_testmodus, 'red')
        except Exception as e:
            print(f"Exception in monitoring: {e}")


    # Methode Autostart
    def autostart(self):
        self.start_vpn()
        time.sleep(30)
        self.start_einsatzauswertung()
        time.sleep(30)
        self.start_status_auswertung_local()
        logging.info("Autostart durchgeführt")

    # Methode um alle Subprozesse des Programms nach einem bestimmen Prozess zu durchsuchen
    def check_child_process(self, process_name):
        parent = psutil.Process(os.getpid())  # Holt den aktuellen Prozess
        # Durchsucht die untergeordneten Prozesse
        for child in parent.children(recursive=True):
            if child.name() == process_name:
                # Der Prozess läuft
                return True
        # Der Prozess läuft nicht
        return False
    
    # Methode um die Version Nr aus der versioninfo.rc zu importieren
    def read_version_from_rc(self, rc_file_path):
        with open(rc_file_path, 'r') as f:
            content = f.read()
            match = re.search(r'filevers=\((\d+,\s*\d+,\s*\d+,\s*\d+)\)', content)
            if match:
                version = match.group(1).replace(',', '.')
                return version
        return None
    
    # Methode für die Grundeinrichtung:
    def wizard(self):
        self.my_wizard = wizard_class.MyWizard(self)
        self.my_wizard.wizardCompleted.connect(lambda: self.set_ui_elements_from_database(self.ui))
        self.my_wizard.show()


    def set_ui_elements_from_database(self, ui):
        config_keys = [
            ("lineEdit_settings_funkrufname", "funkrufname"),
            ("lineEdit_settings_token", "connect_api_fahrzeuge"),
            ("lineEdit_wachendisplay_contend_id", "wachendisplay_content_id"),
            ("lineEdit_settings_wachendisplay_url", "url_wachendisplay"),
            ("lineEdit_settings_wachendisplay_user", "user_wachendisplay"),
            ("lineEdit_wachendisplay_password", "passwort_wachendisplay"),
            ("lineEdit_settings_vpn_user", "ovpn_user"),
            ("lineEdit_settings_vpn_password", "ovpn_passwort"),
            ("lineEdit_settings_vpn_config", "openvpn_config"),
            ("comboBox_settings_headless_browser", "headless_browser"),
            ("comboBox", "autostart"),
            ("lineEdit_setting_email_user", "email_username"),
            ("lineEdit_settings_email_password", "email_password"),
            ("lineEdit_setings_email_server", "email_server"),
            ("lineEdit_settings_kdo_alarm", "kdo_alarm"),
            ("lineEdit_settings_dag_alternative", "dag_alternativ"),
            ("lineEdit_settings_token_test", "token_test"),
            ("lineEdit_settings_token_abt1", "token_abt1"),
            ("lineEdit_settings_token_abt2", "token_abt2"),
            ("lineEdit_settings_token_abt3", "token_abt3"),
            ("lineEdit_settings_token_abt4", "token_abt4"),
            ("lineEdit_settings_token_abt5", "token_abt5"),
            ("lineEdit_settings_token_abt6", "token_abt6"),
            ("lineEdit_settings_fahrzeuge_abt2", "fahrzeuge_abt2"),
            ("lineEdit_settings_fahrzeuge_abt3", "fahrzeuge_abt3"),
            ("lineEdit_settings_fahrzeuge_abt4", "fahrzeuge_abt4"),
            ("lineEdit_settings_fahrzeuge_abt5", "fahrzeuge_abt5"),
            ("lineEdit_settings_fahrzeuge_abt6", "fahrzeuge_abt6"),
        ]

        for ui_element, config_key in config_keys:
            ui_object = getattr(ui, ui_element)
            if isinstance(ui_object, QtWidgets.QComboBox):
                ui_object.setCurrentText(database.select_config(config_key))
            else:
                ui_object.setText(database.select_config(config_key))


try:
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
except Exception as e:
    logger.error("Ein Fehler ist aufgetreten: %s", e)
finally:
    logger.info("Es wird alles geschlossen")
    database.close_connection()
    close_methode.close_all()