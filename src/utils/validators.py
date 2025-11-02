"""
File validation utilities.
"""
import os
import shutil
from pathlib import Path
from typing import Tuple
from .config import config
from .logger import logger


def is_valid_video_file(file_path: str) -> Tuple[bool, str]:
    """
    Check if file is a valid video file for conversion.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "No file path provided"

    path = Path(file_path)

    # Check if file exists
    if not path.exists():
        logger.warning(f"File does not exist: {file_path}")
        return False, f"File not found: {path.name}\n\nThe file may have been moved or deleted."

    if not path.is_file():
        logger.warning(f"Path is not a file: {file_path}")
        return False, f"Invalid file: {path.name}\n\nThis appears to be a directory, not a file."

    # Check file extension
    if path.suffix.lower() not in config.SUPPORTED_INPUT_FORMATS:
        supported = ", ".join(config.SUPPORTED_INPUT_FORMATS)
        logger.warning(f"Unsupported file format: {path.suffix}")
        return False, (f"Unsupported file format: {path.suffix}\n\n"
                      f"Supported formats: {supported}")

    # Check if file is readable
    if not os.access(file_path, os.R_OK):
        logger.warning(f"File is not readable: {file_path}")
        return False, (f"Cannot read file: {path.name}\n\n"
                      "The file may be locked by another program or you don't have permission to read it.")

    # Check if file has content
    file_size = path.stat().st_size
    if file_size == 0:
        logger.warning(f"File is empty: {file_path}")
        return False, f"Empty file: {path.name}\n\nThe file has 0 bytes and cannot be converted."

    # Warn if file is very small (likely corrupted)
    if file_size < 1024:  # Less than 1 KB
        logger.warning(f"File is suspiciously small: {file_path} ({file_size} bytes)")
        return False, (f"File too small: {path.name}\n\n"
                      f"The file is only {file_size} bytes, which is unusually small for a video. "
                      "It may be corrupted.")

    return True, "Valid video file"


def check_disk_space(output_directory: str, estimated_size_bytes: int) -> Tuple[bool, str]:
    """
    Check if there's enough disk space for the output file.

    Args:
        output_directory: Directory where output will be saved
        estimated_size_bytes: Estimated output file size in bytes

    Returns:
        Tuple of (has_space, message)
    """
    try:
        stat = shutil.disk_usage(output_directory)
        available_bytes = stat.free

        # Add 10% buffer for safety
        required_bytes = int(estimated_size_bytes * 1.1)

        if available_bytes < required_bytes:
            available_gb = available_bytes / (1024 ** 3)
            required_gb = required_bytes / (1024 ** 3)
            message = f"Insufficient disk space. Available: {available_gb:.2f} GB, Required: {required_gb:.2f} GB"
            logger.error(message)
            return False, message

        return True, "Sufficient disk space available"

    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return True, "Could not verify disk space (proceeding anyway)"


def check_ffmpeg_available() -> Tuple[bool, str]:
    """
    Check if FFmpeg and ffprobe are available on the system.

    Returns:
        Tuple of (is_available, message)
    """
    import subprocess

    # Check ffmpeg
    try:
        result = subprocess.run(
            [config.FFMPEG_BINARY, '-version'],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            message = "FFmpeg is not working properly"
            logger.error(message)
            return False, message
    except FileNotFoundError:
        message = "FFmpeg is not installed. Please install FFmpeg to use this application."
        logger.error(message)
        return False, message
    except Exception as e:
        message = f"Error checking FFmpeg: {e}"
        logger.error(message)
        return False, message

    # Check ffprobe
    try:
        result = subprocess.run(
            [config.FFPROBE_BINARY, '-version'],
            capture_output=True,
            timeout=5
        )
        if result.returncode != 0:
            message = "ffprobe is not working properly"
            logger.error(message)
            return False, message
    except FileNotFoundError:
        message = "ffprobe is not installed. Please install FFmpeg (includes ffprobe)."
        logger.error(message)
        return False, message
    except Exception as e:
        message = f"Error checking ffprobe: {e}"
        logger.error(message)
        return False, message

    logger.info("FFmpeg and ffprobe are available")
    return True, "FFmpeg and ffprobe are available"


def get_output_filename(input_path: str, output_directory: str = None) -> str:
    """
    Generate output filename for converted video.

    Args:
        input_path: Input file path
        output_directory: Output directory. Uses config default if None.

    Returns:
        Full path to output file
    """
    input_file = Path(input_path)
    output_dir = Path(output_directory or config.get_output_directory())

    # Create output filename: input_name + .mov
    output_name = input_file.stem + config.OUTPUT_FORMAT
    output_path = output_dir / output_name

    # If file exists, add number suffix
    counter = 1
    while output_path.exists():
        output_name = f"{input_file.stem}_{counter}{config.OUTPUT_FORMAT}"
        output_path = output_dir / output_name
        counter += 1

    return str(output_path)


def validate_conversion_request(input_file: str, output_directory: str = None) -> Tuple[bool, str]:
    """
    Validate all requirements for a conversion request.

    Args:
        input_file: Input video file path
        output_directory: Output directory

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if input file is valid
    is_valid, message = is_valid_video_file(input_file)
    if not is_valid:
        return False, message

    # Check FFmpeg availability
    ffmpeg_available, message = check_ffmpeg_available()
    if not ffmpeg_available:
        return False, message

    # Check output directory
    output_dir = output_directory or config.get_output_directory()
    output_path = Path(output_dir)

    # Create directory if it doesn't exist
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        return False, (f"Permission denied creating output directory:\n{output_dir}\n\n"
                      "Please choose a different location or run with appropriate permissions.")
    except Exception as e:
        return False, f"Cannot create output directory:\n{output_dir}\n\nError: {e}"

    # Check if output directory is writable
    if not os.access(output_dir, os.W_OK):
        return False, (f"Output directory is not writable:\n{output_dir}\n\n"
                      "Please choose a different location or check folder permissions.")

    return True, "Validation successful"


