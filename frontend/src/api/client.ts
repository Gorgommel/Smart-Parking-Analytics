import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api"
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
  inference_note?: string | null;
  calibration_status?: string;
  assignment_method?: string;
  spots_configured?: number;
  occupied_spot_ids?: string[];
  detections: Array<{
    class_name: string;
    confidence: number;
    bbox: number[];
    spot_id: string | null;
  }>;
};

export type ParkingSpotPayload = {
  parking_lot_id: string;
  parking_lot_name: string;
  location: string;
  spots: Array<{
    spot_id: string;
    zone: string;
    polygon: number[][];
  }>;
};

export type ParkingCapacityPayload = {
  parking_lot_id: string;
  parking_lot_name: string;
  location: string;
  total_spots: number;
};

export type VideoUploadResponse = {
  job_id: string;
  status: string;
  message?: string;
  progress: number;
  processed_frames: number;
  total_frames: number;
  summary?: PredictionResponse;
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
  form.append("frame_interval_seconds", "10");
  const response = await api.post<VideoUploadResponse>("/video/upload", form);
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

export async function saveParkingSpots(payload: ParkingSpotPayload) {
  const response = await api.post("/parking-spots", payload);
  return response.data;
}

export async function saveParkingCapacity(payload: ParkingCapacityPayload) {
  const response = await api.post("/parking-spots/capacity", payload);
  return response.data;
}


