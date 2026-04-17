from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from backend.models import FuelData, Alert
from backend.schemas import StationFuelSnapshot, SystemStats, StockKPIs, SalesKPIs, PriceKPIs, OpKPIs
from typing import Optional, List
from datetime import datetime, UTC


def get_latest_per_fuel(db: Session, station_id: str) -> List[FuelData]:
    """Returns the most recent record per fuel type for a given station."""
    subquery = (
        db.query(FuelData.fuel_type, func.max(FuelData.timestamp).label("max_ts"))
        .filter(FuelData.station_id == station_id)
        .group_by(FuelData.fuel_type)
        .subquery()
    )
    return (
        db.query(FuelData)
        .join(subquery, (FuelData.fuel_type == subquery.c.fuel_type) &
                        (FuelData.timestamp == subquery.c.max_ts))
        .filter(FuelData.station_id == station_id)
        .all()
    )


def get_history(db: Session, station_id: str, fuel_type: Optional[str] = None,
                limit: int = 500) -> List[FuelData]:
    q = db.query(FuelData).filter(FuelData.station_id == station_id)
    if fuel_type:
        q = q.filter(FuelData.fuel_type == fuel_type)
    return q.order_by(FuelData.timestamp.asc()).limit(limit).all()


def get_alerts(db: Session, station_id: Optional[str], limit: int,
               severity: Optional[str] = None, alert_type: Optional[str] = None) -> List[Alert]:
    q = db.query(Alert)
    if station_id:
        q = q.filter(Alert.station_id == station_id)
    if severity:
        q = q.filter(Alert.severity == severity)
    if alert_type:
        q = q.filter(Alert.alert_type == alert_type)
    return q.order_by(Alert.timestamp.desc()).limit(limit).all()


def get_all_station_ids(db: Session) -> List[str]:
    """Return all unique station IDs that have submitted data."""
    rows = db.query(distinct(FuelData.station_id)).all()
    return [r[0] for r in rows]


def get_system_stats(db: Session) -> dict:
    """Compute system-wide statistics."""
    total_records = db.query(func.count(FuelData.id)).scalar() or 0
    total_alerts = db.query(func.count(Alert.id)).scalar() or 0
    active_alerts = db.query(func.count(Alert.id)).filter(Alert.resolved == False).scalar() or 0
    total_stations = db.query(func.count(distinct(FuelData.station_id))).scalar() or 0

    # Average stock percentage across latest readings
    avg_stock_pct = 0.0
    if total_records > 0:
        result = db.query(
            func.avg(FuelData.stock_liters / FuelData.capacity_liters)
        ).filter(FuelData.capacity_liters > 0).scalar()
        avg_stock_pct = float(result or 0) * 100

    latest_update = db.query(func.max(FuelData.timestamp)).scalar()

    return {
        "total_records": total_records,
        "total_alerts": total_alerts,
        "total_stations": total_stations,
        "active_alerts": active_alerts,
        "avg_stock_pct": round(avg_stock_pct, 1),
        "latest_update": latest_update,
    }


def get_station_summary(db: Session, station_id: str) -> List[StationFuelSnapshot]:
    """Build a per-fuel-type summary for a station with specific KPIs."""
    latest = get_latest_per_fuel(db, station_id)
    summaries = []
    now = datetime.now(UTC).replace(tzinfo=None)

    for r in latest:
        # Stock KPIs
        stock_utilization_pct = (r.stock_liters / r.capacity_liters * 100) if r.capacity_liters > 0 else 0
        low_stock_flag = 1 if stock_utilization_pct < 15 else 0
        
        # Calculate depletion rate (mocked trend as we only have 1 point here for simplicity, 
        # but logically would fetch previous point)
        consumption_rate_lph = r.sales_last_5min_liters * 12
        
        # Sales KPIs
        estimated_daily_sales = consumption_rate_lph * 24
        
        # Price KPIs
        price_deviation = r.price_tnd - r.official_price_tnd
        price_deviation_pct = (price_deviation / r.official_price_tnd * 100) if r.official_price_tnd > 0 else 0
        price_anomaly_flag = 1 if abs(price_deviation_pct) > 5 else 0
        
        # Operational KPIs
        data_freshness_minutes = (now - r.timestamp).total_seconds() / 60

        summaries.append(StationFuelSnapshot(
            fuel_type=r.fuel_type,
            price_tnd=r.price_tnd,
            stock_liters=r.stock_liters,
            stock_kpis=StockKPIs(
                stock_liters=r.stock_liters,
                stock_utilization_pct=round(stock_utilization_pct, 2),
                stock_depletion_rate_lph=round(consumption_rate_lph, 2),
                low_stock_flag=low_stock_flag
            ),
            sales_kpis=SalesKPIs(
                sales_last_5min_liters=r.sales_last_5min_liters,
                estimated_daily_sales=round(estimated_daily_sales, 2)
            ),
            price_kpis=PriceKPIs(
                price_deviation=round(price_deviation, 3),
                price_deviation_pct=round(price_deviation_pct, 2),
                price_anomaly_flag=price_anomaly_flag
            ),
            op_kpis=OpKPIs(
                data_freshness_minutes=round(data_freshness_minutes, 1)
            )
        ))
    return summaries
