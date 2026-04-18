import requests

# URL de base de ton backend FastAPI (à adapter si le port est différent)
BASE_URL = "http://localhost:8000"

def get_current_data(station_id="BI00001"):
    """Récupère l'état actuel pour chaque type de carburant[cite: 227]."""
    try:
        response = requests.get(f"{BASE_URL}/current", params={"station_id": station_id})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

def get_history_data(station_id="BI00001", fuel_type="Gasoil50"):
    """Récupère l'historique pour les graphiques[cite: 247]."""
    try:
        response = requests.get(f"{BASE_URL}/history", params={"station_id": station_id, "fuel_type": fuel_type})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []

def get_alerts(station_id="BI00001", limit=10):
    """Récupère les dernières alertes générées par le système[cite: 270]."""
    try:
        response = requests.get(f"{BASE_URL}/alerts", params={"station_id": station_id, "limit": limit})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []