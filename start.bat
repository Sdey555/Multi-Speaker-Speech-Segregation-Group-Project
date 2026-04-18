@echo off
cd /d "%~dp0"

echo =====================================
echo Setting up environment...
echo =====================================

:: Check if venv exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo =====================================
echo Running project...
echo =====================================

python main.py

echo.
echo Done!
pause