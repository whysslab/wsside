const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { exec, spawn } = require('child_process');
const fs = require('fs');
const { spawn: spawnProcess } = require('child_process');
const GCCInstaller = require('./gcc-installer');

// 全局变量
let mainWindow;
let backendProcess = null;
let gccInstaller = new GCCInstaller();

// 启动后端服务器
/*
function startBackendServer() {
  return new Promise((resolve, reject) => {
    const isDev = !app.isPackaged;
    const backendPath = isDev 
      ? path.join(__dirname, '..', 'backend')
      : path.join(process.resourcesPath, 'backend');
    
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const appPath = path.join(backendPath, 'app.py');
    
    console.log('Starting backend server from:', backendPath);
    
    // 检查后端文件是否存在
    if (!fs.existsSync(appPath)) {
      console.error('Backend app.py not found at:', appPath);
      reject(new Error('Backend server not found'));
      return;
    }
    
    backendProcess = spawnProcess(pythonCmd, [appPath], {
      cwd: backendPath,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    
    backendProcess.stdout.on('data', (data) => {
      console.log('Backend:', data.toString());
      if (data.toString().includes('Running on')) {
        resolve();
      }
    });
    
    backendProcess.stderr.on('data', (data) => {
      console.error('Backend Error:', data.toString());
    });
    
    backendProcess.on('error', (error) => {
      console.error('Failed to start backend:', error);
      reject(error);
    });
    
    // 5秒后如果还没启动成功，也认为成功（可能日志没捕获到）
    setTimeout(() => {
      resolve();
    }, 5000);
  });
}
*/
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'ide', 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false, // 允许跨域请求到本地后端
    },
    show: false, // 先不显示，等后端启动完成
  });
  
  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
  
  // 加载主页
  mainWindow.loadFile('index.html');
  
  // 开发模式下打开开发者工具
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }
  
  // 处理外部链接
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
  
  // 添加路由处理
  mainWindow.webContents.on('will-navigate', (event, navigationUrl) => {
    const url = new URL(navigationUrl);
    if (url.pathname.endsWith('/ide/')) {
      event.preventDefault();
      mainWindow.loadFile('ide/index.html');
    }
  });
}

app.whenReady().then(async () => {
  try {
    // 创建窗口（后端服务器启动被注释掉了）
    createWindow();
    
    // 检查是否为首次运行，如果是则检测并安装 GCC
    if (gccInstaller.isFirstRun()) {
      console.log('检测到首次运行，开始检查 GCC 安装状态...');
      // 等待窗口完全加载后再进行 GCC 检测
      setTimeout(async () => {
        await gccInstaller.checkAndInstallGCC(mainWindow);
      }, 2000);
    }
    
  } catch (error) {
    console.error('应用启动时出错:', error);
    // 即使出错也创建窗口
    createWindow();
    
    // 仍然进行 GCC 检测
    if (gccInstaller.isFirstRun()) {
      console.log('检测到首次运行，开始检查 GCC 安装状态...');
      setTimeout(async () => {
        await gccInstaller.checkAndInstallGCC(mainWindow);
      }, 2000);
    }
  }
});

app.on('window-all-closed', () => {
  // 关闭后端服务器
  if (backendProcess) {
    backendProcess.kill();
  }
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// 应用退出时清理
app.on('before-quit', () => {
  if (backendProcess) {
    backendProcess.kill();
  }
});

ipcMain.handle('save-file-dialog', async (event, { defaultName, content }) => {
  const { filePath, canceled } = await dialog.showSaveDialog({
    title: '保存文件',
    defaultPath: defaultName,
    filters: [
      { name: 'C++ 源文件', extensions: ['cpp', 'c', 'h', 'hpp', 'txt'] },
      { name: '所有文件', extensions: ['*'] },
    ],
  });
  if (!filePath || canceled) return { filePath: '', fileName: '' };
  fs.writeFileSync(filePath, content, 'utf-8');
  return { filePath, fileName: path.basename(filePath) };
});

// IPC处理程序
ipcMain.handle('compile-and-run', async (event, params) => {
  let filePath, fileName;
  if (typeof params === 'string') {
    // 兼容旧调用
    filePath = path.join(app.getPath('temp'), 'main.cpp');
    fileName = 'main.cpp';
    fs.writeFileSync(filePath, params, 'utf-8');
  } else {
    filePath = params.filePath;
    fileName = params.fileName;
  }
  if (!filePath || !fileName) return { success: false, output: '未指定文件路径' };
  const dir = path.dirname(filePath);
  const base = path.parse(fileName).name;
  const exePath = path.join(dir, `${base}.exe`);
  return new Promise((resolve) => {
    exec(`g++ "${filePath}" -o "${exePath}"`, (err, stdout, stderr) => {
      if (err) return resolve({ success: false, output: stderr });
      // 运行 exe 并统计用时和返回值，最后 pause
      const runCmd = [
        `call ${exePath}`,
        'pause',
        'exit',
      ].join(' && ');
      spawn('cmd.exe', ['/c', 'start', '', 'cmd.exe', '/k', runCmd], { detached: true });
      resolve({ success: true, output: '编译成功，已运行 exe。' });
    });
  });
});

ipcMain.handle('open-file-dialog', async () => {
  const { filePaths, canceled } = await dialog.showOpenDialog(mainWindow, {
    title: '打开文件',
    filters: [
      { name: 'C++ 源文件', extensions: ['cpp', 'c', 'h', 'hpp'] },
      { name: '文本文件', extensions: ['txt'] },
      { name: '所有文件', extensions: ['*'] },
    ],
    properties: ['openFile']
  });
  
  if (canceled || filePaths.length === 0) {
    return { filePath: '', content: '', fileName: '' };
  }
  
  const filePath = filePaths[0];
  const content = fs.readFileSync(filePath, 'utf-8');
  const fileName = path.basename(filePath);
  
  return { filePath, content, fileName };
});

ipcMain.handle('show-message-box', async (event, options) => {
  return await dialog.showMessageBox(mainWindow, options);
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

// GCC 相关的 IPC 处理程序
ipcMain.handle('check-gcc-installed', async () => {
  return await gccInstaller.checkGCCInstalled();
});

ipcMain.handle('install-gcc', async () => {
  return await gccInstaller.checkAndInstallGCC(mainWindow);
});

ipcMain.handle('force-gcc-check', async () => {
  // 强制进行 GCC 检测（忽略首次运行标记）
  return await gccInstaller.checkAndInstallGCC(mainWindow);
}); 