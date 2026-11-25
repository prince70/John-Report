@echo off
cd /d "%~dp0"

set "VENV_PY=%~dp0fastAPI\venv\Scripts\python.exe"
set "LOGDIR=%~dp0logs"
set "LOGFILE=%LOGDIR%\backend.log"
REM default port 8092, override with arg: start_prod.bat 8091
set "PORT=8092"
if not "%~1"=="" set "PORT=%~1"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

if not exist "%VENV_PY%" (
    echo [ERROR] venv python not found: %VENV_PY% >> "%LOGFILE%"
    echo [ERROR] venv python not found: %VENV_PY%
    echo         step1: python -m venv fastAPI\venv
    echo         step2: fastAPI\venv\Scripts\pip install -r fastAPI\requirements.txt
    pause
    exit /b 1
)

echo. >> "%LOGFILE%"
echo ================== %date% %time% John-Report service start (port %PORT%) ================== >> "%LOGFILE%"

REM skip if port already in use
netstat -ano | findstr "LISTENING" | findstr /R ":%PORT% " >nul
if not errorlevel 1 (
    echo [%time%] port %PORT% already in use, skip start >> "%LOGFILE%"
    exit /b 0
)

cd /d "%~dp0fastAPI\demo1"
"%VENV_PY%" -m uvicorn mains:app --host 0.0.0.0 --port %PORT% >> "%LOGFILE%" 2>&1
