from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from app_state import app_state

class ProfileScreen(QWidget):
    go_back = pyqtSignal()
    logout = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        app_state.language_changed.connect(self.update_texts)
        app_state.theme_changed.connect(self.update_theme)
        app_state.user_changed.connect(self.update_user)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header Row (Title + Back)
        header_layout = QHBoxLayout()
        self.title = QLabel(app_state.t('profile_settings'))
        self.title.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        header_layout.addWidget(self.title)
        
        header_layout.addStretch()
        
        self.back_btn = QPushButton(app_state.t('back_home'))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #3b82f6; font-weight: bold; font-size: 16px; border: none;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        self.back_btn.clicked.connect(self.go_back.emit)
        header_layout.addWidget(self.back_btn)
        self.main_layout.addLayout(header_layout)

        self.main_layout.addSpacing(40)

        # Avatar & Name
        avatar_layout = QVBoxLayout()
        avatar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label = QLabel("👤")
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("font-size: 60px;")
        avatar_layout.addWidget(self.avatar_label)

        self.name_label = QLabel(app_state.username)
        self.name_label.setStyleSheet("font-size: 22px; font-weight: bold; color: white;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_layout.addWidget(self.name_label)
        self.main_layout.addLayout(avatar_layout)

        self.main_layout.addSpacing(40)

        # Preferences
        self.pref_label = QLabel(app_state.t('preferences'))
        self.pref_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        self.main_layout.addWidget(self.pref_label)

        # Toggle Theme
        self.theme_btn = QPushButton(f"{app_state.t('dark_mode')}: {'ON' if app_state.is_dark_mode else 'OFF'}")
        self.theme_btn.setFixedHeight(50)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.main_layout.addWidget(self.theme_btn)

        # Toggle Language
        lang_text = 'Arabic' if app_state.language == 'ar' else 'English'
        self.lang_btn = QPushButton(f"{app_state.t('language')}: {lang_text}")
        self.lang_btn.setFixedHeight(50)
        self.lang_btn.clicked.connect(self.toggle_language)
        self.main_layout.addWidget(self.lang_btn)

        self.main_layout.addSpacing(20)

        # Account
        self.account_label = QLabel(app_state.t('account'))
        self.account_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        self.main_layout.addWidget(self.account_label)

        self.logout_btn = QPushButton(app_state.t('logout'))
        self.logout_btn.setFixedHeight(50)
        self.logout_btn.clicked.connect(self.logout.emit)
        self.main_layout.addWidget(self.logout_btn)

        self.main_layout.addStretch()
        self.update_theme(app_state.is_dark_mode)

    def toggle_theme(self):
        app_state.toggle_theme()

    def toggle_language(self):
        app_state.toggle_language()

    def update_user(self, name):
        self.name_label.setText(name)

    def update_texts(self, lang=None):
        self.title.setText(app_state.t('profile_settings'))
        self.back_btn.setText(app_state.t('back_home'))
        self.pref_label.setText(app_state.t('preferences'))
        self.account_label.setText(app_state.t('account'))
        self.logout_btn.setText(app_state.t('logout'))
        lang_text = app_state.t('arabic') if app_state.language == 'ar' else app_state.t('english')
        self.lang_btn.setText(f"{app_state.t('language')}: {lang_text}")
        self.theme_btn.setText(f"{app_state.t('dark_mode')}: {'ON' if app_state.is_dark_mode else 'OFF'}")

    def update_theme(self, is_dark):
        bg_color = "#1e293b" if is_dark else "#ffffff"
        text_color = "white" if is_dark else "black"
        border_color = "#334155" if is_dark else "#cbd5e1"
        btn_bg = "#1e293b" if is_dark else "#f1f5f9"
        btn_hover = "#334155" if is_dark else "#e2e8f0"

        self.title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {text_color};")
        self.name_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {text_color};")
        self.pref_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {text_color};")
        self.account_label.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {text_color};")

        btn_style = f"""
            QPushButton {{
                background-color: {btn_bg}; color: {text_color};
                border: 1px solid {border_color}; border-radius: 8px; font-size: 16px; text-align: left; padding-left: 20px;
            }}
            QPushButton:hover {{ background-color: {btn_hover}; }}
        """
        self.theme_btn.setStyleSheet(btn_style)
        self.lang_btn.setStyleSheet(btn_style)

        self.logout_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg}; color: #ef4444; font-weight: bold;
                border: 1px solid {border_color}; border-radius: 8px; font-size: 16px; text-align: left; padding-left: 20px;
            }}
            QPushButton:hover {{ background-color: #fecaca; color: #b91c1c; }}
        """)

        # Re-set toggle button texts to show ON/OFF correctly based on new state
        self.theme_btn.setText(f"{app_state.t('dark_mode')}: {'ON' if is_dark else 'OFF'}")
