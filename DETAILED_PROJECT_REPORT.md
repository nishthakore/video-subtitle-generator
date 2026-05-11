# Video Subtitle Generator - Detailed Project Report

## 1. Project Information
- Project Name: Video Subtitle Generator
- Report Date: April 17, 2026
- Project Type: AI-enabled multimedia processing web application
- Technology Domain: Speech-to-text, subtitle generation, video processing

## 2. Executive Summary
This project implements an end-to-end pipeline for generating subtitles from uploaded videos and producing a final subtitled MP4 output. The application is built with Streamlit for the user interface, Faster-Whisper for transcription, and ffmpeg for media processing. The current version supports configurable recognition quality, optional source language hints, downloadable subtitle files (SRT), and styled karaoke subtitles (ASS) burned into the final video.

The system is designed for practical local use on CPU-based machines and focuses on usability, compatibility, and predictable output quality. It is suitable as a mini-project, portfolio project, or foundation for a production-grade subtitle service.

## 3. Problem Statement
Manual subtitling is slow and labor-intensive. Many creators and students need a low-cost workflow to automatically generate timed subtitles and produce a shareable subtitled video. This project addresses that need by automating upload, transcription, subtitle formatting, and subtitle burn-in in one workflow.

## 4. Objectives
- Accept user video uploads through a web interface.
- Extract clean mono audio suitable for speech recognition.
- Transcribe speech into timestamped segments.
- Generate subtitle artifacts in standard format (SRT).
- Generate styled karaoke subtitle track (ASS).
- Burn subtitles into MP4 output for easy playback.
- Provide downloadable final video and subtitle file.

## 5. Scope
### In Scope
- Local web app workflow via Streamlit.
- CPU-based Faster-Whisper transcription.
- Hard subtitle rendering into video.
- Subtitle style controls (font family, font size, vertical position).
- Multiple model options and decoding quality presets.

### Out of Scope
- Multi-user queue orchestration.
- Cloud storage integration.
- Authentication and access control.
- Real-time live subtitling.
- Speaker diarization and translation pipeline.

## 6. System Architecture
The solution follows a modular architecture with a UI orchestration layer and utility modules:

- app.py:
  - Handles UI, user inputs, orchestration, and output display/download.
- utils/subtitle_generator.py:
  - Handles ASR transcription, timestamp formatting, SRT writing, ASS karaoke creation.
- utils/video_processor.py:
  - Handles ffmpeg availability check, audio extraction, subtitle burn-in rendering.
- temp/:
  - Runtime artifact storage (inputs, extracted audio, subtitles, final outputs).

## 7. Technology Stack
- Language: Python 3.10+
- UI Framework: Streamlit
- ASR Engine: Faster-Whisper
- Media Processing: ffmpeg
- Supporting Packages:
  - ctranslate2
  - av
  - onnxruntime
  - numpy
  - tqdm

## 8. Functional Workflow
1. User uploads a video file (mp4, mov, mkv, avi).
2. App saves the uploaded file in temp/inputs.
3. ffmpeg extracts mono PCM WAV audio at 16 kHz into temp/audio.
4. Faster-Whisper transcribes audio with VAD and word timestamps.
5. System writes standard SRT subtitles.
6. System generates ASS karaoke subtitles with per-word highlight timing.
7. ffmpeg burns subtitles into video using libx264 encoding.
8. App previews output and enables downloads.

## 9. Core Module Analysis
### 9.1 app.py
Primary responsibilities:
- Builds Streamlit layout and sidebar controls.
- Creates required temporary directories at startup.
- Exposes configuration options:
  - model size (tiny, base, small, medium, large-v3)
  - optional language code
  - transcription quality preset (Fast, Balanced, Accurate)
  - subtitle font family, size, and vertical position
- Maps quality presets to decoding parameters:
  - Fast: beam_size=1, best_of=1
  - Balanced: beam_size=5, best_of=5
  - Accurate: beam_size=8, best_of=8
- Applies Hindi-specific decoding strengthening when language=hi.
- Orchestrates the complete processing pipeline with user-visible status steps.
- Shows resulting video and download buttons for MP4 and SRT.

### 9.2 utils/subtitle_generator.py
Primary responsibilities:
- Defines subtitle data structures:
  - SubtitleSegment (start, end, text, words)
  - WordTiming (start, end, word)
- Converts seconds to SRT and ASS timestamp formats.
- Runs Faster-Whisper transcription with:
  - task=transcribe
  - vad_filter=True
  - word_timestamps=True
  - condition_on_previous_text=True
- Writes SRT subtitles.
- Builds ASS karaoke dialogues with timed per-word tags and line wrapping.
- Escapes ASS-sensitive characters for stable rendering.

