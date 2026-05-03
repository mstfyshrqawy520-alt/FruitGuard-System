@echo off
echo ====================================
echo     Starting Desktop (PyQt6)...
echo ====================================
cd pyqt_desktop

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing requirements...
pip install -r requirements.txt

echo Launching app...
python main.py

pause
