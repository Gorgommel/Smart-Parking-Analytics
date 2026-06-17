import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { Presentation, PresentationFile } = require("@oai/artifact-tool");

const project = "C:/Users/Isaac/Documents/v2/Smart-Parking-Analytics";
const outputDir = path.join(project, "apresentacao");
const workDir = path.join(project, "work", "presentations", "nova-apresentacao-smart-parking");
const previewDir = path.join(workDir, "tmp", "preview");
const qaDir = path.join(workDir, "tmp", "qa");
const finalPptx = path.join(outputDir, "Smart-Parking-Analytics-Apresentacao-Final.pptx");

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });
await fs.mkdir(qaDir, { recursive: true });

await fs.writeFile(
  path.join(workDir, "tmp", "source-notes.txt"),
  [
    "Fontes e evidencias usadas na apresentacao",
    "",
    "- README.md, checklist-avaliacao.md e codigo backend/frontend.",
    "- Dataset final: dataset/data.yaml e docs/training-results/training-summary.md.",
    "- Metricas reais: Precision 0.915, Recall 0.885, mAP50 0.930, mAP50-95 0.871 em validation.",
    "- Metricas reais no test: Precision 0.913, Recall 0.919, mAP50 0.921, mAP50-95 0.865.",
    "- Imagens reais: results.png, confusion_matrix.png e backend/outputs/capacity_demo_test.jpg.",
  ].join("\n"),
  "utf8",
);

await fs.writeFile(
  path.join(workDir, "tmp", "slide-plan.txt"),
  [
    "Plano do deck",
    "",
    "Modo: create.",
    "Formato: 16:9, 1280x720.",
    "Paleta: fundo #f8fafc, texto #0f172a, primario #0f766e, secundario #2563eb, acento #f97316.",
    "Fontes: Aptos Display e Aptos.",
    "Slides: capa, problema, proposta, pipeline, dataset, treinamento, metricas, arquitetura, logica, demo, API/frontend, checklist e roteiro.",
  ].join("\n"),
  "utf8",
);

const W = 1280;
const H = 720;
const pres = Presentation.create({ slideSize: { width: W, height: H } });
const c = {
  bg: "#f8fafc",
  ink: "#0f172a",
  muted: "#475569",
  primary: "#0f766e",
  blue: "#2563eb",
  orange: "#f97316",
  red: "#dc2626",
  green: "#16a34a",
  white: "#ffffff",
};

function text(slide, value, left, top, width, height, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left, top, width, height },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = { fontSize: 20, color: c.ink, typeface: "Aptos", ...style };
  return shape;
}

function card(slide, left, top, width, height, fill = c.white, stroke = "#cbd5e1") {
  return slide.shapes.add({
    geometry: "roundRect",
    position: { left, top, width, height },
    fill,
    line: { style: "solid", fill: stroke, width: 1 },
    borderRadius: "rounded-lg",
    shadow: "shadow-sm",
  });
}

function bg(slide, title, kicker = "SMART PARKING ANALYTICS") {
  slide.background.fill = c.bg;
  slide.shapes.add({
    geometry: "rect",
    position: { left: 0, top: 0, width: W, height: 8 },
    fill: c.primary,
    line: { style: "solid", fill: c.primary, width: 0 },
  });
  text(slide, kicker, 64, 34, 420, 24, { fontSize: 12, bold: true, color: c.primary });
  text(slide, title, 64, 62, 940, 58, {
    fontSize: 34,
    bold: true,
    color: c.ink,
    typeface: "Aptos Display",
  });
  text(slide, "Disciplina de Processamento Digital de Imagens e Visao Computacional", 64, 682, 760, 22, {
    fontSize: 11,
    color: "#64748b",
  });
}

function bullets(slide, items, left, top, width, height, fontSize = 20) {
  text(slide, items.map((item) => `- ${item}`).join("\n"), left, top, width, height, {
    fontSize,
    color: c.ink,
  });
}

