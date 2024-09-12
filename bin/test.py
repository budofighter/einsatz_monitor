import einsatz_monitor_modules.fireplan_api
import einsatz_monitor_modules.database_class

database = einsatz_monitor_modules.database_class.Database()

secret = "byeJoNAy7lPX1GPBt8JN5WBaIqxLZclzQprif13Qh9L"
division = "Bad Säckingen"
fp = einsatz_monitor_modules.fireplan_api.Fireplan(secret, division)

kennung = database.translate_fireplan_setting("FLBAS110")
print(kennung)

#kennung = "BWFW WT BAS 1KdoW       "
status = "4"
fp.send_fms_status(kennung, status)