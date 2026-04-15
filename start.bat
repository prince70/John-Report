
@echo off
chcp 65001 >nul
cd /d %~dp0

echo.
echo ========================================
echo   启动开发服务器
echo ========================================
echo.

REM 启动 Vue 开发服务器
echo [1/2] 启动前端服务 (Vue)...
start "Vue Dev Server" cmd /k "cd /d d:\Code\new_report_john\code-ABUS && npm run serve"

REM 等待前端启动后再启动后端
timeout /t 3 /nobreak

REM 启动 FastAPI 后端服务
echo [2/2] 启动后端服务 (FastAPI)...
start "FastAPI Server" cmd /k "cd /d d:\Code\new_report_john\fastAPI\demo1 && d:\Code\new_report\.venv\Scripts\activate.bat && uvicorn mains:app --reload --port 8091"

echo.
echo ========================================
echo   所有服务已启动
echo ========================================
echo   前端: http://localhost:8080
echo   后端: http://localhost:8081
echo ========================================
echo.