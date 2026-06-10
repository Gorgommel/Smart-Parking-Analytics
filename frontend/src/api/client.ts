import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000/api"
});

export type PredictionResponse = {
  event_id: string;
  parking_lot_id: string;
  model_status: string;
  total_spots: number;
  occupied_spots: number;
  free_spots: number;
  occupancy_rate: number;
  vehicles_detected: number;
  annotated_image_url: string;
  alert: string | null;
  detections: Array<{
    class_name: string;
    confidence: number;
    bbox: number[];
    spot_id: string | null;
  }>;
};

export async function predictImage(file: File, parkingLotId = "default") {
  const form = new FormData();
  form.append("file", file);
  form.append("parking_lot_id", parkingLotId);
  const response = await api.post<PredictionResponse>("/predict", form);
  return response.data;
}

export async function uploadVideo(file: File, parkingLotId = "default") {
  const form = new FormData();
  form.append("file", file);
  form.append("parking_lot_id", parkingLotId);
  form.append("frame_interval_seconds", "5");
  const response = await api.post("/video/upload", form);
  return response.data;
}

export async function fetchHistory() {
  const response = await api.get("/history?parking_lot_id=default&limit=40");
  return response.data.items;
}

export async function fetchStatistics() {
  const response = await api.get("/statistics?parking_lot_id=default");
  return response.data;
}

export async function createReport(format: "pdf" | "csv") {
  const response = await api.get(`/reports?parking_lot_id=default&format=${format}`);
  return response.data;
}
