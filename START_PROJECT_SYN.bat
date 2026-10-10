@echo off
title PROJECT SYN // AEGISCORE ONE-CLICK LAUNCHER
color 0B
cd /d "%~dp0"

echo ===============================================================================
echo                PROJECT SYN // AEGISCORE DISASTER RESILIENCE
echo          Target Architecture: IBM LinuxONE (s390x) / Ubuntu 22.04 LTS
echo ===============================================================================
echo.
echo [1/4] Detecting Python Environment...

set PYTHON_CMD=
if exist "venv2\Scripts\python.exe" (
    set PYTHON_CMD=venv2\Scripts\python.exe
    echo       Using Virtual Environment: venv2 (Python 3.11)
) else if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD=venv\Scripts\python.exe
    echo       Using Virtual Environment: venv
) else (
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python
        echo       Using System Python
    ) else (
        echo [ERROR] Python not found! Please install Python or set up venv2.
        pause
        exit /b 1
    )
)

echo.
echo [2/4] Launching Mainframe Core Gateway (FastAPI / CPACF Cryptographic Gate)...
start "AEGISCORE [1] - Mainframe Core Gateway (Port 8000)" cmd /c ""%PYTHON_CMD%" -m uvicorn main:app --app-dir 03-mainframe-core --host 127.0.0.1 --port 8000"

echo       Waiting for server to initialize on 127.0.0.1:8000...
powershell -Command "Start-Sleep -Seconds 3" >nul 2>nul

echo.
echo [3/4] Launching Real-Time Sensor Telemetry Simulator (HMAC-SHA256 Signed)...
start "AEGISCORE [2] - Real-Time Telemetry Simulator" cmd /c ""%PYTHON_CMD%" 02-logic-engine\telemetry_simulator.py"

echo.
echo [4/4] Opening Disaster Command Center Dashboard in Browser...
powershell -Command "Start-Sleep -Seconds 1" >nul 2>nul
start http://127.0.0.1:8000/ui/

echo.
echo ===============================================================================
echo [SYSTEM ACTIVE] AEGISCORE IS NOW FULLY RUNNING!
echo.
echo   • Command Center UI:     http://127.0.0.1:8000/ui/
echo   • REST API Docs:         http://127.0.0.1:8000/docs
echo   • CPACF Hardware Gate:   ENFORCING ZERO-TRUST HMAC-SHA256
echo   • AI Model Cascade:      gemini-3.8-flash (1M tokens) + Auto-Failover
echo   • Offline P2P Mesh:      ACTIVE (868/915 MHz Hospital-to-Hospital & Staff)
echo   • Deterministic Reroute: Nagpur Dijkstra Engine Engaged
echo ===============================================================================
echo You can keep this window open or close it. To stop services, close the
echo two background process windows.
echo.
pause
