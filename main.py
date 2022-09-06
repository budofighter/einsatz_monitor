import sys, os, subprocess, psutil, shutil, time, logging, ctypes, re

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QFileDialog, qApp, QAction, QStyle, QWidget
from PyQt5 import QtWidgets, QtCore, QtGui

from ui.mainwindow import Ui_MainWindow
from ui.logs import Ui_Logfile
from bin.einsatz_monitor_modules import init,  close_methode, database_class, gennerate_cookie_module  # init wird benötigt!
from bin.einsatz_monitor_modules.help_settings_methoden import *

# Einstelungen für High Resolution
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons


# Version Nummer wird hier gesetzt:
version_nr = "0.9.5"

# Konfigurationen importieren:
# config = config_class.Config()
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
        icon.addPixmap(QtGui.QPixmap(os.path.join(resources, "fwsignet_100.png")), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.setWindowIcon(icon)
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EM-Statusauswertung")

        # Fwbs Logo einbinden:
        logo_fwbs = QPixmap(resources + "/logo_fwbs.png")
        self.ui.logo_fwbs.setPixmap(logo_fwbs)

        # Version anzeiegn:
        self.ui.label_status_versionnr.setText(version_nr)

        # Hintergrundfarbe der Logs anpassen:
        self.ui.textEdit_log_main.setStyleSheet("background-color: rgb(240, 240,240)")
        self.ui.textEdit_log_vpn.setStyleSheet("background-color: rgb(240, 240,240)")
        self.ui.textEdit_log_crawler.setStyleSheet("background-color: rgb(240, 240,240)")

        # Einstellungen zu Beginn einlesen:
        self.ui.lineEdit_settings_funkrufname.setText(database.select_config("funkrufname"))
        self.ui.lineEdit_settings_token.setText(database.select_config("connect_api_fahrzeuge"))
        self.ui.lineEdit_wachendisplay_contend_id.setText(database.select_config("wachendisplay_content_id"))
        self.ui.lineEdit_settings_wachendisplay_url.setText(database.select_config("url_wachendisplay"))
        self.ui.lineEdit_settings_wachendisplay_user.setText(database.select_config("user_wachendisplay"))
        self.ui.lineEdit_wachendisplay_password.setText(database.select_config("passwort_wachendisplay"))
        self.ui.lineEdit_settings_vpn_user.setText(database.select_config("ovpn_user"))
        self.ui.lineEdit_settings_vpn_password.setText(database.select_config("ovpn_passwort"))
        self.ui.lineEdit_settings_vpn_path_to_exe.setText(database.select_config("path_to_openvpn.exe"))
        self.ui.lineEdit_settings_vpn_config.setText(database.select_config("openvpn_config"))
        self.ui.comboBox_settings_headless_browser.setCurrentText(database.select_config("headless_browser"))
        self.ui.comboBox.setCurrentText(database.select_config("autostart"))
        self.ui.lineEdit_setting_email_user.setText(database.select_config("email_username"))
        self.ui.lineEdit_settings_email_password.setText(database.select_config("email_password"))
        self.ui.lineEdit_setings_email_server.setText(database.select_config("email_server"))
        self.ui.lineEdit_settings_kdo_alarm.setText(database.select_config("kdo_alarm"))
        self.ui.lineEdit_settings_dag_alternative.setText(database.select_config("dag_alternativ"))
        self.ui.lineEdit_settings_path_to_pdftotext.setText(database.select_config("path_to_pdftotext.exe"))
        self.ui.lineEdit_settings_token_test.setText(database.select_config("token_test"))
        self.ui.lineEdit_settings_token_abt1.setText(database.select_config("token_abt1"))
        self.ui.lineEdit_settings_token_abt2.setText(database.select_config("token_abt2"))
        self.ui.lineEdit_settings_token_abt3.setText(database.select_config("token_abt3"))
        self.ui.lineEdit_settings_token_abt4.setText(database.select_config("token_abt4"))
        self.ui.lineEdit_settings_token_abt5.setText(database.select_config("token_abt5"))
        self.ui.lineEdit_settings_token_abt6.setText(database.select_config("token_abt6"))
        self.ui.lineEdit_settings_fahrzeuge_abt2.setText(database.select_config("fahrzeuge_abt2"))
        self.ui.lineEdit_settings_fahrzeuge_abt3.setText(database.select_config("fahrzeuge_abt3"))
        self.ui.lineEdit_settings_fahrzeuge_abt4.setText(database.select_config("fahrzeuge_abt4"))
        self.ui.lineEdit_settings_fahrzeuge_abt5.setText(database.select_config("fahrzeuge_abt5"))
        self.ui.lineEdit_settings_fahrzeuge_abt6.setText(database.select_config("fahrzeuge_abt6"))

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
        start_all = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), '&Alles Starten', self)
        start_all.setShortcut('Ctrl+P')
        start_all.triggered.connect(self.autostart)
        self.ui.menu_bersicht.addAction(start_all)

        # Exit:
        exit_action = QAction(self.style().standardIcon(QStyle.SP_DialogCancelButton), '&Exit', self)
        exit_action.setStatusTip('Exit application')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)
        self.ui.menu_bersicht.addAction(exit_action)

        # Installationsleitung:
        install_help = QAction(self.style().standardIcon(QStyle.SP_MessageBoxQuestion), '&Installationsanleitung', self)
        install_help.triggered.connect(installationsanleitung)
        self.ui.menuHilfe.addAction(install_help)

        # Kontakt:
        contact = QAction(self.style().standardIcon(QStyle.SP_MessageBoxInformation), '&Kontakt', self)
        contact.triggered.connect(kontakt)
        self.ui.menuHilfe.addAction(contact)

        # Buttons auf der Statusseite:
        self.ui.pushButton_start_vpn.pressed.connect(self.start_vpn)
        self.ui.pushButton_start_auswretung.pressed.connect(self.start_status_auswertung)
        self.ui.pushButton_start_einsatzauswertung.pressed.connect(self.start_einsatzauswertung)
        self.ui.pushButton_testmode.pressed.connect(self.activate_testmode)
        self.ui.pushButton_live_mode.pressed.connect(self.autostart)

        # Buttons aus der Einstellungsseite:
        self.ui.pushButton_safe_settings_funkrufname.clicked.connect(self.safe_settings_funkrufname)
        self.ui.pushButton_safe_setting_fahrzeuge.clicked.connect(self.safe_setting_fahrzeuge)
        self.ui.pushButton_safe_settings_token.clicked.connect(self.safe_settings_token)
        self.ui.pushButton_safe_settings_vpn_user.clicked.connect(self.safe_settings_vpn_user)
        self.ui.pushButton_safe_settings_vpn_password.clicked.connect(self.safe_settings_vpn_password)
        self.ui.pushButton_safe_settings_vpn_path_to_exe.clicked.connect(self.safe_settings_vpn_path_to_exe)
        self.ui.pushButton_safe_settings_vpn_config.clicked.connect(self.safe_settings_vpn_config)
        self.ui.pushButton_safe_settings_wachendisplay_url.clicked.connect(self.safe_settings_wachendisplay_url)
        self.ui.pushButton_safe_wachendisplay_contend_id.clicked.connect(self.safe_wachendisplay_contend_id)
        self.ui.pushButton_safe_ettings_wachendisplay_user.clicked.connect(self.safe_settings_wachendisplay_user)
        self.ui.pushButton_safe_wachendisplay_password.clicked.connect(self.safe_wachendisplay_password)
        self.ui.pushButton_safe_headless_browser.clicked.connect(self.safe_headless_browser)
        self.ui.pushButton_safe_autostart.clicked.connect(self.safe_autostart)
        self.ui.pushButton_settings_gennerat_cookie.clicked.connect(self.generate_cookie)
        self.ui.pushButton_settings_safe_email_user.clicked.connect(self.safe_email_user)
        self.ui.pushButton_settings_safe_email_password.clicked.connect(self.safe_email_password)
        self.ui.pushButton_settings_safe_email_server.clicked.connect(self.safe_email_server)
        self.ui.pushButton_settings_safe_kdo_alarm.clicked.connect(self.safe_kdo_ric)
        self.ui.pushButton_settings_safe_dag_alternative.clicked.connect(self.safe_dag_alternativ)
        self.ui.pushButton_settings_safe_pdftotext.clicked.connect(self.safe_pdftotext)
        self.ui.pushButton_safe_settings_token_test.clicked.connect(self.safe_settings_token_test)
        self.ui.pushButton_safe_settings_token_abt1.clicked.connect(self.safe_settings_token_abt1)
        self.ui.pushButton_safe_settings_token_abt2.clicked.connect(self.safe_settings_token_abt2)
        self.ui.pushButton_safe_settings_token_abt3.clicked.connect(self.safe_settings_token_abt3)
        self.ui.pushButton_safe_settings_token_abt4.clicked.connect(self.safe_settings_token_abt4)
        self.ui.pushButton_safe_settings_token_abt5.clicked.connect(self.safe_settings_token_abt5)
        self.ui.pushButton_safe_settings_token_abt6.clicked.connect(self.safe_settings_token_abt6)

        self.ui.pushButton_browse_settings_vpn_path_to_exe.clicked.connect(self.browse_settings_vpn_path_to_exe)
        self.ui.pushButton_browse_settings_vpn_config.clicked.connect(self.browse_settings_vpn_config)
        self.ui.pushButton_settings_browse_pdftotext.clicked.connect(self.browse_pdftotext)

        self.ui.pushButton_help_settings_funkrufname.clicked.connect(help_settings_funkrufname)
        self.ui.pushButton_help_setting_fahrzeuge.clicked.connect(help_setting_fahrzeuge)
        self.ui.pushButton_help_settings_token.clicked.connect(help_settings_token)
        self.ui.pushButton_help_settings_vpn_user.clicked.connect(help_settings_vpn_user)
        self.ui.pushButton_help_settings_vpn_password.clicked.connect(help_settings_vpn_password)
        self.ui.pushButton_help_settings_vpn_path_to_exe.clicked.connect(help_settings_vpn_path_to_exe)
        self.ui.pushButton_help_settings_vpn_config.clicked.connect(help_settings_vpn_config)
        self.ui.pushButton_help_settings_wachendisplay_url.clicked.connect(help_settings_wachendisplay_url)
        self.ui.pushButton_help_wachendisplay_contend_id.clicked.connect(help_wachendisplay_contend_id)
        self.ui.pushButton_help_settings_wachendisplay_user.clicked.connect(help_settings_wachendisplay_user)
        self.ui.pushButton_help_wachendisplay_password.clicked.connect(help_wachendisplay_password)
        self.ui.pushButton_help_autostart.clicked.connect(help_autostart)
        self.ui.pushButton_settings_help_email_user.clicked.connect(help_email_user)
        self.ui.pushButton_settings_help_email_password.clicked.connect(help_email_passwort)
        self.ui.pushButton_settings_help_email_server.clicked.connect(help_email_Server)
        self.ui.pushButton_settings_help_kdo_alarm.clicked.connect(help_kdo_alarm)
        self.ui.pushButton_settings_help_dag_alternative.clicked.connect(help_dag_alternativ)
        self.ui.pushButton_settings_help_pdftotext.clicked.connect(help_pdftotext)
        self.ui.pushButton_5_help_settings_connect_tokens_all.clicked.connect(help_connect_tokens_all)

        # Buttons aus der Logseite:
        self.ui.pushButton_log_reload.clicked.connect(self.log_reload)
        self.ui.pushButton_logs_reset_mainlog.clicked.connect(self.reset_log_main)
        self.ui.pushButton_logs_reset_vpnlog.clicked.connect(self.reset_log_vpn)
        self.ui.pushButton_logs_reset_crawlerlog.clicked.connect(self.reset_log_crawler)
        self.ui.pushButton_logs_reset_emlog.clicked.connect(self.reset_log_em)
        self.ui.pushButton_open_log_main.clicked.connect(self.open_main_log)
        self.ui.pushButton_open_log_crawler.clicked.connect(self.open_crawler_log)
        self.ui.pushButton_open_log_vpn.clicked.connect(self.open_ovpn_log)
        self.ui.pushButton_open_log_em.clicked.connect(self.open_em_log)

    # ####### Methoden auf der Statusseite:
    # Methode, um das OpenVPN modul zu starten,  bzw. zu stoppen, wenn der openvpn Prozess schon ausgeführt wird.
    def start_vpn(self):
        if self.check_prozess("openvpn.exe"):
            # prüfen ob die Auswertung noch läuft:
            if database.select_aktiv_flag("crawler") == 1:
                msg = QMessageBox()
                msg.setWindowTitle("Fehler - Auswertung noch aktiv")
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bitte zuerst die Auswertung beenden!")
                msg.exec_()
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
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Bitte zuerst das VPN starten!")
                msg.exec_()

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
    def safe_settings_funkrufname(self):
        # Funkrufnahme aus Eingabefeld übernehmen:
        set_funkrufname = self.ui.lineEdit_settings_funkrufname.text()
        if re.match("^[A-Z][A-Z]-[A-Z][A-Z]$", set_funkrufname):
            database.update_config("funkrufname", set_funkrufname.strip())
            database.update_config("fw_kurz", set_funkrufname.split("-")[1])
            # Ausgabe anzeigen
            self.safe_success(set_funkrufname)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Fehler - falsche Syntax!")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bitte den Funkrufnamen nach dieser Syntax eingeben: <br><b> FL-BS</b>")
            msg.exec_()

    def safe_setting_fahrzeuge(self):
        # Textinput einlesen
        set_fahrzeuge = str(self.ui.textEdit_fahrzeuge.toMarkdown())

        # string in Liste verwandeln
        fahrzeuge_list = set_fahrzeuge.split("\n\n")
        fahrzeuge_list_clean = [feld.strip() for feld in fahrzeuge_list if feld != '']
        database.safe_status_fahrzeuge(fahrzeuge_list_clean)

        self.safe_success("Fahrzeugliste")

    def safe_settings_token(self):
        set_token = self.ui.lineEdit_settings_token.text()
        database.update_config("connect_api_fahrzeuge", set_token.strip())
        self.safe_success("Token")

    def safe_settings_vpn_user(self):
        set_vpn_user = self.ui.lineEdit_settings_vpn_user.text()
        database.update_config("ovpn_user", set_vpn_user.strip())
        # pass.txt schreiben
        with open(pass_file_vpn, "w", encoding="utf-8") as file:
            file.write(database.select_config("ovpn_user") + "\n" + database.select_config("ovpn_passwort"))
        self.safe_success(set_vpn_user)

    def safe_settings_vpn_password(self):
        set_vpn_password = self.ui.lineEdit_settings_vpn_password.text()
        database.update_config("ovpn_passwort", set_vpn_password.strip())
        # pass.txt schreiben
        with open(pass_file_vpn, "w", encoding="utf-8") as file:
            file.write(database.select_config("ovpn_user") + "\n" + database.select_config("ovpn_passwort"))
        self.safe_success(set_vpn_password)

    def safe_settings_vpn_path_to_exe(self):
        safe_settings_vpn_path_to_exe = self.ui.lineEdit_settings_vpn_path_to_exe.text()
        database.update_config("path_to_openvpn.exe", safe_settings_vpn_path_to_exe)
        self.safe_success(safe_settings_vpn_path_to_exe)

    def safe_settings_vpn_config(self):
        safe_settings_vpn_config_path = self.ui.lineEdit_settings_vpn_config.text()
        if "/" in safe_settings_vpn_config_path:
            # Datei kopieren in Config Folder:
            try:
                shutil.copy2(safe_settings_vpn_config_path, config_path)
                _, filename = os.path.split(safe_settings_vpn_config_path)
                # Text in Zeile anpassen und Json File aktualisieren
                self.ui.lineEdit_settings_vpn_config.setText(filename)
                database.update_config("openvpn_config", filename)
                self.safe_success(filename)

            except:
                msg = QMessageBox()
                msg.setWindowTitle("Fehler")
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Die Einstellung konnte nicht gespeichert werden.")
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Fehler")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Die Einstellung konnte nicht gespeichert werden, da der Eingabetext nicht einem absoluten "
                        "Pfad entspricht.")
            msg.exec_()

    def safe_settings_wachendisplay_url(self):
        safe_settings_wachendisplay_url = self.ui.lineEdit_settings_wachendisplay_url.text()
        if re.match("^http:\/\/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}:[0-9]{1,4}\/$",
                    safe_settings_wachendisplay_url):
            database.update_config("url_wachendisplay", safe_settings_wachendisplay_url.strip())
            self.safe_success(safe_settings_wachendisplay_url)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Fehler - falsche Syntax!")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bitte die URL nach dieser Syntax eingeben: <br><b> http://172.16.24.3:8080/</b>")
            msg.exec_()

    def safe_wachendisplay_contend_id(self):
        safe_settings_wachendisplay_content_id = self.ui.lineEdit_wachendisplay_contend_id.text()
        database.update_config("wachendisplay_content_id", safe_settings_wachendisplay_content_id.strip())
        self.safe_success(safe_settings_wachendisplay_content_id)

    def safe_settings_wachendisplay_user(self):
        safe_settings_wachendisplay_user = self.ui.lineEdit_settings_wachendisplay_user.text()
        database.update_config("user_wachendisplay", safe_settings_wachendisplay_user.strip())
        self.safe_success(safe_settings_wachendisplay_user)

    def safe_wachendisplay_password(self):
        safe_settings_wachendisplay_passwort = self.ui.lineEdit_wachendisplay_password.text()
        database.update_config("passwort_wachendisplay", safe_settings_wachendisplay_passwort.strip())
        self.safe_success(safe_settings_wachendisplay_passwort)

    def safe_headless_browser(self):
        safe_headless_browser = self.ui.comboBox_settings_headless_browser.currentText()
        database.update_config("headless_browser", safe_headless_browser)
        self.safe_success(safe_headless_browser)

    def safe_autostart(self):
        safe_autostart = self.ui.comboBox.currentText()
        database.update_config("autostart", safe_autostart)
        self.safe_success(safe_autostart)

    def safe_email_user(self):
        input_to_safe = self.ui.lineEdit_setting_email_user.text()
        database.update_config("email_username", input_to_safe.strip())
        self.safe_success(input_to_safe)

    def safe_email_password(self):
        input_to_safe = self.ui.lineEdit_settings_email_password.text()
        database.update_config("email_password", input_to_safe.strip())
        self.safe_success(input_to_safe)

    def safe_email_server(self):
        input_to_safe = self.ui.lineEdit_setings_email_server.text()
        # Überprüfen ob die Synthax stimmt.
        if re.match("^[A-Za-z0-9]+\.[A-Za-z0-9]+\.[A-Za-z0-9]{1,4}$",
                    input_to_safe):
            database.update_config("email_server", input_to_safe.strip())
            self.safe_success(input_to_safe)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Fehler - falsche Syntax!")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bitte die Server-URL nach dieser Syntax eingeben, ohne http(s) oder /: <br><b> "
                        "imap.serverdomain.org</b>")
            msg.exec_()

    def safe_kdo_ric(self):
        input_to_safe = self.ui.lineEdit_settings_kdo_alarm.text()
        database.update_config("kdo_alarm", input_to_safe.strip())
        self.safe_success(input_to_safe)

    def safe_dag_alternativ(self):
        input_to_safe = self.ui.lineEdit_settings_dag_alternative.text()
        database.update_config("dag_alternativ", input_to_safe.strip())
        self.safe_success(input_to_safe)

    def safe_pdftotext(self):
        input_to_safe = self.ui.lineEdit_settings_path_to_pdftotext.text()
        database.update_config("path_to_pdftotext.exe", input_to_safe.strip())
        self.safe_success(input_to_safe)

    def safe_settings_token_test(self):
        input_to_safe = self.ui.lineEdit_settings_token_test.text()
        database.update_config("token_test", input_to_safe.strip())
        self.safe_success("")

    def safe_settings_token_abt1(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt1.text()
        database.update_config("token_abt1", input_to_safe.strip())
        self.safe_success("")

    def safe_settings_token_abt2(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt2.text()
        database.update_config("token_abt2", input_to_safe.strip())
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt2.text()
        database.update_config("fahrzeuge_abt2", input_to_safe_fahrzeuge.strip())
        self.safe_success("")

    def safe_settings_token_abt3(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt3.text()
        database.update_config("token_abt3", input_to_safe.strip())
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt3.text()
        database.update_config("fahrzeuge_abt3", input_to_safe_fahrzeuge.strip())
        self.safe_success("")

    def safe_settings_token_abt4(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt4.text()
        database.update_config("token_abt4", input_to_safe.strip())
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt4.text()
        database.update_config("fahrzeuge_abt4", input_to_safe_fahrzeuge.strip())
        self.safe_success("")

    def safe_settings_token_abt5(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt5.text()
        database.update_config("token_abt5", input_to_safe.strip())
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt5.text()
        database.update_config("fahrzeuge_abt5", input_to_safe_fahrzeuge.strip())
        self.safe_success("")

    def safe_settings_token_abt6(self):
        input_to_safe = self.ui.lineEdit_settings_token_abt6.text()
        database.update_config("token_abt6", input_to_safe.strip())
        input_to_safe_fahrzeuge = self.ui.lineEdit_settings_fahrzeuge_abt6.text()
        database.update_config("fahrzeuge_abt6", input_to_safe_fahrzeuge.strip())
        self.safe_success("")

    def browse_settings_vpn_path_to_exe(self):
        # Datei Öffnen Dialog generieren und Rückgabe in das Textfeld setzen
        filepath, _ = QFileDialog.getOpenFileName(self, 'Bitte openvpn.exe auswählen', 'c:\\', "Executables ("
                                                                                               "*.exe)")
        self.ui.lineEdit_settings_vpn_path_to_exe.setText(filepath)

    def browse_settings_vpn_config(self):
        filetype = 'openvpn File(*.ovpn)'
        filepath, _ = QFileDialog.getOpenFileName(self, 'Bitte VPN Config-Datei auswählen', 'c:\\', filter=filetype)
        self.ui.lineEdit_settings_vpn_config.setText(filepath)

    def browse_pdftotext(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Bitte pdftotext.exe auswählen', 'c:\\', "Executables ("
                                                                                               "*.exe)")
        self.ui.lineEdit_settings_path_to_pdftotext.setText(filepath)

    # methode um die Cookies zu gennerieren:
    def generate_cookie(self):
        r = gennerate_cookie_module.get_cookie()
        if r == "fehler vpn":
            msg = QMessageBox()
            msg.setWindowTitle("Fehler - VPN nicht aktiv")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bitte zuerst das VPN starten!")
            msg.exec_()
        elif r == "fehler config":
            msg = QMessageBox()
            msg.setWindowTitle("Fehler - Wachendisplay Configuration nicht erledigt")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Bitte zuerst die Wachendisplay Config durchführen!")
            msg.exec_()
        elif r == "erfolgreich":
            msg = QMessageBox()
            msg.setWindowTitle("Erfolgreich!")
            msg.setIcon(QMessageBox.Information)
            msg.setText("Cookies erfolgreich erstellt!")
            msg.exec_()

        else:
            msg = QMessageBox()
            msg.setWindowTitle("Fehler - Cookie konnte nicht erstellt werden")
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Unbekannter Fehler")
            msg.exec_()

# ##### Methoden auf der Logseite:
    # Methode um die Loganzeige zu reloaden
    def log_reload(self):
        self.read_last_five_lines("logfile_main.txt")
        self.read_last_five_lines("logfile_ovpn.txt")
        self.read_last_five_lines("logfile_crawler.txt")
        self.read_last_five_lines("logfile_EM.txt")

    # methode um letzte 50 Zeilen einzulesen und an Logausgabe zu senden:
    def read_last_five_lines(self, log_file):
        with open(os.path.join(logfile_path, log_file), "r", encoding="utf-8") as file:
            lines = file.readlines()
            last_lines = lines[-50:]
            change_sort = reversed(last_lines)

        if log_file == "logfile_main.txt":
            self.ui.textEdit_log_main.setText(''.join(change_sort))
        elif log_file == "logfile_ovpn.txt":
            self.ui.textEdit_log_vpn.setText(''.join(change_sort))
        elif log_file == "logfile_crawler.txt":
            self.ui.textEdit_log_crawler.setText(''.join(change_sort))
        elif log_file == "logfile_EM.txt":
            self.ui.textEdit_log_EM.setText(''.join(change_sort))

    def read_log(self, logfile):
        with open(os.path.join(logfile_path, logfile), "r", encoding="utf-8") as file:
            lines = file.readlines()
            return ''.join(lines)

    # Methode um die Mainlog zu löschen
    def reset_log_main(self):
        open(os.path.join(logfile_path, "logfile_main.txt"), "w", encoding="utf-8").close()
        self.read_last_five_lines("logfile_main.txt")

    # Methode um die VPNLog zu löschen
    def reset_log_vpn(self):
        open(os.path.join(logfile_path, "logfile_ovpn.txt"), "w", encoding="utf-8").close()
        self.read_last_five_lines("logfile_ovpn.txt")

    # Methode um die Crawlerlog zu löschen
    def reset_log_crawler(self):
        open(os.path.join(logfile_path,  "logfile_crawler.txt"), "w", encoding="utf-8").close()
        self.read_last_five_lines("logfile_crawler.txt")

    # Methode um die EMlog zu löschen:
    def reset_log_em(self):
        open(os.path.join(logfile_path,  "logfile_EM.txt"), "w", encoding="utf-8").close()
        self.read_last_five_lines("logfile_EM.txt")

    # Methode um die Main-Log in neuem Fenster zu laden:
    def open_main_log(self):
        self.window = AnotherWindow()
        self.window.show()
        self.window.setWindowTitle("Logfile: Mainlog")
        self.window.ui.textEdit.setText(self.read_log("logfile_main.txt"))


    # Methode um die Crawler-Log in neuem Fenster zu laden:
    def open_crawler_log(self):
        self.window = AnotherWindow()
        self.window.show()
        self.window.setWindowTitle("Logfile: Crawler/Wachendisplay")
        self.window.ui.textEdit.setText(self.read_log("logfile_crawler.txt"))

    # Methode um die VPN-Log in neuem Fenster zu laden:
    def open_ovpn_log(self):
        self.window = AnotherWindow()
        self.window.show()
        self.window.setWindowTitle("Logfile: OpenVPN")
        self.window.ui.textEdit.setText(self.read_log("logfile_ovpn.txt"))

    # Methode um die EM-Log in neuem Fenster zu laden:
    def open_em_log(self):
        self.window = AnotherWindow()
        self.window.show()
        self.window.setWindowTitle("Logfile: Einsatzauswertung")
        self.window.ui.textEdit.setText(self.read_log("logfile_EM.txt"))

# ####### Sonstige Methoden:

    # Methode im zu prüfen, ob ein bestimmter Prozess ausgeführt wird. Return: True/False
    def check_prozess(self, prozessname):
        for proc in psutil.process_iter():
            if proc.name() == prozessname:
                return True

    # Methode zur Textausgabe, dass die Speicherung erfolgreich war:
    def safe_success(self, einstellung):
        msg = QMessageBox()
        msg.setWindowTitle("Erfolgreich gespeichert")
        msg.setIcon(QMessageBox.Information)
        msg.setText("Die Einstellung " + einstellung + "  wurde erfolgreich gespeichert!")

        msg.exec_()

    # Methode um einen bestimmten Button auf Grün zu wechseln
    def set_led_green(self, button):
        button_online = QPixmap(resources + "/green-led-on_small.png")
        button.setPixmap(button_online)

    # Methode um einen bestimmten Button auf Rot zu wechseln
    def set_led_red(self, button):
        button_offline = QPixmap(resources + "/led-red-on_small.png")
        button.setPixmap(button_offline)

    # Methode um einen bestimmten Button auf Achtung zu wechseln
    def set_led_attention(self, button):
        button_attention = QPixmap(resources + "/attention_small.png")
        button.setPixmap(button_attention)

    # Methode um die Error-Datenbank auszulesen und die statusanzeigen zu aktualisieren, bzw. einen Neustart zu gennerieren:
    def monitoring(self):
        try:
            if database.select_error("vpn") == 0:
                self.set_led_green(self.ui.status_vpn)
            else:
                self.set_led_red(self.ui.status_vpn)

            if database.select_error("wachendisplay") == 0:
                self.set_led_green(self.ui.status_Wachendisplay)
            else:
                self.set_led_red(self.ui.status_Wachendisplay)

            if database.select_error("statusauswertung") == 0:
                self.set_led_green(self.ui.status_auswertung)
            else:
                self.set_led_red(self.ui.status_auswertung)

            if database.select_error("alarm_server") == 0:
                self.set_led_green(self.ui.status_server)
            else:
                self.set_led_red(self.ui.status_server)

            if database.select_error("testmode") == 1:
                self.set_led_attention(self.ui.status_testmodus)
            else:
                self.set_led_red(self.ui.status_testmodus)

            if database.select_error("alarm_auswertung") == 0:
                self.set_led_green(self.ui.status_alarmscript)
            elif database.select_error("alarm_auswertung") == 2:
                database.update_aktiv_flag("auswertung", "1")
                time.sleep(3)
                self.start_einsatzauswertung()
                time.sleep(5)
                database.update_aktiv_flag("auswertung", "0")
                self.start_einsatzauswertung()
            else:
                self.set_led_red(self.ui.status_alarmscript)
        except:
            logger.exception("Fehler bei der Monitoring Aktualisierung der Datenbank")

    # Methode Autostart
    def autostart(self):
        self.start_vpn()
        time.sleep(30)
        self.start_einsatzauswertung()
        time.sleep(30)
        self.start_status_auswertung()
        logging.info("Autostart durchgeführt")


# Logs anzeigen lassen:

class AnotherWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.ui = Ui_Logfile()
        self.ui.setupUi(self)

window = MainWindow()
window.show()
sys.exit(app.exec_())
