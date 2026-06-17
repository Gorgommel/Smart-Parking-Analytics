# Deploy no Render e na Vercel

Objetivo:

- Backend FastAPI no Render.
- Banco PostgreSQL no Render.
- Frontend React + Vite na Vercel.

## Visao geral

```text
Vercel Frontend
  ↓
Render FastAPI
  ↓
Render PostgreSQL
```

Localmente o projeto pode usar SQLite. Em deploy, use PostgreSQL porque o filesystem do Render pode ser temporario e o banco precisa persistir.

## Checklist antes do deploy

- [ ] Projeto publicado no GitHub.
- [ ] `backend/models/best.pt` presente no repositorio ou disponivel por link.
- [ ] `backend/requirements.txt` atualizado.
- [ ] `frontend/package.json` com script `build`.
- [ ] README com instrucoes.
- [ ] Confirmar que o backend roda localmente.
- [ ] Confirmar que o frontend roda localmente.

## Parte 1 - Preparar o repositorio

Na raiz do projeto:

```powershell
cd C:\Users\Isaac\Documents\v2\Smart-Parking-Analytics
git status
```

Se ainda nao tiver Git inicializado:

```powershell
git init
git add .
git commit -m "final smart parking analytics"
```

Crie um repositorio no GitHub e envie:

```powershell
git remote add origin https://github.com/SEU_USUARIO/Smart-Parking-Analytics.git
git branch -M main
git push -u origin main
```

Observacao importante:

Se o GitHub reclamar do tamanho do `backend/models/best.pt`, use Git LFS ou hospede o peso em Drive/Release e documente o link no README. O arquivo atual tem cerca de 5 MB, entao deve caber normalmente no GitHub.

## Parte 2 - Criar PostgreSQL no Render

1. Acesse:

```text
https://render.com
```

2. Clique em `New`.
3. Escolha `PostgreSQL`.
4. Configure:

```text
Name: smart-parking-db
Region: a mesma do backend
PostgreSQL Version: default
Plan: Free ou o plano disponivel
```

5. Clique em `Create Database`.
6. Depois de criado, copie o valor `External Database URL` ou `Internal Database URL`.

Preferencia:

- Use `Internal Database URL` se o backend tambem estiver no Render.
- Use `External Database URL` apenas para testes externos.

## Parte 3 - Criar backend FastAPI no Render

1. No Render, clique em `New`.
2. Escolha `Web Service`.
3. Conecte o repositorio do GitHub.
4. Configure:

```text
Name: smart-parking-api
Runtime: Python
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. Em `Environment Variables`, cadastre:

```text
DATABASE_URL=<Internal Database URL do PostgreSQL>
MODEL_PATH=models/best.pt
CONFIDENCE_THRESHOLD=0.35
OCCUPANCY_ALERT_THRESHOLD=0.9
DEMO_MODE=false
CORS_ORIGINS=http://localhost:5173
```

Depois que o frontend estiver na Vercel, volte e troque `CORS_ORIGINS` para incluir a URL real:

```text
CORS_ORIGINS=http://localhost:5173,https://SEU-FRONTEND.vercel.app
```

6. Clique em `Create Web Service`.

## Parte 4 - Testar backend no Render

Quando o deploy terminar, abra:

```text
https://SEU-BACKEND.onrender.com/health
```

Resposta esperada:

```json
{
  "status": "ok",
  "app": "Smart Parking Analytics API"
}
```

Teste tambem o Swagger:

```text
https://SEU-BACKEND.onrender.com/docs
```

## Parte 5 - Possiveis problemas no Render

### Erro por causa do PyTorch/Ultralytics

O pacote `ultralytics` instala dependencias pesadas. Se o Render Free falhar por memoria ou timeout, opcoes:

1. Tentar novamente.
2. Usar plano pago temporario.
3. Fazer deploy sem treino, apenas inferencia.
4. Usar uma imagem Docker customizada.

### Backend dorme no plano gratuito

No plano gratuito, o Render pode dormir. Na primeira chamada, a API demora para acordar. Isso e normal.

### Imagens anotadas somem

No Render, arquivos em `outputs/` podem sumir se o ambiente reiniciar, a menos que voce configure disco persistente. Para apresentacao academica isso nao impede a demo, mas em producao use storage externo.

### Banco nao cria tabelas

O app chama `init_db()` ao iniciar. Se `DATABASE_URL` estiver correto, ele cria as tabelas automaticamente.

## Parte 6 - Criar frontend na Vercel

1. Acesse:

```text
https://vercel.com
```

2. Clique em `Add New Project`.
3. Importe o mesmo repositorio do GitHub.
4. Configure:

```text
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

