from sqlalchemy.orm import Session
from backend.models import FuelData, Alert, Station
from backend.schemas import FuelData as FuelDataSchema
from datetime import datetime


def _ensure_station_exists(db: Session, data: FuelDataSchema) -> None:
    existing = db.query(Station).filter(Station.station_id == data.station_id).first()
    if existing:
        return

    station = Station(
        station_id=data.station_id,
        company=data.company,
        location="Unknown",
    )
    db.add(station)
    db.flush()


def save_fuel_data(db: Session, data: FuelDataSchema) -> FuelData:
    _ensure_station_exists(db, data)
    record = FuelData(
        timestamp=data.timestamp,
        station_id=data.station_id,
        fuel_type=data.fuel_type,
        price_tnd=data.price_tnd,
        official_price_tnd=data.official_price_tnd,
        stock_liters=data.stock_liters,
        capacity_liters=data.capacity_liters,
        sales_last_5min_liters=data.sales_last_5min_liters,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def save_fuel_data_batch(db: Session, records: list[FuelDataSchema]) -> list[FuelData]:
    """Save multiple fuel records in a single transaction."""
    db_records = []
    for data in records:
        _ensure_station_exists(db, data)
        record = FuelData(
            timestamp=data.timestamp,
            station_id=data.station_id,
            fuel_type=data.fuel_type,
            price_tnd=data.price_tnd,
            official_price_tnd=data.official_price_tnd,
            stock_liters=data.stock_liters,
            capacity_liters=data.capacity_liters,
            sales_last_5min_liters=data.sales_last_5min_liters,
        )
        db.add(record)
        db_records.append(record)
    db.commit()
    for r in db_records:
        db.refresh(r)
    return db_records


def run_alert_checks(db: Session, data: FuelDataSchema) -> int:
    """Run all alert checks and return the number of alerts generated."""
    alerts = []

    # ── 1. Low stock alert: stock < 15% of capacity ──
    if data.capacity_liters > 0:
        stock_pct = data.stock_liters / data.capacity_liters
        if stock_pct < 0.05:
            alerts.append(Alert(
                timestamp=datetime.utcnow(),
                station_id=data.station_id,
                fuel_type=data.fuel_type,
                alert_type="LOW_STOCK",
                severity="critical",
                message=f"CRITICAL: Stock at {stock_pct:.1%} of capacity ({data.stock_liters:.0f}L remaining)",
            ))
        elif stock_pct < 0.15:
            alerts.append(Alert(
                timestamp=datetime.utcnow(),
                station_id=data.station_id,
                fuel_type=data.fuel_type,
                alert_type="LOW_STOCK",
                severity="warning",
                message=f"Stock at {stock_pct:.1%} of capacity ({data.stock_liters:.0f}L remaining)",
            ))

    # ── 2. Price anomaly: deviation > 5% from official price ──
    if data.official_price_tnd > 0:
        deviation_pct = abs(data.price_tnd - data.official_price_tnd) / data.official_price_tnd
        if deviation_pct > 0.10:
            alerts.append(Alert(
                timestamp=datetime.utcnow(),
                station_id=data.station_id,
                fuel_type=data.fuel_type,
                alert_type="PRICE_ANOMALY",
                severity="critical",
                message=f"Price deviation of {deviation_pct:.1%} from official price "
                        f"({data.price_tnd:.3f} vs {data.official_price_tnd:.3f} TND)",
            ))
        elif deviation_pct > 0.05:
            alerts.append(Alert(
                timestamp=datetime.utcnow(),
                station_id=data.station_id,
                fuel_type=data.fuel_type,
                alert_type="PRICE_ANOMALY",
                severity="warning",
                message=f"Price deviation of {deviation_pct:.1%} from official price "
                        f"({data.price_tnd:.3f} vs {data.official_price_tnd:.3f} TND)",
            ))

    # ── 3. High consumption: selling > 200L in 5 minutes ──
    if data.sales_last_5min_liters > 200:
        alerts.append(Alert(
            timestamp=datetime.utcnow(),
            station_id=data.station_id,
            fuel_type=data.fuel_type,
            alert_type="HIGH_CONSUMPTION",
            severity="warning",
            message=f"Unusually high sales: {data.sales_last_5min_liters:.0f}L in last 5 minutes",
        ))

    # ── 4. Station critical: stock is literally zero ──
    if data.stock_liters == 0:
        alerts.append(Alert(
            timestamp=datetime.utcnow(),
            station_id=data.station_id,
            fuel_type=data.fuel_type,
            alert_type="STATION_CRITICAL",
            severity="critical",
            message=f"Station is OUT OF STOCK for {data.fuel_type}",
        ))

    for alert in alerts:
        db.add(alert)
    if alerts:
        db.commit()
    return len(alerts)


def run_alert_checks_for_station(db: Session, station_id: str) -> int:
    from backend.services.queries import get_latest_per_fuel
    total = 0
    records = get_latest_per_fuel(db, station_id)
    for r in records:
        data = FuelDataSchema.model_validate(r.__dict__)
        total += run_alert_checks(db, data)
    return total
