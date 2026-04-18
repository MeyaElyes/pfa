from datetime import datetime, timezone
from typing import List, Literal, Optional

from fastapi import APIRouter, Query

from backend.schemas import AlertResponse, FuelData, FuelDataResponse

router = APIRouter()


_fuel_records: list[FuelDataResponse] = []
_alerts: list[AlertResponse] = []


def create_record(payload: FuelData) -> FuelDataResponse:
    # Swap this in-memory list for a persisted insert when a database is wired in.
    record = FuelDataResponse(
        id=len(_fuel_records) + 1,
        timestamp=payload.timestamp,
        station_id=payload.station_id,
        company=payload.company,
        fuel_type=payload.fuel_type,
        price_tnd=payload.price_tnd,
        official_price_tnd=payload.official_price_tnd,
        stock_liters=payload.stock_liters,
        capacity_liters=payload.capacity_liters,
        sales_last_5min_liters=payload.sales_last_5min_liters,
    )
    _fuel_records.append(record)
    return record


def _append_alert(station_id: str, fuel_type: str, alert_type: str, severity: str, message: str) -> None:
    _alerts.append(
        AlertResponse(
            timestamp=datetime.now(timezone.utc),
            station_id=station_id,
            fuel_type=fuel_type,
            alert_type=alert_type,
            severity=severity,
            message=message,
        )
    )


def generate_alerts_from_record(record: FuelDataResponse) -> int:
    generated = 0

    if record.capacity_liters > 0:
        stock_pct = record.stock_liters / record.capacity_liters
        if stock_pct < 0.05:
            _append_alert(
                record.station_id,
                record.fuel_type,
                "LOW_STOCK",
                "critical",
                f"CRITICAL: Stock at {stock_pct:.1%} of capacity ({record.stock_liters:.0f}L remaining)",
            )
            generated += 1
        elif stock_pct < 0.15:
            _append_alert(
                record.station_id,
                record.fuel_type,
                "LOW_STOCK",
                "warning",
                f"Stock at {stock_pct:.1%} of capacity ({record.stock_liters:.0f}L remaining)",
            )
            generated += 1

    if record.official_price_tnd > 0:
        deviation_pct = abs(record.price_tnd - record.official_price_tnd) / record.official_price_tnd
        if deviation_pct > 0.10:
            _append_alert(
                record.station_id,
                record.fuel_type,
                "PRICE_ANOMALY",
                "critical",
                f"Price deviation of {deviation_pct:.1%} from official price ({record.price_tnd:.3f} vs {record.official_price_tnd:.3f} TND)",
            )
            generated += 1
        elif deviation_pct > 0.05:
            _append_alert(
                record.station_id,
                record.fuel_type,
                "PRICE_ANOMALY",
                "warning",
                f"Price deviation of {deviation_pct:.1%} from official price ({record.price_tnd:.3f} vs {record.official_price_tnd:.3f} TND)",
            )
            generated += 1

    if record.sales_last_5min_liters > 200:
        _append_alert(
            record.station_id,
            record.fuel_type,
            "HIGH_CONSUMPTION",
            "warning",
            f"Unusually high sales: {record.sales_last_5min_liters:.0f}L in last 5 minutes",
        )
        generated += 1

    if record.stock_liters == 0:
        _append_alert(
            record.station_id,
            record.fuel_type,
            "STATION_CRITICAL",
            "critical",
            f"Station is OUT OF STOCK for {record.fuel_type}",
        )
        generated += 1

    return generated


@router.get("/current", response_model=List[FuelDataResponse])
def get_current(station_id: str = Query(...)):
    latest_by_fuel: dict[str, FuelDataResponse] = {}
    for record in _fuel_records:
        if record.station_id != station_id:
            continue
        latest_by_fuel[record.fuel_type] = record
    return list(latest_by_fuel.values())


@router.get("/history", response_model=List[FuelDataResponse])
def get_history(
    station_id: str = Query(...),
    fuel_type: Optional[Literal["Gasoil50", "SansPlomb"]] = Query(None),
    limit: int = Query(500, le=2000),
):
    results = [
        record
        for record in _fuel_records
        if record.station_id == station_id and (fuel_type is None or record.fuel_type == fuel_type)
    ]
    return results[-limit:]


@router.get("/alerts", response_model=List[AlertResponse])
def get_alerts(
    station_id: Optional[str] = Query(None),
    severity: Optional[Literal["warning", "critical"]] = Query(None),
    alert_type: Optional[Literal["LOW_STOCK", "PRICE_ANOMALY", "HIGH_CONSUMPTION", "STATION_CRITICAL"]] = Query(None),
    limit: int = Query(50, le=500),
):
    results = _alerts
    if station_id:
        results = [alert for alert in results if alert.station_id == station_id]
    if severity:
        results = [alert for alert in results if alert.severity == severity]
    if alert_type:
        results = [alert for alert in results if alert.alert_type == alert_type]
    return results[-limit:][::-1]
