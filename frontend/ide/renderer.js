/*let editor;
let lastSaveName = 'main.cpp';
let lastSavedContent = '';
let lastSavePath = '';

require.config({ paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' } });
require(['vs/editor/editor.main'], function () {
  editor = monaco.editor.create(document.getElementById('editor'), {
    value: '#include <iostream>\nint main() {\n  std::cout << "Hello, World!";\n  return 0;\n}',
    language: 'cpp',
    theme: 'vs-dark',
    automaticLayout: true,
  });
  lastSavedContent = editor.getValue();
  
  // 将编辑器实例暴露给全局，供 AI Agent 使用
  window.editor = editor;
});

// 新建
const newBtn = document.getElementById('newBtn');
newBtn.onclick = () => {
  const current = editor ? editor.getValue() : '';
  if (current !== lastSavedContent) {
    showModal('新建文件', '当前内容已修改，是否丢弃更改并新建？', () => {
      if (editor) editor.setValue('');
      setCompileInfo('');
      setProgramOutput('');
      lastSaveName = 'main.cpp';
      lastSavedContent = '';
      updateEditorTitle(lastSaveName);
    });
  } else {
    if (editor) editor.setValue('');
    setCompileInfo('');
    setProgramOutput('');
    lastSaveName = 'main.cpp';
    lastSavedContent = '';
    updateEditorTitle(lastSaveName);
  }
};

// 打开
const openBtn = document.getElementById('openBtn');
const openFileInput = document.getElementById('openFileInput');
openBtn.onclick = () => openFileInput.click();
openFileInput.onchange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(evt) {
    if (editor) editor.setValue(evt.target.result);
    setCompileInfo('');
    setProgramOutput('');
    lastSaveName = file.name;
    lastSavedContent = evt.target.result;
    updateEditorTitle(lastSaveName);
  };
  reader.readAsText(file, 'utf-8');
};

// 保存（支持指定路径）
async function saveFileWithDialog(defaultName, content) {
  // Electron 主进程弹出保存对话框
  if (!window.electronAPI.saveFileDialog) {
    // 兼容旧主进程，直接下载
    downloadFile(defaultName, content);
    return '';
  }
  const result = await window.electronAPI.saveFileDialog(defaultName, content);
  if (result && result.filePath) {
    lastSaveName = result.fileName;
    lastSavePath = result.filePath;
    lastSavedContent = content;
    updateEditorTitle(lastSaveName);
    return result.filePath;
  }
  return '';
}

// 保存按钮
const saveBtn = document.getElementById('saveBtn');
saveBtn.onclick = async () => {
  const code = editor ? editor.getValue() : '';
  if (window.electronAPI.saveFileDialog) {
    const filePath = await saveFileWithDialog(lastSaveName, code);
    if (filePath) lastSavedContent = code;
  } else {
    downloadFile(lastSaveName, code);
    lastSavedContent = code;
  }
};

function downloadFile(filename, content) {
  const blob = new Blob([content], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// 设置弹窗
const settingsBtn = document.getElementById('settingsBtn');
settingsBtn.onclick = () => {
  showModal('设置', '这里是预设的设置内容。<br>（可扩展：主题切换、字体大小、快捷键等）');
};

// 帮助弹窗
const helpBtn = document.getElementById('helpBtn');
helpBtn.onclick = () => {
  showModal('帮助', '欢迎使用 C++ Web IDE！<br>主要功能：<ul><li>代码高亮编辑</li><li>一键编译运行</li><li>文件新建/打开/保存</li><li>设置与帮助弹窗</li></ul>如需更多帮助，请联系开发者。');
};

// 弹窗关闭
const modalBackdrop = document.getElementById('modalBackdrop');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalConfirmBtn = document.getElementById('modalConfirmBtn');
let modalCallback = null;
let modalHasConfirm = false;
modalCloseBtn.onclick = () => { hideModal(false); };
modalConfirmBtn.onclick = () => { hideModal(true); };
function showModal(title, content, callback) {
  document.getElementById('modalTitle').innerHTML = title;
  document.getElementById('modalContent').innerHTML = content;
  modalBackdrop.classList.remove('hidden');
  modalCallback = callback || null;
  if (callback) {
    modalConfirmBtn.style.display = '';
    modalHasConfirm = true;
  } else {
    modalConfirmBtn.style.display = 'none';
    modalHasConfirm = false;
  }
}
function hideModal(confirmed) {
  modalBackdrop.classList.add('hidden');
  if (modalCallback && confirmed) {
    modalCallback();
  }
  modalCallback = null;
  modalHasConfirm = false;
}

// 控制台输出
function setCompileInfo(msg, isError) {
  const el = document.getElementById('compileInfo');
  el.textContent = msg || '';
  el.className = 'console-section-content' + (isError ? ' error' : '');
}
function setProgramOutput(msg) {
  const el = document.getElementById('programOutput');
  el.textContent = msg || '';
}
function updateEditorTitle(name) {
  document.getElementById('editorTitle').textContent = name;
}

// 运行
const runBtn = document.getElementById('runBtn');
runBtn.onclick = async () => {
  const code = editor ? editor.getValue() : '';
  // 1. 未保存过的文件先弹窗要求保存
  if (!lastSavePath || code !== lastSavedContent) {
    showModal('保存文件', '运行前请先保存文件。', async () => {
      const filePath = await saveFileWithDialog(lastSaveName, code);
      if (filePath) {
        lastSavedContent = code;
        doCompileAndRun(filePath, lastSaveName);
      }
    });
    return;
  }
  // 2. 已保存，直接编译运行
  doCompileAndRun(lastSavePath, lastSaveName);
};

async function doCompileAndRun(filePath, fileName) {
  setCompileInfo('编译中...');
  setProgramOutput('');
  try {
    const result = await window.electronAPI.compileAndRun({ filePath, fileName });
    if (result.success) {
      setCompileInfo('编译成功，无警告。', false);
      setProgramOutput(result.output || '已弹出 exe 窗口。');
    } else {
      setCompileInfo(result.output || '编译失败', true);
      setProgramOutput('');
    }
  } catch (e) {
    setCompileInfo('运行时发生错误', true);
    setProgramOutput(e.message || '');
  }
} */


  let editor;
