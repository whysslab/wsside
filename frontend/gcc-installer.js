const { exec } = require('child_process');
const { dialog, shell } = require('electron');
const fs = require('fs');
const path = require('path');
const https = require('https');
const { promisify } = require('util');

const execAsync = promisify(exec);

class GCCInstaller {
  constructor() {
    this.downloadUrl = 'https://api.ide.whyss.tech/api/download/tdm64-gcc';
    this.installerPath = path.join(require('os').tmpdir(), 'tdm64-gcc-installer.exe');
  }

  /**
   * 检测系统是否安装了 GCC
   */
  async checkGCCInstalled() {
    try {
      // Windows 下使用 where 命令检查 gcc 是否在 PATH 中
      const checkCommand = process.platform === 'win32' ? 'where gcc' : 'which gcc';
      await execAsync(checkCommand);
      
      // 如果找到了 gcc，再检查版本
      const { stdout } = await execAsync('gcc --version');
      console.log('GCC 已安装:', stdout.split('\n')[0]);
      return true;
    } catch (error) {
      console.log('GCC 未安装或不在 PATH 中');
      return false;
    }
  }

  /**
   * 下载 GCC 安装包
   */
  async downloadGCCInstaller() {
    return new Promise((resolve, reject) => {
      console.log('开始下载 GCC 安装包...');
      
      const file = fs.createWriteStream(this.installerPath);
      
      https.get(this.downloadUrl, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`下载失败: HTTP ${response.statusCode}`));
          return;
        }

        const totalSize = parseInt(response.headers['content-length'], 10);
        let downloadedSize = 0;

        response.on('data', (chunk) => {
          downloadedSize += chunk.length;
          const progress = ((downloadedSize / totalSize) * 100).toFixed(1);
          console.log(`下载进度: ${progress}%`);
        });

        response.pipe(file);

        file.on('finish', () => {
          file.close();
          console.log('GCC 安装包下载完成');
          resolve(this.installerPath);
        });

        file.on('error', (err) => {
          fs.unlink(this.installerPath, () => {}); // 删除不完整的文件
          reject(err);
        });

      }).on('error', (err) => {
        reject(err);
      });
    });
  }

  /**
   * 运行安装程序
   */
  async runInstaller() {
    return new Promise((resolve, reject) => {
      console.log('启动 GCC 安装程序...');
      
      // 使用 spawn 而不是 exec 来避免超时问题
      const { spawn } = require('child_process');
      const installer = spawn(this.installerPath, [], {
        detached: false,
        stdio: 'ignore'
      });

      installer.on('close', (code) => {
        console.log(`安装程序退出，代码: ${code}`);
        // 清理临时文件
        fs.unlink(this.installerPath, (err) => {
          if (err) console.log('清理临时文件失败:', err);
        });
        
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`安装失败，退出代码: ${code}`));
        }
      });

      installer.on('error', (err) => {
        console.error('启动安装程序失败:', err);
        reject(err);
      });
    });
  }

  /**
   * 显示用户确认对话框
   */
  async showInstallDialog(mainWindow) {
    const result = await dialog.showMessageBox(mainWindow, {
      type: 'question',
      buttons: ['立即安装', '稍后安装', '取消'],
      defaultId: 0,
      title: 'GCC 编译器未找到',
      message: '检测到您的系统未安装 GCC 编译器',
      detail: 'OIDE 需要 GCC 编译器来编译和运行 C++ 代码。\n\n点击"立即安装"将自动下载并安装 TDM-GCC 编译器。\n\n安装完成后可能需要重启应用程序。'
    });

    return result.response;
  }

  /**
   * 显示下载进度对话框
   */
  showDownloadProgress(mainWindow) {
    // 这里可以创建一个进度窗口，暂时使用控制台输出
    console.log('正在下载 GCC 安装包，请稍候...');
  }

  /**
   * 主要的检测和安装流程
   */
  async checkAndInstallGCC(mainWindow) {
    try {
      // 检查是否已安装 GCC
      const isInstalled = await this.checkGCCInstalled();
      
      if (isInstalled) {
        console.log('GCC 已安装，无需重复安装');
        return true;
      }

      // 显示安装确认对话框
      const userChoice = await this.showInstallDialog(mainWindow);
      
      if (userChoice === 0) { // 立即安装
        try {
          // 显示下载进度
          this.showDownloadProgress(mainWindow);
          
          // 下载安装包
          await this.downloadGCCInstaller();
          
          // 运行安装程序
          await this.runInstaller();
          
          // 安装完成后再次检查
          const installSuccess = await this.checkGCCInstalled();
          
          if (installSuccess) {
            await dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '安装成功',
              message: 'GCC 编译器安装成功！',
              detail: '现在您可以正常编译和运行 C++ 代码了。'
            });
            return true;
          } else {
            await dialog.showMessageBox(mainWindow, {
              type: 'warning',
              title: '安装完成',
              message: '安装程序已运行完成',
              detail: '如果安装成功，您可能需要重启应用程序或重新打开命令提示符。\n\n如果仍然无法使用 GCC，请检查系统环境变量 PATH 设置。'
            });
            return false;
          }
          
        } catch (error) {
          console.error('安装过程中出错:', error);
          await dialog.showMessageBox(mainWindow, {
            type: 'error',
            title: '安装失败',
            message: '安装 GCC 编译器时出现错误',
            detail: `错误信息: ${error.message}\n\n您可以稍后手动重试，或访问 TDM-GCC 官网手动下载安装。`
          });
          return false;
        }
        
      } else if (userChoice === 1) { // 稍后安装
        console.log('用户选择稍后安装 GCC');
        return false;
      } else { // 取消
        console.log('用户取消安装 GCC');
        return false;
      }
      
    } catch (error) {
      console.error('检测 GCC 时出错:', error);
      return false;
    }
  }

  /**
   * 检查是否为首次运行
   */
  isFirstRun() {
    const configPath = path.join(require('os').homedir(), '.oide-config.json');
    
    if (!fs.existsSync(configPath)) {
      // 创建配置文件标记已运行过
      const config = {
        firstRun: false,
        installDate: new Date().toISOString()
      };
      
      try {
        fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
      } catch (error) {
        console.error('创建配置文件失败:', error);
      }
      
      return true;
    }
    
    return false;
  }
}

module.exports = GCCInstaller;