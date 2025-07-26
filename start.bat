@echo off
chcp 65001 >nul
title OIDE 快速启动

echo 🚀 OIDE 快速启动中...

:: 初始化数据库
cd backend
python init_db.py >nul 2>&1
cd ..

:: 启动后端
start "Backend" cmd /k "cd backend && python app.py"

:: 启动 AI Agent 服务
start "AI Agent" cmd /k "cd backend && python ai_agent.py"

:: 启动前端
start "Frontend" cmd /k "cd frontend && python -m http.server 5500"

:: 等待启动
timeout /t 3 /nobreak >nul

echo ✅ 系统启动完成！
echo 📱 前端: http://localhost:5500/index.html
echo 🔧 后端: http://localhost:5000/api
echo 🤖 AI Agent: http://localhost:5001/api/ai

:: 等待服务完全启动
timeout /t 5 /nobreak >nul

:: 检查服务状态
echo 🔍 检查服务状态...
python check-services.py

:: 自动打开浏览器
start http://localhost:5500/index.html

echo 按任意键关闭此窗口...
pause >nul