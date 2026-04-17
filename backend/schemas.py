from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional, List


# ── Fuel Data (Transferred Data FrontEnd-BackEnd-Database) ──

class FuelData(BaseModel):
    timestamp: datetime
    station_id: str
    company: str
    fuel_type: Literal["Gasoil50", "SansPlomb"]
    price_tnd: float = Field(..., gt=0)
    official_price_tnd: float = Field(..., gt=0)
    stock_liters: float = Field(..., ge=0)
    capacity_liters: float = Field(..., gt=0)
    sales_last_5min_liters: float = Field(..., ge=0)


class FuelDataResponse(BaseModel):
    id: int
    timestamp: datetime
    station_id: str
    company: Optional[str] = None
    fuel_type: Literal["Gasoil50", "SansPlomb"]
    price_tnd: float
    official_price_tnd: float
    stock_liters: float
    capacity_liters: float
    sales_last_5min_liters: float

    class Config:
        from_attributes = True


class BatchIngestRequest(BaseModel):
    """Accept multiple fuel readings at once (Extension to spec)."""
    records: List[FuelData]


class BatchIngestResponse(BaseModel):
    ingested: int
    alerts_generated: int


# ── Alerts ─────────────────────────────────────────────────

class AlertResponse(BaseModel):
    timestamp: datetime
    station_id: str
    fuel_type: str
    alert_type: str
    message: str

    class Config:
        from_attributes = True


# ── Station ────────────────────────────────────────────────

class StationCreate(BaseModel):
    station_id: str
    company: str
    location: str


class StationResponse(StationCreate):
    class Config:
        from_attributes = True


class SystemStats(BaseModel):
    total_records: int
    total_alerts: int
    total_stations: int
    active_alerts: int
    avg_stock_pct: float
    latest_update: Optional[datetime]


# ── KPI Analytics schemas ──────────────────────────────────────

class StockKPIs(BaseModel):
    stock_liters: float
    stock_utilization_pct: float
    stock_depletion_rate_lph: Optional[float]  # (stock_now - previous) / time
    low_stock_flag: int  # 1 if < 15%, 0 otherwise


class SalesKPIs(BaseModel):
    sales_last_5min_liters: float
    estimated_daily_sales: float


class PriceKPIs(BaseModel):
    price_deviation: float
    price_deviation_pct: float
    price_anomaly_flag: int


class OpKPIs(BaseModel):
    data_freshness_minutes: float


class StationFuelSnapshot(BaseModel):
    fuel_type: str
    price_tnd: float
    stock_liters: float
    
    # Specific requested KPIs
    stock_kpis: StockKPIs
    sales_kpis: SalesKPIs
    price_kpis: PriceKPIs
    op_kpis: OpKPIs
