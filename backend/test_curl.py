#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import chardet
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_curl_fetch(url, timeout=30):
    """
    测试 curl 获取网页内容
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
        
        print(f"🌐 测试 URL: {url}")
        print(f"⚡ 执行命令: {' '.join(curl_cmd[:5])} ... {url}")
        
        # 执行 curl 命令
        result = subprocess.run(
            curl_cmd,
            capture_output=True,
            timeout=timeout + 5,
            check=False
        )
        
        # 检查返回码
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore').strip()
            print(f"❌ curl 失败 (返回码: {result.returncode}): {error_msg}")
            return None
        
        # 获取原始字节内容
        raw_content = result.stdout
        
        if not raw_content:
            print("❌ 获取到的内容为空")
            return None
        
        # 检测编码
        detected = chardet.detect(raw_content)
        encoding = detected.get('encoding', 'utf-8')
        confidence = detected.get('confidence', 0)
        
        print(f"📝 内容大小: {len(raw_content)} 字节")
        print(f"🔤 检测编码: {encoding} (置信度: {confidence:.2f})")
        
        # 解码内容
        try:
            content = raw_content.decode(encoding, errors='replace')
        except (UnicodeDecodeError, LookupError):
            # 如果检测的编码失败，尝试常见编码
            for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'latin1']:
                try:
                    content = raw_content.decode(fallback_encoding, errors='replace')
                    encoding = fallback_encoding
                    print(f"🔄 使用备用编码: {encoding}")
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            else:
                # 所有编码都失败，使用 utf-8 强制解码
                content = raw_content.decode('utf-8', errors='replace')
                encoding = 'utf-8'
                print("⚠️ 所有编码检测失败，使用 UTF-8 强制解码")
        
        print(f"✅ 成功获取内容，长度: {len(content)} 字符")
        print(f"📄 内容预览 (前200字符):")
        print("-" * 50)
        print(content[:200])
        print("-" * 50)
        
        return {
            'content': content,
            'encoding': encoding,
            'size': len(raw_content),
            'confidence': confidence
        }
        
    except subprocess.TimeoutExpired:
        print("❌ curl 命令执行超时")
        return None
    except FileNotFoundError:
        print("❌ curl 命令未找到，请确保系统已安装 curl")
        return None
    except Exception as e:
        print(f"❌ curl 获取失败: {str(e)}")
        return None

if __name__ == '__main__':
    # 测试 URL 列表
    test_urls = [
        'https://leetcode.com/problems/two-sum/',
        'https://leetcode-cn.com/problems/two-sum/',
        'https://codeforces.com/problemset/problem/1/A',
        'https://www.baidu.com',
        'https://httpbin.org/html'
    ]
    
    print("🧪 开始测试 curl 获取网页内容功能")
    print("=" * 60)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n📋 测试 {i}/{len(test_urls)}")
        result = test_curl_fetch(url)
        
        if result:
            print(f"✅ 测试成功")
        else:
            print(f"❌ 测试失败")
        
        print("=" * 60)
    
    print("\n🏁 测试完成")