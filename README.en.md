# 批量媒体转动图与实况照片工具 / Batch Media to GIF & Live Photo Exporter

A small automation tool for short-form content workflows. Put a batch of videos or images into `input/`, then export them as GIFs in one command. It can also convert short videos into iPhone Live Photo files.

This project comes from a real content operations need: when GIF-like posts, AI-generated videos, and visual assets become popular, converting every file manually in an editing app is slow. This script turns that repetitive workflow into a batch command.

中文 README: [README.md](README.md)

## Features

- Batch scan an input folder for videos and images.
- Convert videos to GIF using `ffmpeg` palette generation.
- Convert still images to GIF files.
- Convert short videos to iPhone Live Photo files.
- Configure GIF FPS, width, and still-image duration.
- Choose the Live Photo key frame from the first, middle, or end frame.

## Use Cases

- Batch converting AI-generated videos or images into GIFs.
- Short-video content operations.
- Douyin, Xiaohongshu, newsletter, and social content asset workflows.
- Replacing repetitive manual exports in editing software.
- Batch exporting short videos into iPhone Live Photo assets.

## Requirements

- macOS
- Python 3.11+
- `ffmpeg` for GIF export
- `makelive` and PyObjC for Live Photo export

Install `ffmpeg`:

```sh
brew install ffmpeg
```

Install Python dependencies:

```sh
python3.11 -m pip install -r requirements.txt
```

## Usage

Put media files into `input/`, then run:

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f gif
```

Common GIF options:

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f gif --gif-fps 12 --gif-width 540
```

Set still-image GIF duration:

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f gif --still-duration 2
```

Export iPhone Live Photo `.pvt` bundles:

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f pvt --frame middle
```

Export photo + video pairs:

```sh
python3.11 batch_media_exporter.py ./input -o ./output -f pair --frame first
```

## Supported Inputs

Video:

```text
.mp4, .mov, .m4v, .avi, .mkv, .webm, .3gp, .flv
```

Image:

```text
.jpg, .jpeg, .png, .webp, .bmp, .tif, .tiff
```

## Outputs

- `gif`: animated `.gif` files.
- `pvt`: `.pvt` Live Photo bundles, useful for AirDrop to iPhone.
- `pair`: photo + video file pairs, suitable for importing into the macOS Photos app.

## Security

This public repository does not include local input media, generated output media, accounts, secrets, or user data. `input/` and `output/` only contain placeholder files.

See [SECURITY.md](SECURITY.md) for details.

## Portfolio Notes

- Real workflow: automates a repetitive content-operations task.
- Practical automation: turns one-by-one manual exports into a batch process.
- Technical stack: Python, ffmpeg, macOS AVFoundation, and PyObjC.
- Extensible: could add compression presets, watermarking, cover-frame selection, and a GUI.
