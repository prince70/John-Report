@echo off
cd /d "E:\Desktop_Backup\ABUS_WEB\John-Report\fastAPI\demo1"
set DB_PASSWORD=
set DB_SERVER=192.168.10.200
set DB_DATABASE=APS_SUO
set DB_USERNAME=sa
echo Starting server...
call .\venv\Scripts\activate
.\venv\Scripts\python.exe -m uvicorn mains:app --port 8091 --host 127.0.0.1 &
set SERVER_PID=%%
timeout /t 5 >nul
echo Testing API...
curl -s http://127.0.0.1:8091/file/pandian-all | find "success" || echo "API test failed"
echo Server running on port 8091