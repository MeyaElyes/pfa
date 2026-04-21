import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import api_client
from datetime import datetime

# 1. Page Config & Custom Styling
st.set_page_config(page_title="AGIL | Fuel Monitor Pro", layout="wide", initial_sidebar_state="expanded")

# Professional CSS Injection
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #003366;
        margin-bottom: 10px;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .station-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #0066cc;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "selected_station" not in st.session_state:
    st.session_state.selected_station = "BI00001"
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "single"
if "selected_stations" not in st.session_state:
    st.session_state.selected_stations = ["BI00001"]

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.divider()
    
    # Load available stations
    try:
        all_stations = api_client.get_stations()
        if isinstance(all_stations, list) and len(all_stations) > 0:
            if isinstance(all_stations[0], dict):
                station_options = {s["station_id"]: f"{s['station_id']} - {s['location']}" for s in all_stations}
            else:
                station_options = {s: s for s in all_stations}
        else:
            station_options = {"BI00001": "BI00001 - Tunis"}
    except:
        station_options = {"BI00001": "BI00001 - Tunis"}
    
    # View mode selector
    st.subheader("View Mode")
    view_mode = st.radio(
        "Select View Type",
        ["Single Station", "Multi-Station Overview"],
        key="view_radio"
    )
    st.session_state.view_mode = "single" if view_mode == "Single Station" else "multi"
    
    st.divider()
    
    if st.session_state.view_mode == "single":
        st.subheader("Single Station")
        selected_station = st.selectbox(
            "Select Station",
            list(station_options.keys()),
            format_func=lambda x: station_options[x],
            key="single_select"
        )
        st.session_state.selected_station = selected_station
    else:
        st.subheader("Multiple Stations")
        selected_stations = st.multiselect(
            "Select Stations",
            list(station_options.keys()),
            default=list(station_options.keys())[:3] if len(station_options) >= 3 else list(station_options.keys()),
            format_func=lambda x: station_options[x],
            key="multi_select"
        )
        st.session_state.selected_stations = selected_stations if selected_stations else ["BI00001"]
    
    st.divider()
    
    # Refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.rerun()

# --- MAIN HEADER ---
with st.container():
    col_title, col_status = st.columns([3, 1])
    with col_title:
        if st.session_state.view_mode == "single":
            st.title(f"⛽ AGIL Fuel Monitor - {st.session_state.selected_station}")
            st.caption(f"Single Station Monitoring • Terminal {st.session_state.selected_station}")
        else:
            st.title(f"⛽ AGIL Fuel Monitor - Fleet View")
            st.caption(f"Multi-Station Overview • {len(st.session_state.selected_stations)} Stations")
    with col_status:
        st.write(f"**Status:** 🟢 Online")
        st.write(f"*Updated: {datetime.now().strftime('%H:%M:%S')}*")

st.divider()

