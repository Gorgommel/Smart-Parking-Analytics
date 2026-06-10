from collections import defaultdict
from datetime import datetime

from app.db.database import get_connection


def get_current_occupancy(parking_lot_id: str) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT * FROM occupancy_history
            WHERE parking_lot_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (parking_lot_id,),
        ).fetchone()
    if row is None:
        return {
            "parking_lot_id": parking_lot_id,
            "total_spots": 0,
            "occupied_spots": 0,
            "free_spots": 0,
            "occupancy_rate": 0,
            "status": "no_data",
        }
    status = "critical" if row["occupancy_rate"] >= 0.9 else "attention" if row["occupancy_rate"] >= 0.7 else "normal"
    return dict(row) | {"status": status}


def get_history(parking_lot_id: str, limit: int = 100) -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT timestamp, total_spots, occupied_spots, free_spots, occupancy_rate
            FROM occupancy_history
            WHERE parking_lot_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (parking_lot_id, limit),
        ).fetchall()
    return {"parking_lot_id": parking_lot_id, "items": [dict(row) for row in reversed(rows)]}


def get_statistics(parking_lot_id: str) -> dict:
    history = get_history(parking_lot_id, 500)["items"]
    if not history:
        return {
            "parking_lot_id": parking_lot_id,
            "average_occupancy_rate": 0,
            "max_occupancy_rate": 0,
            "min_occupancy_rate": 0,
            "peak_hours": [],
            "total_events": 0,
        }

    rates = [item["occupancy_rate"] for item in history]
    by_hour: dict[str, list[float]] = defaultdict(list)
    for item in history:
        hour = datetime.fromisoformat(item["timestamp"]).strftime("%H:00")
        by_hour[hour].append(item["occupancy_rate"])

    peak_hours = sorted(
        by_hour,
        key=lambda hour: sum(by_hour[hour]) / len(by_hour[hour]),
        reverse=True,
    )[:3]

    return {
        "parking_lot_id": parking_lot_id,
        "average_occupancy_rate": round(sum(rates) / len(rates), 4),
        "max_occupancy_rate": round(max(rates), 4),
        "min_occupancy_rate": round(min(rates), 4),
        "peak_hours": peak_hours,
        "average_occupied_spots": round(sum(item["occupied_spots"] for item in history) / len(history), 2),
        "total_events": len(history),
    }
