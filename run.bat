@echo off

cd src
if not exist venv (
    echo Creating venv
    py -m venv venv
    echo Installing requirements
    .\venv\Scripts\python.exe -m pip install -r requirements.txt
)

echo Running
.\venv\Scripts\python.exe main.py