@echo off
setlocal enabledelayedexpansion

REM Log file
set LOGFILE=install_log.txt
echo ==== Tally Supabase Wizard Install Log ==== > %LOGFILE%

REM Check for Python 3.11+
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Downloading and installing Python 3.11... >> %LOGFILE%
    echo Python not found. Downloading and installing Python 3.11...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"
    if exist "%TEMP%\python_installer.exe" (
        "%TEMP%\python_installer.exe" /quiet /InstallAllUsers=1 /PrependPath=1 /Include_test=0
        del "%TEMP%\python_installer.exe"
    ) else (
        echo Failed to download Python installer. >> %LOGFILE%
        echo Failed to download Python installer.
        exit /b 1
    )
)

REM Check Python version
python --version 2>nul | findstr /R "3\.1[1-9]" >nul
if %errorlevel% neq 0 (
    echo Python version is not 3.11+. Please upgrade Python. >> %LOGFILE%
    echo Python version is not 3.11+. Please upgrade Python.
    exit /b 1
)

REM Ensure pip is installed
python -m ensurepip --upgrade >nul 2>&1

REM Upgrade pip
python -m pip install --upgrade pip >nul 2>&1

REM Install Python dependencies
echo Installing Python dependencies... >> %LOGFILE%
echo Installing Python dependencies...
python -m pip install -r requirements.txt >> %LOGFILE% 2>&1
if %errorlevel% neq 0 (
    echo Failed to install Python dependencies. >> %LOGFILE%
    echo Failed to install Python dependencies.
    exit /b 1
)

REM Launch the wizard
echo Launching Tally Supabase Wizard... >> %LOGFILE%
echo Launching Tally Supabase Wizard...
python tally_supabase_wizard.py
exit /b %errorlevel%
