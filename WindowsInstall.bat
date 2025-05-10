@echo off
setlocal

REM ――― Setup
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "APP_NAME=Python Password Manager"
set "ENTRY_SCRIPT=register_user.py"
set "EXE_NAME=register_user.exe"
set "RENAMED_EXE=%APP_NAME%.exe"
set "ICON_PATH=%SCRIPT_DIR%images\password_icon.ico"
set "SRC_EXE=%SCRIPT_DIR%dist\%EXE_NAME%"
set "DST_EXE=%SCRIPT_DIR%%RENAMED_EXE%"
set "DESKTOP_SHORTCUT=%USERPROFILE%\Desktop\%APP_NAME%.lnk"

REM ――― 1. Activate or create virtual environment
if not exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    echo [INFO] Creating virtual environment...
    python -m venv "%SCRIPT_DIR%venv"
)
call "%SCRIPT_DIR%venv\Scripts\activate.bat"

REM ――― 2. Install dependencies
echo [STEP 2] Installing dependencies...
pip install --upgrade pip
pip install -r "%SCRIPT_DIR%requirements.txt"

REM ――― 3. Clean old builds
echo [STEP 3] Cleaning previous builds...
if exist "%SCRIPT_DIR%dist" rmdir /s /q "%SCRIPT_DIR%dist"
if exist "%SCRIPT_DIR%build" rmdir /s /q "%SCRIPT_DIR%build"
for /r %%d in (__pycache__) do if exist "%%d" rmdir /s /q "%%d"
if exist "%SCRIPT_DIR%%EXE_NAME%" del /f /q "%SCRIPT_DIR%%EXE_NAME%"
if exist "%SCRIPT_DIR%%RENAMED_EXE%" del /f /q "%SCRIPT_DIR%%RENAMED_EXE%"

REM ――― 4. Build with PyInstaller
echo [STEP 4] Building executable...
pyinstaller --onefile --windowed --icon "%ICON_PATH%" "%ENTRY_SCRIPT%"

REM ――― 5. Copy and rename
if exist "%SRC_EXE%" (
    copy /Y "%SRC_EXE%" "%DST_EXE%"
    echo [SUCCESS] Renamed to: %RENAMED_EXE%
) else (
    echo [ERROR] Executable not found in dist.
    exit /b 1
)

REM ――― 6. Create desktop shortcut
echo [STEP 6] Creating desktop shortcut...
powershell -NoProfile -Command "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%DESKTOP_SHORTCUT%'); $s.TargetPath = '%DST_EXE%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = '%ICON_PATH%'; $s.Save()"

REM ――― 7. Run the compiled application
echo [STEP 7] Launching the app...
start "" "%DST_EXE%"

echo [DONE] Build complete. Shortcut created and app launched.
endlocal
pause
