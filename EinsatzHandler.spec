# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('EinsatzHandler.manifest','.'),('bin/crawler_process.py','bin'),('bin/einsatz_process.py','bin'),('bin/monitoring_process.py','bin'),('bin/ovpn_process.py','bin'), ('ui/*','ui'),('resources/openvpn/*','resources/openvpn'),('bin/einsatz_monitor_modules/*','bin/einsatz_monitor_modules'),('resources/attention.png','resources'),('resources/fwsignet.ico','resources'),('resources/led-green.png','resources'),('resources/led-red.png','resources'),('resources/logo_fwbs.png','resources'),('resources/pdftotext.exe','resources')],
    
    hiddenimports=[

        # Selenium
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.expected_conditions',
        'selenium.webdriver.support.ui',
        'selenium.common.exceptions',
        
        # Drittanbieter
        'webdriver_manager.chrome',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EinsatzHandler',
    manifest='EinsatzHandler.manifest',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/fwsignet.ico',
    uac_admin=True,
    version='versioninfo.rc',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='EinsatzHandler',
)
