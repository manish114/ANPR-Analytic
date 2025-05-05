import os
import requests

# Create model directory if it doesn't exist
os.makedirs("app/models", exist_ok=True)

# Roboflow-hosted model URL (replace with your model's direct .pt link if needed)
model_url = "https://github.com/murhafsousli/YOLO-License-Plate-Recognition/releases/download/v1.0/best.pt"

# Target path
model_path = "app/models/yolov8_plate.pt"

print(f"Downloading model from {model_url} ...")

response = requests.get(model_url, stream=True)
if response.status_code == 200:
    with open(model_path, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
    print(f"✅ Model saved to: {model_path}")
else:
    print(f"❌ Failed to download model. Status code: {response.status_code}")
