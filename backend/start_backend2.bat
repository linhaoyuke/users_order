@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
flask run --host=0.0.0.0 --port=5000
pause
