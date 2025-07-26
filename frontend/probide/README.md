# ProBIDE - 编程题目解决环境

ProBIDE 是一个专门为编程题目解决而设计的集成开发环境，在标准 IDE 的基础上增加了左侧栏题目处理功能。

## 🎯 核心功能

### 左侧栏 - 题目处理
- **题目输入**: 支持纯文本或 Markdown 格式的题目内容输入
- **AI 转换**: 自动将题目内容转换为标准 Markdown 格式
- **Markdown 渲染**: 格式化显示题目内容，支持标题、代码块、列表等
- **LaTeX 渲染**: 支持数学公式渲染，包括 `$...$`、`\(...\)`、`$$...$$`、`\[...\]` 格式
- **Think 过程过滤**: 自动过滤掉 deepseek-r1 的 `<think>...</think>` 思考过程
- **编辑功能**: 支持重新编辑和重新处理题目内容

### 双侧栏控制
- **独立控制**: 左右侧栏可以独立打开/关闭
- **拖拽调整**: 支持拖拽调整侧栏宽度
- **状态持久化**: 自动保存侧栏状态到本地存储
- **键盘快捷键**: 
  - `Ctrl+Shift+Q`: 切换左侧栏（题目栏）
  - `Ctrl+Shift+C`: 切换右侧栏（AI助手）

### AI 上下文集成
- **自动上下文**: 右侧 AI 助手自动获得当前题目信息
- **智能问答**: AI 能够基于题目内容提供针对性帮助
- **代码建议**: 结合题目要求提供代码优化建议

## 🚀 使用流程

1. **输入题目**: 在左侧栏的文本框中输入或粘贴题目内容
2. **AI 处理**: 点击"处理题目"按钮，AI 自动转换为 Markdown 格式
3. **查看题目**: 左侧栏显示格式化的题目内容
4. **编写代码**: 在中间编辑器编写解决方案
5. **AI 助手**: 右侧 AI 助手提供基于题目的帮助

## 🔧 技术实现

### API 格式
ProBIDE 使用与 IDE ai-agent 相同的 API 格式：

```javascript
// API 基础路径
const apiBase = window.IDE_CONFIG ? 
  window.IDE_CONFIG.getApiConfig().AI_AGENT : 
  'https://api.ide.whyss.tech/api/ai';

// 健康检查
await fetch(`${apiBase}/health`, {
  method: 'GET',
  mode: 'cors'
});

// 聊天请求
await fetch(`${apiBase}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "题目转换请求",
    session_id: sessionId
  }),
  mode: 'cors'
});
```

### 流式响应处理
支持处理 AI 服务的流式响应，实时显示转换进度。

### Markdown 和 LaTeX 渲染
内置 Markdown 渲染器和 MathJax LaTeX 支持：

**Markdown 支持：**
- 标题 (`#`, `##`, `###`)
- 粗体 (`**text**`)
- 斜体 (`*text*`)
- 行内代码 (`` `code` ``)
- 代码块 (``` code ```)
- 列表 (`*` 或 `1.`)

**LaTeX 数学公式支持：**
- 行内公式：`$x^2 + y^2 = z^2$` 或 `\(x^2 + y^2 = z^2\)`
- 块级公式：`$$\int_a^b f(x)dx$$` 或 `\[\int_a^b f(x)dx\]`
- 复杂公式：矩阵、分数、根号、求和、积分等

**内容过滤：**
- 自动过滤 `<think>...</think>` 标签及其内容

## 📁 文件结构

```
frontend/probide/
├── index.html          # 主页面文件
├── config.js           # 配置文件
├── ai-agent.js         # AI 助手功能
├── renderer.js         # 渲染器
├── styles.css          # 样式文件
├── test-probide.html   # 功能测试页面
├── test-api-format.html # API 格式测试页面
└── README.md           # 说明文档
```

## 🧪 测试

### 功能测试
打开 `test-probide.html` 进行完整功能测试。

