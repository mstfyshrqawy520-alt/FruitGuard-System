import sys
import os
import cv2
import numpy as np
from PIL import Image

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.model_service import load_models, predict_class

image_path = r"C:\Users\sasam\.gemini\antigravity\brain\b5d69542-0a14-42d9-a116-569a7bfd9f3d\test_apple_1777476095367.png"

def add_noise_and_blur(img_path):
    # Read image
    img = cv2.imread(img_path)
    # Add Gaussian Noise
    gauss = np.random.normal(0, 50, img.size)
    gauss = gauss.reshape(img.shape[0], img.shape[1], img.shape[2]).astype('uint8')
    noisy = cv2.add(img, gauss)
    # Add Blur
    blurred = cv2.GaussianBlur(noisy, (15, 15), 0)
    # Dim the lighting
    dimmed = cv2.addWeighted(blurred, 0.5, np.zeros(blurred.shape, blurred.dtype), 0, 0)
    
    # Convert to PIL
    return Image.fromarray(cv2.cvtColor(dimmed, cv2.COLOR_BGR2RGB))

try:
    print("Loading models...")
    load_models()
    
    print("\nApplying heavy noise and blur to simulate poor lighting/camera quality...")
    noisy_img = add_noise_and_blur(image_path)
    
    # Save the noisy image for visual reference
    noisy_img.save("noisy_test_apple.jpg")
    
    print("\nRunning classifier directly on noisy image...")
    fruit_name, class_conf = predict_class(noisy_img)
    
    print("\n--- CLASSIFIER RESULTS (NOISY IMAGE) ---")
    print(f"Fruit: {fruit_name} (Conf: {class_conf:.4f})")
    
except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
