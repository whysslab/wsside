@echo off
echo 测试 GCC 自动安装功能
echo.

echo 1. 测试 GCC 检测功能...
node test-gcc-installer.js

echo.
echo 2. 启动 Electron 应用进行完整测试...
echo 请在应用中观察 GCC 状态指示器和首次运行时的自动安装提示
echo.

npm start

pause