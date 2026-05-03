import base64
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
from app_state import app_state

class ResultScreen(QWidget):
    go_home = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        app_state.language_changed.connect(self.update_texts)
        app_state.theme_changed.connect(self.update_theme)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)

        self.title_label = QLabel(app_state.t('result'))
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Images row
        images_layout = QHBoxLayout()
        
        self.orig_image_label = QLabel()
        self.orig_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        images_layout.addWidget(self.orig_image_label)

        self.mask_image_label = QLabel()
        self.mask_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        images_layout.addWidget(self.mask_image_label)

        layout.addLayout(images_layout)
        layout.addSpacing(20)

        # Stats
        self.quality_label = QLabel()
        self.quality_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.quality_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.size_label = QLabel()
        self.size_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #3b82f6;")
        layout.addWidget(self.size_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(30)

        self.home_btn = QPushButton(app_state.t('back_home'))
        self.home_btn.clicked.connect(self.go_home.emit)
        layout.addWidget(self.home_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.update_theme(app_state.is_dark_mode)

    def update_texts(self, lang=None):
        self.home_btn.setText(app_state.t('back_home'))

    def update_theme(self, is_dark):
        text_color = "white" if is_dark else "black"
        self.title_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {text_color};")
        
        btn_bg = "#334155" if is_dark else "#cbd5e1"
        btn_fg = "white" if is_dark else "black"
        self.home_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {btn_bg}; color: {btn_fg}; padding: 12px; border-radius: 8px; font-weight: bold; }}
        """)

    def display_result(self, data, orig_image_path):
        fruit_name = str(data.get("fruit_name", "Unknown")).upper()
        self.title_label.setText(fruit_name)

        quality = str(data.get("quality", "Unknown")).upper()
        if "FRESH" in quality:
            self.quality_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #10b981;") # Green
        else:
            self.quality_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #ef4444;") # Red
            
        self.quality_label.setText(f"{app_state.t('quality')} {quality}")
        self.size_label.setText(f"{app_state.t('size')} {data.get('size_cm', 0)} cm²")

        # Load Original Image
        orig_pixmap = QPixmap(orig_image_path)
        self.orig_image_label.setPixmap(orig_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))

        # Decode Base64 Mask
        b64_mask = data.get("mask")
        if b64_mask:
            try:
                if "," in b64_mask:
                    b64_mask = b64_mask.split(",")[1]
                mask_data = base64.b64decode(b64_mask)
                image = QImage()
                image.loadFromData(mask_data)
                mask_pixmap = QPixmap.fromImage(image)
                self.mask_image_label.setPixmap(mask_pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio))
            except Exception as e:
                print("Error decoding mask:", e)
