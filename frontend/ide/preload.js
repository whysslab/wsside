const { contextBridge, ipcRenderer } = require('electron');
 
contextBridge.exposeInMainWorld('electronAPI', {
  compileAndRun: (params) => ipcRenderer.invoke('compile-and-run', params),
  saveFileDialog: (defaultName, content) => ipcRenderer.invoke('save-file-dialog', { defaultName, content }),
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  // GCC 相关 API
  checkGCCInstalled: () => ipcRenderer.invoke('check-gcc-installed'),
  installGCC: () => ipcRenderer.invoke('install-gcc'),
  forceGCCCheck: () => ipcRenderer.invoke('force-gcc-check'),
  isElectron: true,
});

// 标识Electron环境
contextBridge.exposeInMainWorld('isElectron', true); 