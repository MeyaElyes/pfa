from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.schemas import FuelDataResponse, AlertResponse, StationCreate, StationResponse
from backend.models import Station
from backend.services import queries

router = APIRouter()


@router.get("/current", response_model=List[FuelDataResponse])
def get_current(station_id: str = Query(...), db: Session = Depends(get_db)):
    """Returns the latest snapshot per fuel type for a station."""
    return queries.get_latest_per_fuel(db, station_id)


@router.get("/history", response_model=List[FuelDataResponse])
def get_history(
    station_id: str = Query(...),
    fuel_type: Optional[str] = Query(None),
    limit: int = Query(500, le=2000),
    db: Session = Depends(get_db),
):
    """Returns historical time-ordered records for charts."""
    return queries.get_history(db, station_id, fuel_type, limit)


@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    station_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    db: Session = Depends(get_db),
):
    """Returns anomaly alerts detected by the agent, with optional filters."""
    return queries.get_alerts(db, station_id, limit, severity, alert_type)


@router.get("/stations", response_model=List[str])
def list_stations(db: Session = Depends(get_db)):
    """Returns all station IDs that have submitted data."""
    return queries.get_all_station_ids(db)


@router.post("/stations", response_model=StationResponse, status_code=201)
def create_station(payload: StationCreate, db: Session = Depends(get_db)):
    """Create a station manually for testing or onboarding."""
    existing = db.query(Station).filter(Station.station_id == payload.station_id).first()
    if existing:
        return existing

    station = Station(
        station_id=payload.station_id,
        company=payload.company,
        location=payload.location,
    )
    db.add(station)
    db.commit()
    db.refresh(station)
    return station


@router.post("/run-agent")
def run_agent(station_id: str = Query(...), db: Session = Depends(get_db)):
    """Manually triggers agent analysis for testing."""
    from backend.services.storage import run_alert_checks_for_station
    alert_count = run_alert_checks_for_station(db, station_id)
    return {"status": "Agent ran successfully", "station_id": station_id, "alerts_generated": alert_count}
