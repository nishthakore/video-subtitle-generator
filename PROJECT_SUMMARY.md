# Video Subtitle Generator - Full Project Summary

## 1. Project Title
Automatic Video Subtitle Generator using Python, Streamlit, Faster-Whisper, and ffmpeg

## 2. Problem Statement
The goal of this mini project is to allow a user to upload a video and receive the same video back with subtitles rendered at the bottom. The solution should work fully in Python with Streamlit as the frontend.

## 3. Objective
- Accept user video input from a web UI.
- Convert speech in the video to text with timestamps.
- Generate subtitle file in SRT format.
- Burn subtitles into output video frames.
- Provide downloadable subtitled video and subtitle file.

## 4. Why This Project Is Useful
- Makes video content accessible for hearing-impaired users.
- Improves comprehension for viewers in noisy environments.
- Supports content creators for quick subtitle generation.
- Useful for multilingual education and social media content.

## 5. Current Project Structure

video-subtitle-generator/
|-- app.py
|-- requirements.txt
|-- README.md
|-- PROJECT_SUMMARY.md
|-- utils/
|   |-- __init__.py
|   |-- subtitle_generator.py
|   `-- video_processor.py
`-- temp/

## 6. Technology Stack
- Language: Python 3.10+
- Frontend/App Layer: Streamlit
- Speech Recognition: Faster-Whisper
- Video and Audio Processing: ffmpeg
- Utility Libraries: ctranslate2, av, onnxruntime, numpy, tqdm

## 7. Core Concepts Used

### 7.1 Automatic Speech Recognition (ASR)
ASR converts spoken audio into text. Faster-Whisper is an efficient Whisper implementation that provides timestamped segments.

### 7.2 Timestamped Segmentation
Transcribed text is not enough for subtitles. Each subtitle requires:
- Start time
- End time
- Text line

### 7.3 SRT Subtitle Format
SRT is a standard subtitle format:
1
00:00:01,200 --> 00:00:03,800
Hello world.

### 7.4 Burned Subtitles (Hard Subtitles)
The subtitle text is rendered directly into video frames. End users cannot toggle these subtitles off.

### 7.5 Audio Codec Compatibility
Some processed outputs can become silent in browser players if audio codec/container combinations are not compatible. The project now re-encodes audio to AAC during final export for broad compatibility.

### 7.6 Video Re-encoding
When subtitles are burned into video, frames must be re-encoded. The project uses H.264 for video and AAC for audio in output MP4.

## 8. End-to-End Workflow
1. User opens the Streamlit app.
2. User uploads a video file.
3. App saves video to temp input folder.
4. ffmpeg extracts mono 16 kHz WAV audio.
5. Faster-Whisper transcribes audio to timestamped segments.
6. App writes segments into an SRT file.
7. ffmpeg burns SRT subtitles onto video.
8. App displays output video and provides download buttons.

## 9. Detailed Module Working

### 9.1 app.py
Responsibilities:
- Streamlit UI rendering.
- User input handling (video upload, model size, language, subtitle style).
- Pipeline orchestration.
- Progress status updates.
- Output preview and download actions.

Main flow:
- Validate ffmpeg presence.
- Save uploaded file.
- Extract audio.
- Transcribe to segments.
- Write SRT.
- Burn subtitles.
- Return result files.

### 9.2 utils/subtitle_generator.py
Responsibilities:
- Convert audio to text segments.
- Format timestamps for SRT.
- Write subtitle entries to SRT file.

Important functions:
- format_srt_timestamp(seconds)
- transcribe_audio_to_segments(audio_path, model_size, language, device, compute_type)
- write_srt(segments, output_srt_path)

### 9.3 utils/video_processor.py
Responsibilities:
- Verify ffmpeg availability.
- Extract speech-friendly WAV audio.
- Burn subtitles with visual styling.

Important functions:
- ensure_ffmpeg_available()
- extract_audio_from_video(video_path, output_audio_path)
- burn_subtitles_to_video(input_video_path, input_srt_path, output_video_path, subtitle_font_size, subtitle_margin_v)

## 10. Model Size Study (tiny, base, small)

### tiny
- Fastest
- Lowest resource usage
- Good for quick demo and clean audio
- Lower accuracy in noisy/multi-speaker content

### base
- Balanced speed and quality
- Good default for most practical use
- Better than tiny in accents/noise scenarios

### small
- Better accuracy
- Slower processing on CPU
- Good for final export when quality matters more than speed

Recommended practical policy:
- First pass: tiny
- If errors are high: base
- For important final output: small

## 11. Input/Output and Processing Constraints

Supported upload formats:
- mp4, mov, mkv, avi

Output:
- Subtitled MP4 video (hard subtitles)
- SRT subtitle file

Limitations:
- Very long videos can take time on CPU.
- ASR is not 100 percent perfect.
- Strong background music can reduce transcript quality.

## 12. Manual Setup Needed by User
1. Install Python.
2. Install project dependencies:
   pip install -r requirements.txt
3. Install ffmpeg and add to PATH.
4. Keep internet enabled for first-time model download.
5. Ensure enough disk space in temp folder.
6. If runtime DLL issue occurs on Windows, install Microsoft Visual C++ Redistributable x64.

## 13. How to Run
1. Open project folder in terminal.
2. Run:
   streamlit run app.py
3. Open local Streamlit URL.
4. Upload video.
5. Select model.
6. Generate and download output.

## 14. Testing and Validation Strategy

### Functional tests
- Upload valid supported video.
- Check output video contains subtitles.
- Check subtitle timing is synchronized.
- Check output video has audible audio.
- Download and open generated SRT.

### Negative tests
- Upload unsupported file type.
- Upload video with no speech.
- Process very short or very noisy clips.

### Performance checks
- Measure processing time for 30s, 2min, and 10min videos.
- Compare speed and output quality for tiny/base/small.

## 15. Common Issues and Solutions
- ffmpeg not found:
  Install ffmpeg and add to PATH.
- Subtitles inaccurate:
  Move from tiny to base or small.
- Output muted:
  Ensure AAC re-encoding path is used (already in code).
- Slow processing:
  Use shorter clips, tiny model, or stronger hardware.

## 16. Security and Reliability Considerations
- Validate file types before processing.
- Use temporary directories for controlled storage.
- Add periodic cleanup for temp files.
- Add file size limit to avoid misuse.

## 17. Future Scope
- Soft subtitle track option instead of only hard subtitles.
- Automatic language translation of subtitles.
- Speaker diarization (who spoke each line).
- Queue/background worker system for large files.
- Cloud deployment with object storage.
- Admin dashboard with processing analytics.

## 18. Resume and Viva Points
- Built an end-to-end AI + multimedia pipeline.
- Integrated ASR inference with practical video processing.
- Solved real playback issue by audio codec normalization.
- Designed UI, backend utilities, and export workflow in Python.

## 19. Conclusion
This project successfully demonstrates a production-style subtitle generation pipeline from upload to final subtitled video delivery, using a fully Python-based stack with Streamlit UI and practical engineering choices for compatibility, speed, and usability.
