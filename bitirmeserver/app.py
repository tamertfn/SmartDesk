from fastapi import FastAPI
from pydantic import BaseModel
from ultralytics import YOLO
import pandas as pd
import numpy as np
import io
import base64
from PIL import Image

app = FastAPI()

# Modeli yükle
model = YOLO("best.pt")

class PredictRequest(BaseModel):
    image_base64: str
    target_class: str

class_aliases = {
    "Laptop": ["Laptop"],
    "Tablet computer": ["iPad-Air", "iPad-Pro"],
    "Computer keyboard": ["Keyboard"],
    "Computer monitor": ["Screen","PC"],
    "Computer mouse": ["Mouse"],
    "Pen": ["Pen","Marker"],
    "Book": ["Lecture-notes"],
    "Mobile phone": ["Mobile phone"],
    "Headphones": ["Earphones"],
    "Flashlight": [],  # eşleşen sınıf yok
    "Bottle": ["Water bottle"],
    "Mug": [],  # eşleşen sınıf yok
    "Glasses": ["Glasses"],
    "Bowl": [],  # eşleşen sınıf yok
    "Box": ["Bag"],  # yaklaşık eşleşme
    "Camera": [],  # eşleşen sınıf yok
    "Watch": ["Watch"],
    "Coin": [],  # eşleşen sınıf yok
    "Personal care": [],  # eşleşen sınıf yok
    "Fork": [],  # eşleşen sınıf yok
    "Kitchen knife": [],  # eşleşen sınıf yok
    "Spoon": [],  # eşleşen sınıf yok
    "Glove": [],  # eşleşen sınıf yok
    "IPod": [],  # eşleşen sınıf yok
    "Necklace": [],  # eşleşen sınıf yok
    "Snack": [],  # eşleşen sınıf yok
}


@app.post("/predict")
async def predict(req: PredictRequest):
    try:
        # Base64 çöz
        image_data = base64.b64decode(req.image_base64.split(",")[-1])
        im = Image.open(io.BytesIO(image_data)).convert("RGB")

        # YOLO tahmini yap
        results = model.predict(im)

        boxes = results[0].boxes  # Boxes objesi
        xyxy = boxes.xyxy.cpu().numpy()   # (N, 4) -> xmin, ymin, xmax, ymax
        conf = boxes.conf.cpu().numpy()   # (N,) -> confidence
        cls = boxes.cls.cpu().numpy()     # (N,) -> class id
        names = results[0].names          # class id -> class name dict

        if len(xyxy) == 0:
            return {"message": "No objects detected."}

        # DataFrame oluştur
        df = pd.DataFrame(xyxy, columns=["xmin", "ymin", "xmax", "ymax"])
        df["confidence"] = conf
        df["class"] = cls.astype(int)
        df["name"] = df["class"].map(names)

        # İstemciden gelen sınıf adına karşılık gelen sunucu sınıflarını al
        target_names = class_aliases.get(req.target_class, [req.target_class])
        filtered = df[df["name"].isin(target_names)]


        if filtered.empty:
            return {"message": f"No object found for class '{req.target_class}'."}

        CONFIDENCE_THRESHOLD = 0.5  # ihtiyacına göre ayarla

        # En yüksek confidence satırının etiketini al
        top_idx = filtered["confidence"].idxmax()
        top = filtered.loc[top_idx]

        # Eşik kontrolü
        if top["confidence"] < CONFIDENCE_THRESHOLD:
            print("conf esigi asilmadi")
            return {"message": f"No object found for class '{req.target_class}'."}



        result = {
            "class": req.target_class,
            "confidence": float(top["confidence"]),
            "bbox": [
                int(top["xmin"]),
                int(top["ymin"]),
                int(top["xmax"]),
                int(top["ymax"])
            ]
        }
        return result

    except Exception as e:
        return {"error": str(e)}
