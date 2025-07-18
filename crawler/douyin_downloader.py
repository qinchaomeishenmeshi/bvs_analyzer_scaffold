import time
from pathlib import Path
from typing import List, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.console import Console
from rich.panel import Panel
from rich.progress import (Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn)
from rich.text import Text


class DouyinDownloader:
    def __init__(self, console: Console, progress_bar: bool = True, thread: int = 5, 
                 video: bool = True, music: bool = False, cover: bool = False, 
                 avatar: bool = False, json_data: bool = False, 
                 callback: Callable = None):
        """
        初始化抖音下载器
        :param console: Rich Console对象
        :param progress_bar: 是否显示进度条
        :param thread: 下载线程数
        :param video: 是否下载视频
        :param music: 是否下载音频
        :param cover: 是否下载封面
        :param avatar: 是否下载头像
        :param json_data: 是否保存json数据
        :param callback: 下载进度回调函数
        """
        self.console = console
        self.progress_bar = progress_bar
        self.thread = thread
        self.video = video
        self.music = music
        self.cover = cover
        self.avatar = avatar
        self.json_data = json_data
        self.callback = callback

    def awemeDownload(self, aweme: dict, save_path: Path, progress: Progress):
        """
        单个作品下载的占位符方法。
        实际的下载逻辑将在这里实现。
        """
        # 假设下载需要一些时间
        time.sleep(1)
        progress.print(f"[green]✅ 模拟下载成功: {aweme.get('desc', '未知作品')[:30]}[/]")
        return True

    def download(self, awemeList: List[dict], savePath: Path):
        if not awemeList:
            self.console.print("[yellow]⚠️  没有找到可下载的内容[/]")
            return

        save_path = Path(savePath)
        save_path.mkdir(parents=True, exist_ok=True)

        start_time = time.time()
        total_count = len(awemeList)
        success_count = 0

        if self.progress_bar:
            self.console.print(Panel(
                Text.assemble(
                    ("下载配置\n", "bold cyan"),
                    (f"总数: {total_count} 个作品\n", "cyan"),
                    (f"线程: {self.thread}\n", "cyan"),
                    (f"保存路径: {save_path}\n", "cyan"),
                    (f"下载项: {'视频 ' if self.video else ''}{'音频 ' if self.music else ''}{'封面 ' if self.cover else ''}{'头像 ' if self.avatar else ''}{'JSON ' if self.json_data else ''}", "cyan")
                ),
                title="抖音下载器",
                border_style="cyan"
            ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console,
            transient=False  # 设置为False，以便在下载完成时仍可见
        ) as progress:
            main_task = progress.add_task("[cyan]📥 批量下载进度", total=total_count)

            with ThreadPoolExecutor(max_workers=self.thread) as executor:
                future_to_aweme = {executor.submit(self.awemeDownload, aweme, save_path, progress): aweme for aweme in awemeList}

                downloaded_count = 0
                for future in as_completed(future_to_aweme):
                    downloaded_count += 1
                    aweme = future_to_aweme[future]
                    aweme_desc = aweme.get('desc', '未知作品')[:30]
                    try:
                        future.result()
                        success_count += 1
                        # progress.print(f"[green]✅ 下载成功: {aweme_desc}[/]")
                    except Exception as exc:
                        progress.print(f"[red]❌ 下载失败: {aweme_desc} - {exc}[/]")

                    # 调用回调函数更新外部进度
                    if self.callback:
                        self.callback(downloaded_count, total_count)

                    progress.update(main_task, advance=1)

        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        self.console.print(Panel(
            Text.assemble(
                ("下载完成\n", "bold green"),
                (f"成功: {success_count}/{total_count}\n", "green"),
                (f"用时: {minutes}分{seconds}秒\n", "green"),
                (f"保存位置: {save_path}\n", "green"),
            ),
            title="下载统计",
            border_style="green"
        ))

        return success_count