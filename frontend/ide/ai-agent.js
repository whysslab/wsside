// AI Agent 功能模块
class AIAgent {
    constructor() {
        this.apiBase = window.IDE_CONFIG ? window.IDE_CONFIG.getApiConfig().AI_AGENT : 'https://api.ide.whyss.tech/api/ai';
//zeabur && ppio yyds
        this.sessionId = this.generateSessionId();
        this.isStreaming = false;
        this.currentController = null;
        this.settings = {
            autoExpandThinking: false, // 是否默认展开思考过程
            showThinkingStats: true    // 是否显示思考过程统计信息
        };
        this.init();
    }

    generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    init() {
        this.loadSettings();
        this.createAITab();
        this.setupEventListeners();
        this.loadHistory();
    }

    createAITab() {
        // 添加 AI Agent 标签到控制台标签栏
        const consoleTabs = document.querySelector('.console-tabs');
        const aiTab = document.createElement('button');
        aiTab.id = 'aiTab';
        aiTab.textContent = 'AI Assistant';
        aiTab.style.cssText = `
            background: none;
            border: none;
            color: #a8b2bf;
            font-size: 14px;
            font-weight: 500;
            padding: 8px 16px;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        `;

        // 插入到控制台标签后面
        const consoleTab = document.getElementById('consoleTab');
        consoleTab.insertAdjacentElement('afterend', aiTab);

        // 创建 AI Agent 内容面板
        this.createAIPanel();

        // 设置标签切换逻辑
        this.setupTabSwitching();
    }

    createAIPanel() {
        const consoleContent = document.getElementById('consoleContent');

        // 创建 AI 面板
        const aiPanel = document.createElement('div');
        aiPanel.id = 'aiPanel';
        aiPanel.className = 'hidden';
        aiPanel.style.cssText = `
            height: 100%;
            display: flex;
            flex-direction: column;
            padding: 0;
        `;

        aiPanel.innerHTML = `
            <div id="aiChatContainer" style="
                flex: 1;
                overflow-y: auto;
                padding: 16px;
                background: #1a1d21;
                border-bottom: 1px solid #3c424d;
            ">
                <div id="aiChatHistory"></div>
            </div>
            <div id="aiInputContainer" style="
                padding: 16px;
                background: #24282f;
                border-top: 1px solid #3c424d;
            ">
                <div style="display: flex; gap: 8px; margin-bottom: 8px; flex-wrap: wrap;">
                    <button id="clearHistoryBtn" style="
                        background: #3c424d;
                        color: #e0e0e0;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        cursor: pointer;
                    ">清除历史</button>
                    <button id="insertCodeBtn" style="
                        background: #3c424d;
                        color: #e0e0e0;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        cursor: pointer;
                    ">插入代码</button>
                    <button id="explainCodeBtn" style="
                        background: #3c424d;
                        color: #e0e0e0;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        cursor: pointer;
                    ">解释代码</button>
                    <button id="optimizeCodeBtn" style="
                        background: #3c424d;
                        color: #e0e0e0;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        cursor: pointer;
                    ">优化代码</button>
                    <button id="debugCodeBtn" style="
                        background: #3c424d;
                        color: #e0e0e0;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        cursor: pointer;
                    ">调试帮助</button>
                    <button id="aiSettingsBtn" style="
                        background: #3c424d;
                        color: #e0e0e0;
                        border: none;
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-size: 12px;
                        cursor: pointer;
                        margin-left: auto;
                    " title="AI 助手设置">⚙️</button>
                </div>
                <div style="display: flex; gap: 8px;">
                    <textarea id="aiInput" placeholder="询问 AI 助手..." style="
                        flex: 1;
                        background: #3c424d;
                        color: #e0e0e0;
                        border: 1px solid #505664;
                        border-radius: 4px;
                        padding: 8px;
                        font-size: 14px;
                        resize: vertical;
                        min-height: 36px;
                        max-height: 120px;
                        font-family: inherit;
                    "></textarea>
                    <button id="aiSendBtn" style="
                        background: #89b4fa;
                        color: #181d21;
                        border: none;
                        border-radius: 4px;
                        padding: 8px 16px;
                        font-size: 14px;
                        font-weight: 500;
                        cursor: pointer;
                        white-space: nowrap;
                    ">发送</button>
                </div>
            </div>
        `;

        consoleContent.appendChild(aiPanel);
    }

