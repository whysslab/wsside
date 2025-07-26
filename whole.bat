@echo off
chcp 65001 >nul
title OIDE 认证系统完整启动器

echo.
echo ========================================
echo    🔐 OIDE 认证系统完整启动器
echo ========================================
echo.

:: 检查Python是否安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.7+
    echo 📥 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✅ Python %%i 环境检查通过
echo.

:: 检查并停止可能占用端口的进程
echo 🔍 检查端口占用...
netstat -an | find ":5000" | find "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ 端口5000已被占用，尝试释放...
    for /f "tokens=5" %%a in ('netstat -aon ^| find ":5000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
)

netstat -an | find ":5500" | find "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo ⚠️ 端口5500已被占用，尝试释放...
    for /f "tokens=5" %%a in ('netstat -aon ^| find ":5500" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
)

:: 检查并安装依赖
echo 📦 检查Python依赖...
if exist "backend\requirements.txt" (
    echo 正在安装后端依赖...
    cd backend
    pip install -r requirements.txt >nul 2>&1
    if errorlevel 1 (
        echo ⚠️ 警告: 依赖安装可能有问题，继续启动...
    ) else (
        echo ✅ 后端依赖安装完成
    )
    cd ..
) else (
    echo ⚠️ 未找到requirements.txt，跳过依赖安装
)

echo.

:: 初始化数据库
echo 🗄️ 初始化数据库...
cd backend
python init_db.py
if errorlevel 1 (
    echo ❌ 数据库初始化失败
    cd ..
    echo.
    echo 🔧 可能的解决方案:
    echo   1. 检查Python环境是否正确
    echo   2. 确保backend目录下有app.py文件
    echo   3. 检查文件权限
    echo.
    pause
    exit /b 1
)
cd ..
echo ✅ 数据库初始化完成
echo.

:: 启动后端服务器（在新窗口中）
echo 🚀 启动后端服务器...
start "OIDE Backend Server - 请勿关闭此窗口" cmd /k "cd /d %~dp0backend && echo 🔧 OIDE 后端服务器 && echo 端口: 5000 && echo 按 Ctrl+C 停止服务器 && echo. && python app.py"

:: 等待后端服务器启动
echo ⏳ 等待后端服务器启动...
timeout /t 3 /nobreak >nul

:: 检查后端服务器是否启动成功
set backend_ok=0
for /l %%i in (1,1,10) do (
    python -c "import requests; requests.get('http://localhost:5000/api/session', timeout=2)" >nul 2>&1
    if not errorlevel 1 (
        set backend_ok=1
        goto backend_check_done
    )
    if %%i lss 10 (
        echo ⏳ 后端服务器启动中... (%%i/10)
        timeout /t 2 /nobreak >nul
    )
)

:backend_check_done
if %backend_ok%==1 (
    echo ✅ 后端服务器启动成功
) else (
    echo ⚠️ 后端服务器可能启动失败，请检查后端窗口
    echo 💡 提示: 查看弹出的后端服务器窗口中的错误信息
)

echo.

:: 启动前端服务器（在新窗口中）
echo 🌐 启动前端服务器...
start "OIDE Frontend Server - 请勿关闭此窗口" cmd /k "cd /d %~dp0frontend && echo 🌐 OIDE 前端服务器 && echo 端口: 5500 && echo 按 Ctrl+C 停止服务器 && echo. && python -m http.server 5500"
cd frontend
pnpm electron .
cd ../

:: 等待前端服务器启动
echo ⏳ 等待前端服务器启动...
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    🎉 系统启动完成！
echo ========================================
echo.
echo 📋 访问信息:
echo   🏠 主页地址: http://localhost:5500/index.html
echo   🔧 后端API:  http://localhost:5000/api
echo   📊 系统状态: 运行 status.bat 检查
echo.
echo 👤 默认测试账户:
echo   👑 管理员:   admin / admin123
echo   👤 测试用户: testuser / password123
echo.
echo 🔧 功能页面:
echo   🏠 主页:     http://localhost:5500/index.html
echo   🔑 登录:     http://localhost:5500/login/index.html
echo   📝 注册:     http://localhost:5500/register/index.html
echo   💻 IDE:      http://localhost:5500/ide/index.html
echo   🛠️ 开发工具: http://localhost:5500/developer/index.html
echo.
echo 📝 重要说明:
echo   ✅ 系统已在后台启动，请勿关闭弹出的服务器窗口
echo   🌐 打开浏览器访问主页地址开始使用
echo   👤 首次使用建议先注册新账户或使用测试账户登录
echo   🛑 停止系统请运行 stop.bat 或关闭所有服务器窗口
echo.

:: 询问是否自动打开浏览器
set /p open_browser="🌐 是否自动打开浏览器? (y/n): "
if /i "%open_browser%"=="y" (
    echo 🌐 正在打开浏览器...
    start http://localhost:5500/index.html
    timeout /t 2 /nobreak >nul
)

echo.
echo 🧪 其他操作:
echo   测试系统: python test_auth_system.py
echo   检查状态: status.bat
echo   停止系统: stop.bat
echo   系统菜单: menu.bat
echo.
echo ⏹️ 要停止系统，请运行 stop.bat 或关闭所有服务器窗口
echo.

:: 保持窗口打开
echo 📋 系统启动完成，按任意键关闭此窗口...
echo    (服务器将继续在后台运行)
pause >nul