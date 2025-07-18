#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BVS Analyzer - 视频结构分析工具
主程序入口文件

功能:
- 视频下载和元数据提取
- 音频转写和文本提取
- 分析报告生成
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# 导入自定义模块
from crawler.video_downloader import VideoDownloader
from parser.audio_parser import AudioParser
from report.report_generator import ReportGenerator


class BVSAnalyzer:
    """
    BVS分析器主类，协调各个模块完成视频分析任务
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        初始化BVS分析器
        :param output_dir: 输出目录
        """
        self.console = Console()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化各个模块
        self.downloader = VideoDownloader(console=self.console)
        self.parser = AudioParser(console=self.console)
        self.reporter = ReportGenerator(console=self.console)
        
        # 设置输出路径
        self.video_dir = self.output_dir / "videos"
        self.audio_dir = self.output_dir / "audio"
        self.transcripts_dir = self.output_dir / "transcripts"
        self.reports_dir = self.output_dir / "reports"
        
        # 创建必要的目录
        for directory in [self.video_dir, self.audio_dir, self.transcripts_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)
    
    def analyze_single_video(self, url: str, download_video: bool = True, 
                           generate_report: bool = True) -> dict:
        """
        分析单个视频
        :param url: 视频URL
        :param download_video: 是否下载视频文件
        :param generate_report: 是否生成分析报告
        :return: 分析结果字典
        """
        try:
            self.console.print(Panel(
                f"🎬 开始分析视频: {url}",
                title="BVS Analyzer",
                border_style="blue"
            ))
            
            # 步骤1: 获取视频信息
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("获取视频信息...", total=None)
                video_info = self.downloader.get_video_info(url)
                progress.update(task, description="✅ 视频信息获取完成")
            
            if not video_info:
                raise Exception("无法获取视频信息")
            
            # 步骤2: 下载视频（可选）
            video_path = None
            if download_video:
                self.downloader.configure_options(
                    output_path=str(self.video_dir),
                    format_selector="best[height<=720]",
                    save_metadata=True
                )
                video_path = self.downloader.download_video(url)
            
            # 步骤3: 音频提取和转写
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("提取音频并转写...", total=None)
                
                # 配置音频解析器
                self.parser.configure(
                    audio_output_dir=str(self.audio_dir),
                    transcript_output_dir=str(self.transcripts_dir)
                )
                
                # 执行转写
                transcription_result = self.parser.transcribe_from_url(
                    url, 
                    save_audio=True,
                    save_transcript=True
                )
                
                progress.update(task, description="✅ 音频转写完成")
            
            if not transcription_result:
                raise Exception("音频转写失败")
            
            # 步骤4: 生成分析报告（可选）
            report_paths = {}
            if generate_report:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("生成分析报告...", total=None)
                    
                    # 生成Markdown报告
                    md_report_path = self.reporter.generate_markdown_report(
                        video_info,
                        transcription_result,
                        str(self.reports_dir / f"{video_info.get('id', 'unknown')}_report.md")
                    )
                    
                    # 生成JSON报告
                    json_report_path = self.reporter.generate_json_report(
                        video_info,
                        transcription_result,
                        str(self.reports_dir / f"{video_info.get('id', 'unknown')}_data.json")
                    )
                    
                    report_paths = {
                        'markdown': md_report_path,
                        'json': json_report_path
                    }
                    
                    progress.update(task, description="✅ 分析报告生成完成")
                
                # 显示分析摘要
                self.reporter.display_summary(video_info, transcription_result)
            
            # 返回分析结果
            result = {
                'success': True,
                'video_info': video_info,
                'transcription': transcription_result,
                'video_path': video_path,
                'report_paths': report_paths,
                'output_dir': str(self.output_dir)
            }
            
            self.console.print(Panel(
                "🎉 视频分析完成！",
                title="分析完成",
                border_style="green"
            ))
            
            return result
            
        except Exception as e:
            self.console.print(f"[red]❌ 分析失败: {str(e)}[/]")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_batch_videos(self, urls: List[str], download_video: bool = True,
                           generate_report: bool = True) -> List[dict]:
        """
        批量分析多个视频
        :param urls: 视频URL列表
        :param download_video: 是否下载视频文件
        :param generate_report: 是否生成分析报告
        :return: 分析结果列表
        """
        results = []
        
        self.console.print(Panel(
            f"📋 开始批量分析 {len(urls)} 个视频",
            title="批量分析",
            border_style="blue"
        ))
        
        for i, url in enumerate(urls, 1):
            self.console.print(f"\n[cyan]处理第 {i}/{len(urls)} 个视频[/]")
            result = self.analyze_single_video(url, download_video, generate_report)
            results.append(result)
            
            if not result['success']:
                self.console.print(f"[yellow]⚠️ 第 {i} 个视频分析失败，继续处理下一个[/]")
        
        # 统计结果
        success_count = sum(1 for r in results if r['success'])
        self.console.print(Panel(
            f"✅ 成功: {success_count}/{len(urls)}\n❌ 失败: {len(urls) - success_count}/{len(urls)}",
            title="批量分析完成",
            border_style="green"
        ))
        
        return results


def main():
    """
    主函数，处理命令行参数并执行分析
    """
    parser = argparse.ArgumentParser(
        description="BVS Analyzer - 视频结构分析工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py -u "https://www.youtube.com/watch?v=VIDEO_ID"
  python main.py -f urls.txt --no-download
  python main.py -u "URL1" "URL2" "URL3" -o my_output
        """
    )
    
    # 输入参数
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-u", "--urls",
        nargs="+",
        help="要分析的视频URL（可以是多个）"
    )
    input_group.add_argument(
        "-f", "--file",
        help="包含视频URL的文本文件（每行一个URL）"
    )
    
    # 输出参数
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="输出目录（默认: output）"
    )
    
    # 功能选项
    parser.add_argument(
        "--no-download",
        action="store_true",
        help="不下载视频文件，仅进行音频转写和分析"
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="不生成分析报告"
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 获取URL列表
    urls = []
    if args.urls:
        urls = args.urls
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"错误: 文件 '{args.file}' 不存在")
            sys.exit(1)
        except Exception as e:
            print(f"错误: 读取文件失败 - {str(e)}")
            sys.exit(1)
    
    if not urls:
        print("错误: 没有找到有效的URL")
        sys.exit(1)
    
    # 创建分析器并执行分析
    analyzer = BVSAnalyzer(output_dir=args.output)
    
    try:
        if len(urls) == 1:
            # 单个视频分析
            result = analyzer.analyze_single_video(
                urls[0],
                download_video=not args.no_download,
                generate_report=not args.no_report
            )
            
            if not result['success']:
                sys.exit(1)
        else:
            # 批量视频分析
            results = analyzer.analyze_batch_videos(
                urls,
                download_video=not args.no_download,
                generate_report=not args.no_report
            )
            
            # 检查是否有失败的分析
            if not any(r['success'] for r in results):
                sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()