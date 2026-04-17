import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Fuel Monitor API"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
    update_frequency_minutes: int = 5
    low_stock_threshold_pct: float = 0.15
    price_anomaly_threshold_pct: float = 0.05

    class Config:
        env_file = ".env"

settings = Settings()
