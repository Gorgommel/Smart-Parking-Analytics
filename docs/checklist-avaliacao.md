# Checklist de Avaliacao

Projeto: Smart Parking Analytics

## 1. Treinamento do modelo - 2.5 pontos

Status: Totalmente implementado, se o repositorio entregar o dataset, o peso `backend/models/best.pt` e as metricas.

- [x] Dataset personalizado exportado do Roboflow em formato YOLO26.
- [x] Dataset final adaptado para classe unica `car`.
- [x] Split documentado: 103 train, 34 validation, 29 test.
- [x] Total de 166 imagens e 6688 carros anotados.
- [x] Treinamento executado por 100 epocas com `yolo26n.pt`.
- [x] Peso final copiado para `backend/models/best.pt`.
- [x] Metricas documentadas em `docs/training-results/training-summary.md`.
- [x] Evidencias salvas: `results.csv`, `results.png`, matriz de confusao e curvas PR/F1.

Metricas finais:

- Validation: Precision 0.915, Recall 0.885, mAP50 0.930, mAP50-95 0.871.
- Test: Precision 0.913, Recall 0.919, mAP50 0.921, mAP50-95 0.865.

## 2. Uso correto do YOLO - 1.5 pontos

Status: Totalmente implementado.

- [x] Tarefa correta: Object Detection.
- [x] Modelo base coerente: `yolo26n.pt`.
- [x] Modelo customizado carregado pela API.
- [x] Inferencia real via Ultralytics, nao apenas demo visual.
- [x] API retorna bounding boxes, confianca, classe, imagem anotada e status do modelo.

## 3. Interface grafica propria + API - 2.0 pontos

Status: Totalmente implementado para imagem e video por amostragem.

- [x] Frontend proprio em React + Vite.
- [x] API propria em FastAPI.
- [x] Upload de imagem em `POST /api/predict`.
- [x] Upload de video em `POST /api/video/upload`.
- [x] Dashboard com total de vagas, ocupadas, livres, taxa de ocupacao e carros detectados.
- [x] Visualizacao de imagem anotada.
- [x] Historico e graficos.
- [x] Relatorios CSV e PDF.
- [x] Indicador de modo de ocupacao: poligonos calibrados ou capacidade total.

## 4. Robustez e aplicabilidade do tema - 1.5 pontos

Status: Totalmente implementado, desde que a apresentacao explique a calibracao.

- [x] O sistema vai alem de contador YOLO simples.
- [x] Possui regra de negocio de ocupacao.
- [x] Possui historico temporal.
- [x] Possui estatisticas e horarios de pico.
- [x] Possui alerta de lotacao acima do limite.
- [x] Suporta dois modos reais:
  - `configured`: vagas por poligonos calibrados da camera.
  - `capacity_only`: carros detectados sobre capacidade total cadastrada.

Ponto que deve ser explicado oralmente:

> Detectar carros nao e o mesmo que identificar exatamente cada vaga livre. Para vaga especifica, cada camera precisa de poligonos calibrados. Quando a camera ainda nao esta calibrada, o sistema calcula ocupacao agregada pela capacidade total do estacionamento.

## 5. Apresentacao oral - 1.5 pontos

Status: Preparado, depende do ensaio.

- [x] Roteiro recomendado no README.
- [x] Evidencias de treinamento prontas.
- [x] Modelo treinado disponivel.
- [x] Demo local com backend e frontend.
- [x] Explicacao clara do dataset simplificado para `car`.
- [ ] Ensaiar demonstracao ao vivo antes da entrega.

## 6. Organizacao do repositorio - 1.0 ponto

Status: Totalmente implementado quando o GitHub estiver publico e o peso estiver acessivel.

- [x] README com instrucoes de execucao.
- [x] Estrutura separada em backend, frontend, dataset, docs e reports.
- [x] Diagrama Mermaid no README.
- [x] Fluxograma draw.io em `docs/architecture.drawio`.
- [x] Metricas em `docs/training-results/`.
- [x] Peso em `backend/models/best.pt`.
- [ ] Publicar repositorio.
- [ ] Confirmar se o GitHub aceita o tamanho do `best.pt`; se nao aceitar, publicar link no README.

## Nota estimada

Se o repositorio publico incluir dataset, peso, metricas e a demo rodar:

- Treinamento: 2.5 / 2.5
- YOLO: 1.5 / 1.5
- GUI + API: 2.0 / 2.0
- Robustez: 1.5 / 1.5
- Apresentacao: 1.5 / 1.5, se ensaiada
- Organizacao: 1.0 / 1.0

Total estimado: 10.0 / 10.0.