function metric(slide, label, value, left, top, width, color = c.primary) {
  card(slide, left, top, width, 116, c.white, "#dbe3ef");
  text(slide, label, left + 18, top + 16, width - 36, 24, {
    fontSize: 14,
    bold: true,
    color: c.muted,
  });
  text(slide, value, left + 18, top + 44, width - 36, 54, {
    fontSize: 40,
    bold: true,
    color,
    typeface: "Aptos Display",
  });
}

async function image(slide, imagePath, left, top, width, height, alt) {
  const bytes = await fs.readFile(imagePath);
  const buffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
  slide.images.add({
    blob: buffer,
    contentType: imagePath.toLowerCase().endsWith(".jpg") ? "image/jpeg" : "image/png",
    alt,
    fit: "contain",
    position: { left, top, width, height },
    geometry: "roundRect",
    borderRadius: "rounded-lg",
  });
}

{
  const slide = pres.slides.add();
  slide.background.fill = "#082f2c";
  text(slide, "Smart Parking Analytics", 72, 96, 760, 84, {
    fontSize: 56,
    bold: true,
    color: c.white,
    typeface: "Aptos Display",
  });
  text(
    slide,
    "Sistema inteligente de estacionamento com YOLO, FastAPI, React e analytics em tempo real",
    72,
    194,
    760,
    78,
    { fontSize: 24, color: "#ccfbf1" },
  );
  metric(slide, "Modelo treinado", "YOLO26n", 72, 380, 250, c.orange);
  metric(slide, "Classe final", "car", 350, 380, 250, c.green);
  metric(slide, "mAP50 test", "0.921", 628, 380, 250, c.blue);
  text(
    slide,
    "Aplicacao academica completa: dataset personalizado, treinamento, API propria, dashboard e demonstracao funcional.",
    72,
    560,
    930,
    48,
    { fontSize: 20, color: "#d1fae5" },
  );
}

{
  const slide = pres.slides.add();
  bg(slide, "Problema real");
  bullets(
    slide,
    [
      "Estacionamentos de shoppings, universidades e empresas precisam saber ocupacao em tempo real.",
      "Contagem manual e sensores por vaga aumentam custo e manutencao.",
      "Cameras ja existentes podem virar fonte de dados com visao computacional.",
      "A proposta nao e apenas contar objetos: o sistema gera metricas, historico, alertas e relatorios.",
    ],
    84,
    150,
    620,
    330,
    22,
  );
  card(slide, 760, 148, 420, 330, "#ecfeff", "#67e8f9");
  text(slide, "Pergunta central", 790, 178, 360, 30, { fontSize: 18, bold: true, color: c.primary });
  text(
    slide,
    "Como transformar imagens ou videos de estacionamento em indicadores operacionais para tomada de decisao?",
    790,
    228,
    350,
    160,
    { fontSize: 30, bold: true, color: c.ink, typeface: "Aptos Display" },
  );
}

{
  const slide = pres.slides.add();
  bg(slide, "Proposta da solucao");
  const xs = [80, 348, 616, 884];
  const labels = ["1. Entrada", "2. YOLO", "3. Ocupacao", "4. Analytics"];
  const desc = [
    "Imagem ou video enviado pelo dashboard web.",
    "Modelo treinado detecta carros com bounding boxes.",
    "Sistema calcula ocupadas, livres e taxa.",
    "Historico, picos, alertas e relatorios.",
  ];
  xs.forEach((x, index) => {
    card(slide, x, 170, 220, 250);
    text(slide, labels[index], x + 20, 196, 180, 30, {
      fontSize: 20,
      bold: true,
      color: [c.primary, c.blue, c.orange, c.green][index],
    });
    text(slide, desc[index], x + 20, 250, 170, 110, { fontSize: 19 });
    if (index < 3) text(slide, ">", x + 236, 258, 40, 50, { fontSize: 38, bold: true, color: "#94a3b8" });
  });
  text(
    slide,
    "Resultado: um produto SaaS demonstravel para monitoramento de estacionamentos com interface propria e API propria.",
    90,
    510,
    1020,
    48,
    { fontSize: 24, bold: true },
  );
}

