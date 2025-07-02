@echo off
REM Treta Easy Installer for Windows
REM ===============================
REM
REM This script runs the Treta auto-installer with sensible defaults.
REM Double-click this file to install Treta automatically!

title Treta Music Downloader - Easy Installer

echo.
echo ===============================================
echo    Treta Music Downloader - Easy Installer
echo ===============================================
echo.
echo This will automatically install everything you need:
echo   - Python environment setup
echo   - All music downloaders (Spotify, Apple, YouTube)
echo   - Audio processing tools
echo   - Global 'treta' command
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found!
    echo.
    echo Please install Python 3.8+ from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found! Starting installation...
echo.

REM Run the installer with global install option
python install_auto.py --global-install

echo.
if %errorlevel% equ 0 (
    echo ===============================================
    echo    Installation Complete! 
    echo ===============================================
    echo.
    echo You can now use Treta in several ways:
    echo   1. Type 'treta' in any command prompt
    echo   2. Use treta.bat in this folder
    echo   3. Use PowerShell: .\treta.ps1
    echo.
    echo Next steps:
    echo   1. Run: treta auth add --service spotify
    echo   2. Run: treta download url "YOUR_MUSIC_URL"
    echo.
    echo For help: treta --help
    echo.
) else (
    echo ===============================================
    echo    Installation Had Issues
    echo ===============================================
    echo.
    echo Some components may not have installed correctly.
    echo You can still use Treta with: python treta.py
    echo.
    echo For troubleshooting:
    echo   - Run: python test_installation.py
    echo   - Check the documentation
    echo   - Report issues on GitHub
    echo.
)

echo Press any key to exit...
pause >nul
