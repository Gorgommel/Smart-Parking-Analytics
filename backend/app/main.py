from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes_parking_spots import router as parking_spots_router
from app.api.routes_predict import router as predict_router
from app.api.routes_reports import router as reports_router
from app.api.routes_statistics import router as statistics_router
from app.api.routes_video import router as video_router
from app.core.config import get_settings
from app.db.database import init_db

settings = get_settings()
init_db()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict_router, prefix=settings.api_prefix)
app.include_router(video_router, prefix=settings.api_prefix)
app.include_router(statistics_router, prefix=settings.api_prefix)
app.include_router(reports_router, prefix=settings.api_prefix)
app.include_router(parking_spots_router, prefix=settings.api_prefix)

app.mount("/static/outputs", StaticFiles(directory=settings.outputs_dir), name="outputs")
app.mount("/static/reports", StaticFiles(directory=settings.reports_dir), name="reports")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}
