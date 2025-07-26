#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试多种网页获取方法
"""

import sys
import time
from main import fetch_with_urllib, fetch_with_http_client, fetch_with_socket, fetch_with_curl

def test_method(method_name, fetch_func, url):
    """测试单个获取方法"""
    print(f"\n🧪 测试 {method_name}")
    print("-" * 40)
    
    try:
        start_time = time.time()
        result = fetch_func(url, timeout=15)
        end_time = time.time()
        
        print(f"✅ {method_name} 成功")
        print(f"   - 耗时: {end_time - start_time:.2f}s")
        print(f"   - 内容长度: {len(result['content'])} 字符")
        print(f"   - 原始大小: {result['size']} 字节")
        print(f"   - 编码: {result['encoding']}")
        print(f"   - 置信度: {result['confidence']:.2f}")
        if 'status_code' in result:
            print(f"   - 状态码: {result['status_code']}")
        if 'content_type' in result:
            print(f"   - 内容类型: {result['content_type']}")
        
        # 显示内容预览
        preview = result['content'][:200].replace('\n', ' ').replace('\r', ' ')
        print(f"   - 内容预览: {preview}...")
        
        return True
        
    except Exception as e:
        print(f"❌ {method_name} 失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🌐 多种网页获取方法测试")
    print("=" * 60)
    
    # 测试 URL 列表
    test_urls = [
        "https://httpbin.org/html",
        "https://www.baidu.com",
        "https://example.com",
        "https://httpbin.org/encoding/utf8"
    ]
    
    # 测试方法列表
    methods = [
        ("urllib", fetch_with_urllib),
        ("http.client", fetch_with_http_client),
        ("socket", fetch_with_socket),
        ("curl", fetch_with_curl)
    ]
    
    for url in test_urls:
        print(f"\n🎯 测试 URL: {url}")
        print("=" * 60)
        
        success_count = 0
        total_methods = len(methods)
        
        for method_name, fetch_func in methods:
            if test_method(method_name, fetch_func, url):
                success_count += 1
        
        print(f"\n📊 结果: {success_count}/{total_methods} 方法成功")
        print("=" * 60)
    
    print("\n🏁 测试完成")

if __name__ == '__main__':
    main()