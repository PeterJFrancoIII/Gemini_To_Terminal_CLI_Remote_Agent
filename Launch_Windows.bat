@echo off
setlocal

REM Change to script directory
cd /d "%~dp0"

REM Check/Create Virtual Environment
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate and install requirements
call .venv\Scripts\activate.bat
echo Installing/Updating requirements...
pip install -r requirements.txt

REM Run the application
echo Starting Gemini Terminal Bridge...
python gui_bridge.py

endlocal
pause
