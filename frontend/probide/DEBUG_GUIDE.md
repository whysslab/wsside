# ProBIDE 白屏问题调试指南

## 🔍 问题分析

当 `build:win` 后打开 `file:///D:/Documents/GitHub/wsside/frontend/dist/win-unpacked/resources/app.asar/probide/index.html` 出现白屏时，主要原因是：

### 1. 构建配置问题
- ❌ **原因**: `package.json` 的 `build.files` 中缺少 `probide/**/*`
- ✅ **修复**: 已添加 `probide/**/*` 到构建文件列表

### 2. 外部资源加载问题
在 `file://` 协议下，以下外部资源可能被阻止：
- Font Awesome CSS: `https://static.paraflowcontent.com/...`
- Monaco Editor: `https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/...`
- MathJax: `https://cdn.jsdelivr.net/npm/mathjax@3/...`
- Polyfill: `https://polyfill.io/v3/polyfill.min.js`

### 3. 安全策略问题
- ❌ **原因**: 缺少适当的 Content Security Policy
- ✅ **修复**: 已添加宽松的 CSP 头部

## 🛠️ 修复措施

### 1. 构建配置修复
```json
"files": [
  "main.js",
  "gcc-installer.js",
  "index.html",
  "auth.js",
  "electron-auth.js",
  "ide/**/*",
  "probide/**/*",  // ← 新增
  "login/**/*",
  "register/**/*",
  "developer/**/*",
  "assets/**/*",
  "node_modules/**/*",
  "package.json"
]
```

### 2. CSP 头部添加
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: https: http:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https: http:; style-src 'self' 'unsafe-inline' https: http:; img-src 'self' data: https: http:; font-src 'self' data: https: http:; connect-src 'self' https: http: ws: wss:;">
```

### 3. Electron 安全设置
```javascript
webPreferences: {
  preload: path.join(__dirname, 'ide', 'preload.js'),
  nodeIntegration: false,
  contextIsolation: true,
  webSecurity: false,
  allowRunningInsecureContent: true,
  experimentalFeatures: true,
}
```

### 4. 调试信息添加
- 添加了全局错误处理
- 添加了外部资源加载检查
- 添加了详细的控制台日志

## 🧪 测试方法

### 1. 构建测试
```bash
# 运行构建测试脚本
frontend/test-build-fix.bat
```

### 2. 离线版本测试
打开 `frontend/probide/index-offline.html` 测试基本功能

### 3. 调试步骤
1. 构建应用: `npm run build:win`
2. 运行: `dist/win-unpacked/OIDE.exe`
3. 导航到 probide 页面
4. 按 F12 打开开发者工具
5. 查看控制台输出和网络请求

## 🔧 进一步优化建议

### 1. 本地化外部资源
下载并本地化以下资源：
- Font Awesome 字体和 CSS
- Monaco Editor 完整包
- MathJax 库文件

### 2. 资源回退机制
```javascript
// 示例：Font Awesome 回退
if (!fontAwesomeLoaded) {
  // 使用 Unicode 字符或本地图标
  document.body.classList.add('fallback-icons');
}
```

### 3. 渐进式加载
```javascript
// 优先加载核心功能，外部资源异步加载
document.addEventListener('DOMContentLoaded', function() {
  initCoreFeatures();
  loadExternalResources();
});
```

## 📋 检查清单

- [x] 修复 package.json 构建配置
- [x] 添加 CSP 头部
- [x] 更新 Electron 安全设置
- [x] 添加调试信息
- [x] 创建离线测试版本
- [ ] 本地化外部资源（可选）
- [ ] 添加资源加载回退（可选）

## 🚀 快速验证

1. 运行 `frontend/test-build-fix.bat`
2. 如果构建成功，运行生成的 exe 文件
3. 导航到 probide 页面
4. 如果仍有问题，使用 `index-offline.html` 进行基础测试

如果问题仍然存在，请检查：
- 网络连接（外部资源）
- 防火墙设置
- 杀毒软件拦截
- Windows 安全策略