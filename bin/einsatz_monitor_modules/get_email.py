import imaplib, email, os, logging
from . import database_class

# Zugangsdaten:
database = database_class.Database()

# Logger:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(os.path.join(os.path.dirname(__file__), "..", "..", "logs"),
                                                "logfile_EM.txt"), encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logger.addHandler(file_handler)


def pull_mails():
    try:
        try:
            # IMAP Verbindung per SSL aufbauen und einloggen:
            imap = imaplib.IMAP4_SSL(database.select_config("email_server"))
            imap.login(database.select_config("email_username"), database.select_config("email_password"))
            imap.select("INBOX")
        except:
            logger.error("Error beim Aufbau der IMAP Verbindung")

        # Liste aller ungelesenen E-Mails gennerieren:
        typ, msgnums = imap.search(None, 'UNSEEN')
        unread_ids = str(msgnums).replace("'", "").replace("b", "").replace("[", "").replace("]","").split()

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
                        msg = email.message_from_bytes(response[1])
                        # Wenn die E-Mail eine Multipart E-Mail ist:
                        if msg.is_multipart():
                            # jeden Part durchgehen
                            for part in msg.walk():
                                # und den Content typ auslesen.
                                content_disposition = str(part.get("Content-Disposition"))
                                # wenn der Content Typ ein Anhang ist:
                                if "attachment" in content_disposition:
                                    # Anhang herunterladen und speichern.
                                    filename = part.get_filename()
                                    if filename:
                                        filepath = os.path.join(os.path.dirname(__file__), "..", "..", "tmp", filename)
                                        # Anhang herunterladen und zwischenspeichern:
                                        open(filepath, "wb").write(part.get_payload(decode=True))
                                        pdfs.append(filename)
                                logger.debug("E-Mailanhänge erfolgreich heruntergeladen")
            return pdfs
    finally:
        try:
            imap.close()
            imap.logout()
        except:
            logger.error("Error bei der Verarbeitung der E-Mail Anhänge ")
