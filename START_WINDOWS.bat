@echo off
cd /d "%~dp0"
echo === Village Vault secure bridge ===
set /p "VAULT_PLAYER_KEY=Player projection password (different from GM): "
set /p "VAULT_GM_KEY=GM control password: "
if "%VAULT_PLAYER_KEY%"=="%VAULT_GM_KEY%" (echo ERROR: passwords must differ & pause & exit /b 1)
py -m pip install -r requirements.txt
if errorlevel 1 (pause & exit /b 1)
py bridge.py --port COM7
pause
