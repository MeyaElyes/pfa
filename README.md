# Fuel Monitor API

A real-time fuel station monitoring system for Tunisia. It tracks fuel prices, stock levels, and consumption across stations — and automatically detects anomalies like price manipulation, dangerously low stock, and unusual consumption spikes.

Built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

---

## Why This Exists

Tunisia has regulated fuel prices, but individual stations can deviate. Stock shortages happen without warning. This API acts as a **central monitoring backend** that:

1. **Ingests** live readings from fuel stations (price, stock, sales every 5 minutes)
2. **Detects** anomalies automatically via a rule-based alert engine
3. **Serves** data to dashboards and mobile apps through clean REST endpoints

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server (auto-creates the SQLite database)
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 3. Seed with mock data (in a separate terminal)
python seed_data.py

# 4. Explore the API
#    Open http://localhost:8000/docs in your browser
```

---

## Architecture

```
                    POST /ingest/batch
  Stations ──────────────────────────────> [ Ingest Layer ]
  (every 5 min)                                  │
                                                 ├──> Save to DB (fuel_logs table)
                                                 └──> Alert Engine
                                                        │
                                           ┌────────────┼────────────┐
                                           ▼            ▼            ▼
                                       Low Stock   Price Anomaly  High Consumption
                                           │            │            │
                                           └────────────┴────────────┘
                                                        │
                                                        ▼
                                                  alerts table
                                                        │
                              GET /alerts    ◄──────────┘
                              GET /analytics/dashboard
                              GET /analytics/station-summary
```

---

## API Reference

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Returns `{"status": "healthy", "version": "2.0.0"}` |
| `/docs` | GET | Interactive Swagger UI documentation |

### Ingestion — Receiving Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ingest/` | POST | Submit a single fuel reading |
| `/ingest/batch` | POST | Submit multiple readings at once |

**Single reading payload:**
```json
{
  "timestamp": "2026-04-17T15:00:00",
  "station_id": "AGIL-TUN-001",
  "company": "AGIL",
  "fuel_type": "Gasoil50",
  "price_tnd": 2.085,
  "official_price_tnd": 2.085,
  "stock_liters": 25000,
  "capacity_liters": 30000,
  "sales_last_5min_liters": 45.2
}
```

**Batch payload:**
```json
{
  "records": [
    { ... },
    { ... }
  ]
}
```

**Fuel types:** `"Gasoil50"` (diesel) or `"SansPlomb"` (unleaded gasoline).

### Data — Querying

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/current` | GET | `station_id` (required) | Latest reading per fuel type for a station |
| `/history` | GET | `station_id` (required), `fuel_type`, `limit` | Time-series data for charts |
| `/alerts` | GET | `station_id`, `severity`, `alert_type`, `limit` | Filtered alert list |
| `/stations` | GET | — | All station IDs that have submitted data |
| `/stations` | POST | — | Create one station manually for testing |
| `/run-agent` | POST | `station_id` (required) | Manually re-run alert checks |

**Create one test station payload:**
```json
{
  "station_id": "TEST-TUN-001",
  "company": "AGIL",
  "location": "Tunis"
}
```

### Analytics — Insights

| Endpoint | Method | Params | Description |
|----------|--------|--------|-------------|
| `/analytics/dashboard` | GET | — | System-wide stats (total records, alerts, avg stock) |
| `/analytics/station-summary` | GET | `station_id` (required) | Per-fuel breakdown with consumption rate & time-to-empty |

**Dashboard response example:**
```json
{
  "total_records": 144,
  "total_alerts": 14,
  "total_stations": 3,
  "active_alerts": 14,
  "avg_stock_pct": 72.6,
  "latest_update": "2026-04-17T15:18:17"
}
```

**Station summary response example:**
```json
[
  {
    "station_id": "SHELL-SFX-002",
    "company": "Shell",
    "fuel_type": "Gasoil50",
    "latest_price_tnd": 2.085,
    "official_price_tnd": 2.085,
    "price_deviation_pct": 0.0,
    "stock_pct": 62.0,
    "stock_liters": 18591.0,
    "capacity_liters": 30000.0,
    "consumption_rate_lph": 562.8,
    "hours_until_empty": 33.0,
    "alert_count": 3
  }
]
```

---

## Alert Engine

Every time a reading is ingested, the system checks for 4 types of anomalies:

| Alert Type | Trigger | Severity |
|------------|---------|----------|
| `LOW_STOCK` | Stock < 15% of tank capacity | warning |
| `LOW_STOCK` | Stock < 5% of tank capacity | **critical** |
| `PRICE_ANOMALY` | Price deviates > 5% from official | warning |
| `PRICE_ANOMALY` | Price deviates > 10% from official | **critical** |
| `HIGH_CONSUMPTION` | Sales > 200 liters in 5 minutes | warning |
| `STATION_CRITICAL` | Stock is exactly 0 liters | **critical** |

Alerts are stored in the `alerts` table with a `resolved` flag (default `false`) so they can be tracked and cleared by a frontend.

---

## Project Structure

```
fuel_monitor/
├── main.py              # App entry point, CORS, lifespan, health check
├── database.py          # SQLAlchemy engine + session (SQLite)
├── models.py            # DB tables: FuelLog, Alert, Station
├── schemas.py           # Pydantic request/response models
├── requirements.txt     # Python dependencies
├── seed_data.py         # Generates 144 mock readings for 3 stations
│
├── routes/
│   ├── ingest.py        # POST /ingest/, POST /ingest/batch
│   ├── data.py          # GET /current, /history, /alerts, /stations
│   └── analytics.py     # GET /analytics/dashboard, /station-summary
│
└── services/
    ├── storage.py       # Persistence + alert engine logic
    └── queries.py       # SQL queries, aggregations, summaries
