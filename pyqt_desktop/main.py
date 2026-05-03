import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtGui import QIcon
from auth_screen import AuthScreen
from home_screen import HomeScreen
from camera_screen import CameraScreen
from preview_screen import PreviewScreen
from result_screen import ResultScreen
from profile_screen import ProfileScreen
from app_state import app_state

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fruite AI Desktop")
        self.resize(800, 600)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Initialize screens
        self.auth_screen = AuthScreen()
        self.home_screen = HomeScreen()
        self.camera_screen = CameraScreen()
        self.preview_screen = PreviewScreen()
        self.result_screen = ResultScreen()
        self.profile_screen = ProfileScreen()

        # Add to stack
        self.stacked_widget.addWidget(self.auth_screen)   # Index 0
        self.stacked_widget.addWidget(self.home_screen)   # Index 1
        self.stacked_widget.addWidget(self.camera_screen) # Index 2
        self.stacked_widget.addWidget(self.preview_screen)# Index 3
        self.stacked_widget.addWidget(self.result_screen) # Index 4
        self.stacked_widget.addWidget(self.profile_screen)# Index 5

        # Connect signals
        self.auth_screen.login_successful.connect(self.show_home)
        
        self.home_screen.open_camera.connect(self.show_camera)
        self.home_screen.image_selected.connect(self.show_preview)
        self.home_screen.open_profile.connect(self.show_profile)

        self.camera_screen.go_back.connect(self.show_home)
        self.camera_screen.image_captured.connect(self.show_preview)

        self.preview_screen.go_back.connect(self.show_home)
        self.preview_screen.analysis_complete.connect(self.show_result)

        self.result_screen.go_home.connect(self.show_home)

        self.profile_screen.go_back.connect(self.show_home)
        self.profile_screen.logout.connect(self.show_auth)

        app_state.theme_changed.connect(self.update_theme)
        self.update_theme(app_state.is_dark_mode)

    def update_theme(self, is_dark):
        bg_color = "#0f172a" if is_dark else "#f8fafc"
        self.setStyleSheet(f"background-color: {bg_color};")

    def show_auth(self):
        self.stacked_widget.setCurrentWidget(self.auth_screen)

    def show_home(self):
        self.stacked_widget.setCurrentWidget(self.home_screen)

    def show_camera(self):
        self.camera_screen.start_camera()
        self.stacked_widget.setCurrentWidget(self.camera_screen)

    def show_preview(self, image_path):
        self.preview_screen.set_image(image_path)
        self.stacked_widget.setCurrentWidget(self.preview_screen)

    def show_result(self, data):
        self.result_screen.display_result(data, self.preview_screen.image_path)
        self.stacked_widget.setCurrentWidget(self.result_screen)

    def show_profile(self):
        self.stacked_widget.setCurrentWidget(self.profile_screen)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
