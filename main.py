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
from PyQt6.QtWidgets import QFileDialog, QApplication, QStyle, QDialog, QTextEdit, QVBoxLayout

from bin.einsatz_monitor_modules import init, close_methode, database_class, gennerate_cookie_module  # init wird benötigt!
from bin.einsatz_monitor_modules.help_settings_methoden import *
from ui.mainwindow import Ui_MainWindow

# Einstelungen für High Resolution
#QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.EnableHighDpiScaling, True) #enable highdpi scaling
#QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

# Version Nummer wird hier gesetzt:
version_nr = "0.9.9.9"

# Konfigurationen importieren:
app = QtWidgets.QApplication(sys.argv)
database = database_class.Database()

# Variablen und Pfade setzen:
basedir = os.path.dirname(__file__)
monitoring_file = os.path.join(basedir, "bin", "monitoring_process.py")
vpn_file = os.path.join(basedir, "bin", "ovpn_process.py")
crawler_file = os.path.join(basedir, "bin", "crawler_process.py")
resources = os.path.join(basedir, "resources")
logfile_path = os.path.join(basedir, "logs")
config_path = os.path.join(basedir, "config")
pass_file_vpn = os.path.join(basedir, "config", "pass_ovpn_wachendisplay.txt")
einsatz_process_file = os.path.join(basedir, "bin", "einsatz_process.py" )


# Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(logfile_path, "logfile_main.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)

