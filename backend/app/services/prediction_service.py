from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings
from app.db.database import get_connection
from app.services.occupancy_service import assign_spots, load_spots
from app.services.yolo_service import yolo_service


def process_image_prediction(
    image_path: Path,
    output_path: Path,
    parking_lot_id: str,
    source_type: str = "image",
) -> dict:
    settings = get_settings()
    event_id = f"evt_{uuid4().hex[:12]}"
    timestamp = datetime.now().isoformat(timespec="seconds")

    detections = yolo_service.predict(image_path)
    occupancy = assign_spots(parking_lot_id, detections)
    spots = load_spots(parking_lot_id)
    occupied_spot_codes = {item["spot_id"] for item in detections if item.get("spot_id")}
    yolo_service.annotate(image_path, detections, output_path, spots, occupied_spot_codes)

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
                source_type,
                str(image_path),
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
        "occupied_spot_ids": sorted(occupied_spot_codes),
        **occupancy,
    }
