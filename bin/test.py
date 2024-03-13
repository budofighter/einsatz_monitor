from einsatz_monitor_modules import mail

ausgabe = mail.send_email("Einsatzhandler Monitoring", "cs@csiebold.de", "Die Einsatzauswertung wurde neu gestartet")

print(ausgabe)