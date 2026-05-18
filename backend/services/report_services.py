import os
from groq import Groq
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.models import FuelData, Alert
from .prophet_service import get_prophet_prediction
from dotenv import load_dotenv

load_dotenv()


def generate_report(db: Session, station_id: str, fuel_type: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # 1. Current stock for the requested fuel_type
    current_records = db.query(FuelData).filter(
        FuelData.station_id == station_id,
        FuelData.fuel_type == fuel_type
    ).order_by(FuelData.timestamp.desc()).limit(1).all()

    if current_records:
        r = current_records[0]
        stock_summary = f"- {r.fuel_type}: {r.stock_liters:.0f}L / {r.capacity_liters:.0f}L ({r.stock_liters/r.capacity_liters*100:.1f}%)"
    else:
        stock_summary = "No current data for requested fuel type."

    # 2. Recent alerts for this station & fuel_type (last 10)
    alerts = db.query(Alert).filter(
        Alert.station_id == station_id,
        Alert.fuel_type == fuel_type
    ).order_by(Alert.timestamp.desc()).limit(10).all()

    alerts_summary = "\n".join([
        f"- [{r.severity.upper()}] {r.alert_type}: {r.message}"
        for r in alerts
    ]) or "No recent alerts."

    # 3. Forecast + narrative for the requested fuel_type
    result = get_prophet_prediction(db, station_id, fuel_type, periods=12)
    if result.get("forecast"):
        forecast_summary = f"**{fuel_type}:** {result.get('narrative')}\n"
    else:
        forecast_summary = f"**{fuel_type}:** Not enough data.\n"

    # 4. Prompt LLM
    prompt = f"""You are a professional fuel station operations analyst.
Generate a concise professional report in markdown for station {station_id} and fuel {fuel_type}.

## Current Stock Levels
{stock_summary}

## Recent Alerts
{alerts_summary}

## Forecast Analysis
{forecast_summary}

Write a structured markdown report with:
- Executive Summary
- Stock Status
- Alert Analysis
- Forecast & Recommendations

Be professional, concise, and actionable."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content