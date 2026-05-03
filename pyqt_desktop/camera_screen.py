import cv2
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from app_state import app_state
import tempfile
import os

class CameraScreen(QWidget):
    image_captured = pyqtSignal(str)
    go_back = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.init_ui()
        app_state.language_changed.connect(self.update_texts)
        app_state.theme_changed.connect(self.update_theme)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel(app_state.t('camera'))
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_label, stretch=1)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(20, 20, 20, 20)

        self.back_btn = QPushButton(app_state.t('back'))
        self.back_btn.setStyleSheet("""
            QPushButton { background-color: #ef4444; color: white; padding: 12px; border-radius: 8px; font-weight: bold; }
        """)
        self.back_btn.clicked.connect(self.close_camera)
        bottom_layout.addWidget(self.back_btn)

        self.capture_btn = QPushButton(f"📸 {app_state.t('capture')}")
        self.capture_btn.clicked.connect(self.take_picture)
        bottom_layout.addWidget(self.capture_btn, stretch=1)

        layout.addLayout(bottom_layout)
        self.update_theme(app_state.is_dark_mode)

    def update_texts(self, lang=None):
        self.back_btn.setText(app_state.t('back'))
        self.capture_btn.setText(f"📸 {app_state.t('capture')}")

    def update_theme(self, is_dark):
        bg_color = "black" if is_dark else "#e2e8f0"
        text_color = "white" if is_dark else "black"
        self.video_label.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")

        btn_bg = "#ffffff" if is_dark else "#3b82f6"
        btn_fg = "black" if is_dark else "white"
        self.capture_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {btn_bg}; color: {btn_fg}; padding: 16px; border-radius: 30px; font-weight: bold; font-size: 16px;}}
        """)

    def start_camera(self):
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            QMessageBox.critical(self, app_state.t('error'), "Could not open webcam.")
            self.go_back.emit()
            return
        self.timer.start(30)

    def update_frame(self):
        if self.capture is not None and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.flip(frame, 1) # mirror
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_img).scaled(
                    self.video_label.width(), self.video_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio
                ))

    def take_picture(self):
        if self.capture is not None and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.flip(frame, 1)
                temp_dir = tempfile.gettempdir()
                img_path = os.path.join(temp_dir, "captured_fruit.jpg")
                cv2.imwrite(img_path, frame)
                self.close_camera(emit_back=False)
                self.image_captured.emit(img_path)

    def close_camera(self, emit_back=True):
        self.timer.stop()
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        self.video_label.clear()
        if emit_back:
            self.go_back.emit()
