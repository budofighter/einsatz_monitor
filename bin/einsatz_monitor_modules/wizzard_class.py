import sys, os, shutil

from PyQt6.QtWidgets import QApplication, QWizard, QWizardPage, QLabel, QLineEdit, QTextEdit, QComboBox, QGridLayout, QMessageBox, QPushButton, QFileDialog
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from .validation_utils import validate_input
from . import database_class, gennerate_cookie_module

database = database_class.Database()

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..", "..")

config_path = os.path.join(basedir, "config")

class MyWizardPage(QWizardPage):
    def __init__(self, title, label_text, input_type='line_edit', setting=None):
        super(MyWizardPage, self).__init__()
        self.setTitle(title)
        
        
        layout = QGridLayout(self)
        
        label = QLabel(label_text)
        label.setWordWrap(True)  # Ermöglicht den Zeilenumbruch
        self.setting = setting
        
        self.input_field = None
        self.input_field2 = None  # Initialisieren Sie diese Variable
        
        if input_type == 'line_edit':
            self.input_field = QLineEdit()
        elif input_type == 'text_edit':
            self.input_field = QTextEdit()
        elif input_type == 'cookie':
            self.input_field = QPushButton("Cookies jetzt generieren")
            self.input_field.clicked.connect(self.handle_cookie_button_click)
        elif input_type == 'combo_box':
            self.input_field = QComboBox()
            self.input_field.addItem("Nein")
            self.input_field.addItem("Ja")
        elif input_type == 'none':
            self.input_field = None  # Kein Eingabefeld für diese Seite
        elif input_type == 'vpn_config':
            self.input_field = QLineEdit()
            self.input_field2 = QPushButton(".ovpn Datei auswählen")
            self.input_field2.clicked.connect(self.browse_settings_vpn_config)
        elif input_type == "vpn_start":
            self.input_field = QPushButton("VPN jetzt starten")
            self.input_field.clicked.connect(self.vpn_start)
        
        layout.addWidget(label, 0, 0)  # das ist der Text
        if self.input_field is not None:
            layout.addWidget(self.input_field, 1, 0)
        if self.input_field2 is not None:
            layout.addWidget(self.input_field2, 2, 0)

    # Methode, cookies setzen (für den Button)
    def handle_cookie_button_click(self):
        #gennerate_cookie_module.get_cookie()
        print("Cookies werden gemacht")

    # Methode, cookies setzen (für den Button)
    def browse_settings_vpn_config(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Öffne Datei', '', 'All files ()')
        if filepath:
            self.input_field.setText(filepath)

    def vpn_start(self):
        print("VPN starten")


class MyWizard(QWizard):
    def __init__(self, parent=None):
        super(MyWizard, self).__init__(parent)

        self.skip_validation = False  # Zustandsvariable für Skip Button hinzufügen
        
        self.logo_label = QLabel(self)
        pixmap = QPixmap(os.path.join(basedir, "resources/fwsignet.ico"))
        scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(scaled_pixmap)
        self.update_logo_position()

        self.setOption(QWizard.WizardOption.HaveCustomButton1, True)
        self.setButtonText(QWizard.WizardButton.CustomButton1, "Überspringen")
        self.currentIdChanged.connect(self.handle_current_id_changed)

        self.button(QWizard.WizardButton.NextButton).clicked.connect(self.next_button_clicked)
        self.button(QWizard.WizardButton.FinishButton).clicked.connect(self.finish_button_clicked)
        self.button(QWizard.WizardButton.CancelButton).clicked.connect(self.cancel_button_clicked)
        self.button(QWizard.WizardButton.CustomButton1).clicked.connect(self.skip_button_clicked)        
        
        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br> Allgemein Informationen", 
            ("Sie werden nun schrittweise durch alle Einstellungen des EInsatz Handlers geführt. Bitte nehmen Sie sich die Zeit, diese Ersteinrichtung vollständig durchzuführen. <br> Wenn SIe eine Information erst später hinzufügen wollen, können Sie den Punkt überspringen. <br> Alle Einstellungen können später manuell korrigiert oder angepasst werden."),
            "none"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br> Allgemein Einstellungen - Funkrufname", 
            ("Syntax des <u>Funkrufnahmens</u> bitte folgendermaßen angeben: z.B. <b>FW-BS</b>.<br>"
            "Der Präfix des Funkrufnahmens wird für die Auswertung des Wachendisplays benötigt.<br>"
            "Bitte geben Sie den Funkrufnamen so an, wie er im Wachendisplay hinterlegt ist.<br>"), 
            "line_edit", 
            "funkrufname"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Allgemein Einstellungen - Fahrzeuge", 
            ("Alle <u>Fahrzeuge</u> eintragen nach Format:<br>"
            "z.B. <b>FL BS 2/10</b> oder <b>1/19/1</b>.<br>"
            "Ein Fahrzeug je Zeile!<br>"
            "Bitte ALLE Fahrzeuge aus dem Wachendisplay angeben, welche aufgeführt sind und der entsprechenden Syntax entsprechen.<br>"
            "Bei fehlenden Fahrzeugen kommt es zu einem Fehler!<br>"), 
            'text_edit', 
            "fahrzeuge"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Allgemein Einstellungen - Autostart", 
            ("Bei <b>Ja</b> werden bei Programmstart alle Subprozesse automatisch gestartet.<br>"), 
            'combo_box',
            "autostart"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>OpenVPN - Benutzer", 
            ("Bitte den <b>Benutzernamen</b> des VPN-Zugangs zum Wachendisplay eingeben. "
            "Der Benutzername wird von der ILS vergeben und zur Verfügung gestellt.<br>"
            "Zusammen mit dem SOPHOS VPN Client und dem Passwort stellt dies den sicheren Zugang zum Netzwerk der Leitstelle dar.<br>"), 
            "line_edit",
            "ovpn_user"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>OpenVPN - Passwort", 
            ("Bitte das <b>Passwort</b> des VPN-Zugangs zum Wachendisplay eingeben. "
            "Der Benutzername wird von der ILS vergeben und zur Verfügung gestellt.<br>"
            "Zusammen mit dem SOPHOS VPN Client und dem Benutzernamen stellt dies den sicheren Zugang zum Netzwerk der Leitstelle dar.<br>"), 
            "line_edit",
            "ovpn_passwort"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>OpenVPN - Pfad zur Config", 
            ("Bitte den Pfad zur <b>*.ovpn</b> Datei angeben, welcher von der Leitstelle zur Verfügung gestellt wird. "
            "<b>Bitte Details beachten! Anpassung nötig</b><br>"
            "Die Konfigurationsdatei für die VPN Verbindung wird von der ILS zur Verfügung gestellt.<br>"
            "Vor Verwendung muss diese zwingend angepasst werden:<br>"
            "Die Datei mit einem normalen Texteditor bearbeiten und vor der Zeile &lt;ca&gt; die Zeile:<br>"
            "<i>auth-user-pass ./config/pass_ovpn_wachendisplay.txt</i><br>"
            "einfügen und als Kopie speichern.<br>"
            "Benötigt wird der Pfad zur bearbeiteten Kopie.<br>"), 
            "vpn_config",
            "openvpn_config"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br> VPN Starten", 
            ("Um die VPN-Einstellungen zu testen und die weitere Konfiguration durchzuführen, muss eine VPN Verbindung zum Wachendisplay hergestellt werden."),
             "vpn_start",
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Wachendisplay - URL", 
            ("Bitte die <b>URL</b> des Wachendisplay eingeben. "
            "Die URL wird von der ILS zur Verfügung gestellt. z.B.:<br>"
            "<i>http://172.16.24.3:8080/</i><br>"), 
            "line_edit",
            "url_wachendisplay"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Wachendisplay - ContentID", 
            ("Bitte die <b>ContentID</b> der Ruhedarstellung im Wachendisplay eingeben. "
            "<b>Details beachten!</b><br>"
            "Die ContentID kann auf dem Wachendisplay mit jedem gängigen Internetprogramm gefunden werden. "
            "Am Beispiel Chrome z.B.:<br>"
            "Rechtsklick auf die Seite des Wachendisplays &rarr; Untersuchen &rarr; CTRL+SHIFT+C &rarr; "
            "mit dem Cursor die große Übersichtstabelle markieren und nach dem entsprechenden Eintrag suchen.<br>"
            "z.B.: <i>&lt;div id=\"Feuerwehr Bad Säckingen\"&gt;</i><br>"
            "Eingegeben werden muss in diesem Fall nur <i>Feuerwehr Bad Säckingen</i><br>"), 
            "line_edit",
            "wachendisplay_content_id"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Wachendisplay - Benutzer", 
            ("Bitte den <b>Benutzernamen</b> des Wachendisplay eingeben. "
            "Der Benutzername wird von der ILS vergeben und zur Verfügung gestellt.<br>"), 
            "line_edit",
            "user_wachendisplay"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Wachendisplay - Passwort", 
            ("Bitte das <b>Passwort</b> des Wachendisplay eingeben. "
            "Das Passwort wird von der ILS vergeben und zur Verfügung gestellt.<br>"), 
            "line_edit",
            "passwort_wachendisplay"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Wachendisplay - Headless", 
            ("Bei <b>Nein</b> wird der Browser des Wachendisplays angezeigt.<br> "
            "Bei Ja läuft dieser im Hintergrund."), 
            'combo_box',
            "headless_browser"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Wachendisplay - Cookies generieren", 
            ("Möchten Sie jetzt mit Ihren Zugangsdaten die Cookies generieren?<br>"), 
            'cookie',
            None
            # achtung - Einstelung fehlt noch!
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>E-Mail Einstellungen - Server", 
            ("Bitte den <b>IMAP-Server</b> des E-Mail Postfaches eingeben. "
            "Der Servername muss analog dieser Syntax definiert werden: z.B. <i>imap.server.de</i><br>"), 
            "line_edit",
            "email_server"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>E-Mail Einstellungen - Benutzername", 
            ("Bitte den <b>IMAP-Benutzername</b> des E-Mail Postfaches eingeben. <br>"), 
            "line_edit",
            "email_username"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>E-Mail Einstellungen - Passwort", 
            ("Bitte den <b>IMAP-Passwort</b> des E-Mail Postfaches eingeben. <br>"), 
            "line_edit",
            "email_password"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>E-Mail Einstellungen - KDO-Alarm RIC", 
            ("Falls auf dem Alarmfax der Leitstelle das Kommando mit einem alternativen <b>RIC</b> alarmiert wird, "
            "kann dieser hier eingegeben werden. Auf dem Alarmfax der Leitstelle wird der Kommando Ric als "
            "eigenständige Einsatzmaßnahme alarmiert: z.B. <b>KDO-BadSäckingen</b>-DAG.<br>"
            "In diesem Beispiel kann als eindeutige Zuordnung ein Teilstring <i>KDO-Bad</i> hinzugefügt werden (ohne DAG angeben!).<br>"), 
            "line_edit",
            "kdo_alarm"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>E-Mail Einstellungen - DAG-Alternative", 
            ("Falls eine zusätzliche Identifikation einer <b>DAG-Einsatzmaßnahme</b> nötig sein sollte, "
            "kann diese hier angegeben werden. Als Beispiel wird nicht <i>FL-BS 2/40-DAG</i> alarmiert, "
            "sondern beim Kleinalarm <i>FL-BS 2/40-KLEIN</i>.<br>"
            "In diesem Beispiel muss <i>KLEIN</i> als DAG-Alternative abgespeichert werden.<br>"),
            "line_edit",
            "dag_alternativ"
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Token Einstellungen - Organisations-API", 
            ("Bitte den <b>Token</b> der öffentlichen Connect API (Organisation) eintragen. "
            "Der Token wird benötigt, um ein Update der Fahrzeugstatus an das Connect Portal zu senden. "
            "\nDer Token ist zu finden unter: \n"
            "https://connect.feuersoftware.com/ \n"
            "  --> Organisationsebene \n"
            "    --> Schnittstellen \n"
            "      --> Öffentliche Connect Schnittstelle<br>"),
            "line_edit",
            None
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Token Einstellungen - Test-API", 
            "Hier den Token einer Test-Abteilung hinzufügen, mit welcher man im Testmodus Probleme suchen und beheben kann.<br>",
            "line_edit",
            None
        ))

        self.addPage(MyWizardPage(
            "Einrichtungsassistent <br>Token Einstellungen - Abteilung 1", 
            "Hier den Token der Abteilungs API der Hauptabteilung eintragen. Diese wird immer alarmiert.<br>",
            "line_edit",
            None
        ))



    def next_button_clicked(self):
        self.skip_validation = False  # Zustand zurücksetzen

    def validateCurrentPage(self):
        if self.skip_validation:  # Überprüfen, ob die Validierung übersprungen werden soll
            self.skip_validation = False  # Zustand zurücksetzen
            return True  # Erlaubt den Übergang zur nächsten Seite

        current_page = self.currentPage()
        setting = current_page.setting  # Auslesen der Einstellung der aktuellen Seite

        eingabewert = None  # Initialisieren der Variable

        if current_page.input_field is not None:
            if isinstance(current_page.input_field, QLineEdit):
                eingabewert = current_page.input_field.text()
            elif isinstance(current_page.input_field, QTextEdit):
                eingabewert = current_page.input_field.toPlainText()
            elif isinstance(current_page.input_field, QComboBox):
                eingabewert = current_page.input_field.currentText()

            # Überprüfen, ob die Eingabe leer ist
            if not eingabewert.strip():  # `.strip()` entfernt Leerzeichen am Anfang und am Ende
            
                # Warnmeldung anzeigen
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Eingabe darf nicht leer sein.")
                msg.setWindowTitle("Warnung")
                msg.exec()
                
                return False  # Verhindert den Übergang zur nächsten Seite

            # Überprüfen, ob die Eingabe gültig ist
            if not validate_input(eingabewert, setting):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setText("Ungültige Eingabe.")
                msg.setWindowTitle("Warnung")
                msg.exec()
                
                return False  # Verhindert den Übergang zur nächsten Seite


            if setting:  # Überprüfen, ob eine Einstellung für diese Seite definiert ist
                if setting == "openvpn_config":
                    _, filename = os.path.split(eingabewert)
                    shutil.copy2(eingabewert, config_path)
                    database.update_config("openvpn_config", filename)

                elif setting == "fahrzeuge":
                    fahrzeuge_list = eingabewert.split("\n")
                    fahrzeuge_list_clean = [feld.strip() for feld in fahrzeuge_list if feld != '']
                    print(fahrzeuge_list_clean)
                    r = database.save_status_fahrzeuge(fahrzeuge_list_clean)
                    print(r)
                elif setting == "":
                    pass
                else:
                    database.update_config(setting, eingabewert)  # Aktualisieren der Datenbank
                    print(f"{setting} , {eingabewert}")

        return True  # Erlaubt den Übergang zur nächsten Seite


    def finish_button_clicked(self):
        self.skip_validation = True  # Zustand setzen

    def skip_button_clicked(self):
        self.skip_validation = True  # Zustand setzen
        self.next()
        
    def cancel_button_clicked(self):
        pass

    def resizeEvent(self, event):
        self.update_logo_position()
        super(MyWizard, self).resizeEvent(event)

    def update_logo_position(self):
        window_width = self.width()
        logo_width = self.logo_label.width()
        
        # Positionieren Sie das Logo 20 Pixel vom rechten Rand entfernt
        new_logo_x = window_width - logo_width - 20
        self.logo_label.move(new_logo_x, 30)  # Die Y-Position bleibt unverändert

    #Methode um den Costum Button auf bestimmten Seiten anzuzeigen:
    def handle_current_id_changed(self, id):
        custom_button = self.button(QWizard.WizardButton.CustomButton1)
        custom_button.show()
 #       if id == 2:  # Die ID der Seite, auf der der Button angezeigt werden soll
 #       if id:
 #           custom_button.show()
 #       else:
 #           custom_button.hide()


if __name__ == '__main__':
    app = QApplication([])
    wizard = MyWizard()
    wizard.show()
    
    app.exec()
