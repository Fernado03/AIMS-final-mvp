# AIMS Medical Scribe - Startup Script for Windows PowerShell
# This script checks prerequisites and starts the application

Write-Host "
=== AIMS Medical Scribe Startup ===" -ForegroundColor Cyan
Write-Host "Checking prerequisites...
" -ForegroundColor Yellow

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    Write-Host "Please copy .env.example to .env and configure it.
" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] .env file found" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "
[WARNING] Virtual environment not found!" -ForegroundColor Yellow
    Write-Host "Creating virtual environment...
" -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "
Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if dependencies are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$pipList = pip list
if (-not ($pipList -match "Flask")) {
    Write-Host "
[WARNING] Dependencies not installed!" -ForegroundColor Yellow
    Write-Host "Installing dependencies...
" -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies!" -ForegroundColor Red
        exit 1
    }
}
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Start local Docker Mongo (aims-mongo)
Write-Host "Starting local MongoDB..." -ForegroundColor Yellow
docker start aims-mongo 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    docker run -d --name aims-mongo -p 27017:27017 mongo:7 2>$null | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARNING] Could not start Docker Mongo. Open Docker Desktop, then: docker start aims-mongo" -ForegroundColor Yellow
    }
}

Write-Host "
=== Starting AIMS Backend Server ===" -ForegroundColor Cyan
Write-Host "Backend serving frontend at: http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server
" -ForegroundColor Yellow

# Wait a moment then open browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:5000"

# Start the Flask application
python -m backend.app
