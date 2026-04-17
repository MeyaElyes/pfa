from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Station(Base):
    """Static info for fuel stations"""
    __tablename__ = "stations"

    station_id = Column(String, primary_key=True, index=True)
    company = Column(String)
    location = Column(String)  # Merged governorate/lat/lng into a simple location field per spec

    fuel_data_records = relationship("FuelData", back_populates="station")


class FuelData(Base):
    """Core time-series table for fuel readings"""
    __tablename__ = "fuel_data"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    station_id = Column(String, ForeignKey("stations.station_id"), index=True)
    fuel_type = Column(String)
    price_tnd = Column(Float)
    official_price_tnd = Column(Float)
    stock_liters = Column(Float)
    capacity_liters = Column(Float)
    sales_last_5min_liters = Column(Float)

    station = relationship("Station", back_populates="fuel_data_records")


class Alert(Base):
    """Event table for anomalies"""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    station_id = Column(String, index=True)
    fuel_type = Column(String)
    alert_type = Column(String)  # LOW_STOCK, PRICE_ANOMALY, CRITICAL_ALERT
    severity = Column(String, default="warning")
    message = Column(String)
    resolved = Column(Boolean, default=False)
