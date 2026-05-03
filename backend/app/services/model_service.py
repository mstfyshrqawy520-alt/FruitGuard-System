import os
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
from ..utils.image_processing import image_to_base64, crop_image

# Constants for Paths
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models"))
SEG_MODEL_PATH = os.path.join(MODEL_DIR, "best_seg.pt")
CLASS_MODEL_PATH = os.path.join(MODEL_DIR, "fruit_classifier.pth")
QUAL_MODEL_PATH = os.path.join(MODEL_DIR, "quality_best.pth")

DEBUG = True  # Added Debug flag

# Global model variables
seg_model = None
class_model = None
qual_model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Transformation for classification and quality models (ResNet18 standard)
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Dummy class names (Ideally these would be provided or saved with the model)
# We will fallback to "Fruit Class {i}" if we don't have enough names
class_names = [
    'Amaranth','Apple','Banana','Beetroot','Bell pepper','Bitter Gourd',
    'Blueberry','Bottle Gourd','Broccoli','Cabbage','Cantaloupe','Capsicum',
    'Carrot','Cauliflower','Chilli pepper','Coconut','Corn','Cucumber',
    'Dragon_fruit','Eggplant','Fig','Garlic','Ginger','Grapes','Jalepeno',
    'Kiwi','Lemon','Mango','Okra','Onion','Orange','Paprika','Pear','Peas',
    'Pineapple','Pomegranate','Potato','Pumpkin','Raddish','Raspberry',
    'Ridge Gourd','Soy beans','Spinach','Spiny Gourd','Sponge Gourd',
    'Strawberry','Sweetcorn','Sweetpotato','Tomato','Turnip','Watermelon'
]
QUALITY_CLASSES = ["rotten", "fresh"]

def load_resnet_model(model_path, num_classes=None):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}. Please ensure models are placed in the /models directory.")
    
    # Load state dict first to infer num_classes if not provided
    try:
        state_dict = torch.load(model_path, map_location=device)
    except Exception as e:
        raise RuntimeError(f"Failed to load state dict from {model_path}: {e}")
    
    # Handle DataParallel or normal state dicts
    if 'state_dict' in state_dict:
        state_dict = state_dict['state_dict']
    elif 'model_state' in state_dict:
        state_dict = state_dict['model_state']
    
    if num_classes is None:
        # Infer from the fully connected layer weight
        for key in ['fc.weight', 'classifier.weight', 'model.fc.weight']:
            if key in state_dict:
                num_classes = state_dict[key].shape[0]
                break
    
    if num_classes is None:
        raise ValueError(f"Could not infer num_classes from {model_path}. Provide num_classes explicitly.")

    # Infer ResNet type based on final layer input features
    num_ftrs = 512
    for key in ['fc.weight', 'classifier.weight', 'model.fc.weight']:
        if key in state_dict:
            num_ftrs = state_dict[key].shape[1]
            break
            
    if num_ftrs == 2048:
        model = models.resnet50(weights=None)
    else:
        model = models.resnet18(weights=None)
        
    model.fc = torch.nn.Linear(num_ftrs, num_classes)
    
    # Remove module. prefix if saved with DataParallel
    new_state_dict = {}
    for k, v in state_dict.items():
        name = k.replace('module.', '') if k.startswith('module.') else k
        new_state_dict[name] = v
        
    try:
        model.load_state_dict(new_state_dict, strict=True)
    except RuntimeError as e:
        raise RuntimeError(f"Strict loading failed for {model_path}. Ensure the architecture is exactly ResNet18: {e}")

    model.to(device)
    model.eval()
    return model

try:
    from transformers import pipeline
    clip_classifier = None
except ImportError:
    clip_classifier = None

def load_models():
    global seg_model, class_model, qual_model, clip_classifier
    print("Loading models...")
    
    # 1. Load YOLO Segmentation model
    if os.path.exists(SEG_MODEL_PATH):
        seg_model = YOLO(SEG_MODEL_PATH)
        print("Segmentation model loaded.")
    else:
        raise FileNotFoundError(f"Segmentation model not found at {SEG_MODEL_PATH}")

    # 2. Load Classification model
    class_model = load_resnet_model(CLASS_MODEL_PATH)
    print("Classification model loaded.")

    # 3. Load HuggingFace CLIP for Zero-Shot Quality (Replaces broken qual_model)
    try:
        from transformers import pipeline
        print("Loading HuggingFace CLIP model for zero-shot quality analysis...")
        clip_classifier = pipeline(
            "zero-shot-image-classification", 
            model="openai/clip-vit-base-patch32",
            device=0 if torch.cuda.is_available() else -1
        )
        print("CLIP loaded successfully.")
    except Exception as e:
        print(f"Could not load HuggingFace CLIP (Please install 'transformers'): {e}")

