"""
About dialog for FrameConverter.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QDesktopServices
from PyQt6.QtCore import QUrl

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import config
from utils.logger import logger


class AboutDialog(QDialog):
    """About dialog showing app information and creator details."""

    def __init__(self, parent=None):
        """Initialize about dialog."""
        super().__init__(parent)
        self.setWindowTitle(f"About {config.APP_NAME}")
        self.setModal(True)
        self.setMinimumSize(700, 450)
        self.resize(750, 480)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(20)

        # Horizontal content layout (icon on left, info on right)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(32)

        # === LEFT SIDE: App Icon ===
        left_layout = QVBoxLayout()
        left_layout.addStretch()

        icon_path = Path(__file__).parent.parent / 'resources' / 'app_icon.png'
        if icon_path.exists():
            icon_label = QLabel()
            pixmap = QPixmap(str(icon_path))
            scaled_pixmap = pixmap.scaled(140, 140, Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
            left_layout.addWidget(icon_label)

        left_layout.addStretch()
        content_layout.addLayout(left_layout)

        # === RIGHT SIDE: App Info ===
        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)

        # App name and version
        name_label = QLabel(config.APP_NAME)
        name_label.setObjectName("aboutAppName")
        name_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.02em;
        """)
        right_layout.addWidget(name_label)

        # Version
        version_label = QLabel(f"Version {config.APP_VERSION}")
        version_label.setObjectName("aboutVersion")
        version_label.setStyleSheet("""
            font-size: 13px;
            opacity: 0.6;
            margin-bottom: 8px;
        """)
        right_layout.addWidget(version_label)

        # Description
        desc_text = ("Convert MP4 videos to MOV format optimized for DaVinci Resolve. "
                    "Fast, modern, and easy to use.")
        description = QLabel(desc_text)
        description.setWordWrap(True)
        description.setObjectName("aboutDescription")
        description.setStyleSheet("""
            font-size: 13px;
            opacity: 0.6;
            line-height: 1.5;
        """)
        right_layout.addWidget(description)

        right_layout.addSpacing(16)

        # Creator section
        creator_label = QLabel("Created by Pablo Navarro")
        creator_label.setObjectName("aboutCreator")
        creator_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 600;
        """)
        right_layout.addWidget(creator_label)

        # Company label
        company_label = QLabel(f"{config.ORGANIZATION}")
        company_label.setObjectName("aboutCompany")
        company_label.setStyleSheet("""
            font-size: 13px;
            opacity: 0.6;
            margin-top: 4px;
        """)
        right_layout.addWidget(company_label)

        right_layout.addSpacing(16)

        # Social buttons in horizontal layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)

        # X/Twitter button
        x_button = self._create_link_button("𝕏  Follow on X", "https://x.com/pablothethinker", "twitter")
        x_button.setFixedHeight(44)
        buttons_layout.addWidget(x_button)

        # Buy Me a Coffee button
        coffee_button = self._create_link_button("☕  Buy Me a Coffee", "https://buymeacoffee.com/pablothethinker", "coffee")
        coffee_button.setFixedHeight(44)
        buttons_layout.addWidget(coffee_button)

        buttons_layout.addStretch()
        right_layout.addLayout(buttons_layout)

        right_layout.addStretch()

        # Add right side to content layout
        content_layout.addLayout(right_layout, 1)

        # Add content to main layout
        main_layout.addLayout(content_layout)

        # Copyright
        copyright_label = QLabel(f"© 2025 {config.ORGANIZATION}. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setObjectName("aboutCopyright")
        copyright_label.setStyleSheet("""
            font-size: 11px;
            opacity: 0.5;
            margin-top: 16px;
        """)
        main_layout.addWidget(copyright_label)

        # Close button
        close_button = QPushButton("Close")
        close_button.setObjectName("closeButton")
        close_button.clicked.connect(self.accept)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setFixedHeight(36)
        close_button.setFixedWidth(100)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0A84FF;
            }
        """)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _create_link_button(self, text: str, url: str, button_type: str = "default") -> QPushButton:
        """
        Create a styled button that opens a URL.

        Args:
            text: Button text
            url: URL to open
            button_type: Type of button ("twitter", "coffee", or "default")

        Returns:
            QPushButton configured to open the URL
        """
        button = QPushButton(text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(lambda: self._open_url(url))

        # Style based on button type
        if button_type == "coffee":
            button.setStyleSheet("""
                QPushButton {
                    background-color: #FFDD00;
                    color: #000000;
                    border: none;
                    border-radius: 10px;
                    padding: 0px 20px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #FFE44D;
                }
                QPushButton:pressed {
                    background-color: #F5D000;
                }
            """)
        elif button_type == "twitter":
            button.setStyleSheet("""
                QPushButton {
                    background-color: #1DA1F2;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0px 20px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #3AB3FF;
                }
                QPushButton:pressed {
                    background-color: #0D8ECF;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0px 20px;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #0A84FF;
                }
                QPushButton:pressed {
                    background-color: #0070E0;
                }
            """)

        return button

    def _open_url(self, url: str):
        """
        Open URL in default browser.

        Args:
            url: URL to open
        """
        QDesktopServices.openUrl(QUrl(url))
        logger.info(f"Opening URL: {url}")
