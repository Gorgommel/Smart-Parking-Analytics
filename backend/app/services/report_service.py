import csv
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.core.config import get_settings
from app.services.analytics_service import get_history, get_statistics


def generate_csv(parking_lot_id: str) -> Path:
    settings = get_settings()
    path = settings.reports_dir / f"{parking_lot_id}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    rows = get_history(parking_lot_id, 1000)["items"]
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["timestamp", "total_spots", "occupied_spots", "free_spots", "occupancy_rate"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def generate_pdf(parking_lot_id: str) -> Path:
    settings = get_settings()
    stats = get_statistics(parking_lot_id)
    path = settings.reports_dir / f"{parking_lot_id}_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 72
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(72, y, "Smart Parking Analytics")
    y -= 36
    pdf.setFont("Helvetica", 11)
    lines = [
        f"Estacionamento: {parking_lot_id}",
        f"Gerado em: {datetime.now():%d/%m/%Y %H:%M}",
        f"Eventos analisados: {stats['total_events']}",
        f"Ocupacao media: {stats['average_occupancy_rate'] * 100:.1f}%",
        f"Ocupacao maxima: {stats['max_occupancy_rate'] * 100:.1f}%",
        f"Ocupacao minima: {stats['min_occupancy_rate'] * 100:.1f}%",
        f"Horarios de pico: {', '.join(stats['peak_hours']) or 'sem dados'}",
    ]
    for line in lines:
        pdf.drawString(72, y, line)
        y -= 24
    pdf.save()
    return path
