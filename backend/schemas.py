from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class FuelData(BaseModel):
    timestamp: datetime
    station_id: str = Field(..., min_length=1)
    fuel_type: Literal["Gasoil50", "SansPlomb"]
    price_tnd: float = Field(..., gt=0)
    official_price_tnd: float = Field(..., gt=0)
    stock_liters: float = Field(..., ge=0)
    capacity_liters: float = Field(..., gt=0)
    sales_last_5min_liters: float = Field(..., ge=0)


class FuelDataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    station_id: str
    fuel_type: Literal["Gasoil50", "SansPlomb"]
    price_tnd: float
    official_price_tnd: float
    stock_liters: float
    capacity_liters: float
    sales_last_5min_liters: float


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int                          # added — needed for PATCH endpoint
    timestamp: datetime
    station_id: str
    fuel_type: str
    alert_type: str
    severity: str
    message: str

    # --- Step 1: New fields ---
    status: str                      # new / acknowledged / resolved
    handled_by: Optional[str]        # "agent" or "operator"
    handled_at: Optional[datetime]   # when it was handled
    fingerprint: Optional[str]       # deduplication hash


class AlertUpdate(BaseModel):
    """Used by the PATCH /alerts/{id} endpoint (Step 3)."""
    status: Literal["new", "acknowledged", "resolved"]
    handled_by: Optional[str] = "operator"