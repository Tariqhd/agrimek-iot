import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

st.set_page_config(page_title="AgriMek IoT Dashboard", layout="wide")
st.title("AgriMek — IoT Prototype Dashboard")
st.write("Dashboard connected to Firebase Realtime Database (REST). Configure your Firebase URL and optional auth token in the sidebar.")

# Sidebar - configuration
st.sidebar.header("Configuration Firebase")
firebase_url = st.sidebar.text_input("Firebase Realtime DB URL (e.g. https://your-db.firebaseio.com)", value="")
auth_token = st.sidebar.text_input("Database secret / auth token (optional)", type="password", value="")
refresh = st.sidebar.slider("Auto-refresh (seconds)", 5, 5, 30, 5)
st.sidebar.markdown("Instructions: create a Firebase Realtime Database and set rules to allow read for testing or generate a database secret/token. See README.")

def fetch_data():
    if not firebase_url:
        return pd.DataFrame()
    url = firebase_url.rstrip('/') + '/sensors.json'
    params = {}
    if auth_token:
        params['auth'] = auth_token
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        if not data:
            return pd.DataFrame()
        # data expected as {"timestamp1": {...}, "timestamp2": {...}, ...}
        items = []
        for k, v in data.items():
            # if value already a dict with timestamp field, keep it
            rec = v.copy()
            # ensure timestamp parsing
            if 'timestamp' not in rec:
                rec['timestamp'] = k
            items.append(rec)
        df = pd.DataFrame(items)
        # normalize column names and types
        for col in ['soil_moisture_pct','temperature_C','humidity_pct']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.sort_values('timestamp')
        return df
    except Exception as e:
        st.sidebar.error(f"Erreur fetch Firebase: {e}")
        return pd.DataFrame()

placeholder = st.empty()

while True:
    df = fetch_data()
    with placeholder.container():
        if df.empty:
            st.info("Aucune donnée trouvée. Envoie des données depuis ESP32 ou tests simulés recommandés.")
        else:
            col1, col2 = st.columns([2,1])
            with col1:
                st.subheader("Mesures récentes")
                st.dataframe(df.tail(50).reset_index(drop=True))
                st.subheader("Graphiques")
                st.line_chart(df.set_index('timestamp')[['soil_moisture_pct','temperature_C','humidity_pct']].tail(200))
            with col2:
                st.subheader("Dernière lecture et recommandation")
                last = df.dropna(subset=['soil_moisture_pct']).iloc[-1]
                st.metric("Humidité du sol (%)", f"{last['soil_moisture_pct']}")
                st.metric("Température (°C)", f"{last.get('temperature_C','N/A')}")
                st.metric("Humidité (%)", f"{last.get('humidity_pct','N/A')}")
                # simple rule-based recommendation
                MOISTURE_THRESHOLD = st.sidebar.number_input('Seuil humidité (%)', 30.0, 5.0, 30.0, 1.0)
                if last['soil_moisture_pct'] < MOISTURE_THRESHOLD:
                    deficit = MOISTURE_THRESHOLD - last['soil_moisture_pct']
                    liters = round(0.5 + 0.1*deficit, 2)
                    st.warning(f"Recommandation: Arroser ~{liters} L/m² (humidité basse)")
                else:
                    st.success("Etat: OK — Pas d'arrosage requis")
        st.write('---')
        st.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    time.sleep(refresh)
