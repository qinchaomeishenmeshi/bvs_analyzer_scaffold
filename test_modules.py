#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BVS Analyzer 模块测试脚本
用于验证各个模块是否正常导入和基本功能
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


def test_imports():
    """
    测试模块导入
    """
    console = Console()
    results = []
    
    # 测试导入各个模块
    modules_to_test = [
        ('crawler.video_downloader', 'VideoDownloader'),
        ('crawler.douyin_downloader', 'DouyinDownloader'),
        ('parser.audio_parser', 'AudioParser'),
        ('report.report_generator', 'ReportGenerator'),
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            results.append((module_name, class_name, '✅ 成功', None))
        except Exception as e:
            results.append((module_name, class_name, '❌ 失败', str(e)))
    
    # 显示结果
    table = Table(title="模块导入测试结果")
    table.add_column("模块", style="cyan")
    table.add_column("类名", style="blue")
    table.add_column("状态", style="white")
    table.add_column("错误信息", style="red")
    
    for module_name, class_name, status, error in results:
        table.add_row(module_name, class_name, status, error or "")
    
    console.print(table)
    
    # 统计结果
    success_count = sum(1 for _, _, status, _ in results if '✅' in status)
    total_count = len(results)
    
    if success_count == total_count:
        console.print(Panel(
            f"🎉 所有模块导入成功！({success_count}/{total_count})",
            title="测试完成",
            border_style="green"
        ))
        return True
    else:
        console.print(Panel(
            f"⚠️ 部分模块导入失败：{success_count}/{total_count}",
            title="测试完成",
            border_style="yellow"
        ))
        return False


def test_dependencies():
    """
    测试关键依赖包
    """
    console = Console()
    results = []
    
    # 测试关键依赖
    dependencies = [
        'yt_dlp',
        'whisper',
        'rich',
        'requests',
        'pathlib',
        'json',
        'subprocess',
        'argparse'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            results.append((dep, '✅ 已安装', None))
        except ImportError as e:
            results.append((dep, '❌ 缺失', str(e)))
    
    # 显示结果
    table = Table(title="依赖包检查结果")
    table.add_column("依赖包", style="cyan")
    table.add_column("状态", style="white")
    table.add_column("错误信息", style="red")
    
    for dep, status, error in results:
        table.add_row(dep, status, error or "")
    
    console.print(table)
    
    # 统计结果
    success_count = sum(1 for _, status, _ in results if '✅' in status)
    total_count = len(results)
    
    if success_count == total_count:
        console.print(Panel(
            f"🎉 所有依赖包检查通过！({success_count}/{total_count})",
            title="依赖检查完成",
            border_style="green"
        ))
        return True
    else:
        console.print(Panel(
            f"⚠️ 部分依赖包缺失：{success_count}/{total_count}\n请运行: pip install -r requirements.txt",
            title="依赖检查完成",
            border_style="yellow"
        ))
        return False


def test_basic_functionality():
    """
    测试基本功能
    """
    console = Console()
    
    try:
        # 测试创建各个类的实例
        from crawler.video_downloader import VideoDownloader
        from parser.audio_parser import AudioParser
        from report.report_generator import ReportGenerator
        
        # 创建实例
        downloader = VideoDownloader(console=console)
        parser = AudioParser(console=console)
        reporter = ReportGenerator(console=console)
        
        console.print(Panel(
            "✅ 所有模块实例化成功！\n" +
            "- VideoDownloader: 已创建\n" +
            "- AudioParser: 已创建\n" +
            "- ReportGenerator: 已创建",
            title="功能测试完成",
            border_style="green"
        ))
        return True
        
    except Exception as e:
        console.print(Panel(
            f"❌ 模块实例化失败: {str(e)}",
            title="功能测试失败",
            border_style="red"
        ))
        return False


def check_project_structure():
    """
    检查项目结构
    """
    console = Console()
    
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'crawler/video_downloader.py',
        'crawler/douyin_downloader.py',
        'parser/audio_parser.py',
        'report/report_generator.py',
        'docs/PRD.md',
        'docs/task.md'
    ]
    
    results = []
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            results.append((file_path, '✅ 存在'))
        else:
            results.append((file_path, '❌ 缺失'))
    
    # 显示结果
    table = Table(title="项目结构检查")
    table.add_column("文件路径", style="cyan")
    table.add_column("状态", style="white")
    
    for file_path, status in results:
        table.add_row(file_path, status)
    
    console.print(table)
    
    success_count = sum(1 for _, status in results if '✅' in status)
    total_count = len(results)
    
    if success_count == total_count:
        console.print(Panel(
            f"🎉 项目结构完整！({success_count}/{total_count})",
            title="结构检查完成",
            border_style="green"
        ))
        return True
    else:
        console.print(Panel(
            f"⚠️ 部分文件缺失：{success_count}/{total_count}",
            title="结构检查完成",
            border_style="yellow"
        ))
        return False


def main():
    """
    主测试函数
    """
    console = Console()
    
    console.print(Panel(
        "🧪 BVS Analyzer 模块测试",
        title="开始测试",
        border_style="blue"
    ))
    
    # 执行各项测试
    tests = [
        ("项目结构检查", check_project_structure),
        ("依赖包检查", test_dependencies),
        ("模块导入测试", test_imports),
        ("基本功能测试", test_basic_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        console.print(f"\n[cyan]正在执行: {test_name}[/]")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            console.print(f"[red]测试异常: {str(e)}[/]")
            results.append((test_name, False))
    
    # 总结
    console.print("\n" + "="*50)
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    if success_count == total_count:
        console.print(Panel(
            f"🎉 所有测试通过！({success_count}/{total_count})\n" +
            "BVS Analyzer 已准备就绪，可以开始使用！",
            title="测试总结",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"⚠️ 部分测试失败：{success_count}/{total_count}\n" +
            "请检查失败的项目并修复后再试。",
            title="测试总结",
            border_style="yellow"
        ))
        
        # 显示使用建议
        console.print("\n[yellow]建议操作:[/]")
        console.print("1. 安装缺失的依赖: pip install -r requirements.txt")
        console.print("2. 检查 FFmpeg 是否已安装")
        console.print("3. 确保所有必需文件存在")


if __name__ == "__main__":
    main()