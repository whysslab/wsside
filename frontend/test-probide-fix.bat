@echo off
echo 测试 ProBIDE 白屏修复...
echo.

echo 1. 检查构建文件...
if not exist "dist\win-unpacked\OIDE.exe" (
    echo ❌ 构建文件不存在，请先运行 npm run build:win
    pause
    exit /b 1
)

echo ✅ 构建文件存在

echo 2. 检查 probide 目录...
npx asar list dist/win-unpacked/resources/app.asar | findstr probide > nul
if %errorlevel% equ 0 (
    echo ✅ probide 目录已包含在构建中
) else (
    echo ❌ probide 目录未包含在构建中
    pause
    exit /b 1
)

echo 3. 启动应用进行测试...
echo.
echo 请按照以下步骤测试：
echo 1. 应用启动后，点击主页的 "刷题IDE" 按钮
echo 2. 或者直接在地址栏输入 probide/index.html
echo 3. 检查页面是否正常显示（不再白屏）
echo 4. 按 F12 打开开发者工具查看控制台输出
echo 5. 如果仍有问题，尝试访问 probide/index-offline.html
echo.
echo 启动应用...
start "" "dist\win-unpacked\OIDE.exe"

echo.
echo 测试完成后请报告结果：
echo ✅ 页面正常显示 - 修复成功
echo ❌ 仍然白屏 - 需要进一步调试
echo.
pause