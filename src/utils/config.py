"""
Application configuration and settings.
"""
import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Application configuration manager."""

    # Application info
    APP_NAME = "FrameConverter"
    APP_VERSION = "1.0.0"
    ORGANIZATION = "Kyron Industries"

    # Quality presets optimized for DaVinci Resolve (based on 2025 research)
    QUALITY_PRESETS = {
        "fast": {
            "name": "Fast",
            "preset": "faster",
            "crf": 23,
            "tune": "fastdecode",
            "gop": 1,
            "description": "Faster encoding, optimized for editing"
        },
        "balanced": {
            "name": "Balanced",
            "preset": "medium",
            "crf": 20,
            "tune": "fastdecode",
            "gop": 1,
            "description": "Good balance of speed and quality"
        },
        "high": {
            "name": "High Quality (DaVinci Optimized)",
            "preset": "slow",
            "crf": 17,
            "tune": "fastdecode",
            "gop": 1,
            "description": "Best quality, optimized for DaVinci Resolve"
        },
        "gpu_fast": {
            "name": "GPU Accelerated - Fast",
            "preset": "p4",  # NVENC preset
            "crf": 23,
            "description": "Hardware accelerated, very fast"
        }
    }

    # Hardware acceleration options
    HARDWARE_ACCELERATION = {
        "nvenc": {
            "name": "NVIDIA NVENC",
            "encoder": "h264_nvenc",
            "check_cmd": "ffmpeg -encoders 2>/dev/null | grep nvenc"
        },
        "vaapi": {
            "name": "Intel/AMD VAAPI",
            "encoder": "h264_vaapi",
            "check_cmd": "ffmpeg -encoders 2>/dev/null | grep vaapi"
        },
        "none": {
            "name": "Software (CPU)",
            "encoder": "libx264",
            "check_cmd": None
        }
    }

    # Default conversion settings (as per PROJECT_PLAN.md)
    DEFAULT_VIDEO_CODEC = "libx264"
    DEFAULT_PRESET = "slow"
    DEFAULT_CRF = 18
    DEFAULT_AUDIO_CODEC = "aac"
    DEFAULT_AUDIO_BITRATE = "320k"
    DEFAULT_CONTAINER = ".mov"

    # FFmpeg settings
    FFMPEG_BINARY = "ffmpeg"
    FFPROBE_BINARY = "ffprobe"

    # File validation
    SUPPORTED_INPUT_FORMATS = [".mp4"]
    OUTPUT_FORMAT = ".mov"

    # UI settings
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    WINDOW_DEFAULT_WIDTH = 900
    WINDOW_DEFAULT_HEIGHT = 700

    # Color scheme (from PROJECT_PLAN.md)
    COLORS = {
        "primary": "#2E86AB",      # Blue - professional, trustworthy
        "success": "#06D6A0",      # Green - completion
        "warning": "#F77F00",      # Orange - processing
        "error": "#EF476F",        # Red - errors
        "background": "#FCFCFC",   # Light gray
        "text": "#2D3142",         # Dark gray
        "drop_zone": "#E8F4F8"     # Light blue tint
    }

    def __init__(self):
        """Initialize configuration with user preferences."""
        self.config_dir = Path.home() / '.video-converter'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Default output directory
        self.output_directory = str(Path.home() / 'Videos' / 'Converted')

        # Current quality preset
        self.current_preset = "high"

        # Advanced settings
        self.custom_crf = None  # If set, overrides preset CRF
        self.custom_preset = None  # If set, overrides preset

        # Hardware acceleration
        self.hardware_accel = None  # Will be auto-detected
        self.use_gpu = False  # Enable GPU acceleration if available

        # Theme preference
        self.theme = "light"  # Options: "light" or "dark"

    def get_output_directory(self) -> str:
        """Get the output directory, creating it if needed."""
        output_path = Path(self.output_directory)
        output_path.mkdir(parents=True, exist_ok=True)
        return str(output_path)

    def set_output_directory(self, directory: str):
        """Set the output directory."""
        self.output_directory = directory

    def get_preset_settings(self, preset_name: str = None) -> Dict[str, Any]:
        """
        Get FFmpeg settings for a quality preset.

        Args:
            preset_name: Preset name (fast/balanced/high). Uses current if None.

        Returns:
            Dictionary with preset settings
        """
        if preset_name is None:
            preset_name = self.current_preset

        preset = self.QUALITY_PRESETS.get(preset_name, self.QUALITY_PRESETS["high"])

        return {
            "video_codec": self.DEFAULT_VIDEO_CODEC,
            "preset": self.custom_preset or preset["preset"],
            "crf": self.custom_crf or preset["crf"],
            "audio_codec": self.DEFAULT_AUDIO_CODEC,
            "audio_bitrate": self.DEFAULT_AUDIO_BITRATE,
        }

    def set_quality_preset(self, preset_name: str):
        """Set the current quality preset."""
        if preset_name in self.QUALITY_PRESETS:
            self.current_preset = preset_name

    def set_custom_crf(self, crf: int):
        """Set custom CRF value (0-51)."""
        if 0 <= crf <= 51:
            self.custom_crf = crf

    def reset_custom_settings(self):
        """Reset custom settings to use presets."""
        self.custom_crf = None
        self.custom_preset = None

    def detect_hardware_acceleration(self) -> str:
        """
        Detect available hardware acceleration.

        Returns:
            Hardware acceleration type ('nvenc', 'vaapi', or 'none')
        """
        import subprocess

        # Check for NVENC
        try:
            result = subprocess.run(
                ['ffmpeg', '-encoders'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if 'h264_nvenc' in result.stdout:
                return 'nvenc'
            elif 'h264_vaapi' in result.stdout:
                return 'vaapi'
        except:
            pass

        return 'none'

    def get_ffmpeg_command_args(self, input_file: str, output_file: str) -> list:
        """
        Build FFmpeg command arguments based on current settings.
        Now includes DaVinci Resolve optimizations and GPU acceleration.

        Args:
            input_file: Input video file path
            output_file: Output video file path

        Returns:
            List of command arguments
        """
        settings = self.get_preset_settings()
        preset_config = self.QUALITY_PRESETS.get(self.current_preset, self.QUALITY_PRESETS["high"])

        # Auto-detect hardware acceleration if not set
        if self.hardware_accel is None:
            self.hardware_accel = self.detect_hardware_acceleration()

        # Use GPU if enabled and available
        if self.use_gpu and self.hardware_accel != 'none':
            encoder = self.HARDWARE_ACCELERATION[self.hardware_accel]['encoder']
        else:
            encoder = settings['video_codec']

        cmd = [
            self.FFMPEG_BINARY,
            '-i', input_file,
            '-c:v', encoder,
            '-preset', settings['preset'],
        ]

        # Add CRF for software encoding, or quality for hardware encoding
        if encoder == 'libx264':
            cmd.extend(['-crf', str(settings['crf'])])
            # Add DaVinci Resolve optimizations (from research)
            if 'tune' in preset_config:
                cmd.extend(['-tune', preset_config['tune']])
            if 'gop' in preset_config:
                cmd.extend(['-g', str(preset_config['gop'])])
            # Force yuv420p for compatibility
            cmd.extend(['-pix_fmt', 'yuv420p'])
        elif encoder == 'h264_nvenc':
            cmd.extend(['-cq', str(settings['crf'])])  # NVENC uses -cq instead of -crf
            cmd.extend(['-rc', 'vbr'])  # Variable bitrate
        elif encoder == 'h264_vaapi':
            cmd.extend(['-qp', str(settings['crf'])])  # VAAPI uses -qp

        # Audio settings
        cmd.extend([
            '-c:a', settings['audio_codec'],
            '-b:a', settings['audio_bitrate'],
            '-movflags', '+faststart',
            '-progress', 'pipe:1',
            '-y', output_file
        ])

        return cmd


# Global configuration instance
config = Config()
