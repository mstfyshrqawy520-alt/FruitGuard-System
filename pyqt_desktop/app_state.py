from PyQt6.QtCore import QObject, pyqtSignal
from translations import TRANSLATIONS
import json
import os

class AppState(QObject):
    theme_changed = pyqtSignal(bool) # True = Dark, False = Light
    language_changed = pyqtSignal(str) # 'en' or 'ar'
    user_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._is_dark_mode = True
        self._language = 'en'
        self._username = "User Account"
        self._settings_file = "settings.json"
        self.load_settings()

    @property
    def is_dark_mode(self):
        return self._is_dark_mode

    @is_dark_mode.setter
    def is_dark_mode(self, value):
        self._is_dark_mode = value
        self.save_settings()
        self.theme_changed.emit(self._is_dark_mode)

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        if value in ['en', 'ar']:
            self._language = value
            self.save_settings()
            self.language_changed.emit(self._language)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value
        self.user_changed.emit(self._username)

    def t(self, key):
        return TRANSLATIONS.get(self._language, TRANSLATIONS['en']).get(key, key)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode

    def toggle_language(self):
        self.language = 'ar' if self.language == 'en' else 'en'

    def load_settings(self):
        if os.path.exists(self._settings_file):
            try:
                with open(self._settings_file, 'r') as f:
                    data = json.load(f)
                    self._is_dark_mode = data.get('is_dark_mode', True)
                    self._language = data.get('language', 'en')
            except:
                pass

    def save_settings(self):
        try:
            with open(self._settings_file, 'w') as f:
                json.dump({
                    'is_dark_mode': self._is_dark_mode,
                    'language': self._language
                }, f)
        except:
            pass

app_state = AppState()
