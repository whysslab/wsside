#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import sys

def check_service(name, url, timeout=5):
    """检查服务是否可用"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name} 服务正常 ({url})")
            return True
        else:
            print(f"❌ {name} 服务异常 - HTTP {response.status_code} ({url})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} 服务无法连接 ({url})")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {name} 服务超时 ({url})")
        return False
    except Exception as e:
        print(f"❌ {name} 服务检查失败: {e} ({url})")
        return False

def main():
    print("🔍 检查 OIDE 系统服务状态...\n")
    
    services = [
        ("前端服务", "http://localhost:5500"),
        ("后端 API", "http://localhost:5000/api"),
        ("AI Agent", "http://localhost:5001/api/ai/health"),
    ]
    
    all_ok = True
    
    for name, url in services:
        if not check_service(name, url):
            all_ok = False
        time.sleep(0.5)  # 避免请求过快
    
    print("\n" + "="*50)
    
    if all_ok:
        print("🎉 所有服务运行正常！")
        print("\n📱 访问地址:")
        print("   前端: http://localhost:5500/index.html")
        print("   IDE: http://localhost:5500/ide/index.html")
        print("   后端 API: http://localhost:5000/api")
        print("   AI Agent: http://localhost:5001/api/ai")
    else:
        print("⚠️  部分服务异常，请检查启动脚本")
        sys.exit(1)

if __name__ == "__main__":
    main()