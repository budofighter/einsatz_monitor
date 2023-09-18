@echo off
cd C:\Users\Public\PycharmProjects\einsatz_monitor

echo ##### Step 0: Copy EinsatzHandler.spec to current directory
copy .\bin\install\EinsatzHandler.spec .\

:: Check if the copy operation was successful
if %ERRORLEVEL% == 0 (
    echo File copied successfully.
) else (
    echo Error: Failed to copy file.
    exit /b 1
)

echo ##### Step 1: Activate virtual environment
call .\EinsatzHandler_venv\Scripts\activate

:: Check if the virtual environment was activated
if defined VIRTUAL_ENV (
    echo Virtual environment activated successfully.
    where python
) else (
    echo Error: Could not activate the virtual environment.
    exit /b 1
)

echo ##### Step 2: Update ISS file with new version number
python .\bin\install\versioninfo.py

:: Check if the Python script ran successfully
if %ERRORLEVEL% == 0 (
    echo Python script executed successfully.
) else (
    echo Error: Python script failed to execute.
    exit /b 1
)

echo ##### Step 3: Create installer with PyInstaller
pyinstaller.exe EinsatzHandler.spec

:: Check if PyInstaller ran successfully
if %ERRORLEVEL% == 0 (
    echo Installer created successfully.
) else (
    echo Error: Failed to create installer.
    exit /b 1
)

echo ##### Step 4: Deactivate the virtual environment
:: Deactivate the virtual environment
start cmd /c "call deactivate && exit"

:: Delete the copied EinsatzHandler.spec
del .\EinsatzHandler.spec

echo ##### Step 5: Compile with Inno Setup
:: Abfrage vor Schritt 5
set /p UserInput=Step 5: Soll der Installer mit Inno Setup compiliert werden? (Y/N): 
if /i "%UserInput%"=="Y" (
    echo Compiling with Inno Setup...
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" ".\bin\install\EinsatzHandler2.iss"
    :: Check if Inno Setup ran successfully
    if %ERRORLEVEL% == 0 (
        echo Inno Setup compilation successful.
    ) else (
        echo Error: Inno Setup compilation failed.
        exit /b 1
    )
) else if /i "%UserInput%"=="N" (
    echo Skipping Inno Setup compilation.
) else (
    echo Invalid input. Exiting.
    exit /b 1
)

echo ##### Done!
