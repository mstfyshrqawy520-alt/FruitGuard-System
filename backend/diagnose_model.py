import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import sys
import os

device = torch.device("cpu")

def load_resnet_model(model_path, num_classes=2):
    state_dict = torch.load(model_path, map_location=device)
    if 'state_dict' in state_dict:
        state_dict = state_dict['state_dict']
    elif 'model_state' in state_dict:
        state_dict = state_dict['model_state']
        
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
    
    new_state_dict = {}
    for k, v in state_dict.items():
        name = k.replace('module.', '') if k.startswith('module.') else k
        new_state_dict[name] = v
        
    model.load_state_dict(new_state_dict, strict=True)
    model.to(device)
    model.eval()
    return model

if __name__ == "__main__":
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/quality_best.pth"))
    print(f"Loading model from {model_path}...")
    try:
        model = load_resnet_model(model_path, num_classes=2)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)
        
    # Test with dummy data
    print("\nTesting with purely black image (simulating heavily masked dark fruit)...")
    dummy_black = torch.zeros(1, 3, 224, 224)
    with torch.no_grad():
        out_black = model(dummy_black)
        prob_black = torch.nn.functional.softmax(out_black[0], dim=0)
        print(f"Logits: {out_black[0].tolist()}")
        print(f"Probabilities: {prob_black.tolist()}")
        print(f"Predicted Class Index: {torch.argmax(prob_black).item()}")

    print("\nTesting with purely white image...")
    dummy_white = torch.ones(1, 3, 224, 224)
    with torch.no_grad():
        out_white = model(dummy_white)
        prob_white = torch.nn.functional.softmax(out_white[0], dim=0)
        print(f"Logits: {out_white[0].tolist()}")
        print(f"Probabilities: {prob_white.tolist()}")
        print(f"Predicted Class Index: {torch.argmax(prob_white).item()}")

    print("\nTesting with random noise image...")
    dummy_noise = torch.rand(1, 3, 224, 224)
    with torch.no_grad():
        out_noise = model(dummy_noise)
        prob_noise = torch.nn.functional.softmax(out_noise[0], dim=0)
        print(f"Logits: {out_noise[0].tolist()}")
        print(f"Probabilities: {prob_noise.tolist()}")
        print(f"Predicted Class Index: {torch.argmax(prob_noise).item()}")
