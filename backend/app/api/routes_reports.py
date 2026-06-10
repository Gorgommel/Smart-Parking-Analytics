from fastapi import APIRouter, HTTPException

from app.services.report_service import generate_csv, generate_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("")
def create_report(parking_lot_id: str = "default", format: str = "pdf") -> dict:
    if format == "csv":
        path = generate_csv(parking_lot_id)
    elif format == "pdf":
        path = generate_pdf(parking_lot_id)
    else:
        raise HTTPException(status_code=400, detail="format must be csv or pdf")
    return {"report_url": f"/static/reports/{path.name}", "format": format}
