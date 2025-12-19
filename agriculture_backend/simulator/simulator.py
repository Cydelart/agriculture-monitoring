import time
import numpy as np
import requests
from datetime import datetime, timezone, timedelta

# -----------------------------
# 1️⃣ Get JWT token
# -----------------------------
TOKEN_URL = "http://127.0.0.1:8000/api/token/"
USERNAME = "menyar"
PASSWORD = "menyar"
response = requests.post(TOKEN_URL, json={"username": USERNAME, "password": PASSWORD})
if response.status_code != 200:
    raise Exception(f"Failed to get token: {response.text}")

tokens = response.json()
access_token = tokens["access"]
<<<<<<< HEAD

=======
refresh_token = tokens["refresh"]
#print(refresh_token)
>>>>>>> main
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}"
}

# -----------------------------
# 1️⃣a Test user profile & permissions
# -----------------------------
PROFILE_URL = "http://127.0.0.1:8000/api/user-profiles/"
profile_response = requests.get(PROFILE_URL, headers=HEADERS)
if profile_response.status_code == 200:
    profiles = profile_response.json()
    print("=== User Profiles & Roles ===")
    for profile in profiles:
        # Adjust field names according to your API output
        print(f"ID: {profile['id']}, User: {profile['user']}, Role: {profile['role']}")
    print("=============================\n")
else:
    print(f"Failed to fetch profiles: {profile_response.status_code} → {profile_response.text}\n")

# -----------------------------
# 2️⃣ API setup for sensor readings & anomalies
# -----------------------------
SENSOR_API_URL = "http://127.0.0.1:8000/api/sensor-readings/"
ANOMALY_API_URL = "http://127.0.0.1:8000/api/anomalies/"
PLOT_IDS = [1, 2]
SEND_EVERY_SECONDS = 20  # adjust frequency

# -----------------------------
# 3️⃣ Sensor simulation parameters
# -----------------------------
MOISTURE_BASE = 50
TEMP_BASE = 25
HUMIDITY_BASE = 60

IRRIGATION_INTERVAL = 12 * 60 * 60  # every 12 hours
last_irrigation = datetime.now(timezone.utc) - timedelta(hours=6)

def diurnal_temperature(hour):
    """Simulate a sine-wave temperature (min at 4am, max at 2pm)."""
    return TEMP_BASE + 5 * np.sin((2 * np.pi / 24) * (hour - 4))

def moisture_change(moisture, now):
    """Simulate moisture decreasing, increase at irrigation."""
    global last_irrigation
    if (now - last_irrigation).total_seconds() >= IRRIGATION_INTERVAL:
        moisture += np.random.uniform(10, 20)
        last_irrigation = now
    moisture -= np.random.uniform(0.1, 0.3)
    return moisture

def humidity_from_temperature(temp):
    """Humidity inversely correlated with temperature with noise."""
    return HUMIDITY_BASE - (temp - TEMP_BASE) * 1.5 + np.random.normal(0, 2)

def inject_anomaly(value, sensor_type):
    """Return value and whether it is anomalous"""
    r = np.random.rand()
    is_anomaly = False
    if r < 0.05:
        is_anomaly = True
        if sensor_type == "moisture":
            value -= np.random.uniform(15, 25)
        elif sensor_type == "temperature":
            value += np.random.uniform(5, 10)
        elif sensor_type == "humidity":
            value -= np.random.uniform(20, 30)
    elif r < 0.1:
        is_anomaly = True
        value += np.random.uniform(-10, 10)
    elif r < 0.12:
        is_anomaly = True
        value += np.random.uniform(-5, 5)
    return value, is_anomaly

def send_reading(plot_id, sensor_type, value):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plot": plot_id,
        "sensor_type": sensor_type,
        "value": round(value, 2),
        "source": "simulator",
    }
    timestamp = datetime.now(timezone.utc).isoformat()

    response = requests.post(SENSOR_API_URL, json=payload, headers=HEADERS)

    print(
    f"[{timestamp}] "
    f"[PLOT {plot_id}] {sensor_type}={value:.2f} → status {response.status_code}"
    )

    print(f"[PLOT {plot_id}] {sensor_type}={value:.2f} → status {response.status_code}")
    if response.status_code not in (200, 201):
        print("Response body:", response.text)
    return response.json().get("id")  # return sensor reading ID if available

"""def send_anomaly(plot_id, sensor_type, value, related_reading=None):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plot": plot_id,
        "anomaly_type": f"{sensor_type} anomaly",
        "severity": severity,
        "related_reading": related_reading
    }
    response = requests.post(ANOMALY_API_URL, json=payload, headers=HEADERS)
    print(f"[PLOT {plot_id}] → AnomalyEvent posted: status {response.status_code}")
    if response.status_code not in (200, 201):
        print("Response body:", response.text)
"""
# -----------------------------
# 4️⃣ Main loop
# -----------------------------
def main():
    print("Starting realistic sensor simulator with anomaly posting...")
    print(f"Plots: {PLOT_IDS}")
    print(f"Sending every {SEND_EVERY_SECONDS / 60:.1f} minutes.\n")

    moisture_levels = {pid: MOISTURE_BASE for pid in PLOT_IDS}

    while True:
        now = datetime.now(timezone.utc)
        hour = now.hour + now.minute / 60

        for plot_id in PLOT_IDS:
            temperature = diurnal_temperature(hour) + np.random.normal(0, 0.5)
            moisture_levels[plot_id] = moisture_change(moisture_levels[plot_id], now)
            humidity = humidity_from_temperature(temperature)

            # Inject anomalies
            moisture, mo_anomaly = inject_anomaly(moisture_levels[plot_id], "moisture")
            temperature, temp_anomaly = inject_anomaly(temperature, "temperature")
            humidity, hum_anomaly = inject_anomaly(humidity, "humidity")

            # Send sensor readings
            moisture_id = send_reading(plot_id, "moisture", moisture)
            temp_id = send_reading(plot_id, "temperature", temperature)
            hum_id = send_reading(plot_id, "humidity", humidity)
            print("fffffffffffffffff")

            if mo_anomaly:
                print(f"🚨 [SIMULATOR] Injected MOISTURE anomaly on plot {plot_id}: {moisture:.2f}")

            if temp_anomaly:
                print(f"🚨 [SIMULATOR] Injected TEMPERATURE anomaly on plot {plot_id}: {temperature:.2f}")

            if hum_anomaly:
                print(f"🚨 [SIMULATOR] Injected HUMIDITY anomaly on plot {plot_id}: {humidity:.2f}")

            # Post anomalies if detected
            """
            if mo_anomaly:
                send_anomaly(plot_id, "moisture", moisture, related_reading=moisture_id)
            if temp_anomaly:
                send_anomaly(plot_id, "temperature", temperature, related_reading=temp_id)
            if hum_anomaly:
                send_anomaly(plot_id, "humidity", humidity, related_reading=hum_id)"""

        time.sleep(SEND_EVERY_SECONDS)

if __name__ == "__main__":
    main()
