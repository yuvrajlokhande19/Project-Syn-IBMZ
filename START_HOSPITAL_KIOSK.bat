@echo off
title AEGISCORE // ZERO-TOUCH HOSPITAL KIOSK APPLIANCE
color 0A
cd /d "%~dp0"

echo ===============================================================================
echo        AEGISCORE // ZERO-TOUCH HOSPITAL APPLIANCE MODE
echo   Designed for Hospital Trauma Centers, ICU Walls, and Crash Cart Displays
echo ===============================================================================
echo.
echo [1/3] Detecting Local Runtime...
set PYTHON_CMD=
if exist "venv2\Scripts\python.exe" (
    set PYTHON_CMD=venv2\Scripts\python.exe
) else if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)

echo [2/3] Initializing Mainframe Core and Telemetry Simulator in Background...
start "AEGISCORE [Gateway]" /min cmd /c ""%PYTHON_CMD%" -m uvicorn main:app --app-dir 03-mainframe-core --host 127.0.0.1 --port 8000"
powershell -Command "Start-Sleep -Seconds 2" >nul 2>nul
start "AEGISCORE [Telemetry]" /min cmd /c ""%PYTHON_CMD%" 02-logic-engine\telemetry_simulator.py"
powershell -Command "Start-Sleep -Seconds 1" >nul 2>nul

echo [3/3] Launching Fullscreen Zero-Touch Kiosk Display...
set TARGET_URL=http://127.0.0.1:8000/ui/?kiosk=true

:: Check for Microsoft Edge Kiosk
where msedge >nul 2>nul
if %errorlevel% equ 0 (
    echo       Engaging Edge Kiosk Engine...
    start msedge --kiosk %TARGET_URL% --edge-kiosk-type=fullscreen --no-first-run --disable-pinch
    goto :DONE
)

:: Check for Google Chrome Kiosk
where chrome >nul 2>nul
if %errorlevel% equ 0 (
    echo       Engaging Chrome Kiosk Engine...
    start chrome --kiosk %TARGET_URL% --noerrdialogs --disable-infobars --overscroll-history-navigation=0
    goto :DONE
)

:: Fallback to default browser
echo       Launching Default Browser in Kiosk Mode...
start %TARGET_URL%

:DONE
echo.
echo ===============================================================================
echo [ACTIVE] HOSPITAL KIOSK RUNNING (ZERO MOUSE / KEYBOARD REQUIRED)
echo   • Mode:        Touch-Optimized Hands-Free Autopilot
echo   • Cycle:       Trilingual Alerts (English -> Hindi -> Marathi every 7s)
echo   • Exit Kiosk:  Press Alt+F4 or F11
echo ===============================================================================
timeout /t 5 >nul
exit
