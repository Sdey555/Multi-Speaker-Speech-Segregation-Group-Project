import json
import os
import shutil
import warnings
import sys

# Prevent torchaudio warnings from being treated as exceptions that crash the pipeline
warnings.filterwarnings("ignore")

# PyTorch 2.5 torchcodec raises RuntimeError instead of ImportError on missing FFmpeg DLLs, crashing HF Transformers. 
# We explicitly mock it to None so transformers gracefully falls back to soundfile without crashing!
sys.modules["torchcodec"] = None

from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
    QGroupBox,
    QHBoxLayout,
    QComboBox,
)

from audio_processing.loader import load_audio
from audio_processing.noise_cleaner import clean_noise
from diarization.diarize import perform_diarization
from utils.timestamps import group_by_speaker
from separation.split_speakers import split_into_speakers
from visualization import create_all_visualizations
from GUI.fileExplorer import MainWindow
from config import DATA_FOLDER, CLEAN_AUDIO_FILE, OUTPUT_FOLDER
from diarization.sound_classifier import perform_sound_classification


class PipelineWorker(QThread):
    status_updated = Signal(str)
    finished_success = Signal(str)
    finished_error = Signal(str)

    def __init__(self, input_path: str, segregation_mode: int):
        super().__init__()
        self.input_path = input_path
        self.segregation_mode = segregation_mode

    def run(self):
        try:
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)

            self.status_updated.emit("Loading audio...")
            load_audio(self.input_path, CLEAN_AUDIO_FILE)

            self.status_updated.emit("Cleaning noise...")
            clean_noise(CLEAN_AUDIO_FILE, CLEAN_AUDIO_FILE)

            if self.segregation_mode == 0:
                self.status_updated.emit("Running speaker diarization...")
                segments = perform_diarization(CLEAN_AUDIO_FILE)
            elif self.segregation_mode == 1:
                self.status_updated.emit("Running vocal segregation (Speech vs Singing)...")
                segments = perform_sound_classification(CLEAN_AUDIO_FILE, mode_type="vocals")
            elif self.segregation_mode == 2:
                self.status_updated.emit("Running instrument segregation...")
                segments = perform_sound_classification(CLEAN_AUDIO_FILE, mode_type="instruments")

            self.status_updated.emit("Grouping speakers...")
            speakers = group_by_speaker(segments)

            self.status_updated.emit("Splitting speaker audio...")
            split_into_speakers(CLEAN_AUDIO_FILE, speakers, OUTPUT_FOLDER)

            self.status_updated.emit("Saving diarization results...")
            segments_file = os.path.join(OUTPUT_FOLDER, "segments.json")
            with open(segments_file, "w", encoding="utf-8") as handle:
                json.dump(segments, handle, indent=4)

            self.status_updated.emit("Generating visualizations...")
            create_all_visualizations(CLEAN_AUDIO_FILE, segments, OUTPUT_FOLDER, OUTPUT_FOLDER)

            self.finished_success.emit("Processing complete. Output is available in the Data folder.")
        except Exception as exc:
            import traceback
            with open("crash_log.txt", "w") as f:
                f.write(traceback.format_exc())
            self.finished_error.emit(str(exc))


class LoadingAnimationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.is_animating = False
        
        self.label = QLabel("Ready to process audio.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; color: gray; margin-top: 50px;")
        
        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(self.label)
        layout.addStretch()
        
    def start_animation(self):
        self.label.setText("Initializing Process...")
        self.label.setStyleSheet("font-size: 20px; color: #0275d8; font-weight: bold; margin-top: 100px;")
        self.is_animating = True
        self.timer.start(30)
        
    def stop_animation(self):
        self.is_animating = False
        self.timer.stop()
        self.label.setText("Processing Complete!")
        self.label.setStyleSheet("font-size: 20px; color: #5cb85c; font-weight: bold; margin-top: 50px;")
        self.update()

    def set_status(self, text):
        if self.is_animating:
            self.label.setText(text)

    def rotate(self):
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.is_animating:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        size = 100
        x = (rect.width() - size) / 2
        y = (rect.height() - size) / 2 - 40
        
        pen = QPen(QColor("#0275d8"), 8, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(int(x), int(y), int(size), int(size), int(-self.angle * 16), int(120 * 16))
        painter.end()


class GuiApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Speaker Segregation")
        self.resize(1000, 800)

        self.input_path = ""
        self.worker = None
        self.last_processed_sig = None

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)

        # ====== UPPER: Pipeline Group ======
        self.pipeline_group = QGroupBox("Audio Segregation Pipeline")
        self.pipeline_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; }")
        self._build_pipeline_ui(self.pipeline_group)
        main_layout.addWidget(self.pipeline_group, stretch=0)

        # ====== LOWER: Stacked Widget ======
        self.lower_stack = QStackedWidget()
        
        self.loading_widget = LoadingAnimationWidget()
        
        self.explorer_container = QWidget()
        self.explorer_layout = QVBoxLayout(self.explorer_container)
        self.explorer_layout.setContentsMargins(0, 0, 0, 0)
        self._refresh_explorer()
        
        self.lower_stack.addWidget(self.loading_widget)
        self.lower_stack.addWidget(self.explorer_container)
        
        if os.path.exists(os.path.join(DATA_FOLDER, "output", "segments.json")):
            self.lower_stack.setCurrentIndex(1)
        else:
            self.lower_stack.setCurrentIndex(0)
            
        main_layout.addWidget(self.lower_stack, stretch=1)

    def _build_pipeline_ui(self, parent_widget):
        layout = QVBoxLayout(parent_widget)
        
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Segregation Mode:")
        mode_label.setStyleSheet("font-size: 14px;")
        self.mode_dropdown = QComboBox()
        self.mode_dropdown.setStyleSheet("padding: 5px; font-size: 14px;")
        self.mode_dropdown.addItems([
            "1. Multi-Speaker Segregation (Pyannote)",
            "2. Speaking vs Singing (CED-Tiny)",
            "3. Instrument Sounds (CED-Tiny)"
        ])
        self.mode_dropdown.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_dropdown, stretch=1)
        layout.addLayout(mode_layout)
        
        row1 = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Choose an input audio file (.wav, .mp3, .flac, .m4a, .ogg)")
        self.input_line.setReadOnly(True)
        self.input_line.setStyleSheet("padding: 8px; font-size: 14px; color: #212529; background-color: #ffffff;")
        
        choose_button = QPushButton("Browse")
        choose_button.setStyleSheet("padding: 8px 15px; font-size: 14px;")
        choose_button.clicked.connect(self.choose_input_file)
        
        row1.addWidget(self.input_line)
        row1.addWidget(choose_button)
        layout.addLayout(row1)

        self.run_button = QPushButton("Start Processing Pipeline")
        self.run_button.setEnabled(False)
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #0275d8;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
                margin-top: 10px;
                margin-bottom: 5px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton:hover:!disabled {
                background-color: #0056b3;
            }
        """)
        self.run_button.clicked.connect(self.start_pipeline)
        layout.addWidget(self.run_button)

        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)
        self.status_box.setPlaceholderText("Logs will appear here...")
        self.status_box.setMaximumHeight(80)
        self.status_box.setStyleSheet("background-color: #f8f9fa; color: #212529; border: 1px solid #ced4da; border-radius: 4px;")
        layout.addWidget(self.status_box)

    def _on_mode_changed(self):
        # Clear all input UI states
        self.input_path = ""
        self.input_line.clear()
        self.run_button.setEnabled(False)
        self.last_processed_sig = None
        self.status_box.clear()

        # Completely wipe input, output, and visualization folders
        dirs_to_clear = [
            os.path.join(DATA_FOLDER, "input"),
            OUTPUT_FOLDER, 
            os.path.join(DATA_FOLDER, "visualizations")
        ]
        
        for d in dirs_to_clear:
            if os.path.exists(d):
                try:
                    for filename in os.listdir(d):
                        file_path = os.path.join(d, filename)
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Warning: Failed to gently clear '{d}': {e}")
        
        self.lower_stack.setCurrentIndex(0)
        self.loading_widget.label.setText("Mode Switched. Ready to process.")
        self.loading_widget.label.setStyleSheet("font-size: 18px; color: gray; margin-top: 50px;")
        self._refresh_explorer()
        self._append_status("Mode changed. Cleared input, output & visualizations folders.")

    def _refresh_explorer(self):
        while self.explorer_layout.count():
            child = self.explorer_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        explorer_widget = MainWindow(DATA_FOLDER)
        self.explorer_layout.addWidget(explorer_widget)

    def choose_input_file(self):
        audio_filters = "Audio Files (*.wav *.mp3 *.flac *.m4a *.ogg);;All Files (*)"
        default_dir = os.path.join(DATA_FOLDER, "input") if os.path.exists(os.path.join(DATA_FOLDER, "input")) else ""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Input Audio", default_dir, audio_filters)

        if file_path:
            self.input_path = file_path
            self.input_line.setText(file_path)
            self.run_button.setEnabled(True)
            self._append_status(f"Selected input: {file_path}")

    def start_pipeline(self):
        if not self.input_path:
            self._show_error("Please choose a valid input audio file before running the pipeline.")
            return

        try:
            current_sig = (
                self.input_path,
                os.path.getmtime(self.input_path),
                os.path.getsize(self.input_path)
            )
        except Exception as e:
            self._show_error(f"Error accessing file: {str(e)}")
            return

        if self.last_processed_sig == current_sig:
            QMessageBox.information(self, "Already Processed", "This exact file has already been processed.")
            if os.path.exists(os.path.join(DATA_FOLDER, "output", "segments.json")):
                self.lower_stack.setCurrentIndex(1)
            return

        self.last_processed_sig = current_sig

        self.run_button.setEnabled(False)
        self.status_box.clear()
        
        self.lower_stack.setCurrentIndex(0)
        self.loading_widget.start_animation()
        self._append_status("Starting processing...")

        self._append_status("Clearing previous output data...")
        dirs_to_clear = [OUTPUT_FOLDER, os.path.join(DATA_FOLDER, "visualizations")]
        for d in dirs_to_clear:
            if os.path.exists(d):
                try:
                    for filename in os.listdir(d):
                        file_path = os.path.join(d, filename)
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                except Exception as e:
                    self._append_status(f"Warning: Failed to clear {d}: {e}")

        self.worker = PipelineWorker(self.input_path, self.mode_dropdown.currentIndex())
        self.worker.status_updated.connect(self._append_status)
        self.worker.finished_success.connect(self._on_success)
        self.worker.finished_error.connect(self._on_error)
        self.worker.start()

    def _append_status(self, message: str):
        self.status_box.append(f"• {message}")
        self.status_box.verticalScrollBar().setValue(self.status_box.verticalScrollBar().maximum())
        self.loading_widget.set_status(message)

    def _on_success(self, message: str):
        self._append_status(message)
        self._append_status("You can now preview the results.")
        self.run_button.setEnabled(True)
        self.loading_widget.stop_animation()
        self._refresh_explorer()
        self.lower_stack.setCurrentIndex(1)
        QMessageBox.information(self, "Pipeline Complete", message)

    def _on_error(self, message: str):
        self._append_status(f"Error: {message}")
        self.run_button.setEnabled(True)
        self.loading_widget.stop_animation()
        self.loading_widget.label.setText("Error during processing.")
        self.loading_widget.label.setStyleSheet("font-size: 20px; color: red; font-weight: bold; margin-top: 50px;")
        QMessageBox.critical(self, "Pipeline Failed", message)

    def _show_error(self, message: str):
        QMessageBox.warning(self, "Input Required", message)


def launch_gui():
    app = QApplication.instance()
    if not app:
        app = QApplication([])

    window = GuiApp()
    window.show()

    if not QApplication.instance().startingUp():
        app.exec()
