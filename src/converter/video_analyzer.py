"""
Video analysis and metadata extraction.
"""
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from converter.ffmpeg_wrapper import FFmpegWrapper
from utils.logger import logger


class VideoAnalyzer:
    """Analyze video files and extract metadata."""

    @staticmethod
    def get_video_metadata(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Extract comprehensive video metadata.

        Args:
            file_path: Path to video file

        Returns:
            Dictionary with video metadata or None on error
        """
        info = FFmpegWrapper.get_video_info(file_path)

        if not info:
            return None

        try:
            metadata = {
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'file_size_bytes': Path(file_path).stat().st_size,
                'file_size_mb': Path(file_path).stat().st_size / (1024 * 1024),
            }

            # Extract format information
            format_info = info.get('format', {})
            metadata['duration'] = float(format_info.get('duration', 0))
            metadata['bit_rate'] = int(format_info.get('bit_rate', 0))
            metadata['format_name'] = format_info.get('format_name', 'unknown')

            # Find video stream
            video_stream = None
            audio_stream = None

            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video' and not video_stream:
                    video_stream = stream
                elif stream.get('codec_type') == 'audio' and not audio_stream:
                    audio_stream = stream

            # Extract video stream information
            if video_stream:
                metadata['width'] = video_stream.get('width', 0)
                metadata['height'] = video_stream.get('height', 0)
                metadata['resolution'] = f"{metadata['width']}x{metadata['height']}"
                metadata['codec'] = video_stream.get('codec_name', 'unknown')
                metadata['codec_long'] = video_stream.get('codec_long_name', 'unknown')
                metadata['fps'] = VideoAnalyzer._parse_frame_rate(video_stream.get('r_frame_rate', '0/1'))
                metadata['pixel_format'] = video_stream.get('pix_fmt', 'unknown')
            else:
                logger.warning(f"No video stream found in {file_path}")
                return None

            # Extract audio stream information
            if audio_stream:
                metadata['audio_codec'] = audio_stream.get('codec_name', 'unknown')
                metadata['audio_sample_rate'] = audio_stream.get('sample_rate', 0)
                metadata['audio_channels'] = audio_stream.get('channels', 0)
            else:
                metadata['audio_codec'] = 'none'
                metadata['audio_sample_rate'] = 0
                metadata['audio_channels'] = 0

            # Estimate output file size
            metadata['estimated_output_size_mb'] = VideoAnalyzer.estimate_output_size(metadata)

            logger.debug(f"Metadata extracted for {file_path}")
            return metadata

        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return None

    @staticmethod
    def _parse_frame_rate(frame_rate_str: str) -> float:
        """
        Parse frame rate from FFmpeg format (e.g., '30000/1001').

        Args:
            frame_rate_str: Frame rate string

        Returns:
            Frame rate as float
        """
        try:
            if '/' in frame_rate_str:
                num, denom = frame_rate_str.split('/')
                return float(num) / float(denom)
            else:
                return float(frame_rate_str)
        except (ValueError, ZeroDivisionError):
            return 0.0

    @staticmethod
    def estimate_output_size(metadata: Dict[str, Any]) -> float:
        """
        Estimate output file size based on video metadata.

        This is an approximation based on:
        - Video resolution
        - Duration
        - Target CRF (18 for high quality)
        - H.264 codec characteristics

        Args:
            metadata: Video metadata dictionary

        Returns:
            Estimated size in MB
        """
        try:
            duration = metadata.get('duration', 0)
            width = metadata.get('width', 0)
            height = metadata.get('height', 0)
            input_size_mb = metadata.get('file_size_mb', 0)

            if duration == 0 or width == 0 or height == 0:
                # Fallback: assume similar size
                return input_size_mb * 1.05

            # Calculate pixel count
            pixels = width * height

            # Estimate bitrate based on resolution and CRF 18
            # These are approximate values for H.264 with CRF 18
            if pixels <= 1280 * 720:  # 720p or less
                estimated_video_bitrate = 3000  # kbps
            elif pixels <= 1920 * 1080:  # 1080p
                estimated_video_bitrate = 6000  # kbps
            elif pixels <= 2560 * 1440:  # 1440p
                estimated_video_bitrate = 12000  # kbps
            else:  # 4K and above
                estimated_video_bitrate = 20000  # kbps

            # Audio bitrate (320 kbps AAC)
            audio_bitrate = 320  # kbps

            # Total bitrate
            total_bitrate = estimated_video_bitrate + audio_bitrate

            # Calculate size: (bitrate in kbps * duration in seconds) / 8 / 1024
            estimated_size_mb = (total_bitrate * duration) / 8 / 1024

            # Add 5% overhead for container
            estimated_size_mb *= 1.05

            logger.debug(f"Estimated output size: {estimated_size_mb:.2f} MB")
            return estimated_size_mb

        except Exception as e:
            logger.error(f"Error estimating output size: {e}")
            # Fallback: assume similar size to input
            return metadata.get('file_size_mb', 0) * 1.05

    @staticmethod
    def get_resolution_label(metadata: Dict[str, Any]) -> str:
        """
        Get human-readable resolution label (e.g., "1080p", "4K").

        Args:
            metadata: Video metadata dictionary

        Returns:
            Resolution label string
        """
        height = metadata.get('height', 0)

        if height >= 2160:
            return "4K"
        elif height >= 1440:
            return "1440p"
        elif height >= 1080:
            return "1080p"
        elif height >= 720:
            return "720p"
        elif height >= 480:
            return "480p"
        else:
            return f"{height}p"

    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in human-readable format.

        Args:
            seconds: Duration in seconds

        Returns:
            Formatted duration string (HH:MM:SS)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string (e.g., "2.5 GB")
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
