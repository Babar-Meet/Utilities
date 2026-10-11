@echo off
title Dr Clock and Battery
color 0A

cd /d "%~dp0"

python "Time_Battry_info.py"

if errorlevel 1 (
    echo.
    echo The overlay did not start. Check that Python is on PATH and that
    echo psutil is installed:  pip install psutil
    echo.
    pause
)