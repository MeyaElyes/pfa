from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from database import Base


class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    station_id = Column(String, index=True)
    company = Column(String)
    fuel_type = Column(String)
    price_tnd = Column(Float)
    official_price_tnd = Column(Float)
    stock_liters = Column(Float)
    capacity_liters = Column(Float)
    sales_last_5min_liters = Column(Float)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    station_id = Column(String, index=True)
    fuel_type = Column(String)
    alert_type = Column(String)  # LOW_STOCK, PRICE_ANOMALY, HIGH_CONSUMPTION, STATION_CRITICAL
    severity = Column(String, default="warning")  # info, warning, critical
    message = Column(String)
    resolved = Column(Boolean, default=False)


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, unique=True, index=True)
    name = Column(String)
    company = Column(String)
    governorate = Column(String)  # Tunisian governorate
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
