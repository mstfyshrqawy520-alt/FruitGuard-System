@echo off
echo ====================================
echo     Starting Full Application...
echo ====================================

echo Starting Backend in a new window...
start cmd /k "call run_backend.bat"

echo.
echo Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak

echo.
echo Choose which client to launch:
echo 1. Desktop App (Python PyQt6)
echo 2. Mobile App (Auto-Detect Device)
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="1" (
    echo Starting Desktop App in a new window...
    start cmd /k "call run_pyqt.bat"
) else if "%choice%"=="2" (
    echo Starting Mobile App in a new window...
    start cmd /k "call run_mobile.bat"
) else (
    echo Invalid choice.
)

echo.
echo All requested services launched!
pause
