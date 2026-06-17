import json
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.db.database import get_connection

router = APIRouter(prefix="/parking-spots", tags=["parking spots"])


class SpotPayload(BaseModel):
    spot_id: str
    zone: str = "A"
    polygon: list[list[float]] = Field(min_length=3)


class ParkingSpotsPayload(BaseModel):
    parking_lot_id: str = "default"
    parking_lot_name: str = "Demo Parking"
    location: str = "Campus"
    spots: list[SpotPayload]


@router.post("")
def create_spots(payload: ParkingSpotsPayload) -> dict:
    now = datetime.now().isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute("DELETE FROM parking_lots WHERE id = ?", (payload.parking_lot_id,))
        conn.execute(
            """
            INSERT INTO parking_lots VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload.parking_lot_id,
                payload.parking_lot_name,
                payload.location,
                len(payload.spots),
                now,
            ),
        )
        conn.execute("DELETE FROM parking_spots WHERE parking_lot_id = ?", (payload.parking_lot_id,))
        for spot in payload.spots:
            conn.execute(
                """
                INSERT INTO parking_spots VALUES (?, ?, ?, ?, ?, 1)
                """,
                (
                    f"spot_{uuid4().hex[:12]}",
                    payload.parking_lot_id,
                    spot.spot_id,
                    spot.zone,
                    json.dumps(spot.polygon),
                ),
            )
    return {"message": "Parking spots registered successfully.", "total_spots": len(payload.spots)}


@router.get("")
def list_spots(parking_lot_id: str = "default") -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT spot_code, zone, polygon_json
            FROM parking_spots
            WHERE parking_lot_id = ? AND is_active = 1
            ORDER BY zone, spot_code
            """,
            (parking_lot_id,),
        ).fetchall()
    return {
        "parking_lot_id": parking_lot_id,
        "spots": [
            {"spot_id": row["spot_code"], "zone": row["zone"], "polygon": json.loads(row["polygon_json"])}
            for row in rows
        ],
    }