# Bei schließen des Programms wird die close methode ausgeführt:
app.aboutToQuit.connect(close_methode.close_all)
app.aboutToQuit.connect(database.close_connection)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Einsatz Monitor")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        logger.info("Programm gestartet.")

        # erst mal alle Error, PIDS und Status auf rot serten
        database.reset_pids_and_errors()

        # Subprozess, um das Monitoring zu generieren:
        p = subprocess.Popen([sys.executable, monitoring_file])
        pid = p.pid
        database.update_pid("monitoring", str(pid))

        # timer um die Statusanzeige zu aktualisieren:
        timer_status = QTimer(self)
        timer_status.timeout.connect(self.monitoring)
        timer_status.start(1000)

        # # timer um die Logs anzuzeigen
        timer_logs = QTimer(self)
        timer_logs.timeout.connect(self.log_reload)
        timer_logs.start(800)

        # Icon und Taskbar:
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(resources, "fwsignet_100.png")), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.On)
        self.setWindowIcon(icon)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EM-Statusauswertung")

        # Fwbs Logo einbinden:
        logo_fwbs = QPixmap(resources + "/logo_fwbs.png")
        self.ui.logo_fwbs.setPixmap(logo_fwbs)

        # Version anzeiegn:
        self.ui.label_status_versionnr.setText(version_nr)

        # Hintergrundfarbe der Logs anpassen:
        textedit_widgets = [self.ui.textEdit_log_main, self.ui.textEdit_log_vpn, self.ui.textEdit_log_crawler, self.ui.textEdit_log_EM]
        for widget in textedit_widgets:
            widget.setStyleSheet("background-color: rgb(240, 240,240)")

        # Einstellungen zu Beginn einlesen:
        def set_ui_elements_from_database(ui, config_keys):
            for ui_element, config_key in config_keys:
                ui_object = getattr(ui, ui_element)
                if isinstance(ui_object, QtWidgets.QComboBox):
                    ui_object.setCurrentText(database.select_config(config_key))
                else:
                    ui_object.setText(database.select_config(config_key))

        # Verwenden Sie die neue Funktion, um die Einstellungen zu Beginn einzulesen:
        config_keys = [
            ("lineEdit_settings_funkrufname", "funkrufname"),
            ("lineEdit_settings_token", "connect_api_fahrzeuge"),
            ("lineEdit_wachendisplay_contend_id", "wachendisplay_content_id"),
            ("lineEdit_settings_wachendisplay_url", "url_wachendisplay"),
            ("lineEdit_settings_wachendisplay_user", "user_wachendisplay"),
            ("lineEdit_wachendisplay_password", "passwort_wachendisplay"),
            ("lineEdit_settings_vpn_user", "ovpn_user"),
            ("lineEdit_settings_vpn_password", "ovpn_passwort"),
            ("lineEdit_settings_vpn_path_to_exe", "path_to_openvpn.exe"),
            ("lineEdit_settings_vpn_config", "openvpn_config"),
            ("comboBox_settings_headless_browser", "headless_browser"),
            ("comboBox", "autostart"),
            ("lineEdit_setting_email_user", "email_username"),
            ("lineEdit_settings_email_password", "email_password"),
            ("lineEdit_setings_email_server", "email_server"),
            ("lineEdit_settings_kdo_alarm", "kdo_alarm"),
            ("lineEdit_settings_dag_alternative", "dag_alternativ"),
            #("lineEdit_settings_path_to_pdftotext", "path_to_pdftotext.exe"),
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

        set_ui_elements_from_database(self.ui, config_keys)

        # Autostart:
        if self.ui.comboBox.currentText() == "Ja":
            self.autostart()

        # Fahrzeugliste zu Beginn einlesen:
        fahrzeuge = database.select_all_fahrzeuge()
        fahrzeug_str = ";".join(fahrzeuge)
        self.ui.textEdit_fahrzeuge.setText(fahrzeug_str.replace(";", "\n"))

        # Logs zu Beginn auslesen:
        self.log_reload()

### Menüaufbau und aktionen
        # Alles starten:
        start_all = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay), '&Alles Starten', self)
        start_all.setShortcut('Ctrl+P')
        start_all.triggered[bool].connect(self.autostart)
        self.ui.menu_bersicht.addAction(start_all)

        # Korrigierter Code für PyQt6:

        # Exit:
        exit_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton), '&Exit', self)
        exit_action.setStatusTip('Exit application')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered[bool].connect(QApplication.instance().quit)
        self.ui.menu_bersicht.addAction(exit_action)

        # Installationsleitung:
        install_help = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion),
                               '&Installationsanleitung', self)
        install_help.triggered[bool].connect(installationsanleitung)
        self.ui.menuHilfe.addAction(install_help)

        # Kontakt:
        contact = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation), '&Kontakt', self)
        contact.triggered[bool].connect(kontakt)
        self.ui.menuHilfe.addAction(contact)

        def connect_buttons_to_methods(ui, button_connections):
            for button_name, method in button_connections:
                button = getattr(ui, button_name)
                button.clicked.connect(method)

        # Liste der Button-Verbindungen:
        button_connections = [
            ('pushButton_start_vpn', self.start_vpn),
            ('pushButton_start_auswretung', self.start_status_auswertung),
            ('pushButton_start_einsatzauswertung', self.start_einsatzauswertung),
            ('pushButton_testmode', self.activate_testmode),
            ('pushButton_live_mode', self.autostart),
            ('pushButton_safe_settings_funkrufname', self.safe_settings_funkrufname),
            ('pushButton_safe_setting_fahrzeuge', self.safe_setting_fahrzeuge),
            ('pushButton_safe_settings_token', self.safe_settings_token),
            ('pushButton_safe_settings_vpn_user', self.safe_settings_vpn_user),
            ('pushButton_safe_settings_vpn_password', self.safe_settings_vpn_password),
            ('pushButton_safe_settings_vpn_path_to_exe', self.safe_settings_vpn_path_to_exe),
            ('pushButton_safe_settings_vpn_config', self.safe_settings_vpn_config),
            ('pushButton_safe_settings_wachendisplay_url', self.safe_settings_wachendisplay_url),
            ('pushButton_safe_wachendisplay_contend_id', self.safe_wachendisplay_contend_id),
            ('pushButton_safe_ettings_wachendisplay_user', self.safe_settings_wachendisplay_user),
            ('pushButton_safe_wachendisplay_password', self.safe_wachendisplay_password),
            ('pushButton_safe_headless_browser', self.safe_headless_browser),
            ('pushButton_safe_autostart', self.safe_autostart),
            ('pushButton_settings_gennerat_cookie', self.generate_cookie),
            ('pushButton_settings_safe_email_user', self.safe_email_user),
            ('pushButton_settings_safe_email_password', self.safe_email_password),
            ('pushButton_settings_safe_email_server', self.safe_email_server),
            ('pushButton_settings_safe_kdo_alarm', self.safe_kdo_ric),
            ('pushButton_settings_safe_dag_alternative', self.safe_dag_alternativ),
            #('pushButton_settings_safe_pdftotext', self.safe_pdftotext),
            ('pushButton_safe_settings_token_test', self.safe_settings_token_test),
            ('pushButton_safe_settings_token_abt1', self.safe_settings_token_abt1),
            ('pushButton_safe_settings_token_abt2', self.safe_settings_token_abt2),
            ('pushButton_safe_settings_token_abt3', self.safe_settings_token_abt3),
            ('pushButton_safe_settings_token_abt4', self.safe_settings_token_abt4),
            ('pushButton_safe_settings_token_abt5', self.safe_settings_token_abt5),
            ('pushButton_safe_settings_token_abt6', self.safe_settings_token_abt6),
            ('pushButton_browse_settings_vpn_path_to_exe', self.browse_settings_vpn_path_to_exe),
            ('pushButton_browse_settings_vpn_config', self.browse_settings_vpn_config),
            #('pushButton_settings_browse_pdftotext', self.browse_pdftotext),
            ('pushButton_help_settings_funkrufname', help_settings_funkrufname),
            ('pushButton_help_setting_fahrzeuge', help_setting_fahrzeuge),
            ('pushButton_help_settings_token', help_settings_token),
            ('pushButton_help_settings_vpn_user', help_settings_vpn_user),
            ('pushButton_help_settings_vpn_password', help_settings_vpn_password),
            ('pushButton_help_settings_vpn_path_to_exe', help_settings_vpn_path_to_exe),
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
            #('pushButton_settings_help_pdftotext', help_pdftotext),
            ('pushButton_5_help_settings_connect_tokens_all', help_connect_tokens_all),
            ('pushButton_log_reload', self.log_reload),
            ('pushButton_logs_reset_mainlog', self.reset_log_main),
            ('pushButton_logs_reset_vpnlog', self.reset_log_vpn),
            ('pushButton_logs_reset_crawlerlog', self.reset_log_crawler),
            ('pushButton_logs_reset_emlog', self.reset_log_em),
            ('pushButton_open_log_main', self.open_main_log),
            ('pushButton_open_log_crawler', self.open_crawler_log),
            ('pushButton_open_log_vpn', self.open_ovpn_log),
            ('pushButton_open_log_em', self.open_em_log)
        ]

        # Verbinde die Buttons mit ihren Methoden
        connect_buttons_to_methods(self.ui, button_connections)

    # ####### Methoden auf der Statusseite:
    # Methode, um das OpenVPN modul zu starten,  bzw. zu stoppen, wenn der openvpn Prozess schon ausgeführt wird.
    def start_vpn(self):
        if self.check_prozess("openvpn.exe"):
            # prüfen ob die Auswertung noch läuft:
            if database.select_aktiv_flag("crawler") == 1:
                msg = QMessageBox()
                msg.setWindowTitle("Fehler - Auswertung noch aktiv")
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("Bitte zuerst die Auswertung beenden!")
                msg.exec()
            else:
                pid = list(item.pid for item in psutil.process_iter() if item.name() == 'openvpn.exe')
                for i in pid:
                    psutil.Process(i).terminate()
                    database.update_pid("vpn", "0")
                    print("gekillt!")
        else:
            p = subprocess.Popen([sys.executable, vpn_file])
            pid = p.pid
            database.update_pid("vpn", str(pid))

    # Methode um die Crawler Methode zu starten/stoppen
    def start_status_auswertung(self):
        if database.select_aktiv_flag("crawler") == 1:
            database.update_aktiv_flag("crawler", "0")
            database.update_pid("crawler", "0")
        else:
            # Testen ob das VPN schon steht
            if database.select_error("vpn") == 0:
                database.update_aktiv_flag("crawler", "1")
                p = subprocess.Popen([sys.executable, crawler_file])
                pid = p.pid
                database.update_pid("crawler", str(pid))

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
            database.update_pid("auswertung", "0")
        else:
            database.update_aktiv_flag("auswertung", "1")
            p = subprocess.Popen([sys.executable, einsatz_process_file])
            pid = p.pid
            database.update_pid("auswertung", str(pid))

    # Methode um den Testmodus zu aktivieren:
    def activate_testmode(self):
        if database.select_config("testmode") == "True":
            database.update_config("testmode", "False")
            logger.info("Testmodus wird beendet.")
        else:
            database.update_config("testmode", "True")
            logger.info("Testmodus wird aktiviert.")

