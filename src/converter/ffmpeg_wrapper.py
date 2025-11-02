"""
FFmpeg wrapper for video conversion and analysis.
"""
import subprocess
import json
import re
import threading
from typing import Dict, Any, Callable, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import config
from utils.logger import logger


class FFmpegWrapper:
    """Wrapper class for FFmpeg operations."""

    @staticmethod
    def get_video_info(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get video information using ffprobe.

        Args:
            file_path: Path to video file

        Returns:
            Dictionary with video information or None on error
        """
        cmd = [
            config.FFPROBE_BINARY,
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]

        try:
            logger.debug(f"Running ffprobe on: {file_path}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                logger.error(f"ffprobe failed: {result.stderr}")
                return None

            info = json.loads(result.stdout)
            logger.debug(f"Video info retrieved for: {file_path}")
            return info

        except subprocess.TimeoutExpired:
            logger.error(f"ffprobe timeout for file: {file_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ffprobe output: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None

    @staticmethod
    def convert_video(
        input_file: str,
        output_file: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None
    ) -> bool:
        """
        Convert video using FFmpeg with progress tracking.

        Args:
            input_file: Input video file path
            output_file: Output video file path
            progress_callback: Optional callback for progress updates.
                              Called with dict containing 'frame', 'fps', 'time', 'speed', 'progress'
            error_callback: Optional callback for error messages
            cancel_check: Optional callback that returns True if conversion should be cancelled

        Returns:
            True if conversion successful, False otherwise
        """
        # Get video duration for progress calculation
        video_info = FFmpegWrapper.get_video_info(input_file)
        total_duration = None

        if video_info:
            try:
                format_info = video_info.get('format', {})
                total_duration = float(format_info.get('duration', 0))
                logger.info(f"Video duration: {total_duration:.2f} seconds")
            except (ValueError, TypeError):
                logger.warning("Could not determine video duration")

        # Build FFmpeg command
        cmd = config.get_ffmpeg_command_args(input_file, output_file)

        logger.info(f"Starting conversion: {input_file} -> {output_file}")
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # Read stderr in a separate thread to prevent blocking
            def read_stderr():
                for line in process.stderr:
                    line = line.strip()
                    if 'error' in line.lower() or 'failed' in line.lower():
                        logger.error(f"FFmpeg error: {line}")
                        if error_callback:
                            error_callback(line)

            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stderr_thread.start()

            # Parse progress output from stdout
            # Note: With -progress pipe:1, progress goes to stdout in key=value format
            logger.info("Reading progress from FFmpeg...")

            for line in process.stdout:
                # Check if we should cancel
                if cancel_check and cancel_check():
                    logger.info("Cancellation requested, terminating FFmpeg process")
                    process.terminate()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        logger.warning("FFmpeg didn't terminate gracefully, killing it")
                        process.kill()
                        process.wait()
                    return False

                line = line.strip()

                if not line:
                    continue

                # FFmpeg progress format with -progress pipe:1 is key=value pairs
                if '=' in line:
                    key, value = line.split('=', 1)
                    logger.debug(f"FFmpeg progress key: {key} = {value}")

                    if key == 'out_time_ms':
                        # Parse microseconds (despite the name, it's actually microseconds!)
                        try:
                            time_us = int(value)
                            current_time = time_us / 1000000.0  # Convert microseconds to seconds

                            progress_data = {
                                'time': current_time,
                                'time_formatted': FFmpegWrapper._format_time(current_time)
                            }

                            if total_duration and total_duration > 0:
                                progress_percent = (current_time / total_duration) * 100
                                progress_data['progress'] = min(progress_percent, 100.0)

                            if progress_callback:
                                logger.debug(f"Progress: {progress_percent:.1f}%")
                                progress_callback(progress_data)

                        except (ValueError, IndexError) as e:
                            logger.debug(f"Error parsing out_time_ms: {e}")

                    elif key == 'speed':
                        # Parse speed (e.g., "1.5x")
                        try:
                            speed_str = value.rstrip('x')
                            speed = float(speed_str)
                            if progress_callback:
                                progress_callback({'speed': speed})
                        except (ValueError, IndexError):
                            pass

                    elif key == 'bitrate':
                        # Parse bitrate (e.g., "1234.5kbits/s")
                        try:
                            # Remove "kbits/s" suffix and convert to Mbps
                            bitrate_str = value.replace('kbits/s', '').strip()
                            bitrate_kbps = float(bitrate_str)
                            bitrate_mbps = bitrate_kbps / 1000.0  # Convert to Mbps
                            logger.debug(f"Parsed bitrate: {bitrate_mbps:.1f} Mbps")
                            if progress_callback:
                                progress_callback({'bitrate_mbps': bitrate_mbps})
                        except (ValueError, IndexError) as e:
                            logger.debug(f"Error parsing bitrate: {e}")

            # Wait for process to complete
            return_code = process.wait()
            logger.info(f"FFmpeg process completed with code {return_code}")

            if return_code == 0:
                logger.info(f"Conversion successful: {output_file}")
                return True
            else:
                stderr_output = process.stderr.read() if process.stderr else ""
                logger.error(f"Conversion failed with return code {return_code}")
                logger.error(f"FFmpeg stderr: {stderr_output}")

                if error_callback:
                    error_callback(f"Conversion failed (code {return_code})")

                return False

        except subprocess.TimeoutExpired:
            logger.error("FFmpeg process timeout")
            if error_callback:
                error_callback("Conversion timeout")
            return False
        except Exception as e:
            logger.error(f"Error during conversion: {e}")
            if error_callback:
                error_callback(str(e))
            return False

    @staticmethod
    def _parse_progress_line(line: str, total_duration: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Parse FFmpeg progress output line.

        Args:
            line: Progress line from FFmpeg
            total_duration: Total video duration in seconds

        Returns:
            Dictionary with progress information or None
        """
        try:
            progress_data = {}

            # Extract frame number
            frame_match = re.search(r'frame=\s*(\d+)', line)
            if frame_match:
                progress_data['frame'] = int(frame_match.group(1))

            # Extract fps
            fps_match = re.search(r'fps=\s*(\d+\.?\d*)', line)
            if fps_match:
                progress_data['fps'] = float(fps_match.group(1))

            # Extract time (format: HH:MM:SS.ms)
            time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = float(time_match.group(3))
                current_time = hours * 3600 + minutes * 60 + seconds
                progress_data['time'] = current_time
                progress_data['time_formatted'] = f"{hours:02d}:{minutes:02d}:{int(seconds):02d}"

                # Calculate progress percentage if we have total duration
                if total_duration and total_duration > 0:
                    progress_percent = (current_time / total_duration) * 100
                    progress_data['progress'] = min(progress_percent, 100.0)

            # Extract speed
            speed_match = re.search(r'speed=\s*(\d+\.?\d*)x', line)
            if speed_match:
                progress_data['speed'] = float(speed_match.group(1))

            # Extract bitrate
            bitrate_match = re.search(r'bitrate=\s*(\d+\.?\d*)\s*kbits/s', line)
            if bitrate_match:
                progress_data['bitrate'] = float(bitrate_match.group(1))

            # Extract size
            size_match = re.search(r'size=\s*(\d+)kB', line)
            if size_match:
                progress_data['size_kb'] = int(size_match.group(1))

            return progress_data if progress_data else None

        except Exception as e:
            logger.debug(f"Error parsing progress line: {e}")
            return None

    @staticmethod
    def cancel_conversion(process: subprocess.Popen):
        """
        Cancel an ongoing conversion process.

        Args:
            process: The FFmpeg subprocess to terminate
        """
        try:
            logger.info("Cancelling conversion...")
            process.terminate()

            # Wait briefly for graceful termination
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                logger.warning("Force killing FFmpeg process")
                process.kill()

            logger.info("Conversion cancelled")

        except Exception as e:
            logger.error(f"Error cancelling conversion: {e}")

    @staticmethod
    def _format_time(seconds: float) -> str:
        """
        Format time in seconds to HH:MM:SS.

        Args:
            seconds: Time in seconds

        Returns:
            Formatted time string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
