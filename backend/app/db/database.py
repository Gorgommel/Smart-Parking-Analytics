import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.config import get_settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS parking_lots (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    total_spots INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS parking_spots (
    id TEXT PRIMARY KEY,
    parking_lot_id TEXT NOT NULL,
    spot_code TEXT NOT NULL,
    zone TEXT NOT NULL,
    polygon_json TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS parking_events (
    id TEXT PRIMARY KEY,
    parking_lot_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_path TEXT,
    timestamp TEXT NOT NULL,
    total_vehicles INTEGER NOT NULL,
    occupied_spots INTEGER NOT NULL,
    free_spots INTEGER NOT NULL,
    occupancy_rate REAL NOT NULL,
    annotated_image_path TEXT
);

CREATE TABLE IF NOT EXISTS vehicle_detections (
    id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL,
    class_name TEXT NOT NULL,
    confidence REAL NOT NULL,
    bbox_x1 INTEGER NOT NULL,
    bbox_y1 INTEGER NOT NULL,
    bbox_x2 INTEGER NOT NULL,
    bbox_y2 INTEGER NOT NULL,
    assigned_spot_id TEXT
);

CREATE TABLE IF NOT EXISTS occupancy_history (
    id TEXT PRIMARY KEY,
    parking_lot_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    total_spots INTEGER NOT NULL,
    occupied_spots INTEGER NOT NULL,
    free_spots INTEGER NOT NULL,
    occupancy_rate REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS alert_logs (
    id TEXT PRIMARY KEY,
    parking_lot_id TEXT NOT NULL,
    event_id TEXT,
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    value REAL NOT NULL,
    created_at TEXT NOT NULL
);
"""


def init_db() -> None:
    db_path = Path(get_settings().database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(get_settings().database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
