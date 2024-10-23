@echo off
REM Setup Virtual Environment Script for Windows

echo Checking if virtual environment exists...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip to the latest version...
python -m pip install --upgrade pip

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo Setup complete. Virtual environment is ready to use.
echo To activate the virtual environment later, run: venv\Scripts\activate.bat