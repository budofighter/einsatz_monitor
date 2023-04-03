# Optimiert 31.03.23
import imaplib
import os
import logging
import re
from email import message_from_bytes

from . import database_class

# Zugangsdaten:
database = database_class.Database()

# Logger:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "logs", "logfile_EM.txt")
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
        else:
            pdfs = []
            # jede ungelesene
            for unread_id in unread_ids:
                # Emails mit ihrer ID holen
                res, msg = imap.fetch(str(unread_id), "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        # Email in ein msg Objekt parsen
                        msg = message_from_bytes(response[1])
                        # Wenn die E-Mail eine Multipart E-Mail ist:
                        if msg.is_multipart():
                            # jeden Part durchgehen
                            for part in msg.walk():
                                # und den Content-Typ auslesen.
                                content_disposition = str(part.get("Content-Disposition"))
                                # wenn der Content-Typ ein Anhang ist:
                                if "attachment" in content_disposition:
                                    # Anhang herunterladen und speichern.
                                    filename = part.get_filename()
                                    if filename:
                                        filepath = os.path.join(
                                            os.path.dirname(__file__), "..", "..", "tmp", filename
                                        )
                                        # Anhang herunterladen und zwischenspeichern:
                                        with open(filepath, "wb") as file:
                                            file.write(part.get_payload(decode=True))
                                        pdfs.append(filename)
                            logger.debug("E-Mailanhänge erfolgreich heruntergeladen")
            return pdfs
    except Exception as e:
        logger.exception(f"Error beim Aufbau der IMAP Verbindung: {e}")
        database.update_aktiv_flag("auswertung", "2")
    finally:
        try:
            imap.close()
            imap.logout()
        except Exception as e:
            logger.error(f"Error bei der Verarbeitung der E-Mail Anhänge: {e}")
