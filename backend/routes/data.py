from datetime import datetime, timezone
from typing import List, Literal, Optional
import hashlib

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.schemas import AlertResponse, AlertUpdate, FuelData, FuelDataResponse
from backend.services import storage
from backend.database import models
from backend.database.database import get_db

router = APIRouter()


def create_record(db: Session, payload: FuelData) -> FuelDataResponse:
    db_record = models.FuelData(**payload.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record


def _make_fingerprint(station_id: str, fuel_type: str, alert_type: str) -> str:
    """Generate a unique hash to identify a specific alert condition."""
    raw = f"{station_id}:{fuel_type}:{alert_type}"
    return hashlib.md5(raw.encode()).hexdigest()


def _append_alert(db: Session, station_id: str, fuel_type: str, alert_type: str, severity: str, message: str) -> None:
    """
    Saves a new alert to the DB, skipping if an identical unresolved alert already exists (deduplication).
    """
    fingerprint = _make_fingerprint(station_id, fuel_type, alert_type)

    # Step 2: Deduplication — skip if same condition is already active
    existing = db.query(models.Alert).filter(
        models.Alert.fingerprint == fingerprint,
        models.Alert.status != "resolved"
    ).first()

    if existing:
        return  # Already tracking this condition, don't create a duplicate

    storage.create_alert(
        db=db,
        station_id=station_id,
        fuel_type=fuel_type,
        alert_type=alert_type,
        severity=severity,
        message=f"[{severity.upper()}] {message}",
        fingerprint=fingerprint,
        status="new"
    )


def generate_alerts_from_record(db: Session, record: FuelDataResponse) -> int:
    generated = 0

    if record.capacity_liters > 0:
        stock_pct = record.stock_liters / record.capacity_liters
        if stock_pct < 0.05:
            _append_alert(db, record.station_id, record.fuel_type, "LOW_STOCK", "critical",
                f"CRITICAL: Stock at {stock_pct:.1%} of capacity ({record.stock_liters:.0f}L remaining)")
            generated += 1
        elif stock_pct < 0.15:
            _append_alert(db, record.station_id, record.fuel_type, "LOW_STOCK", "warning",
                f"Stock at {stock_pct:.1%} of capacity ({record.stock_liters:.0f}L remaining)")
            generated += 1

    if record.official_price_tnd > 0:
        deviation_pct = abs(record.price_tnd - record.official_price_tnd) / record.official_price_tnd
        if deviation_pct > 0.10:
            _append_alert(db, record.station_id, record.fuel_type, "PRICE_ANOMALY", "critical",
                f"Price deviation of {deviation_pct:.1%} from official price ({record.price_tnd:.3f} vs {record.official_price_tnd:.3f} TND)")
            generated += 1
        elif deviation_pct > 0.05:
            _append_alert(db, record.station_id, record.fuel_type, "PRICE_ANOMALY", "warning",
                f"Price deviation of {deviation_pct:.1%} from official price ({record.price_tnd:.3f} vs {record.official_price_tnd:.3f} TND)")
            generated += 1

    if record.sales_last_5min_liters > 200:
        _append_alert(db, record.station_id, record.fuel_type, "HIGH_CONSUMPTION", "warning",
            f"Unusually high sales: {record.sales_last_5min_liters:.0f}L in last 5 minutes")
        generated += 1

    if record.stock_liters == 0:
        _append_alert(db, record.station_id, record.fuel_type, "STATION_CRITICAL", "critical",
            f"Station is OUT OF STOCK for {record.fuel_type}")
        generated += 1

    return generated


location_map = {
    "BI00001": "Tunis Centre",
    "BI00002": "Tunis Nord",
    "BI00003": "Sousse"
}


@router.get("/stations")
def get_stations(db: Session = Depends(get_db)):
    """Get all stations from the Station table."""
    stations = db.query(models.Station).all()
    return [
        {
            "station_id": s.station_id,
            "company": s.company,
            "location": s.location
        }
        for s in stations
    ]


@router.get("/companies")
def get_companies(db: Session = Depends(get_db)):
    """Get all unique companies from the Station table."""
    companies = db.query(models.Station.company).distinct().all()
    return [c[0] for c in companies]


@router.get("/current", response_model=List[FuelDataResponse])
def get_current(station_id: str = Query(...), db: Session = Depends(get_db)):
    subquery = db.query(
        models.FuelData.fuel_type,
        func.max(models.FuelData.timestamp).label('max_ts')
    ).filter(models.FuelData.station_id == station_id).group_by(models.FuelData.fuel_type).subquery()

    results = db.query(models.FuelData).join(
        subquery,
        (models.FuelData.fuel_type == subquery.c.fuel_type) &
        (models.FuelData.timestamp == subquery.c.max_ts)
    ).filter(models.FuelData.station_id == station_id).all()

    return results


@router.get("/history", response_model=List[FuelDataResponse])
def get_history(
    station_id: str = Query(...),
    fuel_type: Optional[Literal["Gasoil50", "SansPlomb"]] = Query(None),
    limit: int = Query(500, le=2000),
    db: Session = Depends(get_db),
):
    query = db.query(models.FuelData).filter(models.FuelData.station_id == station_id)
    if fuel_type:
        query = query.filter(models.FuelData.fuel_type == fuel_type)
    results = query.order_by(models.FuelData.timestamp.desc()).limit(limit).all()
    return results[::-1]


@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    station_id: Optional[str] = Query(None),
    severity: Optional[Literal["warning", "critical"]] = Query(None),
    alert_type: Optional[Literal["LOW_STOCK", "PRICE_ANOMALY", "HIGH_CONSUMPTION", "STATION_CRITICAL"]] = Query(None),
    status: Optional[Literal["new", "acknowledged", "resolved"]] = Query(None),
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(models.Alert)
    if station_id:
        query = query.filter(models.Alert.station_id == station_id)
    if severity:
        query = query.filter(models.Alert.severity == severity)
    if alert_type:
        query = query.filter(models.Alert.alert_type == alert_type)
    if status:
        query = query.filter(models.Alert.status == status)
    results = query.order_by(models.Alert.timestamp.desc()).limit(limit).all()
    return results


# Step 3: PATCH endpoint for operators to acknowledge or resolve alerts
@router.patch("/alerts/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    payload: AlertUpdate,
    db: Session = Depends(get_db),
):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = payload.status
    alert.handled_by = payload.handled_by or "operator"
    alert.handled_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert


# Step 7: Trigger endpoint for Student 4 (orchestration agent handoff)
@router.post("/agent/trigger")
def trigger_agent(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(models.Alert).filter(models.Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    # Watcher/responder will pick this up — placeholder for now
    return {"status": "triggered", "alert_id": alert_id}