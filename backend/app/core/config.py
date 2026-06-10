from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Smart Parking Analytics API"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    database_path: Path = Path("smart_parking.db")
    uploads_dir: Path = Path("uploads")
    outputs_dir: Path = Path("outputs")
    reports_dir: Path = Path("../reports")
    model_path: Path = Path("models/best.pt")
    fallback_model: str = "yolo11n.pt"
    confidence_threshold: float = 0.35
    occupancy_alert_threshold: float = 0.9
    demo_mode: bool = False

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    settings.outputs_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    return settings
