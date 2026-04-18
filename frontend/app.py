import streamlit as st
import pandas as pd
import api_client
from datetime import datetime

# Configuration de la page Streamlit 
st.set_page_config(page_title="Dashboard AGIL - Sprint 2", layout="wide")

# Identifiant de la station (spécifié dans le document : BI00001) [cite: 22, 41]
STATION_ID = "BI00001"

st.title(f"⛽ Système de Monitoring AGIL - Station {STATION_ID}")
st.markdown("---")

# --- RÉCUPÉRATION DES DONNÉES ACTUELLES ---
current_data = api_client.get_current_data(STATION_ID) # Appelle GET /current [cite: 225]

if current_data:
    st.header("📊 Indicateurs Clés de Performance (KPIs)")
    
    # Création de colonnes pour chaque type de carburant (Gasoil50, SansPlomb) [cite: 42]
    cols = st.columns(len(current_data))
    
    total_sales_5min = 0
    sales_split = {}

    for i, fuel in enumerate(current_data):
        # Extraction des données brutes [cite: 34-39]
        f_type = fuel.get("fuel_type", "Inconnu")
        stock = fuel.get("stock_liters", 0)
        capacity = fuel.get("capacity_liters", 10000)
        price = fuel.get("price_tnd", 0.0)
        off_price = fuel.get("official_price_tnd", 0.0)
        sales_5min = fuel.get("sales_last_5min_liters", 0)
        ts_str = fuel.get("timestamp")

        # 1. KPIs de Stock [cite: 105-108, 120]
        utilization_pct = (stock / capacity) * 100 if capacity > 0 else 0
        is_low_stock = utilization_pct < 15

        # 2. KPIs de Ventes (Extrapolation quotidienne) [cite: 128-131]
        est_daily_sales = sales_5min * (24 * 12)
        total_sales_5min += sales_5min
        sales_split[f_type] = sales_5min

        # 3. KPIs de Prix (Déviation et Anomalie) [cite: 139-144]
        price_diff = price - off_price
        price_diff_pct = (price_diff / off_price * 100) if off_price > 0 else 0

        # 4. KPI de Fraîcheur des données [cite: 151-153]
        freshness_msg = "N/A"
        if ts_str:
            last_update = pd.to_datetime(ts_str).tz_localize(None)
            diff_min = int((datetime.now() - last_update).total_seconds() / 60)
            freshness_msg = f"Il y a {diff_min} min"

        # Affichage dans l'interface
        with cols[i]:
            st.subheader(f"Produit : {f_type}")
            st.caption(f"Dernière mise à jour : {freshness_msg}")
            
            # Métrique Stock avec alerte visuelle si < 15% [cite: 120]
            st.metric(
                label="Niveau de Stock", 
                value=f"{stock:,.0f} L", 
                delta=f"{utilization_pct:.1f}% utilisé",
                delta_color="normal" if not is_low_stock else "inverse"
            )

            # Métrique Prix avec écart par rapport au prix officiel 
            st.metric(
                label="Prix Actuel (TND)", 
                value=f"{price:.3f}", 
                delta=f"{price_diff:+.3f} ({price_diff_pct:+.1f}%)",
                delta_color="inverse" # Rouge si le prix est supérieur au prix officiel
            )

            # Métrique Ventes 
            st.metric(label="Ventes Est. / Jour", value=f"{est_daily_sales:,.0f} L")
            st.divider()

    # Affichage de la répartition de la demande [cite: 132-137]
    st.subheader("🎯 Répartition de la Demande")
    if total_sales_5min > 0:
        split_cols = st.columns(len(sales_split))
        for idx, (ft, val) in enumerate(sales_split.items()):
            pct = (val / total_sales_5min) * 100
            split_cols[idx].progress(pct/100, text=f"{ft} : {pct:.1f}%")
    else:
        st.info("En attente de données de ventes pour calculer la répartition.")

else:
    st.error("Impossible de charger les données actuelles. Vérifiez la connexion avec le Backend.")

st.markdown("---")

# --- SECTION HISTORIQUE ET GRAPHIQUES ---
st.header("📈 Évolution Historique")
fuel_choice = st.selectbox("Sélectionner un carburant pour l'analyse :", ["Gasoil50", "SansPlomb"])

# Récupération de l'historique via GET /history [cite: 245]
history_data = api_client.get_history_data(STATION_ID, fuel_choice)

if history_data:
    df = pd.DataFrame(history_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    g_col1, g_col2 = st.columns(2)
    
    with g_col1:
        st.write(f"**Évolution des stocks - {fuel_choice}**")
        st.line_chart(df.set_index('timestamp')['stock_liters']) # [cite: 14, 265]
        
    with g_col2:
        st.write(f"**Tendance des ventes (toutes les 5 min) - {fuel_choice}**")
        st.bar_chart(df.set_index('timestamp')['sales_last_5min_liters']) # [cite: 14, 266]
else:
    st.info("Aucun historique disponible pour ce carburant.")

st.markdown("---")

# --- SECTION ALERTES TEMPS RÉEL ---
st.header("⚠️ Alertes Système")
# Récupération des alertes via GET /alerts [cite: 268]
alerts = api_client.get_alerts(STATION_ID)

if alerts:
    df_alerts = pd.DataFrame(alerts)
    # Style conditionnel pour les types d'alertes [cite: 161, 163]
    st.dataframe(
        df_alerts[["timestamp", "fuel_type", "alert_type", "message"]].sort_values('timestamp', ascending=False),
        use_container_width=True,
        hide_index=True
    )
else:
    st.success("✅ Aucune alerte active. Le système est stable.")