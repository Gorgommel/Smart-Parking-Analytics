from fastapi import APIRouter

from app.db.database import get_connection
from app.services.analytics_service import get_current_occupancy, get_history, get_statistics

router = APIRouter(tags=["analytics"])


@router.get("/occupancy")
def occupancy(parking_lot_id: str = "default") -> dict:
    return get_current_occupancy(parking_lot_id)


@router.get("/history")
def history(parking_lot_id: str = "default", limit: int = 100) -> dict:
    return get_history(parking_lot_id, limit)


@router.get("/statistics")
def statistics(parking_lot_id: str = "default") -> dict:
    return get_statistics(parking_lot_id)


@router.get("/alerts")
def alerts(parking_lot_id: str = "default") -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, parking_lot_id, type, severity, message, value AS occupancy_rate, created_at
            FROM alert_logs
            WHERE parking_lot_id = ?
            ORDER BY created_at DESC
            LIMIT 50
            """,
            (parking_lot_id,),
        ).fetchall()
    return {"alerts": [dict(row) for row in rows]}
