#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BVS Analyzer 单元测试
测试第一阶段核心功能模块
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json
from rich.console import Console

# 导入待测试的模块
from crawler.video_downloader import VideoDownloader
from parser.audio_parser import AudioParser
from report.report_generator import ReportGenerator
from main import BVSAnalyzer


class TestVideoDownloader(unittest.TestCase):
    """
    测试视频下载器模块
    """
    
    def setUp(self):
        """测试前准备"""
        self.console = Console(file=open('/dev/null', 'w'))  # 静默输出
        self.downloader = VideoDownloader(console=self.console)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.downloader, VideoDownloader)
        self.assertEqual(self.downloader.console, self.console)
    
    def test_configure_options(self):
        """测试配置选项"""
        self.downloader.configure_options(
            output_path=self.temp_dir,
            format_selector="best[height<=720]",
            save_metadata=True
        )
        
        # 验证配置是否正确设置
        self.assertEqual(self.downloader.output_path, self.temp_dir)
        self.assertEqual(self.downloader.format_selector, "best[height<=720]")
        self.assertTrue(self.downloader.save_metadata)
    
    @patch('yt_dlp.YoutubeDL')
    def test_get_video_info(self, mock_ytdl):
        """测试获取视频信息"""
        # 模拟返回数据
        mock_info = {
            'id': 'test_video_id',
            'title': '测试视频标题',
            'uploader': '测试作者',
            'duration': 300,
            'view_count': 10000,
            'like_count': 500
        }
        
        mock_instance = Mock()
        mock_instance.extract_info.return_value = mock_info
        mock_ytdl.return_value.__enter__.return_value = mock_instance
        
        # 执行测试
        result = self.downloader.get_video_info("https://test.com/video")
        
        # 验证结果
        self.assertEqual(result, mock_info)
        mock_instance.extract_info.assert_called_once()
    
    def test_format_duration(self):
        """测试时长格式化"""
        # 测试秒数
        self.assertEqual(self.downloader._format_duration(30), "30秒")
        
        # 测试分钟
        self.assertEqual(self.downloader._format_duration(90), "1分30秒")
        
        # 测试小时
        self.assertEqual(self.downloader._format_duration(3661), "1小时1分1秒")


class TestAudioParser(unittest.TestCase):
    """
    测试音频解析器模块
    """
    
    def setUp(self):
        """测试前准备"""
        self.console = Console(file=open('/dev/null', 'w'))
        self.parser = AudioParser(console=self.console)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.parser, AudioParser)
        self.assertEqual(self.parser.console, self.console)
    
    def test_configure(self):
        """测试配置"""
        self.parser.configure(
            audio_output_dir=self.temp_dir,
            transcript_output_dir=self.temp_dir,
            model_size="base"
        )
        
        self.assertEqual(str(self.parser.audio_output_dir), self.temp_dir)
        self.assertEqual(str(self.parser.transcript_output_dir), self.temp_dir)
        self.assertEqual(self.parser.model_size, "base")
    
    def test_format_time_for_srt(self):
        """测试SRT时间格式化"""
        # 测试正常时间
        result = self.parser._format_time_for_srt(65.5)
        self.assertEqual(result, "00:01:05,500")
        
        # 测试小时
        result = self.parser._format_time_for_srt(3665.123)
        self.assertEqual(result, "01:01:05,123")
    
    def test_generate_srt_content(self):
        """测试SRT内容生成"""
        segments = [
            {'start': 0.0, 'end': 2.5, 'text': '第一段文本'},
            {'start': 2.5, 'end': 5.0, 'text': '第二段文本'}
        ]
        
        result = self.parser._generate_srt_content(segments)
        
        # 验证SRT格式
        self.assertIn('1\n00:00:00,000 --> 00:00:02,500\n第一段文本', result)
        self.assertIn('2\n00:00:02,500 --> 00:00:05,000\n第二段文本', result)


