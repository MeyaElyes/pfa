import requests
import time
import random
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000"
STATION_ID = "BI00001"
ANOMALY_FREQUENCY = 0.01
class StationAgent:
    def __init__(self):
        self.tanks = {
            "Gasoil50": {"stock": 8000.0, "capacity": 10000.0, "price": 2.550},
            "SansPlomb": {"stock": 6000.0, "capacity": 12000.0, "price": 2.300}
        }

    def simulate_step(self):
        """Simulates 5 minutes of activity."""
        # Determine the 'hour' to simulate traffic patterns
        hour = datetime.now(timezone.utc).hour
        traffic_multiplier = 2.0 if (7 <= hour <= 9 or 17 <= hour <= 19) else 0.5
        
        for fuel_type, data in self.tanks.items():
            # 1. Random Sales (Influenced by time of day & random spikes)
            # 5% chance for a massive fleet to refuel, triggering HIGH_CONSUMPTION alert
            if random.random() < ANOMALY_FREQUENCY:
                sales = random.uniform(210, 250)
            else:
                sales = random.uniform(5, 30) * traffic_multiplier
            
            # 2. Update internal stock
            data["stock"] = max(0, data["stock"] - sales)
            
            # 3. Simulate a random price change (Anomalies)
            # 10% chance the station manager raises the price drastically to trigger PRICE_ANOMALY alert
            current_price = data["price"]
            if random.random() < 0.1:
                current_price += 0.300 

            # 4. Prepare Payload with the required ISO 8601 timestamp
            payload = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "station_id": STATION_ID,
                "fuel_type": fuel_type,
                "price_tnd": round(current_price, 3),
                "official_price_tnd": data["price"], # Keep official price stable
                "stock_liters": round(data["stock"], 2),
                "capacity_liters": data["capacity"],
                "sales_last_5min_liters": round(sales, 2)
            }

            try:
                # Ensure the endpoint matches your FastAPI routing exactly
                response = requests.post(f"{BASE_URL}/ingest", json=payload)
                if response.status_code in [200, 201]:
                    print(f"[{fuel_type}] Sent: {sales:.1f}L sold. Stock: {data['stock']:.1f}L | Price: {current_price:.3f} TND")
                else:
                    print(f"❌ Error: {response.text}")
            except Exception as e:
                print(f"Connection failed: {e}")

    def run(self, interval=5):
        print(f"Station Agent {STATION_ID} is now online...")
        while True:
            self.simulate_step()
            time.sleep(interval)

if __name__ == "__main__":
    agent = StationAgent()
    agent.run()