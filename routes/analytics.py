from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import StationSummary, SystemStats
from services import queries

router = APIRouter()


@router.get("/dashboard", response_model=SystemStats)
def system_dashboard(db: Session = Depends(get_db)):
    """Returns system-wide statistics for a monitoring dashboard."""
    return queries.get_system_stats(db)


@router.get("/station-summary", response_model=List[StationSummary])
def station_summary(station_id: str = Query(...), db: Session = Depends(get_db)):
    """Returns a rich analytical summary for a station, per fuel type.
    Includes consumption rate, hours until empty, and active alert count."""
    return queries.get_station_summary(db, station_id)