class TestReportGenerator(unittest.TestCase):
    """
    测试报告生成器模块
    """
    
    def setUp(self):
        """测试前准备"""
        self.console = Console(file=open('/dev/null', 'w'))
        self.reporter = ReportGenerator(console=self.console)
        self.temp_dir = tempfile.mkdtemp()
        
        # 模拟数据
        self.mock_video_info = {
            'id': 'test_video',
            'title': '测试视频标题',
            'uploader': '测试作者',
            'duration': 300,
            'view_count': 10000,
            'like_count': 500,
            'upload_date': '20240101'
        }
        
        self.mock_transcription = {
            'text': '这是一个测试视频的完整转写文本。',
            'language': 'zh',
            'segments': [
                {'start': 0.0, 'end': 2.0, 'text': '你知道什么样的开头'},
                {'start': 2.0, 'end': 4.0, 'text': '能让观众看完整个视频吗？'},
                {'start': 4.0, 'end': 6.0, 'text': '今天我来告诉你秘密。'}
            ]
        }
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.reporter, ReportGenerator)
        self.assertEqual(self.reporter.console, self.console)
    
    def test_format_duration(self):
        """测试时长格式化"""
        self.assertEqual(self.reporter._format_duration(30), "30.0秒")
        self.assertEqual(self.reporter._format_duration(90), "1分30秒")
        self.assertEqual(self.reporter._format_duration(3661), "1小时1分钟")
    
    def test_format_time(self):
        """测试时间戳格式化"""
        self.assertEqual(self.reporter._format_time(65), "01:05")
        self.assertEqual(self.reporter._format_time(125), "02:05")
    
    def test_format_number(self):
        """测试数字格式化"""
        self.assertEqual(self.reporter._format_number(5000), "5000")
        self.assertEqual(self.reporter._format_number(15000), "1.5万")
        self.assertEqual(self.reporter._format_number("N/A"), "N/A")
    
    def test_extract_hook_content(self):
        """测试钩子内容提取"""
        result = self.reporter._extract_hook_content(self.mock_transcription['segments'])
        
        # 验证钩子类型识别
        self.assertIn("疑问式钩子", result)
        self.assertIn("你知道什么样的开头能让观众看完整个视频吗？", result)
    
    def test_analyze_hook(self):
        """测试钩子分析"""
        result = self.reporter._analyze_hook(self.mock_transcription['segments'])
        
        self.assertEqual(result['type'], 'question')
        self.assertIn('你知道', result['content'])
        self.assertEqual(result['duration'], 4.0)
    
    def test_generate_markdown_report(self):
        """测试Markdown报告生成"""
        output_path = Path(self.temp_dir) / "test_report.md"
        
        result_path = self.reporter.generate_markdown_report(
            self.mock_video_info,
            self.mock_transcription,
            str(output_path)
        )
        
        # 验证文件生成
        self.assertTrue(Path(result_path).exists())
        
        # 验证内容
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('# 视频分析报告', content)
            self.assertIn('测试视频标题', content)
            self.assertIn('疑问式钩子', content)
    
    def test_generate_json_report(self):
        """测试JSON报告生成"""
        output_path = Path(self.temp_dir) / "test_data.json"
        
        result_path = self.reporter.generate_json_report(
            self.mock_video_info,
            self.mock_transcription,
            str(output_path)
        )
        
        # 验证文件生成
        self.assertTrue(Path(result_path).exists())
        
        # 验证JSON结构
        with open(result_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertIn('basic_info', data)
            self.assertIn('transcription', data)
            self.assertIn('analysis', data)
            self.assertEqual(data['analysis']['hook_analysis']['type'], 'question')


class TestBVSAnalyzer(unittest.TestCase):
    """
    测试主分析器类
    """
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = BVSAnalyzer(output_dir=self.temp_dir)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.analyzer, BVSAnalyzer)
        self.assertTrue(self.analyzer.output_dir.exists())
        self.assertTrue(self.analyzer.video_dir.exists())
        self.assertTrue(self.analyzer.audio_dir.exists())
        self.assertTrue(self.analyzer.transcripts_dir.exists())
        self.assertTrue(self.analyzer.reports_dir.exists())
    
    @patch.object(VideoDownloader, 'get_video_info')
    @patch.object(VideoDownloader, 'download_video')
    @patch.object(AudioParser, 'transcribe_from_url')
    @patch.object(ReportGenerator, 'generate_markdown_report')
    @patch.object(ReportGenerator, 'generate_json_report')
    def test_analyze_single_video_success(self, mock_json_report, mock_md_report, 
                                        mock_transcribe, mock_download, mock_info):
        """测试单个视频分析成功流程"""
        # 设置模拟返回值
        mock_info.return_value = {'id': 'test', 'title': '测试视频'}
        mock_download.return_value = '/path/to/video.mp4'
        mock_transcribe.return_value = {'text': '测试转写', 'segments': []}
        mock_md_report.return_value = '/path/to/report.md'
        mock_json_report.return_value = '/path/to/data.json'
        
        # 执行测试
        result = self.analyzer.analyze_single_video("https://test.com/video")
        
        # 验证结果
        self.assertTrue(result['success'])
        self.assertIn('video_info', result)
        self.assertIn('transcription', result)
        self.assertIn('report_paths', result)
        
        # 验证方法调用
        mock_info.assert_called_once()
        mock_download.assert_called_once()
        mock_transcribe.assert_called_once()
        mock_md_report.assert_called_once()
        mock_json_report.assert_called_once()
    
    @patch.object(VideoDownloader, 'get_video_info')
    def test_analyze_single_video_failure(self, mock_info):
        """测试单个视频分析失败流程"""
        # 设置模拟异常
        mock_info.side_effect = Exception("网络错误")
        
        # 执行测试
        result = self.analyzer.analyze_single_video("https://test.com/video")
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], "网络错误")


