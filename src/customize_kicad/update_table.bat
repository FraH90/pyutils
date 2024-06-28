@echo off
:: Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    :: If not running as administrator, use runas to relaunch the script
    echo Requesting administrative privileges...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~fnx0' -Verb RunAs"
    exit /b
)

:: Change to the directory where the batch file is located
cd /d %~dp0

:: If running as administrator, execute the Python script
python update_table.py

pause