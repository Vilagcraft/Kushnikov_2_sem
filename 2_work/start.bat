@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo Installing requirements...
pip install -r requirements.txt

echo Starting calculator...
echo Open in browser: http://127.0.0.1:8000/glass
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

pause