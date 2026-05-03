from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from app_state import app_state

class HomeScreen(QWidget):
    open_camera = pyqtSignal()
    image_selected = pyqtSignal(str)
    open_history = pyqtSignal()
    open_profile = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        app_state.language_changed.connect(self.update_texts)
        app_state.theme_changed.connect(self.update_theme)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)

        # Header Row
        header_layout = QHBoxLayout()
        self.title = QLabel(app_state.t('analyze_fruit'))
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(self.title)

        header_layout.addStretch()

        self.profile_btn = QPushButton(app_state.t('profile'))
        self.profile_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #3b82f6; font-weight: bold; font-size: 16px; border: none;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        self.profile_btn.clicked.connect(self.open_profile.emit)
        header_layout.addWidget(self.profile_btn)
        self.main_layout.addLayout(header_layout)

        self.subtitle = QLabel(app_state.t('upload_photo'))
        self.subtitle.setStyleSheet("font-size: 16px; color: #94a3b8;")
        self.main_layout.addWidget(self.subtitle)

        self.main_layout.addSpacing(30)

        # Buttons row
        buttons_layout = QHBoxLayout()
        
        # Camera Button
        self.camera_btn = QPushButton(app_state.t('take_photo'))
        self.camera_btn.setFixedHeight(120)
        self.camera_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.camera_btn.clicked.connect(self.open_camera.emit)
        buttons_layout.addWidget(self.camera_btn)

        # Gallery Button
        self.gallery_btn = QPushButton(app_state.t('gallery'))
        self.gallery_btn.setFixedHeight(120)
        self.gallery_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.gallery_btn.clicked.connect(self.pick_file)
        buttons_layout.addWidget(self.gallery_btn)

        self.main_layout.addLayout(buttons_layout)

        self.main_layout.addSpacing(30)

        # History Button
        self.history_btn = QPushButton(app_state.t('view_history'))
        self.history_btn.setFixedHeight(60)
        self.history_btn.clicked.connect(self.open_history.emit)
        self.main_layout.addWidget(self.history_btn)

        self.main_layout.addStretch()
        self.update_theme(app_state.is_dark_mode)

    def update_texts(self, lang=None):
        self.title.setText(app_state.t('analyze_fruit'))
        self.subtitle.setText(app_state.t('upload_photo'))
        self.profile_btn.setText(app_state.t('profile'))
        self.camera_btn.setText(app_state.t('take_photo'))
        self.gallery_btn.setText(app_state.t('gallery'))
        self.history_btn.setText(app_state.t('view_history'))

    def update_theme(self, is_dark):
        bg_color = "#1e293b" if is_dark else "#ffffff"
        text_color = "white" if is_dark else "black"
        sub_text_color = "#94a3b8" if is_dark else "#64748b"

        self.title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {text_color};")
        self.subtitle.setStyleSheet(f"font-size: 16px; color: {sub_text_color};")

        self.camera_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: {text_color};
                border: 2px solid #3b82f6; border-radius: 16px;
                font-size: 18px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #3b82f6; color: white; }}
        """)

        self.gallery_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: {text_color};
                border: 2px solid #10b981; border-radius: 16px;
                font-size: 18px; font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #10b981; color: white; }}
        """)

        btn_hover = "#334155" if is_dark else "#e2e8f0"
        border_color = "transparent" if is_dark else "#cbd5e1"
        
        self.history_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: {text_color};
                border: 1px solid {border_color}; border-radius: 8px; font-size: 16px; text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{ background-color: {btn_hover}; }}
        """)

    def pick_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.image_selected.emit(file_name)
