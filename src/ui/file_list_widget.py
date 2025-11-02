"""
File list widget for displaying queued video files.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from converter.video_analyzer import VideoAnalyzer
from utils.logger import logger


class FileListWidget(QWidget):
    """
    Widget for displaying and managing the file conversion queue.

    Signals:
        file_removed: Emitted with file path when a file is removed
        clear_all: Emitted when all files are cleared
    """

    file_removed = pyqtSignal(str)
    clear_all = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize file list widget."""
        super().__init__(parent)
        self.file_items = {}  # Map file_path -> QListWidgetItem
        self.file_metadata = {}  # Map file_path -> metadata dict
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout()
        layout.setSpacing(12)  # 1.5 × 8pt base

        # Header with title and clear button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)  # 2 × 8pt base

        self.title_label = QLabel("Files to Convert:")
        self.title_label.setObjectName("fileListTitle")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        self.clear_button = QPushButton("Clear All")
        self.clear_button.setObjectName("clearAllButton")
        self.clear_button.clicked.connect(self._on_clear_all)
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout.addWidget(self.clear_button)

        layout.addLayout(header_layout)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("fileList")
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)
        self._update_title()

    def add_files(self, file_paths: list):
        """
        Add files to the queue.

        Args:
            file_paths: List of file paths to add
        """
        for file_path in file_paths:
            if file_path not in self.file_items:
                self._add_file_item(file_path)

        self._update_title()

    def _add_file_item(self, file_path: str):
        """
        Add a single file item to the list.

        Args:
            file_path: Path to the file
        """
        # Analyze video
        logger.info(f"Analyzing video: {file_path}")
        metadata = VideoAnalyzer.get_video_metadata(file_path)

        if not metadata:
            logger.error(f"Failed to analyze video: {file_path}")
            return

        # Store metadata
        self.file_metadata[file_path] = metadata

        # Create list item
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, file_path)

        # Create custom widget for the item
        item_widget = self._create_file_item_widget(file_path, metadata)

        # Add to list
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)
        item.setSizeHint(item_widget.sizeHint())

        # Store reference
        self.file_items[file_path] = item

        logger.info(f"Added file to queue: {file_path}")

    def _create_file_item_widget(self, file_path: str, metadata: dict) -> QWidget:
        """
        Create custom widget for a file item.

        Args:
            file_path: Path to the file
            metadata: Video metadata dictionary

        Returns:
            QWidget for the list item
        """
        widget = QWidget()
        widget.setStyleSheet("")  # Ensure widget inherits parent styles
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 8, 12, 8)  # Apple HIG: comfortable padding
        layout.setSpacing(12)  # 1.5 × 8pt base

        # Status icon (pending by default)
        status_label = QLabel("⏸")
        status_label.setObjectName("statusIcon")
        status_label.setProperty("status", "pending")
        layout.addWidget(status_label)

        # File information
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)  # Tight spacing for related text

        # File name
        name_label = QLabel(metadata['file_name'])
        name_label.setObjectName("fileName")
        name_label.setWordWrap(False)
        name_label.setTextFormat(Qt.TextFormat.PlainText)
        info_layout.addWidget(name_label)

        # Details (resolution, size, estimated output)
        resolution_label = VideoAnalyzer.get_resolution_label(metadata)
        input_size = VideoAnalyzer.format_file_size(metadata['file_size_bytes'])
        estimated_output = f"{metadata['estimated_output_size_mb']:.1f} MB"

        details_text = f"{resolution_label} • {metadata['codec']} • {input_size} → ~{estimated_output}"
        details_label = QLabel(details_text)
        details_label.setObjectName("fileDetails")
        details_label.setWordWrap(False)
        details_label.setTextFormat(Qt.TextFormat.PlainText)
        info_layout.addWidget(details_label)

        layout.addLayout(info_layout, stretch=1)

        # Remove button
        remove_button = QPushButton("×")
        remove_button.setObjectName("removeFileButton")
        remove_button.setFixedSize(24, 24)
        remove_button.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_button.clicked.connect(lambda: self._on_remove_file(file_path))
        layout.addWidget(remove_button)

        widget.setLayout(layout)
        return widget

    def _on_remove_file(self, file_path: str):
        """
        Handle file removal.

        Args:
            file_path: Path to the file to remove
        """
        if file_path in self.file_items:
            item = self.file_items[file_path]
            row = self.list_widget.row(item)
            self.list_widget.takeItem(row)

            del self.file_items[file_path]
            if file_path in self.file_metadata:
                del self.file_metadata[file_path]

            self.file_removed.emit(file_path)
            self._update_title()
            logger.info(f"Removed file from queue: {file_path}")

    def _on_clear_all(self):
        """Handle clear all button click."""
        self.list_widget.clear()
        self.file_items.clear()
        self.file_metadata.clear()
        self.clear_all.emit()
        self._update_title()
        logger.info("Cleared all files from queue")

    def update_file_status(self, file_path: str, status: str):
        """
        Update the status icon for a file.

        Args:
            file_path: Path to the file
            status: Status string ("pending", "processing", "completed", "failed")
        """
        if file_path not in self.file_items:
            return

        item = self.file_items[file_path]
        widget = self.list_widget.itemWidget(item)

        if widget:
            # Find status label
            status_label = widget.findChild(QLabel, "statusIcon")
            if status_label:
                # Update icon based on status
                icons = {
                    "pending": "⏸",
                    "processing": "⏳",
                    "completed": "✓",
                    "failed": "✗"
                }
                status_label.setText(icons.get(status, "⏸"))
                status_label.setProperty("status", status)

                # Force style refresh
                status_label.style().unpolish(status_label)
                status_label.style().polish(status_label)

    def get_file_count(self) -> int:
        """
        Get the number of files in the queue.

        Returns:
            Number of files
        """
        return len(self.file_items)

    def get_file_list(self) -> list:
        """
        Get list of all file paths in the queue.

        Returns:
            List of file paths
        """
        return list(self.file_items.keys())

    def get_file_metadata(self, file_path: str) -> dict:
        """
        Get metadata for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            Metadata dictionary or None
        """
        return self.file_metadata.get(file_path)

    def _update_title(self):
        """Update the title label with file count."""
        count = self.get_file_count()
        if count == 0:
            self.title_label.setText("Files to Convert:")
        elif count == 1:
            self.title_label.setText("Files to Convert: (1 file)")
        else:
            self.title_label.setText(f"Files to Convert: ({count} files)")

        self.clear_button.setEnabled(count > 0)
