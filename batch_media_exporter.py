#!/usr/bin/env -S python3.11
"""Batch export short-form media to GIF or iPhone Live Photo files.

GIF export uses ffmpeg. Live Photo export uses macOS AVFoundation + makelive.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from AVFoundation import (
    AVAsset,
    AVAssetExportPresetPassthrough,
    AVAssetExportSession,
    AVAssetImageGenerator,
    AVAssetImageGeneratorApertureModeCleanAperture,
    AVFileTypeQuickTimeMovie,
    CMTimeMake,
)
from Foundation import NSURL
from Quartz import (
    CGImageDestinationCreateWithURL,
    CGImageDestinationAddImage,
    CGImageDestinationFinalize,
    kCGImageDestinationLossyCompressionQuality,
)
from CoreServices import kUTTypeJPEG


VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp", ".flv"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
MEDIA_EXTENSIONS = VIDEO_EXTENSIONS | IMAGE_EXTENSIONS


def check_makelive():
    try:
        import makelive
        return makelive
    except ImportError:
        print("错误: 未找到 makelive。请安装:")
        print("  pip3 install makelive")
        sys.exit(1)


def check_ffmpeg():
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        print("错误: 未找到 ffmpeg。GIF 模式需要先安装:")
        print("  brew install ffmpeg")
        sys.exit(1)
    return ffmpeg


def get_video_duration(video_path):
    """使用 AVFoundation 获取视频时长（秒）."""
    url = NSURL.fileURLWithPath_(str(video_path))
    asset = AVAsset.assetWithURL_(url)
    cm_duration = asset.duration()
    ts = cm_duration.timescale
    val = cm_duration.value
    if ts != 0:
        return float(val) / float(ts)
    return 0.0


def extract_frame(video_path, output_path, time_pos=0.0):
    """使用 AVAssetImageGenerator 从视频提取一帧为 JPEG."""
    url = NSURL.fileURLWithPath_(str(video_path))
    asset = AVAsset.assetWithURL_(url)
    generator = AVAssetImageGenerator.assetImageGeneratorWithAsset_(asset)
    generator.setApertureMode_(AVAssetImageGeneratorApertureModeCleanAperture)
    generator.setAppliesPreferredTrackTransform_(True)

    duration = get_video_duration(video_path)
    if time_pos < 0:
        time_pos = 0
    if time_pos > duration and duration > 0:
        time_pos = duration * 0.5

    cm_time = CMTimeMake(int(time_pos * 600), 600)
    cg_image, error = generator.copyCGImageAtTime_actualTime_error_(
        cm_time, None, None
    )

    if error or cg_image is None:
        raise RuntimeError(f"无法从视频提取帧: {error}")

    dest_url = NSURL.fileURLWithPath_(str(output_path))
    dest = CGImageDestinationCreateWithURL(dest_url, kUTTypeJPEG, 1, None)
    if dest is None:
        raise RuntimeError("无法创建 JPEG 输出文件")

    options = {kCGImageDestinationLossyCompressionQuality: 1.0}
    CGImageDestinationAddImage(dest, cg_image, options)
    if not CGImageDestinationFinalize(dest):
        raise RuntimeError("写入 JPEG 文件失败")

    return output_path


def scan_files(input_dir, extensions):
    """扫描输入目录中的所有支持文件."""
    files = []
    for entry in sorted(Path(input_dir).iterdir()):
        if entry.is_file() and entry.suffix.lower() in extensions:
            files.append(entry)
    return files


def run_command(args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "命令执行失败")
    return result


def convert_mp4_to_mov(mp4_path, output_path):
    """使用 AVAssetExportSession 将 mp4 无损重封装为 mov."""
    input_url = NSURL.fileURLWithPath_(str(mp4_path))
    output_url = NSURL.fileURLWithPath_(str(output_path))
    asset = AVAsset.assetWithURL_(input_url)
    export = AVAssetExportSession.alloc().initWithAsset_presetName_(
        asset, AVAssetExportPresetPassthrough
    )
    export.setOutputFileType_(AVFileTypeQuickTimeMovie)
    export.setOutputURL_(output_url)
    export.exportAsynchronouslyWithCompletionHandler_(lambda: None)
    while export.status() == 2:  # AVAssetExportSessionStatusExporting
        import time
        time.sleep(0.05)
    if export.status() != 3:  # AVAssetExportSessionStatusCompleted
        raise RuntimeError(f"mp4→mov 转换失败: {export.error()}")
    return output_path


def process_video(makelive, video_path, output_dir, output_format, frame_pos):
    """处理单个视频，转换为 Live Photo."""
    video_name = video_path.stem
    print(f"  处理: {video_path.name}")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 步骤1: 提取关键帧
        photo_path = tmpdir / f"{video_name}.jpg"
        duration = get_video_duration(video_path)

        if frame_pos == "middle":
            time_pos = duration / 2.0
        elif frame_pos == "end":
            time_pos = max(0, duration - 0.5)
        else:
            time_pos = 0.0

        extract_frame(video_path, photo_path, time_pos)
        print(f"     关键帧: {time_pos:.1f}s / {duration:.1f}s")

        # 步骤1.5: mp4 无损转为 mov，避免 makelive 导出时容器格式混乱
        if video_path.suffix.lower() == ".mp4":
            mov_video = tmpdir / f"{video_name}.mov"
            convert_mp4_to_mov(video_path, mov_video)
            video_for_live = mov_video
        else:
            video_for_live = video_path

        # 步骤2: 使用 makelive 创建 Live Photo
        if output_format == "pvt":
            asset_id, pvt_path = makelive.save_live_photo_pair_as_pvt(
                str(photo_path), str(video_for_live)
            )
            dest = Path(output_dir) / f"{video_name}.pvt"
            if dest.exists():
                shutil.rmtree(dest)
            shutil.move(pvt_path, dest)
            print(f"    -> {dest.name}")

        elif output_format == "pair":
            tmp_photo = tmpdir / f"{video_name}_live.jpg"
            shutil.copy2(photo_path, tmp_photo)

            tmp_video = tmpdir / f"{video_name}_live.mov"
            shutil.copy2(video_for_live, tmp_video)

            asset_id = makelive.make_live_photo(str(tmp_photo), str(tmp_video))

            # 移动到输出目录（makelive 可能将照片转为 heic）
            for f in tmpdir.iterdir():
                if f.name.startswith(video_name + "_live"):
                    ext = f.suffix
                    if ext in (".heic", ".jpg", ".jpeg"):
                        dest = Path(output_dir) / f"{video_name}.heic"
                    elif ext in (".mov", ".mp4", ".m4v"):
                        dest = Path(output_dir) / f"{video_name}{ext}"
                    else:
                        continue
                    shutil.move(str(f), dest)
                    print(f"    -> {dest.name}")

    return True


def process_gif(ffmpeg, media_path, output_dir, fps, width, still_duration):
    """Convert a video or still image into a GIF."""
    output_path = Path(output_dir) / f"{media_path.stem}.gif"
    print(f"  处理: {media_path.name}")

    vf = f"scale={width}:-1:flags=lanczos"

    if media_path.suffix.lower() in VIDEO_EXTENSIONS:
        with tempfile.TemporaryDirectory() as tmpdir:
            palette = Path(tmpdir) / "palette.png"
            palette_filter = f"fps={fps},{vf},palettegen"
            gif_filter = f"fps={fps},{vf}[x];[x][1:v]paletteuse"

            run_command([
                ffmpeg, "-y", "-i", str(media_path),
                "-vf", palette_filter,
                str(palette),
            ])
            run_command([
                ffmpeg, "-y", "-i", str(media_path), "-i", str(palette),
                "-filter_complex", gif_filter,
                "-loop", "0",
                str(output_path),
            ])
    else:
        run_command([
            ffmpeg, "-y", "-loop", "1", "-t", str(still_duration),
            "-i", str(media_path),
            "-vf", vf,
            "-loop", "0",
            str(output_path),
        ])

    print(f"    -> {output_path.name}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="批量将短视频/图片转换为 GIF，或将短视频转换为 iPhone Live Photo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3.11 batch_media_exporter.py ./input -o ./output -f gif
  python3.11 batch_media_exporter.py ./videos -o ./out -f pvt
  python3.11 batch_media_exporter.py ./videos -o ./out -f pair --frame middle
        """
    )
    parser.add_argument(
        "input_dir", nargs="?", default="input",
        help="输入目录（包含短视频），默认为 ./input"
    )
    parser.add_argument(
        "-o", "--output", default="output",
        help="输出目录，默认为 ./output"
    )
    parser.add_argument(
        "-f", "--format", choices=["gif", "pvt", "pair"], default="gif",
        help="输出格式: gif、pvt (AirDrop 友好) 或 pair (照片+视频文件对)"
    )
    parser.add_argument(
        "--frame", choices=["first", "middle", "end"], default="first",
        help="Live Photo 关键帧位置: first(开头), middle(中间), end(结尾)"
    )
    parser.add_argument(
        "--gif-fps", type=int, default=12,
        help="GIF 帧率，默认 12"
    )
    parser.add_argument(
        "--gif-width", type=int, default=540,
        help="GIF 宽度，默认 540px，高度按比例缩放"
    )
    parser.add_argument(
        "--still-duration", type=float, default=2.0,
        help="静态图片转 GIF 时的时长，默认 2 秒"
    )

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"错误: 输入路径不是目录: {input_dir}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    if args.format == "gif":
        ffmpeg = check_ffmpeg()
        media_files = scan_files(input_dir, MEDIA_EXTENSIONS)
        supported = MEDIA_EXTENSIONS
    else:
        makelive = check_makelive()
        media_files = scan_files(input_dir, VIDEO_EXTENSIONS)
        supported = VIDEO_EXTENSIONS

    if not media_files:
        print(f"在 {input_dir} 中未找到任何支持文件")
        print(f"支持的格式: {', '.join(sorted(supported))}")
        sys.exit(0)

    print(f"找到 {len(media_files)} 个文件")
    if args.format == "gif":
        print("输出格式: GIF 动图")
        print(f"GIF 参数: {args.gif_fps} fps, 宽度 {args.gif_width}px")
    else:
        print(f"输出格式: {'PVT 包' if args.format == 'pvt' else '照片+视频文件对'}")
        print(f"关键帧位置: {args.frame}")
    print()

    success = 0
    for i, media_file in enumerate(media_files, 1):
        print(f"[{i}/{len(media_files)}]", end=" ")
        try:
            if args.format == "gif":
                process_gif(
                    ffmpeg,
                    media_file,
                    output_dir,
                    args.gif_fps,
                    args.gif_width,
                    args.still_duration,
                )
            else:
                process_video(makelive, media_file, output_dir, args.format, args.frame)
            success += 1
        except Exception as e:
            print(f"   错误: {e}")

    print()
    print(f"完成! {success}/{len(media_files)} 个文件成功转换")
    print(f"输出目录: {output_dir}")

    if args.format == "pvt" and success > 0:
        print()
        print("提示: .pvt 文件可通过 AirDrop 发送到 iPhone，会自动出现在照片 App 中")

    if args.format == "pair" and success > 0:
        print()
        print("提示: 将输出文件对导入到 macOS 照片 App 即可识别为 Live Photo")


if __name__ == "__main__":
    main()
