# Resultado do Treinamento Final

Modelo base: YOLO26n
Peso final usado pela API: backend/models/best.pt
Dataset final: classe unica car
Total: 166 imagens
Train: 103 imagens
Validation: 34 imagens
Test: 29 imagens
Objetos anotados: 6688 carros
Epochs: 100
Image size: 640
Batch: 4
Device: CPU

Melhor metrica em validation durante treino:
- Epoch: 80
- Precision: 0.91478
- Recall: 0.88481
- mAP50: 0.93021
- mAP50-95: 0.87089

Validation final do best.pt:
- Precision: 0.915
- Recall: 0.885
- mAP50: 0.930
- mAP50-95: 0.871

Teste separado no split test:
- Precision: 0.913
- Recall: 0.919
- mAP50: 0.921
- mAP50-95: 0.865

Artefatos principais:
- docs/training-results/results.csv
- docs/training-results/results.png
- docs/training-results/confusion_matrix.png
- docs/training-results/confusion_matrix_normalized.png
- docs/training-results/BoxPR_curve.png
- docs/training-results/BoxF1_curve.png
- docs/training-results/test/
