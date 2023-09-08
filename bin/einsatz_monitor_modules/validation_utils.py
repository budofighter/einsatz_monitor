import re

# Regex-Dictionary
regex_dict = {
    "kdo_alarm": r"^(?!.*DAG)[a-zA-Z0-9_\:,.-]+$",
    "fahrzeuge": r"^(([A-Z]{2}[ -][A-Z]{2,3} )?(\d\/)\d{2}(\/\d{1,2})?\n{0,2})+",
    "funkrufname": r"^[A-Z]{2}-[A-Z]{2,3}$", 
    "url_wachendisplay": r"^http://(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)/?$",
    "wachendisplay_content_id": r"^[a-zA-Z0-9äöüÄÖÜß]+([a-zA-Z0-9äöüÄÖÜß\s]*[a-zA-Z0-9äöüÄÖÜß]+)?$",
    "openvpn_config": r"^[a-zA-Z]:[\\/](?:[^\\/\r\n]+[\\/])*[^\\/\r\n]+\.ovpn$",
    "email_server": r"^[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,8}$",  
    "fahrzeuge_abt": r"^(\d{1,2}/\d{2,3})(;\d{1,2}/\d{2,3})*$"

}

def validate_input(input_value, setting):
    """Validiert die Eingabe anhand eines Regex-Musters, das mit der Einstellung verknüpft ist."""
    regex_pattern = regex_dict.get(setting, None)
    if regex_pattern:
        return bool(re.fullmatch(regex_pattern, input_value))
    return True  # Wenn keine Regex-Regel für die Einstellung definiert ist, gilt die Eingabe als gültig
