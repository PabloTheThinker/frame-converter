# Video Converter GUI - Development Plan

## Project Goal

Create a user-friendly GUI application that converts MP4 videos to MOV format for DaVinci Resolve, with drag-and-drop functionality and real-time progress tracking.

## Technology Stack Decision

**Selected: Python + PyQt6**

Reasons:
1. Native performance and appearance
2. Excellent FFmpeg integration via subprocess
3. Rich widget library for modern UI
4. Cross-platform (if needed later)
5. Good documentation and community support

## UI/UX Design

### Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│  Video Converter for DaVinci Resolve         [_][□][X] │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ╔════════════════════════════════════════════════╗    │
│  ║                                                ║    │
│  ║         Drag & Drop Video Files Here          ║    │
│  ║                    or                          ║    │
│  ║              [ Browse Files ]                  ║    │
│  ║                                                ║    │
│  ╚════════════════════════════════════════════════╝    │
│                                                          │
│  Files to Convert:                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ ✓ video1.mp4      1080p   2.5GB → ~2.6GB       │  │
│  │ ⏳ video2.mp4     1080p   5.1GB → ~5.3GB       │  │
│  │ ⏸ video3.mp4      4K      8.2GB → ~8.5GB       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Current: video2.mp4                                    │
│  Progress: ████████████░░░░░░░░░░░ 55%                │
│  Time: 2:34 / 4:42 remaining                            │
│                                                          │
│  [ Start Conversion ]  [ Pause ]  [ Cancel ]  [⚙️]      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Color Scheme

- Primary: #2E86AB (Blue - professional, trustworthy)
- Success: #06D6A0 (Green - completion)
- Warning: #F77F00 (Orange - processing)
- Error: #EF476F (Red - errors)
- Background: #FCFCFC (Light gray)
- Text: #2D3142 (Dark gray)
- Drop Zone: #E8F4F8 (Light blue tint)

## Implementation Steps

### Step 1: Basic Window Setup
**File:** `src/main.py`
```python
- Create QApplication
- Initialize main window
- Set window properties (size, title, icon)
- Create basic layout
```

### Step 2: Drop Zone Widget
**File:** `src/ui/drop_zone.py`
```python
- Create custom QWidget for drag & drop
- Implement dragEnterEvent
- Implement dropEvent
- Add visual feedback (hover state)
- Validate file types (MP4 only)
```

### Step 3: File List Widget
**File:** `src/ui/file_list.py`
```python
- Create QListWidget or QTableWidget
- Display file information (name, resolution, size)
- Add remove button for each file
- Show conversion status icons
```

### Step 4: FFmpeg Integration
**File:** `src/converter/ffmpeg_wrapper.py`
```python
- Create FFmpeg wrapper class
- Parse ffprobe output for video info
- Run conversion with progress tracking
- Parse FFmpeg progress output
- Handle errors and timeouts
```

### Step 5: Progress Tracking
**File:** `src/ui/progress_bar.py`
```python
- Create custom progress widget
- Update from FFmpeg output
- Calculate time remaining
- Show current file and overall progress
```

### Step 6: Settings Panel
**File:** `src/ui/settings_dialog.py`
```python
- Create settings dialog
- Quality presets (Fast/Balanced/High)
- Output directory selection
- Advanced options (CRF, codec)
```

### Step 7: Polish & Error Handling
```python
- Add notifications (completion, errors)
- Implement proper logging
- Add tooltips and help text
- Create about dialog
```

## File Structure

```
video-converter-gui/
├── README.md
├── PROJECT_PLAN.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── main.py                    # Entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py         # Main application window
│   │   ├── drop_zone.py           # Drag & drop widget
│   │   ├── file_list_widget.py    # File list display
│   │   ├── progress_widget.py     # Progress bars
│   │   └── settings_dialog.py     # Settings window
│   ├── converter/
│   │   ├── __init__.py
│   │   ├── ffmpeg_wrapper.py      # FFmpeg integration
│   │   ├── video_analyzer.py      # Video info extraction
│   │   └── conversion_worker.py   # Background conversion thread
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py              # App configuration
│   │   ├── logger.py              # Logging setup
│   │   └── validators.py          # File validation
│   └── resources/
│       └── styles.qss             # Qt stylesheet
├── scripts/
│   └── convert_to_mov.sh          # Backend conversion script
├── assets/
│   └── icons/
│       ├── app_icon.png
│       ├── drop_icon.png
│       └── ...
└── tests/
    ├── test_ffmpeg_wrapper.py
    └── test_video_analyzer.py
```

