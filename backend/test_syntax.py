#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
语法检查和基本功能测试脚本
"""

import sys
import importlib.util

def test_syntax():
    """测试 main.py 的语法"""
    try:
        # 尝试编译文件
        import py_compile
        py_compile.compile('main.py', doraise=True)
        print("✅ 语法检查通过")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ 语法错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 编译错误: {e}")
        return False

def test_import():
    """测试模块导入"""
    try:
        # 尝试导入模块
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_module)
        print("✅ 模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入错误: {e}")
        return False

def test_flask_app():
    """测试 Flask 应用创建"""
    try:
        from main import app
        print("✅ Flask 应用创建成功")
        print(f"   - 应用名称: {app.name}")
        print(f"   - 调试模式: {app.debug}")
        return True
    except Exception as e:
        print(f"❌ Flask 应用错误: {e}")
        return False

def test_routes():
    """测试路由注册"""
    try:
        from main import app
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(f"{rule.rule} [{', '.join(rule.methods)}]")
        
        print("✅ 路由注册成功")
        for route in sorted(routes):
            print(f"   - {route}")
        return True
    except Exception as e:
        print(f"❌ 路由测试错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始测试 main.py")
    print("=" * 50)
    
    tests = [
        ("语法检查", test_syntax),
        ("模块导入", test_import),
        ("Flask 应用", test_flask_app),
        ("路由注册", test_routes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n🏁 测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！后端服务可以正常启动")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
        return 1

if __name__ == '__main__':
    sys.exit(main())