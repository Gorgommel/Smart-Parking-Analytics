import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, BarChart3, Car, Download, Gauge, ParkingCircle, UploadCloud, Video } from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { MetricCard } from "./components/MetricCard";
import { PredictionResponse, createReport, fetchHistory, fetchStatistics, predictImage, uploadVideo } from "./api/client";

const apiOrigin = import.meta.env.VITE_API_ORIGIN ?? "http://localhost:8000";

export function App() {
  const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("Envie uma imagem para iniciar a analise.");

  async function refreshAnalytics() {
    const [historyData, statsData] = await Promise.all([fetchHistory(), fetchStatistics()]);
    setHistory(historyData);
    setStatistics(statsData);
  }

  useEffect(() => {
    refreshAnalytics().catch(() => undefined);
  }, []);

  const chartData = useMemo(() => {
    if (history.length > 0) {
      return history.map((item) => ({
        time: new Date(item.timestamp).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }),
        ocupacao: Math.round(item.occupancy_rate * 100),
        ocupadas: item.occupied_spots,
        livres: item.free_spots
      }));
    }
    return [
      { time: "08:00", ocupacao: 28, ocupadas: 34, livres: 86 },
      { time: "10:00", ocupacao: 48, ocupadas: 58, livres: 62 },
      { time: "12:00", ocupacao: 76, ocupadas: 91, livres: 29 },
      { time: "18:00", ocupacao: 92, ocupadas: 110, livres: 10 }
    ];
  }, [history]);

  async function handleImage(file?: File) {
    if (!file) return;
    setLoading(true);
    setMessage("Processando imagem com YOLO...");
    try {
      const data = await predictImage(file);
      setPrediction(data);
      await refreshAnalytics();
      setMessage(data.alert ?? "Analise concluida com sucesso.");
    } catch (error) {
      setMessage("Nao foi possivel processar a imagem. Verifique se a API esta online.");
    } finally {
      setLoading(false);
    }
  }

  async function handleVideo(file?: File) {
    if (!file) return;
    setLoading(true);
    try {
      const data = await uploadVideo(file);
      setMessage(`Video recebido. Job: ${data.job_id}`);
    } catch {
      setMessage("Nao foi possivel enviar o video.");
    } finally {
      setLoading(false);
    }
  }

  async function downloadReport(format: "pdf" | "csv") {
    const report = await createReport(format);
    window.open(`${apiOrigin}${report.report_url}`, "_blank");
  }

  const total = prediction?.total_spots ?? 120;
  const occupied = prediction?.occupied_spots ?? 0;
  const free = prediction?.free_spots ?? total - occupied;
  const rate = prediction?.occupancy_rate ?? 0;
  const vehicles = prediction?.vehicles_detected ?? 0;

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <ParkingCircle size={34} />
          <div>
            <strong>Smart Parking</strong>
            <span>Analytics</span>
          </div>
        </div>
        <nav>
          <a className="active">Dashboard</a>
          <a>Upload</a>
          <a>Historico</a>
          <a>Relatorios</a>
          <a>Alertas</a>
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <h1>Dashboard operacional</h1>
            <p>Monitoramento de ocupacao, deteccoes e utilizacao temporal.</p>
          </div>
          <div className={`status ${rate >= 0.9 ? "critical" : rate >= 0.7 ? "warning" : "normal"}`}>
            {rate >= 0.9 ? "Critico" : rate >= 0.7 ? "Atencao" : "Normal"}
          </div>
        </header>

        <section className="metrics-grid">
          <MetricCard label="Total de vagas" value={String(total)} helper="capacidade monitorada" icon={<ParkingCircle />} />
          <MetricCard label="Ocupadas" value={String(occupied)} helper="vagas com veiculo" icon={<Car />} />
          <MetricCard label="Livres" value={String(free)} helper="disponiveis agora" icon={<Gauge />} />
          <MetricCard label="Taxa de ocupacao" value={`${Math.round(rate * 100)}%`} helper="ocupadas / total" icon={<BarChart3 />} />
          <MetricCard label="Veiculos detectados" value={String(vehicles)} helper={prediction?.model_status ?? "aguardando inferencia"} icon={<Car />} />
        </section>

        {message && (
          <section className={`notice ${prediction?.alert ? "alert" : ""}`}>
            <AlertTriangle size={18} />
            <span>{message}</span>
          </section>
        )}

        <section className="workspace-grid">
          <div className="panel upload-panel">
            <h2>Entrada de midia</h2>
            <div className="upload-actions">
              <label className="upload-box">
                <UploadCloud />
                <strong>Imagem</strong>
                <span>JPG, PNG ou WEBP</span>
                <input type="file" accept="image/*" onChange={(event) => handleImage(event.target.files?.[0])} />
              </label>
              <label className="upload-box">
                <Video />
                <strong>Video</strong>
                <span>MP4, MOV ou AVI</span>
                <input type="file" accept="video/*" onChange={(event) => handleVideo(event.target.files?.[0])} />
              </label>
            </div>
            <div className="report-actions">
              <button onClick={() => downloadReport("pdf")} disabled={loading}>
                <Download size={16} /> PDF
              </button>
              <button onClick={() => downloadReport("csv")} disabled={loading}>
                <Download size={16} /> CSV
              </button>
            </div>
          </div>

          <div className="panel result-panel">
            <h2>Resultado visual</h2>
            {prediction ? (
              <img src={`${apiOrigin}${prediction.annotated_image_url}`} alt="Resultado anotado" />
            ) : (
              <div className="empty-preview">A imagem anotada aparecera aqui.</div>
            )}
          </div>
        </section>

        <section className="charts-grid">
          <div className="panel chart-panel">
            <h2>Evolucao temporal</h2>
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d7dde8" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area dataKey="ocupacao" stroke="#2563eb" fill="#bfdbfe" name="Ocupacao %" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="panel chart-panel">
            <h2>Livres x ocupadas</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData.slice(-6)}>
                <CartesianGrid strokeDasharray="3 3" stroke="#d7dde8" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="ocupadas" fill="#ef4444" name="Ocupadas" />
                <Bar dataKey="livres" fill="#22c55e" name="Livres" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel detections-panel">
          <h2>Deteccoes recentes</h2>
          <table>
            <thead>
              <tr>
                <th>Classe</th>
                <th>Confianca</th>
                <th>Vaga</th>
                <th>Bounding box</th>
              </tr>
            </thead>
            <tbody>
              {(prediction?.detections ?? []).map((item, index) => (
                <tr key={`${item.class_name}-${index}`}>
                  <td>{item.class_name}</td>
                  <td>{Math.round(item.confidence * 100)}%</td>
                  <td>{item.spot_id ?? "nao atribuida"}</td>
                  <td>{item.bbox.join(", ")}</td>
                </tr>
              ))}
              {!prediction && (
                <tr>
                  <td colSpan={4}>Nenhuma inferencia executada nesta sessao.</td>
                </tr>
              )}
            </tbody>
          </table>
          {statistics && <p className="stats-line">Picos detectados: {statistics.peak_hours?.join(", ") || "sem dados"}.</p>}
        </section>
      </section>
    </main>
  );
}
