@echo off
echo 测试构建修复...
echo.

echo 1. 清理旧的构建文件...
if exist dist rmdir /s /q dist

echo 2. 开始构建...
npm run build:win

echo 3. 检查构建结果...
if exist "dist\win-unpacked\resources\app.asar" (
    echo ✅ app.asar 构建成功
) else (
    echo ❌ app.asar 构建失败
    exit /b 1
)

echo 4. 检查 probide 目录是否被包含...
if exist "dist\win-unpacked\probide" (
    echo ✅ probide 目录已包含在构建中
) else (
    echo ❌ probide 目录未包含在构建中
)

echo.
echo 构建完成！请测试以下文件：
echo - dist\win-unpacked\OIDE.exe
echo - 打开后导航到 probide/index.html
echo.
pause