## FFmpeg Progress Parsing

FFmpeg outputs progress in this format:
```
frame= 1234 fps= 45 q=28.0 size=   12345kB time=00:01:23.45 bitrate=1234.5kbits/s speed=1.23x
```

Parse this to calculate:
- Current frame / Total frames = Progress %
- Speed value to estimate time remaining
- Real-time bitrate for size estimation

## Code Snippets

### Main Application Entry

```python
# src/main.py
import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Video Converter")
    app.setOrganizationName("Kyron Industries")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
```

### Drag & Drop Implementation

```python
# src/ui/drop_zone.py
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal

class DropZone(QWidget):
    files_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            if url.toLocalFile().endswith('.mp4'):
                files.append(url.toLocalFile())

        if files:
            self.files_dropped.emit(files)
```

### FFmpeg Wrapper

```python
# src/converter/ffmpeg_wrapper.py
import subprocess
import re
import json

class FFmpegWrapper:
    @staticmethod
    def get_video_info(file_path):
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)

    @staticmethod
    def convert_video(input_file, output_file, progress_callback=None):
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-c:v', 'libx264',
            '-preset', 'slow',
            '-crf', '18',
            '-c:a', 'aac',
            '-b:a', '320k',
            '-movflags', '+faststart',
            '-progress', 'pipe:1',
            '-y', output_file
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        # Parse progress output
        for line in process.stdout:
            if progress_callback and 'time=' in line:
                # Extract time and calculate progress
                progress_callback(line)

        process.wait()
        return process.returncode == 0
```

## Testing Plan

1. **Unit Tests**
   - FFmpeg wrapper functions
   - Video info parsing
   - File validation
   - Progress calculation

2. **Integration Tests**
   - Full conversion workflow
   - Multiple file batch processing
   - Error handling scenarios

3. **UI Tests**
   - Drag & drop functionality
   - Button interactions
   - Progress updates

4. **Manual Tests**
   - Various video formats
   - Different resolutions (720p, 1080p, 4K)
   - Long videos (2+ hours)
   - Multiple simultaneous conversions

## Performance Considerations

1. **Threading**: Run FFmpeg in separate thread to keep UI responsive
2. **Queue System**: Process one video at a time to avoid system overload
3. **Memory**: Stream processing, don't load entire video into memory
4. **Temp Files**: Clean up temporary files after conversion
5. **Cancellation**: Properly terminate FFmpeg process on cancel

## Error Handling

1. **Missing FFmpeg**: Check on startup, show installation instructions
2. **Invalid File**: Validate file before adding to queue
3. **Insufficient Space**: Check available disk space
4. **Conversion Failure**: Show detailed error message, allow retry
5. **Cancelled Conversion**: Clean up partial files

## Future Enhancements

- [ ] GPU acceleration (NVENC/VAAPI)
- [ ] Video preview thumbnails
- [ ] Trim/cut functionality
- [ ] Subtitle support
- [ ] Custom output resolution
- [ ] Batch preset templates
- [ ] CLI mode for automation
- [ ] System tray integration
- [ ] Desktop notifications

## Development Timeline Estimate

- **Week 1**: Basic window, drop zone, file list
- **Week 2**: FFmpeg integration, conversion logic
- **Week 3**: Progress tracking, UI polish
- **Week 4**: Settings, error handling, testing

## Resources

- [PyQt6 Documentation](https://doc.qt.io/qtforpython-6/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Qt Designer](https://doc.qt.io/qt-6/qtdesigner-manual.html) - For visual UI design

## Notes

- Keep UI simple and intuitive
- Prioritize reliability over features
- Test with real-world video files
- Consider different screen sizes
- Make it easy to batch process multiple files
