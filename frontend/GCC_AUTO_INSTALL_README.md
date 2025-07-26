# GCC 自动安装功能说明

## 功能概述

本功能为 OIDE Electron 应用添加了 GCC 编译器的自动检测和安装功能，确保用户能够顺利编译和运行 C++ 代码。

## 主要特性

### 1. 首次运行检测
- 应用首次启动时会自动检测系统是否安装了 GCC 编译器
- 如果未安装，会弹出安装确认对话框
- 用户可以选择立即安装、稍后安装或取消

### 2. 实时状态显示
- IDE 工具栏中显示 GCC 状态指示器
- 三种状态：
  - 🔄 检查中... (灰色)
  - ✅ GCC 就绪 (绿色)
  - ⚠️ GCC 未安装 (红色，可点击安装)

### 3. 自动下载安装
- 从 `api.ide.whyss.tech/api/download/tdm64-gcc` 下载 TDM-GCC 安装包
- 显示下载进度
- 自动启动安装程序
- 安装完成后重新检测状态

### 4. 编译前检查
- 运行代码前会检查 GCC 是否可用
- 如果未安装会提示用户安装
- 确保编译环境正常

## 文件结构

```
frontend/
├── gcc-installer.js          # GCC 安装器核心模块
├── main.js                   # 主进程，集成了 GCC 检测
├── ide/
│   ├── preload.js            # 暴露 GCC 相关 API
│   ├── index.html            # IDE 界面，添加了状态显示
│   └── renderer.js           # 渲染进程，处理 GCC 状态
├── test-gcc-installer.js     # 测试脚本
├── test-gcc-feature.bat      # 测试启动脚本
└── GCC_AUTO_INSTALL_README.md # 本说明文件
```

## API 接口

### 主进程 IPC 处理程序
- `check-gcc-installed`: 检查 GCC 是否已安装
- `install-gcc`: 执行 GCC 安装流程
- `force-gcc-check`: 强制进行 GCC 检测（忽略首次运行标记）

### 渲染进程 API
- `window.electronAPI.checkGCCInstalled()`: 检查 GCC 状态
- `window.electronAPI.installGCC()`: 安装 GCC
- `window.electronAPI.forceGCCCheck()`: 强制检查 GCC

## 使用方法

### 开发者
1. 确保所有文件都已正确放置
2. 运行 `npm start` 启动应用
3. 观察 GCC 状态指示器
4. 测试编译功能

### 用户
1. 首次启动应用时，如果系统未安装 GCC，会自动弹出安装提示
2. 点击"立即安装"开始自动下载和安装过程
3. 安装完成后，GCC 状态指示器会显示为绿色"GCC 就绪"
4. 现在可以正常编译和运行 C++ 代码

## 配置文件

应用会在用户主目录创建 `.oide-config.json` 配置文件：
```json
{
  "firstRun": false,
  "installDate": "2025-01-27T..."
}
```

## 故障排除

### GCC 检测失败
- 检查系统 PATH 环境变量
- 手动运行 `gcc --version` 验证安装
- 重启应用或系统

### 下载失败
- 检查网络连接
- 确认下载 URL 可访问
- 手动下载安装包

### 安装失败
- 以管理员权限运行应用
- 检查系统权限设置
- 手动安装 TDM-GCC

## 技术实现

### 核心模块 (gcc-installer.js)
- 使用 Node.js child_process 检测 GCC
- 使用 https 模块下载安装包
- 使用 Electron dialog 显示用户界面

### 集成方式
- 主进程启动时进行首次检测
- 渲染进程实时显示状态
- IPC 通信协调前后端

### 安全考虑
- 验证下载文件完整性
- 用户确认后才执行安装
- 清理临时文件

## 扩展建议

1. 添加其他编译器支持 (Clang, MSVC)
2. 支持自定义下载源
3. 添加安装进度条
4. 支持离线安装包
5. 添加编译器版本管理

## 更新日志

### v1.0.0 (2025-01-27)
- 初始版本
- 支持 TDM-GCC 自动下载安装
- 实时状态显示
- 首次运行检测