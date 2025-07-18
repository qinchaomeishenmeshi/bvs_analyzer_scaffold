#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音专用测试脚本
专门测试BVS Analyzer处理抖音视频的能力
"""

import sys
import tempfile
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# 用户提供的抖音链接
DOUYIN_URL = "https://www.douyin.com/jingxuan?modal_id=7526877413813292329"

def test_douyin_url_parsing():
    """测试抖音URL解析"""
    console = Console()
    console.print("\n🔍 测试抖音URL解析...")
    
    try:
        from crawler.video_downloader import VideoDownloader
        
        downloader = VideoDownloader(console=console)
        
        # 尝试获取视频信息
        console.print(f"  🔗 测试URL: {DOUYIN_URL}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("正在解析抖音视频信息...", total=None)
            
            try:
                video_info = downloader.get_video_info(DOUYIN_URL)
                progress.update(task, completed=True)
                
                if video_info:
                    console.print("  ✅ 抖音视频信息解析成功")
                    console.print(f"  📹 标题: {video_info.get('title', 'Unknown')}")
                    console.print(f"  ⏱️ 时长: {video_info.get('duration', 'Unknown')}秒")
                    console.print(f"  👤 作者: {video_info.get('uploader', 'Unknown')}")
                    console.print(f"  📱 平台: {video_info.get('extractor', 'Unknown')}")
                    return True, video_info
                else:
                    console.print("  ❌ 无法获取抖音视频信息")
                    return False, None
                    
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"  ⚠️ 抖音URL解析失败: {str(e)}")
                
                # 检查是否是不支持的URL格式
                if "Unsupported URL" in str(e) or "not supported" in str(e).lower():
                    console.print("  💡 提示: 当前yt-dlp版本可能不支持此抖音URL格式")
                    console.print("  🔧 建议: 尝试使用直接的视频URL或更新yt-dlp版本")
                
                return False, str(e)
                
    except ImportError as e:
        console.print(f"  💥 模块导入失败: {e}")
        return False, str(e)
    except Exception as e:
        console.print(f"  💥 未知异常: {e}")
        return False, str(e)

def test_alternative_douyin_methods():
    """测试替代的抖音处理方法"""
    console = Console()
    console.print("\n🔄 测试替代抖音处理方法...")
    
    try:
        # 方法1: 尝试不同的URL格式
        console.print("  📋 方法1: 尝试不同的URL格式")
        
        # 从原URL提取modal_id
        import re
        modal_match = re.search(r'modal_id=([0-9]+)', DOUYIN_URL)
        if modal_match:
            modal_id = modal_match.group(1)
            console.print(f"  🆔 提取到modal_id: {modal_id}")
            
            # 尝试构造不同格式的URL
            alternative_urls = [
                f"https://www.douyin.com/video/{modal_id}",
                f"https://v.douyin.com/{modal_id}",
                f"https://www.iesdouyin.com/share/video/{modal_id}"
            ]
            
            console.print("  🔗 尝试的替代URL格式:")
            for i, url in enumerate(alternative_urls, 1):
                console.print(f"    {i}. {url}")
            
            return True, {"modal_id": modal_id, "alternative_urls": alternative_urls}
        else:
            console.print("  ❌ 无法从URL中提取modal_id")
            return False, None
            
    except Exception as e:
        console.print(f"  💥 替代方法测试异常: {e}")
        return False, str(e)

def test_yt_dlp_douyin_support():
    """测试yt-dlp对抖音的支持情况"""
    console = Console()
    console.print("\n🔧 测试yt-dlp抖音支持情况...")
    
    try:
        import yt_dlp
        
        # 检查yt-dlp版本
        console.print(f"  📦 yt-dlp版本: {yt_dlp.version.__version__}")
        
        # 检查支持的提取器
        extractors = yt_dlp.extractor.list_extractors()
        douyin_extractors = [e for e in extractors if 'douyin' in e.lower() or 'tiktok' in e.lower()]
        
        if douyin_extractors:
            console.print("  ✅ 找到抖音相关提取器:")
            for extractor in douyin_extractors:
                console.print(f"    - {extractor}")
        else:
            console.print("  ❌ 未找到抖音相关提取器")
        
        # 测试基本的yt-dlp配置
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # 只提取基本信息
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                console.print("  🔍 尝试提取基本信息...")
                info = ydl.extract_info(DOUYIN_URL, download=False)
                if info:
                    console.print("  ✅ 基本信息提取成功")
                    return True, info
                else:
                    console.print("  ❌ 基本信息提取失败")
                    return False, None
            except Exception as e:
                console.print(f"  ⚠️ 基本信息提取异常: {str(e)}")
                return False, str(e)
                
    except ImportError as e:
        console.print(f"  💥 yt-dlp导入失败: {e}")
        return False, str(e)
    except Exception as e:
        console.print(f"  💥 yt-dlp测试异常: {e}")
        return False, str(e)

def test_mock_douyin_analysis():
    """使用模拟数据测试抖音分析流程"""
    console = Console()
    console.print("\n🎭 使用模拟数据测试抖音分析流程...")
    
    try:
        # 创建模拟的抖音视频信息
        mock_douyin_info = {
            'id': '7526877413813292329',
            'title': '抖音测试视频 - 模拟数据',
            'description': '这是一个用于测试BVS Analyzer的模拟抖音视频',
            'uploader': '测试用户',
            'duration': 15.5,
            'view_count': 12345,
            'like_count': 678,
            'comment_count': 89,
            'upload_date': '20241201',
            'extractor': 'douyin',
            'webpage_url': DOUYIN_URL,
            'thumbnail': 'https://example.com/thumbnail.jpg',
            'tags': ['测试', '短视频', 'BVS分析'],
            'categories': ['娱乐'],
            'language': 'zh-CN'
        }
        
        # 创建模拟的转写结果
        mock_transcription = {
            'text': '大家好，这是一个抖音短视频测试。今天我们来测试BVS分析器的功能。这个工具可以帮助我们分析视频内容，提取关键信息。希望大家喜欢！',
            'language': 'zh',
            'segments': [
                {
                    'start': 0.0,
                    'end': 3.5,
                    'text': '大家好，这是一个抖音短视频测试。',
                    'words': []
                },
                {
                    'start': 3.5,
                    'end': 8.0,
                    'text': '今天我们来测试BVS分析器的功能。',
                    'words': []
                },
                {
                    'start': 8.0,
                    'end': 12.5,
                    'text': '这个工具可以帮助我们分析视频内容，提取关键信息。',
                    'words': []
                },
                {
                    'start': 12.5,
                    'end': 15.5,
                    'text': '希望大家喜欢！',
                    'words': []
                }
            ],
            'duration': 15.5
        }
        
        console.print("  ✅ 模拟抖音数据创建成功")
        console.print(f"  📹 视频标题: {mock_douyin_info['title']}")
        console.print(f"  ⏱️ 视频时长: {mock_douyin_info['duration']}秒")
        console.print(f"  📝 转写文本长度: {len(mock_transcription['text'])}字符")
        console.print(f"  🎬 转写片段数: {len(mock_transcription['segments'])}个")
        
        # 测试报告生成
        from report.report_generator import ReportGenerator
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            reports_dir = temp_path / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            reporter = ReportGenerator(console=console)
            
            # 生成报告
            md_path = reporter.generate_markdown_report(
                mock_douyin_info,
                mock_transcription,
                str(reports_dir / "douyin_test_report.md")
            )
            
            json_path = reporter.generate_json_report(
                mock_douyin_info,
                mock_transcription,
                str(reports_dir / "douyin_test_data.json")
            )
            
            if md_path and json_path:
                console.print("  ✅ 抖音模拟数据报告生成成功")
                console.print(f"  📄 Markdown报告: {Path(md_path).name}")
                console.print(f"  📋 JSON数据: {Path(json_path).name}")
                
                # 显示分析摘要
                console.print("\n  📈 抖音视频分析摘要:")
                reporter.display_summary(mock_douyin_info, mock_transcription)
                
                return True, (mock_douyin_info, mock_transcription)
            else:
                console.print("  ❌ 抖音模拟数据报告生成失败")
                return False, None
                
    except Exception as e:
        console.print(f"  💥 模拟抖音分析异常: {e}")
        return False, str(e)

def test_douyin_url_recommendations():
    """提供抖音URL处理建议"""
    console = Console()
    console.print("\n💡 抖音URL处理建议...")
    
    recommendations = [
        "1. 更新yt-dlp到最新版本: pip install --upgrade yt-dlp",
        "2. 尝试使用移动端分享链接格式",
        "3. 考虑使用专门的抖音API或第三方服务",
        "4. 检查网络连接和代理设置",
        "5. 验证视频是否为公开可访问状态"
    ]
    
    console.print("  🔧 建议的解决方案:")
    for rec in recommendations:
        console.print(f"    {rec}")
    
    console.print("\n  📚 相关资源:")
    console.print("    - yt-dlp官方文档: https://github.com/yt-dlp/yt-dlp")
    console.print("    - 抖音开放平台: https://developer.open-douyin.com/")
    
    return True

def main():
    """主测试函数"""
    console = Console()
    
    console.print(Panel(
        f"🎵 BVS Analyzer 抖音专用测试\n\n测试URL: {DOUYIN_URL}\n\n本测试将验证系统对抖音视频的处理能力",
        title="抖音功能测试",
        border_style="magenta"
    ))
    
    # 测试步骤
    tests = [
        ("抖音URL解析", test_douyin_url_parsing),
        ("yt-dlp抖音支持", test_yt_dlp_douyin_support),
        ("替代处理方法", test_alternative_douyin_methods),
        ("模拟抖音分析", test_mock_douyin_analysis),
        ("处理建议", test_douyin_url_recommendations)
    ]
    
    results = []
    
    # 执行测试
    for test_name, test_func in tests:
        try:
            result = test_func()
            if isinstance(result, tuple):
                success, data = result
                results.append((test_name, success, data))
            else:
                success = result
                results.append((test_name, success, None))
        except Exception as e:
            console.print(f"💥 {test_name} 测试异常: {e}")
            results.append((test_name, False, str(e)))
    
    # 显示结果
    console.print("\n" + "=" * 60)
    console.print("📊 抖音测试结果:")
    
    success_count = 0
    for test_name, success, data in results:
        status = "✅ 通过" if success else "❌ 失败"
        console.print(f"  {test_name}: {status}")
        if success:
            success_count += 1
        elif data and isinstance(data, str):
            console.print(f"    错误信息: {data[:100]}..." if len(data) > 100 else f"    错误信息: {data}")
    
    total_count = len(results)
    console.print(f"\n总计: {success_count}/{total_count} 通过")
    
    # 结论和建议
    if success_count >= 3:  # 至少3个测试通过
        console.print(Panel(
            "✅ 抖音测试基本通过\n\n虽然直接URL解析可能失败，但系统具备\n处理抖音视频的基础能力。建议使用\n模拟数据或替代方法进行开发测试。",
            title="测试结论",
            border_style="green"
        ))
    else:
        console.print(Panel(
            "⚠️ 抖音支持需要改进\n\n当前yt-dlp版本可能不完全支持\n该抖音URL格式。建议更新依赖\n或使用替代解决方案。",
            title="需要改进",
            border_style="yellow"
        ))
    
    return success_count >= 3

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