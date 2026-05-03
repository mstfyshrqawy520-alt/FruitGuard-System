import torch
import os

model_path = os.path.abspath(os.path.join(r"d:\fruite app\models", "quality_best.pth"))
state_dict = torch.load(model_path, map_location='cpu')

if 'state_dict' in state_dict:
    state_dict = state_dict['state_dict']
elif 'model_state' in state_dict:
    state_dict = state_dict['model_state']

for key in ['fc.weight', 'classifier.weight', 'model.fc.weight']:
    if key in state_dict:
        print(f"{key} shape: {state_dict[key].shape}")
        break
