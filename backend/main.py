#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import sqlite3
import requests
import logging
import subprocess
import tempfile
import chardet
import urllib.request
import urllib.parse
import urllib.error
import ssl
import gzip
import socket
import base64
import hashlib
from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory
from flask_cors import CORS

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app, origins=["http://localhost:5500", "http://127.0.0.1:5500", "https://api.ide.whyss.tech", "*"], 
     allow_headers=["Content-Type", "Authorization"], 
     methods=["GET", "POST", "DELETE", "OPTIONS"])

# PPIO API 配置
PPIO_API_KEY = "sk_pCJFuTlnfpk2cQBhb7BcewihXu9XSNv25ENrbxQDNno"
PPIO_BASE_URL = "https://api.ppinfra.com/v3/openai"
DEFAULT_MODEL = "deepseek/deepseek-r1"

# 验证 API Key 格式
if not PPIO_API_KEY or not PPIO_API_KEY.startswith('sk_'):
    logging.error("PPIO API Key 格式错误或未设置")
    print("❌ 错误: PPIO API Key 格式错误或未设置")
    print("请检查 API Key 是否正确: sk_pCJFuTlnfpk2cQBhb7BcewihXu9XSNv25ENrbxQDNno")

# 数据库初始化
def init_db():
    conn = sqlite3.connect('ai_conversations.db')
    cursor = conn.cursor()
    
    # 创建对话记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建代码补全缓存表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS code_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prefix TEXT NOT NULL,
            suffix TEXT NOT NULL,
            completion TEXT NOT NULL,
            language TEXT DEFAULT 'cpp',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# 保存对话记录
def save_conversation(session_id, role, content):
    conn = sqlite3.connect('ai_conversations.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO conversations (session_id, role, content) VALUES (?, ?, ?)',
        (session_id, role, content)
    )
    conn.commit()
    conn.close()

