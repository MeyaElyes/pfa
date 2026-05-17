#I USED THIS TO FILL THE DATABASE YOU CAN REMOVE IT IF U HAVE INITATED DATABASE  


from backend.database.database import SessionLocal, engine
from backend.database import models
from datetime import datetime, timezone
import random


def seed_stations():
    db = SessionLocal()
    stations = [
        {"station_id": "BI00001", "company": "AGIL", "location": "Tunis Centre"},
        {"station_id": "BI00002", "company": "AGIL", "location": "Tunis Nord"},
        {"station_id": "BI00003", "company": "AGIL", "location": "Sousse"},
    ]

    try:
        models.Base.metadata.create_all(bind=engine)

        # Seed stations
        for station in stations:
            exists = db.query(models.Station).filter_by(station_id=station["station_id"]).first()
            if not exists:
                db.add(models.Station(**station))
        db.commit()
        
        # Seed sample fuel data for each station
        fuel_types = ["Gasoil50", "SansPlomb"]
        now = datetime.now(timezone.utc)
        
        for station in stations:
            for fuel_type in fuel_types:
                # Check if data already exists for this station/fuel combo
                existing = db.query(models.FuelData).filter_by(
                    station_id=station["station_id"],
                    fuel_type=fuel_type
                ).first()
                
                if not existing:
                    fuel_data = models.FuelData(
                        station_id=station["station_id"],
                        fuel_type=fuel_type,
                        stock_liters=random.uniform(5000, 15000),
                        capacity_liters=20000,
                        price_tnd=round(random.uniform(1.60, 1.80), 3),
                        official_price_tnd=1.700,
                        sales_last_5min_liters=random.uniform(10, 50),
                        timestamp=now
                    )
                    db.add(fuel_data)
        
        db.commit()
        print("Stations and sample fuel data seeded.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_stations()