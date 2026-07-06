@echo off
title Building Dr Broken Display EXE

echo Installing build tools...
pip install pyinstaller

echo.
echo Building EXE...
pyinstaller --onefile --noconsole --name "DrBrokenDisplay" ^
    --icon "dr_broken_display.ico" ^
    --exclude-module PyQt5 ^
    --exclude-module cv2 ^
    --exclude-module numpy ^
    --hidden-import pynput.keyboard ^
    --hidden-import pynput.mouse ^
    --hidden-import mss ^
    --hidden-import PIL._tkinter_finder ^
    mouse_preview.py

echo.
if exist "dist\DrBrokenDisplay.exe" (
    echo SUCCESS! EXE created at: dist\DrBrokenDisplay.exe
    echo.
    echo You can copy dist\DrBrokenDisplay.exe anywhere and run it.
) else (
    echo FAILED. Check the output above.
)

pause
