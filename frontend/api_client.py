import requests

# URL de base de ton backend FastAPI (à adapter si le port est différent)
BASE_URL = "http://localhost:8000"

# Mock data for stations (fallback)
MOCK_STATIONS = [
    {"station_id": "BI00001", "company": "AGIL", "location": "Bizerte, Jarzouna"},
]

def get_stations():
    """Get all available stations."""
    try:
        response = requests.get(f"{BASE_URL}/stations", timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return MOCK_STATIONS

def get_companies():
    """Get all unique companies."""
    try:
        response = requests.get(f"{BASE_URL}/companies", timeout=5)
        response.raise_for_status()
        return response.json()
    except:
        return ["AGIL"]

def get_current_data(station_id="BI00001"):
    """Récupère l'état actuel pour chaque type de carburant."""
    try:
        response = requests.get(f"{BASE_URL}/current", params={"station_id": station_id}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

def get_current_data_multi(station_ids):
    """Get current data for multiple stations.
    station_ids: list of station IDs or comma-separated string
    """
    try:
        if isinstance(station_ids, list):
            station_ids = ",".join(station_ids)
        response = requests.get(f"{BASE_URL}/current-multi", params={"station_ids": station_ids}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

def get_history_data(station_id="BI00001", fuel_type="Gasoil50"):
    """Récupère l'historique pour les graphiques."""
    try:
        response = requests.get(f"{BASE_URL}/history", params={"station_id": station_id, "fuel_type": fuel_type}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

def get_alerts(station_id=None, limit=50):
    """Récupère les dernières alertes générées par le système."""
    try:
        params = {"limit": limit}
        if station_id:
            params["station_id"] = station_id
        response = requests.get(f"{BASE_URL}/alerts", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []
    
def get_predictions(station_id: str, fuel_type: str):
    """Fetch the Prophet forecast from the backend."""
    url = f"{BASE_URL}/predict"
    params = {
        "station_id": station_id,
        "fuel_type": fuel_type,
        "periods": 24  # 2 hours ahead
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching predictions: {e}")
        return []