{
  const slide = pres.slides.add();
  bg(slide, "Ciclo completo de PDI");
  const steps = [
    "Coleta/adaptacao do dataset",
    "Anotacao no Roboflow",
    "Exportacao YOLO26",
    "Treinamento Ultralytics",
    "Inferencia na API",
    "Dashboard e relatorios",
  ];
  steps.forEach((step, index) => {
    const y = 145 + index * 72;
    card(slide, 110, y, 470, 48, index % 2 ? "#ffffff" : "#f0fdfa", "#99f6e4");
    text(slide, `${index + 1}. ${step}`, 132, y + 12, 420, 22, { fontSize: 19, bold: true });
    if (index < steps.length - 1) text(slide, "v", 330, y + 48, 40, 24, { fontSize: 24, bold: true, color: c.primary });
  });
  card(slide, 710, 150, 400, 350, "#fff7ed", "#fed7aa");
  text(slide, "O que sera demonstrado", 746, 185, 330, 28, { fontSize: 22, bold: true, color: c.orange });
  bullets(
    slide,
    [
      "Modelo treinado, nao pre-treinado puro.",
      "API FastAPI consumindo o peso final.",
      "Frontend React proprio.",
      "Calculo de ocupacao e relatorios.",
      "Evidencias de metricas e teste.",
    ],
    750,
    242,
    310,
    210,
    20,
  );
}

{
  const slide = pres.slides.add();
  bg(slide, "Dataset personalizado");
  metric(slide, "Total de imagens", "166", 74, 150, 230, c.primary);
  metric(slide, "Objetos anotados", "6688", 326, 150, 260, c.blue);
  metric(slide, "Classes", "1: car", 608, 150, 230, c.orange);
  metric(slide, "Formato", "YOLO26", 860, 150, 230, c.green);
  bullets(
    slide,
    [
      "Split: 103 train, 34 validation, 29 test.",
      "Dataset exportado do Roboflow e ajustado para classe unica car.",
      "A simplificacao reduziu confusao entre carro, van e moto na demonstracao.",
      "O escopo final e adequado para estacionamentos onde o objetivo e detectar carros e calcular ocupacao.",
    ],
    90,
    330,
    980,
    210,
    22,
  );
}

{
  const slide = pres.slides.add();
  bg(slide, "Treinamento do modelo");
  await image(slide, path.join(project, "docs/training-results/results.png"), 72, 140, 600, 410, "Grafico de resultados");
  card(slide, 720, 150, 410, 390);
  text(slide, "Configuracao", 750, 180, 330, 32, { fontSize: 24, bold: true, color: c.primary });
  bullets(
    slide,
    ["Modelo base: yolo26n.pt", "Tarefa: Object Detection", "Epochs: 100", "Image size: 640", "Batch: 4", "Peso final: backend/models/best.pt"],
    750,
    230,
    340,
    245,
    21,
  );
}

{
  const slide = pres.slides.add();
  bg(slide, "Metricas obtidas");
  metric(slide, "Precision val", "0.915", 80, 145, 240, c.primary);
  metric(slide, "Recall val", "0.885", 350, 145, 240, c.blue);
  metric(slide, "mAP50 val", "0.930", 620, 145, 240, c.orange);
  metric(slide, "mAP50-95 val", "0.871", 890, 145, 260, c.green);
  await image(slide, path.join(project, "docs/training-results/confusion_matrix.png"), 110, 315, 410, 300, "Matriz de confusao");
  card(slide, 580, 330, 520, 260, "#eef2ff", "#c7d2fe");
  text(slide, "Leitura para a banca", 612, 360, 440, 28, { fontSize: 24, bold: true, color: c.blue });
  bullets(
    slide,
    [
      "mAP50 acima de 0.90 indica boa deteccao para a demo.",
      "Recall alto significa que poucos carros deixam de ser detectados.",
      "mAP50-95 mostra qualidade mais exigente das caixas.",
      "O split test separado confirmou generalizacao: mAP50 test 0.921.",
    ],
    612,
    412,
    430,
    150,
    19,
  );
}