def predict_class(image: Image.Image) -> tuple[str, float]:
    if class_model is None:
        raise RuntimeError("Classification model is not loaded")
    
    input_tensor = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = class_model(input_tensor)
        logits = outputs[0]
        
        if DEBUG:
            top3_logits, _ = torch.topk(logits, 3)
            print(f"[DEBUG] Raw classifier top 3 logits: {[round(l, 4) for l in top3_logits.tolist()]}")
            
        # Apply Temperature Scaling to smooth the distribution
        temperature = 2.0
        scaled_logits = logits / temperature
        
        probabilities = torch.nn.functional.softmax(scaled_logits, dim=0)
        
        if DEBUG:
            top3_prob, top3_idx = torch.topk(probabilities, 3)
            print("[DEBUG] Classifier Top 3 Predictions:")
            for i in range(3):
                p = top3_prob[i].item()
                idx = top3_idx[i].item()
                print(f"  {i+1}. {class_names[idx]} (Conf: {p:.4f})")
                
        confidence, predicted = torch.max(probabilities, 0)
        
        conf_val = confidence.item()
        class_idx = predicted.item()
        
        if class_idx < 0 or class_idx >= len(class_names):
            raise ValueError(f"Predicted index {class_idx} is out of bounds for class names.")
            
        if DEBUG:
            print(f"[DEBUG] Predicted index: {class_idx}")
            print(f"[DEBUG] Fruit name: {class_names[class_idx]}")
        
        fruit_name = class_names[class_idx]
        return fruit_name, conf_val

def predict_quality(image: Image.Image, fruit_name: str) -> tuple[str, float]:
    global clip_classifier
    
    # 1. Use Hugging Face CLIP (if installed and loaded)
    if clip_classifier is not None:
        try:
            labels = [f"fresh {fruit_name}", f"rotten {fruit_name}"]
            results = clip_classifier(image, candidate_labels=labels)
            
            # results[0] is the most likely label
            best_label = results[0]['label']
            confidence = results[0]['score']
            
            if DEBUG:
                print(f"[DEBUG] HuggingFace CLIP Results: {results}")
                
            quality = "rotten" if "rotten" in best_label else "fresh"
            return quality, round(confidence, 4)
        except Exception as e:
            if DEBUG:
                print(f"[DEBUG] CLIP failed: {e}. Falling back to OpenCV heuristic.")

    # 2. Fallback: Advanced OpenCV Computer Vision heuristic
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Ignore background pixels (black)
    _, fruit_mask = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
    fruit_pixels = cv2.countNonZero(fruit_mask)
    
    if fruit_pixels == 0:
        return "unknown", 0.0
        
    # Analyze Brown / Dark colors (Rotting spots)
    # Hue 12-25 is true brown. Hue < 10 is RED (like capsicum/apple), Hue > 25 is YELLOW.
    lower_brown = np.array([12, 40, 20])
    upper_brown = np.array([25, 255, 140])
    brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
    
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([179, 255, 25]) # Only extremely black spots are rot
    dark_mask = cv2.inRange(hsv, lower_dark, upper_dark)
    
    decay_mask = cv2.bitwise_or(brown_mask, dark_mask)
    decay_mask = cv2.bitwise_and(decay_mask, fruit_mask)
    
    decay_pixels = cv2.countNonZero(decay_mask)
    decay_ratio = decay_pixels / fruit_pixels
    
    if DEBUG:
        print(f"[DEBUG] Quality Heuristic [{fruit_name}] - Decay Ratio: {decay_ratio:.4f}")

    # Naturally brown or rough fruits should have different thresholds
    naturally_brown = ['Coconut', 'Potato', 'Kiwi', 'Fig', 'Ginger', 'Sweetpotato', 'Garlic', 'Onion']
    
    # Dynamic Thresholds
    decay_threshold = 0.45 if fruit_name in naturally_brown else 0.20
    
    is_rotten = False
    confidence = 0.50
    
    # Rotten condition (only decay ratio, removed laplacian texture because it fails on blurry images)
    if decay_ratio > decay_threshold:
        is_rotten = True
        confidence += min(0.48, (decay_ratio * 1.5))
    else:
        is_rotten = False
        confidence += min(0.49, ((decay_threshold - decay_ratio) * 2.5))

    quality = "rotten" if is_rotten else "fresh"
    return quality, min(0.99, confidence)

