from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, UploadFile

from app.core.config import get_settings
from app.db.database import get_connection
from app.services.occupancy_service import assign_spots
from app.services.yolo_service import yolo_service

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("")
async def predict_image(
    file: UploadFile = File(...),
    parking_lot_id: str = Form("default"),
) -> dict:
    settings = get_settings()
    event_id = f"evt_{uuid4().hex[:12]}"
    timestamp = datetime.now().isoformat(timespec="seconds")
    extension = Path(file.filename or "image.jpg").suffix or ".jpg"
    input_path = settings.uploads_dir / f"{event_id}{extension}"
    output_path = settings.outputs_dir / f"{event_id}.jpg"

    input_path.write_bytes(await file.read())
    detections = yolo_service.predict(input_path)
    occupancy = assign_spots(parking_lot_id, detections)
    yolo_service.annotate(input_path, detections, output_path)

    alert = None
    if occupancy["occupancy_rate"] >= settings.occupancy_alert_threshold:
        alert = "Estacionamento proximo da lotacao."

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO parking_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                parking_lot_id,
                "image",
                str(input_path),
                timestamp,
                len(detections),
                occupancy["occupied_spots"],
                occupancy["free_spots"],
                occupancy["occupancy_rate"],
                str(output_path),
            ),
        )
        conn.execute(
            """
            INSERT INTO occupancy_history VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"hist_{uuid4().hex[:12]}",
                parking_lot_id,
                timestamp,
                occupancy["total_spots"],
                occupancy["occupied_spots"],
                occupancy["free_spots"],
                occupancy["occupancy_rate"],
            ),
        )
        for detection in detections:
            x1, y1, x2, y2 = detection["bbox"]
            conn.execute(
                """
                INSERT INTO vehicle_detections VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"det_{uuid4().hex[:12]}",
                    event_id,
                    detection["class_name"],
                    detection["confidence"],
                    x1,
                    y1,
                    x2,
                    y2,
                    detection.get("spot_uuid"),
                ),
            )
        if alert:
            conn.execute(
                """
                INSERT INTO alert_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"alert_{uuid4().hex[:12]}",
                    parking_lot_id,
                    event_id,
                    "high_occupancy",
                    "warning",
                    alert,
                    occupancy["occupancy_rate"],
                    timestamp,
                ),
            )

    return {
        "event_id": event_id,
        "parking_lot_id": parking_lot_id,
        "model_status": yolo_service.model_status,
        "vehicles_detected": len(detections),
        "detections": detections,
        "alert": alert,
        "annotated_image_url": f"/static/outputs/{output_path.name}",
        **occupancy,
    }
