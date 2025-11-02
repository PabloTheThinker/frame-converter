"""
Drag and drop zone widget for video files.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import config
from utils.validators import is_valid_video_file
from utils.logger import logger


class DropZone(QWidget):
    """
    Widget for drag-and-drop and file selection.

    Signals:
        files_dropped: Emitted with list of valid file paths when files are dropped/selected
    """

    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        """Initialize drop zone widget."""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._is_dragging = False
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)  # Apple HIG: 2 × 8pt base
        layout.setContentsMargins(24, 24, 24, 24)  # 3 × 8pt base

        # Main label
        self.label = QLabel("Drag & Drop Video Files Here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("dropZoneLabel")
        self.label.setToolTip("Drag and drop MP4 files here to add them to the conversion queue")
        layout.addWidget(self.label)

        # "or" text
        or_label = QLabel("or")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        or_label.setObjectName("dropZoneOrLabel")
        layout.addWidget(or_label)

        # Browse button
        self.browse_button = QPushButton("Browse Files")
        self.browse_button.setObjectName("dropZoneBrowseButton")
        self.browse_button.setToolTip("Click to select MP4 video files from your computer")
        self.browse_button.clicked.connect(self._on_browse_clicked)
        self.browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.browse_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Supported format label
        format_label = QLabel("Supported format: MP4")
        format_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        format_label.setObjectName("dropZoneFormatLabel")
        layout.addWidget(format_label)

        self.setLayout(layout)
        self.setObjectName("dropZone")

        # Set minimum size
        self.setMinimumHeight(200)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        Handle drag enter event.

        Args:
            event: Drag enter event
        """
        if event.mimeData().hasUrls():
            # Check if at least one URL is a valid video file
            has_valid_file = False
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.mp4'):
                    has_valid_file = True
                    break

            if has_valid_file:
                event.acceptProposedAction()
                self._is_dragging = True
                self._update_style()
                logger.debug("Drag enter accepted")
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """
        Handle drag leave event.

        Args:
            event: Drag leave event
        """
        self._is_dragging = False
        self._update_style()
        logger.debug("Drag leave")

    def dropEvent(self, event: QDropEvent):
        """
        Handle drop event.

        Args:
            event: Drop event
        """
        self._is_dragging = False
        self._update_style()

        files = []
        invalid_files = []
        error_messages = {}

        for url in event.mimeData().urls():
            file_path = url.toLocalFile()

            # Validate file
            is_valid, message = is_valid_video_file(file_path)
            if is_valid:
                files.append(file_path)
                logger.info(f"File dropped: {file_path}")
            else:
                file_name = Path(file_path).name
                invalid_files.append(file_name)
                error_messages[file_name] = message
                logger.warning(f"Invalid file dropped: {file_path} - {message}")

        if files:
            self.files_dropped.emit(files)
            event.acceptProposedAction()

        if invalid_files:
            # Show detailed error message for the first invalid file
            first_invalid = invalid_files[0]
            error_msg = error_messages[first_invalid]

            if len(invalid_files) > 1:
                error_msg += f"\n\n(And {len(invalid_files) - 1} other file(s) were also invalid)"

            QMessageBox.warning(
                self,
                "Invalid File",
                error_msg
            )

    def _on_browse_clicked(self):
        """Handle browse button click."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("MP4 Videos (*.mp4)")
        file_dialog.setWindowTitle("Select Video Files")

        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            valid_files = []
            invalid_files = []
            error_messages = {}

            for file_path in files:
                is_valid, message = is_valid_video_file(file_path)
                if is_valid:
                    valid_files.append(file_path)
                else:
                    file_name = Path(file_path).name
                    invalid_files.append(file_name)
                    error_messages[file_name] = message

            if valid_files:
                logger.info(f"Files selected via browse: {len(valid_files)} files")
                self.files_dropped.emit(valid_files)

            if invalid_files:
                # Show detailed error message
                first_invalid = invalid_files[0]
                error_msg = error_messages[first_invalid]

                if len(invalid_files) > 1:
                    error_msg += f"\n\n(And {len(invalid_files) - 1} other file(s) were also invalid)"

                QMessageBox.warning(
                    self,
                    "Invalid File",
                    error_msg
                )

    def _update_style(self):
        """Update widget style based on drag state."""
        # This will be handled by QSS, but we can set properties
        self.setProperty("dragging", self._is_dragging)
        # Force style refresh
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def set_enabled(self, enabled: bool):
        """
        Enable or disable the drop zone.

        Args:
            enabled: Whether to enable the drop zone
        """
        self.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
        self.setAcceptDrops(enabled)
