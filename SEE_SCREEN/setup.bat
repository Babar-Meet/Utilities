@echo off
title Mouse Preview - Setup
echo Installing dependencies...
pip install -r "%~dp0requirements.txt"
echo.
echo Done! You can now run: launch_mouse_preview.bat
pause
