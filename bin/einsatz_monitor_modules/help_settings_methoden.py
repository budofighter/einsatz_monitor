# hier sind alle Help-Boxen aus den Einstellungen zu finden
from PyQt5.QtWidgets import QMessageBox


def help_settings_funkrufname():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Funkrufname")
    msg.setInformativeText("Syntax des <u>Funkrufnahmens</u> bitte folgendermaßen angeben: z.b. <b>\"FW-BS\"</b>")
    msg.setDetailedText("Der Präfix des Funkrufnahmens wird für die Auswertung des Wachendisplays benötigt. "
                        "\nBitte gebe den Funkrufnahmen an, wie er im Wachendisplay hinterlegt ist.")
    msg.exec_()


def help_setting_fahrzeuge():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Fahrzeugliste")
    msg.setInformativeText("Alle <u>Fahrzeuge</u> eintragen nach Format <br> z.b. <b>FL BS 2/10</b></br> oder "
                           "<b>1/19/1</b>. <br>Ein Fahrzeug je Zeile!</br>")
    msg.setDetailedText("Bitte ALLE Fahrzeuge aus dem Wachendisplay angeben, welche aufgeführt sind und der "
                        "entsprechenden Syntax entsprechen. \nBei fehlenden Fahrzeugen, kommt es zu einem "
                        "Fehler!")
    msg.exec_()


def help_settings_token():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Connect Token")
    msg.setInformativeText("Bitte den <b>Token</b> der öffentlichen Connect API (Organisation) eintragen.")
    msg.setDetailedText("Der Token wird benötigt, um ein Update der Fahrzeugstatus an das Connect Portal zu "
                        "senden. \nDer Token ist zu finden unter \nhttps://connect.feuersoftware.com/ \n  --> "
                        "Organisationsebene \n    --> Schnittstellen \n      --> Öffentliche Connect Schnittstelle")
    msg.exec_()


def help_settings_vpn_user():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: OpenVPN User")
    msg.setInformativeText("Bitte den <b>Benutzernamen</b> des VPN-Zugangs zum Wachendisplay eingeben")
    msg.setDetailedText("Der Benutzername wird von der ILS vergeben und zur Verfügung gestellt. \n"
                        "Zusammen mit dem SOPHOS VPN Client und dem Passwort, stellt dies der sichere Zugang"
                        " zum Netzwerk der Leitstelle dar.")
    msg.exec_()


def help_settings_vpn_password():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: OpenVPN Passwort")
    msg.setInformativeText("Bitte das <b>Passwort</b> des VPN-Zugangs zum Wachendisplay eingeben")
    msg.setDetailedText("Der Benutzername wird von der ILS vergeben und zur Verfügung gestellt. \n"
                        "Zusammen mit dem SOPHOS VPN Client und dem Benutzernamen, stellt dies der sichere Zugang"
                        " zum Netzwerk der Leitstelle dar.")
    msg.exec_()


def help_settings_vpn_path_to_exe():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: OpenVPN Programm")
    msg.setInformativeText("Bitte den <b>Pfad</b> zur openvpn.exe angeben, welcher von der Leitstelle zur "
                           "Verfügung gestellt wird.")
    msg.setDetailedText("Der Standardpfad ist:\n C:\\Program Files (x86)\\Sophos\\Sophos SSL VPN "
                        "Client\\bin\\openvpn.exe \nZusammen mit den Zugangsdaten wird mit diesem Programm das "
                        "sichere VPN aufgebaut. Die Installationsdatei wird von der ILS zusammen mit den "
                        "Zugangsdaten zur Verfügung gestellt.")
    msg.exec_()


def help_settings_vpn_config():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: OpenVPN Config")
    msg.setInformativeText("Bitte den Pfad zur <b>*.ovpn</b> Datei angeben, welcher von der Leitstelle zur "
                           "Verfügung gestellt wird. <br><b> Bitte Details beachten! Anpassung nötig </b></br>")
    msg.setDetailedText("Die Konfigurationsdatei für die VPN Verbindung wird von der ILS zur Verfügung gestellt. "
                        "\nVor Verwendung muss diese zwingend angepasst werden: \nDie Datei mit einem normalen "
                        "Texteditor bearbeiten und vor der Zeile \"<ca>\" die Zeile: \n \"auth-user-pass "
                        "./config/pass_ovpn_wachendisplay.txt\" \neinfügen und als Kopie speichern. \nBenötigt "
                        "wird der Pfad zur bearbeiteten Kopie.  ")
    msg.exec_()


def help_wachendisplay_contend_id():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Wachendisplay ContentID")
    msg.setInformativeText(
        "Bitte die <b>ContentID</b> der Ruhedarstellung im Wachendisplay eingeben. <br><b> Details beachten!</b></br>")
    msg.setDetailedText("Die ContentID kann auf dem Wachendisplay mit jedem gängigen Internetprogramm gefunden "
                        "werden. Am Beispiel Chrome z.b.: \nRechtsklick auf die Seite des Wachendisplays \n--> "
                        "Untersuchen\n-->CTRL+SHIFT+C \n--> mit dem Courser dei große Übersichtstabelle markieren "
                        "und nach dem entsprechenden Eintrag suchen. \nz.B.: <div id=\"Feuerwehr Bad "
                        "Säckingen\"\neingegeben werden muss in diesem Fall nur Feuerwehr Bad Säckingen")
    msg.exec_()


