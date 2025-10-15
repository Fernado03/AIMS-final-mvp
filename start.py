#!/usr/bin/env python3
"""
AIMS Medical Scribe - Cross-Platform Startup Script
This script checks prerequisites and starts the application
"""

import os
import sys
import subprocess
import platform
import time
import webbrowser
from pathlib import Path


def print_header(text, color='cyan'):
    colors = {
        'cyan': '\033[96m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'reset': '\033[0m'
    }
    print(f"\n{colors.get(color, '')}{text}{colors['reset']}")


def print_status(status, message):
    colors = {
        'OK': '\033[92m',
        'ERROR': '\033[91m',
        'WARNING': '\033[93m',
        'INFO': '\033[96m',
        'reset': '\033[0m'
    }
    color = colors.get(status, colors['INFO'])
    print(f"{color}[{status}]{colors['reset']} {message}")


def check_env_file():
    """Check if .env file exists"""
    if not Path('.env').exists():
        print_status('ERROR', '.env file not found!')
        print('Please copy .env.example to .env and configure it.')
        sys.exit(1)
    print_status('OK', '.env file found')


def check_venv():
    """Check if virtual environment exists"""
    venv_path = Path('venv')
    if not venv_path.exists():
        print_status('WARNING', 'Virtual environment not found!')
        print('Creating virtual environment...')
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print_status('OK', 'Virtual environment created')
    return venv_path


def get_python_executable(venv_path):
    """Get the Python executable path in virtual environment"""
    system = platform.system()
    if system == 'Windows':
        return venv_path / 'Scripts' / 'python.exe'
    else:
        return venv_path / 'bin' / 'python'


def get_pip_executable(venv_path):
    """Get the pip executable path in virtual environment"""
    system = platform.system()
    if system == 'Windows':
        return venv_path / 'Scripts' / 'pip.exe'
    else:
        return venv_path / 'bin' / 'pip'


def check_dependencies(pip_path):
    """Check if dependencies are installed"""
    print('Checking dependencies...')
    result = subprocess.run([str(pip_path), 'show', 'Flask'], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print_status('WARNING', 'Dependencies not installed!')
        print('Installing dependencies...')
        subprocess.run([str(pip_path), 'install', '-r', 'requirements.txt'], 
                      check=True)
    print_status('OK', 'Dependencies installed')


def check_database():
    """Check if database exists"""
    db_path = Path('backend') / 'notes_main.db'
    if not db_path.exists():
        print_status('INFO', 'Database will be created on first run')


def open_browser(url, delay=3):
    """Open browser after a delay"""
    time.sleep(delay)
    webbrowser.open(url)


def main():
    """Main startup function"""
    print_header('=== AIMS Medical Scribe Startup ===', 'cyan')
    print_header('Checking prerequisites...', 'yellow')
    
    # Run checks
    check_env_file()
    venv_path = check_venv()
    
    # Get executables
    python_exe = get_python_executable(venv_path)
    pip_exe = get_pip_executable(venv_path)
    
    # Check dependencies
    check_dependencies(pip_exe)
    check_database()
    
    # Start server
    print_header('=== Starting AIMS Backend Server ===', 'cyan')
    print_status('INFO', 'Backend serving frontend at: http://localhost:5000')
    print_status('INFO', 'Press Ctrl+C to stop the server\n')
    
    # Open browser in background
    from threading import Thread
    browser_thread = Thread(target=open_browser, args=('http://localhost:5000',))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start Flask application
    try:
        subprocess.run([str(python_exe), '-m', 'backend.app'])
    except KeyboardInterrupt:
        print_header('\nServer stopped by user', 'yellow')
        sys.exit(0)


if __name__ == '__main__':
    main()
