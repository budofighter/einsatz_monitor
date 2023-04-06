# Script um das Programm upzudaten und auf den neuesten Stand zu bringen. Die Einstellungen bleiben erhalten.

# Funktion zum Herunterladen von GitHub
function Get-GitHubRelease($url, $destination) {
    try {
        $response = Invoke-RestMethod -Uri $url -UseBasicParsing
        $response.content > $destination
        Write-Output "Update erfolgreich heruntergeladen..."
        return $true
    }
    catch {
        Write-Output "==> Download des Updates nicht möglich, daher Scriptabbruch."
        return $false
    }
}

# Funktion zum Entfernen von Dateien und Ordnern
function Remove-FileOrFolder($path) {
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force -Confirm:$false
        Write-Output "$path erfolgreich gelöscht..."
        return $true
    }
    else {
        Write-Output "$path ist nicht vorhanden!"
        return $false
    }
}

# Funktion zum Installieren von Updates
function Install-Update($zipPath, $extractPath) {
    try {
        Expand-Archive -LiteralPath $zipPath -DestinationPath $extractPath
        Write-Output "Update erfolgreich installiert..."
        return $true
    }
    catch {
        Write-Output "==> Update-Installation fehlgeschlagen, daher Scriptabbruch. Bitte manuell in diesen Ordner extrahieren."
        return $false
    }
}

# GitHub-URL definieren
$url = "https://github.com/budofighter/einsatz_monitor/archive/refs/heads/main.zip"

# Ordner und Dateien, die entfernt werden sollen, definieren
#$files = @("./EM_start.ps1", "./README.md", "./main.py")

# Update-Ordner definieren
$updateFolder = "./einsatz_monitor-main"

# Update herunterladen
if (Get-GitHubRelease -url $url -destination "./EM_update.zip")
{
    # Alte Dateien löschen
    $output = ""
    foreach ($directory in $directories)
    {
        if (Remove-FileOrFolder $directory)
        {
            $output += "$directory erfolgreich gelöscht...`n"
        }
    }
    foreach ($file in $files)
    {
        if (Remove-FileOrFolder $file)
        {
            $output += "$file erfolgreich gelöscht...`n"
        }
    }
    # Update installieren
    if (Install-Update -zipPath "./EM_update.zip" -extractPath "./") {
        # Dateien verschieben und löschen
        $output += "Dateien erfolgreich verschoben und TMP-Dateien gelöscht...`n"
        robocopy $updateFolder .\ /E /MOVE /Z /XO /XD .git /XD __pycache__ /XF .gitignore | Out-Null
        Remove-FileOrFolder "./EM_update.zip" | Out-Null
        Remove-FileOrFolder $updateFolder | Out-Null

        # Config-Modul verschieben
        robocopy "$updateFolder\config" ".\bin\einsatz_monitor_modules" /MOV /XF config.ini.example | Out-Null
        $output += "Verschieben der Config-Datei erfolgreich...`n"

        # Update erfolgreich abgeschlossen!
        $output += "Update erfolgreich abgeschlossen!`n"

        # Script beenden
        Exit 0
    }
    else {
        $output += "Update-Installation fehlgeschlagen, daher Scriptabbruch. Bitte manuell in diesen Ordner extrahieren.`n"
    }
}
else {
    $output += "Download des Updates nicht möglich, daher Scriptabbruch.`n"
}

#Ausgabe
Write-Output $output