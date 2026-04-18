import os
import json
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsLineItem, QPushButton, QHBoxLayout, QLabel,
    QSlider, QWidget
)
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter
from PySide6.QtCore import Qt, QUrl, QRectF, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

class TimelineBlock(QGraphicsRectItem):
    def __init__(self, start_pos, y_pos, width, height, segment, color, parent_timeline):
        super().__init__(start_pos, y_pos, width, height)
        self.segment = segment
        self.default_color = color
        self.setBrush(QBrush(self.default_color))
        self.setPen(QPen(Qt.black, 1))
        self.setAcceptHoverEvents(True)
        self.parent_timeline = parent_timeline
        
        # Add text
        self.text = QGraphicsTextItem(self.segment['speaker'], self)
        self.text.setFont(QFont("Arial", 10, QFont.Bold))
        self.text.setDefaultTextColor(Qt.white)
        
        # Ensure text does not overflow standard segments
        # Center roughly
        rect = self.rect()
        self.text.setPos(rect.x() + 5, rect.y() + (rect.height() - 20) / 2)

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(self.default_color.lighter(120)))
        self.setCursor(Qt.PointingHandCursor)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(self.default_color))
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent_timeline.play_segment(self.segment)
        super().mousePressEvent(event)

class InteractiveTimelineWindow(QDialog):
    def __init__(self, audio_file: str, segments_file: str):
        super().__init__()
        self.setWindowTitle("Interactive Speaker Timeline")
        self.resize(1000, 400)
        
        self.audio_file = audio_file
        
        with open(segments_file, "r") as f:
            self.segments = json.load(f)
            
        self.init_audio_player()
        self.init_ui()
        self.playing_segment_end = None
        
    def init_audio_player(self):
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.player.setSource(QUrl.fromLocalFile(self.audio_file))
        self.player.positionChanged.connect(self.on_position_changed)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header layout
        header_layout = QHBoxLayout()
        self.info_label = QLabel("Click on any speaker block to play that segment.")
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #444;")
        header_layout.addWidget(self.info_label)
        
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        self.stop_button.clicked.connect(self.stop_playback)
        header_layout.addStretch()
        header_layout.addWidget(self.stop_button)
        
        layout.addLayout(header_layout)

        # Plotting timeline
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.pixels_per_second = 50
        self.track_height = 50
        self.track_spacing = 10
        self.render_timeline()
        layout.addWidget(self.view)
        
    def render_timeline(self):
        if not self.segments:
            return
            
        speakers = sorted(list(set(seg["speaker"] for seg in self.segments)))
        speaker_to_y = {spk: i for i, spk in enumerate(speakers)}
        
        # We need distinct colors for speakers
        colors = [
            QColor(31, 119, 180), QColor(255, 127, 14), 
            QColor(44, 160, 44), QColor(214, 39, 40), 
            QColor(148, 103, 189), QColor(140, 86, 75), 
            QColor(227, 119, 194), QColor(127, 127, 127), 
            QColor(188, 189, 34), QColor(23, 190, 207)
        ]

        max_x = 0
        
        for i, speaker in enumerate(speakers):
            y_pos = i * (self.track_height + self.track_spacing)
            # Add speaker label
            label = self.scene.addText(speaker)
            label.setFont(QFont("Arial", 12, QFont.Bold))
            label.setPos(-100, y_pos + (self.track_height/2) - 10)
        
        for seg in self.segments:
            start = seg["start"]
            end = seg["end"]
            speaker = seg["speaker"]
            
            x_pos = start * self.pixels_per_second
            width = (end - start) * self.pixels_per_second
            y_pos = speaker_to_y[speaker] * (self.track_height + self.track_spacing)
            
            color = colors[speaker_to_y[speaker] % len(colors)]
            block = TimelineBlock(x_pos, y_pos, width, self.track_height, seg, color, self)
            self.scene.addItem(block)
            
            if x_pos + width > max_x:
                max_x = x_pos + width
                
        # Draw playback cursor
        self.cursor_line = QGraphicsLineItem(0, 0, 0, len(speakers) * (self.track_height + self.track_spacing))
        self.cursor_line.setPen(QPen(Qt.red, 2))
        self.scene.addItem(self.cursor_line)
        self.cursor_line.hide()
        
        # Set scene rect
        total_height = len(speakers) * (self.track_height + self.track_spacing)
        self.scene.setSceneRect(-120, 0, max_x + 150, total_height)
        
    def play_segment(self, segment):
        start_ms = int(segment["start"] * 1000)
        self.playing_segment_end = int(segment["end"] * 1000)
        
        self.player.setPosition(start_ms)
        self.player.play()
        self.cursor_line.show()
        
        self.info_label.setText(f"Playing: {segment['speaker']} ({segment['start']:.2f}s - {segment['end']:.2f}s)")
        
    def stop_playback(self):
        self.player.pause()
        self.cursor_line.hide()
        self.info_label.setText("Click on any speaker block to play that segment.")
        
    def on_position_changed(self, position):
        if self.playing_segment_end and position >= self.playing_segment_end:
            self.stop_playback()
            self.playing_segment_end = None
            return
            
        cursor_x = (position / 1000.0) * self.pixels_per_second
        self.cursor_line.setLine(cursor_x, 0, cursor_x, self.scene.sceneRect().height())
        
        # Ensure cursor is visible
        if cursor_x > self.view.horizontalScrollBar().value() + self.view.viewport().width() - 50:
            self.view.horizontalScrollBar().setValue(int(cursor_x - 50))
        elif cursor_x < self.view.horizontalScrollBar().value():
            self.view.horizontalScrollBar().setValue(int(cursor_x))
            
    def closeEvent(self, event):
        # Stop audio playback when dialog is closed
        self.player.stop()
        super().closeEvent(event)