5. Em `Environment Variables`, cadastre:

```text
VITE_API_URL=https://SEU-BACKEND.onrender.com/api
VITE_API_ORIGIN=https://SEU-BACKEND.onrender.com
```

6. Clique em `Deploy`.

## Parte 7 - Ajustar CORS no Render

Depois que a Vercel gerar a URL, volte no Render:

1. Abra o servico `smart-parking-api`.
2. Va em `Environment`.
3. Atualize:

```text
CORS_ORIGINS=http://localhost:5173,https://SEU-FRONTEND.vercel.app
```

4. Clique em `Save Changes`.
5. O Render vai redeployar.

## Parte 8 - Testar frontend publicado

Abra:

```text
https://SEU-FRONTEND.vercel.app
```

Teste:

1. Coloque `40` em Total de vagas.
2. Clique em `Salvar capacidade`.
3. Envie uma imagem.
4. Verifique se aparecem:
   - Veiculos detectados.
   - Vagas ocupadas.
   - Vagas livres.
   - Taxa de ocupacao.
   - Imagem anotada.

## Parte 9 - Se der erro no upload

Verifique no DevTools do navegador:

### Erro CORS

Sintoma:

```text
blocked by CORS policy
```

Correcao:

```text
CORS_ORIGINS=https://SEU-FRONTEND.vercel.app
```

Ou com local:

```text
CORS_ORIGINS=http://localhost:5173,https://SEU-FRONTEND.vercel.app
```

### Erro 404

Confira se o frontend esta usando:

```text
VITE_API_URL=https://SEU-BACKEND.onrender.com/api
```

Nao use somente:

```text
https://SEU-BACKEND.onrender.com
```

porque as rotas ficam abaixo de `/api`.

### Erro ao abrir imagem anotada

Confira se:

```text
VITE_API_ORIGIN=https://SEU-BACKEND.onrender.com
```

O frontend usa essa variavel para abrir `/static/outputs/...`.

## Parte 10 - Ordem correta resumida

1. Subir codigo no GitHub.
2. Criar PostgreSQL no Render.
3. Criar backend no Render.
4. Testar `/health`.
5. Criar frontend na Vercel.
6. Copiar URL da Vercel.
7. Atualizar `CORS_ORIGINS` no Render.
8. Testar upload pela URL da Vercel.

## Variaveis finais esperadas

Render backend:

```text
DATABASE_URL=postgresql://...
MODEL_PATH=models/best.pt
CONFIDENCE_THRESHOLD=0.35
OCCUPANCY_ALERT_THRESHOLD=0.9
DEMO_MODE=false
CORS_ORIGINS=http://localhost:5173,https://SEU-FRONTEND.vercel.app
```

Vercel frontend:

```text
VITE_API_URL=https://SEU-BACKEND.onrender.com/api
VITE_API_ORIGIN=https://SEU-BACKEND.onrender.com
```

## Observacao para apresentacao

Para a banca, o deploy e um diferencial, mas nao substitui a demo local. Como YOLO e Ultralytics podem deixar o deploy mais pesado, tenha sempre a demo local pronta como plano principal.
