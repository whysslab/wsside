# 多种网页获取方法说明

## 🎯 概述

为了解决 CORS 问题和提高网页获取的成功率，我们实现了多种网页内容获取方法，按优先级顺序尝试：

## 📋 方法列表

### 1. urllib (Python 标准库) ⭐⭐⭐⭐⭐
- **优点**: Python 内置，无需额外依赖，稳定可靠
- **特性**: 支持 HTTPS、自动重定向、压缩处理
- **适用**: 大多数标准网站

```python
# 使用示例
result = fetch_with_urllib("https://example.com")
```

### 2. http.client (底层 HTTP 客户端) ⭐⭐⭐⭐
- **优点**: 更底层的控制，可以处理复杂的 HTTP 场景
- **特性**: 手动处理连接、支持 HTTP/HTTPS
- **适用**: 需要精确控制 HTTP 请求的场景

```python
# 使用示例
result = fetch_with_http_client("https://example.com")
```

### 3. 公共代理服务 ⭐⭐⭐
- **优点**: 绕过某些网站的反爬虫机制
- **特性**: 使用 allorigins.win 等公共代理
- **缺点**: 依赖第三方服务，可能不稳定

```python
# 使用示例
result = fetch_with_proxy_service("https://example.com")
```

### 4. Data URL 方法 ⭐⭐
- **优点**: 可以生成 base64 编码的数据 URL
- **特性**: 适合小文件，可用于缓存
- **缺点**: 大文件会导致 URL 过长

```python
# 使用示例
result = fetch_with_data_url("https://example.com")
```

### 5. Socket 直接请求 ⭐⭐
- **优点**: 最底层的网络访问，完全控制
- **特性**: 手动构建 HTTP 请求
- **缺点**: 复杂度高，容错性差

```python
# 使用示例
result = fetch_with_socket("https://example.com")
```

### 6. curl 命令 ⭐⭐⭐⭐
- **优点**: 功能强大，处理复杂网站效果好
- **特性**: 支持各种 HTTP 特性和选项
- **缺点**: 需要系统安装 curl

```python
# 使用示例
result = fetch_with_curl("https://example.com")
```

### 7. requests 库 (最终备用) ⭐⭐⭐⭐⭐
- **优点**: 最流行的 Python HTTP 库
- **特性**: 简单易用，功能完整
- **缺点**: 需要额外安装

## 🔄 级联策略

系统会按以下顺序尝试各种方法：

1. **urllib** → 2. **http.client** → 3. **proxy_service** → 4. **data_url** → 5. **socket** → 6. **curl** → 7. **requests**

每个方法失败后会自动尝试下一个，直到成功或所有方法都失败。

## 🛠️ 技术特性

### 编码处理
- 自动检测网页编码 (使用 chardet)
- 支持多种编码: UTF-8, GBK, GB2312, Latin1
- 智能编码回退机制

### 压缩支持
- 自动处理 gzip 压缩
- 支持 deflate 压缩
- 透明解压缩

### SSL/HTTPS
- 支持 HTTPS 连接
- 忽略 SSL 证书验证 (开发环境)
- 自定义 SSL 上下文

### 错误处理
- 详细的错误分类和报告
- 超时处理
- 网络错误恢复

## 📊 性能对比

| 方法 | 速度 | 稳定性 | 兼容性 | 依赖 |
|------|------|--------|--------|------|
| urllib | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 无 |
| http.client | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 无 |
| proxy_service | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 网络 |
| data_url | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | 无 |
| socket | ⭐⭐ | ⭐⭐ | ⭐⭐ | 无 |
| curl | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | curl |
| requests | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | requests |

## 🧪 测试方法

### 运行测试脚本
```bash
cd backend
python test_fetch_methods.py
```

### 单独测试某个方法
```python
from main import fetch_with_urllib

result = fetch_with_urllib("https://httpbin.org/html")
print(f"内容长度: {len(result['content'])}")
print(f"编码: {result['encoding']}")
```

## 🔧 配置选项

### 超时设置
```python
# 默认 30 秒超时
result = fetch_with_urllib(url, timeout=30)
```

### 自定义请求头
所有方法都使用相同的浏览器请求头：
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9...',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}
```

## 🚀 部署建议

### 生产环境
- 优先使用 urllib 和 http.client (无外部依赖)
- 保留 requests 作为最终备用
- 根据需要启用 curl 支持

### 开发环境
- 启用所有方法进行测试
- 使用详细日志记录
- 监控各方法的成功率

## 🔍 故障排除

### 常见问题

1. **SSL 证书错误**
   - 解决: 代码中已忽略证书验证
   - 生产环境建议启用证书验证

2. **编码问题**
   - 解决: 自动检测 + 多重备用编码
   - 支持中文网站

3. **超时问题**
   - 解决: 可调整超时时间
   - 多方法级联提高成功率

4. **反爬虫机制**
   - 解决: 使用真实浏览器请求头
   - 代理服务可绕过部分限制

### 调试技巧

1. **查看日志**
```python
import logging
logging.basicConfig(level=logging.INFO)
```

2. **测试单个方法**
```python
# 测试特定方法
result = fetch_with_urllib(url)
```

3. **检查返回信息**
```python
print(f"方法: {result.get('method')}")
print(f"状态码: {result.get('status_code')}")
print(f"编码: {result['encoding']}")
print(f"置信度: {result['confidence']}")
```

## 📈 未来扩展

### 可能的新方法
- Selenium WebDriver (处理 JavaScript)
- Playwright (现代浏览器自动化)
- 自定义代理池
- 分布式爬取

### 优化方向
- 智能方法选择 (基于网站特征)
- 缓存机制
- 并发获取
- 失败重试策略