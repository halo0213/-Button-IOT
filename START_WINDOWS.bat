@echo off
cd /d "%~dp0"
py -m pip install -r requirements.txt
if errorlevel 1 goto fail
py bridge.py --port COM7
pause
exit /b
:fail
echo Python not found. Install Python 3 from python.org and enable PATH.
pause
