"""
Video Converter GUI - Main Entry Point

A user-friendly application for converting MP4 videos to MOV format
optimized for DaVinci Resolve video editing.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ui.main_window import MainWindow
from utils.config import config
from utils.logger import logger


def load_stylesheet(app: QApplication, theme: str = None) -> None:
    """
    Load and apply the application stylesheet based on theme.

    Args:
        app: QApplication instance
        theme: Theme name ("light" or "dark"). Uses config if None.
    """
    try:
        # Use config theme if not specified
        if theme is None:
            theme = config.theme

        # Select stylesheet file based on theme
        if theme == "dark":
            stylesheet_file = 'styles_dark.qss'
        else:
            stylesheet_file = 'styles.qss'

        stylesheet_path = Path(__file__).parent / 'resources' / stylesheet_file

        if stylesheet_path.exists():
            with open(stylesheet_path, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
                app.setStyleSheet(stylesheet)
                logger.info(f"Stylesheet loaded successfully: {theme} mode")
        else:
            logger.warning(f"Stylesheet not found: {stylesheet_path}")

    except Exception as e:
        logger.error(f"Failed to load stylesheet: {e}")


def main():
    """Main application entry point."""
    # Create application
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    app.setOrganizationName(config.ORGANIZATION)

    # Set application icon
    icon_path = Path(__file__).parent / 'resources' / 'app_icon.png'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
        logger.info(f"Application icon set: {icon_path}")

    # Note: High DPI scaling is enabled by default in PyQt6

    # Load stylesheet
    load_stylesheet(app)

    # Create and show main window
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    window = MainWindow()
    window.show()

    # Run application
    exit_code = app.exec()

    logger.info(f"Application exited with code {exit_code}")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
