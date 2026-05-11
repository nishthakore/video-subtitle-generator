from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def ensure_ffmpeg_available() -> None:
    ffmpeg_binary = shutil.which("ffmpeg")
    if ffmpeg_binary is None:
        raise RuntimeError(
            "ffmpeg not found. Install ffmpeg and make sure it is available in PATH."
        )


def extract_audio_from_video(video_path: Path, output_audio_path: Path) -> Path:
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(output_audio_path),
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Audio extraction failed: {result.stderr}")

    return output_audio_path


def burn_subtitles_to_video(
    input_video_path: Path,
    subtitle_path: Path,
    output_video_path: Path,
    subtitle_font_size: int = 20,
    subtitle_margin_v: int = 30,
) -> Path:
    output_video_path.parent.mkdir(parents=True, exist_ok=True)

    subtitle_for_ffmpeg = str(subtitle_path).replace("\\", "/").replace(":", "\\:")
    is_ass = subtitle_path.suffix.lower() == ".ass"

    if is_ass:
        # ASS contains style, position, and karaoke timing, so do not override here.
        vf_filter = f"ass='{subtitle_for_ffmpeg}'"
    else:
        subtitle_style = (
            f"FontSize={subtitle_font_size},"
            "PrimaryColour=&HFFFFFF&,"
            "OutlineColour=&H000000&,"
            "BorderStyle=1,"
            "Outline=2,"
            "Shadow=1,"
            "Alignment=2,"
            f"MarginV={subtitle_margin_v}"
        )
        vf_filter = f"subtitles='{subtitle_for_ffmpeg}':force_style='{subtitle_style}'"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_video_path),
        "-map",
        "0:v:0",
        "-map",
        "0:a?",
        "-vf",
        vf_filter,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(output_video_path),
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Subtitle burn-in failed: {result.stderr}")

    return output_video_path
