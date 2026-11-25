@echo off
REM stop John-Report service, optional port arg: this.bat 8091
set "PORT=8092"
if not "%~1"=="" set "PORT=%~1"
echo Stopping John-Report service on port %PORT% ...
set "FOUND=0"
for /f "tokens=5" %%p in ('netstat -ano ^| findstr "LISTENING" ^| findstr /R ":%PORT% "') do (
    echo Killing PID=%%p
    taskkill /f /pid %%p
    set "FOUND=1"
)
if "%FOUND%"=="0" echo No service found on port %PORT%
timeout /t 2 >nul
