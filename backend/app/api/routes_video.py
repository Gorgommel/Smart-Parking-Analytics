from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, UploadFile

from app.core.config import get_settings

router = APIRouter(prefix="/video", tags=["video"])

JOBS: dict[str, dict] = {}


@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    parking_lot_id: str = Form("default"),
    frame_interval_seconds: int = Form(5),
) -> dict:
    settings = get_settings()
    job_id = f"job_{uuid4().hex[:12]}"
    extension = Path(file.filename or "video.mp4").suffix or ".mp4"
    path = settings.uploads_dir / f"{job_id}{extension}"
    path.write_bytes(await file.read())
    JOBS[job_id] = {
        "job_id": job_id,
        "parking_lot_id": parking_lot_id,
        "status": "queued",
        "progress": 0,
        "processed_frames": 0,
        "total_frames": 0,
        "frame_interval_seconds": frame_interval_seconds,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "file_path": str(path),
    }
    return {"job_id": job_id, "status": "queued", "message": "Video uploaded and scheduled for processing."}


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    return JOBS.get(job_id, {"job_id": job_id, "status": "not_found", "progress": 0})
