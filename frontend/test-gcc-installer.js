// 测试 GCC 安装器功能的简单脚本
const GCCInstaller = require('./gcc-installer');

async function testGCCInstaller() {
  console.log('开始测试 GCC 安装器...');
  
  const installer = new GCCInstaller();
  
  // 测试 GCC 检测
  console.log('\n1. 测试 GCC 检测功能:');
  const isInstalled = await installer.checkGCCInstalled();
  console.log('GCC 安装状态:', isInstalled ? '已安装' : '未安装');
  
  // 测试首次运行检测
  console.log('\n2. 测试首次运行检测:');
  const isFirstRun = installer.isFirstRun();
  console.log('是否首次运行:', isFirstRun);
  
  console.log('\n测试完成！');
}

// 运行测试
testGCCInstaller().catch(console.error);