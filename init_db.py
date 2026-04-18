# init_db.py
from backend.database import engine, Base
from backend.models import Station, FuelData, Alert

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done! Check for 'sql_app.db' in your folder.")