from fastapi import APIRouter, HTTPException

from backend.schemas import FuelData as FuelDataSchema, FuelDataResponse
from backend.routes.data import create_record, generate_alerts_from_record

router = APIRouter()


@router.post("/", response_model=FuelDataResponse, status_code=201)
def ingest_fuel_data(payload: FuelDataSchema):
    try:
        # If a database is added later, this is where the insert/save call would go.
        record = create_record(payload)
        generate_alerts_from_record(record)
        return record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
