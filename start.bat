@echo off
REM AIMS Medical Scribe - Startup Script for Windows Command Prompt
echo.
echo === AIMS Medical Scribe Startup ===
echo.

REM Check if .env exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please copy .env.example to .env and configure it.
    pause
    exit /b 1
)

REM Check if venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies if needed
echo Checking dependencies...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo === Starting AIMS Backend Server ===
echo Backend serving frontend at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Open browser after 2 seconds
timeout /t 2 /nobreak >nul
start http://localhost:5000

REM Start Flask application
python -m backend.app
