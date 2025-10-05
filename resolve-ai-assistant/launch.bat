@echo off
REM Quick launcher for DaVinci Resolve AI Assistant
REM Double-click to run (or run from PowerShell)

echo.
echo ============================================================
echo    DaVinci Resolve AI Assistant - Quick Launcher
echo ============================================================
echo.

REM Check if DaVinci Resolve is running
tasklist /FI "IMAGENAME eq Resolve.exe" 2>NUL | find /I /N "Resolve.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo WARNING: DaVinci Resolve doesn't appear to be running
    echo Please start DaVinci Resolve and open a project first.
    echo.
    echo Press any key to continue anyway, or Ctrl+C to cancel...
    pause >nul
)

REM Navigate to project directory
cd /d "%~dp0"

echo Starting assistant...
echo.
echo REMEMBER: Type a command before pressing Enter!
echo Empty input will exit the assistant.
echo.
echo ============================================================
echo.

REM Run the assistant
python simple_launch.py

echo.
echo ============================================================
echo Assistant closed.
echo.
pause