let lastSaveName = 'main.cpp';
let lastSavedContent = '';
let lastSavePath = '';

require.config({ paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' } });
require(['vs/editor/editor.main'], function () {
  editor = monaco.editor.create(document.getElementById('editor'), {
    value: '#include <iostream>\nint main() {\n  std::cout << "Hello, World!";\n  return 0;\n}',
    language: 'cpp',
    theme: 'vs-dark',
    automaticLayout: true,
  });
  lastSavedContent = editor.getValue();
  
  // 将编辑器实例暴露给全局，供 AI Agent 使用，这里好像写爆了？
  window.editor = editor; //TODO: Debug
});

// 新建
const newBtn = document.getElementById('newBtn');
newBtn.onclick = () => {
  const current = editor ? editor.getValue() : '';
  if (current !== lastSavedContent) {
    showModal('新建文件', '当前内容已修改，是否丢弃更改并新建？', () => {
      if (editor) editor.setValue('');
      setCompileInfo('');
      setProgramOutput('');
      lastSaveName = 'main.cpp';
      lastSavedContent = '';
      updateEditorTitle(lastSaveName);
    });
  } else {
    if (editor) editor.setValue('');
    setCompileInfo('');
    setProgramOutput('');
    lastSaveName = 'main.cpp';
    lastSavedContent = '';
    updateEditorTitle(lastSaveName);
  }
};

// 打开
const openBtn = document.getElementById('openBtn');
const openFileInput = document.getElementById('openFileInput');
openBtn.onclick = () => openFileInput.click();
openFileInput.onchange = (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(evt) {
    if (editor) editor.setValue(evt.target.result);
    setCompileInfo('');
    setProgramOutput('');
    lastSaveName = file.name;
    lastSavedContent = evt.target.result;
    updateEditorTitle(lastSaveName);
  };
  reader.readAsText(file, 'utf-8');
};

// 保存（支持指定路径）
async function saveFileWithDialog(defaultName, content) {
  // Electron 主进程弹出保存对话框
  if (!window.electronAPI.saveFileDialog) {
    // 兼容旧主进程，直接下载
    downloadFile(defaultName, content);
    return '';
  }
  const result = await window.electronAPI.saveFileDialog(defaultName, content);
  if (result && result.filePath) {
    lastSaveName = result.fileName;
    lastSavePath = result.filePath;
    lastSavedContent = content;
    updateEditorTitle(lastSaveName);
    return result.filePath;
  }
  return '';
}

// 保存按钮
const saveBtn = document.getElementById('saveBtn');
saveBtn.onclick = async () => {
  const code = editor ? editor.getValue() : '';
  if (window.electronAPI.saveFileDialog) {
    const filePath = await saveFileWithDialog(lastSaveName, code);
    if (filePath) lastSavedContent = code;
  } else {
    downloadFile(lastSaveName, code);
    lastSavedContent = code;
  }
};

function downloadFile(filename, content) {
  const blob = new Blob([content], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

// 设置弹窗
/*
const settingsBtn = document.getElementById('settingsBtn');
settingsBtn.onclick = () => {
  showModal('设置', '这里是预设的设置内容。<br>（可扩展：主题切换、字体大小、快捷键等）');
};
*/
// 帮助弹窗
const helpBtn = document.getElementById('helpBtn');
helpBtn.onclick = () => {
  showModal('帮助', '欢迎使用 WSS IDE!<br>主要功能：<ul>每个人都有一双手，你怎么不试试看</ul>如需更多帮助，mailto:orangezhsc#gmail.com。');
};

// 弹窗关闭
const modalBackdrop = document.getElementById('modalBackdrop');
const modalCloseBtn = document.getElementById('modalCloseBtn');
const modalConfirmBtn = document.getElementById('modalConfirmBtn');
let modalCallback = null;
let modalHasConfirm = false;
modalCloseBtn.onclick = () => { hideModal(false); };
modalConfirmBtn.onclick = () => { hideModal(true); };
function showModal(title, content, callback) {
  document.getElementById('modalTitle').innerHTML = title;
  document.getElementById('modalContent').innerHTML = content;
  modalBackdrop.classList.remove('hidden');
  modalCallback = callback || null;
  if (callback) {
    modalConfirmBtn.style.display = '';
    modalHasConfirm = true;
  } else {
    modalConfirmBtn.style.display = 'none';
    modalHasConfirm = false;
  }
}
function hideModal(confirmed) {
  modalBackdrop.classList.add('hidden');
  if (modalCallback && confirmed) {
    modalCallback();
  }
  modalCallback = null;
  modalHasConfirm = false;
}

// 控制台输出
function setCompileInfo(msg, isError) {
  const el = document.getElementById('compileInfo');
  el.textContent = msg || '';
  el.className = 'console-section-content' + (isError ? ' error' : '');
}
function setProgramOutput(msg) {
  const el = document.getElementById('programOutput');
  el.textContent = msg || '';
}
function updateEditorTitle(name) {
  document.getElementById('editorTitle').textContent = name;
}

// 运行
const runBtn = document.getElementById('runBtn');
runBtn.onclick = async () => {
  const code = editor ? editor.getValue() : '';
  // 1. 未保存过的文件先弹窗要求保存
  if (!lastSavePath || code !== lastSavedContent) {
    showModal('保存文件', '运行前请先保存文件。', async () => {
      const filePath = await saveFileWithDialog(lastSaveName, code);
      if (filePath) {
        lastSavedContent = code;
        doCompileAndRun(filePath, lastSaveName);
      }
    });
    return;
  }
  // 2. 已保存，直接编译运行
  doCompileAndRun(lastSavePath, lastSaveName);
};

async function doCompileAndRun(filePath, fileName) {
  // 在编译前检查 GCC 状态
  if (window.electronAPI && window.electronAPI.checkGCCInstalled) {
    const gccInstalled = await window.electronAPI.checkGCCInstalled();
    if (!gccInstalled) {
      showModal('GCC 未安装', 'GCC 编译器未安装或未在 PATH 中找到。<br><br>点击右上角的 GCC 状态指示器可以自动安装。', async () => {
        // 用户确认后尝试安装 GCC
        await installGCC();
      });
      return;
    }
  }
  
  setCompileInfo('编译中...');
  setProgramOutput('');
  try {
    const result = await window.electronAPI.compileAndRun({ filePath, fileName });
    if (result.success) {
      setCompileInfo('编译成功，无警告。', false);
      setProgramOutput(result.output || '已弹出 exe 窗口。');
    } else {
      setCompileInfo(result.output || '编译失败', true);
      setProgramOutput('');
    }
  } catch (e) {
    setCompileInfo('运行时发生错误', true);
    setProgramOutput(e.message || '');
  }
} 

// GCC 状态管理
let gccStatus = {
  installed: false,
  checking: false
};

// 检查 GCC 状态
async function checkGCCStatus() {
  if (!window.electronAPI || !window.electronAPI.checkGCCInstalled) {
    console.log('非 Electron 环境，跳过 GCC 检查');
    return;
  }
  
  gccStatus.checking = true;
  updateGCCStatusDisplay();
  
  try {
    gccStatus.installed = await window.electronAPI.checkGCCInstalled();
    console.log('GCC 状态检查完成:', gccStatus.installed ? '已安装' : '未安装');
  } catch (error) {
    console.error('检查 GCC 状态时出错:', error);
    gccStatus.installed = false;
  }
  
  gccStatus.checking = false;
  updateGCCStatusDisplay();
}

// 更新 GCC 状态显示
function updateGCCStatusDisplay() {
  const statusElement = document.getElementById('gccStatus');
  if (!statusElement) return;
  
  if (gccStatus.checking) {
    statusElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 检查中...';
    statusElement.className = 'gcc-status checking';
  } else if (gccStatus.installed) {
    statusElement.innerHTML = '<i class="fas fa-check-circle"></i> GCC 就绪';
    statusElement.className = 'gcc-status installed';
  } else {
    statusElement.innerHTML = '<i class="fas fa-exclamation-triangle"></i> GCC 未安装';
    statusElement.className = 'gcc-status not-installed';
    statusElement.style.cursor = 'pointer';
    statusElement.onclick = installGCC;
  }
}

// 安装 GCC
async function installGCC() {
  if (!window.electronAPI || !window.electronAPI.forceGCCCheck) {
    showModal('错误', '无法在当前环境中安装 GCC');
    return;
  }
  
  try {
    const success = await window.electronAPI.forceGCCCheck();
    if (success) {
      gccStatus.installed = true;
      updateGCCStatusDisplay();
    }
  } catch (error) {
    console.error('安装 GCC 时出错:', error);
    showModal('错误', '安装 GCC 时出现错误: ' + error.message);
  }
}

// 在页面加载时检查 GCC 状态
document.addEventListener('DOMContentLoaded', function() {
  // 延迟检查 GCC 状态，确保 Electron API 已准备就绪
  setTimeout(checkGCCStatus, 1000);
});

// 关于 ide 和 problem style ide 的 renderer 都一样但是我把 probide 的 copy 过来了之后就没 bug 了这件事
// 重生之我被用在了同父异母的家庭