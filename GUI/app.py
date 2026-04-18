import json
import os

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
)

from audio_processing.loader import load_audio
from audio_processing.noise_cleaner import clean_noise
from diarization.diarize import perform_diarization
from utils.timestamps import group_by_speaker
from separation.split_speakers import split_into_speakers
from visualization import create_all_visualizations
from GUI.fileExplorer import MainWindow
from config import DATA_FOLDER, CLEAN_AUDIO_FILE, OUTPUT_FOLDER


class PipelineWorker(QThread):
    status_updated = Signal(str)
    finished_success = Signal(str)
    finished_error = Signal(str)

    def __init__(self, input_path: str):
        super().__init__()
        self.input_path = input_path

    def run(self):
        try:
            os.makedirs(OUTPUT_FOLDER, exist_ok=True)

            self.status_updated.emit("Loading audio...")
            load_audio(self.input_path, CLEAN_AUDIO_FILE)

            self.status_updated.emit("Cleaning noise...")
            clean_noise(CLEAN_AUDIO_FILE, CLEAN_AUDIO_FILE)

            self.status_updated.emit("Running speaker diarization...")
            segments = perform_diarization(CLEAN_AUDIO_FILE)

            self.status_updated.emit("Grouping speakers...")
            speakers = group_by_speaker(segments)

            self.status_updated.emit("Splitting speaker audio...")
            split_into_speakers(CLEAN_AUDIO_FILE, speakers, OUTPUT_FOLDER)

            self.status_updated.emit("Saving diarization results...")
            segments_file = os.path.join(OUTPUT_FOLDER, "segments.json")
            with open(segments_file, "w", encoding="utf-8") as handle:
                json.dump(segments, handle, indent=4)

            self.status_updated.emit("Generating visualizations...")
            create_all_visualizations(CLEAN_AUDIO_FILE, segments, OUTPUT_FOLDER)

            self.finished_success.emit("Processing complete. Output is available in the Data folder.")
        except Exception as exc:
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

        self.run_button.setEnabled(False)
        self.status_box.clear()
        
        self.lower_stack.setCurrentIndex(0)
        self.loading_widget.start_animation()
        self._append_status("Starting processing...")

        self.worker = PipelineWorker(self.input_path)
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
