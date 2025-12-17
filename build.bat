@echo off
REM CatLock Build Script for Windows
REM This script builds a local executable that won't be blocked by SmartScreen

echo ========================================
echo CatLock Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo [3/3] Building CatLock executable...
pyinstaller --onefile ^
    --add-data="./resources/img/icon.ico;./resources/img/" ^
    --add-data="./resources/img/icon.png;./resources/img/" ^
    --add-data="./resources/config/config.json;./resources/config/" ^
    --icon="./resources/img/icon.ico" ^
    --hidden-import plyer.platforms.win.notification ^
    --noconsole ^
    --name="CatLock" ^
    "./src/main.py"

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SUCCESSFUL!
echo ========================================
echo.
echo Your executable is located at:
echo   dist\CatLock.exe
echo.
echo TIP: If Windows Defender flags it, add the dist folder
echo      to your exclusions list in Windows Security.
echo.
pause