class TestIntegration(unittest.TestCase):
    """
    集成测试 - 测试模块间协作
    """
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_module_integration(self):
        """测试模块集成"""
        console = Console(file=open('/dev/null', 'w'))
        
        # 创建各模块实例
        downloader = VideoDownloader(console=console)
        parser = AudioParser(console=console)
        reporter = ReportGenerator(console=console)
        
        # 验证模块可以正常协作
        self.assertIsInstance(downloader, VideoDownloader)
        self.assertIsInstance(parser, AudioParser)
        self.assertIsInstance(reporter, ReportGenerator)
        
        # 测试配置传递
        downloader.configure_options(output_path=self.temp_dir)
        parser.configure(audio_output_dir=self.temp_dir)
        
        self.assertEqual(downloader.output_path, self.temp_dir)
        self.assertEqual(str(parser.audio_output_dir), self.temp_dir)


def run_douyin_test():
    """
    使用真实抖音链接进行功能测试
    """
    console = Console()
    
    console.print("\n🧪 [bold blue]开始抖音链接功能测试[/bold blue]")
    console.print("链接: https://www.douyin.com/jingxuan?modal_id=7526877413813292329")
    
    try:
        # 创建临时测试目录
        test_dir = tempfile.mkdtemp(prefix="bvs_test_")
        console.print(f"测试目录: {test_dir}")
        
        # 创建分析器
        analyzer = BVSAnalyzer(output_dir=test_dir)
        
        # 执行分析（仅转写，不下载视频以节省时间）
        console.print("\n📝 [yellow]开始分析（仅转写模式）...[/yellow]")
        result = analyzer.analyze_single_video(
            "https://www.douyin.com/jingxuan?modal_id=7526877413813292329",
            download_video=False,  # 不下载视频文件
            generate_report=True
        )
        
        if result['success']:
            console.print("\n✅ [green]抖音链接测试成功！[/green]")
            console.print(f"视频标题: {result['video_info'].get('title', 'N/A')}")
            console.print(f"转写文本长度: {len(result['transcription'].get('text', ''))} 字符")
            console.print(f"报告文件: {result['report_paths']}")
        else:
            console.print(f"\n❌ [red]抖音链接测试失败: {result['error']}[/red]")
        
        # 清理测试目录
        shutil.rmtree(test_dir, ignore_errors=True)
        
        return result['success']
        
    except Exception as e:
        console.print(f"\n💥 [red]测试过程中发生异常: {str(e)}[/red]")
        return False


if __name__ == '__main__':
    # 运行单元测试
    console = Console()
    
    console.print("\n🧪 [bold blue]BVS Analyzer 单元测试套件[/bold blue]")
    console.print("=" * 50)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestVideoDownloader,
        TestAudioParser, 
        TestReportGenerator,
        TestBVSAnalyzer,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 显示测试结果
    console.print("\n" + "=" * 50)
    if result.wasSuccessful():
        console.print("✅ [green]所有单元测试通过！[/green]")
    else:
        console.print(f"❌ [red]测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误[/red]")
    
    # 运行抖音链接功能测试
    console.print("\n" + "=" * 50)
    douyin_success = run_douyin_test()
    
    # 最终总结
    console.print("\n" + "=" * 50)
    console.print("📊 [bold]测试总结[/bold]")
    console.print(f"单元测试: {'✅ 通过' if result.wasSuccessful() else '❌ 失败'}")
    console.print(f"功能测试: {'✅ 通过' if douyin_success else '❌ 失败'}")
    
    if result.wasSuccessful() and douyin_success:
        console.print("\n🎉 [bold green]所有测试通过，第一阶段功能验证完成！[/bold green]")
    else:
        console.print("\n⚠️ [bold yellow]部分测试未通过，请检查相关功能。[/bold yellow]")