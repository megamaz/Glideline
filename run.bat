@echo off

cd src
if not exist venv (
    echo Creating venv
    py -m venv venv
    echo Activating venv
    call ".\venv\Scripts\activate.bat"
    echo Installing requirements
    python -m pip install -r requirements.txt
)
@REM Works because we can't activate an already activated venv
@REM So this does nothing if we *just* went through venv setup
call ".\venv\Scripts\activate.bat"

python main.py

call "deactivate.bat"