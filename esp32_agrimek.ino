/*
 AgriMek ESP32 prototype (sends sensor data to Firebase Realtime Database via REST API)
 Hardware example:
  - ESP32 Dev board
  - DHT22 sensor (for temperature and humidity)
  - Analog soil moisture sensor (or capacitive sensor)

 Before using:
  - Create Firebase Realtime Database, get the database URL (https://your-db.firebaseio.com)
  - For testing you can set Realtime DB rules to true for read/write (not for production)
  - Optionally create a database secret or use an authenticated route. Here we use unauthenticated write for simplicity.
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// === CONFIG ===
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* firebase_url = "https://your-db.firebaseio.com/sensors.json"; // replace with your db + /sensors.json
const char* firebase_auth = ""; // optional: ?auth=TOKEN appended if set

// Pins
#define DHTPIN 4     // GPIO where DHT is connected
#define DHTTYPE DHT22
#define SOIL_PIN 34  // ADC pin for soil moisture sensor

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(1000);
  dht.begin();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  int retries = 0;
  while (WiFi.status() != WL_CONNECTED && retries < 20) {
    delay(500);
    Serial.print(".");
    retries++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi connection failed");
  }
}

void loop() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // read analog soil value and convert to percentage (calibration required)
  int analogValue = analogRead(SOIL_PIN);
  // assuming 0 (wet) -> 4095 (dry) for ESP32, map to 0-100%
  float soilPercent = map(analogValue, 4095, 0, 0, 100);

  // Build JSON payload
  unsigned long t = millis();
  String timestamp = String((unsigned long)time(NULL));

  String payload = "{";
  payload += "\"timestamp\":\"" + timestamp + "\",";
  payload += "\"temperature_C\":" + String(temperature) + ",";
  payload += "\"humidity_pct\":" + String(humidity) + ",";
  payload += "\"soil_moisture_pct\":" + String(soilPercent);
  payload += "}";

  Serial.println("Payload: " + payload);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String postUrl = String(firebase_url);
    if (strlen(firebase_auth) > 0) {
      postUrl += "?auth=";
      postUrl += firebase_auth;
    }
    http.begin(postUrl);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(payload);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.printf("HTTP %d\n", httpResponseCode);
      Serial.println(response);
    } else {
      Serial.printf("Error in POST: %d\n", httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi not connected");
  }

  delay(60000); // send every 60s (adjust as needed)
}
