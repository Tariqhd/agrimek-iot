    # AgriMek — IoT Prototype (ESP32 + Firebase + Streamlit)

    This repository contains a prototype to connect an ESP32 + sensors to a Firebase Realtime Database and visualize the data with a Streamlit dashboard.

    ## Contents
    - `streamlit_app.py` — Streamlit dashboard that reads from Firebase Realtime Database via REST.
    - `esp32_agrimek.ino` — ESP32 Arduino sketch (DHT22 + analog soil moisture).
    - `requirements.txt` — Python dependencies.
    - `.gitignore`

    ## Quick setup (Firebase)
    1. Create a Firebase project and Realtime Database.
    2. In Realtime Database -> Rules, for testing you can set:

```
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

   **Warning:** This is only for testing. Do not leave open in production.

    3. Note your database URL, e.g. `https://your-db.firebaseio.com`.
    4. If you require authentication, use a database secret or service account and update the Streamlit app / ESP32 code accordingly.

    ## Running the Streamlit dashboard locally
    1. Create a virtualenv and install dependencies:
       ```bash
       python -m venv venv
       source venv/bin/activate  # on Windows: venv\Scripts\activate
       pip install -r requirements.txt
       ```
    2. Copy `streamlit_app.py` to a folder and run:
       ```bash
       streamlit run streamlit_app.py
       ```
    3. In the sidebar enter your Firebase Realtime Database URL (e.g. `https://your-db.firebaseio.com`) and optional auth token.

    ## Flashing the ESP32
    1. Open `esp32_agrimek.ino` in Arduino IDE or PlatformIO.
    2. Replace `YOUR_WIFI_SSID`, `YOUR_WIFI_PASSWORD`, and `firebase_url`.
    3. Connect DHT sensor and soil sensor to the pins defined in the sketch (adjust pins as needed).
    4. Flash the board and monitor serial to see POST responses.

    ## Deploying to Streamlit Cloud / Replit
    - Create a GitHub repo with these files, then deploy to Streamlit Cloud or Replit following their guides.

    ## Next steps (recommended)
    - Add authentication (Firebase service account for secure writes).
    - Use MQTT broker (e.g., Mosquitto or Adafruit IO) for lower-latency telemetry.
    - Calibrate soil sensor and convert ADC readings to real moisture percentages per sensor model.
    - Add crop-specific thresholds and ML models for irrigation scheduling.

    ----
    Developed for the AgriMek competition prototype. Contact: tarikhmidani11@gmail.com
