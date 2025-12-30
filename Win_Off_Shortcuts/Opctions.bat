@echo off
:: Enable color and cursor options
title System Control Menu
color 0A

:menu
cls
echo ================================================
echo   Welcome to the System Control Menu
echo ================================================
echo.
echo   Please select an option:
echo.
echo   [1] Shutdown
echo   [2] Sleep
echo   [3] Restart
echo   [4] Logoff
echo   [5] Exit
echo.
echo ================================================
set /p "userinput=  Enter your choice (1-5): "

if "%userinput%"=="1" (
    echo.
    echo Shutting down your computer...
    shutdown /s /f /t 0
) else if "%userinput%"=="2" (
    echo.
    echo Putting your computer to sleep...
    rundll32.exe powrprof.dll,SetSuspendState 0,1,0
) else if "%userinput%"=="3" (
    echo.
    echo Restarting your computer...
    shutdown /r /f /t 0
) else if "%userinput%"=="4" (
    echo.
    echo Logging off...
    shutdown /l
) else if "%userinput%"=="5" (
    echo.
    echo Exiting the menu. Have a nice day!
    exit
) else (
    echo.
    color 0C
    echo Invalid choice. Please try again.
    pause >nul
    color 0A
    goto menu
)
