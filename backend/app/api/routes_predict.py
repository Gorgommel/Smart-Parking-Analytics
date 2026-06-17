from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, UploadFile

from app.core.config import get_settings
from app.services.prediction_service import process_image_prediction

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("")
async def predict_image(
    file: UploadFile = File(...),
    parking_lot_id: str = Form("default"),
) -> dict:
    settings = get_settings()
    event_id = f"evt_{uuid4().hex[:12]}"
    extension = Path(file.filename or "image.jpg").suffix or ".jpg"
    input_path = settings.uploads_dir / f"{event_id}{extension}"
    output_path = settings.outputs_dir / f"{event_id}.jpg"

    input_path.write_bytes(await file.read())
    return process_image_prediction(input_path, output_path, parking_lot_id)
