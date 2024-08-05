@echo off
REM Get the full path of the batch file
set "BatchPath=%~dp0"
REM Get the name of the currently executing batch file without the extension
set "BatchFileName=%~n0"
REM Construct the full path to the Python script
set "PythonScriptPath=%BatchPath%\..\..\src\gitutils\%BatchFileName%.py"
REM Run the Python script with the full path
python "%PythonScriptPath%"
pause