# PFA Project Description

## Overview

This project is a fuel monitoring and forecasting system for an AGIL fuel station environment. It includes a FastAPI backend, an Angular frontend dashboard, a database layer, and a simulated station agent that generates ingest data.

The main purpose is to:
- collect fuel station telemetry (stock, price, sales, capacity)
- store records in SQLite
- generate alerts for low stock, price anomalies, high consumption, and out-of-stock events
- provide history, current state, station metadata, and AI forecast endpoints
- display live and historical metrics through an Angular single-page dashboard
- simulate a station sending data via a local agent

## Key Components

### Backend

- `pfa/backend/main.py`
  - Creates the FastAPI app
  - Adds CORS middleware for local frontend access
  - Initializes the SQLite database tables
  - Includes routers for ingest, read operations, and Prophet predictions

- `pfa/backend/routes/ingest.py`
  - Defines the `/ingest` endpoint
  - Stores incoming fuel telemetry via `storage.store_fuel_data`
  - Runs alert generation after data ingestion

- `pfa/backend/routes/data.py`
  - Implements `/stations`, `/companies`, `/current`, `/history`, and `/alerts`
  - Generates alerts based on fuel record thresholds
  - Queries current and historical fuel data

- `pfa/backend/routes/prophet_routes.py`
  - Implements `/predict`
  - Calls the Prophet service to produce stock forecasts

- `pfa/backend/schemas.py`
  - Pydantic models for request and response payloads
  - Defines `FuelData`, `FuelDataResponse`, and `AlertResponse`

- `pfa/backend/services/storage.py`
  - Writes fuel data and alerts to the database
  - Reads fuel history and alerts for reporting

- `pfa/backend/services/prophet_service.py`
  - Trains a Prophet model on fuel stock history
  - Produces short-term stock predictions using 5-minute intervals

- `pfa/backend/database/database.py`
  - SQLAlchemy engine configuration for SQLite
  - Session factory and `get_db()` dependency generator

- `pfa/backend/database/models.py`
  - SQLAlchemy ORM models
  - `Station`, `FuelData`, and `Alert` tables

### Frontend (Angular 16)

The frontend is a modular Angular single-page application that consumes the FastAPI backend over HTTP.

Directory layout (`pfa/frontend/src/app/`):

- `app.module.ts`, `app-routing.module.ts`, `app.component.*`
  - Application shell with sidebar, view-mode switcher, and `<router-outlet>`
  - Loads station metadata once on startup and shares it via the context service
- `core/`
  - `models/` — TypeScript interfaces for `Station`, `FuelData`, `FuelAlert`, and `ForecastPoint`
  - `services/` — `ApiService` (thin HttpClient wrapper), feature services (`StationService`, `FuelDataService`, `AlertService`, `ForecastService`), and `StationContextService` for shared selection state
- `shared/`
  - `SharedModule` re-exports `CommonModule` + `FormsModule` and the reusable presentational components
  - Components: `StatusBadge`, `StatCard`, `ProgressBar`, `EmptyState`, `LoadingSpinner`
  - Pipe: `SeverityTonePipe` maps backend severities to badge tones
- `features/single-station/`
  - Lazy-loaded module with a tabbed layout
  - Tab components: `OverviewComponent`, `HistoryComponent`, `AlertsComponent`, `ForecastComponent`
  - Each tab is a small, focused component that subscribes to the shared station context
- `features/multi-station/`
  - Lazy-loaded module with a fleet overview (station cards, detailed table, global alerts)

Each feature component owns its own template, stylesheet, and TypeScript controller, so concerns stay isolated and the codebase scales cleanly.

### Station Simulation

- `pfa/stations/agilAgentStation.py`
  - Simulates station telemetry every few seconds
  - Sends `/ingest` payloads to the backend
  - Creates randomized sales, stock drain, and occasional price anomalies

## Supporting Files

- `pfa/requirements.txt`
  - Lists required Python dependencies: FastAPI, Uvicorn, SQLAlchemy, Pydantic, requests, pandas, and Prophet support
- `pfa/init_db.py`
  - Intended to create database tables before starting the app
  - Bootstraps the SQLite schema from backend models
- `pfa/.gitignore`
  - Standard Python ignore rules for virtual environments, database files, logs, compiled artifacts, and IDE settings
- `pfa/frontend/package.json` / `pfa/frontend/angular.json`
  - Angular workspace configuration

## Running the Project

1. Create or activate the Python environment.
2. Install dependencies from `pfa/requirements.txt`.
3. Initialize the database with `pfa/init_db.py` or by running the backend app.
4. Start the backend with `uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000` from `pfa/`.
5. In another shell, install frontend deps (`cd pfa/frontend && npm install`) and run `npm start`. The dev server listens on `http://localhost:4200`.
6. Optionally run the station simulator with `python stations/agilAgentStation.py`.

## Project Structure

- `pfa/backend/` - API implementation, database models, schemas, and services
- `pfa/frontend/` - Angular workspace (modular dashboard SPA)
- `pfa/stations/` - data ingestion simulation agent
- `pfa/requirements.txt` - dependency list
- `pfa/init_db.py` - database bootstrap script
- `pfa/.gitignore` - ignored files and folders

## Notes

- The project uses an SQLite database at `sql_app.db` by default.
- Some files contain comments or placeholder logic for future improvements, especially around station metadata and alert persistence.
- The forecast route is based on Prophet and expects sufficient historical data for meaningful predictions.
- The Angular frontend points at `http://localhost:8000` by default (`src/environments/environment.ts`); adjust `apiUrl` for production builds in `environment.prod.ts`.
