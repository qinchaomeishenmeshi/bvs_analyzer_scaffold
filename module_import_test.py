#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块导入测试脚本
逐步测试各个依赖包的导入情况
"""

import sys
from pathlib import Path

def test_standard_library():
    """测试标准库导入"""
    print("📚 标准库导入测试")
    
    modules = [
        'os', 'sys', 'json', 'pathlib', 'argparse',
        'tempfile', 'subprocess', 'datetime', 'typing'
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_third_party_basic():
    """测试基础第三方库"""
    print("\n📦 基础第三方库测试")
    
    modules = [
        ('requests', 'HTTP请求库'),
        ('rich', 'Rich终端库'),
        ('pathlib', '路径处理')
    ]
    
    failed = []
    for module, desc in modules:
        try:
            __import__(module)
            print(f"  ✅ {module} ({desc})")
        except ImportError as e:
            print(f"  ❌ {module} ({desc}): {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_rich_components():
    """测试Rich组件"""
    print("\n🎨 Rich组件测试")
    
    components = [
        'rich.console',
        'rich.panel', 
        'rich.progress',
        'rich.table'
    ]
    
    failed = []
    for component in components:
        try:
            __import__(component)
            print(f"  ✅ {component}")
        except ImportError as e:
            print(f"  ❌ {component}: {e}")
            failed.append(component)
    
    return len(failed) == 0

def test_video_processing():
    """测试视频处理相关库"""
    print("\n🎬 视频处理库测试")
    
    modules = [
        ('yt_dlp', '视频下载库'),
        ('ffmpeg', 'FFmpeg Python绑定'),
        ('whisper', 'OpenAI Whisper语音识别')
    ]
    
    available = []
    failed = []
    
    for module, desc in modules:
        try:
            __import__(module)
            print(f"  ✅ {module} ({desc})")
            available.append(module)
        except ImportError as e:
            print(f"  ❌ {module} ({desc}): {e}")
            failed.append(module)
    
    if failed:
        print(f"\n  ⚠️ 缺失的视频处理库: {failed}")
        print("  💡 请运行: pip install yt-dlp openai-whisper ffmpeg-python")
    
    return len(available) > 0  # 至少有一个可用即可

def test_custom_modules():
    """测试自定义模块导入"""
    print("\n🔧 自定义模块测试")
    
    modules = [
        ('crawler.video_downloader', 'VideoDownloader'),
        ('parser.audio_parser', 'AudioParser'),
        ('report.report_generator', 'ReportGenerator')
    ]
    
    failed = []
    for module_path, class_name in modules:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"  ✅ {module_path}.{class_name}")
        except ImportError as e:
            print(f"  ❌ {module_path}.{class_name}: 导入错误 - {e}")
            failed.append(module_path)
        except AttributeError as e:
            print(f"  ❌ {module_path}.{class_name}: 类不存在 - {e}")
            failed.append(module_path)
        except Exception as e:
            print(f"  ❌ {module_path}.{class_name}: 其他错误 - {e}")
            failed.append(module_path)
    
    return len(failed) == 0

def test_main_module():
    """测试主模块"""
    print("\n🚀 主模块测试")
    
    try:
        from main import BVSAnalyzer
        print("  ✅ main.BVSAnalyzer 导入成功")
        
        # 尝试创建实例
        analyzer = BVSAnalyzer(output_dir="test_temp")
        print("  ✅ BVSAnalyzer 实例创建成功")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ main.BVSAnalyzer 导入失败: {e}")
        return False
    except Exception as e:
        print(f"  ❌ BVSAnalyzer 实例创建失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n⚙️ 基本功能测试")
    
    try:
        from rich.console import Console
        console = Console()
        console.print("Rich Console 工作正常", style="green")
        print("  ✅ Rich Console 功能正常")
        
        from pathlib import Path
        test_path = Path("test_temp")
        test_path.mkdir(exist_ok=True)
        test_path.rmdir()
        print("  ✅ 文件系统操作正常")
        
        import json
        test_data = {"test": "data"}
        json_str = json.dumps(test_data)
        parsed_data = json.loads(json_str)
        print("  ✅ JSON处理正常")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 基本功能测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 BVS Analyzer 模块导入测试")
    print("=" * 60)
    
    tests = [
        ("标准库", test_standard_library),
        ("基础第三方库", test_third_party_basic),
        ("Rich组件", test_rich_components),
        ("视频处理库", test_video_processing),
        ("自定义模块", test_custom_modules),
        ("主模块", test_main_module),
        ("基本功能", test_basic_functionality)
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
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    
    success_count = 0
    critical_failures = []
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
        if success:
            success_count += 1
        else:
            if test_name in ["标准库", "自定义模块", "主模块"]:
                critical_failures.append(test_name)
    
    total_count = len(results)
    print(f"\n总计: {success_count}/{total_count} 通过")
    
    if critical_failures:
        print(f"\n🚨 关键模块失败: {critical_failures}")
        print("这些模块是核心功能，必须修复后才能继续。")
    elif success_count >= total_count - 1:  # 允许视频处理库缺失
        print("\n🎉 核心模块测试通过！")
        print("项目可以进行基本功能测试。")
        if success_count < total_count:
            print("💡 建议安装缺失的依赖包以获得完整功能。")
    else:
        print(f"\n⚠️ {total_count - success_count} 个测试失败")
        print("请安装缺失的依赖包。")
    
    return len(critical_failures) == 0

if __name__ == "__main__":
    try:
        success = main()
        print(f"\n退出码: {0 if success else 1}")
    except Exception as e:
        print(f"\n程序异常: {e}")
        print("退出码: 1")