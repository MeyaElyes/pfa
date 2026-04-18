from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# 1. Station Table: Static metadata [cite: 145]
class Station(Base):
    __tablename__ = "stations"
    
    station_id = Column(String, primary_key=True, index=True) # e.g., "BI00001" [cite: 6, 146]
    company = Column(String) # e.g., "AGIL" [cite: 7, 147]
    location = Column(String) # [cite: 148]
    
    # Relationship: One station has many fuel updates
    fuel_records = relationship("FuelData", back_populates="station")

# 2. FuelData Table: Core time-series records [cite: 152]
class FuelData(Base):
    __tablename__ = "fuel_data"
    
    id = Column(Integer, primary_key=True, index=True) 
    timestamp = Column(DateTime) 
    station_id = Column(String, ForeignKey("stations.station_id")) 
    fuel_type = Column(String) # "Gasoil50" or "SansPlomb" [cite: 8, 25, 157]
    
    # Financials and Inventory [cite: 158-162]
    price_tnd = Column(Float)
    official_price_tnd = Column(Float)
    stock_liters = Column(Float)
    capacity_liters = Column(Float)
    sales_last_5min_liters = Column(Float)
    
    station = relationship("Station", back_populates="fuel_records")

# 3. Alert Table: System decisions/problems [cite: 168]
class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True) 
    timestamp = Column(DateTime) 
    station_id = Column(String, ForeignKey("stations.station_id")) 
    fuel_type = Column(String) 
    alert_type = Column(String) # e.g., "LOW_STOCK" [cite: 175, 254]
    message = Column(String) 