@echo off
echo ====================================
echo         Starting Backend...
echo ====================================
cd backend

if exist venv\Scripts\activate.bat (
    echo Activating Virtual Environment...
    call venv\Scripts\activate.bat
)

if exist requirements.txt (
    echo Checking/Installing Requirements...
    pip install -r requirements.txt
)

echo Starting FastAPI Server...
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
