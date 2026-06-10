# Treinamento YOLO

## Modelo base

Use `yolo11n.pt` pela relacao entre velocidade, tamanho e acuracia.

## Dataset

Classes:

```text
car
motorcycle
pickup
van
```

Split recomendado:

```text
train: 70%
val: 20%
test: 10%
```

## data.yaml

```yaml
path: ../dataset
train: images/train
val: images/val
test: images/test

names:
  0: car
  1: motorcycle
  2: pickup
  3: van
```

## Comando sugerido

```bash
yolo detect train model=yolo11n.pt data=dataset/data.yaml epochs=100 imgsz=640 batch=16 patience=20
```

Copie o melhor peso para:

```text
backend/models/best.pt
```

## Metricas-alvo para apresentacao

| Metrica | Bom |
|---|---:|
| Precision | > 0.85 |
| Recall | > 0.80 |
| mAP50 | > 0.85 |
| mAP50-95 | > 0.55 |