### 9.3 utils/video_processor.py
Primary responsibilities:
- Validates ffmpeg availability via PATH detection.
- Extracts speech-ready WAV audio from source video.
- Burns subtitle track into video:
  - If ASS input: use ass filter directly.
  - If non-ASS input: use subtitles filter with force_style.
- Re-encodes output for compatibility:
  - video: libx264
  - audio: aac
  - output optimization: +faststart

## 10. Data and Artifact Lifecycle
Runtime artifacts are created under temp/:
- temp/inputs: uploaded source videos
- temp/audio: extracted WAV files
- temp/subtitles: generated SRT and ASS files
- temp/outputs: final subtitled MP4 files

Naming strategy uses Unix timestamps to reduce filename collisions.

## 11. User Interface and UX Behavior
- Clean single-page flow with sidebar configuration and main-area actions.
- Immediate preview of uploaded input video.
- Explicit action button to start processing.
- Step-by-step status updates during processing.
- Final success state with output preview and downloads.
- Error handling through visible Streamlit error notifications.

## 12. Subtitle Styling and Readability
The project supports user-adjustable subtitle presentation:
- Font family selection from a list of common fonts.
- Font size control.
- Vertical positioning via percentage-based slider.
- Karaoke-like word highlighting using ASS timing tags.

This improves readability and can be tuned per content type (lectures, reels, interviews).

## 13. Performance Characteristics
### Processing Cost Drivers
- Video duration and audio complexity.
- Selected model size.
- Decoding settings (beam search and best-of values).
- Hardware profile (CPU speed, RAM, storage throughput).

### Practical Quality-Speed Tradeoff
- Fast mode: fastest throughput, lower transcription stability.
- Balanced mode: recommended default for most cases.
- Accurate mode: higher quality, slower processing.

## 14. Reliability and Error Handling
Current reliability measures:
- ffmpeg binary check before processing.
- Runtime exception handling around the full pipeline.
- Speech-empty guard: fails clearly when no segments are detected.
- Controlled creation of output directories.

Potential robustness improvements:
- Validate upload size and duration limits.
- Add temp artifact cleanup policy.
- Improve ffmpeg stderr surfacing with categorized user messages.
- Add retries for transient model loading issues.

## 15. Security and Safety Considerations
- File processing is local by default, reducing remote exposure.
- Inputs are constrained by extension at UI level.
- No direct shell input from users beyond controlled file operations.

Recommended security improvements:
- Validate MIME type and probe media headers server-side.
- Add file size limits and request throttling.
- Sanitize and normalize uploaded file names aggressively.
- Introduce sandboxing/containerization for untrusted media in shared deployments.

## 16. Compatibility Notes
- Requires ffmpeg installed and available in PATH.
- Designed for Python virtual environment execution.
- Uses AAC audio in final MP4 for broad browser/player compatibility.
- First model run may trigger model download and extra startup delay.

## 17. Testing Strategy
### Functional Tests
- Upload each supported input container type.
- Validate subtitle timing and text visibility.
- Validate output audio playback.
- Verify SRT download integrity and format.

### Negative Tests
- Unsupported extension upload.
- Very short or no-speech media.
- Corrupt file input.
- Extremely noisy audio.

### Performance Tests
- Benchmark short, medium, and long clips.
- Compare throughput across model sizes and quality presets.
- Track memory and CPU utilization on representative hardware.

## 18. Current Limitations
- No built-in asynchronous job queue.
- CPU defaults can be slow for long videos.
- No speaker diarization.
- No automatic subtitle translation.
- Temporary artifact retention can grow disk usage over time.

## 19. Future Enhancement Roadmap
- Add soft subtitle track export option in output MP4.
- Add multi-language translation mode.
- Add speaker diarization labels.
- Add chunked or batched processing for long-form media.
- Add background task queue and progress persistence.
- Add cloud storage connectors and deployment templates.
- Add automated test suite and CI pipeline.

## 20. Educational and Portfolio Value
This project demonstrates integration of:
- Applied AI inference (ASR)
- Practical multimedia processing with ffmpeg
- Full pipeline orchestration in Python
- User-centric web interface with configurable quality controls
- Production-relevant compatibility decisions (codec/format handling)

## 21. Conclusion
The Video Subtitle Generator successfully delivers a complete upload-to-output subtitle workflow and goes beyond a basic MVP by supporting configurable decoding quality and karaoke-style subtitle rendering. The codebase is modular and extensible, making it a strong foundation for advanced features such as translation, diarization, and scalable background processing.

The current implementation is suitable for academic demonstration, practical personal use, and iterative expansion toward a production-ready subtitle platform.
