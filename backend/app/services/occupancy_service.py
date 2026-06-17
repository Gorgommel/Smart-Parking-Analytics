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


def scale_polygon(polygon: list[list[float]], image_size: tuple[int, int] | None = None) -> list[list[float]]:
    """Scale normalized polygons to image pixels; keep absolute polygons unchanged."""
    if not polygon:
        return polygon
    if image_size is None:
        return polygon

    width, height = image_size
    max_x = max(point[0] for point in polygon)
    max_y = max(point[1] for point in polygon)
    if max_x <= 1.0 and max_y <= 1.0:
        return [[point[0] * width, point[1] * height] for point in polygon]
    return polygon


def polygon_bounds(polygon: list[list[float]]) -> tuple[float, float, float, float]:
    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]
    return min(xs), min(ys), max(xs), max(ys)


def bbox_area(bbox: list[int] | tuple[float, float, float, float]) -> float:
    x1, y1, x2, y2 = bbox
    return max(x2 - x1, 0) * max(y2 - y1, 0)


def intersection_area(
    first: list[int] | tuple[float, float, float, float],
    second: list[int] | tuple[float, float, float, float],
) -> float:
    ax1, ay1, ax2, ay2 = first
    bx1, by1, bx2, by2 = second
    width = max(min(ax2, bx2) - max(ax1, bx1), 0)
    height = max(min(ay2, by2) - max(ay1, by1), 0)
    return width * height


def overlap_ratio(
    vehicle_bbox: list[int],
    spot_polygon: list[list[float]],
) -> float:
    """Return how much of a parking spot is covered by a detected vehicle bbox."""
    spot_bbox = polygon_bounds(spot_polygon)
    spot_area = bbox_area(spot_bbox)
    if spot_area == 0:
        return 0.0
    return intersection_area(vehicle_bbox, spot_bbox) / spot_area


def load_lot_capacity(parking_lot_id: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT total_spots
            FROM parking_lots
            WHERE id = ?
            """,
            (parking_lot_id,),
        ).fetchone()
    return int(row["total_spots"]) if row else 0


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


def capacity_occupancy(parking_lot_id: str, detections: list[dict[str, Any]], total_spots: int) -> dict[str, Any]:
    occupied_count = min(len(detections), total_spots) if total_spots else 0
    free_spots = max(total_spots - occupied_count, 0)
    occupancy_rate = occupied_count / total_spots if total_spots else 0
    return {
        "total_spots": total_spots,
        "occupied_spots": occupied_count,
        "free_spots": free_spots,
        "occupancy_rate": round(occupancy_rate, 4),
        "spots_configured": 0,
        "calibration_status": "capacity_only" if total_spots else "missing_spots",
        "calibration_note": (
            "Modo capacidade: o YOLO conta carros e o sistema calcula ocupacao agregada pelo total de vagas cadastrado. "
            "Para saber exatamente qual vaga esta livre, cadastre os poligonos dessa camera."
            if total_spots
            else "Nenhuma vaga/capacidade foi cadastrada. O YOLO detecta carros, mas a ocupacao precisa de capacidade total ou poligonos."
        ),
        "assignment_method": "vehicle_count_over_configured_capacity" if total_spots else "none",
        "min_spot_coverage": None,
    }


def assign_spots(
    parking_lot_id: str,
    detections: list[dict[str, Any]],
    image_size: tuple[int, int] | None = None,
    min_spot_coverage: float = 0.12,
) -> dict[str, Any]:
    lot_capacity = load_lot_capacity(parking_lot_id)
    spots = load_spots(parking_lot_id)
    if not spots:
        return capacity_occupancy(parking_lot_id, detections, lot_capacity)

    scaled_spots = [
        Spot(id=spot.id, code=spot.code, zone=spot.zone, polygon=scale_polygon(spot.polygon, image_size))
        for spot in spots
    ]

    candidates: list[tuple[float, dict[str, Any], Spot]] = []
    for detection in detections:
        for spot in scaled_spots:
            score = overlap_ratio(detection["bbox"], spot.polygon)
            if score >= min_spot_coverage:
                candidates.append((score, detection, spot))

    occupied: dict[str, dict[str, Any]] = {}
    assigned_detection_ids: set[int] = set()
    for score, detection, spot in sorted(candidates, key=lambda item: item[0], reverse=True):
        detection_key = id(detection)
        if spot.id in occupied or detection_key in assigned_detection_ids:
            continue
        detection["spot_id"] = spot.code
        detection["spot_uuid"] = spot.id
        detection["spot_overlap"] = round(score, 4)
        occupied[spot.id] = detection
        assigned_detection_ids.add(detection_key)

    total_spots = len(spots)
    occupied_count = len(occupied)
    free_spots = max(total_spots - occupied_count, 0)
    occupancy_rate = occupied_count / total_spots if total_spots else 0

    calibration_status = "configured"
    calibration_note = None
    if detections and occupied_count == 0:
        calibration_status = "misaligned_spots"
        calibration_note = (
            "Carros foram detectados, mas nenhum cruzou as vagas cadastradas. "
            "Isso indica que os poligonos nao pertencem a este enquadramento/camera."
        )
    elif detections and occupied_count < max(1, min(len(detections), total_spots) * 0.35):
        calibration_status = "needs_review"
        calibration_note = (
            "Poucos carros detectados foram associados a vagas. "
            "Revise os poligonos para esta imagem antes da apresentacao."
        )

    return {
        "total_spots": total_spots,
        "occupied_spots": occupied_count,
        "free_spots": free_spots,
        "occupancy_rate": round(occupancy_rate, 4),
        "spots_configured": len(spots),
        "calibration_status": calibration_status,
        "calibration_note": calibration_note,
        "assignment_method": "vehicle_bbox_spot_overlap",
        "min_spot_coverage": min_spot_coverage,
    }
