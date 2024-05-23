# Optimiert 31.03.23
import imaplib
import os
import logging
import sys
import re
from email import message_from_bytes
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from . import database_class

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..", "..")

# Zugangsdaten:
database = database_class.Database()

# Logger:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file_path = os.path.join(basedir, "logs", "logfile_EM.txt")
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s"))
logger.addHandler(file_handler)

def pull_mails():
    try:
        # IMAP Verbindung per TLS aufbauen und einloggen:
        imap = imaplib.IMAP4(database.select_config("email_server"))
        imap.starttls()
        imap.login(database.select_config("email_username"), database.select_config("email_password"))
        imap.select("INBOX")

        # Liste aller ungelesenen E-Mails generieren:
        typ, msgnums = imap.search(None, "UNSEEN")
        unread_ids = re.sub(r"[\[\]b']+", "", str(msgnums)).split()

        if not unread_ids:
            logger.debug("Keine neuen Mails")
            return None
        else:
            # Nur die neueste ungelesene E-Mail abrufen
            latest_unread_id = max(unread_ids, key=int)
            
            # E-Mail mit ihrer ID holen
            res, msg = imap.fetch(str(latest_unread_id), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # E-Mail in ein msg Objekt parsen
                    msg = message_from_bytes(response[1])
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_disposition = str(part.get("Content-Disposition"))
                            if "attachment" in content_disposition:
                                filename = part.get_filename()
                                if filename:
                                    filepath = os.path.join(basedir, "tmp", filename)
                                    # Anhang herunterladen und zwischenspeichern:
                                    with open(filepath, "wb") as file:
                                        file.write(part.get_payload(decode=True))
                                    # E-Mail als gelesen markieren
                                    imap.store(str(latest_unread_id), '+FLAGS', '\Seen')
                                    logger.debug("E-Mailanhänge erfolgreich heruntergeladen und als gelesen markiert")
                                    return filename
    except Exception as e:
        database2 = database_class.Database()
        database2.update_aktiv_flag("auswertung", "error")
        logger.exception(f"Error beim Aufbau der IMAP Verbindung: {e}")
    finally:
        try:
            imap.close()
            imap.logout()
        except Exception as e:
            logger.error(f"Error bei der Verarbeitung der E-Mail Anhänge: {e}")


def send_email(subject, body, recipient):
    try:
        # Überprüfen, ob SMTP-Server-Konfiguration vorhanden ist:
        smtp_server = database.select_config("smtp_server")
        if not smtp_server:
            logger.info("Keine SMTP-Server-Konfiguration gefunden.")
            return

        # Überprüfen, ob Benutzername und Passwort vorhanden sind:
        smtp_user = database.select_config("smtp_user")
        smtp_password = database.select_config("smtp_password")
        if not smtp_user or not smtp_password:
            logger.info("SMTP-Benutzername oder Passwort nicht konfiguriert.")
            return

        # SMTP Verbindung aufbauen:
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()

        # einloggen:
        server.login(smtp_user, smtp_password)

        # erstellen der Email:
        msg = MIMEMultipart()
        msg["From"] = "alarm-test@fw-wallbach.de"
        msg["To"] = recipient
        msg["Subject"] = subject

        # anhängen des Texts:
        msg.attach(MIMEText(body, 'plain'))

        # senden der Email:
        server.send_message(msg)

        # beenden der Verbindung:
        server.quit()

        logger.info("Email erfolgreich gesendet")

    except Exception as e:
        logger.exception(f"Fehler beim Senden der Email: {e}")



