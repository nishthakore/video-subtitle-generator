from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from faster_whisper import WhisperModel


@dataclass
class SubtitleSegment:
    start: float
    end: float
    text: str
    words: List["WordTiming"]


@dataclass
class WordTiming:
    start: float
    end: float
    word: str


def format_srt_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0

    milliseconds_total = int(round(seconds * 1000))
    hours = milliseconds_total // 3_600_000
    remaining = milliseconds_total % 3_600_000
    minutes = remaining // 60_000
    remaining = remaining % 60_000
    secs = remaining // 1000
    millis = remaining % 1000

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def transcribe_audio_to_segments(
    audio_path: Path,
    model_size: str = "base",
    language: str | None = None,
    task: str = "transcribe",
    device: str = "cpu",
    compute_type: str = "int8",
    beam_size: int = 5,
    best_of: int = 5,
    temperature: float = 0.0,
    initial_prompt: str | None = None,
    hotwords: str | None = None,
) -> List[SubtitleSegment]:
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    segments, _ = model.transcribe(
        str(audio_path),
        language=language,
        task=task,
        vad_filter=True,
        word_timestamps=True,
        beam_size=beam_size,
        best_of=best_of,
        temperature=temperature,
        initial_prompt=initial_prompt,
        hotwords=hotwords,
        condition_on_previous_text=True,
    )

    collected: List[SubtitleSegment] = []
    for segment in segments:
        text = segment.text.strip()
        if not text:
            continue

        words: List[WordTiming] = []
        for word_info in (segment.words or []):
            word_text = (word_info.word or "").strip()
            if not word_text:
                continue

            words.append(
                WordTiming(
                    start=float(word_info.start),
                    end=float(word_info.end),
                    word=word_text,
                )
            )

        collected.append(
            SubtitleSegment(
                start=float(segment.start),
                end=float(segment.end),
                text=text,
                words=words,
            )
        )

    return collected


def write_srt(segments: List[SubtitleSegment], output_srt_path: Path) -> Path:
    output_srt_path.parent.mkdir(parents=True, exist_ok=True)

    with output_srt_path.open("w", encoding="utf-8") as srt_file:
        for index, segment in enumerate(segments, start=1):
            srt_file.write(f"{index}\n")
            srt_file.write(
                f"{format_srt_timestamp(segment.start)} --> {format_srt_timestamp(segment.end)}\n"
            )
            srt_file.write(f"{segment.text}\n\n")

    return output_srt_path


def format_ass_timestamp(seconds: float) -> str:
    if seconds < 0:
        seconds = 0

    centiseconds_total = int(round(seconds * 100))
    hours = centiseconds_total // 360_000
    remaining = centiseconds_total % 360_000
    minutes = remaining // 6_000
    remaining = remaining % 6_000
    secs = remaining // 100
    centis = remaining % 100

    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def escape_ass_text(text: str) -> str:
    # ASS uses braces for inline tags, so we escape them in content.
    return text.replace("{", r"\{").replace("}", r"\}")


def _karaoke_line_from_words(segment: SubtitleSegment) -> str:
    if not segment.words:
        return escape_ass_text(segment.text)

    max_chars_per_line = 42
    lines: List[List[WordTiming]] = [[]]
    current_line_chars = 0

    for word_timing in segment.words:
        word_len = len(word_timing.word)
        projected = current_line_chars + (1 if current_line_chars else 0) + word_len
        if projected > max_chars_per_line and lines[-1]:
            lines.append([])
            current_line_chars = 0

        lines[-1].append(word_timing)
        current_line_chars += (1 if current_line_chars else 0) + word_len

    karaoke_lines: List[str] = []
    for line_words in lines:
        line_parts: List[str] = []
        for word_timing in line_words:
            duration_cs = max(1, int(round((word_timing.end - word_timing.start) * 100)))
            line_parts.append(f"{{\\k{duration_cs}}}{escape_ass_text(word_timing.word)}")

        karaoke_lines.append(" ".join(line_parts))

    return r"\N".join(karaoke_lines)


def write_ass_karaoke(
    segments: List[SubtitleSegment],
    output_ass_path: Path,
    font_family: str,
    font_size: int,
    vertical_position_percent: int,
) -> Path:
    output_ass_path.parent.mkdir(parents=True, exist_ok=True)

    safe_font = font_family.strip() or "Arial"
    clamped_position = max(0, min(100, vertical_position_percent))
    # ASS play resolution is 1080p, so map 0-100% to 0-1080 Y coordinate.
    y_position = int((clamped_position / 100) * 1080)

    ass_header = "\n".join(
        [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1920",
            "PlayResY: 1080",
            "WrapStyle: 0",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
            f"Style: Default,{safe_font},{font_size},&H00FFFFFF,&H0000A5FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,2,1,2,40,40,30,1",
            "",
            "[Events]",
            "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
        ]
    )

    with output_ass_path.open("w", encoding="utf-8") as ass_file:
        ass_file.write(ass_header + "\n")

        for segment in segments:
            karaoke_text = _karaoke_line_from_words(segment)
            dialogue_text = f"{{\\an5\\pos(960,{y_position})}}{karaoke_text}"
            ass_file.write(
                "Dialogue: 0,"
                f"{format_ass_timestamp(segment.start)},"
                f"{format_ass_timestamp(segment.end)},"
                f"Default,,0,0,0,,{dialogue_text}\n"
            )

    return output_ass_path
