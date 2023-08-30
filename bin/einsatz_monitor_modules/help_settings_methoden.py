# Optimiert 31.03.23
# hier sind alle Help-Boxen aus den Einstellungen zu finden
from PyQt6.QtWidgets import QMessageBox


def create_message_box(title, informative_text, detailed_text=None):
    msg = QMessageBox()
    msg.setStyleSheet("QLabel{min-width: 500px;}")
    msg.setWindowTitle(title)
    msg.setInformativeText(informative_text)

    if detailed_text:
        msg.setDetailedText(detailed_text)

    msg.exec()

def help_settings_funkrufname():
    create_message_box(
        "Einstellung: Funkrufname",
        "Syntax des <u>Funkrufnahmens</u> bitte folgendermaßen angeben: z.b. <b>\"FW-BS\"</b>",
        "Der Präfix des Funkrufnahmens wird für die Auswertung des Wachendisplays benötigt. "
        "\nBitte gebe den Funkrufnahmen an, wie er im Wachendisplay hinterlegt ist."
    )


def help_setting_fahrzeuge():
    create_message_box(
        "Einstellung: Fahrzeugliste",
        "Alle <u>Fahrzeuge</u> eintragen nach Format <br> z.b. <b>FL BS 2/10</b></br> oder "
                           "<b>1/19/1</b>. <br>Ein Fahrzeug je Zeile!</br>",
        "Bitte ALLE Fahrzeuge aus dem Wachendisplay angeben, welche aufgeführt sind und der "
                        "entsprechenden Syntax entsprechen. \nBei fehlenden Fahrzeugen, kommt es zu einem "
                        "Fehler!"
    )


def help_settings_token():
    create_message_box(
        "Einstellung: Connect Token",
        "Bitte den <b>Token</b> der öffentlichen Connect API (Organisation) eintragen.",
        "Der Token wird benötigt, um ein Update der Fahrzeugstatus an das Connect Portal zu "
                            "senden. \nDer Token ist zu finden unter \nhttps://connect.feuersoftware.com/ \n  --> "
                            "Organisationsebene \n    --> Schnittstellen \n      --> Öffentliche Connect Schnittstelle"
    )


def help_settings_vpn_user():
    create_message_box(
        "Einstellung: OpenVPN User",
        "Bitte den <b>Benutzernamen</b> des VPN-Zugangs zum Wachendisplay eingeben",
        "Der Benutzername wird von der ILS vergeben und zur Verfügung gestellt. \n"
                            "Zusammen mit dem SOPHOS VPN Client und dem Passwort, stellt dies der sichere Zugang"
                            " zum Netzwerk der Leitstelle dar."
    )


def help_settings_vpn_password():
    create_message_box(
        "Einstellung: OpenVPN Passwort",
        "Bitte das <b>Passwort</b> des VPN-Zugangs zum Wachendisplay eingeben",
        "Der Benutzername wird von der ILS vergeben und zur Verfügung gestellt. \n"
                            "Zusammen mit dem SOPHOS VPN Client und dem Benutzernamen, stellt dies der sichere Zugang"
                            " zum Netzwerk der Leitstelle dar."
    )


#def help_settings_vpn_path_to_exe():
#    create_message_box(
#        "Einstellung: OpenVPN Programm",
#        "Bitte den <b>Pfad</b> zur openvpn.exe angeben, welcher von der Leitstelle zur "
#                               "Verfügung gestellt wird.",
#        "Der Standardpfad ist:\n C:\\Program Files (x86)\\Sophos\\Sophos SSL VPN "
#                            "Client\\bin\\openvpn.exe \nZusammen mit den Zugangsdaten wird mit diesem Programm das "
#                            "sichere VPN aufgebaut. Die Installationsdatei wird von der ILS zusammen mit den "
#                            "Zugangsdaten zur Verfügung gestellt."
#    )


def help_settings_vpn_config():
    create_message_box(
        "Einstellung: OpenVPN Config",
        "Bitte den Pfad zur <b>*.ovpn</b> Datei angeben, welcher von der Leitstelle zur "
                               "Verfügung gestellt wird. <br><b> Bitte Details beachten! Anpassung nötig </b></br>",
        "Die Konfigurationsdatei für die VPN Verbindung wird von der ILS zur Verfügung gestellt. "
                            "\nVor Verwendung muss diese zwingend angepasst werden: \nDie Datei mit einem normalen "
                            "Texteditor bearbeiten und vor der Zeile \"<ca>\" die Zeile: \n \"auth-user-pass "
                            "./config/pass_ovpn_wachendisplay.txt\" \neinfügen und als Kopie speichern. \nBenötigt "
                            "wird der Pfad zur bearbeiteten Kopie.  "
    )


