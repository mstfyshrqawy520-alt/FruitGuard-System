import requests
import sys

# We need an image path
image_path = r"C:\Users\sasam\.gemini\antigravity\brain\b5d69542-0a14-42d9-a116-569a7bfd9f3d\test_apple_1777476095367.png"

url = "http://127.0.0.1:8000/api/analyze"

try:
    with open(image_path, 'rb') as f:
        files = {'file': ('test_apple.png', f, 'image/png')}
        # Note: authentication is required. Wait, the endpoint uses Depends(get_current_user)
        # We need a token first.
        # Register a test user
        auth_url = "http://127.0.0.1:8000/auth"
        requests.post(f"{auth_url}/register", json={"email": "test2@test.com", "password": "password123"})
        
        # Login to get token
        login_res = requests.post(f"{auth_url}/login", data={"username": "test2@test.com", "password": "password123"})
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.text}")
            sys.exit(1)
            
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("Sending image for analysis...")
        res = requests.post(url, files=files, headers=headers)
        
        if res.status_code == 200:
            data = res.json()
            print("API Response received successfully!")
            print(f"Fruit Name: {data['fruit_name']} (Conf: {data['confidence']})")
            print(f"Quality: {data['quality']} (Conf: {data['quality_confidence']})")
            print(f"Size: {data['size_cm']} cm2")
        else:
            print(f"Error {res.status_code}: {res.text}")
except Exception as e:
    print(f"Error: {e}")
