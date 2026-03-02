# Enterprise RAG Platform

## Project Setup

### Quick Start (Docker)

```bash
# 1. Copy and fill in your environment variables
cp .env.example .env

# 2. Build and start all services
docker compose up --build

# Services:
#   Frontend (Next.js)  → http://localhost:3000
#   Backend (FastAPI)   → http://localhost:8000  (Swagger UI: /docs)
#   Qdrant Vector DB    → http://localhost:6333  (Dashboard: /dashboard)
```

### Local Development (without Docker)

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
cp .env.local.example .env.local   # fill in values
npm install
npm run dev
```

## Architecture

```
Enterprise-RAG/
├── docker-compose.yml        # Orchestrates all services on rag_network (bridge)
├── .env.example              # Root env template
├── backend/
│   ├── main.py               # FastAPI app (GET /health, GET /)
│   ├── requirements.txt      # fastapi, uvicorn, python-jose, pydantic
│   └── Dockerfile            # Multi-stage Python 3.12-slim image
└── frontend/
    ├── app/
    │   ├── page.tsx           # Landing page (MUI + Lucide icons)
    │   └── api/auth/[...nextauth]/route.ts   # NextAuth handler stub
    ├── next.config.ts         # standalone output + API URL env
    ├── .env.local.example     # Frontend env template
    └── Dockerfile             # Multi-stage Node 20-alpine image
```

## Environment Variables

| Variable | Where | Description |
|---|---|---|
| `NEXTAUTH_SECRET` | root `.env` | JWT signing secret (generate with `openssl rand -base64 32`) |
| `OIDC_CLIENT_ID` | root `.env` | OAuth2 / OIDC client identifier |
| `DATABASE_URL` | root `.env` | PostgreSQL (or other) connection string |
| `NEXT_PUBLIC_API_URL` | frontend `.env.local` | Backend API URL visible to browser |
