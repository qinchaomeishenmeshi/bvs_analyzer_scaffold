import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class ReportGenerator:
    """
    报告生成器，负责整合视频分析结果并生成可读性强的报告
    """
    
    def __init__(self, console: Console = None):
        """
        初始化报告生成器
        :param console: Rich Console对象
        """
        self.console = console or Console()
    
    def generate_markdown_report(self, video_info: Dict, transcription_data: Dict, 
                               output_path: str = None) -> str:
        """
        生成 Markdown 格式的分析报告
        :param video_info: 视频基本信息
        :param transcription_data: 转写数据
        :param output_path: 报告保存路径
        :return: 报告文件路径
        """
        try:
            # 生成报告内容
            report_content = self._build_markdown_content(video_info, transcription_data)
            
            # 确定输出路径
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"video_analysis_report_{timestamp}.md"
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存报告
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.console.print(f"[green]📊 Markdown报告已生成: {output_path.name}[/]")
            return str(output_path)
            
        except Exception as e:
            self.console.print(f"[red]❌ 报告生成失败: {str(e)}[/]")
            raise e
    
    def _build_markdown_content(self, video_info: Dict, transcription_data: Dict) -> str:
        """
        构建 Markdown 报告内容
        """
        # 获取基本信息
        title = video_info.get('title', '未知标题')
        uploader = video_info.get('uploader', '未知作者')
        duration = video_info.get('duration', 0)
        view_count = video_info.get('view_count', 'N/A')
        like_count = video_info.get('like_count', 'N/A')
        upload_date = video_info.get('upload_date', 'N/A')
        
        # 转写信息
        full_text = transcription_data.get('text', '')
        segments = transcription_data.get('segments', [])
        language = transcription_data.get('language', 'unknown')
        
        # 分析开头钩子（前3秒内容）
        hook_content = self._extract_hook_content(segments)
        
        # 构建报告
        report = f"""# 视频分析报告

## 📹 基本信息

| 项目 | 内容 |
|------|------|
| **标题** | {title} |
| **作者** | {uploader} |
| **时长** | {self._format_duration(duration)} |
| **观看数** | {self._format_number(view_count)} |
| **点赞数** | {self._format_number(like_count)} |
| **发布日期** | {upload_date} |
| **识别语言** | {language} |
| **字幕片段数** | {len(segments)} |

## 🎯 开头钩子分析（前3秒）

{hook_content}

## 📝 完整转写文本

{full_text}

## ⏱️ 分段字幕

{self._build_segments_section(segments)}

## 📊 内容结构分析

{self._analyze_content_structure(segments)}

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def _extract_hook_content(self, segments: List[Dict]) -> str:
        """
        提取开头3秒的钩子内容
        """
        hook_segments = [seg for seg in segments if seg['start'] <= 3.0]
        
        if not hook_segments:
            return "⚠️ 未检测到开头3秒内的内容"
        
        hook_text = " ".join([seg['text'] for seg in hook_segments])
        
        # 简单的钩子类型判断
        hook_type = "未知类型"
        if any(char in hook_text for char in ['？', '?']):
            hook_type = "疑问式钩子"
        elif any(word in hook_text for word in ['但是', '然而', '不过', '其实']):
            hook_type = "反转式钩子"
        elif any(word in hook_text for word in ['秘密', '方法', '技巧', '绝招']):
            hook_type = "干货式钩子"
        elif any(word in hook_text for word in ['震惊', '惊人', '不敢相信', '太厉害']):
            hook_type = "震惊式钩子"
        
        return f"""**钩子类型**: {hook_type}

**钩子内容**: {hook_text}

**时长**: {hook_segments[-1]['end']:.1f}秒"""
    
    def _build_segments_section(self, segments: List[Dict]) -> str:
        """
        构建分段字幕部分
        """
        if not segments:
            return "暂无字幕数据"
        
        segments_md = ""
        for i, segment in enumerate(segments, 1):
            start_time = self._format_time(segment['start'])
            end_time = self._format_time(segment['end'])
            text = segment['text']
            
            segments_md += f"**{i}.** `{start_time} - {end_time}` {text}\n\n"
        
        return segments_md
    
    def _analyze_content_structure(self, segments: List[Dict]) -> str:
        """
        分析内容结构
        """
        if not segments:
            return "暂无数据进行结构分析"
        
        total_duration = segments[-1]['end'] if segments else 0
        total_words = sum(len(seg['text']) for seg in segments)
        avg_segment_length = total_words / len(segments) if segments else 0
        
        # 计算语速（字/分钟）
        speech_rate = (total_words / total_duration * 60) if total_duration > 0 else 0
        
        # 分析节奏变化（基于片段长度变化）
        segment_lengths = [len(seg['text']) for seg in segments]
        rhythm_analysis = "节奏平稳" if len(set(segment_lengths)) < len(segment_lengths) * 0.3 else "节奏多变"
        
        return f"""### 基础数据
