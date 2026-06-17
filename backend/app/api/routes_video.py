from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, UploadFile

from app.core.config import get_settings
from app.services.prediction_service import process_image_prediction

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
        "status": "processing",
        "progress": 0,
        "processed_frames": 0,
        "total_frames": 0,
        "frame_interval_seconds": frame_interval_seconds,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "file_path": str(path),
    }

    try:
        import cv2

        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            JOBS[job_id]["status"] = "failed"
            JOBS[job_id]["message"] = "Could not open video file."
            return JOBS[job_id]

        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        step = max(int(fps * max(frame_interval_seconds, 1)), 1)
        max_frames_to_process = 5
        frame_index = 0
        processed = 0
        last_result = None
        best_result = None

        JOBS[job_id]["total_frames"] = total_frames

        while processed < max_frames_to_process:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            success, frame = cap.read()
            if not success:
                break

            frame_id = f"{job_id}_frame_{processed:03d}"
            frame_path = settings.uploads_dir / f"{frame_id}.jpg"
            output_path = settings.outputs_dir / f"{frame_id}.jpg"
            cv2.imwrite(str(frame_path), frame)

            result = process_image_prediction(frame_path, output_path, parking_lot_id, source_type="video")
            last_result = result
            if best_result is None or result["occupancy_rate"] > best_result["occupancy_rate"]:
                best_result = result

            processed += 1
            frame_index += step
            JOBS[job_id]["processed_frames"] = processed
            if total_frames:
                JOBS[job_id]["progress"] = min(round((frame_index / total_frames) * 100), 100)

        cap.release()
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["progress"] = 100
        JOBS[job_id]["summary"] = best_result or last_result
        JOBS[job_id]["message"] = f"Video processado: {processed} frames amostrados."
        return JOBS[job_id]
    except Exception as exc:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["message"] = f"Video processing failed: {exc.__class__.__name__}"
        return JOBS[job_id]


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    return JOBS.get(job_id, {"job_id": job_id, "status": "not_found", "progress": 0})

