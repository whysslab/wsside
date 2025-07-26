// IDE 配置文件
const IDE_CONFIG = {
    // API 配置
    API: {
        // AI Agent API 地址
        AI_AGENT: 'https://api.ide.whyss.tech/api/ai',
        
        // 后端 API 地址（如果需要）
        BACKEND: 'http://localhost:5000/api'
    },
    
    // 开发模式配置
    DEV: {
        // 开发模式下的 AI Agent API 地址
        AI_AGENT: 'http://localhost:5001/api/ai',
        
        // 开发模式下的后端 API 地址
        BACKEND: 'http://localhost:5000/api'
    },
    
    // 环境检测
    isDevelopment: () => {
        return window.location.hostname === 'localhost' || 
               window.location.hostname === '127.0.0.1' ||
               window.location.port === '5500';
    },
    
    // 获取当前环境的 API 配置
    getApiConfig: () => {
        return IDE_CONFIG.isDevelopment() ? IDE_CONFIG.DEV : IDE_CONFIG.API;
    }
};

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IDE_CONFIG;
} else {
    window.IDE_CONFIG = IDE_CONFIG;
}