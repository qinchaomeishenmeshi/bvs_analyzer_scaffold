import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import whisper
import ffmpeg
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


class AudioParser:
    """
    音频解析器，负责从视频中提取音频并进行语音转写
    """
    
    def __init__(self, console: Console = None, model_size: str = "base"):
        """
        初始化音频解析器
        :param console: Rich Console对象
        :param model_size: Whisper模型大小 (tiny, base, small, medium, large)
        """
        self.console = console or Console()
        self.model_size = model_size
        self.model = None
        self.audio_output_dir = None
        self.transcript_output_dir = None
        self._load_whisper_model()
    
    def configure(self, audio_output_dir: str = None, transcript_output_dir: str = None):
        """
        配置输出目录
        :param audio_output_dir: 音频输出目录
        :param transcript_output_dir: 转写文本输出目录
        """
        if audio_output_dir:
            self.audio_output_dir = Path(audio_output_dir)
            self.audio_output_dir.mkdir(parents=True, exist_ok=True)
        
        if transcript_output_dir:
            self.transcript_output_dir = Path(transcript_output_dir)
            self.transcript_output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_whisper_model(self):
        """
        加载 Whisper 模型
        """
        try:
            self.console.print(f"[cyan]🤖 正在加载 Whisper {self.model_size} 模型...[/]")
            self.model = whisper.load_model(self.model_size)
            self.console.print(f"[green]✅ Whisper 模型加载成功[/]")
        except Exception as e:
            self.console.print(f"[red]❌ Whisper 模型加载失败: {str(e)}[/]")
            raise e
    
    def extract_audio_from_video(self, video_path: str, audio_path: str = None) -> str:
        """
        从视频文件中提取音频
        :param video_path: 视频文件路径
        :param audio_path: 音频输出路径，如果为None则自动生成
        :return: 音频文件路径
        """
        video_path = Path(video_path)
        
        if audio_path is None:
            audio_path = video_path.parent / f"{video_path.stem}_audio.wav"
        else:
            audio_path = Path(audio_path)
        
        try:
            self.console.print(f"[cyan]🎵 正在提取音频: {video_path.name}[/]")
            
            # 使用 ffmpeg 提取音频
            (
                ffmpeg
                .input(str(video_path))
                .output(str(audio_path), acodec='pcm_s16le', ac=1, ar='16000')
                .overwrite_output()
                .run(quiet=True)
            )
            
            self.console.print(f"[green]✅ 音频提取完成: {audio_path.name}[/]")
            return str(audio_path)
            
        except Exception as e:
            self.console.print(f"[red]❌ 音频提取失败: {str(e)}[/]")
            raise e
    
    def transcribe_audio(self, audio_path: str, language: str = "zh") -> Dict:
        """
        使用 Whisper 转写音频为文本
        :param audio_path: 音频文件路径
        :param language: 语言代码 (zh, en, etc.)
        :return: 转写结果字典
        """
        try:
            self.console.print(f"[cyan]📝 正在转写音频: {Path(audio_path).name}[/]")
            
            # 使用 Whisper 进行转写
            result = self.model.transcribe(
                audio_path,
                language=language,
                word_timestamps=True,
                verbose=False
            )
            
            # 处理转写结果
            segments = []
            for segment in result['segments']:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'words': segment.get('words', [])
                })
            
            transcription_result = {
                'text': result['text'].strip(),
                'language': result['language'],
                'segments': segments,
                'duration': segments[-1]['end'] if segments else 0
            }
            
            self.console.print(f"[green]✅ 音频转写完成，共 {len(segments)} 个片段[/]")
            return transcription_result
            
        except Exception as e:
            self.console.print(f"[red]❌ 音频转写失败: {str(e)}[/]")
            raise e
    
    def process_video(self, video_path: str, output_dir: str = None) -> Dict:
        """
        处理视频文件：提取音频 + 转写文本
        :param video_path: 视频文件路径
        :param output_dir: 输出目录，如果为None则使用视频所在目录
        :return: 完整的处理结果
        """
        video_path = Path(video_path)
        
        if output_dir is None:
            output_dir = video_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. 提取音频
            audio_path = output_dir / f"{video_path.stem}_audio.wav"
            self.extract_audio_from_video(str(video_path), str(audio_path))
            
            # 2. 转写音频
            transcription = self.transcribe_audio(str(audio_path))
            
            # 3. 保存转写结果
            transcript_path = output_dir / f"{video_path.stem}_transcript.json"
            with open(transcript_path, 'w', encoding='utf-8') as f:
                json.dump(transcription, f, ensure_ascii=False, indent=2)
            
            # 4. 生成 SRT 字幕文件
            srt_path = output_dir / f"{video_path.stem}_subtitles.srt"
            self._save_as_srt(transcription['segments'], str(srt_path))
            
            result = {
                'video_path': str(video_path),
                'audio_path': str(audio_path),
                'transcript_path': str(transcript_path),
                'srt_path': str(srt_path),
                'transcription': transcription
            }
            
            self.console.print(f"[green]🎉 视频处理完成: {video_path.name}[/]")
            return result
            
        except Exception as e:
            self.console.print(f"[red]❌ 视频处理失败: {str(e)}[/]")
            raise e
    
    def _save_as_srt(self, segments: List[Dict], srt_path: str):
        """
        将转写片段保存为 SRT 字幕文件
        :param segments: 转写片段列表
        :param srt_path: SRT文件保存路径
        """
        def format_time(seconds):
            """将秒数转换为 SRT 时间格式"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            millisecs = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
        
        with open(srt_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                start_time = format_time(segment['start'])
                end_time = format_time(segment['end'])
                text = segment['text']
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        self.console.print(f"[green]📄 SRT字幕文件已保存: {Path(srt_path).name}[/]")
    
    def transcribe_from_url(self, url: str, save_audio: bool = True, save_transcript: bool = True) -> Optional[Dict]:
        """
        从URL直接转写音频（使用yt-dlp下载音频）
        :param url: 视频URL
        :param save_audio: 是否保存音频文件
        :param save_transcript: 是否保存转写文件
        :return: 转写结果
        """
        import yt_dlp
        import tempfile
        
        try:
            # 创建临时目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 配置yt-dlp选项，只下载音频
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': str(temp_path / '%(title)s.%(ext)s'),
                    'extractaudio': True,
                    'audioformat': 'wav',
                    'quiet': True,
                    'no_warnings': True
                }
                
                self.console.print(f"[cyan]🎵 正在从URL提取音频...[/]")
                
                # 下载音频
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    # 查找下载的音频文件
                    audio_files = list(temp_path.glob("*"))
                    if not audio_files:
                        raise Exception("未找到下载的音频文件")
                    
                    audio_file = audio_files[0]
                    
                    # 转写音频
                    transcription = self.transcribe_audio(str(audio_file))
                    
                    # 保存文件（如果配置了输出目录）
                    if save_audio and self.audio_output_dir:
                        saved_audio_path = self.audio_output_dir / f"{info.get('id', 'unknown')}_audio.wav"
                        import shutil
                        shutil.copy2(audio_file, saved_audio_path)
                        transcription['audio_path'] = str(saved_audio_path)
                    
                    if save_transcript and self.transcript_output_dir:
                        transcript_path = self.transcript_output_dir / f"{info.get('id', 'unknown')}_transcript.json"
                        with open(transcript_path, 'w', encoding='utf-8') as f:
                            json.dump(transcription, f, ensure_ascii=False, indent=2)
                        transcription['transcript_path'] = str(transcript_path)
                    
                    return transcription
                    
        except Exception as e:
            self.console.print(f"[red]❌ URL音频转写失败: {str(e)}[/]")
            return None
    
    def batch_process_videos(self, video_paths: List[str], output_dir: str = None) -> List[Dict]:
        """
        批量处理多个视频文件
        :param video_paths: 视频文件路径列表
        :param output_dir: 输出目录
        :return: 处理结果列表
        """
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]批量处理视频", total=len(video_paths))
            
            for i, video_path in enumerate(video_paths):
                progress.update(task, description=f"[cyan]处理第 {i+1}/{len(video_paths)} 个视频")
                try:
                    result = self.process_video(video_path, output_dir)
                    results.append(result)
                except Exception as e:
                    self.console.print(f"[red]❌ 处理视频失败 {video_path}: {str(e)}[/]")
                progress.advance(task)
        
        self.console.print(f"[green]✅ 批量处理完成，成功处理 {len(results)}/{len(video_paths)} 个视频[/]")
        return results