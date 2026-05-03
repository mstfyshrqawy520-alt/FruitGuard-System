import sys
import os
from PIL import Image
import torch

# Add backend directory to sys path so we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.model_service import load_models, analyze_fruit

image_path = r"C:\Users\sasam\.gemini\antigravity\brain\b5d69542-0a14-42d9-a116-569a7bfd9f3d\test_apple_1777476095367.png"

try:
    print("Initializing models...")
    load_models()
    
    print("\nLoading image...")
    img = Image.open(image_path).convert("RGB")
    
    print("\nRunning inference pipeline...")
    result = analyze_fruit(img)
    
    print("\n--- INFERENCE RESULTS ---")
    print(f"Fruit: {result['fruit_name']} (Conf: {result['confidence']})")
    print(f"Quality: {result['quality']} (Conf: {result['quality_confidence']})")
    print(f"Size: {result['size_cm']} cm2")
    print(f"Low Confidence Failsafe Triggered: {result['low_confidence']}")
    
    if 'mask' in result and result['mask'].startswith('data:image'):
        print("Mask Base64: GENERATED SUCCESSFULLY")
        import base64
        from io import BytesIO
        base64_str = result['mask'].split(",")[1]
        img_data = base64.b64decode(base64_str)
        mask_img = Image.open(BytesIO(img_data))
        out_path = r"C:\Users\sasam\.gemini\antigravity\brain\b5d69542-0a14-42d9-a116-569a7bfd9f3d\scratch\mask_overlay.jpg"
        import os
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        mask_img.save(out_path)
        print(f"Mask overlay saved to: {out_path}")
        
        # Save raw mask
        raw_mask_str = result['raw_mask'].split(",")[1]
        raw_mask_data = base64.b64decode(raw_mask_str)
        raw_img = Image.open(BytesIO(raw_mask_data))
        raw_out_path = r"C:\Users\sasam\.gemini\antigravity\brain\b5d69542-0a14-42d9-a116-569a7bfd9f3d\scratch\raw_mask.jpg"
        raw_img.save(raw_out_path)
        print(f"Raw mask saved to: {raw_out_path}")
        
        # Save cropped image
        crop_str = result['cropped_image'].split(",")[1]
        crop_data = base64.b64decode(crop_str)
        crop_img = Image.open(BytesIO(crop_data))
        crop_out_path = r"C:\Users\sasam\.gemini\antigravity\brain\b5d69542-0a14-42d9-a116-569a7bfd9f3d\scratch\cropped_image.jpg"
        crop_img.save(crop_out_path)
        print(f"Cropped image saved to: {crop_out_path}")
        
    else:
        print("Mask Base64: FAILED")
        
except Exception as e:
    print(f"\n[ERROR] Pipeline failed: {e}")
