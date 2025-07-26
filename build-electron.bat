@echo off
chcp 65001 >nul
title OIDE Electron 构建工具

echo 🔧 OIDE Electron 应用构建工具
echo ================================

:: 检查Node.js环境
echo 🔍 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Node.js，请先安装Node.js
    echo 📥 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version') do echo ✅ Node.js %%i

:: 检查Python环境
echo 🔍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.7+
    echo 📥 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✅ Python %%i

:: 进入frontend目录
cd frontend

:: 检查pnpm
echo 📦 检查包管理器...
pnpm --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 未找到pnpm，尝试安装...
    npm install -g pnpm
    if errorlevel 1 (
        echo ❌ pnpm安装失败，使用npm代替
        set PKG_MANAGER=npm
    ) else (
        set PKG_MANAGER=pnpm
    )
) else (
    set PKG_MANAGER=pnpm
)

echo ✅ 使用包管理器: %PKG_MANAGER%

:: 安装依赖
echo 📦 安装前端依赖...
%PKG_MANAGER% install
if errorlevel 1 (
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)

:: 安装后端依赖
echo 📦 安装后端依赖...
cd ..\backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️ 后端依赖安装可能有问题，继续构建...
)

:: 初始化数据库
echo 🗄️ 初始化数据库...
python init_db.py
if errorlevel 1 (
    echo ❌ 数据库初始化失败
    cd ..\frontend
    pause
    exit /b 1
)

cd ..\frontend

:: 选择构建类型
echo.
echo 🏗️ 选择构建类型:
echo 1. 开发版本 (快速构建，包含调试信息)
echo 2. 生产版本 (完整构建，体积较大)
echo 3. 便携版本 (单文件，无需安装)
echo 4. 仅打包 (不创建安装程序)
echo.

set /p build_type="请选择构建类型 (1-4): "

if "%build_type%"=="1" goto dev_build
if "%build_type%"=="2" goto prod_build
if "%build_type%"=="3" goto portable_build
if "%build_type%"=="4" goto pack_only
goto invalid_choice

:dev_build
echo 🔨 构建开发版本...
%PKG_MANAGER% run build:win -- --config.compression=store --config.nsis.oneClick=false
goto build_complete

:prod_build
echo 🔨 构建生产版本...
%PKG_MANAGER% run build:win
goto build_complete

:portable_build
echo 🔨 构建便携版本...
%PKG_MANAGER% run build:win -- --config.win.target=portable
goto build_complete

:pack_only
echo 📦 仅打包应用...
%PKG_MANAGER% run pack
goto build_complete

:invalid_choice
echo ❌ 无效选择，使用默认构建
%PKG_MANAGER% run build:win
goto build_complete

:build_complete
if errorlevel 1 (
    echo ❌ 构建失败
    echo.
    echo 🔧 可能的解决方案:
    echo   1. 检查Node.js和Python环境
    echo   2. 确保所有依赖已正确安装
    echo   3. 检查磁盘空间是否充足
    echo   4. 查看上方的错误信息
    echo.
    pause
    exit /b 1
)

echo.
echo 🎉 构建完成！
echo ================

:: 检查构建结果
if exist "dist\OIDE Setup 1.0.0.exe" (
    echo ✅ 安装程序: dist\OIDE Setup 1.0.0.exe
)

if exist "dist\OIDE 1.0.0.exe" (
    echo ✅ 便携版本: dist\OIDE 1.0.0.exe
)

if exist "dist\win-unpacked" (
    echo ✅ 解压版本: dist\win-unpacked\
)

echo.
echo 📋 构建信息:
echo   构建目录: %cd%\dist
echo   应用名称: OIDE
echo   版本号: 1.0.0
echo.

:: 询问是否打开构建目录
set /p open_dist="🗂️ 是否打开构建目录? (y/n): "
if /i "%open_dist%"=="y" (
    start explorer dist
)

:: 询问是否运行应用
if exist "dist\win-unpacked\OIDE.exe" (
    set /p run_app="🚀 是否运行构建的应用? (y/n): "
    if /i "%run_app%"=="y" (
        start "" "dist\win-unpacked\OIDE.exe"
    )
)

echo.
echo 💡 使用说明:
echo   - 安装程序: 双击 .exe 文件安装
echo   - 便携版本: 直接运行 .exe 文件
echo   - 解压版本: 运行 win-unpacked 目录中的 OIDE.exe
echo.
echo 🎯 分发建议:
echo   - 给用户: 使用安装程序版本
echo   - 测试用: 使用便携版本
echo   - 开发用: 使用解压版本
echo.

pause