#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单功能测试
验证BVS Analyzer基本功能
"""

import sys
from pathlib import Path

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试基本导入
        print("  导入 rich...")
        from rich.console import Console
        console = Console()
        print("  ✅ rich 导入成功")
        
        print("  导入 pathlib...")
        from pathlib import Path
        print("  ✅ pathlib 导入成功")
        
        print("  导入 json...")
        import json
        print("  ✅ json 导入成功")
        
        # 测试自定义模块
        print("  导入 VideoDownloader...")
        from crawler.video_downloader import VideoDownloader
        print("  ✅ VideoDownloader 导入成功")
        
        print("  导入 AudioParser...")
        from parser.audio_parser import AudioParser
        print("  ✅ AudioParser 导入成功")
        
        print("  导入 ReportGenerator...")
        from report.report_generator import ReportGenerator
        print("  ✅ ReportGenerator 导入成功")
        
        print("  导入 BVSAnalyzer...")
        from main import BVSAnalyzer
        print("  ✅ BVSAnalyzer 导入成功")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"  💥 导入异常: {e}")
        return False

def test_class_creation():
    """测试类实例化"""
    print("\n🏗️ 测试类实例化...")
    
    try:
        from rich.console import Console
        from crawler.video_downloader import VideoDownloader
        from parser.audio_parser import AudioParser
        from report.report_generator import ReportGenerator
        from main import BVSAnalyzer
        
        console = Console()
        
        print("  创建 VideoDownloader...")
        downloader = VideoDownloader(console=console)
        print("  ✅ VideoDownloader 创建成功")
        
        print("  创建 AudioParser...")
        parser = AudioParser(console=console)
        print("  ✅ AudioParser 创建成功")
        
        print("  创建 ReportGenerator...")
        reporter = ReportGenerator(console=console)
        print("  ✅ ReportGenerator 创建成功")
        
        print("  创建 BVSAnalyzer...")
        analyzer = BVSAnalyzer(output_dir="test_output")
        print("  ✅ BVSAnalyzer 创建成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 实例化失败: {e}")
        return False

def test_basic_methods():
    """测试基本方法"""
    print("\n⚙️ 测试基本方法...")
    
    try:
        from rich.console import Console
        from report.report_generator import ReportGenerator
        
        console = Console()
        reporter = ReportGenerator(console=console)
        
        # 测试格式化方法
        print("  测试时长格式化...")
        duration_result = reporter._format_duration(125)
        print(f"    125秒 -> {duration_result}")
        print("  ✅ 时长格式化正常")
        
        print("  测试时间格式化...")
        time_result = reporter._format_time(65)
        print(f"    65秒 -> {time_result}")
        print("  ✅ 时间格式化正常")
        
        print("  测试数字格式化...")
        number_result = reporter._format_number(15000)
        print(f"    15000 -> {number_result}")
        print("  ✅ 数字格式化正常")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 方法测试失败: {e}")
        return False

def test_project_structure():
    """测试项目结构"""
    print("\n📁 检查项目结构...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'crawler/video_downloader.py',
        'parser/audio_parser.py',
        'report/report_generator.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} 缺失")
            all_exist = False
    
    return all_exist

def test_dependencies():
    """测试关键依赖"""
    print("\n📦 检查依赖包...")
    
    dependencies = [
        'rich',
        'pathlib',
        'json',
        'argparse',
        'tempfile'
    ]
    
    all_ok = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"  ✅ {dep}")
        except ImportError:
            print(f"  ❌ {dep} 未安装")
            all_ok = False
    
    return all_ok

def main():
    """主测试函数"""
    print("🧪 BVS Analyzer 简单功能测试")
    print("=" * 40)
    
    tests = [
        ("依赖检查", test_dependencies),
        ("项目结构", test_project_structure),
        ("模块导入", test_imports),
        ("类实例化", test_class_creation),
        ("基本方法", test_basic_methods)
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
    print("\n" + "=" * 40)
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
        print("\n🎉 所有基本功能测试通过！")
        print("BVS Analyzer 第一阶段开发验证完成。")
    else:
        print(f"\n⚠️ {total_count - success_count} 个测试失败")
        print("请检查相关模块和依赖。")
    
    return success_count == total_count

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试程序异常: {e}")
        sys.exit(1)