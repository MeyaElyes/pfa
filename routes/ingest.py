from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import FuelDataCreate, FuelDataResponse, BatchIngestRequest, BatchIngestResponse
from services import storage

router = APIRouter()


@router.post("/", response_model=FuelDataResponse, status_code=201)
def ingest_fuel_data(payload: FuelDataCreate, db: Session = Depends(get_db)):
    """Receives and stores a single fuel data reading."""
    try:
        record = storage.save_fuel_data(db, payload)
        storage.run_alert_checks(db, payload)
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchIngestResponse, status_code=201)
def ingest_batch(payload: BatchIngestRequest, db: Session = Depends(get_db)):
    """Receives and stores multiple fuel data readings at once."""
    try:
        records = storage.save_fuel_data_batch(db, payload.records)
        alert_count = 0
        for data in payload.records:
            alert_count += storage.run_alert_checks(db, data)
        return BatchIngestResponse(ingested=len(records), alerts_generated=alert_count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