def help_wachendisplay_contend_id():
    create_message_box(
        "Einstellung: Wachendisplay ContentID",
        "Bitte die <b>ContentID</b> der Ruhedarstellung im Wachendisplay eingeben. <br><b> Details beachten!</b></br>",
        "Die ContentID kann auf dem Wachendisplay mit jedem gängigen Internetprogramm gefunden "
                            "werden. Am Beispiel Chrome z.b.: \nRechtsklick auf die Seite des Wachendisplays \n--> "
                            "Untersuchen\n-->CTRL+SHIFT+C \n--> mit dem Courser dei große Übersichtstabelle markieren "
                            "und nach dem entsprechenden Eintrag suchen. \nz.B.: <div id=\"Feuerwehr Bad "
                            "Säckingen\"\neingegeben werden muss in diesem Fall nur Feuerwehr Bad Säckingen"
    )


def help_settings_wachendisplay_url():
    create_message_box(
        "Einstellung: Wachendisplay URL",
        "Bitte die <b>URL</b> des Wachendisplay eingeben",
        "Die URL wird von der ILS Verfügung gestellt. z.B.:\nhttp://172.16.24.3:8080/"
    )


def help_settings_wachendisplay_user():
    create_message_box(
        "Einstellung: Wachendisplay User",
        "Bitte den <b>Benutzernamen</b> des Wachendisplay eingeben",
        "Der Benutzername wird von der ILS vergeben und zur Verfügung gestellt."
    )


def help_wachendisplay_password():
    create_message_box(
        "Einstellung: Wachendisplay Passwort",
        "Bitte das <b>Passwort</b> des Wachendisplay eingeben",
        "Das Passwort wird von der ILS vergeben und zur Verfügung gestellt."
    )

def help_email_user():
    create_message_box(
        "Einstellung: E-Mail Benutzer",
        "Bitte den Benutzernamen des E-Mail Postfaches eingeben."
    )

def help_email_passwort():
    create_message_box(
        "Einstellung: E-Mail Passwort",
        "Bitte das Passwort des E-Mail Postfaches eingeben."
    )

def help_email_Server():
    create_message_box(
        "Einstellung: E-Mail Server"
        "Bitte den IMAP-Server des E-Mail Postfaches eingeben.",
        "Der Servername muss analog dieser Synthax definiert werden: z.b. imap.server.de "
    )

def help_kdo_alarm():
    create_message_box(
        "Einstellung: KDO-Alarm",
        "Falls auf dem Alarmfax der Leistelle das Kommando min einem alternativen RIC alarmiert "
                               "wird, kann dieser hier eingegeben werden.",
        "Auf dem Alarmfax der Leitstelle wird der Kommando Ric als eigenstänige Einsatzmaßnahme "
                            "alarmiert: z.b. <b> KDO-BadSäckingen-DAG \nIn diesem Beispiel kann als eindeutige "
                            "Zuordnung ein Teilstring KDO-Bad hinzugefügt werden."
    )

def help_dag_alternativ():
    create_message_box(
        "Einstellung: DAG-Alternative",
        "Falls eine zusätzliche Identifikation einer DAG-Einsatzmaßnahme nötig sein, kann diese "
                               "hier angegeben werden.",
        "Also Beispiel wird nicht FL-BS 2/40-DAG alarmiert, sonder beim Kleinalarm FL-BS 2/40-KLEIN. "
                            "In diesem Beispiel muss KLEIN als DAG-Alternative abgespeichert werden."
    )

def help_connect_tokens_all():
    create_message_box(
        "Einstellung: Tokens",
        "Details beachten!!! <br> Synthax Fahrzuge: <b>z.b. 2/40;2/42 </br>",
        "Test-API: \nDieser Token wird benötigt, wenn im Testmodus eine separate Fake-Abteilung "
                            "alarmiert werden soll (für Debug-Massnahmen). \n\nAbteilung 1-4:\nHier werden jeweils die "
                            "Connect API-Tokens der jeweiligen Abteilungen eingetragen. Zu finden unter: "
                            "\nhttps://connect.feuersoftware.com/ \n  --> jeweilige Abteilung \n    --> Schnittstellen \n "
                            "     --> Öffentliche Connect Schnittstelle \n\num eine Auswahl zu treffen, wann welche "
                            "Abteilung alarmiert werden soll, kann bei den Nebenabteilungen die jeweiligen Funkrufnahmen "
                            "eingetragen werden. \nSobald bei einem Alarm ein solcher Funkrufnahme alarmiert ist, "
                            "wird die zugehörige Abteilung mitalarmiert. \nBitte die Funkrufnahmen mit ; trennen: z.B. "
                            "2/40;2/42"
    )


def help_autostart():
    create_message_box(
        "Einstellung: Autostart",
        "Bei <b> Ja</b> wird bei Programmstart alle Subprozesse automatisch gestartet"
    )

def kontakt():
    create_message_box(
        "Kontakt",
        'Bei Fragen, Problemen oder Feedback, bitte per E-Mail an <a href= '
                    '"mailto:public@cm-siebold.de">public@cm-siebold.de</a> wenden'
    )

def installationsanleitung():
    create_message_box(
        "Installationsanleitung",
        'Die Installationsanleitung ist zu finden unter: <br><a '
                    'href="https://github.com/budofighter/EM_Statusplugin.git">Github</a>'
    )