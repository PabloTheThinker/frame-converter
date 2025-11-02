"""
Logging configuration for Video Converter application.
"""
import logging
import os
from pathlib import Path


def setup_logger(name: str = "VideoConverter", log_file: str = None) -> logging.Logger:
    """
    Set up application logger with console and file handlers.

    Args:
        name: Logger name
        log_file: Optional log file path. If None, creates logs directory in home

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if logger already exists
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (DEBUG and above)
    if log_file is None:
        # Create logs directory in user's home
        log_dir = Path.home() / '.video-converter' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / 'video_converter.log'

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info(f"Logger initialized. Log file: {log_file}")

    return logger


# Create default logger instance
logger = setup_logger()