{
  const slide = pres.slides.add();
  bg(slide, "Arquitetura profissional");
  const nodes = [
    ["React + Vite", 70, 170, 210, 70, c.green],
    ["FastAPI", 350, 170, 210, 70, c.orange],
    ["YOLO Service", 630, 170, 210, 70, c.blue],
    ["Banco de Dados", 910, 170, 230, 70, c.primary],
    ["Analytics", 350, 360, 210, 70, c.blue],
    ["Relatorios PDF/CSV", 630, 360, 250, 70, c.orange],
  ];
  nodes.forEach((node) => {
    card(slide, node[1], node[2], node[3], node[4], c.white, node[5]);
    text(slide, node[0], node[1] + 20, node[2] + 22, node[3] - 40, 30, { fontSize: 21, bold: true, color: node[5] });
  });
  text(slide, ">", 295, 185, 40, 34, { fontSize: 34, bold: true, color: "#64748b" });
  text(slide, ">", 575, 185, 40, 34, { fontSize: 34, bold: true, color: "#64748b" });
  text(slide, ">", 855, 185, 40, 34, { fontSize: 34, bold: true, color: "#64748b" });
  text(slide, "v", 455, 262, 34, 44, { fontSize: 34, bold: true, color: "#64748b" });
  text(slide, ">", 575, 375, 40, 34, { fontSize: 34, bold: true, color: "#64748b" });
  text(slide, "Local: SQLite. Deploy: PostgreSQL no Render via DATABASE_URL. Frontend pode ficar na Vercel consumindo a API.", 90, 535, 1040, 58, {
    fontSize: 22,
    bold: true,
  });
}

{
  const slide = pres.slides.add();
  bg(slide, "Logica de estacionamento revisada");
  card(slide, 80, 150, 500, 330, "#f0fdfa", "#5eead4");
  text(slide, "Modo por capacidade", 112, 184, 390, 32, { fontSize: 26, bold: true, color: c.primary });
  bullets(slide, ["Usado quando nao ha poligonos confiaveis.", "ocupadas = min(carros_detectados, total_vagas)", "livres = total_vagas - ocupadas", "taxa = ocupadas / total_vagas"], 112, 246, 390, 180, 21);
  card(slide, 700, 150, 500, 330, "#eff6ff", "#93c5fd");
  text(slide, "Modo por poligonos", 732, 184, 390, 32, { fontSize: 26, bold: true, color: c.blue });
  bullets(slide, ["Usado para camera fixa e calibrada.", "Cada vaga tem um poligono.", "Carro ocupa vaga quando sua bbox sobrepoe a regiao.", "Permite dizer quais vagas estao livres."], 732, 246, 390, 180, 21);
  text(slide, "Mensagem-chave: detectar carros e identificar vagas livres sao problemas diferentes. O sistema trata os dois cenarios de forma transparente.", 105, 550, 1010, 52, {
    fontSize: 23,
    bold: true,
    color: c.red,
  });
}

{
  const slide = pres.slides.add();
  bg(slide, "Demonstracao funcional");
  await image(slide, path.join(project, "backend/outputs/capacity_demo_test.jpg"), 70, 140, 610, 420, "Imagem anotada pela API");
  card(slide, 730, 150, 420, 380);
  text(slide, "Resultado do teste real", 760, 180, 340, 28, { fontSize: 24, bold: true, color: c.primary });
  metric(slide, "Carros detectados", "23", 760, 235, 320, c.blue);
  metric(slide, "Vagas livres", "17", 760, 365, 320, c.green);
  text(slide, "Capacidade cadastrada: 40 vagas. Modo usado: capacity_only.", 760, 500, 340, 42, { fontSize: 18, bold: true });
}