def help_settings_wachendisplay_url():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Wachendisplay URL")
    msg.setInformativeText("Bitte die <b>URL</b> des Wachendisplay eingeben")
    msg.setDetailedText("Die URL wird von der ILS Verfügung gestellt. z.B.:\nhttp://172.16.24.3:8080/")
    msg.exec_()


def help_settings_wachendisplay_user():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Wachendisplay User")
    msg.setInformativeText("Bitte den <b>Benutzernamen</b> des Wachendisplay eingeben")
    msg.setDetailedText("Der Benutzername wird von der ILS vergeben und zur Verfügung gestellt.")
    msg.exec_()


def help_wachendisplay_password():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Wachendisplay Passwort")
    msg.setInformativeText("Bitte das <b>Passwort</b> des Wachendisplay eingeben")
    msg.setDetailedText("Das Passwort wird von der ILS vergeben und zur Verfügung gestellt.")
    msg.exec_()

def help_email_user():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: E-Mail Benutzer")
    msg.setInformativeText("Bitte den Benutzernamen des E-Mail Postfaches eingeben.")
    msg.exec_()

def help_email_passwort():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: E-Mail Passwort")
    msg.setInformativeText("Bitte das Passwort des E-Mail Postfaches eingeben.")
    msg.exec_()

def help_email_Server():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: E-Mail Server")
    msg.setInformativeText("Bitte den IMAP-Server des E-Mail Postfaches eingeben.")
    msg.setDetailedText("Der Servername muss analog dieser Synthax definiert werden: z.b. imap.server.de ")
    msg.exec_()

def help_kdo_alarm():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: KDO-Alarm")
    msg.setInformativeText("Falls auf dem Alarmfax der Leistelle das Kommando min einem alternativen RIC alarmiert "
                           "wird, kann dieser hier eingegeben werden.")
    msg.setDetailedText("Auf dem Alarmfax der Leitstelle wird der Kommando Ric als eigenstänige Einsatzmaßnahme "
                        "alarmiert: z.b. <b> KDO-BadSäckingen-DAG \nIn diesem Beispiel kann als eindeutige "
                        "Zuordnung ein Teilstring KDO-Bad hinzugefügt werden.")
    msg.exec_()

def help_dag_alternativ():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: DAG-Alternative")
    msg.setInformativeText("Falls eine zusätzliche Identifikation einer DAG-Einsatzmaßnahme nötig sein, kann diese "
                           "hier angegeben werden.")
    msg.setDetailedText("Also Beispiel wird nicht FL-BS 2/40-DAG alarmiert, sonder beim Kleinalarm FL-BS 2/40-KLEIN. "
                        "In diesem Beispiel muss KLEIN als DAG-Alternative abgespeichert werden.")
    msg.exec_()

def help_pdftotext():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Pfad zu pdftotext.exe")
    msg.setInformativeText("Bitte die pdftotext.exe Datei auswählen")
    msg.setDetailedText("Dieses Programm wird benötigt, um die PDF Dateien in Text umzuwandeln. Bitte hier downloaden "
                        "und den Pfad einstellen: https://www.xpdfreader.com/download")
    msg.exec_()

def help_connect_tokens_all():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Tokens")
    msg.setInformativeText("Details beachten!!! <br> Synthax Fahrzuge: <b>z.b. 2/40;2/42 </br>")
    msg.setDetailedText("Test-API: \nDieser Token wird benötigt, wenn im Testmodus eine separate Fake-Abteilung "
                        "alarmiert werden soll (für Debug-Massnahmen). \n\nAbteilung 1-4:\nHier werden jeweils die "
                        "Connect API-Tokens der jeweiligen Abteilungen eingetragen. Zu finden unter: "
                        "\nhttps://connect.feuersoftware.com/ \n  --> jeweilige Abteilung \n    --> Schnittstellen \n "
                        "     --> Öffentliche Connect Schnittstelle \n\num eine Auswahl zu treffen, wann welche "
                        "Abteilung alarmiert werden soll, kann bei den Nebenabteilungen die jeweiligen Funkrufnahmen "
                        "eingetragen werden. \nSobald bei einem Alarm ein solcher Funkrufnahme alarmiert ist, "
                        "wird die zugehörige Abteilung mitalarmiert. \nBitte die Funkrufnahmen mit ; trennen: z.B. "
                        "2/40;2/42")
    msg.exec_()


def help_autostart():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Einstellung: Autostart")
    msg.setInformativeText("Bei <b> Ja</b> wird bei Programmstart alle Subprozesse automatisch gestartet")
    msg.exec_()

def kontakt():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Kontakt")
    msg.setText('Bei Fragen, Problemen oder Feedback, bitte per E-Mail an <a href= '
                '"mailto:public@cm-siebold.de">public@cm-siebold.de</a> wenden')
    msg.exec_()

def installationsanleitung():
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle("Installationsanleitung")
    msg.setText('Die Installationsanleitung ist zu finden unter: <br><a '
                'href="https://github.com/budofighter/EM_Statusplugin.git">Github</a>')
    msg.exec_()