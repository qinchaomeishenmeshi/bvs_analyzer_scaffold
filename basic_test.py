#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础测试脚本
只测试最基本的功能
"""

import os
import sys
from pathlib import Path

def test_python_basic():
    """测试Python基础功能"""
    print("🐍 Python基础测试")
    print(f"  Python版本: {sys.version}")
    print(f"  当前目录: {os.getcwd()}")
    print("  ✅ Python基础功能正常")
    return True

def test_file_structure():
    """测试文件结构"""
    print("\n📁 文件结构测试")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'crawler/__init__.py',
        'crawler/video_downloader.py',
        'parser/__init__.py', 
        'parser/audio_parser.py',
        'report/__init__.py',
        'report/report_generator.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} 缺失")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n  缺失文件: {missing_files}")
        return False
    else:
        print("  ✅ 所有必需文件存在")
        return True

def test_basic_imports():
    """测试基础导入"""
    print("\n📦 基础导入测试")
    
    basic_modules = [
        'os',
        'sys', 
        'json',
        'pathlib',
        'argparse'
    ]
    
    failed_imports = []
    for module in basic_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n  导入失败: {failed_imports}")
        return False
    else:
        print("  ✅ 基础模块导入正常")
        return True

def test_syntax_check():
    """测试主要文件语法"""
    print("\n🔍 语法检查测试")
    
    python_files = [
        'main.py',
        'crawler/video_downloader.py',
        'parser/audio_parser.py',
        'report/report_generator.py'
    ]
    
    syntax_errors = []
    for file_path in python_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, file_path, 'exec')
                print(f"  ✅ {file_path}")
            except SyntaxError as e:
                print(f"  ❌ {file_path}: 语法错误 - {e}")
                syntax_errors.append(file_path)
            except Exception as e:
                print(f"  ⚠️ {file_path}: 其他错误 - {e}")
        else:
            print(f"  ❌ {file_path}: 文件不存在")
            syntax_errors.append(file_path)
    
    if syntax_errors:
        print(f"\n  语法错误文件: {syntax_errors}")
        return False
    else:
        print("  ✅ 所有文件语法正确")
        return True

def main():
    """主测试函数"""
    print("🧪 BVS Analyzer 基础功能测试")
    print("=" * 50)
    
    tests = [
        ("Python基础", test_python_basic),
        ("文件结构", test_file_structure), 
        ("基础导入", test_basic_imports),
        ("语法检查", test_syntax_check)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"💥 {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    
    success_count = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if success:
            success_count += 1
    
    total_count = len(results)
    print(f"\n总计: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("\n🎉 基础功能测试全部通过！")
        print("项目结构和语法检查正常，可以进行下一步测试。")
    else:
        print(f"\n⚠️ {total_count - success_count} 个测试失败")
        print("请先修复基础问题再进行功能测试。")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n退出码: {0 if success else 1}")
    except Exception as e:
        print(f"\n程序异常: {e}")
        print("退出码: 1")