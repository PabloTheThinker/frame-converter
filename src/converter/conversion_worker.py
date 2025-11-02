"""
Background worker for video conversion.
"""
import sys
from pathlib import Path
from typing import Dict, Any
from PyQt6.QtCore import QThread, pyqtSignal, QEventLoop

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from converter.ffmpeg_wrapper import FFmpegWrapper
from utils.logger import logger
from utils.validators import get_output_filename


class ConversionWorker(QThread):
    """
    Background thread worker for video conversion.

    Signals:
        progress_updated: Emitted with progress data dictionary
        conversion_started: Emitted when conversion starts with (input_file, output_file)
        conversion_finished: Emitted when conversion completes successfully with output_file
        conversion_failed: Emitted when conversion fails with error_message
        conversion_cancelled: Emitted when conversion is cancelled
    """

    # Signals
    progress_updated = pyqtSignal(dict)
    conversion_started = pyqtSignal(str, str)
    conversion_finished = pyqtSignal(str)
    conversion_failed = pyqtSignal(str, str)  # input_file, error_message
    conversion_cancelled = pyqtSignal()

    def __init__(self, input_file: str, output_file: str = None):
        """
        Initialize conversion worker.

        Args:
            input_file: Path to input video file
            output_file: Path to output file. If None, generates automatically.
        """
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file or get_output_filename(input_file)
        self._is_cancelled = False

    def run(self):
        """Run the conversion in background thread."""
        try:
            logger.info(f"Conversion worker started for: {self.input_file}")
            self.conversion_started.emit(self.input_file, self.output_file)

            # Run conversion with callbacks
            success = FFmpegWrapper.convert_video(
                input_file=self.input_file,
                output_file=self.output_file,
                progress_callback=self._on_progress,
                error_callback=self._on_error,
                cancel_check=lambda: self._is_cancelled
            )

            if self._is_cancelled:
                logger.info("Conversion was cancelled")
                self.conversion_cancelled.emit()
            elif success:
                logger.info(f"Conversion completed: {self.output_file}")
                self.conversion_finished.emit(self.output_file)
            else:
                error_msg = "Conversion failed"
                logger.error(error_msg)
                self.conversion_failed.emit(self.input_file, error_msg)

        except Exception as e:
            error_msg = f"Unexpected error during conversion: {str(e)}"
            logger.error(error_msg)
            self.conversion_failed.emit(self.input_file, error_msg)

    def _on_progress(self, progress_data: Dict[str, Any]):
        """
        Handle progress updates from FFmpeg.

        Args:
            progress_data: Progress information dictionary
        """
        if not self._is_cancelled:
            logger.debug(f"Worker emitting progress: {progress_data}")
            self.progress_updated.emit(progress_data)

    def _on_error(self, error_message: str):
        """
        Handle error messages from FFmpeg.

        Args:
            error_message: Error message string
        """
        logger.error(f"FFmpeg error: {error_message}")

    def cancel(self):
        """Cancel the conversion."""
        logger.info("Cancelling conversion...")
        self._is_cancelled = True
        self.requestInterruption()


class BatchConversionManager(QThread):
    """
    Manager for batch conversion of multiple files.

    Processes files one at a time to avoid system overload.

    Signals:
        file_started: Emitted when a file starts converting (index, total, input_file)
        file_finished: Emitted when a file finishes (index, total, output_file)
        file_failed: Emitted when a file fails (index, total, input_file, error)
        progress_updated: Emitted with progress for current file
        all_finished: Emitted when all conversions complete
        batch_cancelled: Emitted when batch is cancelled
    """

    # Signals
    file_started = pyqtSignal(int, int, str)  # index, total, input_file
    file_finished = pyqtSignal(int, int, str)  # index, total, output_file
    file_failed = pyqtSignal(int, int, str, str)  # index, total, input_file, error
    progress_updated = pyqtSignal(int, dict)  # index, progress_data
    all_finished = pyqtSignal()
    batch_cancelled = pyqtSignal()

    def __init__(self, file_list: list):
        """
        Initialize batch conversion manager.

        Args:
            file_list: List of input file paths to convert
        """
        super().__init__()
        self.file_list = file_list
        self.current_worker = None
        self._is_cancelled = False

    def run(self):
        """Run batch conversion."""
        try:
            total_files = len(self.file_list)
            logger.info(f"Starting batch conversion of {total_files} files")

            for index, input_file in enumerate(self.file_list):
                if self._is_cancelled:
                    logger.info("Batch conversion cancelled")
                    self.batch_cancelled.emit()
                    return

                logger.info(f"Processing file {index + 1}/{total_files}: {input_file}")
                self.file_started.emit(index, total_files, input_file)

                # Create output filename
                output_file = get_output_filename(input_file)

                # Create and run worker for this file
                self.current_worker = ConversionWorker(input_file, output_file)

                success = False
                error_message = ""

                # Define callbacks BEFORE connecting signals
                def on_finished(output):
                    nonlocal success
                    success = True
                    logger.info(f"Batch manager: File finished callback triggered for {output}")

                def on_failed(inp, error):
                    nonlocal success, error_message
                    success = False
                    error_message = error
                    logger.error(f"Batch manager: File failed callback triggered: {error}")

                # Connect ALL signals BEFORE starting the thread
                self.current_worker.conversion_started.connect(
                    lambda inp, out: None  # Already emitted file_started
                )
                self.current_worker.conversion_finished.connect(on_finished)
                self.current_worker.conversion_failed.connect(on_failed)

                # Progress forwarding with logging
                def forward_progress(data, idx=index):
                    logger.debug(f"BatchManager forwarding progress for file {idx}: {data}")
                    self.progress_updated.emit(idx, data)

                self.current_worker.progress_updated.connect(forward_progress)

                # Start worker and wait for completion using event loop
                # This allows signals to be processed while waiting
                loop = QEventLoop()
                self.current_worker.finished.connect(loop.quit)
                self.current_worker.start()
                loop.exec()  # Process events while waiting

                logger.info(f"Worker thread finished for file {index + 1}/{total_files}")

                if self._is_cancelled:
                    logger.info("Batch conversion cancelled")
                    self.batch_cancelled.emit()
                    return

                if success:
                    self.file_finished.emit(index, total_files, output_file)
                else:
                    self.file_failed.emit(index, total_files, input_file, error_message)

            logger.info("Batch conversion completed")
            self.all_finished.emit()

        except Exception as e:
            logger.error(f"Error in batch conversion: {e}")

    def cancel(self):
        """Cancel the batch conversion."""
        logger.info("Cancelling batch conversion...")
        self._is_cancelled = True

        # Cancel current worker if running
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker.wait()

        self.requestInterruption()