def analyze_fruit(image: Image.Image) -> dict:
    if seg_model is None:
        raise Exception("Segmentation model is not loaded")

    # 1. Segmentation (YOLO) with lower threshold to capture more detections for logging
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    results = seg_model(img_cv, conf=0.20)
    
    if not results or len(results) == 0 or results[0].masks is None:
        raise Exception("No object detected")
        
    result = results[0]
    boxes = result.boxes
    if len(boxes) == 0:
        raise Exception("No object detected")
        
    # Log top 3 detections for debugging
    if DEBUG:
        sorted_indices = torch.argsort(boxes.conf, descending=True)
        top_k = min(3, len(sorted_indices))
        print(f"[DEBUG] Total YOLO detections: {len(boxes)}")
        for i in range(top_k):
            idx = sorted_indices[i].item()
            print(f"[DEBUG] Detection {i+1}: Conf = {boxes.conf[idx].item():.4f}")

    best_idx = torch.argmax(boxes.conf).item()
    best_conf = boxes.conf[best_idx].item()
    
    # 1. Enforce strict rejection threshold for weak detections
    if best_conf < 0.25:
        raise Exception(f"Detection confidence too low ({best_conf:.4f}). Please take a clearer photo.")
    
    # 2. Extract Mask
    mask_tensor = result.masks.data[best_idx]
    mask_np = mask_tensor.cpu().numpy()
    mask_np = cv2.resize(mask_np, (img_cv.shape[1], img_cv.shape[0]))
    
    # Convert to binary
    binary_mask = (mask_np > 0.5).astype(np.uint8)
    
    # Morphology (Erosion + Dilation = Opening) to remove noise
    kernel = np.ones((5,5), np.uint8)
    cleaned_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)
    
    # Optional: Gaussian Blur for smooth edges
    blurred_mask = cv2.GaussianBlur(cleaned_mask.astype(np.float32), (5,5), 0)
    final_mask = (blurred_mask > 0.5).astype(np.uint8)
    
    # Get mask-based Bounding Box
    y_indices, x_indices = np.where(final_mask > 0)
    if len(y_indices) == 0 or len(x_indices) == 0:
        raise Exception("No object detected after mask processing")
    
    x_min, x_max = x_indices.min(), x_indices.max()
    y_min, y_max = y_indices.min(), y_indices.max()
    mask_bbox = [x_min, y_min, x_max, y_max]
    
    pixel_area = np.sum(final_mask > 0)
    bbox_area = max(1, (x_max - x_min) * (y_max - y_min))
    mask_ratio = pixel_area / bbox_area
    
    # Size calibration (Option B)
    PIXELS_PER_CM = float(os.environ.get("PIXELS_PER_CM", 10.0))  # Set default to 10.0
    import math
    size_cm = float(math.sqrt(pixel_area) / PIXELS_PER_CM)
    
    if DEBUG:
        print(f"[DEBUG] Best confidence: {best_conf:.4f}")
        print(f"[DEBUG] Mask area: {pixel_area}, BBox area: {bbox_area}")
        print(f"[DEBUG] Mask Pixel Ratio vs BBox: {mask_ratio:.4f}")
    
    # Create visual mask overlay for frontend
    colored_mask = np.zeros_like(img_cv)
    colored_mask[final_mask > 0] = [0, 0, 255] # BGR Red
    overlay_img = cv2.addWeighted(img_cv, 0.7, colored_mask, 0.3, 0)
    
    # Draw tightly cropped bounding box
    cv2.rectangle(overlay_img, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)
    
    overlay_pil = Image.fromarray(cv2.cvtColor(overlay_img, cv2.COLOR_BGR2RGB))
    mask_base64 = image_to_base64(overlay_pil)
    
    # Generate raw mask image for visual validation
    raw_mask_pil = Image.fromarray(final_mask * 255)
    raw_mask_base64 = image_to_base64(raw_mask_pil)
    
    # 3. Apply Mask and Crop tightly using mask-based bbox
    img_array = np.array(image)
    mask_3d = np.repeat(final_mask[:, :, np.newaxis], 3, axis=2)
    img_array[mask_3d == 0] = 0  # Black out background
    
    masked_pil = Image.fromarray(img_array)
    cropped_image = crop_image(masked_pil, mask_bbox)
    cropped_base64 = image_to_base64(cropped_image)
    
    # Generate unmasked cropped image for models (models usually fail on black backgrounds if not trained on them)
    unmasked_cropped_image = crop_image(image, mask_bbox)
    
    if DEBUG:
        print(f"[DEBUG] Crop shape: {cropped_image.size}")
    
    # 4. Pass unmasked cropped image to Classification
    fruit_name, class_conf = predict_class(unmasked_cropped_image)
    
    # Pass masked image to our OpenCV heuristic so it doesn't analyze the background!
    quality, qual_conf = predict_quality(cropped_image, fruit_name)
    
    # 5. Combined Low Confidence Flag
    # Triggered if YOLO is weak (<0.35) or Classifier is weak (<0.60)
    low_confidence = (best_conf < 0.35) or (class_conf < 0.60)
    
    if DEBUG:
        print(f"[DEBUG] Classifier Output: {fruit_name} (Conf: {class_conf:.4f})")
        print(f"[DEBUG] Quality Output: {quality} (Conf: {qual_conf:.4f})")
        print(f"[DEBUG] Final Low Confidence Flag: {low_confidence} (YOLO: {best_conf:.4f}, Class: {class_conf:.4f})")
    
    return {
        "fruit_name": fruit_name,
        "confidence": round(class_conf, 4),
        "quality": quality,
        "quality_confidence": round(qual_conf, 4),
        "size_cm": round(size_cm, 2),
        "mask": mask_base64,
        "raw_mask": raw_mask_base64,
        "cropped_image": cropped_base64,
        "low_confidence": low_confidence
    }
