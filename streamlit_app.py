import streamlit as st
import pandas as pd
import requests
import time
import random
from datetime import datetime

# -------------------------------
# 🌿 AgriMek — IoT Prototype Dashboard
# -------------------------------

st.set_page_config(page_title="AgriMek — IoT Dashboard", layout="wide")

# --- Sidebar Configuration ---
st.sidebar.title("Configuration Firebase")
firebase_url = st.sidebar.text_input(
    "Firebase Realtime DB URL (e.g. https://your-db.firebaseio.com)",
    value=""
)
auth_token = st.sidebar.text_input("Database secret / auth token (optional)", type="password")
refresh_interval = st.sidebar.slider("Auto-refresh (seconds)", 5, 60, 30)

# --- Simulate Data Section ---
st.sidebar.markdown("---")
st.sidebar.subheader("🧪 Simulation de données (test)")

sim_count = st.sidebar.number_input("Nombre d'envois", min_value=1, max_value=100, value=5)
sim_delay = st.sidebar.number_input("Délai entre envois (secondes)", min_value=1, max_value=30, value=2)

def simulate_data(firebase_url, count=5, delay_seconds=2):
    """Simule l'envoi de lectures IoT aléatoires vers Firebase."""
    st.info("🚀 Simulation démarrée — envoi des données vers Firebase...")
    for i in range(count):
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "temperature_C": round(random.uniform(20, 35), 2),
            "humidity_pct": round(random.uniform(40, 80), 2),
            "soil_moisture_pct": round(random.uniform(20, 60), 2)
        }
        try:
            response = requests.post(f"{firebase_url.rstrip('/')}/sensors.json", json=data)
            if response.status_code in (200, 201):
                st.success(f"✅ Donnée {i+1}/{count} envoyée : {data}")
            else:
                st.error(f"⚠️ Erreur {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"❌ Erreur de connexion : {e}")
        time.sleep(delay_seconds)
    st.success("🎉 Simulation terminée avec succès !")

if st.sidebar.button("🚀 Simuler des données"):
    if firebase_url:
        simulate_data(firebase_url, count=sim_count, delay_seconds=sim_delay)
    else:
        st.sidebar.warning("⚠️ Veuillez d'abord entrer votre URL Firebase.")

# --- Fetch Data from Firebase ---
def fetch_data(firebase_url, auth_token=None):
    """Récupère les données depuis Firebase Realtime Database."""
    try:
        url = f"{firebase_url.rstrip('/')}/sensors.json"
        if auth_token:
            url += f"?auth={auth_token}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if not data:
                return pd.DataFrame()
            df = pd.DataFrame(data.values())
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df.sort_values("timestamp", ascending=False, inplace=True)
            return df
        else:
            st.error(f"Erreur fetch Firebase: {response.status_code} — {response.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur de connexion Firebase: {e}")
        return pd.DataFrame()

# --- Main Dashboard Layout ---
st.title("🌿 AgriMek — IoT Prototype Dashboard")
st.caption("Dashboard connected to Firebase Realtime Database (REST). Configure your Firebase URL and optional auth token in the sidebar.")

if firebase_url:
    placeholder = st.empty()

    while True:
        df = fetch_data(firebase_url, auth_token)

        with placeholder.container():
            if not df.empty:
                st.subheader("📊 Mesures récentes")
                st.dataframe(df[["humidity_pct", "soil_moisture_pct", "temperature_C", "timestamp"]].head(10))

                last_row = df.iloc[0]
                st.subheader("🧭 Dernière lecture et recommandation")

                col1, col2, col3 = st.columns(3)
                col1.metric("Humidité du sol (%)", f"{last_row['soil_moisture_pct']}")
                col2.metric("Température (°C)", f"{last_row['temperature_C']}")
                col3.metric("Humidité (%)", f"{last_row['humidity_pct']}")

                st.subheader("📈 Graphiques")
                st.line_chart(df[["temperature_C", "humidity_pct", "soil_moisture_pct"]].set_index("timestamp"))
            else:
                st.warning("Aucune donnée trouvée. Envoie des données depuis ESP32 ou utilise la simulation.")

            st.markdown(f"⏱️ Dernière mise à jour : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(refresh_interval)
else:
    st.info("👉 Entrez votre URL Firebase pour démarrer le tableau de bord.")
