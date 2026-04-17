import sys
import os

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout,
    QPushButton, QScrollArea, QFrame, QDialog, QSlider,
    QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
)

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput


# =========================
# CUSTOM VIEW (DRAG)
# =========================
class ImageGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.last_mouse_pos = None
        self.setDragMode(QGraphicsView.NoDrag)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.last_mouse_pos:
            current_pos = event.position().toPoint()
            delta = current_pos - self.last_mouse_pos
            self.last_mouse_pos = current_pos

            h_scroll = self.horizontalScrollBar()
            v_scroll = self.verticalScrollBar()

            if h_scroll.maximum() > 0:
                h_scroll.setValue(h_scroll.value() - delta.x())

            if v_scroll.maximum() > 0:
                v_scroll.setValue(v_scroll.value() - delta.y())

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.last_mouse_pos = None
        super().mouseReleaseEvent(event)


# =========================
# IMAGE VIEWER
# =========================
class ImageViewer(QDialog):
    def __init__(self, image_path):
        super().__init__()

        self.setWindowTitle("Image Viewer")
        self.resize(700, 700)

        self.view = ImageGraphicsView()
        self.scene = QGraphicsScene()

        self.pixmap_item = QGraphicsPixmapItem(QPixmap(image_path))
        self.scene.addItem(self.pixmap_item)

        self.view.setScene(self.scene)
        self.view.setAlignment(Qt.AlignCenter)

        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.scale_factor = 1.0
        self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        factor = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale_factor *= factor

        if self.scale_factor < 0.2:
            self.scale_factor = 0.2
            self.view.resetTransform()
            self.view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
            return

        self.view.scale(factor, factor)


# =========================
# AUDIO PLAYER
# =========================
class AudioPlayer(QDialog):
    def __init__(self, audio_path):
        super().__init__()

        self.setWindowTitle("Audio Player")
        self.resize(400, 180)

        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)

        self.player.setSource(QUrl.fromLocalFile(audio_path))

        # =========================
        # BIG CIRCULAR PLAY BUTTON
        # =========================
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(90, 90)

        self.play_button.setStyleSheet("""
            QPushButton {
                border: 3px solid #888;
                border-radius: 45px;
                font-size: 32px;
                background-color: #222;
                color: white;
            }
            QPushButton:hover {
                border: 3px solid #aaa;
                background-color: #333;
            }
            QPushButton:pressed {
                background-color: #555;
            }
        """)

        self.play_button.clicked.connect(self.toggle_play)

        # =========================
        # SLIDER
        # =========================
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)

        self.player.positionChanged.connect(self.update_slider)
        self.player.durationChanged.connect(self.set_duration)

        self.slider.sliderPressed.connect(self.start_seek)
        self.slider.sliderReleased.connect(self.end_seek)
        self.slider.sliderMoved.connect(self.seek)

        # =========================
        # LAYOUT
        # =========================
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        # center button
        btn_layout.addStretch()
        btn_layout.addWidget(self.play_button)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        layout.addWidget(self.slider)

        self.setLayout(layout)

        self.duration = 0
        self.is_user_seeking = False

        self.player.errorOccurred.connect(self.handle_error)

    # =========================
    # PLAY / PAUSE
    # =========================
    def toggle_play(self):
        if self.player.playbackState() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_button.setText("▶")
        else:
            self.player.play()
            self.play_button.setText("⏸")

    # =========================
    # SEEK CONTROL
    # =========================
    def start_seek(self):
        self.is_user_seeking = True

    def end_seek(self):
        self.is_user_seeking = False
        self.seek(self.slider.value())

    def update_slider(self, position):
        if self.duration > 0 and not self.is_user_seeking:
            self.slider.setValue(int(position * 100 / self.duration))

    def set_duration(self, duration):
        self.duration = duration

    def seek(self, value):
        if self.duration > 0:
            new_pos = int(value * self.duration / 100)
            self.player.setPosition(new_pos)

    def handle_error(self, error, error_string):
        print("Audio Error:", error_string)


# =========================
# FILE TILE
# =========================
class FileTile(QWidget):
    IMAGE_EXTS = (".png", ".jpg", ".jpeg")

    def __init__(self, file_path):
        super().__init__()

        self.file_path = file_path
        self.window = None

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)  # ⭐ CENTER EVERYTHING

        self.button = QPushButton()
        self.button.setFixedSize(120, 120)

        lower_path = file_path.lower()

        # IMAGE
        if lower_path.endswith(self.IMAGE_EXTS):
            pix = QPixmap(file_path).scaled(
                120, 120,
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            self.button.setIcon(pix)
            self.button.setIconSize(pix.size())

        # AUDIO
        else:
            self.button.setText("🎵")
            self.button.setStyleSheet("font-size: 40px;")

        # LABEL
        self.label = QLabel(os.path.basename(file_path))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        self.label.setStyleSheet("""
            QLabel {
                border: none;
                background: transparent;
                padding: 2px;
            }
        """)

        # ⭐ IMPORTANT: center each widget individually
        layout.addWidget(self.button, alignment=Qt.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        self.button.clicked.connect(self.open_file)

    def open_file(self):
        if self.file_path.lower().endswith(self.IMAGE_EXTS):
            self.window = ImageViewer(self.file_path)
        else:
            self.window = AudioPlayer(self.file_path)

        self.window.show()
# =========================
# MAIN WINDOW (NOW TAKES PATH)
# =========================
class MainWindow(QWidget):
    FILE_EXTS = (".png", ".jpg", ".jpeg", ".wav", ".mp3")

    def __init__(self, data_path):
        super().__init__()

        self.setWindowTitle("DATA Explorer 😏")
        self.resize(900, 700)

        main_layout = QVBoxLayout()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout()

        if not os.path.exists(data_path):
            container_layout.addWidget(QLabel("Folder not found"))
        else:
            for folder in os.listdir(data_path):
                folder_path = os.path.join(data_path, folder)

                if not os.path.isdir(folder_path):
                    continue

                title = QLabel(folder.upper())
                title.setStyleSheet("font-size: 22px; font-weight: bold;")
                container_layout.addWidget(title)

                frame = QFrame()
                frame.setStyleSheet("""
                    QFrame {
                        border: 2px solid gray;
                        border-radius: 10px;
                        padding: 10px;
                    }
                """)

                grid = QGridLayout()
                files = [
                    f for f in os.listdir(folder_path)
                    if f.lower().endswith(self.FILE_EXTS)
                ]

                cols = 5

                for i, file in enumerate(files):
                    path = os.path.join(folder_path, file)
                    grid.addWidget(FileTile(path), i // cols, i % cols)

                frame.setLayout(grid)
                container_layout.addWidget(frame)

        container.setLayout(container_layout)
        scroll.setWidget(container)

        main_layout.addWidget(scroll)
        self.setLayout(main_layout)


# =========================
# LAUNCH FUNCTION ⭐
# =========================
def launch_data_explorer(data_path):
    app = QApplication.instance()

    if not app:
        app = QApplication(sys.argv)

    window = MainWindow(data_path)
    window.show()

    if not QApplication.instance().startingUp():
        app.exec()