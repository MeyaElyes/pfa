import pandas as pd
from prophet import Prophet
from sqlalchemy.orm import Session
from ..database.models import FuelData # Ensure this import matches your structure

# def get_prophet_prediction(db: Session, station_id: str, fuel_type: str, periods: int = 1):
#     """
#     Directly queries SQLite via SQLAlchemy, trains Prophet, and predicts future stock.
#     periods=24 at 5-min intervals = 2 hours into the future.
#     """
#     # 1. Direct SQLAlchemy Query (Fastest method)
#     query = db.query(FuelData.timestamp, FuelData.stock_liters)\
#               .filter(FuelData.station_id == station_id)\
#               .filter(FuelData.fuel_type == fuel_type)
    
#     # Load directly into Pandas
#     df = pd.read_sql(query.statement, db.bind)
    
#     # Handle empty/insufficient data gracefully
#     if len(df) < 0:
#         return []

#     # 2. Format for Prophet
#     df.rename(columns={'timestamp': 'ds', 'stock_liters': 'y'}, inplace=True)
#     df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None) # Strip timezones for Prophet
    
#     # 3. Train the Model
#     model = Prophet(daily_seasonality=True, yearly_seasonality=False)
#     model.fit(df)
    
#     # 4. Predict
#     future = model.make_future_dataframe(periods=periods, freq='5min')
#     forecast = model.predict(future)
    
#     # 5. Extract only the future predictions (tail) to keep the API payload tiny
#     future_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
    
#     # Convert timestamps to strings so FastAPI can serialize them to JSON
#     future_forecast['ds'] = future_forecast['ds'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
#     # Return as a list of dictionaries
#     return future_forecast.to_dict(orient='records')

def get_prophet_prediction(db: Session, station_id: str, fuel_type: str, periods: int = 10):
    query = db.query(FuelData.timestamp, FuelData.stock_liters)\
              .filter(FuelData.station_id == station_id)\
              .filter(FuelData.fuel_type == fuel_type)\
              .order_by(FuelData.timestamp.asc()) # Ensure chronological order
    
    df = pd.read_sql(query.statement, db.bind)
    
    if len(df) < 50:
        return []

    df.rename(columns={'stock_liters': 'y'}, inplace=True)

    # --- THE TIME WARP FIX ---
    # Prophet needs to see 5-minute intervals to understand your daily seasonality.
    # We generate a fake timeline ending at the current real-world time, 
    # stepping backwards by 5 minutes for exactly the number of rows we have.
    
    latest_real_time = pd.Timestamp.now().replace(microsecond=0)
    simulated_timeline = pd.date_range(end=latest_real_time, periods=len(df), freq='5min')
    
    # Overwrite the real 5-second DB timestamps with our simulated 5-minute timeline
    df['ds'] = simulated_timeline
    # -------------------------

    # Train the Model
    model = Prophet(daily_seasonality=True, yearly_seasonality=False)
    model.fit(df)
    
    # Predict the next 24 periods (24 * 5 mins = 2 hours)
    future = model.make_future_dataframe(periods=periods, freq='5min')
    forecast = model.predict(future)
    
    future_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(periods)
    future_forecast['ds'] = future_forecast['ds'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return future_forecast.to_dict(orient='records')