"""
Settings dialog for conversion options.
"""
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSpinBox, QFileDialog,
    QLineEdit, QGroupBox, QRadioButton, QButtonGroup, QCheckBox,
    QWidget, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config import config
from utils.logger import logger


class SettingsDialog(QDialog):
    """
    Dialog for configuring conversion settings.

    Signals:
        settings_changed: Emitted when settings are saved
    """

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize settings dialog."""
        super().__init__(parent)
        self.setWindowTitle("Conversion Settings")
        self.setModal(True)
        # Stable window that fits all content without scrolling
        self.setMinimumSize(1500, 580)
        self.resize(1500, 600)
        self.setFixedHeight(600)  # Fixed height - no scrolling needed
        self._setup_ui()
        self._load_current_settings()

    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout - Compact horizontal design
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(28, 24, 28, 24)
        main_layout.setSpacing(20)

        # Content layout - no scroll area needed
        content_layout = QGridLayout()
        content_layout.setHorizontalSpacing(40)  # Spacing between columns
        content_layout.setVerticalSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # === COLUMN 1: Quality & Appearance ===
        col1_layout = QVBoxLayout()
        col1_layout.setSpacing(20)  # Section spacing

        # Quality preset section
        preset_group = QGroupBox("Quality Preset")
        preset_group.setMinimumWidth(400)  # Ensure enough space for text
        preset_layout = QVBoxLayout()
        preset_layout.setSpacing(10)
        preset_layout.setContentsMargins(16, 16, 16, 16)

        self.preset_button_group = QButtonGroup()

        for preset_id, preset_data in config.QUALITY_PRESETS.items():
            radio = QRadioButton(preset_data['name'])
            radio.setProperty("preset_id", preset_id)
            radio.setMinimumWidth(350)  # Ensure text doesn't wrap

            # Add description as tooltip
            description = f"{preset_data['description']}\n"
            description += f"Preset: {preset_data['preset']}, CRF: {preset_data['crf']}"
            radio.setToolTip(description)

            self.preset_button_group.addButton(radio)
            preset_layout.addWidget(radio)

        preset_group.setLayout(preset_layout)
        col1_layout.addWidget(preset_group)

        # Appearance section
        appearance_group = QGroupBox("Appearance")
        appearance_group.setMinimumWidth(400)  # Ensure enough space for text
        appearance_layout = QVBoxLayout()
        appearance_layout.setSpacing(12)
        appearance_layout.setContentsMargins(16, 16, 16, 16)

        # Theme selection
        self.theme_button_group = QButtonGroup()

        light_radio = QRadioButton("☀️  Light Mode")
        light_radio.setProperty("theme_id", "light")
        light_radio.setToolTip("Classic light theme with bright colors")
        light_radio.setMinimumWidth(200)  # Ensure text doesn't wrap
        self.theme_button_group.addButton(light_radio)
        appearance_layout.addWidget(light_radio)

        dark_radio = QRadioButton("🌙  Dark Mode")
        dark_radio.setProperty("theme_id", "dark")
        dark_radio.setToolTip("Modern dark theme, easier on the eyes")
        dark_radio.setMinimumWidth(200)  # Ensure text doesn't wrap
        self.theme_button_group.addButton(dark_radio)
        appearance_layout.addWidget(dark_radio)

        # Spacer before note
        appearance_layout.addSpacing(8)

        theme_note = QLabel("Theme applies when you click Save")
        theme_note.setObjectName("noteLabel")
        appearance_layout.addWidget(theme_note)

        appearance_group.setLayout(appearance_layout)
        col1_layout.addWidget(appearance_group)
        col1_layout.addStretch()

        # Add column 1 to grid
        content_layout.addLayout(col1_layout, 0, 0)

        # === COLUMN 2: Hardware & Advanced ===
        col2_layout = QVBoxLayout()
        col2_layout.setSpacing(20)  # Section spacing

        # Hardware Acceleration section
        hardware_group = QGroupBox("Hardware Acceleration")
        hardware_group.setMinimumWidth(400)  # Ensure enough space for text
        hardware_layout = QVBoxLayout()
        hardware_layout.setSpacing(12)
        hardware_layout.setContentsMargins(16, 16, 16, 16)

        # GPU toggle checkbox
        self.gpu_checkbox = QCheckBox("Enable GPU Acceleration (if available)")
        self.gpu_checkbox.setToolTip("Use NVIDIA NVENC or Intel/AMD VAAPI for faster encoding")
        self.gpu_checkbox.setMinimumWidth(300)  # Ensure text doesn't wrap
        hardware_layout.addWidget(self.gpu_checkbox)

        # Detection info
        detected_hw = config.detect_hardware_acceleration()
        hw_name = config.HARDWARE_ACCELERATION.get(detected_hw, {}).get('name', 'None')

        self.hw_info_label = QLabel(f"Detected: {hw_name}")
        self.hw_info_label.setObjectName("infoLabel")
        hardware_layout.addWidget(self.hw_info_label)

        # Spacer before note
        hardware_layout.addSpacing(8)

        # GPU note
        if detected_hw != 'none':
            gpu_note = QLabel("GPU encoding is 5-10x faster but may have slightly lower quality.")
        else:
            gpu_note = QLabel("No GPU acceleration available. Using CPU encoding.")
        gpu_note.setObjectName("noteLabel")
        gpu_note.setWordWrap(True)
        hardware_layout.addWidget(gpu_note)

        hardware_group.setLayout(hardware_layout)
        col2_layout.addWidget(hardware_group)

        # Advanced settings section
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout()
        advanced_layout.setSpacing(12)
        advanced_layout.setContentsMargins(16, 16, 16, 16)

        # Custom CRF
        crf_label = QLabel("Custom CRF (0-51):")
        crf_label.setToolTip("Lower values = better quality, larger files\nDefault: 17 (high quality)")
        advanced_layout.addWidget(crf_label)

        self.crf_spinbox = QSpinBox()
        self.crf_spinbox.setRange(0, 51)
        self.crf_spinbox.setValue(17)
        self.crf_spinbox.setSpecialValueText("Use preset")
        advanced_layout.addWidget(self.crf_spinbox)

        # Spacer before note
        advanced_layout.addSpacing(8)

        # Note about CRF
        crf_note = QLabel("Set to 0 to use preset CRF value")
        crf_note.setObjectName("noteLabel")
        advanced_layout.addWidget(crf_note)

        advanced_group.setLayout(advanced_layout)
        col2_layout.addWidget(advanced_group)
        col2_layout.addStretch()

        # Add column 2 to grid
        content_layout.addLayout(col2_layout, 0, 1)

        # === COLUMN 3: Output & Info ===
        col3_layout = QVBoxLayout()
        col3_layout.setSpacing(20)  # Section spacing

        # Output directory section
        output_group = QGroupBox("Output Directory")
        output_layout = QVBoxLayout()
        output_layout.setSpacing(12)
        output_layout.setContentsMargins(16, 16, 16, 16)

        dir_layout = QHBoxLayout()

        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        dir_layout.addWidget(self.output_dir_edit)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._on_browse_directory)
        browse_button.setCursor(Qt.CursorShape.PointingHandCursor)
        dir_layout.addWidget(browse_button)

        output_layout.addLayout(dir_layout)
        output_group.setLayout(output_layout)
        col3_layout.addWidget(output_group)

        # Conversion info section
        info_group = QGroupBox("Conversion Information")
        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)
        info_layout.setContentsMargins(16, 16, 16, 16)

        info_text = QLabel(
            f"Video Codec: {config.DEFAULT_VIDEO_CODEC}\n"
            f"Audio Codec: {config.DEFAULT_AUDIO_CODEC} @ {config.DEFAULT_AUDIO_BITRATE}\n"
            f"Output Format: {config.OUTPUT_FORMAT}"
        )
        info_text.setObjectName("infoLabel")
        info_layout.addWidget(info_text)

        info_group.setLayout(info_layout)
        col3_layout.addWidget(info_group)
        col3_layout.addStretch()

        # Add column 3 to grid
        content_layout.addLayout(col3_layout, 0, 2)

        # Add content layout directly to main layout - no scrolling
        main_layout.addLayout(content_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self._on_save)
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        save_button.setDefault(True)
        button_layout.addWidget(save_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def _load_current_settings(self):
        """Load current settings from config."""
        # Set quality preset
        for button in self.preset_button_group.buttons():
            preset_id = button.property("preset_id")
            if preset_id == config.current_preset:
                button.setChecked(True)
                break

        # Set theme
        for button in self.theme_button_group.buttons():
            theme_id = button.property("theme_id")
            if theme_id == config.theme:
                button.setChecked(True)
                break

        # Set GPU acceleration
        self.gpu_checkbox.setChecked(config.use_gpu)

        # Set custom CRF
        if config.custom_crf is not None:
            self.crf_spinbox.setValue(config.custom_crf)
        else:
            self.crf_spinbox.setValue(0)

        # Set output directory
        self.output_dir_edit.setText(config.output_directory)

    def _on_browse_directory(self):
        """Handle browse directory button click."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            config.output_directory
        )

        if directory:
            self.output_dir_edit.setText(directory)
            logger.debug(f"Selected output directory: {directory}")

    def _on_save(self):
        """Handle save button click."""
        # Save quality preset
        for button in self.preset_button_group.buttons():
            if button.isChecked():
                preset_id = button.property("preset_id")
                config.set_quality_preset(preset_id)
                logger.info(f"Quality preset set to: {preset_id}")
                break

        # Save theme preference
        for button in self.theme_button_group.buttons():
            if button.isChecked():
                theme_id = button.property("theme_id")
                old_theme = config.theme
                config.theme = theme_id
                logger.info(f"Theme set to: {theme_id}")

                # Reload stylesheet if theme changed
                if old_theme != theme_id:
                    from PyQt6.QtWidgets import QApplication
                    from main import load_stylesheet
                    load_stylesheet(QApplication.instance(), theme_id)
                    logger.info(f"Theme switched from {old_theme} to {theme_id}")
                break

        # Save GPU acceleration setting
        config.use_gpu = self.gpu_checkbox.isChecked()
        logger.info(f"GPU acceleration: {'enabled' if config.use_gpu else 'disabled'}")

        # Save custom CRF
        crf_value = self.crf_spinbox.value()
        if crf_value > 0:
            config.set_custom_crf(crf_value)
            logger.info(f"Custom CRF set to: {crf_value}")
        else:
            config.reset_custom_settings()
            logger.info("Using preset CRF values")

        # Save output directory
        output_dir = self.output_dir_edit.text()
        if output_dir:
            config.set_output_directory(output_dir)
            logger.info(f"Output directory set to: {output_dir}")

        self.settings_changed.emit()
        self.accept()


