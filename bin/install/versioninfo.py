import re
import sys
import os

if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS
else:
    basedir = os.path.join(os.path.dirname(__file__), "..", "..")

rc_file_path = os.path.join(basedir, "versioninfo.rc")
iss_file_path = os.path.join(basedir, "bin", "install", "EinsatzHandler2.iss")

def read_version_from_rc(rc_file_path):
    with open(rc_file_path, 'r') as f:
        content = f.read()
        match = re.search(r'filevers=\((\d+,\s*\d+,\s*\d+,\s*\d+)\)', content)

        if match:
            version = match.group(1).replace(',', '.').replace(' ', '')
            return version
    return None

def update_iss_file(iss_file_path, version):
    with open(iss_file_path, 'r') as f:
        content = f.read()
    updated_content = re.sub(r'#define MyAppVersion ".*"', f'#define MyAppVersion "{version}"', content)

    with open(iss_file_path, 'w') as f:
        f.write(updated_content)


if __name__ == "__main__":
    version = read_version_from_rc(rc_file_path)
    if version:
        print(f"Found version: {version}")
        update_iss_file(iss_file_path, version)
    else:
        print("Could not find version in RC file.")