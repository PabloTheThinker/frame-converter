"""
Main application window.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.drop_zone import DropZone
from ui.file_list_widget import FileListWidget
from ui.progress_widget import ProgressWidget, BatchProgressWidget
from ui.settings_dialog import SettingsDialog, QuickSettingsWidget
from ui.about_dialog import AboutDialog
from converter.conversion_worker import BatchConversionManager
from utils.config import config
from utils.validators import check_ffmpeg_available, validate_conversion_request, parse_ffmpeg_error
from utils.logger import logger


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()
        self.conversion_manager = None
        self._is_converting = False
        self._setup_window()
        self._setup_ui()
        self._check_dependencies()

    def _setup_window(self):
        """Set up window properties."""
        self.setWindowTitle(config.APP_NAME)

        # Set application icon
        icon_path = Path(__file__).parent.parent / 'resources' / 'app_icon.png'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            logger.info(f"Application icon loaded from: {icon_path}")
        else:
            logger.warning(f"Application icon not found at: {icon_path}")

        # Larger, more spacious window for modern design
        self.setMinimumSize(900, 700)
        self.resize(1000, 800)

    def _setup_ui(self):
        """Set up the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout - More spacious Apple-style
        main_layout = QVBoxLayout()
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self._on_files_dropped)
        main_layout.addWidget(self.drop_zone)

        # File list
        self.file_list = FileListWidget()
        self.file_list.file_removed.connect(self._on_file_removed)
        self.file_list.clear_all.connect(self._on_clear_all)
        main_layout.addWidget(self.file_list, stretch=1)

        # Progress widgets
        self.progress_widget = ProgressWidget()
        main_layout.addWidget(self.progress_widget)

        self.batch_progress_widget = BatchProgressWidget()
        self.batch_progress_widget.setVisible(False)
        main_layout.addWidget(self.batch_progress_widget)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(16)  # Proper spacing between buttons

        self.start_button = QPushButton("Start Conversion")
        self.start_button.setObjectName("startButton")
        self.start_button.setToolTip("Start converting all files in the queue to MOV format optimized for DaVinci Resolve")
        self.start_button.clicked.connect(self._on_start_conversion)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.setEnabled(False)
        button_layout.addWidget(self.start_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setToolTip("Stop the current conversion process")
        self.cancel_button.clicked.connect(self._on_cancel_conversion)
        self.cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        self.settings_button = QPushButton("⚙ Settings")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.setToolTip("Configure quality presets, GPU acceleration, and output directory")
        self.settings_button.clicked.connect(self._on_settings_clicked)
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.settings_button)

        self.about_button = QPushButton("ℹ About")
        self.about_button.setObjectName("aboutButton")
        self.about_button.setToolTip("About FrameConverter and creator information")
        self.about_button.clicked.connect(self._on_about_clicked)
        self.about_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(self.about_button)

        main_layout.addLayout(button_layout)

        # Quick settings (optional, can be commented out)
        # self.quick_settings = QuickSettingsWidget()
        # self.quick_settings.settings_button_clicked.connect(self._on_settings_clicked)
        # main_layout.addWidget(self.quick_settings)

        central_widget.setLayout(main_layout)

        logger.info("Main window UI initialized")

    def _check_dependencies(self):
        """Check if required dependencies are available."""
        is_available, message = check_ffmpeg_available()

        if not is_available:
            QMessageBox.critical(
                self,
                "Missing Dependencies",
                f"{message}\n\n"
                "Please install FFmpeg to use this application.\n"
                "Visit: https://ffmpeg.org/download.html"
            )
            logger.error("FFmpeg not available")
            # Disable UI
            self.drop_zone.set_enabled(False)
            self.start_button.setEnabled(False)
        else:
            logger.info("All dependencies available")

    def _on_files_dropped(self, file_paths: list):
        """
        Handle files dropped/selected.

        Args:
            file_paths: List of file paths
        """
        if self._is_converting:
            QMessageBox.warning(
                self,
                "Conversion in Progress",
                "Please wait for the current conversion to finish before adding more files."
            )
            return

        self.file_list.add_files(file_paths)
        self._update_button_states()

        logger.info(f"Added {len(file_paths)} files to queue")

    def _on_file_removed(self, file_path: str):
        """
        Handle file removed from queue.

        Args:
            file_path: Path to removed file
        """
        self._update_button_states()
        logger.info(f"File removed: {file_path}")

    def _on_clear_all(self):
        """Handle clear all button click."""
        self._update_button_states()
        logger.info("All files cleared")

    def _on_start_conversion(self):
        """Handle start conversion button click."""
        file_list = self.file_list.get_file_list()

        if not file_list:
            return

        # Validate all files
        for file_path in file_list:
            is_valid, error_msg = validate_conversion_request(file_path)
            if not is_valid:
                QMessageBox.critical(
                    self,
                    "Validation Error",
                    f"Cannot convert {Path(file_path).name}:\n{error_msg}"
                )
                return

        # Start conversion
        self._is_converting = True
        self._update_button_states()

        # Show batch progress if multiple files
        if len(file_list) > 1:
            self.batch_progress_widget.setVisible(True)
            self.batch_progress_widget.start_batch(len(file_list))

        # Create and start conversion manager
        self.conversion_manager = BatchConversionManager(file_list)
        self.conversion_manager.file_started.connect(self._on_file_started)
        self.conversion_manager.file_finished.connect(self._on_file_finished)
        self.conversion_manager.file_failed.connect(self._on_file_failed)
        self.conversion_manager.progress_updated.connect(self._on_progress_updated)
        self.conversion_manager.all_finished.connect(self._on_all_finished)
        self.conversion_manager.batch_cancelled.connect(self._on_batch_cancelled)

        self.conversion_manager.start()

        logger.info(f"Started batch conversion of {len(file_list)} files")

    def _on_cancel_conversion(self):
        """Handle cancel conversion button click."""
        if self.conversion_manager and self.conversion_manager.isRunning():
            reply = QMessageBox.question(
                self,
                "Cancel Conversion",
                "Are you sure you want to cancel the conversion?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.conversion_manager.cancel()
                logger.info("User cancelled conversion")

    def _on_file_started(self, index: int, total: int, input_file: str):
        """
        Handle file conversion started.

        Args:
            index: File index
            total: Total files
            input_file: Input file path
        """
        file_name = Path(input_file).name
        self.progress_widget.start_conversion(file_name)
        self.file_list.update_file_status(input_file, "processing")

        logger.info(f"Converting file {index + 1}/{total}: {file_name}")

    def _on_file_finished(self, index: int, total: int, output_file: str):
        """
        Handle file conversion finished.

        Args:
            index: File index
            total: Total files
            output_file: Output file path
        """
        # Find input file for this output
        for input_file in self.file_list.get_file_list():
            self.file_list.update_file_status(input_file, "completed")
            break

        self.progress_widget.finish_conversion(success=True)

        if len(self.file_list.get_file_list()) > 1:
            self.batch_progress_widget.file_completed()

        logger.info(f"File {index + 1}/{total} completed: {Path(output_file).name}")

    def _on_file_failed(self, index: int, total: int, input_file: str, error: str):
        """
        Handle file conversion failed.

        Args:
            index: File index
            total: Total files
            input_file: Input file path
            error: Error message
        """
        self.file_list.update_file_status(input_file, "failed")
        self.progress_widget.finish_conversion(success=False)

        # Parse FFmpeg error for better user feedback
        user_friendly_error = parse_ffmpeg_error(error)

        QMessageBox.critical(
            self,
            "Conversion Failed",
            f"Failed to convert:\n{Path(input_file).name}\n\n{user_friendly_error}"
        )

        logger.error(f"File {index + 1}/{total} failed: {Path(input_file).name} - {error}")

    def _on_progress_updated(self, index: int, progress_data: dict):
        """
        Handle progress update.

        Args:
            index: File index
            progress_data: Progress information
        """
        logger.debug(f"MainWindow received progress: {progress_data}")
        self.progress_widget.update_progress(progress_data)

    def _on_all_finished(self):
        """Handle all conversions finished."""
        self._is_converting = False
        self._update_button_states()

        self.batch_progress_widget.setVisible(False)
        self.progress_widget.set_status("All conversions completed!")

        # Show completion message
        QMessageBox.information(
            self,
            "Conversion Complete",
            f"All {self.file_list.get_file_count()} files have been converted successfully!\n\n"
            f"Output directory: {config.get_output_directory()}"
        )

        logger.info("All conversions completed successfully")

    def _on_batch_cancelled(self):
        """Handle batch conversion cancelled."""
        self._is_converting = False
        self._update_button_states()

        self.batch_progress_widget.setVisible(False)
        self.progress_widget.reset()

        logger.info("Batch conversion cancelled")

    def _on_settings_clicked(self):
        """Handle settings button click."""
        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self._on_settings_changed)
        dialog.exec()

    def _on_about_clicked(self):
        """Handle about button click."""
        dialog = AboutDialog(self)
        dialog.exec()

    def _on_settings_changed(self):
        """Handle settings changed."""
        # Update quick settings if it exists
        # if hasattr(self, 'quick_settings'):
        #     self.quick_settings.update_from_config()

        logger.info("Settings updated")

    def _update_button_states(self):
        """Update button enabled states based on current state."""
        has_files = self.file_list.get_file_count() > 0

        self.start_button.setEnabled(has_files and not self._is_converting)
        self.cancel_button.setEnabled(self._is_converting)
        self.drop_zone.set_enabled(not self._is_converting)

    def closeEvent(self, event):
        """
        Handle window close event.

        Args:
            event: Close event
        """
        if self._is_converting:
            reply = QMessageBox.question(
                self,
                "Conversion in Progress",
                "A conversion is in progress. Are you sure you want to quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

            # Cancel conversion
            if self.conversion_manager and self.conversion_manager.isRunning():
                self.conversion_manager.cancel()
                self.conversion_manager.wait()

        logger.info("Application closing")
        event.accept()
