from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from utils.subtitle_generator import (
    transcribe_audio_to_segments,
    write_ass_karaoke,
    write_srt,
)
from utils.video_processor import (
    burn_subtitles_to_video,
    ensure_ffmpeg_available,
    extract_audio_from_video,
)


BASE_DIR = Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
INPUT_DIR = TEMP_DIR / "inputs"
AUDIO_DIR = TEMP_DIR / "audio"
SUBTITLE_DIR = TEMP_DIR / "subtitles"
OUTPUT_DIR = TEMP_DIR / "outputs"

for directory in [INPUT_DIR, AUDIO_DIR, SUBTITLE_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


st.set_page_config(page_title="Video Subtitle Generator", layout="wide")
st.title("Video Subtitle Generator")
st.caption("Upload a video, generate subtitles, and get back the same video with burned subtitles.")


with st.sidebar:
    st.header("Settings")
    model_size = st.selectbox(
        "Whisper model size",
        options=["tiny", "base", "small", "medium", "large-v3"],
        index=2,
        help="Bigger models are slower but more accurate, especially for non-English audio.",
    )
    language = st.text_input(
        "Language code (optional)",
        value="",
        help="Use ISO code like en, hi, ta. Leave empty for auto-detect.",
    ).strip()
    quality_preset = st.selectbox(
        "Transcription quality",
        options=["Fast", "Balanced", "Accurate"],
        index=1,
        help="Accurate mode improves recognition for Hindi and noisy audio, but is slower.",
    )
    st.caption(
        "For Hindi or other non-English videos, set language code explicitly (for example: hi). "
        "This app uses transcription mode only, not translation mode."
    )
    if model_size in ["tiny", "base"]:
        st.warning(
            "For Hindi audio, prefer model size 'small' or higher for significantly better accuracy."
        )

    if quality_preset == "Fast":
        beam_size, best_of, temperature = 1, 1, 0.0
    elif quality_preset == "Balanced":
        beam_size, best_of, temperature = 5, 5, 0.0
    else:
        beam_size, best_of, temperature = 8, 8, 0.0

    normalized_language = language.lower() if language else ""

    if normalized_language == "hi":
        # Hindi on smaller models often drifts; stronger decoding improves stability.
        beam_size = max(beam_size, 6)
        best_of = max(best_of, 6)

    font_size = st.slider("Subtitle font size", min_value=14, max_value=36, value=20)
    font_family = st.selectbox(
        "Subtitle font family",
        options=[
            "Arial",
            "Arial Black",
            "Bahnschrift",
            "Calibri",
            "Cambria",
            "Candara",
            "Century Gothic",
            "Comic Sans MS",
            "Consolas",
            "Courier New",
            "Franklin Gothic Medium",
            "Garamond",
            "Georgia",
            "Impact",
            "Lucida Sans Unicode",
            "Palatino Linotype",
            "Segoe UI",
            "Tahoma",
            "Times New Roman",
            "Trebuchet MS",
            "Verdana",
        ],
        index=0,
        help="Choose the font style used for burned subtitles.",
    )
    vertical_position = st.slider(
        "Subtitle vertical position (%)",
        min_value=5,
        max_value=95,
        value=88,
        help="5 is near top, 95 is near bottom.",
    )


uploaded_file = st.file_uploader(
    "Upload video",
    type=["mp4", "mov", "mkv", "avi"],
)


if uploaded_file is not None:
    st.video(uploaded_file)

    if st.button("Generate subtitled video", type="primary"):
        try:
            ensure_ffmpeg_available()

            timestamp = str(int(time.time()))
            input_video_path = INPUT_DIR / f"{timestamp}_{uploaded_file.name}"
            audio_path = AUDIO_DIR / f"{timestamp}.wav"
            srt_path = SUBTITLE_DIR / f"{timestamp}.srt"
            ass_path = SUBTITLE_DIR / f"{timestamp}.ass"
            output_video_path = OUTPUT_DIR / f"{timestamp}_subtitled.mp4"

            with st.status("Processing video...", expanded=True) as status:
                status.write("Saving uploaded video...")
                with input_video_path.open("wb") as output_file:
                    output_file.write(uploaded_file.getbuffer())

                status.write("Extracting audio...")
                extract_audio_from_video(input_video_path, audio_path)

                status.write("Transcribing audio into subtitles...")
                segments = transcribe_audio_to_segments(
                    audio_path=audio_path,
                    model_size=model_size,
                    language=language or None,
                    task="transcribe",
                    beam_size=beam_size,
                    best_of=best_of,
                    temperature=temperature,
                )

                if not segments:
                    raise RuntimeError("No speech was detected, subtitles could not be generated.")

                status.write("Writing SRT subtitle file...")
                write_srt(segments, srt_path)

                status.write("Building styled subtitles with live word highlighting...")
                write_ass_karaoke(
                    segments=segments,
                    output_ass_path=ass_path,
                    font_family=font_family,
                    font_size=font_size,
                    vertical_position_percent=vertical_position,
                )

                status.write("Burning subtitles into video...")
                burn_subtitles_to_video(
                    input_video_path=input_video_path,
                    subtitle_path=ass_path,
                    output_video_path=output_video_path,
                    subtitle_font_size=font_size,
                )

                status.update(label="Processing complete", state="complete")

            st.success("Subtitled video generated successfully")
            st.video(str(output_video_path))

            with output_video_path.open("rb") as video_file:
                st.download_button(
                    "Download subtitled video",
                    data=video_file,
                    file_name=output_video_path.name,
                    mime="video/mp4",
                )

            with srt_path.open("rb") as subtitle_file:
                st.download_button(
                    "Download SRT file",
                    data=subtitle_file,
                    file_name=srt_path.name,
                    mime="text/plain",
                )

        except Exception as exc:
            st.error(f"Error: {exc}")
else:
    st.info("Upload a video to begin")





