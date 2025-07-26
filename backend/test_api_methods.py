#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 API 接口的多种获取方法
"""

import requests
import json
import time

def test_fetch_api(url_to_fetch):
    """测试 fetch-content API"""
    api_url = "http://localhost:5001/api/fetch-content"
    
    payload = {
        "url": url_to_fetch
    }
    
    print(f"🌐 测试获取: {url_to_fetch}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        response = requests.post(api_url, json=payload, timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取成功")
            print(f"   - 耗时: {end_time - start_time:.2f}s")
            print(f"   - 方法: {data.get('method', 'unknown')}")
            print(f"   - 状态码: {data.get('status_code', 'unknown')}")
            print(f"   - 内容长度: {len(data.get('content', ''))} 字符")
            print(f"   - 编码: {data.get('encoding', 'unknown')}")
            print(f"   - 原始大小: {data.get('size', 'unknown')} 字节")
            print(f"   - 置信度: {data.get('confidence', 'unknown')}")
            print(f"   - 内容类型: {data.get('content_type', 'unknown')}")
            
            # 内容预览
            content = data.get('content', '')
            preview = content[:200].replace('\n', ' ').replace('\r', ' ')
            print(f"   - 内容预览: {preview}...")
            
            return True
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            print(f"❌ API 错误 {response.status_code}: {error_data.get('error', response.text)}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接失败 - 请确保后端服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 API 多方法获取测试")
    print("=" * 60)
    print("请确保后端服务正在运行: python backend/main.py")
    print("=" * 60)
    
    # 测试 URL 列表
    test_urls = [
        "https://httpbin.org/html",
        "https://example.com",
        "https://www.baidu.com",
        "https://httpbin.org/encoding/utf8",
        "https://jsonplaceholder.typicode.com/posts/1"
    ]
    
    success_count = 0
    total_tests = len(test_urls)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📋 测试 {i}/{total_tests}")
        if test_fetch_api(url):
            success_count += 1
        print("=" * 60)
    
    print(f"\n🏁 测试完成: {success_count}/{total_tests} 成功")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！多方法获取功能正常")
    elif success_count > 0:
        print("⚠️ 部分测试成功，多方法级联正在发挥作用")
    else:
        print("❌ 所有测试失败，请检查后端服务和网络连接")

if __name__ == '__main__':
    main()