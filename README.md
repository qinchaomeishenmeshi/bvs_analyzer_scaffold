# BVS Analyzer - 视频结构分析工具

一个强大的视频内容分析工具，专门用于分析视频的结构、提取文本内容并生成详细的分析报告。

## 🚀 功能特性

- **视频下载**: 支持多平台视频下载（YouTube、B站等）
- **音频转写**: 使用 OpenAI Whisper 进行高精度语音转文字
- **结构分析**: 分析视频开头钩子、内容节奏、语速等关键指标
- **报告生成**: 生成 Markdown 和 JSON 格式的详细分析报告
- **批量处理**: 支持批量分析多个视频
- **进度显示**: 美观的进度条和状态显示

## 📦 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 FFmpeg（必需）
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Windows
# 下载 FFmpeg 并添加到 PATH
```

## 🎯 快速开始

### 分析单个视频

```bash
# 完整分析（下载视频 + 转写 + 报告）
python main.py -u "https://www.youtube.com/watch?v=VIDEO_ID"

# 仅转写分析，不下载视频
python main.py -u "https://www.youtube.com/watch?v=VIDEO_ID" --no-download

# 指定输出目录
python main.py -u "https://www.youtube.com/watch?v=VIDEO_ID" -o my_analysis
```

### 批量分析视频

```bash
# 从文件读取URL列表
python main.py -f video_urls.txt

# 直接指定多个URL
python main.py -u "URL1" "URL2" "URL3"
```

### 创建URL文件

创建一个 `video_urls.txt` 文件，每行一个视频URL：

```
https://www.youtube.com/watch?v=VIDEO_ID1
https://www.youtube.com/watch?v=VIDEO_ID2
https://www.bilibili.com/video/BV1234567890
```

## 📁 项目结构

```
bvs_analyzer_scaffold/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖包列表
├── README.md              # 项目说明
├── crawler/               # 视频爬取模块
│   ├── __init__.py
│   ├── video_downloader.py    # 视频下载器
│   └── douyin_downloader.py   # 抖音下载器
├── parser/                # 内容解析模块
│   ├── __init__.py
│   └── audio_parser.py        # 音频转写器
├── report/                # 报告生成模块
│   ├── __init__.py
│   └── report_generator.py    # 报告生成器
├── docs/                  # 文档目录
│   ├── PRD.md                # 产品需求文档
│   └── task.md               # 任务规划文档
└── output/                # 输出目录（自动创建）
    ├── videos/               # 下载的视频文件
    ├── audio/                # 提取的音频文件
    ├── transcripts/          # 转写文本文件
    └── reports/              # 分析报告
```

## 📊 输出文件说明

### 转写文件
- `{video_id}_transcript.json`: 完整的转写数据（包含时间戳）
- `{video_id}_transcript.srt`: SRT字幕文件

### 分析报告
- `{video_id}_report.md`: Markdown格式的可读性报告
- `{video_id}_data.json`: 结构化的分析数据

### 报告内容包括
- 📹 **基本信息**: 标题、作者、时长、观看数等
- 🎯 **开头钩子分析**: 前3秒内容的钩子类型和效果
- 📝 **完整转写文本**: 视频的完整文字内容
- ⏱️ **分段字幕**: 带时间戳的分段内容
- 📊 **结构分析**: 语速、节奏、内容密度等指标

## 🛠️ 高级用法

### 使用 Python API

```python
from main import BVSAnalyzer

# 创建分析器
analyzer = BVSAnalyzer(output_dir="my_output")

# 分析单个视频
result = analyzer.analyze_single_video(
    url="https://www.youtube.com/watch?v=VIDEO_ID",
    download_video=True,
    generate_report=True
)

# 检查结果
if result['success']:
    print(f"分析完成！报告路径: {result['report_paths']}")
else:
    print(f"分析失败: {result['error']}")
```

### 自定义配置

```python
# 配置视频下载器
analyzer.downloader.configure_options(
    output_path="custom_videos",
    format_selector="best[height<=480]",  # 下载480p视频
    save_metadata=True
)

# 配置音频解析器
analyzer.parser.configure(
    audio_output_dir="custom_audio",
    transcript_output_dir="custom_transcripts",
    model_size="medium"  # 使用中等大小的Whisper模型
)
```

## 🔧 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `-u, --urls` | 视频URL（可多个） | `-u "URL1" "URL2"` |
| `-f, --file` | URL文件路径 | `-f urls.txt` |
| `-o, --output` | 输出目录 | `-o my_output` |
| `--no-download` | 不下载视频文件 | `--no-download` |
| `--no-report` | 不生成分析报告 | `--no-report` |

## 🎨 输出示例

### 控制台输出
```
🎬 开始分析视频: https://www.youtube.com/watch?v=example
✅ 视频信息获取完成
🎵 正在下载视频...
✅ 视频下载完成: example_video.mp4
🎤 正在提取音频...
✅ 音频提取完成: example_audio.wav
🔤 正在转写音频...
✅ 音频转写完成
📊 正在生成报告...
✅ Markdown报告已生成: example_report.md
✅ JSON报告已生成: example_data.json
🎉 视频分析完成！
```

### Markdown 报告示例
```markdown
# 视频分析报告

## 📹 基本信息

| 项目 | 内容 |
|------|------|
| **标题** | 如何制作吸引人的视频开头 |
| **作者** | 创作者名称 |
| **时长** | 5分30秒 |
| **观看数** | 12.5万 |

## 🎯 开头钩子分析（前3秒）

**钩子类型**: 疑问式钩子
**钩子内容**: 你知道什么样的开头能让观众看完整个视频吗？
**时长**: 2.8秒

## 📊 内容结构分析

- **总时长**: 5分30秒
- **总字数**: 1,245 字
- **平均语速**: 226.4 字/分钟
- **节奏特点**: 节奏多变
```

## 🚨 注意事项

1. **网络要求**: 需要稳定的网络连接下载视频和模型
2. **存储空间**: 确保有足够的磁盘空间存储视频和音频文件
3. **处理时间**: 转写时间取决于视频长度和硬件性能
4. **版权合规**: 请确保分析的视频内容符合相关法律法规

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证。