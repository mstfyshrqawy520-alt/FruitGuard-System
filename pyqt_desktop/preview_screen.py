from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from api_client import api
from app_state import app_state

class PreviewScreen(QWidget):
    go_back = pyqtSignal()
    analysis_complete = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.image_path = None
        self.init_ui()
        app_state.language_changed.connect(self.update_texts)
        app_state.theme_changed.connect(self.update_theme)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)

        self.title = QLabel(app_state.t('preview'))
        self.main_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.image_label, stretch=1)

        bottom_layout = QHBoxLayout()
        
        self.retake_btn = QPushButton(app_state.t('back'))
        self.retake_btn.clicked.connect(self.go_back.emit)
        bottom_layout.addWidget(self.retake_btn)

        self.analyze_btn = QPushButton(f"✨ {app_state.t('analyze_btn')}")
        self.analyze_btn.clicked.connect(self.analyze_image)
        bottom_layout.addWidget(self.analyze_btn)

        self.main_layout.addLayout(bottom_layout)
        self.update_theme(app_state.is_dark_mode)

    def update_texts(self, lang=None):
        self.title.setText(app_state.t('preview'))
        self.retake_btn.setText(app_state.t('back'))
        self.analyze_btn.setText(f"✨ {app_state.t('analyze_btn')}")

    def update_theme(self, is_dark):
        text_color = "white" if is_dark else "black"
        self.title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {text_color};")
        
        img_bg = "#0f172a" if is_dark else "#e2e8f0"
        self.image_label.setStyleSheet(f"background-color: {img_bg}; border-radius: 12px;")

        btn_bg = "#334155" if is_dark else "#cbd5e1"
        btn_fg = "white" if is_dark else "black"
        self.retake_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {btn_bg}; color: {btn_fg}; padding: 12px; border-radius: 8px; font-weight: bold; }}
        """)

        self.analyze_btn.setStyleSheet("""
            QPushButton { background-color: #3b82f6; color: white; padding: 12px; border-radius: 8px; font-weight: bold; }
        """)

    def set_image(self, path):
        self.image_path = path
        pixmap = QPixmap(path)
        self.image_label.setPixmap(pixmap.scaled(
            400, 400, Qt.AspectRatioMode.KeepAspectRatio
        ))

    def analyze_image(self):
        if not self.image_path:
            return
            
        self.analyze_btn.setText(app_state.t('analyzing'))
        self.analyze_btn.setEnabled(False)

        success, data = api.analyze_image(self.image_path)
        
        self.analyze_btn.setText(f"✨ {app_state.t('analyze_btn')}")
        self.analyze_btn.setEnabled(True)

        if success:
            self.analysis_complete.emit(data)
        else:
            QMessageBox.critical(self, app_state.t('error'), data)
