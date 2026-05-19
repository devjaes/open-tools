# Audio/Video Merger

A cross-platform desktop application built with Python and Tkinter for merging video and audio files effortlessly using FFmpeg.

## Features
- **Modern UI**: Uses `tkinter.ttk` for native and sleek components across OSs.
- **Dynamic Progress Bar**: Parses `ffmpeg` and `ffprobe` to accurately calculate and display the progress of the merging process.
- **Cross-Platform**: Designed to work and compile natively on Windows, macOS, and Linux.

## Prerequisites
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) (Ensure it is in your system's `PATH`)

## How to Run Locally
Run the Python script directly:
```bash
python audio-video-merge.py
```

## How to Compile (Standalone Executable)
To package this tool into a standalone executable (no Python required on the target machine), go back to the root of the `open-tools` repository and run the build script:
```bash
cd ../../
python build.py
```
This script handles `PyInstaller` internally and will place the final executable inside the `dist/` directory at the root level.