    setupTabSwitching() {
        const consoleTab = document.getElementById('consoleTab');
        const aiTab = document.getElementById('aiTab');
        const consoleContent = document.querySelector('.console-content > div:not(#aiPanel)');
        const aiPanel = document.getElementById('aiPanel');

        // 控制台标签点击
        consoleTab.addEventListener('click', () => {
            this.switchToTab('console');
        });

        // AI 标签点击
        aiTab.addEventListener('click', () => {
            this.switchToTab('ai');
        });

        // 默认显示控制台
        this.switchToTab('console');
    }

    switchToTab(tab) {
        const consoleTab = document.getElementById('consoleTab');
        const aiTab = document.getElementById('aiTab');
        const consoleContent = document.querySelector('.console-content');
        const aiPanel = document.getElementById('aiPanel');

        if (tab === 'console') {
            // 激活控制台标签
            consoleTab.style.color = '#89b4fa';
            consoleTab.style.borderBottomColor = '#89b4fa';
            aiTab.style.color = '#a8b2bf';
            aiTab.style.borderBottomColor = 'transparent';

            // 显示控制台内容
            Array.from(consoleContent.children).forEach(child => {
                if (child.id !== 'aiPanel') {
                    child.classList.remove('hidden');
                }
            });
            aiPanel.classList.add('hidden');
        } else {
            // 激活 AI 标签
            aiTab.style.color = '#89b4fa';
            aiTab.style.borderBottomColor = '#89b4fa';
            consoleTab.style.color = '#a8b2bf';
            consoleTab.style.borderBottomColor = 'transparent';

            // 显示 AI 面板
            Array.from(consoleContent.children).forEach(child => {
                if (child.id !== 'aiPanel') {
                    child.classList.add('hidden');
                }
            });
            aiPanel.classList.remove('hidden');
        }
    }