{
  const slide = pres.slides.add();
  bg(slide, "API e interface propria");
  bullets(slide, ["POST /api/predict: inferencia em imagem.", "POST /api/video/upload: processamento de video por frames.", "POST /api/parking-spots/capacity: capacidade total.", "POST /api/parking-spots: poligonos calibrados.", "GET /api/statistics, /history, /reports: analytics e relatorios."], 90, 145, 540, 340, 21);
  card(slide, 710, 150, 420, 340, "#f8fafc", "#cbd5e1");
  text(slide, "Dashboard React", 744, 184, 330, 30, { fontSize: 26, bold: true, color: c.blue });
  bullets(slide, ["Upload de imagem e video.", "Cards de ocupacao.", "Graficos temporais.", "Imagem anotada.", "PDF e CSV."], 744, 246, 330, 180, 22);
}

{
  const slide = pres.slides.add();
  bg(slide, "Checklist da avaliacao");
  const items = [["Treinamento proprio", "2.5 / 2.5"], ["Uso correto do YOLO", "1.5 / 1.5"], ["GUI propria + API", "2.0 / 2.0"], ["Robustez e aplicabilidade", "1.5 / 1.5"], ["Apresentacao oral", "1.5 / 1.5"], ["Repositorio organizado", "1.0 / 1.0"]];
  items.forEach((item, index) => {
    const x = index < 3 ? 100 : 680;
    const y = 150 + (index % 3) * 130;
    card(slide, x, y, 420, 82);
    text(slide, item[0], x + 22, y + 18, 260, 26, { fontSize: 21, bold: true });
    text(slide, item[1], x + 300, y + 16, 100, 40, { fontSize: 25, bold: true, color: c.primary });
  });
  text(slide, "Ponto critico para defender: o modelo foi treinado; a aplicacao usa API propria; a ocupacao e calculada com regra de negocio, historico e relatorios.", 100, 560, 1000, 50, {
    fontSize: 22,
    bold: true,
  });
}

{
  const slide = pres.slides.add();
  slide.background.fill = "#0f172a";
  text(slide, "Roteiro da demo ao vivo", 72, 70, 820, 64, { fontSize: 46, bold: true, color: c.white, typeface: "Aptos Display" });
  bullets(slide, ["Abrir frontend e mostrar dashboard.", "Cadastrar capacidade total de vagas.", "Enviar imagem ou video.", "Mostrar deteccoes, ocupacao, livres e alerta.", "Abrir metricas de treinamento e explicar mAP/precision/recall.", "Encerrar com arquitetura e aplicabilidade real."], 100, 170, 860, 310, 24);
  text(slide, "Fechamento: o projeto cobre o ciclo completo de PDI: dataset -> treinamento -> inferencia -> API -> interface -> analytics.", 100, 560, 980, 52, {
    fontSize: 24,
    bold: true,
    color: "#ccfbf1",
  });
}

for (const [index, slide] of pres.slides.items.entries()) {
  const stem = `slide-${String(index + 1).padStart(2, "0")}`;
  const png = await pres.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(previewDir, `${stem}.png`), new Uint8Array(await png.arrayBuffer()));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(path.join(previewDir, `${stem}.layout.json`), await layout.text());
}

const montage = await pres.export({ format: "webp", montage: true, scale: 1 });
await fs.writeFile(path.join(previewDir, "deck-montage.webp"), new Uint8Array(await montage.arrayBuffer()));
const pptx = await PresentationFile.exportPptx(pres);
await pptx.save(finalPptx);

await fs.writeFile(
  path.join(qaDir, "visual-qa.txt"),
  `QA visual executado: ${pres.slides.items.length} slides renderizados em PNG e montage. Arquivo final: ${finalPptx}\n`,
  "utf8",
);

console.log(JSON.stringify({ finalPptx, slides: pres.slides.items.length, montage: path.join(previewDir, "deck-montage.webp") }, null, 2));