- **总时长**: {self._format_duration(total_duration)}
- **总字数**: {total_words} 字
- **平均语速**: {speech_rate:.1f} 字/分钟
- **平均片段长度**: {avg_segment_length:.1f} 字
- **节奏特点**: {rhythm_analysis}

### 结构建议
- 开头钩子时长适中，能够快速抓住观众注意力
- 内容节奏{rhythm_analysis.lower()}，适合目标受众
- 语速适中，便于观众理解和跟随"""
    
    def _format_duration(self, seconds: float) -> str:
        """
        格式化时长显示
        """
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}分{secs}秒"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}小时{minutes}分钟"
    
    def _format_time(self, seconds: float) -> str:
        """
        格式化时间戳显示
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def _format_number(self, number) -> str:
        """
        格式化数字显示
        """
        if isinstance(number, (int, float)):
            if number >= 10000:
                return f"{number/10000:.1f}万"
            else:
                return str(number)
        return str(number)
    
    def generate_json_report(self, video_info: Dict, transcription_data: Dict, 
                           output_path: str = None) -> str:
        """
        生成 JSON 格式的结构化报告
        :param video_info: 视频基本信息
        :param transcription_data: 转写数据
        :param output_path: 报告保存路径
        :return: 报告文件路径
        """
        try:
            # 构建结构化数据
            report_data = {
                'basic_info': video_info,
                'transcription': transcription_data,
                'analysis': {
                    'hook_analysis': self._analyze_hook(transcription_data.get('segments', [])),
                    'structure_analysis': self._get_structure_data(transcription_data.get('segments', [])),
                    'generated_at': datetime.now().isoformat()
                }
            }
            
            # 确定输出路径
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"video_analysis_data_{timestamp}.json"
            
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存报告
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            self.console.print(f"[green]📊 JSON报告已生成: {output_path.name}[/]")
            return str(output_path)
            
        except Exception as e:
            self.console.print(f"[red]❌ JSON报告生成失败: {str(e)}[/]")
            raise e
    
    def _analyze_hook(self, segments: List[Dict]) -> Dict:
        """
        分析开头钩子的结构化数据
        """
        hook_segments = [seg for seg in segments if seg['start'] <= 3.0]
        
        if not hook_segments:
            return {'type': 'none', 'content': '', 'duration': 0}
        
        hook_text = " ".join([seg['text'] for seg in hook_segments])
        hook_duration = hook_segments[-1]['end']
        
        # 钩子类型判断
        hook_type = 'unknown'
        if any(char in hook_text for char in ['？', '?']):
            hook_type = 'question'
        elif any(word in hook_text for word in ['但是', '然而', '不过', '其实']):
            hook_type = 'reversal'
        elif any(word in hook_text for word in ['秘密', '方法', '技巧', '绝招']):
            hook_type = 'value'
        elif any(word in hook_text for word in ['震惊', '惊人', '不敢相信', '太厉害']):
            hook_type = 'shock'
        
        return {
            'type': hook_type,
            'content': hook_text,
            'duration': hook_duration,
            'segments': hook_segments
        }
    
    def _get_structure_data(self, segments: List[Dict]) -> Dict:
        """
        获取内容结构的数据分析
        """
        if not segments:
            return {}
        
        total_duration = segments[-1]['end']
        total_words = sum(len(seg['text']) for seg in segments)
        speech_rate = (total_words / total_duration * 60) if total_duration > 0 else 0
        
        return {
            'total_duration': total_duration,
            'total_words': total_words,
            'speech_rate': speech_rate,
            'segment_count': len(segments),
            'avg_segment_length': total_words / len(segments) if segments else 0
        }
    
    def display_summary(self, video_info: Dict, transcription_data: Dict):
        """
        在控制台显示分析摘要
        """
        # 创建基本信息表格
        info_table = Table(title="📹 视频基本信息")
        info_table.add_column("项目", style="cyan")
        info_table.add_column("内容", style="white")
        
        info_table.add_row("标题", video_info.get('title', 'N/A'))
        info_table.add_row("作者", video_info.get('uploader', 'N/A'))
        info_table.add_row("时长", self._format_duration(video_info.get('duration', 0)))
        info_table.add_row("观看数", self._format_number(video_info.get('view_count', 'N/A')))
        info_table.add_row("点赞数", self._format_number(video_info.get('like_count', 'N/A')))
        
        self.console.print(info_table)
        
        # 显示钩子分析
        segments = transcription_data.get('segments', [])
        hook_analysis = self._analyze_hook(segments)
        
        hook_panel = Panel(
            f"**类型**: {hook_analysis['type']}\n**内容**: {hook_analysis['content'][:100]}...\n**时长**: {hook_analysis['duration']:.1f}秒",
            title="🎯 开头钩子分析",
            border_style="green"
        )
        self.console.print(hook_panel)