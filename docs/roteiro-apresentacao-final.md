# Roteiro da Apresentacao

Arquivo da apresentacao:

```text
apresentacao/Smart-Parking-Analytics-Apresentacao-Final.pptx
```

Tempo ideal: 8 a 12 minutos.

## Antes de apresentar

1. Abra o backend:

```powershell
cd C:\Users\Isaac\Documents\v2\Smart-Parking-Analytics\backend
.\restart_local.ps1
```

2. Abra o frontend:

```powershell
cd C:\Users\Isaac\Documents\v2\Smart-Parking-Analytics\frontend
npm run dev
```

3. Abra:

```text
http://127.0.0.1:5173
```

4. Tenha uma imagem de teste pronta em `dataset/test/images`.

## Slide 1 - Capa

Fala:

"Este projeto se chama Smart Parking Analytics. A ideia e transformar imagens ou videos de estacionamento em indicadores operacionais, usando YOLO treinado, API propria em FastAPI e dashboard proprio em React."

Ponto importante:

- Ja diga que o modelo nao e apenas pre-treinado: ele foi treinado com dataset personalizado.

## Slide 2 - Problema real

Fala:

"O problema e que estacionamentos precisam saber ocupacao em tempo real. Fazer isso manualmente e ruim, e sensores por vaga podem ser caros. Como muitos lugares ja possuem cameras, usamos visao computacional para gerar esses dados."

## Slide 3 - Proposta da solucao

Fala:

"A solucao recebe imagem ou video, passa pelo YOLO, calcula ocupacao e envia tudo para o dashboard. O diferencial e que nao paramos na deteccao: tambem temos historico, taxa de ocupacao, alertas e relatorios."

## Slide 4 - Ciclo completo de PDI

Fala:

"O projeto cobre o ciclo completo da disciplina: preparacao do dataset, anotacao, exportacao, treinamento, inferencia, API e interface grafica."

Se perguntarem sobre Roboflow:

"Usei Roboflow para organizar e exportar as anotacoes no formato YOLO26. O treino foi feito localmente com Ultralytics."

## Slide 5 - Dataset personalizado

Fala:

"O dataset final foi simplificado para uma classe: car. Isso deixou o projeto mais estavel para a demonstracao, porque o estacionamento analisado e composto apenas por carros."

Dados para falar:

- 166 imagens.
- 6688 carros anotados.
- 103 train, 34 validation, 29 test.
- Classe unica: `car`.

## Slide 6 - Treinamento

Fala:

"O modelo base foi o yolo26n.pt, usando Object Detection. Treinei por 100 epocas, imagem 640 e batch 4. O melhor peso foi salvo em backend/models/best.pt e e esse peso que a API carrega."

## Slide 7 - Metricas

Fala:

"As metricas ficaram boas para apresentacao: no validation, mAP50 de 0.930 e mAP50-95 de 0.871. No test separado, mAP50 de 0.921. Isso indica que o modelo generalizou bem dentro do dataset."

Explique rapidamente:

- Precision: quando o modelo detecta, qual a chance de estar certo.
- Recall: quantos carros reais ele consegue encontrar.
- mAP50: qualidade media da deteccao com criterio IoU 50%.
- mAP50-95: metrica mais exigente, avalia caixas em varios niveis de IoU.

## Slide 8 - Arquitetura

Fala:

"A arquitetura segue um fluxo profissional: React no frontend, FastAPI na API, servico YOLO para inferencia, banco de dados para historico e analytics, e modulo de relatorios."

Deploy:

"Localmente uso SQLite. Para deploy no Render, o correto e usar PostgreSQL via DATABASE_URL."

## Slide 9 - Logica de estacionamento

Fala essencial:

"Detectar carros nao e automaticamente saber qual vaga esta livre. Por isso o sistema tem dois modos. No modo capacidade, ele conta carros e calcula ocupacao pelo total de vagas. No modo poligonos, quando a camera e fixa e calibrada, ele associa cada carro a uma vaga especifica."

Se o professor questionar:

"Essa separacao deixa a solucao mais honesta tecnicamente. Para dizer exatamente qual vaga esta livre, a camera precisa ter os poligonos cadastrados para aquele enquadramento."

## Slide 10 - Demonstracao funcional

Fala:

"Aqui esta um teste real: o modelo detectou 23 carros. Com capacidade cadastrada de 40 vagas, o sistema calcula 23 ocupadas, 17 livres e 57,5% de ocupacao."

Demo ao vivo:

1. No dashboard, coloque `40` em Total de vagas.
2. Clique em `Salvar capacidade`.
3. Envie uma imagem.
4. Mostre:
   - Veiculos detectados.
   - Total de vagas.
   - Ocupadas.
   - Livres.
   - Taxa de ocupacao.
   - Imagem anotada.

## Slide 11 - API e interface

Fala:

"A interface nao e reaproveitada do YOLO. Ela e propria, feita em React. A API tambem e propria e expoe endpoints para predicao, video, relatorios, estatisticas e cadastro de vagas."

Endpoints para citar:

- `POST /api/predict`
- `POST /api/video/upload`
- `POST /api/parking-spots/capacity`
- `GET /api/statistics`
- `GET /api/history`
- `GET /api/reports`

## Slide 12 - Checklist

Fala:

"O projeto atende aos criterios: modelo treinado, YOLO correto para deteccao, interface e API proprias, regra de negocio alem do exemplo basico, metricas documentadas e organizacao de repositorio."

## Slide 13 - Fechamento

Fala:

"O Smart Parking Analytics demonstra uma aplicacao pratica de visao computacional com ciclo completo: dataset, treinamento, inferencia, API, interface e analytics. Como melhoria futura, eu adicionaria um editor visual de poligonos e WebSockets para tempo real."

## Perguntas provaveis e respostas

### Por que usar classe unica `car`?

"Porque o novo dataset tem melhor consistencia para carros. Como o estacionamento da demo e composto por carros, isso reduz erro de classe e melhora a estabilidade."

### O modelo foi treinado mesmo?

"Sim. O treino foi feito por 100 epocas com yolo26n.pt. As metricas e graficos estao em `docs/training-results`, e o peso final esta em `backend/models/best.pt`."

### Como calcula vagas livres?

"No modo capacidade: total de vagas menos carros detectados. No modo poligono: cada carro e associado a uma vaga calibrada por sobreposicao da bounding box com a area da vaga."

### Por que nao usar apenas YOLO pronto?

"Porque o criterio exige modelo proprio ou personalizado. O YOLO pre-treinado foi usado apenas como base; o peso final foi treinado no dataset personalizado."

### O que torna isso aplicavel no mundo real?

"Ele gera indicadores operacionais: ocupacao, historico, picos, alertas e relatorios. Isso pode apoiar shoppings, universidades, condominios e empresas."
