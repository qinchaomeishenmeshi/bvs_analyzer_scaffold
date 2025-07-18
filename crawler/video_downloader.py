import os
import json
from pathlib import Path
from typing import Dict, Optional, List
import yt_dlp
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn


class VideoDownloader:
    """
    通用视频下载器，支持抖音、快手、B站等平台
    """
    
    def __init__(self, console: Console = None, download_path: str = "./downloads"):
        """
        初始化视频下载器
        :param console: Rich Console对象
        :param download_path: 下载保存路径
        """
        self.console = console or Console()
        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.custom_opts = {}
    
    def configure_options(self, output_path: str = None, format_selector: str = None, save_metadata: bool = True):
        """
        配置下载选项
        :param output_path: 输出路径
        :param format_selector: 格式选择器
        :param save_metadata: 是否保存元数据
        """
        if output_path:
            self.download_path = Path(output_path)
            self.download_path.mkdir(parents=True, exist_ok=True)
        
        if format_selector:
            self.custom_opts['format'] = format_selector
        
        self.custom_opts['writeinfojson'] = save_metadata
        self.custom_opts['writethumbnail'] = save_metadata
        
    def _get_ydl_opts(self, output_path: Path) -> Dict:
        """
        获取 yt-dlp 配置选项
        """
        opts = {
            'outtmpl': str(output_path / '%(title)s.%(ext)s'),
            'format': 'best[height<=720]',  # 优先下载720p以下的视频
            'writeinfojson': True,  # 保存视频信息为JSON
            'writethumbnail': True,  # 下载缩略图
            'writesubtitles': False,  # 暂不下载字幕
            'ignoreerrors': True,  # 忽略错误继续下载
            'no_warnings': False,
        }
        
        # 应用自定义选项
        opts.update(self.custom_opts)
        return opts
    
    def download_video(self, url: str, custom_filename: str = None) -> Optional[str]:
        """
        下载视频并返回文件路径
        :param url: 视频链接
        :param custom_filename: 自定义文件名
        :return: 下载的视频文件路径
        """
        result = self.download_single_video(url, custom_filename)
        if result:
            # 尝试找到下载的视频文件
            download_dir = Path(result['download_path'])
            video_files = list(download_dir.glob("*.mp4")) + list(download_dir.glob("*.webm")) + list(download_dir.glob("*.mkv"))
            if video_files:
                return str(video_files[0])
        return None
    
    def download_single_video(self, url: str, custom_filename: str = None) -> Optional[Dict]:
        """
        下载单个视频
        :param url: 视频链接
        :param custom_filename: 自定义文件名
        :return: 下载结果信息
        """
        try:
            output_path = self.download_path
            if custom_filename:
                output_path = output_path / custom_filename
                output_path.mkdir(parents=True, exist_ok=True)
            
            ydl_opts = self._get_ydl_opts(output_path)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 先获取视频信息
                info = ydl.extract_info(url, download=False)
                
                self.console.print(f"[cyan]📹 准备下载: {info.get('title', 'Unknown')}[/]")
                self.console.print(f"[cyan]📊 时长: {info.get('duration', 0)}秒[/]")
                self.console.print(f"[cyan]👀 观看数: {info.get('view_count', 'Unknown')}[/]")
                
                # 开始下载
                ydl.download([url])
                
                # 返回视频信息
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'upload_date': info.get('upload_date'),
                    'uploader': info.get('uploader'),
                    'description': info.get('description'),
                    'url': url,
                    'download_path': str(output_path)
                }
                
        except Exception as e:
            self.console.print(f"[red]❌ 下载失败: {str(e)}[/]")
            return None
    
    def download_batch_videos(self, urls: List[str]) -> List[Dict]:
        """
        批量下载视频
        :param urls: 视频链接列表
        :return: 下载结果列表
        """
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]批量下载进度", total=len(urls))
            
            for i, url in enumerate(urls):
                progress.update(task, description=f"[cyan]下载第 {i+1}/{len(urls)} 个视频")
                result = self.download_single_video(url, f"video_{i+1}")
                if result:
                    results.append(result)
                progress.advance(task)
        
        self.console.print(f"[green]✅ 批量下载完成，成功下载 {len(results)}/{len(urls)} 个视频[/]")
        return results
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """
        仅获取视频信息，不下载
        :param url: 视频链接
        :return: 视频信息字典
        """
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'upload_date': info.get('upload_date'),
                    'uploader': info.get('uploader'),
                    'description': info.get('description'),
                    'thumbnail': info.get('thumbnail'),
                    'url': url
                }
        except Exception as e:
            self.console.print(f"[red]❌ 获取视频信息失败: {str(e)}[/]")
            return None