def parse_ffmpeg_error(error_output: str) -> str:
    """
    Parse FFmpeg error output and provide user-friendly error messages.

    Args:
        error_output: FFmpeg error output

    Returns:
        User-friendly error message
    """
    error_lower = error_output.lower()

    # Common FFmpeg errors with helpful messages
    if "no such file or directory" in error_lower:
        return ("File not found.\n\n"
                "The input file may have been moved or deleted during conversion.")

    if "permission denied" in error_lower:
        return ("Permission denied.\n\n"
                "The file may be locked by another program or you don't have permission to access it.")

    if "invalid data" in error_lower or "invalid argument" in error_lower:
        return ("Invalid or corrupted video file.\n\n"
                "The file may be damaged or in an unsupported format.")

    if "codec not found" in error_lower or "unknown encoder" in error_lower:
        return ("Required video codec not available.\n\n"
                "Your FFmpeg installation may be missing required codecs.")

    if "disk full" in error_lower or "no space left" in error_lower:
        return ("Not enough disk space.\n\n"
                "Free up some disk space and try again.")

    if "out of memory" in error_lower or "cannot allocate memory" in error_lower:
        return ("Out of memory.\n\n"
                "Close some applications and try again.")

    if "could not open" in error_lower and "output" in error_lower:
        return ("Cannot create output file.\n\n"
                "Check that the output directory is writable and has enough space.")

    if "timeout" in error_lower:
        return ("Conversion timeout.\n\n"
                "The file may be too large or complex to convert.")

    # If no specific error matched, return a generic helpful message
    return ("Video conversion failed.\n\n"
            "The file may be corrupted, in an incompatible format, or there may be a system issue.\n\n"
            f"Technical details: {error_output[:200]}")
