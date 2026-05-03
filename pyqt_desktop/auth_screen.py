from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from api_client import api
from app_state import app_state
import os

class AuthScreen(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_login = True
        self.init_ui()
        app_state.language_changed.connect(self.update_texts)
        app_state.theme_changed.connect(self.update_theme)

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(pixmap)
        self.main_layout.addWidget(self.logo_label)
        self.main_layout.addSpacing(10)

        # Title
        self.title_label = QLabel(app_state.t('app_name'))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel(app_state.t('login_subtitle'))
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.subtitle_label)

        self.main_layout.addSpacing(30)

        # Name Input (Hidden by default)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(app_state.t('full_name'))
        self.name_input.setFixedWidth(300)
        self.name_input.hide()
        self.main_layout.addWidget(self.name_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addSpacing(10)

        # Email Input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText(app_state.t('email'))
        self.email_input.setFixedWidth(300)
        self.main_layout.addWidget(self.email_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.main_layout.addSpacing(10)

        # Password Input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(app_state.t('password'))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedWidth(300)
        self.main_layout.addWidget(self.password_input, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addSpacing(20)

        # Main Button
        self.action_btn = QPushButton(app_state.t('login_btn'))
        self.action_btn.setFixedWidth(300)
        self.action_btn.clicked.connect(self.handle_action)
        self.main_layout.addWidget(self.action_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addSpacing(10)

        # Toggle Button
        self.toggle_btn = QPushButton(app_state.t('need_account'))
        self.toggle_btn.setFixedWidth(300)
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_mode)
        self.main_layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.update_theme(app_state.is_dark_mode)

    def update_texts(self, lang=None):
        self.title_label.setText(app_state.t('app_name'))
        self.subtitle_label.setText(app_state.t('login_subtitle') if self.is_login else app_state.t('create_subtitle'))
        self.name_input.setPlaceholderText(app_state.t('full_name'))
        self.email_input.setPlaceholderText(app_state.t('email'))
        self.password_input.setPlaceholderText(app_state.t('password'))
        self.action_btn.setText(app_state.t('login_btn') if self.is_login else app_state.t('register_btn'))
        self.toggle_btn.setText(app_state.t('need_account') if self.is_login else app_state.t('have_account'))

    def update_theme(self, is_dark):
        bg_color = "#1e293b" if is_dark else "#ffffff"
        text_color = "white" if is_dark else "black"
        border_color = "#334155" if is_dark else "#cbd5e1"
        sub_text_color = "#94a3b8" if is_dark else "#64748b"

        self.title_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {text_color};")
        self.subtitle_label.setStyleSheet(f"font-size: 16px; color: {sub_text_color};")

        input_style = f"""
            QLineEdit {{
                padding: 12px; border-radius: 8px;
                background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color};
            }}
        """
        self.name_input.setStyleSheet(input_style)
        self.email_input.setStyleSheet(input_style)
        self.password_input.setStyleSheet(input_style)

        self.action_btn.setStyleSheet("""
            QPushButton {
                padding: 12px; border-radius: 8px; font-weight: bold;
                background-color: #3b82f6; color: white; border: none;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)

        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 8px; color: {text_color}; background-color: transparent; border: none;
            }}
            QPushButton:hover {{ text-decoration: underline; }}
        """)

    def toggle_mode(self):
        self.is_login = not self.is_login
        self.name_input.setVisible(not self.is_login)
        self.update_texts()

    def handle_action(self):
        email = self.email_input.text()
        password = self.password_input.text()
        name = self.name_input.text()

        if not email or not password or (not self.is_login and not name):
            QMessageBox.warning(self, app_state.t('error'), app_state.t('fill_fields'))
            return

        self.action_btn.setEnabled(False)

        if self.is_login:
            self.action_btn.setText(app_state.t('logging_in'))
            success, msg = api.login(email, password)
            if success:
                self.login_successful.emit()
            else:
                QMessageBox.critical(self, app_state.t('login_failed'), msg)
        else:
            self.action_btn.setText(app_state.t('registering'))
            success, msg = api.register(name, email, password)
            if success:
                success_login, msg_login = api.login(email, password)
                if success_login:
                    self.login_successful.emit()
                else:
                    QMessageBox.critical(self, app_state.t('login_failed'), msg_login)
            else:
                QMessageBox.critical(self, app_state.t('register_failed'), msg)

        self.action_btn.setEnabled(True)
        self.update_texts()
