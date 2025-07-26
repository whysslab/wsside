const { contextBridge, ipcRenderer } = require('electron');
 
contextBridge.exposeInMainWorld('electronAPI', {
  compileAndRun: (params) => ipcRenderer.invoke('compile-and-run', params),
  saveFileDialog: (defaultName, content) => ipcRenderer.invoke('save-file-dialog', { defaultName, content }),
  openFileDialog: () => ipcRenderer.invoke('open-file-dialog'),
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  isElectron: true,
});

contextBridge.exposeInMainWorld('isElectron', true); 