# ####### Methoden auf der Einstellungsseite:

    def safe_settings(self, setting_name, setting_value):
        database.update_config(setting_name, setting_value.strip())
        self.safe_success(setting_value)

    def update_setting_with_validation(self, setting_name, setting_value, regex_pattern, error_message):
        if re.match(regex_pattern, setting_value):
            self.safe_settings(setting_name, setting_value)
        else:
            self.show_error_message("Fehler - falsche Syntax!", error_message)

    def show_error_message(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.exec()

    def safe_settings_funkrufname(self):
        set_funkrufname = self.ui.lineEdit_settings_funkrufname.text()
        regex_pattern = "^[A-Z][A-Z]-[A-Z][A-Z]$"
        error_message = "Bitte den Funkrufnamen nach dieser Syntax eingeben: <br><b> FL-BS</b>"
        self.update_setting_with_validation("funkrufname", set_funkrufname, regex_pattern, error_message)
        if re.match(regex_pattern, set_funkrufname):
            self.safe_settings("fw_kurz", set_funkrufname.split("-")[1])

    def safe_setting_fahrzeuge(self):
        set_fahrzeuge = str(self.ui.textEdit_fahrzeuge.toMarkdown())
        fahrzeuge_list = set_fahrzeuge.split("\n\n")
        fahrzeuge_list_clean = [feld.strip() for feld in fahrzeuge_list if feld != '']
        database.safe_status_fahrzeuge(fahrzeuge_list_clean)
        self.safe_success("Fahrzeugliste")

    def safe_settings_token(self):
        set_token = self.ui.lineEdit_settings_token.text()
        self.safe_settings("connect_api_fahrzeuge", set_token)

    def safe_settings_vpn_user(self):
        set_vpn_user = self.ui.lineEdit_settings_vpn_user.text()
        self.safe_settings("ovpn_user", set_vpn_user)
        self.update_vpn_pass_file()

    def safe_settings_vpn_password(self):
        set_vpn_password = self.ui.lineEdit_settings_vpn_password.text()
        self.safe_settings("ovpn_passwort", set_vpn_password)
        self.update_vpn_pass_file()

    def update_vpn_pass_file(self):
        with open(pass_file_vpn, "w", encoding="utf-8") as file:
            file.write(database.select_config("ovpn_user") + "\n" + database.select_config("ovpn_passwort"))

    def safe_settings_vpn_path_to_exe(self):
        safe_settings_vpn_path_to_exe = self.ui.lineEdit_settings_vpn_path_to_exe.text()
        self.safe_settings("path_to_openvpn.exe", safe_settings_vpn_path_to_exe)

    def safe_settings_vpn_config(self):
        safe_settings_vpn_config_path = self.ui.lineEdit_settings_vpn_config.text()
        if "/" in safe_settings_vpn_config_path:
            try:
                shutil.copy2(safe_settings_vpn_config_path, config_path)
                _, filename = os.path.split(safe_settings_vpn_config_path)
                self.ui.lineEdit_settings_vpn_config.setText(filename)
                self.safe_settings("openvpn_config", filename)
            except:
                self.show_error_message("Fehler", "Die Einstellung konnte nicht gespeichert werden.")
        else:
            self.show_error_message("Fehler",
                                    "Die Einstellung konnte nicht gespeichert werden, da der Eingabetext nicht einem absoluten Pfad entspricht.")

    def safe_settings_wachendisplay_url(self):
        safe_settings_wachendisplay_url = self.ui.lineEdit_settings_wachendisplay_url.text()
        regex_pattern = "^http://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,4}/$"
        error_message = "Bitte die URL nach dieser Syntax eingeben: <br><b> http://172.16.24.3:8080/</b>"
        self.update_setting_with_validation("url_wachendisplay", safe_settings_wachendisplay_url, regex_pattern,
                                            error_message)

    def safe_wachendisplay_contend_id(self):
        safe_settings_wachendisplay_content_id = self.ui.lineEdit_wachendisplay_contend_id.text()
        self.safe_settings("wachendisplay_content_id", safe_settings_wachendisplay_content_id)

    def safe_settings_wachendisplay_user(self):
        safe_settings_wachendisplay_user = self.ui.lineEdit_settings_wachendisplay_user.text()
        self.safe_settings("user_wachendisplay", safe_settings_wachendisplay_user)

    def safe_wachendisplay_password(self):
        safe_settings_wachendisplay_passwort = self.ui.lineEdit_wachendisplay_password.text()
        self.safe_settings("passwort_wachendisplay", safe_settings_wachendisplay_passwort)

    def safe_headless_browser(self):
        safe_headless_browser = self.ui.comboBox_settings_headless_browser.currentText()
        self.safe_settings("headless_browser", safe_headless_browser)

    def safe_autostart(self):
        safe_autostart = self.ui.comboBox.currentText()
        self.safe_settings("autostart", safe_autostart)

    def browse_settings_vpn_path_to_exe(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Bitte openvpn.exe auswählen', 'c:\\', "Executables (*.exe)")
        self.ui.lineEdit_settings_vpn_path_to_exe.setText(filepath)


    def safe_email_user(self):
        input_to_safe = self.ui.lineEdit_setting_email_user.text()
        self.safe_settings("email_username", input_to_safe)

    def safe_email_password(self):
        input_to_safe = self.ui.lineEdit_settings_email_password.text()
        self.safe_settings("email_password", input_to_safe)

    def safe_email_server(self):
        input_to_safe = self.ui.lineEdit_setings_email_server.text()
        regex_pattern = "^[A-Za-z0-9]+.[A-Za-z0-9]+.[A-Za-z0-9]{1,4}$"
        error_message = "Bitte die Server-URL nach dieser Syntax eingeben, ohne http(s) oder /: <br><b>imap.serverdomain.org</b>"
        self.update_setting_with_validation("email_server", input_to_safe, regex_pattern, error_message)

    def safe_kdo_ric(self):
        input_to_safe = self.ui.lineEdit_settings_kdo_alarm.text()
        self.safe_settings("kdo_alarm", input_to_safe)

    def safe_dag_alternativ(self):
        input_to_safe = self.ui.lineEdit_settings_dag_alternative.text()
        self.safe_settings("dag_alternativ", input_to_safe)

   # def safe_pdftotext(self):
   #     input_to_safe = self.ui.lineEdit_settings_path_to_pdftotext.text()
   #     self.safe_settings("path_to_pdftotext.exe", input_to_safe)

    def safe_settings_token_test(self):
        input_to_safe = self.ui.lineEdit_settings_token_test.text()
        self.safe_settings("token_test", input_to_safe)

    def safe_settings_token_abt1(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt1.text()
        self.safe_settings("token_abt1", input_to_safe)

    def safe_settings_token_abt2(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt2.text()
        self.safe_settings("token_abt2", input_to_safe)
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt2.text()
        self.safe_settings("fahrzeuge_abt2", input_to_safe_fahrzeuge)

    def safe_settings_token_abt3(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt3.text()
        self.safe_settings("token_abt3", input_to_safe)
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt3.text()
        self.safe_settings("fahrzeuge_abt3", input_to_safe_fahrzeuge)

    def safe_settings_token_abt4(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt4.text()
        self.safe_settings("token_abt4", input_to_safe)
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt4.text()
        self.safe_settings("fahrzeuge_abt4", input_to_safe_fahrzeuge)

    def safe_settings_token_abt5(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt5.text()
        self.safe_settings("token_abt5", input_to_safe)
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt5.text()
        self.safe_settings("fahrzeuge_abt5", input_to_safe_fahrzeuge)

    def safe_settings_token_abt6(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt6.text()
        self.safe_settings("token_abt6", input_to_safe)
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt6.text()
        self.safe_settings("fahrzeuge_abt6", input_to_safe_fahrzeuge)

    def browse_settings_vpn_config(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Öffne Datei', '', 'Config (.ovpn);;All files ()')
        if filepath:
            self.ui.lineEdit_settings_vpn_config.setText(filepath)

   # def browse_settings_pdftotext(self):
   #     filepath, _ = QFileDialog.getOpenFileName(self, 'Öffne Datei', '', 'Executable (.exe);;All files ()')
   #     if filepath:
   #         self.ui.lineEdit_settings_path_to_pdftotext.setText(filepath)

    #def browse_pdftotext(self):
    #    filepath, _ = QFileDialog.getOpenFileName(self, 'Bitte pdftotext.exe auswählen', 'c:\\', "Executables ("
     #                                                                                          "*.exe)")
   #     self.ui.lineEdit_settings_path_to_pdftotext.setText(filepath)

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
            icon = QMessageBox.Icon.Critical
            message = "Cookies erfolgreich erstellt!"
        else:
            title = "Fehler - Cookie konnte nicht erstellt werden"
            icon = QMessageBox.Icon.Critical
            message = "Unbekannter Fehler"

        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setIcon(icon)
        msg.setText(message)
        msg.exec()

# ##### Methoden auf der Logseite:
    LOG_FILES = {
        "Main": "logfile_main.txt",
        "VPN": "logfile_ovpn.txt",
        "Crawler": "logfile_crawler.txt",
        "EM": "logfile_EM.txt",
    }

    def log_reload(self):
        for log_name, log_file in self.LOG_FILES.items():
            self.read_last_five_lines(log_file)

    def read_last_five_lines(self, log_file):
        with open(os.path.join(logfile_path, log_file), "r", encoding="utf-8") as file:
            last_lines = file.readlines()[-50:]
            change_sort = reversed(last_lines)

        if log_file == self.LOG_FILES["Main"]:
            self.ui.textEdit_log_main.setText("".join(change_sort))
        elif log_file == self.LOG_FILES["VPN"]:
            self.ui.textEdit_log_vpn.setText("".join(change_sort))
        elif log_file == self.LOG_FILES["Crawler"]:
            self.ui.textEdit_log_crawler.setText("".join(change_sort))
        elif log_file == self.LOG_FILES["EM"]:
            self.ui.textEdit_log_EM.setText("".join(change_sort))

    def read_log(self, logfile):
        with open(os.path.join(logfile_path, logfile), "r", encoding="utf-8") as file:
            return file.read()

    def reset_log(self, log_file):
        with open(os.path.join(logfile_path, log_file), "w", encoding="utf-8"):
            pass
        self.read_last_five_lines(log_file)

    def reset_log_main(self):
        self.reset_log(self.LOG_FILES["Main"])

    def reset_log_vpn(self):
        self.reset_log(self.LOG_FILES["VPN"])

    def reset_log_crawler(self):
        self.reset_log(self.LOG_FILES["Crawler"])

    def reset_log_em(self):
        self.reset_log(self.LOG_FILES["EM"])

    def open_log_file(self, log_file):
        # Erstelle das Fenster
        dialog = QDialog()
        dialog.setWindowTitle(f"Logfile: {log_file}")

        # Erstelle den Texteditor und lese die Logdatei
        text_edit = QTextEdit()
        with open(os.path.join(logfile_path, log_file), "r", encoding="utf-8") as f:
            log_content = f.read()
            text_edit.setPlainText(log_content)

        # Füge den Texteditor dem Dialog hinzu
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        dialog.setLayout(layout)

        # Zeige den Dialog an
        dialog.exec()

    def open_main_log(self):
        self.open_log_file(self.LOG_FILES["Main"])


    def open_crawler_log(self):
        self.open_log_file(self.LOG_FILES["Crawler"])


    def open_ovpn_log(self):
        self.open_log_file(self.LOG_FILES["VPN"])


    def open_em_log(self):
        self.open_log_file(self.LOG_FILES["EM"])

# ####### Sonstige Methoden:

    # Methode im zu prüfen, ob ein bestimmter Prozess ausgeführt wird. Return: True/False
    def check_prozess(self, prozessname):
        return any(proc.name() == prozessname for proc in psutil.process_iter())

    # Methode zur Textausgabe, dass die Speicherung erfolgreich war:
#    def safe_success(self, einstellung):
#        QMessageBox.information(
#            None,
#            "Erfolgreich gespeichert",
#            f"Die Einstellung {einstellung} wurde erfolgreich gespeichert!"
#        )

    def safe_success(self, einstellung):
        msg = QMessageBox()
        msg.setWindowTitle("Erfolgreich gespeichert")
        msg.setText(f"Die Einstellung {einstellung} wurde erfolgreich gespeichert!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    # Methode um den Farbbutton zu ändern:
    def set_led(self, button, status):
        status_to_image = {
            'green': resources + "/green-led-on_small.png",
            'red': resources + "/led-red-on_small.png",
            'attention': resources + "/attention_small.png"
        }
        button_image = QPixmap(status_to_image[status])
        button.setPixmap(button_image)

    # Methode um die Error-Datenbank auszulesen und die statusanzeigen zu aktualisieren, bzw. einen Neustart zu gennerieren:
    def monitoring(self):
        # Eine Liste von Tupeln, die jedes Status-Widget und zugehörigen Fehler-Typ enthalten
        try:
            STATUS_WIDGETS = [
                (self.ui.status_vpn, "vpn"),
                (self.ui.status_Wachendisplay, "wachendisplay"),
                (self.ui.status_auswertung, "statusauswertung"),
                (self.ui.status_server, "alarm_server"),
                (self.ui.status_alarmscript, "alarm_auswertung")
            ]

            for status_widget, error_type in STATUS_WIDGETS:
                error_count = database.select_error(error_type)
                if error_count == 0:
                    self.set_led(status_widget, 'green')
                elif error_count == 2 and error_type == "alarm_auswertung":
                    database.update_aktiv_flag("auswertung", "1")
                    time.sleep(3)
                    self.start_einsatzauswertung()
                    time.sleep(5)
                    database.update_aktiv_flag("auswertung", "0")
                    self.start_einsatzauswertung()
                    pass
                else:
                    self.set_led(status_widget, 'red')

                if database.select_error('testmode') == 0:
                    self.set_led(self.ui.status_testmodus, 'attention')
                else:
                    self.set_led(self.ui.status_testmodus, 'red')
        except:
            logger.error("Fehler bei der Monitoring Aktualisierung der Datenbank")

    # Methode Autostart
    def autostart(self):
        self.start_vpn()
        time.sleep(30)
        self.start_einsatzauswertung()
        time.sleep(30)
        self.start_status_auswertung()
        logging.info("Autostart durchgeführt")



window = MainWindow()
window.show()
sys.exit(app.exec())