# Script um das Programm upzudaten und auf den neuesten Stand zu bringen. Die Einstellungen bleiben erhalten.

# 1. Update von GitHub herunterladen
try{
    Invoke-WebRequest "https://github.com/budofighter/einsatz_monitor/archive/refs/heads/main.zip" -outfile "./EM_update.zip"
    "Update erfolgreich heruntergeladen..."
}
catch{
    "==> Downloadad des Updates nicht moeglich, daher Scriptabbruch."
    exit
}

# 2. Alles auser die Config und die DB entfernen:

if(Test-Path ./bin/) {
    Remove-Item "./bin/" -Recurse -Force -Confirm:$false
    " ./bin/ erfolgreich geloescht..."
}
else{
    "./bin/ ist nicht vorhanden!"
}

if(Test-Path ./logs/) {
    Remove-Item "./logs/" -Recurse -Force -Confirm:$false
    " ./logs/ erfolgreich geloescht..."
}
else {
    "./logs/ ist nicht vorhanden!"
}
if(Test-Path ./resources/) {
    Remove-Item "./resources/" -Recurse -Force -Confirm:$false
    " ./resources/ erfolgreich geloescht..."
}
else {
    "./resources/ ist nicht vorhanden!"
}

if(Test-Path ./tmp/) {
    Remove-Item "./tmp/" -Recurse -Force -Confirm:$false
    " ./tmp/ erfolgreich geloescht..."
}
else {
    "./tmp/ ist nicht vorhanden!"
}

if(Test-Path ./ui/) {
    Remove-Item "./ui/" -Recurse -Force -Confirm:$false
    " ./ui/ erfolgreich geloescht..."
}
else {
    "./ui/ ist nicht vorhanden!"
}

if(Test-Path ./EM_start.ps1) {
    Remove-Item "./EM_start.ps1" -Recurse -Force -Confirm:$false
    " ./EM_start.ps1 erfolgreich geloescht..."
}
else {
    "./EM_start.ps1 ist nicht vorhanden!"
}

if(Test-Path ./README.md) {
    Remove-Item "./README.md" -Recurse -Force -Confirm:$false
    " ./README.md erfolgreich geloescht..."
}
else {
    "./README.md ist nicht vorhanden!"
}

"Loeschung der alten Dateien erfolgreich abgeschlossen..."


Add-Type -AssemblyName System.IO.Compression.FileSystem
function Unzip
{
    param([string]$zipfile, [string]$outpath)

    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipfile, $outpath)
}

Try{
    Unzip "./EM_update.zip" "./"
    "Unzip erfolgreich durchgeführt..."
}
Catch{
    "==> Unzip hat nicht funktioniert, daher Scriptabbruch. Bitte manuell in diesen Ordner Extrahieren."
    exit
}

Try
{
    Move-Item -Path "./EM_Statusplugin-main/*" -Destination "./" -Force
    Remove-Item "./EM_update.zip" -Recurse -Force -Confirm:$false
    Remove-Item "./EM_Statusplugin-main" -Recurse -Force -Confirm:$false
    "Dateien erfolgrich verschoben und TMP-Dateien geloescht"
}
Catch{
    "==> Verschieben und Löschen der Dateien hat nicht funktioniert. Bitte manuell durchführen."
}

"Update erfolgreich abgeschlossen!"
"blablabla"
Start-Sleep(30)