```

---

## Data Model

### fuel_logs
| Column | Type | Description |
|--------|------|-------------|
| id | int | Auto-increment primary key |
| timestamp | datetime | When the reading was taken |
| station_id | string | Unique station identifier (e.g. `AGIL-TUN-001`) |
| company | string | Fuel company name |
| fuel_type | string | `Gasoil50` or `SansPlomb` |
| price_tnd | float | Actual price in Tunisian Dinars per liter |
| official_price_tnd | float | Government-set official price |
| stock_liters | float | Current fuel stock in liters |
| capacity_liters | float | Total tank capacity in liters |
| sales_last_5min_liters | float | Volume sold in the last 5-minute window |

### alerts
| Column | Type | Description |
|--------|------|-------------|
| id | int | Auto-increment primary key |
| timestamp | datetime | When the alert was generated |
| station_id | string | Which station triggered it |
| fuel_type | string | Which fuel type |
| alert_type | string | `LOW_STOCK`, `PRICE_ANOMALY`, `HIGH_CONSUMPTION`, `STATION_CRITICAL` |
| severity | string | `warning` or `critical` |
| message | string | Human-readable description |
| resolved | bool | Whether the alert has been cleared |

### stations
| Column | Type | Description |
|--------|------|-------------|
| id | int | Auto-increment primary key |
| station_id | string | Unique identifier |
| name | string | Display name |
| company | string | Fuel company |
| governorate | string | Tunisian governorate (region) |
| latitude | float | GPS latitude (optional) |
| longitude | float | GPS longitude (optional) |

---

## Mock Data

The `seed_data.py` script simulates 3 Tunisian stations:

| Station ID | Company | Location |
|------------|---------|----------|
| `AGIL-TUN-001` | AGIL | Tunis |
| `SHELL-SFX-002` | Shell | Sfax |
| `TOTAL-SOU-003` | TotalEnergies | Sousse |

It generates 2 hours of readings at 5-minute intervals (24 readings per fuel type per station = **144 total**) with:
- Realistic consumption patterns (higher during daytime)
- ~5% chance of consumption spikes (triggers `HIGH_CONSUMPTION` alerts)
- ~8% chance of price deviations (triggers `PRICE_ANOMALY` alerts)
- Depleting stock that may hit low thresholds (triggers `LOW_STOCK` alerts)

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.0 |
| Database | SQLite (file-based, zero config) |
| Validation | Pydantic v2 |
| Server | Uvicorn (ASGI) |
| HTTP Client | httpx (for seed script) |
