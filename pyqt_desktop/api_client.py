import requests
import os

BASE_URL = "http://127.0.0.1:8000"

class ApiClient:
    def __init__(self):
        self.token = None

    def set_token(self, token: str):
        self.token = token

    def get_headers(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def login(self, username, password):
        # The backend uses OAuth2PasswordRequestForm which requires form data (x-www-form-urlencoded)
        data = {"username": username, "password": password}
        try:
            response = requests.post(f"{BASE_URL}/auth/login", data=data, timeout=5)
            response.raise_for_status()
            token_data = response.json()
            self.set_token(token_data.get("access_token"))
            name = token_data.get("name")
            if name:
                from app_state import app_state
                app_state.username = name
            return True, "Success"
        except requests.exceptions.RequestException as e:
            msg = "Login failed."
            if e.response is not None:
                try:
                    msg = e.response.json().get("detail", msg)
                except:
                    pass
            return False, msg

    def register(self, name, email, password):
        data = {"name": name, "email": email, "password": password}
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=data, timeout=5)
            response.raise_for_status()
            return True, "Registration successful"
        except requests.exceptions.RequestException as e:
            msg = "Registration failed."
            if e.response is not None:
                try:
                    msg = e.response.json().get("detail", msg)
                except:
                    pass
            return False, msg

    def analyze_image(self, image_path):
        if not self.token:
            return False, "Not authenticated."
        try:
            with open(image_path, "rb") as f:
                files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
                response = requests.post(
                    f"{BASE_URL}/api/analyze", 
                    files=files, 
                    headers=self.get_headers(),
                    timeout=30
                )
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            msg = f"Analysis failed: {e}"
            if e.response is not None:
                try:
                    msg = e.response.json().get("detail", msg)
                except:
                    pass
            return False, msg

    def get_history(self):
        if not self.token:
            return False, "Not authenticated."
        try:
            response = requests.get(f"{BASE_URL}/api/history", headers=self.get_headers(), timeout=5)
            response.raise_for_status()
            return True, response.json()
        except requests.exceptions.RequestException as e:
            return False, str(e)

# Global API client instance
api = ApiClient()
