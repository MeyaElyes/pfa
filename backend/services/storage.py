from sqlalchemy.orm import Session
from backend.database import models

# --- WRITE METHODS ---

def store_fuel_data(db: Session, data):
    new_record = models.FuelData(**data.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def create_alert(db: Session, station_id: str, fuel_type: str, alert_type: str, severity: str, message: str):
    new_alert = models.Alert(
        station_id=station_id,
        fuel_type=fuel_type,
        alert_type=alert_type,
        severity=severity,
        message=message
    )
    db.add(new_alert)
    db.commit()
    return new_alert

# --- READ METHODS ---

def get_fuel_history(db: Session, station_id: str, fuel_type: str, limit: int = 100):
    return db.query(models.FuelData)\
             .filter(models.FuelData.station_id == station_id)\
             .filter(models.FuelData.fuel_type == fuel_type)\
             .order_by(models.FuelData.timestamp.desc())\
             .limit(limit).all()

def get_all_alerts(db: Session, station_id: str = None):
    query = db.query(models.Alert)
    if station_id:
        query = query.filter(models.Alert.station_id == station_id)
    return query.order_by(models.Alert.timestamp.desc()).all()