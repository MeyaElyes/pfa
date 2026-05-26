# Fuel Station Monitoring System

A full-stack fuel monitoring and forecasting platform for AGIL fuel stations. Collects real-time telemetry, generates automated alerts, forecasts stock levels, and provides an AI-powered chat assistant.

---

## Architecture

Three independent services + one simulation agent:

```
pfa/
├── backend/        FastAPI REST API              → port 8000
├── chat/           AI chat microservice          → port 8001
├── frontend/       Angular 16 dashboard          → port 4200
└── stations/       Station simulation agent
```

---

## Features

- **Real-time ingestion** — stations push fuel telemetry every few seconds
- **Automated alerts** — LOW_STOCK, PRICE_ANOMALY, HIGH_CONSUMPTION, STATION_CRITICAL
- **Stock forecasting** — Prophet-based time-series predictions with LLM narrative
- **AI chat assistant** — Groq-powered agent with tool-calling and RAG over historical alerts
- **PDF reports** — LLM-generated station reports exported as PDF
- **Multi-station dashboard** — Angular SPA with live stock, history, alerts, forecast, and chat tabs

---

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- PostgreSQL 17

---

## Docker (recommended)

The fastest way to run the full stack.

**Prerequisites:** Docker Desktop

```bash
# 1. Copy and fill in your credentials
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD and GROQ_API_KEY at minimum

# 2. Build and start all services
docker compose up --build
```

| Service | URL |
|---|---|
| Dashboard | http://localhost |
| Backend API docs | http://localhost:8000/docs |
| Chat service docs | http://localhost:8001/docs |

```bash
# Stop everything
docker compose down

# Stop and delete all data (DB + vector store)
docker compose down -v
```

---

## Manual Setup

### 1. Python environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Backend dependencies

```bash
pip install -r requirements.txt
```

### 3. Frontend dependencies

```bash
cd frontend
npm install --legacy-peer-deps
```

### 4. Chat service dependencies

```bash
cd chat
pip install -r requirements.txt
```

### 5. Environment variables

Copy the template and fill in your values:

```bash
cp .env.example .env
```

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/fuelmonitor
GROQ_API_KEY=your_groq_api_key_here
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
MANAGER_EMAIL=manager@example.com
```

Get a free Groq API key at [console.groq.com](https://console.groq.com).

Also configure `chat/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
BACKEND_MODE=real
BACKEND_URL=http://localhost:8000
```

### 6. Initialize the database

Creates the PostgreSQL database and tables (run once):

```bash
python init_db.py
```

---

## Running

Start each service in a separate terminal, **in this order**:

**Terminal 1 — Backend API**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Chat microservice**
```bash
cd chat
python main.py
```

**Terminal 3 — Frontend**
```bash
cd frontend
npm start
```

**Terminal 4 — Station agent**
```bash
python stations/agilAgentStation.py
```

| Service | URL |
|---|---|
| Dashboard | http://localhost:4200 |
| Backend API docs | http://localhost:8000/docs |
| Chat service docs | http://localhost:8001/docs |

---

## Alert Thresholds

| Alert | Condition | Severity |
|---|---|---|
| LOW_STOCK | Stock < 15% of capacity | warning |
| LOW_STOCK | Stock < 5% of capacity | critical |
| PRICE_ANOMALY | Price deviates > 5% from official | warning |
| PRICE_ANOMALY | Price deviates > 10% from official | critical |
| HIGH_CONSUMPTION | Sales > 200 L in 5 minutes | warning |
| STATION_CRITICAL | Stock reaches 0 L | critical |

---

## Project Structure

```
backend/
├── main.py                  FastAPI app + startup
├── schemas.py               Pydantic request/response models
├── database/
│   ├── models.py            SQLAlchemy ORM models
│   └── database.py          DB engine and session factory
├── routes/
│   ├── ingest.py            POST /ingest
│   ├── data.py              GET /stations /current /history /alerts
│   ├── prophet_routes.py    GET /predict
│   └── report_routes.py     GET /report
├── services/
│   ├── storage.py           DB read/write helpers
│   ├── prophet_service.py   Stock forecasting
│   └── report_services.py   LLM report generation
└── agent/
    ├── watcher.py           Polls DB for critical alerts
    ├── responder.py         LLM decision-making for alerts
    └── actions.py           Executes alert actions (email, reorder)

chat/
├── main.py                  FastAPI app + RAG startup indexing
├── config.py                Settings from environment
├── schemas.py               Chat request/response models
├── routes/
│   ├── chat.py              POST /chat
│   └── alerts.py            GET /alerts (with LLM enrichment)
├── services/
│   ├── gemini_service.py    Groq LLM tool-calling loop
│   ├── agent_tools.py       Tool implementations (stock, alerts, forecast)
│   ├── retriever.py         ChromaDB RAG over historical alerts
│   └── alert_enricher.py   Async LLM alert explanations
└── mocks/
    └── backend_mock.py      Mock data for offline development

frontend/src/app/
├── core/
│   ├── models/              TypeScript interfaces
│   └── services/            HTTP services for all API endpoints
├── shared/                  Reusable components and pipes
└── features/
    ├── single-station/      Tabbed station view (overview, history, alerts, forecast, chat, report)
    └── multi-station/       Fleet overview with station cards and global alerts

stations/
└── agilAgentStation.py      Simulates 5 AGIL stations sending telemetry
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, PostgreSQL |
| Forecasting | Prophet, pandas |
| AI / LLM | Groq (llama-3.3-70b-versatile, llama-3.1-8b-instant) |
| RAG | ChromaDB + sentence-transformers |
| Reports | ReportLab, Markdown |
| Frontend | Angular 16, Chart.js |
| Communication | REST over HTTP |
