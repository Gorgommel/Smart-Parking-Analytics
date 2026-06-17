# Deploy

## Arquitetura recomendada

```text
Vercel Static Site -> React + Vite
Render Web Service -> FastAPI + YOLO26
Render PostgreSQL -> historico, eventos, alertas e relatorios
```

## Frontend na Vercel

Configuracao:

```text
Framework Preset: Vite
Root Directory: frontend
Build Command: npm install && npm run build
Output Directory: dist
```

Variaveis de ambiente:

```text
VITE_API_URL=https://sua-api.onrender.com/api
VITE_API_ORIGIN=https://sua-api.onrender.com
```

O arquivo `frontend/vercel.json` redireciona rotas SPA para `index.html`.

## Backend no Render

Criar um Web Service apontando para o repositorio.

Configuracao:

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Variaveis de ambiente:

```text
DATABASE_URL=<internal database URL do Render PostgreSQL>
CORS_ORIGINS=https://seu-front.vercel.app,http://localhost:5173
MODEL_PATH=models/best.pt
FALLBACK_MODEL=yolo26n.pt
DEMO_MODE=false
```

## PostgreSQL

No Render, crie um Postgres database na mesma regiao do backend e use a Internal Database URL em `DATABASE_URL`.

Localmente, se `DATABASE_URL` estiver vazio, a API usa SQLite (`smart_parking.db`).

## Peso do modelo

O arquivo `backend/models/best.pt` precisa estar disponivel para o backend.

Opcoes:

1. Incluir `backend/models/best.pt` no repositorio se o arquivo couber.
2. Publicar o peso em uma GitHub Release e baixar no build/start.
3. Usar storage externo e baixar o arquivo antes de iniciar a API.

Para apresentacao academica, a opcao mais simples e incluir link para o peso no README.
