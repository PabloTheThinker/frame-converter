# Quick Start Guide

## What This Project Is

A GUI application that converts MP4 videos to MOV format for DaVinci Resolve editing, with a simple drag-and-drop interface.

## Status: ✅ FULLY IMPLEMENTED

The complete application has been implemented according to PROJECT_PLAN.md specifications!

## Quick Start (First Time Setup)

### Option 1: Automated Setup (Recommended)

```bash
cd ~/Documents/Kyron\ Industries/video-converter-gui

# Run the setup script
./setup.sh

# Run the application
./run.sh
```

### Option 2: Manual Setup

```bash
cd ~/Documents/Kyron\ Industries/video-converter-gui

# Install python3-venv if needed
sudo apt install python3-venv

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install PyQt6
pip install -r requirements.txt

# Run the application
python src/main.py
```

## Running the Application (After Setup)

```bash
cd ~/Documents/Kyron\ Industries/video-converter-gui

# Option 1: Use the run script
./run.sh

# Option 2: Manually activate and run
source venv/bin/activate
python src/main.py
```

## Implemented Features ✅

1. **Drag & Drop Interface** - Drop MP4 files directly into the application
2. **File Browser** - Alternative way to select files
3. **File Queue Display** - Shows file info (name, resolution, codec, size estimation)
4. **Real-time Progress** - Progress bar with percentage and time estimates
5. **Batch Processing** - Convert multiple files sequentially
6. **Settings Panel** - Quality presets (Fast/Balanced/High Quality)
7. **Custom CRF** - Advanced control over video quality
8. **Output Directory** - Configure where converted files are saved
9. **Error Handling** - Validates FFmpeg installation and file integrity
10. **Professional UI** - Styled with the color scheme from PROJECT_PLAN.md

## Project Structure

```
video-converter-gui/
├── src/
│   ├── main.py                      # ✅ Application entry point
│   ├── ui/
│   │   ├── main_window.py           # ✅ Main application window
│   │   ├── drop_zone.py             # ✅ Drag & drop widget
│   │   ├── file_list_widget.py      # ✅ File queue display
│   │   ├── progress_widget.py       # ✅ Progress tracking
│   │   └── settings_dialog.py       # ✅ Settings configuration
│   ├── converter/
│   │   ├── ffmpeg_wrapper.py        # ✅ FFmpeg integration
│   │   ├── video_analyzer.py        # ✅ Video metadata extraction
│   │   └── conversion_worker.py     # ✅ Background threading
│   ├── utils/
│   │   ├── config.py                # ✅ Configuration management
│   │   ├── logger.py                # ✅ Logging system
│   │   └── validators.py            # ✅ File validation
│   └── resources/
│       └── styles.qss               # ✅ Qt stylesheet
├── scripts/
│   └── convert_to_mov.sh            # ✅ Standalone bash script
├── setup.sh                         # ✅ Automated setup script
├── run.sh                           # ✅ Run script
├── requirements.txt                 # ✅ Python dependencies
├── README.md                        # ✅ Full documentation
└── PROJECT_PLAN.md                  # ✅ Development plan
```

## File Overview

- **README.md** - Complete project overview, features, and technical details
- **PROJECT_PLAN.md** - Development plan that was followed for implementation
- **QUICKSTART.md** - This file - quick start instructions
- **requirements.txt** - Python dependencies (PyQt6)
- **setup.sh** - Automated setup script
- **run.sh** - Quick run script
- **scripts/convert_to_mov.sh** - Standalone bash conversion script

## Important Notes

- Uses **H.264 codec** (not DNxHD) to keep file sizes reasonable
- A 2-hour video should be ~5-10GB, not 385GB
- PyQt6 provides modern, native-looking GUI
- FFmpeg handles all conversion work
- Conversions run in background threads to keep UI responsive
- Logs are saved to `~/.video-converter/logs/` for debugging

## Requirements

- **Python 3.8+** - Programming language
- **FFmpeg** - Video conversion engine (install: `sudo apt install ffmpeg`)
- **PyQt6** - GUI framework (installed automatically by setup.sh)
- **python3-venv** - Virtual environment support (installed by setup.sh if needed)

## Troubleshooting

If you encounter issues:

1. **Check FFmpeg installation**: `ffmpeg -version`
2. **Check logs**: `~/.video-converter/logs/video_converter.log`
3. **Verify Python version**: `python3 --version` (should be 3.8+)
4. **Reinstall dependencies**: Delete `venv/` folder and run `./setup.sh` again
