"""
Seed the Fuel Monitor database with realistic Tunisian fuel station data.

Run this script AFTER the server is started:
    python seed_data.py

It will POST mock data to http://localhost:8000/ingest/batch
simulating 3 stations over the last 2 hours of readings.
"""

import httpx
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000"

# -- Tunisian fuel station definitions --
STATIONS = [
    {"station_id": "AGIL-TUN-001", "company": "AGIL", "governorate": "Tunis"},
    {"station_id": "SHELL-SFX-002", "company": "Shell", "governorate": "Sfax"},
    {"station_id": "TOTAL-SOU-003", "company": "TotalEnergies", "governorate": "Sousse"},
]

FUEL_TYPES = ["Gasoil50", "SansPlomb"]

# Official prices (TND/L) -- approximate 2025/2026 values
OFFICIAL_PRICES = {
    "Gasoil50": 2.085,
    "SansPlomb": 2.375,
}

CAPACITIES = {
    "Gasoil50": 30000,  # 30,000 L tank
    "SansPlomb": 20000, # 20,000 L tank
}


def generate_readings(station: dict, hours: int = 2, interval_min: int = 5):
    """Generate time-series readings for one station."""
    records = []
    now = datetime.utcnow()
    start = now - timedelta(hours=hours)
    steps = (hours * 60) // interval_min

    for fuel_type in FUEL_TYPES:
        capacity = CAPACITIES[fuel_type]
        official_price = OFFICIAL_PRICES[fuel_type]
        stock = capacity * random.uniform(0.6, 0.95)  # start 60-95% full

        for i in range(steps):
            ts = start + timedelta(minutes=i * interval_min)

            # Simulate consumption -- busier during "daytime" hours
            hour_of_day = (ts.hour + 1) % 24  # Tunis is UTC+1
            if 7 <= hour_of_day <= 20:
                sales = random.uniform(15, 80)  # normal daytime
            else:
                sales = random.uniform(2, 20)   # quiet at night

            # Occasionally spike consumption
            if random.random() < 0.05:
                sales = random.uniform(200, 350)  # unusual spike

            stock = max(0, stock - sales)

            # Price: usually matches official, but occasionally deviates
            price = official_price
            if random.random() < 0.08:
                # 8% chance of a price anomaly
                price = official_price * random.uniform(1.06, 1.15)

            records.append({
                "timestamp": ts.isoformat(),
                "station_id": station["station_id"],
                "company": station["company"],
                "fuel_type": fuel_type,
                "price_tnd": round(price, 3),
                "official_price_tnd": official_price,
                "stock_liters": round(stock, 1),
                "capacity_liters": capacity,
                "sales_last_5min_liters": round(sales, 1),
            })

    return records


def main():
    print("[SEED] Fuel Monitor -- Seeding database with mock data...\n")

    all_records = []
    for station in STATIONS:
        readings = generate_readings(station, hours=2, interval_min=5)
        all_records.extend(readings)
        print(f"  [+] {station['station_id']} ({station['company']}) -> {len(readings)} readings")

    print(f"\n  [BATCH] Total records to ingest: {len(all_records)}")

    # Send in batch
    with httpx.Client(timeout=30) as client:
        resp = client.post(f"{API_URL}/ingest/batch", json={"records": all_records})
        resp.raise_for_status()
        result = resp.json()

    print(f"  [OK] Ingested: {result['ingested']} records")
    print(f"  [ALERT] Alerts generated: {result['alerts_generated']}")

    # Show dashboard stats
    print("\n-- Dashboard Stats ------------------------------------")
    with httpx.Client() as client:
        stats = client.get(f"{API_URL}/analytics/dashboard").json()
        for k, v in stats.items():
            print(f"  {k}: {v}")

    # Show alerts
    print("\n-- Recent Alerts --------------------------------------")
    with httpx.Client() as client:
        alerts = client.get(f"{API_URL}/alerts", params={"limit": 10}).json()
        if alerts:
            for a in alerts:
                icon = "[!!]" if a["severity"] == "critical" else "[!]"
                print(f"  {icon} [{a['alert_type']}] {a['station_id']}/{a['fuel_type']}: {a['message']}")
        else:
            print("  No alerts generated.")

    # Show station summary for first station
    print("\n-- Station Summary (AGIL-TUN-001) ---------------------")
    with httpx.Client() as client:
        summaries = client.get(f"{API_URL}/analytics/station-summary",
                               params={"station_id": "AGIL-TUN-001"}).json()
        for s in summaries:
            print(f"  [{s['fuel_type']}]")
            print(f"     Price: {s['latest_price_tnd']} TND (deviation: {s['price_deviation_pct']}%)")
            print(f"     Stock: {s['stock_pct']}% ({s['stock_liters']}L / {s['capacity_liters']}L)")
            print(f"     Consumption: {s['consumption_rate_lph']} L/hour")
            if s['hours_until_empty'] is not None:
                print(f"     Hours until empty: {s['hours_until_empty']}")
            print(f"     Active alerts: {s['alert_count']}")

    print("\n[DONE] Seed complete! Open http://localhost:8000/docs to explore the API.")


if __name__ == "__main__":
    main()
