# 批量媒体转动图与实况照片工具 / Batch Media to GIF & Live Photo Exporter

一个面向短视频内容运营的小工具：把一批视频或图片放进 `input/`，一次性批量导出 GIF 动图；也可以把短视频批量转换成 iPhone Live Photo（实况照片）文件。

这个项目来自真实内容生产需求：当抖音、小红书等平台流行动图/实况素材时，如果每条素材都手动用剪映或其他工具转换，会非常浪费时间。这个脚本把重复步骤变成一次命令，适合几十个、上百个素材的批量处理。

English README: [README.en.md](README.en.md)

## 功能

- 批量扫描输入目录中的视频和图片。
- 视频转 GIF：使用 `ffmpeg` 生成调色板，输出质量更稳定。
- 图片转 GIF：把静态图片批量导出为 GIF 文件。
- 短视频转 iPhone Live Photo：支持 `.pvt` 包或照片 + 视频文件对。
- 支持设置 GIF 帧率、宽度、静态图时长。
- 支持选择 Live Photo 关键帧：开头、中间、结尾。

## 适合场景

- AI 生成视频/图片素材批量转动图。
- 短视频运营素材批量处理。
- 抖音、小红书、公众号等内容资产整理。
- 把重复的剪辑软件导出步骤自动化。
- 需要把短视频批量转成 iPhone Live Photo 的素材工作流。

## 环境要求

- macOS
- Python 3.11+
- GIF 模式需要 `ffmpeg`
- Live Photo 模式需要 `makelive` 和 PyObjC

安装 `ffmpeg`：

```sh
brew install ffmpeg
```

安装 Python 依赖：

```sh
python3.11 -m pip install -r requirements.txt
```

## 使用方法

把素材放进 `input/` 目录，然后运行：

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f gif
```

常用 GIF 参数：

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f gif --gif-fps 12 --gif-width 540
```

静态图片转 GIF 时设置显示时长：

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f gif --still-duration 2
```

导出 iPhone Live Photo 的 `.pvt` 包：

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f pvt --frame middle
```

导出照片 + 视频文件对：

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f pair --frame first
```

## 支持格式

视频输入：

```text
.mp4, .mov, .m4v, .avi, .mkv, .webm, .3gp, .flv
```

图片输入：

```text
.jpg, .jpeg, .png, .webp, .bmp, .tif, .tiff
```

## 输出说明

- `gif`：输出 `.gif` 动图。
- `pvt`：输出 `.pvt` 包，适合通过 AirDrop 发送到 iPhone。
- `pair`：输出照片 + 视频文件对，可导入 macOS 照片 App。

## 安全说明

这个仓库不会包含本地输入素材、输出素材、账号、密钥或用户数据。`input/` 和 `output/` 只保留空目录占位文件。

更多说明见 [SECURITY.md](SECURITY.md)。

## 作品亮点

- 真实业务场景：解决内容运营中高频、重复、低价值的素材转换工作。
- 自动化思路清晰：把“一个个手动转”的动作变成批量命令。
- 技术组合务实：`ffmpeg` 负责 GIF 质量，macOS AVFoundation 负责 Live Photo 工作流。
- 可扩展：后续可以加入批量压缩、尺寸模板、水印、封面帧选择和 GUI 界面。
