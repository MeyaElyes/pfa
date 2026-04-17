from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional, List


# ── Fuel Data ──────────────────────────────────────────────

class FuelDataCreate(BaseModel):
    timestamp: datetime
    station_id: str
    company: str
    fuel_type: Literal["Gasoil50", "SansPlomb"]
    price_tnd: float = Field(..., gt=0)
    official_price_tnd: float = Field(..., gt=0)
    stock_liters: float = Field(..., ge=0)
    capacity_liters: float = Field(..., gt=0)
    sales_last_5min_liters: float = Field(..., ge=0)


class FuelDataResponse(FuelDataCreate):
    id: int

    class Config:
        from_attributes = True


class BatchIngestRequest(BaseModel):
    """Accept multiple fuel readings at once."""
    records: List[FuelDataCreate]


class BatchIngestResponse(BaseModel):
    ingested: int
    alerts_generated: int


# ── Alerts ─────────────────────────────────────────────────

class AlertResponse(BaseModel):
    id: int
    timestamp: datetime
    station_id: str
    fuel_type: str
    alert_type: str
    severity: str
    message: str
    resolved: bool

    class Config:
        from_attributes = True


# ── Station ────────────────────────────────────────────────

class StationCreate(BaseModel):
    station_id: str
    name: str
    company: str
    governorate: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class StationResponse(StationCreate):
    id: int

    class Config:
        from_attributes = True


# ── Analytics ──────────────────────────────────────────────

class StationSummary(BaseModel):
    station_id: str
    company: str
    fuel_type: str
    latest_price_tnd: float
    official_price_tnd: float
    price_deviation_pct: float
    stock_pct: float
    stock_liters: float
    capacity_liters: float
    consumption_rate_lph: float  # liters per hour (estimated)
    hours_until_empty: Optional[float]
    alert_count: int


class SystemStats(BaseModel):
    total_records: int
    total_alerts: int
    total_stations: int
    active_alerts: int
    avg_stock_pct: float
    latest_update: Optional[datetime]
