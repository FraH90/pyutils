@echo off
REM Get the full path of the batch file
set "BatchPath=%~dp0"
REM Get the name of the currently executing batch file without the extension
set "BatchFileName=%~n0"
REM Remove "_admin" from the BatchFileName if present
set "PythonFileName=%BatchFileName:_admin=%"
REM Construct the full path to the Python script
set "PythonScriptPath=%BatchPath%\..\..\src\%PythonFileName%\%PythonFileName%.py"
REM Get the directory of the Python script
for %%F in ("%PythonScriptPath%") do set "PythonScriptDir=%%~dpF"

REM Check if the batch file name ends with "_admin"
echo %BatchFileName% | findstr /E "_admin" >nul
if %errorlevel% equ 0 (
    REM If the name ends with "_admin", check for admin privileges
    net session >nul 2>&1
    if %errorlevel% neq 0 (
        REM If not running as administrator, use runas to relaunch the script
        echo Requesting administrative privileges...
        powershell -Command "Start-Process cmd -ArgumentList '/c %~fnx0' -Verb RunAs"
        exit /b
    )
)

REM Change to the directory where the Python script is located
cd /d "%PythonScriptDir%"

REM Run the Python script with the full path
python "%PythonScriptPath%"
pause