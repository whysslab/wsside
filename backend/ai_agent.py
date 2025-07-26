#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import sqlite3
import requests
import logging
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app, origins=["http://localhost:5500", "http://127.0.0.1:5500"], 
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
                'Access-Control-Allow-Origin': 'http://localhost:5500',
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
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
            return response
        else:
            response = jsonify({"error": "无法生成代码补全"})
            response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
            return response, 500
            
    except Exception as e:
        logging.error(f"代码补全错误: {e}")
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
        return response, 500

# 获取对话历史接口
@app.route('/api/ai/history/<session_id>', methods=['GET'])
def get_history(session_id):
    try:
        limit = request.args.get('limit', 50, type=int)
        history = get_conversation_history(session_id, limit)
        response = jsonify({"history": history})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
        return response
    except Exception as e:
        logging.error(f"获取历史记录错误: {e}")
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
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
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
        return response
    except Exception as e:
        logging.error(f"清除历史记录错误: {e}")
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
        return response, 500

# OPTIONS 预检请求处理
@app.route('/api/ai/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response

# 健康检查
@app.route('/api/ai/health', methods=['GET'])
def health_check():
    response = jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "model": DEFAULT_MODEL
    })
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
    return response

if __name__ == '__main__':
    init_db()
    print("AI Agent 后端服务启动中...")
    print(f"使用模型: {DEFAULT_MODEL}")
    app.run(host='0.0.0.0', port=5001, debug=True)