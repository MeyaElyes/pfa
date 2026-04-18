from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.services import storage
from backend.schemas import FuelData as FuelDataSchema, FuelDataResponse
# Assuming alert logic is still in data.py or moved to services
from backend.routes.data import generate_alerts_from_record 

router = APIRouter()

@router.post("/", response_model=FuelDataResponse, status_code=201)
def ingest_fuel_data(payload: FuelDataSchema, db: Session = Depends(get_db)):
    try:
        # 1. Save to SQLite via the storage service
        # This replaces the old in-memory 'create_record'
        record = storage.store_fuel_data(db, payload)
        
        # 2. Run the alert logic
        # Note: You might need to update generate_alerts_from_record 
        # to also save alerts to the DB using storage.create_alert
        generate_alerts_from_record(db, record)
        
        return record
    except Exception as e:
        # It's good practice to log 'e' here for debugging
        raise HTTPException(status_code=500, detail=str(e))