# 获取对话历史
def get_conversation_history(session_id, limit=20):
    conn = sqlite3.connect('ai_conversations.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT role, content FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?',
        (session_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    
    # 反转顺序，最新的在后面
    messages = []
    for role, content in reversed(rows):
        messages.append({"role": role, "content": content})
    
    return messages

# 调用 PPIO API
def call_ppio_api(messages, stream=True, max_tokens=2048):
    headers = {
        "Authorization": f"Bearer {PPIO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "stream": stream,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        logging.info(f"调用 PPIO API - Model: {DEFAULT_MODEL}, Stream: {stream}")
        response = requests.post(
            f"{PPIO_BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            stream=stream,
            timeout=30
        )
        
        # 详细的错误处理
        if response.status_code == 401:
            logging.error("PPIO API 认证失败 - API Key 无效或已过期")
            return None
        elif response.status_code == 403:
            logging.error("PPIO API 访问被拒绝 - 可能余额不足或权限不够")
            return None
        elif response.status_code == 429:
            logging.error("PPIO API 请求过于频繁 - 触发限流")
            return None
        elif response.status_code == 404:
            logging.error(f"PPIO API 模型不存在 - {DEFAULT_MODEL}")
            return None
        elif response.status_code >= 500:
            logging.error(f"PPIO API 服务器错误 - {response.status_code}")
            return None
        
        response.raise_for_status()
        return response
        
    except requests.exceptions.Timeout:
        logging.error("PPIO API 请求超时")
        return None
    except requests.exceptions.ConnectionError:
        logging.error("PPIO API 连接失败 - 请检查网络")
        return None
    except Exception as e:
        logging.error(f"PPIO API 调用失败: {e}")
        return None

# AI 对话接口
@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    try:
        # 验证请求头
        if not request.is_json:
            return jsonify({"error": "请求必须是 JSON 格式"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "请求体不能为空"}), 400
            
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({"error": "消息不能为空"}), 400
            
        logging.info(f"收到对话请求 - Session: {session_id}, Message: {message[:50]}...")
        
        # 获取历史对话
        history = get_conversation_history(session_id)
        
        # 添加系统提示
        system_message = {
            "role": "system",
            "content": "你是一个专业的编程助手，专门帮助用户解决 C++ 编程问题。你可以：\n1. 解答编程问题\n2. 代码审查和优化建议\n3. 调试帮助\n4. 算法和数据结构指导\n5. 最佳实践建议\n\n请用简洁、准确的中文回答。"
        }
        
        # 构建消息列表
        messages = [system_message] + history + [{"role": "user", "content": message}]
        
        # 保存用户消息
        save_conversation(session_id, "user", message)
        
        # 调用 PPIO API
        response = call_ppio_api(messages, stream=True)
        if not response:
            logging.error("PPIO API 调用失败")
            return jsonify({"error": "AI 服务暂时不可用"}), 500
        
        def generate():
            assistant_content = ""
            try:
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data_str = line[6:]
                            if data_str.strip() == '[DONE]':
                                break
                            
                            try:
                                chunk_data = json.loads(data_str)
                                if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                    delta = chunk_data['choices'][0].get('delta', {})
                                    content = delta.get('content', '')
                                    if content:
                                        assistant_content += content
                                        yield f"data: {json.dumps({'content': content})}\n\n"
                            except json.JSONDecodeError:
                                continue
                
                # 保存助手回复
                if assistant_content:
                    save_conversation(session_id, "assistant", assistant_content)
                    logging.info(f"对话完成 - Session: {session_id}, Response length: {len(assistant_content)}")
                
                yield f"data: {json.dumps({'done': True})}\n\n"
                
            except Exception as e:
                logging.error(f"流式响应处理错误: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            }
        )
        
    except Exception as e:
        logging.error(f"对话接口错误: {e}")
        return jsonify({"error": str(e)}), 500

# 代码补全接口
@app.route('/api/ai/complete', methods=['POST'])
def code_complete():
    try:
        data = request.get_json()
        prefix = data.get('prefix', '')
        suffix = data.get('suffix', '')
        language = data.get('language', 'cpp')
        
        # 构建代码补全提示
        prompt = f"""请为以下 {language} 代码提供智能补全。只返回补全的代码，不要解释。

前缀代码:
{prefix}

后缀代码:
{suffix}

请提供合适的代码补全："""
        
        messages = [
            {
                "role": "system", 
                "content": "你是一个专业的代码补全助手。只返回需要补全的代码，不要添加任何解释或格式化。"
            },
            {"role": "user", "content": prompt}
        ]
        
        # 调用 PPIO API (非流式)
        response = call_ppio_api(messages, stream=False, max_tokens=512)
        if not response:
            return jsonify({"error": "代码补全服务暂时不可用"}), 500
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            completion = result['choices'][0]['message']['content'].strip()
            
            # 缓存补全结果
            conn = sqlite3.connect('ai_conversations.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO code_completions (prefix, suffix, completion, language) VALUES (?, ?, ?, ?)',
                (prefix[-100:], suffix[:100], completion, language)  # 只保存部分前后缀以节省空间
            )
            conn.commit()
            conn.close()
            
            response = jsonify({"completion": completion})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        else:
            response = jsonify({"error": "无法生成代码补全"})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, 500
            
    except Exception as e:
        logging.error(f"代码补全错误: {e}")
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# 获取对话历史接口
@app.route('/api/ai/history/<session_id>', methods=['GET'])
def get_history(session_id):
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_conversation_history(session_id, limit)
        response = jsonify({"history": history})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        logging.error(f"获取历史记录错误: {e}")
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# 清除对话历史
@app.route('/api/ai/history/<session_id>', methods=['DELETE'])
def clear_history(session_id):
    try:
        conn = sqlite3.connect('ai_conversations.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()
        logging.info(f"清除历史记录 - Session: {session_id}")
        response = jsonify({"message": "对话历史已清除"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        logging.error(f"清除历史记录错误: {e}")
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

# 下载 TDM-GCC 编译器
@app.route('/api/download/tdm64-gcc', methods=['GET'])
def download_tdm_gcc():
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'tdm64-gcc-10.3.0-2.exe')
        
        if not os.path.exists(file_path):
            logging.error("TDM-GCC 文件不存在")
            return jsonify({"error": "文件不存在"}), 404
        
        logging.info("开始下载 TDM-GCC 编译器")
        return send_from_directory(
            directory=current_dir,
            path='tdm64-gcc-10.3.0-2.exe',
            as_attachment=True,
            mimetype='application/octet-stream'
        )
    except Exception as e:
        logging.error(f"下载 TDM-GCC 失败: {e}")
        return jsonify({"error": str(e)}), 500

# OPTIONS 预检请求处理
@app.route('/api/ai/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response

# 方案1: 使用 urllib (Python 标准库)
def fetch_with_urllib(url, timeout=30):
    """
    使用 urllib 获取网页内容
    """
    try:
        # 创建 SSL 上下文，忽略证书验证
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # 创建请求对象
        req = urllib.request.Request(url, headers=headers)
        
        logging.info(f"使用 urllib 获取网页内容: {url}")
        
        # 发送请求
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context) as response:
            # 获取响应信息
            status_code = response.getcode()
            content_type = response.getheader('Content-Type', '')
            content_encoding = response.getheader('Content-Encoding', '')
            
            # 读取原始数据
            raw_data = response.read()
            
            # 处理压缩内容
            if content_encoding == 'gzip':
                raw_data = gzip.decompress(raw_data)
            elif content_encoding == 'deflate':
                import zlib
                raw_data = zlib.decompress(raw_data)
            
            # 检测编码
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')
            confidence = detected.get('confidence', 0)
            
            # 从 Content-Type 头中提取编码
            if 'charset=' in content_type:
                header_encoding = content_type.split('charset=')[1].split(';')[0].strip()
                if header_encoding:
                    encoding = header_encoding
            
            logging.info(f"urllib 检测到编码: {encoding} (置信度: {confidence:.2f})")
            
            # 解码内容
            try:
                content = raw_data.decode(encoding, errors='replace')
            except (UnicodeDecodeError, LookupError):
                # 尝试常见编码
                for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                    try:
                        content = raw_data.decode(fallback_encoding, errors='replace')
                        encoding = fallback_encoding
                        logging.info(f"urllib 使用备用编码: {encoding}")
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue
                else:
                    content = raw_data.decode('utf-8', errors='replace')
                    encoding = 'utf-8'
            
            return {
                'content': content,
                'encoding': encoding,
                'size': len(raw_data),
                'confidence': confidence,
                'status_code': status_code,
                'content_type': content_type
            }
            
    except urllib.error.HTTPError as e:
        raise Exception(f"HTTP错误 {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise Exception(f"URL错误: {e.reason}")
    except socket.timeout:
        raise Exception("请求超时")
    except Exception as e:
        raise Exception(f"urllib 获取失败: {str(e)}")

# 方案2: 使用 http.client (更底层的 HTTP 客户端)
def fetch_with_http_client(url, timeout=30):
    """
    使用 http.client 获取网页内容
    """
    try:
        import http.client
        from urllib.parse import urlparse
        
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path or '/'
        if parsed_url.query:
            path += '?' + parsed_url.query
        
        # 选择连接类型
        if parsed_url.scheme == 'https':
            if port is None:
                port = 443
            # 创建 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            conn = http.client.HTTPSConnection(host, port, timeout=timeout, context=ssl_context)
        else:
            if port is None:
                port = 80
            conn = http.client.HTTPConnection(host, port, timeout=timeout)
        
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close',
            'Host': host
        }
        
        logging.info(f"使用 http.client 获取网页内容: {url}")
        
        # 发送请求
        conn.request('GET', path, headers=headers)
        response = conn.getresponse()
        
        # 获取响应信息
        status_code = response.status
        content_type = response.getheader('Content-Type', '')
        content_encoding = response.getheader('Content-Encoding', '')
        
        # 读取数据
        raw_data = response.read()
        conn.close()
        
        # 处理压缩
        if content_encoding == 'gzip':
            raw_data = gzip.decompress(raw_data)
        elif content_encoding == 'deflate':
            import zlib
            raw_data = zlib.decompress(raw_data)
        
        # 检测编码
        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding', 'utf-8')
        confidence = detected.get('confidence', 0)
        
        # 从 Content-Type 头中提取编码
        if 'charset=' in content_type:
            header_encoding = content_type.split('charset=')[1].split(';')[0].strip()
            if header_encoding:
                encoding = header_encoding
        
        logging.info(f"http.client 检测到编码: {encoding} (置信度: {confidence:.2f})")
        
        # 解码内容
        try:
            content = raw_data.decode(encoding, errors='replace')
        except (UnicodeDecodeError, LookupError):
            for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                try:
                    content = raw_data.decode(fallback_encoding, errors='replace')
                    encoding = fallback_encoding
                    logging.info(f"http.client 使用备用编码: {encoding}")
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            else:
                content = raw_data.decode('utf-8', errors='replace')
                encoding = 'utf-8'
        
        return {
            'content': content,
            'encoding': encoding,
            'size': len(raw_data),
            'confidence': confidence,
            'status_code': status_code,
            'content_type': content_type
        }
        
    except Exception as e:
        raise Exception(f"http.client 获取失败: {str(e)}")

# 方案3: 使用 socket 直接发送 HTTP 请求
def fetch_with_socket(url, timeout=30):
    """
    使用 socket 直接发送 HTTP 请求
    """
    try:
        from urllib.parse import urlparse
        
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
        path = parsed_url.path or '/'
        if parsed_url.query:
            path += '?' + parsed_url.query
        
        # 创建 socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # HTTPS 需要 SSL 包装
        if parsed_url.scheme == 'https':
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            sock = ssl_context.wrap_socket(sock, server_hostname=host)
        
        logging.info(f"使用 socket 获取网页内容: {url}")
        
        # 连接服务器
        sock.connect((host, port))
        
        # 构建 HTTP 请求
        request = f"""GET {path} HTTP/1.1\r
Host: {host}\r
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\r
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8\r
Accept-Encoding: gzip, deflate\r
Connection: close\r
\r
"""
        
        # 发送请求
        sock.send(request.encode())
        
        # 接收响应
        response_data = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response_data += chunk
        
        sock.close()
        
        # 解析 HTTP 响应
        response_str = response_data.decode('utf-8', errors='ignore')
        header_end = response_str.find('\r\n\r\n')
        if header_end == -1:
            raise Exception("无效的 HTTP 响应")
        
        headers_str = response_str[:header_end]
        body_start = header_end + 4
        
        # 提取状态码
        status_line = headers_str.split('\r\n')[0]
        status_code = int(status_line.split()[1])
        
        # 提取 Content-Type
        content_type = ''
        content_encoding = ''
        for line in headers_str.split('\r\n')[1:]:
            if line.lower().startswith('content-type:'):
                content_type = line.split(':', 1)[1].strip()
            elif line.lower().startswith('content-encoding:'):
                content_encoding = line.split(':', 1)[1].strip()
        
        # 获取响应体的原始字节
        raw_data = response_data[body_start:]
        
        # 处理压缩
        if content_encoding == 'gzip':
            raw_data = gzip.decompress(raw_data)
        elif content_encoding == 'deflate':
            import zlib
            raw_data = zlib.decompress(raw_data)
        
        # 检测编码
        detected = chardet.detect(raw_data)
        encoding = detected.get('encoding', 'utf-8')
        confidence = detected.get('confidence', 0)
        
        # 从 Content-Type 头中提取编码
        if 'charset=' in content_type:
            header_encoding = content_type.split('charset=')[1].split(';')[0].strip()
            if header_encoding:
                encoding = header_encoding
        
        logging.info(f"socket 检测到编码: {encoding} (置信度: {confidence:.2f})")
        
        # 解码内容
        try:
            content = raw_data.decode(encoding, errors='replace')
        except (UnicodeDecodeError, LookupError):
            for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                try:
                    content = raw_data.decode(fallback_encoding, errors='replace')
                    encoding = fallback_encoding
                    logging.info(f"socket 使用备用编码: {encoding}")
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            else:
                content = raw_data.decode('utf-8', errors='replace')
                encoding = 'utf-8'
        
        return {
            'content': content,
            'encoding': encoding,
            'size': len(raw_data),
            'confidence': confidence,
            'status_code': status_code,
            'content_type': content_type
        }
        
    except Exception as e:
        raise Exception(f"socket 获取失败: {str(e)}")

# 方案4: 使用公共代理服务
def fetch_with_proxy_service(url, timeout=30):
    """
    使用公共代理服务获取网页内容
    """
    try:
        # 使用 allorigins.win 代理服务
        proxy_url = f"https://api.allorigins.win/get?url={urllib.parse.quote(url)}"
        
        logging.info(f"使用代理服务获取网页内容: {url}")
        
        # 使用 urllib 请求代理服务
        req = urllib.request.Request(proxy_url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            proxy_data = json.loads(response.read().decode('utf-8'))
            
            if proxy_data.get('status', {}).get('http_code') != 200:
                raise Exception(f"代理服务返回错误: {proxy_data.get('status', {})}")
            
            content = proxy_data.get('contents', '')
            
            # 检测编码
            content_bytes = content.encode('utf-8')
            detected = chardet.detect(content_bytes)
            encoding = detected.get('encoding', 'utf-8')
            confidence = detected.get('confidence', 0)
            
            return {
                'content': content,
                'encoding': encoding,
                'size': len(content_bytes),
                'confidence': confidence,
                'status_code': 200,
                'content_type': 'text/html'
            }
            
    except Exception as e:
        raise Exception(f"代理服务获取失败: {str(e)}")

# 方案5: 使用 base64 编码的数据 URL (适用于小文件)
def fetch_with_data_url(url, timeout=30):
    """
    将 URL 转换为 data URL 格式 (实验性)
    """
    try:
        # 这个方法主要用于演示，实际上还是需要先获取内容
        # 但可以用于缓存和离线处理
        
        # 先用 urllib 获取内容
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw_data = response.read()
            content_type = response.getheader('Content-Type', 'text/html')
            
            # 检测编码
            detected = chardet.detect(raw_data)
            encoding = detected.get('encoding', 'utf-8')
            confidence = detected.get('confidence', 0)
            
            # 解码内容
            content = raw_data.decode(encoding, errors='replace')
            
            # 创建 data URL (可用于缓存)
            b64_content = base64.b64encode(raw_data).decode('ascii')
            data_url = f"data:{content_type};base64,{b64_content}"
            
            logging.info(f"data URL 方法获取内容，长度: {len(content)}")
            
            return {
                'content': content,
                'encoding': encoding,
                'size': len(raw_data),
                'confidence': confidence,
                'status_code': 200,
                'content_type': content_type,
                'data_url': data_url[:100] + '...' if len(data_url) > 100 else data_url
            }
            
    except Exception as e:
        raise Exception(f"data URL 方法失败: {str(e)}")

# 使用 curl 获取网页内容
def fetch_with_curl(url, timeout=30):
    """
    使用 curl 命令获取网页内容
    """
    try:
        # 构建 curl 命令
        curl_cmd = [
            'curl',
            '-L',  # 跟随重定向
            '-s',  # 静默模式
            '-S',  # 显示错误
            '--max-time', str(timeout),  # 超时设置
            '--connect-timeout', '10',  # 连接超时
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            '--header', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            '--header', 'Accept-Language: zh-CN,zh;q=0.9,en;q=0.8',
            '--header', 'Accept-Encoding: gzip, deflate, br',
            '--header', 'Connection: keep-alive',
            '--header', 'Upgrade-Insecure-Requests: 1',
            '--compressed',  # 自动解压缩
            '--insecure',  # 忽略 SSL 证书错误（谨慎使用）
            url
        ]
        
        logging.info(f"使用 curl 获取网页内容: {url}")
        
        # 执行 curl 命令
        result = subprocess.run(
            curl_cmd,
            capture_output=True,
            timeout=timeout + 5,  # 给 subprocess 额外的超时时间
            check=False  # 不自动抛出异常，手动处理返回码
        )
        
        # 检查返回码
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore').strip()
            if result.returncode == 28:  # curl 超时错误码
                raise Exception(f"请求超时: {error_msg}")
            elif result.returncode == 6:  # 无法解析主机
                raise Exception(f"无法解析主机: {error_msg}")
            elif result.returncode == 7:  # 无法连接
                raise Exception(f"无法连接到服务器: {error_msg}")
            else:
                raise Exception(f"curl 执行失败 (返回码: {result.returncode}): {error_msg}")
        
        # 获取原始字节内容
        raw_content = result.stdout
        
        if not raw_content:
            raise Exception("获取到的内容为空")
        
        # 检测编码
        detected = chardet.detect(raw_content)
        encoding = detected.get('encoding', 'utf-8')
        confidence = detected.get('confidence', 0)
        
        logging.info(f"检测到编码: {encoding} (置信度: {confidence:.2f})")
        
        # 解码内容
        try:
            content = raw_content.decode(encoding, errors='replace')
        except (UnicodeDecodeError, LookupError):
            # 如果检测的编码失败，尝试常见编码
            for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                try:
                    content = raw_content.decode(fallback_encoding, errors='replace')
                    encoding = fallback_encoding
                    logging.info(f"使用备用编码: {encoding}")
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            else:
                # 所有编码都失败，使用 utf-8 强制解码
                content = raw_content.decode('utf-8', errors='replace')
                encoding = 'utf-8'
                logging.warning("所有编码检测失败，使用 UTF-8 强制解码")
        
        return {
            'content': content,
            'encoding': encoding,
            'size': len(raw_content),
            'confidence': confidence
        }
        
    except subprocess.TimeoutExpired:
        raise Exception("curl 命令执行超时")
    except FileNotFoundError:
        raise Exception("curl 命令未找到，请确保系统已安装 curl")
    except Exception as e:
        raise Exception(f"curl 获取失败: {str(e)}")

# 网页内容获取代理接口
@app.route('/api/fetch-content', methods=['POST'])
def fetch_web_content():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({"error": "URL 不能为空"}), 400
        
        # 验证 URL 格式
        if not url.startswith(('http://', 'https://')):
            return jsonify({"error": "URL 格式无效"}), 400
        
        logging.info(f"开始获取网页内容: {url}")
        
        # 多种方法级联尝试 (按推荐顺序排列)
        methods = [
            ("urllib", fetch_with_urllib),           # Python 标准库，最稳定
            ("http.client", fetch_with_http_client), # 更底层的 HTTP 客户端
            ("proxy_service", fetch_with_proxy_service), # 公共代理服务
            ("data_url", fetch_with_data_url),       # 实验性方法
            ("socket", fetch_with_socket),           # 最底层的 socket 方法
            ("curl", fetch_with_curl)                # 外部命令 (如果可用)
        ]
        
        last_error = None
        
        for method_name, fetch_func in methods:
            try:
                logging.info(f"尝试使用 {method_name} 获取网页内容")
                fetch_result = fetch_func(url, timeout=30)
                content = fetch_result['content']
                encoding = fetch_result['encoding']
                
                logging.info(f"{method_name} 成功获取网页内容，长度: {len(content)}, 编码: {encoding}")
                
                result = jsonify({
                    "content": content,
                    "url": url,
                    "status_code": fetch_result.get('status_code', 200),
                    "content_type": fetch_result.get('content_type', 'text/html'),
                    "encoding": encoding,
                    "method": method_name,
                    "size": fetch_result['size'],
                    "confidence": fetch_result['confidence']
                })
                result.headers.add('Access-Control-Allow-Origin', '*')
                return result
                
            except Exception as e:
                last_error = e
                logging.warning(f"{method_name} 获取失败: {e}")
                continue
        
        # 所有方法都失败，最后尝试 requests 作为最终备用
        try:
            logging.info("所有方法失败，最后尝试 requests")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # 检测编码
            response.encoding = response.apparent_encoding or 'utf-8'
            content = response.text
            
            logging.info(f"requests 成功获取网页内容，长度: {len(content)}")
            
            result = jsonify({
                "content": content,
                "url": url,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type', ''),
                "encoding": response.encoding,
                "method": "requests"
            })
            result.headers.add('Access-Control-Allow-Origin', '*')
            return result
            
        except Exception as requests_error:
            logging.error(f"requests 也失败了: {requests_error}")
            # 抛出最后一个非 requests 的错误
            raise last_error or requests_error
        
    except requests.exceptions.Timeout:
        logging.error(f"请求超时: {url}")
        result = jsonify({"error": "请求超时，请检查网络连接或稍后重试"})
        result.headers.add('Access-Control-Allow-Origin', '*')
        return result, 408
    except requests.exceptions.ConnectionError:
        logging.error(f"连接失败: {url}")
        result = jsonify({"error": "无法连接到目标网站，请检查URL是否正确"})
        result.headers.add('Access-Control-Allow-Origin', '*')
        return result, 503
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP错误: {e}")
        result = jsonify({"error": f"网站返回错误: {e.response.status_code}"})
        result.headers.add('Access-Control-Allow-Origin', '*')
        return result, e.response.status_code
    except Exception as e:
        logging.error(f"获取网页内容失败: {e}")
        result = jsonify({"error": f"获取失败: {str(e)}"})
        result.headers.add('Access-Control-Allow-Origin', '*')
        return result, 500

# 题目信息提取接口
@app.route('/api/extract-problem', methods=['POST'])
def extract_problem_info():
    try:
        data = request.get_json()
        html_content = data.get('content', '')
        url = data.get('url', '')
        
        if not html_content:
            return jsonify({"error": "网页内容不能为空"}), 400
        
        logging.info(f"开始提取题目信息，内容长度: {len(html_content)}")
        
        # 构建提取题目信息的提示词
        prompt_template = """请分析以下网页内容，提取编程题目的关键信息，并转换为结构化的 Markdown 格式。

网页内容：
{content}

请提取以下信息并按照以下格式输出：

# 题目标题

## 题目描述
[题目的详细描述]

## 输入说明
[输入格式说明]

## 输出说明
[输出格式说明]

## 示例
### 示例 1
**输入：**
```
[示例输入]
```

**输出：**
```
[示例输出]
```

**说明：**
[示例说明]

## 约束条件
[数据范围和约束条件]

## 提示
[解题提示或算法提示]

---
**题目来源：** {url}

注意：
1. 如果网页内容不包含编程题目，请返回"未找到有效的编程题目信息"
2. 请尽量提取完整的信息，如果某些部分缺失，请标注"信息不完整"
3. 保持 Markdown 格式的规范性"""

        prompt = prompt_template.format(
            content=html_content[:8000],  # 限制内容长度避免token过多
            url=url
        )

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的编程题目分析助手。你的任务是从网页内容中提取编程题目的关键信息，并转换为结构化的 Markdown 格式。请准确提取题目标题、描述、输入输出说明、示例、约束条件等信息。"
            },
            {"role": "user", "content": prompt}
        ]
        
        # 调用 AI API
        response = call_ppio_api(messages, stream=False, max_tokens=2048)
        if not response:
            return jsonify({"error": "AI 服务暂时不可用"}), 500
        
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            extracted_info = result['choices'][0]['message']['content'].strip()
            
            logging.info(f"题目信息提取完成，长度: {len(extracted_info)}")
            
            result = jsonify({
                "problem_info": extracted_info,
                "url": url,
                "status": "success"
            })
            result.headers.add('Access-Control-Allow-Origin', '*')
            return result
        else:
            result = jsonify({"error": "无法提取题目信息"})
            result.headers.add('Access-Control-Allow-Origin', '*')
            return result, 500
            
    except Exception as e:
        logging.error(f"题目信息提取错误: {e}")
        result = jsonify({"error": str(e)})
        result.headers.add('Access-Control-Allow-Origin', '*')
        return result, 500

# 健康检查
@app.route('/api/ai/health', methods=['GET'])
def health_check():
    response = jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "model": DEFAULT_MODEL
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == '__main__':
    init_db()
    print("AI Agent 后端服务启动中...")
    print(f"使用模型: {DEFAULT_MODEL}")
    app.run(host='0.0.0.0', port=5001, debug=True)