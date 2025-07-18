#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音链接功能测试
测试BVS Analyzer对抖音视频的处理能力
"""

import sys
import tempfile
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# 导入BVS Analyzer
try:
    from main import BVSAnalyzer
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保所有依赖已安装: pip install -r requirements.txt")
    sys.exit(1)


def test_douyin_video():
    """
    测试抖音视频分析功能
    """
    console = Console()
    
    # 抖音测试链接
    douyin_url = "https://www.douyin.com/jingxuan?modal_id=7526877413813292329"
    
    console.print(Panel(
        f"🎬 抖音视频功能测试\n\n链接: {douyin_url}",
        title="BVS Analyzer - 抖音测试",
        border_style="blue"
    ))
    
    # 创建临时测试目录
    test_dir = tempfile.mkdtemp(prefix="bvs_douyin_test_")
    console.print(f"\n📁 测试目录: {test_dir}")
    
    try:
        # 创建分析器
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("初始化BVS分析器...", total=None)
            analyzer = BVSAnalyzer(output_dir=test_dir)
            progress.update(task, description="✅ 分析器初始化完成")
        
        console.print("\n🔍 [yellow]开始测试视频信息获取...[/yellow]")
        
        # 测试1: 获取视频信息
        try:
            video_info = analyzer.downloader.get_video_info(douyin_url)
            if video_info:
                console.print("✅ [green]视频信息获取成功[/green]")
                console.print(f"   标题: {video_info.get('title', 'N/A')[:50]}...")
                console.print(f"   作者: {video_info.get('uploader', 'N/A')}")
                console.print(f"   时长: {video_info.get('duration', 'N/A')}秒")
            else:
                console.print("❌ [red]视频信息获取失败[/red]")
                return False
        except Exception as e:
            console.print(f"❌ [red]视频信息获取异常: {str(e)}[/red]")
            return False
        
        console.print("\n🎵 [yellow]开始测试音频转写功能...[/yellow]")
        
        # 测试2: 音频转写（不下载视频文件）
        try:
            # 配置解析器
            analyzer.parser.configure(
                audio_output_dir=str(analyzer.audio_dir),
                transcript_output_dir=str(analyzer.transcripts_dir),
                model_size="base"  # 使用较小的模型以节省时间
            )
            
            # 执行转写
            transcription_result = analyzer.parser.transcribe_from_url(
                douyin_url,
                save_audio=True,
                save_transcript=True
            )
            
            if transcription_result:
                console.print("✅ [green]音频转写成功[/green]")
                text_length = len(transcription_result.get('text', ''))
                segments_count = len(transcription_result.get('segments', []))
                console.print(f"   转写文本长度: {text_length} 字符")
                console.print(f"   字幕片段数: {segments_count} 个")
                console.print(f"   识别语言: {transcription_result.get('language', 'unknown')}")
                
                # 显示前100个字符的转写内容
                if text_length > 0:
                    preview_text = transcription_result['text'][:100]
                    console.print(f"   内容预览: {preview_text}...")
            else:
                console.print("❌ [red]音频转写失败[/red]")
                return False
                
        except Exception as e:
            console.print(f"❌ [red]音频转写异常: {str(e)}[/red]")
            return False
        
        console.print("\n📊 [yellow]开始测试报告生成功能...[/yellow]")
        
        # 测试3: 报告生成
        try:
            # 生成Markdown报告
            md_report_path = analyzer.reporter.generate_markdown_report(
                video_info,
                transcription_result,
                str(analyzer.reports_dir / "douyin_test_report.md")
            )
            
            # 生成JSON报告
            json_report_path = analyzer.reporter.generate_json_report(
                video_info,
                transcription_result,
                str(analyzer.reports_dir / "douyin_test_data.json")
            )
            
            # 验证文件生成
            if Path(md_report_path).exists() and Path(json_report_path).exists():
                console.print("✅ [green]报告生成成功[/green]")
                console.print(f"   Markdown报告: {Path(md_report_path).name}")
                console.print(f"   JSON数据: {Path(json_report_path).name}")
                
                # 显示报告摘要
                analyzer.reporter.display_summary(video_info, transcription_result)
            else:
                console.print("❌ [red]报告文件生成失败[/red]")
                return False
                
        except Exception as e:
            console.print(f"❌ [red]报告生成异常: {str(e)}[/red]")
            return False
        
        # 测试完成
        console.print(Panel(
            "🎉 抖音视频功能测试全部通过！\n\n" +
            "✅ 视频信息获取\n" +
            "✅ 音频转写功能\n" +
            "✅ 报告生成功能\n\n" +
            f"测试文件保存在: {test_dir}",
            title="测试完成",
            border_style="green"
        ))
        
        return True
        
    except Exception as e:
        console.print(Panel(
            f"💥 测试过程中发生未预期的错误:\n{str(e)}",
            title="测试失败",
            border_style="red"
        ))
        return False
    
    finally:
        # 询问是否保留测试文件
        try:
            keep_files = input("\n是否保留测试文件？(y/N): ").lower().strip()
            if keep_files != 'y':
                shutil.rmtree(test_dir, ignore_errors=True)
                console.print(f"🗑️ 测试文件已清理")
            else:
                console.print(f"📁 测试文件保留在: {test_dir}")
        except KeyboardInterrupt:
            shutil.rmtree(test_dir, ignore_errors=True)
            console.print("\n🗑️ 测试文件已清理")


def test_basic_imports():
    """
    测试基本模块导入
    """
    console = Console()
    
    console.print("\n🔍 [yellow]检查模块导入...[/yellow]")
    
    try:
        from crawler.video_downloader import VideoDownloader
        console.print("✅ VideoDownloader 导入成功")
        
        from parser.audio_parser import AudioParser
        console.print("✅ AudioParser 导入成功")
        
        from report.report_generator import ReportGenerator
        console.print("✅ ReportGenerator 导入成功")
        
        from main import BVSAnalyzer
        console.print("✅ BVSAnalyzer 导入成功")
        
        return True
        
    except ImportError as e:
        console.print(f"❌ [red]模块导入失败: {str(e)}[/red]")
        return False


def test_dependencies():
    """
    测试关键依赖
    """
    console = Console()
    
    console.print("\n🔍 [yellow]检查依赖包...[/yellow]")
    
    dependencies = [
        ('yt_dlp', 'yt-dlp'),
        ('whisper', 'openai-whisper'),
        ('rich', 'rich'),
        ('requests', 'requests')
    ]
    
    all_ok = True
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            console.print(f"✅ {package_name} 已安装")
        except ImportError:
            console.print(f"❌ [red]{package_name} 未安装[/red]")
            all_ok = False
    
    return all_ok


def main():
    """
    主测试函数
    """
    console = Console()
    
    console.print(Panel(
        "🧪 BVS Analyzer 抖音功能测试\n\n" +
        "本测试将验证:\n" +
        "• 模块导入和依赖检查\n" +
        "• 抖音视频信息获取\n" +
        "• 音频转写功能\n" +
        "• 分析报告生成",
        title="开始测试",
        border_style="blue"
    ))
    
    # 执行测试步骤
    tests = [
        ("依赖检查", test_dependencies),
        ("模块导入", test_basic_imports),
        ("抖音功能", test_douyin_video)
    ]
    
    results = []
    for test_name, test_func in tests:
        console.print(f"\n{'='*50}")
        console.print(f"🧪 [bold cyan]执行测试: {test_name}[/bold cyan]")
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                console.print(f"✅ [green]{test_name} 测试通过[/green]")
            else:
                console.print(f"❌ [red]{test_name} 测试失败[/red]")
                
        except Exception as e:
            console.print(f"💥 [red]{test_name} 测试异常: {str(e)}[/red]")
            results.append((test_name, False))
    
    # 显示最终结果
    console.print(f"\n{'='*50}")
    console.print("📊 [bold]测试总结[/bold]")
    
    success_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        console.print(f"  {test_name}: {status}")
    
    if success_count == total_count:
        console.print(Panel(
            f"🎉 所有测试通过！({success_count}/{total_count})\n\n" +
            "BVS Analyzer 抖音功能验证完成，第一阶段开发成功！",
            title="测试成功",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"⚠️ 部分测试失败：{success_count}/{total_count}\n\n" +
            "请检查失败的功能模块并修复相关问题。",
            title="测试结果",
            border_style="yellow"
        ))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试程序异常: {str(e)}")
        sys.exit(1)