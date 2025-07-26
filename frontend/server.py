#!/usr/bin/env python3
"""
簡單的前端服務器，用於開發和測試
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 添加 CORS 頭部
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # 切換到前端目錄
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    print(f"=== OIDE 前端開發服務器 ===")
    print(f"服務器運行在: http://localhost:{PORT}")
    print(f"服務目錄: {frontend_dir}")
    print("按 Ctrl+C 停止服務器\n")
    
    # 創建服務器
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"正在啟動服務器...")
        
        # 自動打開瀏覽器
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服務器已停止")

if __name__ == '__main__':
    main()