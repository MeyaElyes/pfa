import time
import httpx
import random
from datetime import datetime, UTC

API_URL = "http://localhost:8000"

# -- Mock Data based on PFA spec --
STATION = {
    "station_id": "BI00001",
    "company": "AGIL",
    "location": "Tunis"
}

FUEL_TYPES = ["Gasoil50", "SansPlomb"]
OFFICIAL_PRICES = {"Gasoil50": 2.25, "SansPlomb": 2.50}
CAPACITIES = {"Gasoil50": 10000, "SansPlomb": 10000}

# Global state for stock tracking
stock_levels = {
    "Gasoil50": 4200.0,
    "SansPlomb": 5000.0
}

def generate_reading(fuel_type):
    official_price = OFFICIAL_PRICES[fuel_type]
    capacity = CAPACITIES[fuel_type]
    
    # Simulate consumption
    sales = random.uniform(20, 150)
    stock_levels[fuel_type] = max(0, stock_levels[fuel_type] - sales)
    
    # Occasionally trigger refuel
    if stock_levels[fuel_type] < 1000:
        stock_levels[fuel_type] += 8000
    
    # Randomly introduce price anomalies as per spec requirements (Price KPIs)
    price = official_price
    if random.random() < 0.1:  # 10% chance
        price += random.uniform(0.1, 0.4) # Deviation
        
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "station_id": STATION["station_id"],
        "company": STATION["company"],
        "fuel_type": fuel_type,
        "price_tnd": round(price, 3),
        "official_price_tnd": official_price,
        "stock_liters": round(stock_levels[fuel_type], 1),
        "capacity_liters": capacity,
        "sales_last_5min_liters": round(sales, 1)
    }

def main():
    print(f"🚀 Mock Generator for {STATION['company']} ({STATION['station_id']}) started.")
    print(f"📡 Sending data to {API_URL}/ingest every 5 minutes...")
    
    while True:
        records = []
        for ftype in FUEL_TYPES:
            reading = generate_reading(ftype)
            records.append(reading)
            
        try:
            # Pushing to Batch endpoint for efficiency
            with httpx.Client() as client:
                resp = client.post(f"{API_URL}/ingest/batch", json={"records": records})
                if resp.status_code == 201:
                    print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Ingested data for {FUEL_TYPES}")
                else:
                    print(f"❌ Error {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"🚨 Connection error: {e}")
            
        # Per spec: Update frequency is fixed (5 min)
        time.sleep(300)

if __name__ == "__main__":
    main()
