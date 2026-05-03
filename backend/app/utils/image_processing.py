import base64
from io import BytesIO
from PIL import Image
import numpy as np

def base64_to_image(base64_str: str) -> Image.Image:
    if "base64," in base64_str:
        base64_str = base64_str.split("base64,")[1]
    image_data = base64.b64decode(base64_str)
    image = Image.open(BytesIO(image_data)).convert("RGB")
    return image

def image_to_base64(image: Image.Image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{img_str}"

def crop_image(image: Image.Image, bbox: list) -> Image.Image:
    """
    Crops the image based on bounding box [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = map(int, bbox)
    return image.crop((x1, y1, x2, y2))
