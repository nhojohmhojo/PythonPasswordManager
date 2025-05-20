@echo off

:: Step 1: Go to script folder
cd /d "%~dp0"

:: Step 2: Set up virtual environment
if not exist venv\Scripts\activate.bat (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

:: Step 3: Install required packages
echo Installing Python packages...
pip install -r requirements.txt

:: Step 4: Clean previous builds
echo Cleaning old builds...
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
del /q *.spec 2>nul

:: Step 5: Build app with PyInstaller
echo Building the app...
pyinstaller --onefile --windowed --icon="images\password_icon.ico" register_and_login.py

:: Step 6: Rename and copy EXE to project root
if exist dist\register_and_login.exe (
    copy /Y dist\register_and_login.exe "Python Password Manager.exe"
) else (
    echo ERROR: Build failed. EXE not found.
    exit /b 1
)

:: Step 7: Create a desktop shortcut
powershell -NoProfile -Command ^
 "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('$env:USERPROFILE\Desktop\Python Password Manager.lnk'); ^
 $s.TargetPath = '%~dp0Python Password Manager.exe'; ^
 $s.WorkingDirectory = '%~dp0'; ^
 $s.IconLocation = '%~dp0images\password_icon.ico'; ^
 $s.Save()"

:: Step 8: Launch the app
start "" "Python Password Manager.exe"

echo Done!
exit
