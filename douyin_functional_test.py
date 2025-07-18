#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音功能测试脚本
测试BVS Analyzer对抖音视频的实际处理能力
"""

import sys
import tempfile
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# 测试用的抖音视频链接
TEST_DOUYIN_URL = "https://www.douyin.com/jingxuan?modal_id=7526877413813292329"

def test_video_info_extraction():
    """测试视频信息提取"""
    console = Console()
    console.print("\n🔍 测试视频信息提取...")
    
    try:
        from crawler.video_downloader import VideoDownloader
        
        downloader = VideoDownloader(console=console)
        video_info = downloader.get_video_info(TEST_DOUYIN_URL)
        
        if video_info:
            console.print("  ✅ 视频信息提取成功")
            console.print(f"  📹 标题: {video_info.get('title', 'Unknown')}")
            console.print(f"  ⏱️ 时长: {video_info.get('duration', 'Unknown')}秒")
            console.print(f"  👤 作者: {video_info.get('uploader', 'Unknown')}")
            return True, video_info
        else:
            console.print("  ❌ 视频信息提取失败")
            return False, None
            
    except Exception as e:
        console.print(f"  💥 视频信息提取异常: {e}")
        return False, None

def test_audio_transcription():
    """测试音频转写功能"""
    console = Console()
    console.print("\n🎵 测试音频转写功能...")
    
    try:
        from parser.audio_parser import AudioParser
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            audio_dir = temp_path / "audio"
            transcript_dir = temp_path / "transcripts"
            
            parser = AudioParser(console=console)
            parser.configure(
                audio_output_dir=str(audio_dir),
                transcript_output_dir=str(transcript_dir)
            )
            
            console.print("  🔄 开始音频转写（这可能需要几分钟）...")
            result = parser.transcribe_from_url(
                TEST_DOUYIN_URL,
                save_audio=True,
                save_transcript=True
            )
            
            if result and result.get('text'):
                console.print("  ✅ 音频转写成功")
                text = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
                console.print(f"  📝 转写文本预览: {text}")
                console.print(f"  📊 文本长度: {len(result['text'])} 字符")
                return True, result
            else:
                console.print("  ❌ 音频转写失败或无文本内容")
                return False, None
                
    except Exception as e:
        console.print(f"  💥 音频转写异常: {e}")
        return False, None

def test_report_generation(video_info, transcription_result):
    """测试报告生成功能"""
    console = Console()
    console.print("\n📊 测试报告生成功能...")
    
    try:
        from report.report_generator import ReportGenerator
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            reports_dir = temp_path / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            reporter = ReportGenerator(console=console)
            
            # 生成Markdown报告
            md_path = reporter.generate_markdown_report(
                video_info,
                transcription_result,
                str(reports_dir / "test_report.md")
            )
            
            # 生成JSON报告
            json_path = reporter.generate_json_report(
                video_info,
                transcription_result,
                str(reports_dir / "test_data.json")
            )
            
            if md_path and json_path:
                console.print("  ✅ 报告生成成功")
                console.print(f"  📄 Markdown报告: {Path(md_path).name}")
                console.print(f"  📋 JSON数据: {Path(json_path).name}")
                
                # 显示分析摘要
                console.print("\n  📈 分析摘要:")
                reporter.display_summary(video_info, transcription_result)
                
                return True
            else:
                console.print("  ❌ 报告生成失败")
                return False
                
    except Exception as e:
        console.print(f"  💥 报告生成异常: {e}")
        return False

def test_integrated_analysis():
    """测试集成分析功能"""
    console = Console()
    console.print("\n🚀 测试集成分析功能...")
    
    try:
        from main import BVSAnalyzer
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            analyzer = BVSAnalyzer(output_dir=temp_dir)
            
            console.print("  🔄 开始完整分析流程...")
            result = analyzer.analyze_single_video(
                TEST_DOUYIN_URL,
                download_video=False,  # 不下载视频文件以节省时间
                generate_report=True
            )
            
            if result.get('success'):
                console.print("  ✅ 集成分析成功")
                console.print(f"  📁 输出目录: {result.get('output_dir')}")
                
                # 检查生成的文件
                output_path = Path(result['output_dir'])
                generated_files = list(output_path.rglob("*"))
                console.print(f"  📄 生成文件数: {len([f for f in generated_files if f.is_file()])}")
                
                return True, result
            else:
                console.print(f"  ❌ 集成分析失败: {result.get('error')}")
                return False, None
                
    except Exception as e:
        console.print(f"  💥 集成分析异常: {e}")
        return False, None

def main():
    """主测试函数"""
    console = Console()
    
    console.print(Panel(
        f"🧪 BVS Analyzer 抖音功能测试\n\n测试视频: {TEST_DOUYIN_URL}",
        title="功能测试",
        border_style="blue"
    ))
    
    # 测试步骤
    tests = [
        ("视频信息提取", test_video_info_extraction),
        ("音频转写", test_audio_transcription),
    ]
    
    results = []
    video_info = None
    transcription_result = None
    
    # 执行前两个测试
    for test_name, test_func in tests:
        try:
            if test_name == "视频信息提取":
                success, data = test_func()
                if success:
                    video_info = data
                results.append((test_name, success))
            elif test_name == "音频转写":
                success, data = test_func()
                if success:
                    transcription_result = data
                results.append((test_name, success))
        except Exception as e:
            console.print(f"💥 {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 如果前两个测试成功，继续后续测试
    if video_info and transcription_result:
        try:
            success = test_report_generation(video_info, transcription_result)
            results.append(("报告生成", success))
        except Exception as e:
            console.print(f"💥 报告生成测试异常: {e}")
            results.append(("报告生成", False))
        
        try:
            success, _ = test_integrated_analysis()
            results.append(("集成分析", success))
        except Exception as e:
            console.print(f"💥 集成分析测试异常: {e}")
            results.append(("集成分析", False))
    
    # 显示结果
    console.print("\n" + "=" * 60)
    console.print("📊 功能测试结果:")
    
    success_count = 0
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        console.print(f"  {test_name}: {status}")
        if success:
            success_count += 1
    
    total_count = len(results)
    console.print(f"\n总计: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        console.print(Panel(
            "🎉 所有功能测试通过！\n\nBVS Analyzer 第一阶段开发完成，\n抖音视频分析功能正常工作。",
            title="测试完成",
            border_style="green"
        ))
    elif success_count >= 2:  # 至少基本功能正常
        console.print(Panel(
            f"⚠️ 部分功能测试通过 ({success_count}/{total_count})\n\n核心功能正常，建议检查失败的模块。",
            title="部分成功",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            f"❌ 功能测试失败 ({success_count}/{total_count})\n\n请检查依赖包安装和网络连接。",
            title="测试失败",
            border_style="red"
        ))
    
    return success_count >= 2  # 至少基本功能正常即可

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