    setupEventListeners() {
        // 按钮事件监听
        document.addEventListener('click', (e) => {
            if (e.target.id === 'aiSendBtn') {
                this.sendMessage();
            } else if (e.target.id === 'clearHistoryBtn') {
                this.clearHistory();
            } else if (e.target.id === 'insertCodeBtn') {
                this.insertCurrentCode();
            } else if (e.target.id === 'explainCodeBtn') {
                this.explainCode();
            } else if (e.target.id === 'optimizeCodeBtn') {
                this.optimizeCode();
            } else if (e.target.id === 'debugCodeBtn') {
                this.debugCode();
            } else if (e.target.id === 'aiSettingsBtn') {
                this.showSettings();
            }
        });

        // 输入框回车发送
        document.addEventListener('keydown', (e) => {
            if (e.target.id === 'aiInput' && e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        const input = document.getElementById('aiInput');
        const message = input.value.trim();

        if (!message || this.isStreaming) return;

        // 清空输入框
        input.value = '';

        // 添加用户消息到聊天历史
        this.addMessageToHistory('user', message);

        // 开始流式响应
        this.isStreaming = true;
        this.updateSendButton(true);

        // 创建助手消息容器
        const assistantMessageDiv = this.addMessageToHistory('assistant', '正在思考...');
        const contentDiv = assistantMessageDiv.querySelector('.message-content');

        try {
            // 检查服务是否可用
            const healthResponse = await fetch(`${this.apiBase}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                mode: 'cors'
            });
            if (!healthResponse.ok) {
                throw new Error('AI 服务暂时不可用，请稍后重试');
            }

            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                }),
                mode: 'cors',
                signal: this.currentController?.signal
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`服务器错误 (${response.status}): ${errorText}`);
            }

            // 清空"正在思考"提示
            contentDiv.textContent = '';

            // 处理流式响应
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let hasContent = false;
            let fullContent = ''; // 累积完整内容

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // 保留不完整的行

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const data = JSON.parse(line.slice(6));
                            if (data.content) {
                                fullContent += data.content;
                                hasContent = true;

                                // 实时更新显示，但需要重新处理思考内容
                                const processedContent = this.processThinkingContent(fullContent);
                                contentDiv.innerHTML = processedContent;
                                this.scrollToBottom();
                            } else if (data.done) {
                                if (!hasContent) {
                                    contentDiv.textContent = '抱歉，我没有收到有效的回复。请重试。';
                                } else {
                                    // 最终处理完整内容
                                    const finalProcessedContent = this.processThinkingContent(fullContent);
                                    contentDiv.innerHTML = finalProcessedContent;
                                }
                                this.isStreaming = false;
                                this.updateSendButton(false);
                            } else if (data.error) {
                                throw new Error(data.error);
                            }
                        } catch (e) {
                            console.warn('解析流数据失败:', e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error('发送消息失败:', error);

            // 更新助手消息显示错误
            contentDiv.textContent = `抱歉，发生了错误: ${error.message}`;
            contentDiv.style.color = '#ff6b6b';

            // 添加重试建议
            setTimeout(() => {
                const retryBtn = document.createElement('button');
                retryBtn.textContent = '重试';
                retryBtn.style.cssText = `
                    background: #89b4fa;
                    color: #181d21;
                    border: none;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 12px;
                    cursor: pointer;
                    margin-left: 8px;
                `;
                retryBtn.onclick = () => {
                    input.value = message;
                    assistantMessageDiv.remove();
                    this.sendMessage();
                };
                contentDiv.appendChild(retryBtn);
            }, 100);
        } finally {
            this.isStreaming = false;
            this.updateSendButton(false);
        }
    }

    addMessageToHistory(role, content) {
        const chatHistory = document.getElementById('aiChatHistory');
        const messageDiv = document.createElement('div');

        const roleColors = {
            user: '#89b4fa',
            assistant: '#3ecf8e',
            system: '#ff6b6b'
        };

        const roleNames = {
            user: '你',
            assistant: 'AI',
            system: '系统'
        };

        messageDiv.style.cssText = `
            margin-bottom: 16px;
            padding: 12px;
            background: #24282f;
            border-radius: 8px;
            border-left: 3px solid ${roleColors[role]};
        `;

        // 处理思考过程内容
        const processedContent = this.processThinkingContent(content);

        messageDiv.innerHTML = `
            <div style="
                color: ${roleColors[role]};
                font-size: 12px;
                font-weight: 500;
                margin-bottom: 4px;
            ">${roleNames[role]}</div>
            <div class="message-content" style="
                color: #e0e0e0;
                font-size: 14px;
                line-height: 1.5;
                white-space: pre-wrap;
                word-wrap: break-word;
            ">${processedContent}</div>
        `;

        chatHistory.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    processThinkingContent(content) {
        // 检测是否包含 <think> 标签
        const thinkRegex = /<think>([\s\S]*?)<\/think>/g;
        let match;
        let processedContent = content;
        let thinkingBlocks = [];

        // 提取所有思考块
        while ((match = thinkRegex.exec(content)) !== null) {
            thinkingBlocks.push({
                fullMatch: match[0],
                thinkingContent: match[1].trim()
            });
        }

        // 如果没有思考块，直接返回原内容
        if (thinkingBlocks.length === 0) {
            return content;
        }

        // 替换思考块为可折叠的 UI
        thinkingBlocks.forEach((block, index) => {
            const thinkingId = `thinking-${Date.now()}-${index}`;
            const wordCount = block.thinkingContent.length;
            const lineCount = block.thinkingContent.split('\n').length;
            const isExpanded = this.settings.autoExpandThinking;
            const displayStyle = isExpanded ? 'block' : 'none';
            const iconText = isExpanded ? '▼' : '▶';
            const iconTransform = isExpanded ? 'rotate(90deg)' : 'rotate(0deg)';

            const statsHtml = this.settings.showThinkingStats ? `
                <span style="
                    margin-left: auto; 
                    font-size: 10px; 
                    opacity: 0.6;
                    background: #3c424d;
                    padding: 2px 6px;
                    border-radius: 10px;
                ">${wordCount} 字符 · ${lineCount} 行</span>
            ` : '';

            const thinkingUI = `
                <div class="thinking-container" style="
                    margin: 12px 0;
                    border: 1px solid #3c424d;
                    border-radius: 8px;
                    background: #1a1d21;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                ">
                    <div class="thinking-header" onclick="toggleThinking('${thinkingId}')" style="
                        padding: 10px 14px;
                        background: linear-gradient(135deg, #2a2d35 0%, #24282f 100%);
                        border-radius: 8px 8px 0 0;
                        cursor: pointer;
                        display: flex;
                        align-items: center;
                        font-size: 12px;
                        color: #a8b2bf;
                        user-select: none;
                        transition: background 0.2s ease;
                        border-bottom: 1px solid #3c424d;
                    ">
                        <span id="${thinkingId}-icon" class="thinking-icon" style="
                            margin-right: 8px;
                            transition: transform 0.2s ease;
                            font-size: 10px;
                            color: #89b4fa;
                            transform: ${iconTransform};
                        ">${iconText}</span>
                        <span style="color: #89b4fa; font-weight: 500;">💭 AI 思考过程</span>
                        ${statsHtml}
                    </div>
                    <div id="${thinkingId}" class="thinking-content" style="
                        padding: 16px;
                        display: ${displayStyle};
                        font-size: 13px;
                        color: #c9d1d9;
                        background: #1a1d21;
                        border-radius: 0 0 8px 8px;
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        line-height: 1.5;
                        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
                        border-top: 1px solid #2a2d35;
                        max-height: 400px;
                        overflow-y: auto;
                    ">${this.escapeHtml(block.thinkingContent)}</div>
                </div>
            `;

            processedContent = processedContent.replace(block.fullMatch, thinkingUI);
        });

        return processedContent;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateSendButton(isLoading) {
        const sendBtn = document.getElementById('aiSendBtn');
        if (isLoading) {
            sendBtn.textContent = '发送中...';
            sendBtn.disabled = true;
            sendBtn.style.opacity = '0.6';
        } else {
            sendBtn.textContent = '发送';
            sendBtn.disabled = false;
            sendBtn.style.opacity = '1';
        }
    }

    scrollToBottom() {
        const chatContainer = document.getElementById('aiChatContainer');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    async loadHistory() {
        try {
            const response = await fetch(`${this.apiBase}/history/${this.sessionId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                mode: 'cors'
            });
            if (response.ok) {
                const data = await response.json();
                const history = data.history || [];

                // 清空当前历史
                document.getElementById('aiChatHistory').innerHTML = '';

                // 重新加载历史消息
                history.forEach(msg => {
                    this.addMessageToHistory(msg.role, msg.content);
                });
            }
        } catch (error) {
            console.warn('加载历史记录失败:', error);
        }
    }

    async clearHistory() {
        if (!confirm('确定要清除所有对话历史吗？')) return;

        try {
            const response = await fetch(`${this.apiBase}/history/${this.sessionId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                },
                mode: 'cors'
            });

            if (response.ok) {
                document.getElementById('aiChatHistory').innerHTML = '';
                this.addMessageToHistory('system', '对话历史已清除');
            }
        } catch (error) {
            console.error('清除历史失败:', error);
            this.addMessageToHistory('system', '清除历史失败: ' + error.message);
        }
    }

    insertCurrentCode() {
        if (!window.editor) {
            this.addMessageToHistory('system', '编辑器未初始化');
            return;
        }

        const code = window.editor.getValue();
        if (!code.trim()) {
            this.addMessageToHistory('system', '当前编辑器为空');
            return;
        }

        const input = document.getElementById('aiInput');
        const currentValue = input.value;
        const codeBlock = `\n\`\`\`cpp\n${code}\n\`\`\`\n`;

        input.value = currentValue + (currentValue ? '\n' : '') + '请帮我分析这段代码：' + codeBlock;
        input.focus();
    }

    explainCode() {
        const code = this.getCurrentCode();
        if (!code) return;

        const input = document.getElementById('aiInput');
        input.value = `请详细解释这段 C++ 代码的功能和逻辑：\n\`\`\`cpp\n${code}\n\`\`\``;
        this.sendMessage();
    }

    optimizeCode() {
        const code = this.getCurrentCode();
        if (!code) return;

        const input = document.getElementById('aiInput');
        input.value = `请帮我优化这段 C++ 代码，提供更高效或更清晰的实现：\n\`\`\`cpp\n${code}\n\`\`\``;
        this.sendMessage();
    }

    debugCode() {
        const code = this.getCurrentCode();
        if (!code) return;

        const input = document.getElementById('aiInput');
        input.value = `请帮我检查这段 C++ 代码是否有错误或潜在问题：\n\`\`\`cpp\n${code}\n\`\`\``;
        this.sendMessage();
    }

    getCurrentCode() {
        if (!window.editor) {
            this.addMessageToHistory('system', '编辑器未初始化');
            return null;
        }

        const code = window.editor.getValue();
        if (!code.trim()) {
            this.addMessageToHistory('system', '当前编辑器为空');
            return null;
        }

        return code;
    }

    showSettings() {
        const settingsHtml = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(0,0,0,0.5);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            " id="aiSettingsModal">
                <div style="
                    background: #24282f;
                    border-radius: 8px;
                    padding: 24px;
                    min-width: 320px;
                    max-width: 480px;
                    border: 1px solid #3c424d;
                ">
                    <h3 style="
                        color: #e0e0e0;
                        margin: 0 0 16px 0;
                        font-size: 16px;
                        display: flex;
                        align-items: center;
                    ">
                        <span style="margin-right: 8px;">⚙️</span>
                        AI 助手设置
                    </h3>
                    
                    <div style="margin-bottom: 16px;">
                        <label style="
                            display: flex;
                            align-items: center;
                            color: #e0e0e0;
                            font-size: 14px;
                            cursor: pointer;
                        ">
                            <input type="checkbox" id="autoExpandThinking" ${this.settings.autoExpandThinking ? 'checked' : ''} style="
                                margin-right: 8px;
                                accent-color: #89b4fa;
                            ">
                            默认展开思考过程
                        </label>
                        <div style="
                            color: #a8b2bf;
                            font-size: 12px;
                            margin-left: 20px;
                            margin-top: 4px;
                        ">新消息中的思考过程将自动展开显示</div>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="
                            display: flex;
                            align-items: center;
                            color: #e0e0e0;
                            font-size: 14px;
                            cursor: pointer;
                        ">
                            <input type="checkbox" id="showThinkingStats" ${this.settings.showThinkingStats ? 'checked' : ''} style="
                                margin-right: 8px;
                                accent-color: #89b4fa;
                            ">
                            显示思考过程统计
                        </label>
                        <div style="
                            color: #a8b2bf;
                            font-size: 12px;
                            margin-left: 20px;
                            margin-top: 4px;
                        ">在思考过程标题栏显示字符数和行数</div>
                    </div>
                    
                    <div style="
                        display: flex;
                        gap: 8px;
                        justify-content: flex-end;
                    ">
                        <button onclick="window.aiAgent.closeSettings()" style="
                            background: #3c424d;
                            color: #e0e0e0;
                            border: none;
                            border-radius: 4px;
                            padding: 8px 16px;
                            font-size: 14px;
                            cursor: pointer;
                        ">取消</button>
                        <button onclick="window.aiAgent.saveSettings()" style="
                            background: #89b4fa;
                            color: #181d21;
                            border: none;
                            border-radius: 4px;
                            padding: 8px 16px;
                            font-size: 14px;
                            font-weight: 500;
                            cursor: pointer;
                        ">保存</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', settingsHtml);
    }

    saveSettings() {
        const autoExpandThinking = document.getElementById('autoExpandThinking').checked;
        const showThinkingStats = document.getElementById('showThinkingStats').checked;

        this.settings.autoExpandThinking = autoExpandThinking;
        this.settings.showThinkingStats = showThinkingStats;

        // 保存到本地存储
        localStorage.setItem('aiAgentSettings', JSON.stringify(this.settings));

        this.closeSettings();
        this.addMessageToHistory('system', '设置已保存');
    }

    closeSettings() {
        const modal = document.getElementById('aiSettingsModal');
        if (modal) {
            modal.remove();
        }
    }

    loadSettings() {
        try {
            const saved = localStorage.getItem('aiAgentSettings');
            if (saved) {
                this.settings = { ...this.settings, ...JSON.parse(saved) };
            }
        } catch (e) {
            console.warn('加载设置失败:', e);
        }
    }
}

// 代码补全功能
class CodeCompletion {
    constructor() {
        this.apiBase = window.IDE_CONFIG ? window.IDE_CONFIG.getApiConfig().AI_AGENT : 'https://api.ide.whyss.tech/api/ai';
        this.isCompleting = false;
        this.completionTimeout = null;
        this.init();
    }

    init() {
        // 等待编辑器初始化
        const checkEditor = () => {
            if (window.editor) {
                this.setupCompletion();
            } else {
                setTimeout(checkEditor, 100);
            }
        };
        checkEditor();
    }

    setupCompletion() {
        // 监听 Ctrl+Space 进行代码补全
        window.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space, () => {
            this.triggerCompletion();
        });

        // 监听 Tab 键进行代码补全
        window.editor.onKeyDown((e) => {
            if (e.keyCode === monaco.KeyCode.Tab && !e.shiftKey && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                this.triggerCompletion();
            }
        });

        // 自动补全提示
        monaco.languages.registerCompletionItemProvider('cpp', {
            provideCompletionItems: (model, position) => {
                return this.provideCompletionItems(model, position);
            }
        });
    }

    async triggerCompletion() {
        if (this.isCompleting) return;

        const model = window.editor.getModel();
        const position = window.editor.getPosition();

        // 获取当前行内容，判断是否需要补全
        const currentLine = model.getLineContent(position.lineNumber);
        const beforeCursor = currentLine.substring(0, position.column - 1);

        // 如果当前行为空或只有空格，跳过补全
        if (!beforeCursor.trim()) {
            // 插入制表符
            window.editor.executeEdits('tab-indent', [{
                range: new monaco.Range(
                    position.lineNumber,
                    position.column,
                    position.lineNumber,
                    position.column
                ),
                text: '  ' // 两个空格作为缩进
            }]);
            return;
        }

        // 获取当前位置前后的代码
        const prefix = model.getValueInRange({
            startLineNumber: Math.max(1, position.lineNumber - 10), // 只取前10行作为上下文
            startColumn: 1,
            endLineNumber: position.lineNumber,
            endColumn: position.column
        });

        const suffix = model.getValueInRange({
            startLineNumber: position.lineNumber,
            startColumn: position.column,
            endLineNumber: Math.min(model.getLineCount(), position.lineNumber + 5), // 只取后5行作为上下文
            endColumn: model.getLineMaxColumn(Math.min(model.getLineCount(), position.lineNumber + 5))
        });

        this.isCompleting = true;

        try {
            const response = await fetch(`${this.apiBase}/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prefix: prefix,
                    suffix: suffix,
                    language: 'cpp'
                }),
                mode: 'cors'
            });

            if (response.ok) {
                const data = await response.json();
                let completion = data.completion;

                if (completion && completion.trim()) {
                    // 清理补全内容，移除可能的代码块标记
                    completion = completion.replace(/^```cpp\n?/, '').replace(/\n?```$/, '');

                    // 插入补全内容
                    window.editor.executeEdits('ai-completion', [{
                        range: new monaco.Range(
                            position.lineNumber,
                            position.column,
                            position.lineNumber,
                            position.column
                        ),
                        text: completion
                    }]);

                    // 显示补全提示
                    this.showCompletionHint();
                }
            }
        } catch (error) {
            console.warn('代码补全失败:', error);
        } finally {
            this.isCompleting = false;
        }
    }

    async provideCompletionItems(model, position) {
        // 简单的本地补全项
        const suggestions = [
            {
                label: 'cout',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: 'std::cout << ${1:text} << std::endl;',
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: 'C++ 标准输出'
            },
            {
                label: 'cin',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: 'std::cin >> ${1:variable};',
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: 'C++ 标准输入'
            },
            {
                label: 'for',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: 'for (${1:int i = 0}; ${2:i < n}; ${3:i++}) {\n\t${4:// code}\n}',
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: 'for 循环'
            },
            {
                label: 'if',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: 'if (${1:condition}) {\n\t${2:// code}\n}',
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: 'if 条件语句'
            }
        ];

        return { suggestions };
    }

    showCompletionHint() {
        // 可以在这里添加补全提示的视觉反馈
        console.log('AI 代码补全完成');
    }
}

// 全局函数：切换思考过程显示
window.toggleThinking = function (thinkingId) {
    const content = document.getElementById(thinkingId);
    const icon = document.getElementById(thinkingId + '-icon');

    if (content && icon) {
        // 获取当前显示状态，考虑计算样式而不仅仅是内联样式
        const computedStyle = window.getComputedStyle(content);
        const isHidden = computedStyle.display === 'none' || content.style.display === 'none';

        // 防止重复点击导致的动画冲突
        if (content.dataset.animating === 'true') {
            return;
        }

        content.dataset.animating = 'true';

        if (isHidden) {
            // 展开思考过程
            content.style.display = 'block';
            icon.textContent = '▼';
            icon.style.transform = 'rotate(90deg)';

            // 重置初始状态
            content.style.opacity = '0';
            content.style.maxHeight = '0';
            content.style.transition = 'opacity 0.3s ease, max-height 0.3s ease';

            // 触发展开动画
            requestAnimationFrame(() => {
                content.style.opacity = '1';
                content.style.maxHeight = '400px';
            });

            // 动画完成后清理
            setTimeout(() => {
                content.dataset.animating = 'false';
            }, 300);
        } else {
            // 收起思考过程
            icon.textContent = '▶';
            icon.style.transform = 'rotate(0deg)';

            // 设置收起动画
            content.style.transition = 'opacity 0.3s ease, max-height 0.3s ease';
            content.style.opacity = '0';
            content.style.maxHeight = '0';

            // 动画完成后隐藏元素
            setTimeout(() => {
                content.style.display = 'none';
                // 重置样式以便下次展开
                content.style.opacity = '1';
                content.style.maxHeight = '400px';
                content.style.transition = '';
                content.dataset.animating = 'false';
            }, 300);
        }
    }
};

// 初始化 AI Agent
document.addEventListener('DOMContentLoaded', () => {
    // 等待一段时间确保其他组件初始化完成
    setTimeout(() => {
        window.aiAgent = new AIAgent();
        window.codeCompletion = new CodeCompletion();
        console.log('AI Agent 初始化完成');
    }, 1000);
});