# OIDE - 在线集成开发环境

OIDE (Online Integrated Development Environment) 是一个基于Web的C++集成开发环境，支持代码编辑、编译和运行。

## ✨ 主要特性

### 💻 智能编辑器
- **Monaco Editor**: 基于VS Code的代码编辑器
- **语法高亮**: 完整的C++语法支持
- **自动补全**: 智能代码提示
- **错误检测**: 实时语法错误提示

### ⚡ 编译运行
- **一键编译**: 集成GCC编译器
- **实时输出**: 显示编译信息和程序输出
- **错误提示**: 详细的编译错误信息

### 📁 文件管理
- **新建文件**: 快速创建新的C++文件
- **打开文件**: 支持本地文件导入
- **保存文件**: 下载编辑的代码文件

### 🎨 现代界面
- **响应式设计**: 支持多种设备和屏幕尺寸
- **暗色主题**: 护眼的编程环境
- **直观操作**: 简洁易用的用户界面

## 🛠️ 技术栈

### 前端
- **HTML5 + CSS3 + JavaScript**: 现代Web技术
- **Monaco Editor**: VS Code编辑器核心
- **Font Awesome**: 图标库
- **响应式设计**: 适配多种设备

### 后端 (Electron环境)
- **Node.js**: JavaScript运行时
- **Electron**: 跨平台桌面应用框架
- **GCC编译器**: C++代码编译
- **文件系统API**: 本地文件操作

## 🚀 快速开始

### 方式一：Electron桌面应用

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动Electron应用**
```bash
npm start
```

### 方式二：Web版本

1. **启动前端服务器**
```bash
cd frontend
python server.py
```

2. **访问Web页面**
```
打开浏览器访问: http://localhost:3000
```

### 🎯 使用方法

1. **打开IDE**: 点击"开始编程"按钮
2. **编写代码**: 在编辑器中输入C++代码
3. **编译运行**: 点击"运行"按钮编译并执行代码
4. **查看结果**: 在右侧控制台查看输出结果

## 📁 项目结构

```
oide/
├── frontend/                 # 前端文件
│   ├── index.html           # 主页
│   ├── ide/                 # IDE页面
│   │   ├── index.html       # IDE主页面
│   │   ├── renderer.js      # IDE功能逻辑
│   │   ├── preload.js       # Electron预加载脚本
│   │   └── styles.css       # IDE样式
│   ├── main.js              # Electron主进程
│   ├── server.py            # Web服务器
│   └── package.json         # Node.js依赖
├── build-electron.bat       # Electron构建脚本
├── menu.bat                 # 菜单启动脚本
├── start.bat                # 启动脚本
├── whole.bat                # 完整启动脚本
└── README.md                # 项目说明
```

## 🎯 主要功能

### 📝 代码编辑
- **语法高亮**: 完整的C++语法着色
- **自动缩进**: 智能代码格式化
- **括号匹配**: 自动匹配和高亮显示
- **多主题**: 支持暗色和亮色主题

### ⚙️ 编译运行
- **GCC集成**: 内置GCC编译器支持
- **实时编译**: 快速编译C++代码
- **错误提示**: 详细的编译错误信息
- **程序输出**: 实时显示程序运行结果

### 💾 文件操作
- **新建文件**: 创建新的C++源文件
- **打开文件**: 导入本地C++文件
- **保存文件**: 保存代码到本地
- **文件管理**: 简单直观的文件操作

### 🖥️ 用户界面
- **响应式布局**: 适配不同屏幕尺寸
- **分屏显示**: 编辑器和控制台分屏
- **工具栏**: 常用功能快速访问
- **状态提示**: 实时显示操作状态

## 🔧 开发说明

### 环境要求
- **Node.js**: 14.0 或更高版本
- **GCC编译器**: 用于C++代码编译
- **Python**: 3.7+ (用于Web服务器)

### 自定义配置
- **编辑器主题**: 修改Monaco Editor配置
- **编译器选项**: 调整GCC编译参数
- **界面样式**: 自定义CSS样式文件

### 添加新功能
1. **编辑器功能**: 修改`frontend/ide/renderer.js`
2. **界面样式**: 修改`frontend/ide/styles.css`
3. **Electron功能**: 修改`frontend/main.js`
4. **预加载脚本**: 修改`frontend/ide/preload.js`

### 调试技巧
- **前端调试**: 使用浏览器开发者工具
- **Electron调试**: 使用Electron DevTools
- **编译调试**: 查看控制台编译输出
- **文件操作**: 检查文件系统权限

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 提交 [Issue](../../issues)
- 发起 [Discussion](../../discussions)

---

**注意**: 这是一个教育和演示项目，适合学习C++编程和Web开发技术。