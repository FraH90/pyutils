@echo off
REM Change to the directory where this batch script is located
cd /d %~dp0

REM Run the deploy.py script from the zdistr subdirectory using relative path
python zdistr\deploy.py

REM Pause the script to see the output
pause