### API 测试
打开 `test-api-format.html` 测试 AI API 连接和格式。

### 示例题目

#### 基础题目示例
```markdown
# 两数之和

## 题目描述
给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

## 示例
**输入：** nums = [2,7,11,15], target = 9
**输出：** [0,1]
**解释：** 因为 nums[0] + nums[1] == 9，所以返回 [0, 1]

## 约束条件
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
```

#### 数学题目示例（支持 LaTeX）
```markdown
# 二次方程求解

## 题目描述
求解二次方程 $ax^2 + bx + c = 0$ 的根，其中 $a \neq 0$。

## 求根公式
根据求根公式：
$$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$

## 判别式分析
设判别式 $\Delta = b^2 - 4ac$：
- 当 $\Delta > 0$ 时，方程有两个不同的实根
- 当 $\Delta = 0$ 时，方程有一个重根：$x = -\frac{b}{2a}$
- 当 $\Delta < 0$ 时，方程无实根

## 示例
求解方程 $x^2 - 5x + 6 = 0$：
- $a = 1, b = -5, c = 6$
- $\Delta = (-5)^2 - 4 \cdot 1 \cdot 6 = 25 - 24 = 1 > 0$
- $x = \frac{5 \pm 1}{2}$，所以 $x_1 = 3, x_2 = 2$
```

## 🔍 故障排除

### 常见问题

1. **数学公式不渲染**
   - 确认 MathJax 库已正确加载
   - 检查公式语法是否正确
   - 确保使用支持的格式：`$...$`、`\(...\)`、`$$...$$`、`\[...\]`

2. **Think 过程仍然显示**
   - 确认使用最新版本的代码（v1.1.0+）
   - 检查 `<think>` 标签是否正确闭合
   - 过滤功能在 `renderMarkdown` 函数中自动执行

3. **题面内容显示为 `[object PointerEvent]`**
   - 这是事件处理问题，已在 v1.0.1 中修复
   - 确保使用最新版本的代码
   - 如果仍有问题，检查事件绑定是否正确

4. **左侧栏不显示**
   - 检查浏览器控制台是否有 JavaScript 错误
   - 确认 DOM 元素是否正确加载

3. **AI 转换失败**
   - 使用 API 测试页面检查服务连接
   - 确认网络连接和 CORS 设置
   - 检查 AI 服务是否正常运行

4. **上下文集成不工作**
   - 确认 AI 助手已正确初始化
   - 检查题目内容是否正确保存到全局变量

### 调试命令

在浏览器控制台中运行：

```javascript
// 检查基本元素
console.log('左侧栏:', document.getElementById('leftPanel'));
console.log('题目内容:', document.getElementById('problemContent'));

// 检查状态
console.log('侧栏状态:', window.sidebarState);
console.log('当前题目:', window.currentProblemMarkdown);

// 手动测试
showProblemInput();
```

## 📝 更新日志

### v1.1.0
- ✨ 新增 LaTeX 渲染支持：支持 `$...$`、`\(...\)`、`$$...$$`、`\[...\]` 格式的数学公式
- ✨ 新增 Think 过程过滤：自动过滤掉 deepseek-r1 的 `<think>...</think>` 思考过程
- 🔧 集成 MathJax 3.0：提供专业的数学公式渲染
- 📝 改进内容处理：在渲染前自动清理不需要的内容

### v1.0.1
- 🐛 修复事件处理问题：解决题面内容变成 `[object PointerEvent]` 的问题
- 🔧 改进事件绑定：使用箭头函数包装事件处理器，避免传递事件对象

### v1.0.0
- ✅ 实现左侧栏题目输入和显示功能
- ✅ 集成 AI 题目转换服务
- ✅ 支持 Markdown 渲染
- ✅ 实现双侧栏控制
- ✅ 添加 AI 上下文集成
- ✅ 更新 API 格式与 IDE ai-agent 保持一致