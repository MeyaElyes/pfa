from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from models import FuelLog, Alert
from typing import Optional, List


def get_latest_per_fuel(db: Session, station_id: str) -> List[FuelLog]:
    """Returns the most recent record per fuel type for a given station."""
    subquery = (
        db.query(FuelLog.fuel_type, func.max(FuelLog.timestamp).label("max_ts"))
        .filter(FuelLog.station_id == station_id)
        .group_by(FuelLog.fuel_type)
        .subquery()
    )
    return (
        db.query(FuelLog)
        .join(subquery, (FuelLog.fuel_type == subquery.c.fuel_type) &
                        (FuelLog.timestamp == subquery.c.max_ts))
        .filter(FuelLog.station_id == station_id)
        .all()
    )


def get_history(db: Session, station_id: str, fuel_type: Optional[str] = None,
                limit: int = 500) -> List[FuelLog]:
    q = db.query(FuelLog).filter(FuelLog.station_id == station_id)
    if fuel_type:
        q = q.filter(FuelLog.fuel_type == fuel_type)
    return q.order_by(FuelLog.timestamp.asc()).limit(limit).all()


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
    rows = db.query(distinct(FuelLog.station_id)).all()
    return [r[0] for r in rows]


def get_system_stats(db: Session) -> dict:
    """Compute system-wide statistics."""
    total_records = db.query(func.count(FuelLog.id)).scalar() or 0
    total_alerts = db.query(func.count(Alert.id)).scalar() or 0
    active_alerts = db.query(func.count(Alert.id)).filter(Alert.resolved == False).scalar() or 0
    total_stations = db.query(func.count(distinct(FuelLog.station_id))).scalar() or 0

    # Average stock percentage across latest readings
    avg_stock_pct = 0.0
    if total_records > 0:
        result = db.query(
            func.avg(FuelLog.stock_liters / FuelLog.capacity_liters)
        ).filter(FuelLog.capacity_liters > 0).scalar()
        avg_stock_pct = float(result or 0) * 100

    latest_update = db.query(func.max(FuelLog.timestamp)).scalar()

    return {
        "total_records": total_records,
        "total_alerts": total_alerts,
        "total_stations": total_stations,
        "active_alerts": active_alerts,
        "avg_stock_pct": round(avg_stock_pct, 1),
        "latest_update": latest_update,
    }


def get_station_summary(db: Session, station_id: str) -> list[dict]:
    """Build a per-fuel-type summary for a station."""
    latest = get_latest_per_fuel(db, station_id)
    summaries = []
    for r in latest:
        stock_pct = (r.stock_liters / r.capacity_liters * 100) if r.capacity_liters > 0 else 0
        deviation = abs(r.price_tnd - r.official_price_tnd) / r.official_price_tnd * 100 if r.official_price_tnd > 0 else 0
        consumption_rate_lph = r.sales_last_5min_liters * 12  # 5-min rate → per hour
        hours_left = (r.stock_liters / consumption_rate_lph) if consumption_rate_lph > 0 else None

        alert_count = db.query(func.count(Alert.id)).filter(
            Alert.station_id == station_id,
            Alert.fuel_type == r.fuel_type,
            Alert.resolved == False,
        ).scalar() or 0

        summaries.append({
            "station_id": station_id,
            "company": r.company,
            "fuel_type": r.fuel_type,
            "latest_price_tnd": r.price_tnd,
            "official_price_tnd": r.official_price_tnd,
            "price_deviation_pct": round(deviation, 2),
            "stock_pct": round(stock_pct, 1),
            "stock_liters": r.stock_liters,
            "capacity_liters": r.capacity_liters,
            "consumption_rate_lph": round(consumption_rate_lph, 1),
            "hours_until_empty": round(hours_left, 1) if hours_left is not None else None,
            "alert_count": alert_count,
        })
    return summaries