# --- SINGLE STATION VIEW ---
if st.session_state.view_mode == "single":
    current_data = api_client.get_current_data(st.session_state.selected_station)
    
    if current_data:
        # Tabs for single station
        tab1, tab2, tab3 = st.tabs(["📊 Real-Time Overview", "📈 Analytics & Trends", "⚠️ Incident Log"])
        
        with tab1:
            st.subheader("Current Inventory & Pricing")
            cols = st.columns(len(current_data))
            
            for i, fuel in enumerate(current_data):
                f_type = fuel.get("fuel_type", "Unknown")
                stock = fuel.get("stock_liters", 0)
                capacity = fuel.get("capacity_liters", 10000)
                price = fuel.get("price_tnd", 0.0)
                off_price = fuel.get("official_price_tnd", 0.0)
                utilization = (stock / capacity) * 100 if capacity > 0 else 0
                
                # Status Logic
                status_icon = "🟢" if utilization > 20 else "🟡" if utilization > 10 else "🔴"
                price_status = "⚠️" if abs(price - off_price) > 0.01 else "✅"
                
                with cols[i]:
                    st.markdown(f"### {status_icon} {f_type}")
                    
                    # Progress Bar for Stock
                    st.progress(utilization/100)
                    
                    # Metric Grid
                    m1, m2 = st.columns(2)
                    m1.metric("Stock Level", f"{stock:,.0f} L", f"{utilization:.1f}%")
                    m2.metric("Price (TND)", f"{price:.3f}", f"{price - off_price:+.3f}", delta_color="inverse")
                    
                    with st.expander("View Details"):
                        st.write(f"**Capacity:** {capacity:,.0f} L")
                        st.write(f"**Sales (5min):** {fuel.get('sales_last_5min_liters', 0):.0f} L")
                        st.write(f"**Est. Daily Sales:** {fuel.get('sales_last_5min_liters', 0) * 288:,.0f} L")
                        st.write(f"**Official Price:** {off_price:.3f} TND")
                        st.write(f"**Price Compliance:** {price_status}")
        
        with tab2:
            st.subheader("Historical Performance Analysis")
            fuel_choice = st.segmented_control("Fuel Type", ["Gasoil50", "SansPlomb"], default="Gasoil50")
            
            history_data = api_client.get_history_data(st.session_state.selected_station, fuel_choice)
            if history_data:
                df = pd.DataFrame(history_data)
                
                # Debug: Show raw data first
                with st.expander("🔍 Debug: Raw API Data", expanded=False):
                    st.write("Raw data sample:")
                    st.dataframe(df.head(), use_container_width=True)
                    st.write(f"Timestamp column type: {df['timestamp'].dtype}")
                    st.write(f"Stock column type: {df['stock_liters'].dtype}")
                
                # Fix timestamp parsing with explicit format handling
                try:
                    # Try parsing as datetime, handle various formats
                    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
                    # Convert to local timezone for display
                    df['timestamp'] = df['timestamp'].dt.tz_convert('Africa/Tunis')
                except:
                    # Fallback: assume it's already datetime or parse without timezone
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Ensure data is sorted by timestamp
                df = df.sort_values('timestamp').reset_index(drop=True)
                
                # Remove duplicates based on timestamp (keep the last occurrence)
                df = df.drop_duplicates(subset=['timestamp'], keep='last')
                
                # Debug: Show processed data
                st.write(f"**Data Range:** {len(df)} records from {df['timestamp'].min()} to {df['timestamp'].max()}")
                st.write(f"**Stock Range:** {df['stock_liters'].min():.1f} - {df['stock_liters'].max():.1f} L")
                st.write(f"**Unique timestamps:** {df['timestamp'].nunique()}")
                
                if len(df) > 1:
                    col_chart1, col_chart2 = st.columns(2)
                    with col_chart1:
                        st.markdown("**Stock Level Over Time**")
                        # Use line chart instead of area chart for better visibility
                        st.line_chart(df.set_index('timestamp')['stock_liters'], use_container_width=True)
                        # Also show area chart below
                        st.area_chart(df.set_index('timestamp')['stock_liters'], use_container_width=True)
                    with col_chart2:
                        st.markdown("**5-Minute Sales Velocity**")
                        st.bar_chart(df.set_index('timestamp')['sales_last_5min_liters'], use_container_width=True)
                else:
                    st.warning("Not enough data points for meaningful charts. Need at least 2 data points.")
            else:
                st.info("No historical data available for selected fuel type.")
            
            # ===== AI FORECAST SECTION =====
            st.divider()
            st.subheader("🤖 AI-Powered Stock Forecast (Prophet)")
            
            # Get available stations for forecast
            try:
                all_stations = api_client.get_stations()
                if isinstance(all_stations, list) and len(all_stations) > 0:
                    if isinstance(all_stations[0], dict):
                        forecast_stations = {s["station_id"]: f"{s['station_id']} - {s['location']}" for s in all_stations}
                    else:
                        forecast_stations = {s: s for s in all_stations}
                else:
                    forecast_stations = {"BI00001": "BI00001 - Tunis"}
            except:
                forecast_stations = {"BI00001": "BI00001 - Tunis"}
            
            # Station and Fuel Selectors
            col_station, col_fuel = st.columns(2)
            with col_station:
                selected_station_forecast = st.selectbox(
                    "Select Station for Forecast",
                    list(forecast_stations.keys()),
                    format_func=lambda x: forecast_stations[x],
                    key="forecast_station"
                )
            with col_fuel:
                selected_fuel = st.selectbox("Select Fuel Type for Forecast", ["Gasoil50", "SansPlomb"], key="forecast_fuel")
            
            if st.button("Generate AI Forecast"):
                with st.spinner(f"Training Prophet model for {selected_fuel} at {selected_station_forecast} on the backend..."):
                    # 1. Get History (Actuals)
                    history_data = api_client.get_history_data(selected_station_forecast, selected_fuel)
                    df_history = pd.DataFrame(history_data).reset_index(drop=True)
                    
                    # 2. Get Predictions (Forecast)
                    pred_data = api_client.get_predictions(selected_station_forecast, selected_fuel)
                    df_pred = pd.DataFrame(pred_data)
                    
                    if not df_history.empty and not df_pred.empty:
                        import plotly.graph_objects as go
                        
                        # Process historical data timestamps
                        try:
                            df_history['timestamp'] = pd.to_datetime(df_history['timestamp'], utc=True)
                            df_history['timestamp'] = df_history['timestamp'].dt.tz_convert('Africa/Tunis')
                        except:
                            df_history['timestamp'] = pd.to_datetime(df_history['timestamp'])
                        
                        # Process prediction timestamps
                        df_pred['ds'] = pd.to_datetime(df_pred['ds'])
                        
                        # Create Plotly Figure
                        fig = go.Figure()

                        # Add Historical Actuals (Solid Line)
                        fig.add_trace(go.Scatter(
                            x=df_history['timestamp'], 
                            y=df_history['stock_liters'],
                            mode='lines',
                            name='Actual Stock',
                            line=dict(color='blue', width=2)
                        ))

                        # Add Forecast Prediction (Dashed Line)
                        fig.add_trace(go.Scatter(
                            x=df_pred['ds'], 
                            y=df_pred['yhat'],
                            mode='lines',
                            name='Predicted Stock',
                            line=dict(color='orange', dash='dash', width=2)
                        ))
                        
                        # Add Confidence Intervals (Shaded Area)
                        # Create closed shape: upper -> lower (reversed)
                        x_vals = df_pred['ds'].tolist()
                        upper_vals = df_pred['yhat_upper'].tolist()
                        lower_vals = df_pred['yhat_lower'].tolist()
                        
                        fig.add_trace(go.Scatter(
                            x=x_vals + x_vals[::-1],  # forward + backward
                            y=upper_vals + lower_vals[::-1],  # upper + reversed lower
                            fill='toself',
                            fillcolor='rgba(255,165,0,0.2)',
                            line=dict(color='rgba(255,255,255,0)', width=0),
                            hoverinfo="skip",
                            showlegend=True,
                            name='Confidence Interval (95%)'
                        ))

                        fig.update_layout(
                            title=f"{selected_fuel} Stock Depletion Forecast - {selected_station_forecast}",
                            xaxis_title="Time",
                            yaxis_title="Stock Level (Liters)",
                            hovermode='x unified',
                            xaxis=dict(
                                tickformat='%H:%M',
                                tickangle=45
                            ),
                            yaxis=dict(
                                tickformat=',.0f'
                            ),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Not enough data to generate forecast.")
        
        with tab3:
            st.subheader("System Alerts & Notifications")
            alerts = api_client.get_alerts(st.session_state.selected_station, limit=100)
            if alerts:
                df_alerts = pd.DataFrame(alerts)
                
                # Add severity coloring
                severity_colors = {"critical": "🔴", "warning": "🟠", "info": "🟢"}
                df_alerts["Severity"] = df_alerts.get("severity", "info").map(lambda x: severity_colors.get(x, ""))
                
                st.dataframe(
                    df_alerts[["timestamp", "fuel_type", "alert_type", "severity", "message"]].sort_values('timestamp', ascending=False).head(50),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("✅ System clean. No alerts recorded.")
    else:
        st.error("📡 Backend Connection Lost. Please check API status.")

# --- MULTI-STATION VIEW ---
else:
    st.subheader(f"Monitoring {len(st.session_state.selected_stations)} Stations")
    
    # Try multi-station endpoint first, fallback to individual requests
    try:
        all_data = api_client.get_current_data_multi(st.session_state.selected_stations)
    except:
        all_data = []
        for sid in st.session_state.selected_stations:
            try:
                data = api_client.get_current_data(sid)
                for record in data:
                    record['station_id'] = sid
                all_data.extend(data)
            except:
                pass
    
    if all_data:
        # Station overview cards
        st.markdown("### Station Status Overview")
        cols = st.columns(min(3, len(st.session_state.selected_stations)))
        
        for idx, station_id in enumerate(st.session_state.selected_stations):
            station_data = [r for r in all_data if r.get('station_id') == station_id]
            
            with cols[idx % len(cols)]:
                if station_data:
                    # Calculate aggregate metrics
                    total_stock = sum(r.get('stock_liters', 0) for r in station_data)
                    total_capacity = sum(r.get('capacity_liters', 0) for r in station_data)
                    avg_utilization = (total_stock / total_capacity * 100) if total_capacity > 0 else 0
                    
                    status_icon = "🟢" if avg_utilization > 20 else "🟡" if avg_utilization > 10 else "🔴"
                    
                    st.markdown(f"""
                    <div class="station-card">
                    <h3>{status_icon} {station_id}</h3>
                    <p><strong>Stock:</strong> {total_stock:,.0f} / {total_capacity:,.0f} L ({avg_utilization:.1f}%)</p>
                    <p><strong>Fuels:</strong> {len(station_data)} types</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"No data for {station_id}")
        
        st.divider()
        
        # Detailed table view
        st.markdown("### Detailed Metrics Table")
        if all_data:
            df_all = pd.DataFrame(all_data)
            df_all['timestamp'] = pd.to_datetime(df_all.get('timestamp', ''))
            df_all['utilization_%'] = (df_all.get('stock_liters', 0) / df_all.get('capacity_liters', 1) * 100).round(1)
            
            display_cols = ['station_id', 'fuel_type', 'stock_liters', 'capacity_liters', 'utilization_%', 'price_tnd', 'official_price_tnd']
            available_cols = [c for c in display_cols if c in df_all.columns]
            
            st.dataframe(
                df_all[available_cols].sort_values('station_id'),
                use_container_width=True,
                hide_index=True
            )
        
        st.divider()
        
        # Global alerts across all stations
        st.markdown("### Global Alerts (All Selected Stations)")
        all_alerts = api_client.get_alerts(limit=100)
        
        if all_alerts:
            df_alerts = pd.DataFrame(all_alerts)
            
            # Filter to selected stations only
            if 'station_id' in df_alerts.columns:
                df_alerts = df_alerts[df_alerts['station_id'].isin(st.session_state.selected_stations)]
            
            if not df_alerts.empty:
                severity_colors = {"critical": "🔴", "warning": "🟠", "info": "🟢"}
                df_alerts["Severity"] = df_alerts.get("severity", "info").map(lambda x: severity_colors.get(x, ""))
                
                st.dataframe(
                    df_alerts[["timestamp", "station_id", "fuel_type", "alert_type", "severity"]].sort_values('timestamp', ascending=False).head(50),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No alerts for selected stations.")
        else:
            st.info("No alerts available.")
    else:
        st.error("No data available for selected stations. Please check API status.")