# ProBIDE 后端部署说明

## 🚀 功能特性

### 网页内容获取 (curl + requests 双重方案)
- **主要方案**: 使用 curl 命令获取网页内容
- **备用方案**: 当 curl 失败时自动回退到 requests
- **优势**: 更好地处理复杂网站和反爬虫机制

### AI 题目分析
- 使用 PPIO API 进行题目信息提取
- 支持多种编程题目网站
- 智能格式化为 Markdown

## 📋 系统要求

### 必需软件
- Python 3.7+
- curl 命令行工具
- pip (Python 包管理器)

### Python 依赖
```bash
pip install flask flask-cors requests chardet
```

## 🔧 安装步骤

### 1. 检查 curl 安装
```bash
# Linux/macOS
curl --version

# Windows (需要安装 curl 或使用 WSL)
curl --version
```

### 2. 安装 Python 依赖
```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 可选：设置 PPIO API Key
export PPIO_API_KEY="your_api_key_here"
```

### 4. 启动服务
```bash
python main.py
```

服务将在 `http://localhost:5001` 启动

## 🌐 API 端点

### 获取网页内容
```http
POST /api/fetch-content
Content-Type: application/json

{
  "url": "https://leetcode.com/problems/two-sum/"
}
```

**响应示例:**
```json
{
  "content": "<!DOCTYPE html>...",
  "url": "https://leetcode.com/problems/two-sum/",
  "status_code": 200,
  "content_type": "text/html",
  "encoding": "utf-8",
  "method": "curl",
  "size": 12345,
  "confidence": 0.99
}
```

### 提取题目信息
```http
POST /api/extract-problem
Content-Type: application/json

{
  "content": "题目的HTML或文本内容",
  "url": "https://leetcode.com/problems/two-sum/"
}
```

**响应示例:**
```json
{
  "problem_info": "# Two Sum\n\n## 题目描述\n...",
  "url": "https://leetcode.com/problems/two-sum/",
  "status": "success"
}
```

## 🔍 故障排除

### curl 相关问题

#### 1. curl 未安装
**错误**: `curl 命令未找到`
**解决**: 
- Linux: `sudo apt-get install curl` 或 `sudo yum install curl`
- macOS: `brew install curl` (通常已预装)
- Windows: 下载并安装 curl 或使用 WSL

#### 2. SSL 证书问题
**错误**: SSL certificate problem
**解决**: 代码中已使用 `--insecure` 参数，如需更安全可移除此参数

#### 3. 编码问题
**特性**: 自动检测编码并提供多种备用方案
- 使用 chardet 库检测编码
- 支持 utf-8, gbk, gb2312, latin1 等编码
- 自动降级处理

### 网络相关问题

#### 1. 连接超时
- 默认超时: 30秒
- 连接超时: 10秒
- 可在代码中调整

#### 2. 反爬虫机制
- 使用真实浏览器 User-Agent
- 支持 gzip 压缩
- 自动处理重定向

## 📊 性能优化

### curl 优势
1. **更好的兼容性**: 处理各种网站的反爬虫机制
2. **自动压缩**: 支持 gzip, deflate, br 压缩
3. **重定向处理**: 自动跟随重定向
4. **SSL 支持**: 更好的 HTTPS 支持

### 双重方案
1. **主要**: curl 命令 (推荐)
2. **备用**: requests 库 (兼容性)

## 🔒 安全考虑

### CORS 设置
- 当前设置为 `*` (允许所有来源)
- 生产环境建议限制特定域名

### SSL 证书
- 开发环境使用 `--insecure` 忽略证书错误
- 生产环境建议移除此参数

## 📝 日志和监控

### 日志级别
- INFO: 正常操作日志
- WARNING: curl 失败回退到 requests
- ERROR: 严重错误

### 监控指标
- 请求成功率
- 响应时间
- 编码检测准确率
- curl vs requests 使用比例

## 🚀 部署到生产环境

### 1. 使用 Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 main:app
```

### 2. 使用 Docker
```dockerfile
FROM python:3.9-slim

# 安装 curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5001

CMD ["python", "main.py"]
```

### 3. 环境变量
```bash
export FLASK_ENV=production
export PPIO_API_KEY="your_production_api_key"
```

## 🧪 测试

### 运行测试脚本
```bash
python test_curl.py
```

### 手动测试
```bash
# 测试 curl 功能
curl -X POST http://localhost:5001/api/fetch-content \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/html"}'

# 测试题目分析
curl -X POST http://localhost:5001/api/extract-problem \
  -H "Content-Type: application/json" \
  -d '{"content": "Two Sum problem...", "url": "test"}'
```