# AGIL Fuel Monitor Pro

AGIL Fuel Monitor Pro is a fuel station monitoring platform built with FastAPI, SQLite, and Streamlit. It ingests fuel telemetry, stores time-series data, generates alerts, deduplicates repeated alert conditions, and runs a background agent that can hand critical alerts to Grok (xAI) for automated response selection.

## What It Does

- Tracks fuel stock, pricing, and recent sales for each station.
- Generates alerts for low stock, price anomalies, high consumption, and out-of-stock stations.
- Deduplicates alerts with a fingerprint based on station, fuel type, and alert type.
- Lets operators acknowledge or resolve alerts through the API.
- Runs a background watcher that polls for critical new alerts and sends them to a Grok-powered responder.
- Provides a Streamlit dashboard for live monitoring and forecasting.

## Project Structure

```text
pfa/
├─ backend/
│  ├─ agent/
│  │  ├─ actions.py
│  │  ├─ responder.py
│  │  └─ watcher.py
│  ├─ database/
│  │  ├─ database.py
│  │  ├─ models.py
│  │  └─ seed.py
│  ├─ routes/
│  │  ├─ data.py
│  │  ├─ ingest.py
│  │  └─ prophet_routes.py
│  ├─ services/
│  │  ├─ prophet_service.py
│  │  └─ storage.py
│  ├─ main.py
│  └─ schemas.py
├─ frontend/
│  ├─ api_client.py
│  └─ app.py
├─ stations/
│  └─ agilAgentStation.py
├─ init_db.py
└─ requirements.txt
```

## Tech Stack

- **Backend:** FastAPI
- **Database:** SQLite + SQLAlchemy
- **Frontend:** Streamlit
- **Forecasting:** Prophet route/service integration
- **Agent:** Background watcher + Grok (xAI) responder

## Requirements

- Python 3.10+ recommended
- A virtual environment
- Grok API key in `.env`

## Installation

From the `pfa/` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root with your Grok key:

```env
GROK_API_KEY=xai-your-key-here
```

The backend loads `.env` on startup.

## Database Setup

The app uses SQLite and stores data in `sql_app.db`.

To create or reset the database:

```powershell
python init_db.py
```

Station seed data is loaded automatically on app startup. You can also run the seed script directly:

```powershell
python -m backend.database.seed
```

Seeded stations:

- `BI00001` - AGIL - Tunis Centre
- `BI00002` - AGIL - Tunis Nord
- `BI00003` - AGIL - Sousse

## Running the Backend

From the `pfa/` folder:

```powershell
uvicorn backend.main:app --reload
```

The backend will:

- Load environment variables from `.env`
- Create tables if needed
- Seed stations
- Start the background alert watcher

Backend URL:

- `http://127.0.0.1:8000`

## Running the Frontend

In a second terminal:

```powershell
streamlit run frontend/app.py
```

The Streamlit app uses `frontend/api_client.py` to talk to the FastAPI backend.

## Startup Order

1. Activate the virtual environment.
2. Install dependencies.
3. Create `.env` with `GROK_API_KEY`.
4. Initialize or reset the database if needed.
5. Start the FastAPI backend.
6. Start the Streamlit frontend.

Example:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
uvicorn backend.main:app --reload
```

In another terminal:

```powershell
streamlit run frontend/app.py
```

## API Overview

### Read and Alert Endpoints

- `GET /stations` - list stations
- `GET /companies` - list companies
- `GET /current?station_id=...` - current fuel snapshot
- `GET /history?station_id=...&fuel_type=...` - historical fuel data
- `GET /alerts` - list alerts with optional filters
- `PATCH /alerts/{alert_id}` - acknowledge or resolve an alert
- `POST /agent/trigger` - manual trigger endpoint for a specific alert

### Ingest Endpoint

The ingest router handles incoming fuel data and generates alerts from it.

## Alert Lifecycle

1. Fuel data is stored.
2. Alert rules run against the new record.
3. A fingerprint is generated from `station_id + fuel_type + alert_type`.
4. If an unresolved alert with the same fingerprint exists, the alert is skipped.
5. Otherwise, a new alert is saved with `status="new"`.
6. The watcher polls for `status="new"` and `severity="critical"` alerts.
7. The responder sends the alert context to Grok.
8. The selected action runs through the action handlers.

## Alert Model Fields

The `alerts` table includes:

- `id`
- `timestamp`
- `station_id`
- `fuel_type`
- `alert_type`
- `severity`
- `message`
- `status` (`new`, `acknowledged`, `resolved`)
- `handled_by`
- `handled_at`
- `fingerprint`

## Agent Workflow

- `backend/agent/watcher.py` polls the database every 30 seconds.
- `backend/agent/responder.py` calls Grok through the xAI API.
- `backend/agent/actions.py` currently logs actions and can be extended later.

## Notes

- The app currently uses SQLite for development.
- The Grok integration expects `GROK_API_KEY` to be set in `.env`.
- The agent is designed to be background-only and starts with the FastAPI lifespan hook.
- The frontend will fall back to mock station data if the backend is not reachable.

## Troubleshooting

- If `backend` imports fail, run commands from the `pfa/` directory.
- If the app complains about missing stations, rerun `python -m backend.database.seed` or restart the backend.
- If Grok calls fail, verify `GROK_API_KEY` in `.env` and that outbound network access is available.

## License

No license has been specified yet.