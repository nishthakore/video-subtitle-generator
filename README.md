# Video Subtitle Generator

A mini-project that lets users upload a video and get the same video back with subtitles burned at the bottom.

## 1. Features
- Upload video from browser (Streamlit)
- Extract audio from video (ffmpeg)
- Speech-to-text transcription using Faster-Whisper
- Auto-generate subtitle file in SRT format
- Burn subtitles directly into video using ffmpeg
- Download both subtitled video and SRT file

## 2. Tech Stack
- Python 3.10+
- Streamlit for frontend + app server
- Faster-Whisper for transcription
- ffmpeg for video/audio processing

Default runtime mode in this project is lightweight:
- Whisper model default is `tiny` in the app settings.
- This is the fastest and easiest option for laptops.

## 3. Project Structure

video-subtitle-generator/
├── app.py
├── requirements.txt
├── utils/
│   ├── __init__.py
│   ├── video_processor.py
│   └── subtitle_generator.py
├── temp/
└── README.md

## 4. Setup Instructions
### 4.1 Clone/Open Project
Open this folder in VS Code.

### 4.2 Create virtual environment (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4.3 Install Python dependencies
```powershell
pip install -r requirements.txt
```

### 4.4 Install ffmpeg
You must install ffmpeg and add it to system PATH.

Check:
```powershell
ffmpeg -version
```

### 4.5 Manual prerequisites on Windows
You may need to add these manually:
- Microsoft Visual C++ Redistributable (x64), if Faster-Whisper fails to load.
- GPU drivers + CUDA runtime only if you later switch to GPU acceleration.
- Sufficient free disk space in `temp/` for uploaded and processed videos.

## 5. Run the App
```powershell
streamlit run app.py
```

## 5.1 Deploy on Streamlit Community Cloud
1. Push this repository to GitHub.
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app** and select:
   - Repository: your GitHub repo
   - Branch: `main`
   - Main file path: `app.py`
4. Click **Deploy**.

Notes:
- This project includes `packages.txt` with `ffmpeg` so Streamlit Cloud installs the system package automatically.
- If deployment fails after changes, use the app dashboard option to reboot/redeploy.

## 6. How it Works (Pipeline)
1. User uploads video.
2. App stores video in temp/inputs.
3. ffmpeg extracts mono 16kHz WAV audio.
4. Faster-Whisper transcribes audio into timed segments.
5. App writes timed segments to SRT file.
6. ffmpeg burns subtitle text onto original video frames.
7. App returns subtitled video and SRT for download.

## 7. Important Concepts
- **ASR (Automatic Speech Recognition):** Converts speech to text.
- **Timestamped Segments:** Subtitle text with start/end time.
- **SRT Format:** Standard subtitle format used by most video players.
- **Burned Subtitles:** Subtitles permanently rendered into video frames.
- **Soft Subtitles:** Separate subtitle track (not used in this version).

## 8. Future Improvements
- Speaker diarization (who said what)
- Word-level subtitle highlighting
- Translation to other languages
- Queue + background workers for large files
- Cloud storage integration (S3/GCS)
- Docker deployment

## 9. Troubleshooting
- If app fails at transcription, verify Python packages installed correctly.
- If app fails at video processing, verify ffmpeg is installed and available in PATH.
- Large videos can take time on CPU; start with small test videos.
- If subtitle quality is low, change model from `tiny` to `base` or `small` in the sidebar.
- If output video appears muted in browser players, this is usually an audio codec compatibility issue. The app now re-encodes audio to AAC during subtitle burn-in for reliable playback.
- If Hindi or other non-English subtitles appear translated to English, set the language code explicitly (for example `hi`, `ta`, `te`). The app is configured to use transcription mode (same-language subtitles), not translation mode.
