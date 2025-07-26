@echo off
chcp 65001 >nul
title OIDE 系统停止

echo 🛑 正在停止OIDE系统...

:: 停止Python进程（Flask和HTTP服务器）
taskkill /f /im python.exe >nul 2>&1

:: 停止占用5000和5500端口的进程
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5500" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

echo ✅ OIDE系统已停止

timeout /t 2 /nobreak >nul