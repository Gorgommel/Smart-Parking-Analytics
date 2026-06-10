from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from app.core.config import get_settings


VEHICLE_CLASSES = {"car", "motorcycle", "pickup", "van", "truck", "bus"}


class YoloService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = None
        self.model_status = "demo"
        if not self.settings.demo_mode:
            self._try_load_model()

    def _try_load_model(self) -> None:
        try:
            from ultralytics import YOLO

            model_source = (
                str(self.settings.model_path)
                if self.settings.model_path.exists()
                else self.settings.fallback_model
            )
            self.model = YOLO(model_source)
            self.model_status = f"loaded:{model_source}"
        except Exception as exc:
            self.model = None
            self.model_status = f"demo:{exc.__class__.__name__}"

    def predict(self, image_path: Path) -> list[dict[str, Any]]:
        if self.model is None:
            return self._demo_predict(image_path)

        results = self.model.predict(
            source=str(image_path),
            conf=self.settings.confidence_threshold,
            verbose=False,
        )
        detections: list[dict[str, Any]] = []
        names = results[0].names
        for box in results[0].boxes:
            class_name = names[int(box.cls[0])]
            mapped_name = self._map_class(class_name)
            if mapped_name not in {"car", "motorcycle", "pickup", "van"}:
                continue
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            detections.append(
                {
                    "class_name": mapped_name,
                    "confidence": round(float(box.conf[0]), 4),
                    "bbox": [x1, y1, x2, y2],
                    "spot_id": None,
                    "spot_uuid": None,
                }
            )
        return detections

    def annotate(self, image_path: Path, detections: list[dict[str, Any]], output_path: Path) -> None:
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()

        colors = {
            "car": "#1d4ed8",
            "motorcycle": "#f59e0b",
            "pickup": "#7c3aed",
            "van": "#059669",
        }
        for item in detections:
            x1, y1, x2, y2 = item["bbox"]
            color = colors.get(item["class_name"], "#ef4444")
            label = f'{item["class_name"]} {item["confidence"]:.2f}'
            if item.get("spot_id"):
                label += f' | {item["spot_id"]}'
            draw.rectangle((x1, y1, x2, y2), outline=color, width=4)
            draw.rectangle((x1, max(y1 - 22, 0), x1 + 190, y1), fill=color)
            draw.text((x1 + 4, max(y1 - 20, 0)), label, fill="white", font=font)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)

    def _demo_predict(self, image_path: Path) -> list[dict[str, Any]]:
        image = Image.open(image_path)
        width, height = image.size
        boxes = [
            ("car", 0.91, [0.12, 0.42, 0.27, 0.63]),
            ("car", 0.88, [0.34, 0.40, 0.50, 0.62]),
            ("pickup", 0.84, [0.57, 0.38, 0.75, 0.64]),
            ("motorcycle", 0.79, [0.78, 0.50, 0.88, 0.66]),
        ]
        detections = []
        for class_name, confidence, rel in boxes:
            x1, y1, x2, y2 = rel
            detections.append(
                {
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": [int(x1 * width), int(y1 * height), int(x2 * width), int(y2 * height)],
                    "spot_id": None,
                    "spot_uuid": None,
                }
            )
        return detections

    @staticmethod
    def _map_class(class_name: str) -> str:
        if class_name == "truck":
            return "pickup"
        if class_name == "bus":
            return "van"
        return class_name


yolo_service = YoloService()
