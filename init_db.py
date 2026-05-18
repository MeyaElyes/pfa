# init_db.py
from backend.database.database import engine, Base
from backend.database.models import Station, FuelData, Alert, IncidentLog

print("Dropping existing tables...")
Base.metadata.drop_all(bind=engine)
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done! Check for 'sql_app.db' in your folder.")
