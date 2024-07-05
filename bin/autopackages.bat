@echo off
REM Get the name of the currently executing batch file without the extension
set BatchFileName=%~n0

REM Navigate to the parent folder, then to src, and then to the folder with the batch file name substituted
cd ..\src\%BatchFileName%

REM Run the Python script with the same name as the batch file
python %BatchFileName%.py

pause