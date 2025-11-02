"""
Progress widget for displaying conversion progress.
"""
import sys
import time
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import logger


class ProgressWidget(QWidget):
    """Widget for displaying conversion progress with time estimates."""

    def __init__(self, parent=None):
        """Initialize progress widget."""
        super().__init__(parent)
        self._start_time = None
        self._current_progress = 0
        self._last_bitrate_mbps = None  # Track last known bitrate
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout()
        layout.setSpacing(8)  # Apple HIG: 1 × 8pt base

        # Current file label
        self.current_file_label = QLabel("Ready")
        self.current_file_label.setObjectName("currentFileLabel")
        layout.addWidget(self.current_file_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("conversionProgressBar")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)

        # Time information
        time_layout = QHBoxLayout()
        time_layout.setSpacing(16)  # 2 × 8pt base

        self.time_label = QLabel("")
        self.time_label.setObjectName("timeLabel")
        time_layout.addWidget(self.time_label)

        time_layout.addStretch()

        self.speed_label = QLabel("")
        self.speed_label.setObjectName("speedLabel")
        time_layout.addWidget(self.speed_label)

        layout.addLayout(time_layout)

        self.setLayout(layout)

    def start_conversion(self, file_name: str):
        """
        Start tracking conversion progress.

        Args:
            file_name: Name of the file being converted
        """
        self._start_time = time.time()
        self._current_progress = 0
        self._last_bitrate_mbps = None  # Reset bitrate

        self.current_file_label.setText(f"Converting: {file_name}")
        self.progress_bar.setValue(0)
        self.time_label.setText("Starting...")
        self.speed_label.setText("")

        logger.debug(f"Progress widget started for: {file_name}")

    def update_progress(self, progress_data: dict):
        """
        Update progress display.

        Args:
            progress_data: Dictionary with progress information
                - progress: Percentage (0-100)
                - speed: Encoding speed (e.g., 1.5x)
                - time: Current time in seconds
                - fps: Frames per second
        """
        logger.debug(f"ProgressWidget.update_progress called with: {progress_data}")

        # Update progress bar
        if 'progress' in progress_data:
            progress = int(progress_data['progress'])
            self._current_progress = progress
            logger.debug(f"Setting progress bar to: {progress}%")
            self.progress_bar.setValue(progress)

        # Update bitrate tracking and display
        if 'bitrate_mbps' in progress_data:
            self._last_bitrate_mbps = progress_data['bitrate_mbps']

        # Always display bitrate if we have it, regardless of what's in current update
        if self._last_bitrate_mbps is not None:
            self.speed_label.setText(f"{self._last_bitrate_mbps:.1f} Mbps")
        elif 'speed' in progress_data:
            # Fallback to speed multiplier if no bitrate available
            speed = progress_data['speed']
            self.speed_label.setText(f"Speed: {speed:.2f}x")

        # Calculate and display time information
        if self._start_time and self._current_progress > 0:
            elapsed = time.time() - self._start_time
            elapsed_str = self._format_time(elapsed)

            # Estimate remaining time
            if self._current_progress > 5:  # Only show estimate after 5%
                estimated_total = (elapsed / self._current_progress) * 100
                remaining = estimated_total - elapsed
                remaining_str = self._format_time(remaining)

                self.time_label.setText(f"Time: {elapsed_str} / {remaining_str} remaining")
            else:
                self.time_label.setText(f"Time: {elapsed_str}")

    def finish_conversion(self, success: bool = True):
        """
        Mark conversion as finished.

        Args:
            success: Whether the conversion was successful
        """
        if success:
            self.progress_bar.setValue(100)
            self.current_file_label.setText("Conversion completed!")

            if self._start_time:
                elapsed = time.time() - self._start_time
                elapsed_str = self._format_time(elapsed)
                self.time_label.setText(f"Completed in {elapsed_str}")
            else:
                self.time_label.setText("Completed")

            self.speed_label.setText("")
        else:
            self.current_file_label.setText("Conversion failed")
            self.time_label.setText("")
            self.speed_label.setText("")

        logger.debug(f"Progress widget finished (success={success})")

    def reset(self):
        """Reset the progress widget to initial state."""
        self._start_time = None
        self._current_progress = 0
        self._last_bitrate_mbps = None  # Reset bitrate

        self.current_file_label.setText("Ready")
        self.progress_bar.setValue(0)
        self.time_label.setText("")
        self.speed_label.setText("")

        logger.debug("Progress widget reset")

    def set_status(self, message: str):
        """
        Set a custom status message.

        Args:
            message: Status message to display
        """
        self.current_file_label.setText(message)

    @staticmethod
    def _format_time(seconds: float) -> str:
        """
        Format time in seconds to human-readable format.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string (MM:SS or HH:MM:SS)
        """
        if seconds < 0:
            return "00:00"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


class BatchProgressWidget(QWidget):
    """Widget for displaying batch conversion progress."""

    def __init__(self, parent=None):
        """Initialize batch progress widget."""
        super().__init__(parent)
        self._total_files = 0
        self._completed_files = 0
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout()
        layout.setSpacing(8)  # Apple HIG: 1 × 8pt base

        # Overall progress label
        self.overall_label = QLabel("Overall Progress")
        self.overall_label.setObjectName("overallProgressLabel")
        layout.addWidget(self.overall_label)

        # Overall progress bar
        self.overall_progress_bar = QProgressBar()
        self.overall_progress_bar.setObjectName("overallProgressBar")
        self.overall_progress_bar.setRange(0, 100)
        self.overall_progress_bar.setValue(0)
        self.overall_progress_bar.setTextVisible(True)
        layout.addWidget(self.overall_progress_bar)

        self.setLayout(layout)

    def start_batch(self, total_files: int):
        """
        Start tracking batch progress.

        Args:
            total_files: Total number of files to convert
        """
        self._total_files = total_files
        self._completed_files = 0
        self._update_display()
        logger.debug(f"Batch progress started: {total_files} files")

    def update_batch_progress(self, completed_files: int):
        """
        Update batch progress.

        Args:
            completed_files: Number of completed files
        """
        self._completed_files = completed_files
        self._update_display()

    def file_completed(self):
        """Increment completed file count."""
        self._completed_files += 1
        self._update_display()

    def _update_display(self):
        """Update the display based on current progress."""
        if self._total_files > 0:
            progress = int((self._completed_files / self._total_files) * 100)
            self.overall_progress_bar.setValue(progress)
            self.overall_label.setText(
                f"Overall Progress: {self._completed_files} / {self._total_files} files"
            )
        else:
            self.overall_progress_bar.setValue(0)
            self.overall_label.setText("Overall Progress")

    def reset(self):
        """Reset batch progress."""
        self._total_files = 0
        self._completed_files = 0
        self._update_display()
        logger.debug("Batch progress reset")