class QuickSettingsWidget(QGroupBox):
    """
    Quick settings widget for the main window.

    Provides quick access to common settings without opening the full dialog.
    """

    settings_button_clicked = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize quick settings widget."""
        super().__init__("Settings", parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QHBoxLayout()

        # Quality preset dropdown
        preset_label = QLabel("Quality:")
        layout.addWidget(preset_label)

        self.preset_combo = QComboBox()
        for preset_id, preset_data in config.QUALITY_PRESETS.items():
            self.preset_combo.addItem(preset_data['name'], preset_id)

        self.preset_combo.setCurrentText(
            config.QUALITY_PRESETS[config.current_preset]['name']
        )
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        layout.addWidget(self.preset_combo)

        layout.addStretch()

        # Settings button
        settings_button = QPushButton("More Settings...")
        settings_button.clicked.connect(self.settings_button_clicked.emit)
        settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(settings_button)

        self.setLayout(layout)

    def _on_preset_changed(self, index):
        """Handle preset selection change."""
        preset_id = self.preset_combo.itemData(index)
        if preset_id:
            config.set_quality_preset(preset_id)
            logger.info(f"Quality preset changed to: {preset_id}")

    def update_from_config(self):
        """Update widget to reflect current config."""
        preset_name = config.QUALITY_PRESETS[config.current_preset]['name']
        self.preset_combo.setCurrentText(preset_name)
