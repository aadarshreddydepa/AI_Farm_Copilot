# app/ml/inference.py
import io
from PIL import Image, ImageOps
import random

# Try to import torch; if available we'll run a lightweight pretrained model
try:
    import torch
    import torchvision.transforms as T
    from torchvision import models
    TORCH_AVAILABLE = True
except Exception:
    TORCH_AVAILABLE = False

# If you run with torch available, this will lazy-load a pretrained model on first call.
_model = None
_labels = None

def _load_model():
    global _model, _labels
    if _model is not None:
        return
    # Using ImageNet labels as placeholders. Replace with your crop-disease labels & model.
    _model = models.mobilenet_v2(pretrained=True)
    _model.eval()
    # load ImageNet labels file from torchvision (or define your own)
    try:
        # small helper to load labels shipped with torchvision (if available)
        import json, pkgutil
        data = pkgutil.get_data("torchvision", "imagenet_classes.txt")
        if data:
            _labels = [l.decode("utf-8").strip() for l in data.splitlines()]
    except Exception:
        _labels = None

transform = T.Compose([
    T.Resize(256),
    T.CenterCrop(224),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]),
])

def predict_image_bytes(image_bytes: bytes):
    """
    Returns a prediction dict: { label: str, score: float }
    If torch is not available, returns a mock deterministic label.
    """
    if TORCH_AVAILABLE:
        global _model, _labels
        if _model is None:
            _load_model()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_t = transform(img).unsqueeze(0)  # add batch dim
        with torch.no_grad():
            out = _model(img_t)
            probs = torch.nn.functional.softmax(out[0], dim=0)
            top1 = torch.topk(probs, k=1)
            idx = int(top1.indices[0].item())
            score = float(top1.values[0].item())
            label = _labels[idx] if _labels else f"imagenet_{idx}"
            return {"label": label, "score": score}
    else:
        # Deterministic fallback: hash length of bytes to make repeatable deterministic "predictions".
        h = len(image_bytes) % 3
        if h == 0:
            return {"label": "healthy", "score": 0.85}
        elif h == 1:
            return {"label": "diseased", "score": 0.73}
        else:
            return {"label": "nutrient_deficit", "score": 0.62}
