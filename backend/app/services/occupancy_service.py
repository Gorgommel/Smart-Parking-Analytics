import json
from dataclasses import dataclass
from typing import Any

from app.db.database import get_connection


@dataclass
class Spot:
    id: str
    code: str
    zone: str
    polygon: list[list[float]]


def _point_in_polygon(x: float, y: float, polygon: list[list[float]]) -> bool:
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-9) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def _bbox_center(bbox: list[int]) -> tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2


def load_spots(parking_lot_id: str) -> list[Spot]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, spot_code, zone, polygon_json
            FROM parking_spots
            WHERE parking_lot_id = ? AND is_active = 1
            ORDER BY zone, spot_code
            """,
            (parking_lot_id,),
        ).fetchall()
    return [
        Spot(
            id=row["id"],
            code=row["spot_code"],
            zone=row["zone"],
            polygon=json.loads(row["polygon_json"]),
        )
        for row in rows
    ]


def assign_spots(parking_lot_id: str, detections: list[dict[str, Any]]) -> dict[str, Any]:
    spots = load_spots(parking_lot_id)
    occupied: dict[str, dict[str, Any]] = {}

    for detection in detections:
        cx, cy = _bbox_center(detection["bbox"])
        for spot in spots:
            if spot.id in occupied:
                continue
            if _point_in_polygon(cx, cy, spot.polygon):
                detection["spot_id"] = spot.code
                detection["spot_uuid"] = spot.id
                occupied[spot.id] = detection
                break

    total_spots = len(spots)
    if total_spots == 0:
        total_spots = max(len(detections) + 12, 20)
        occupied_count = min(len(detections), total_spots)
    else:
        occupied_count = len(occupied)

    free_spots = max(total_spots - occupied_count, 0)
    occupancy_rate = occupied_count / total_spots if total_spots else 0

    return {
        "total_spots": total_spots,
        "occupied_spots": occupied_count,
        "free_spots": free_spots,
        "occupancy_rate": round(occupancy_rate, 4),
        "spots_configured": len(spots),
    }
