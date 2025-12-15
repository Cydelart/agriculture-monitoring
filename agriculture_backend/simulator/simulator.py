import time
import numpy as np
import requests
from datetime import datetime, timezone, timedelta

# -----------------------------
# Get JWT token
# -----------------------------
TOKEN_URL = "http://127.0.0.1:8000/api/token/"  # adjust if your endpoint differs
USERNAME = "syrin"
PASSWORD = "cyrine"

token_resp = requests.post(TOKEN_URL, json={"username": USERNAME, "password": PASSWORD})
if token_resp.status_code != 200:
    raise Exception(f"Failed to get token: {token_resp.status_code} → {token_resp.text}")

access_token = token_resp.json()["access"]

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}

# -----------------------------
# Test user profile & permissions (optional)
# -----------------------------
PROFILE_URL = "http://127.0.0.1:8000/api/user-profiles/"
profile_response = requests.get(PROFILE_URL, headers=HEADERS)
if profile_response.status_code == 200:
    profiles = profile_response.json()
    print("=== User Profiles & Roles ===")
    for profile in profiles:
        # adjust keys if your API returns different field names
        print(f"ID: {profile.get('id')}, User: {profile.get('user')}, Role: {profile.get('role')}")
    print("=============================\n")
else:
    print(f"Failed to fetch profiles: {profile_response.status_code} → {profile_response.text}\n")

# -----------------------------
# API setup - send sensor readings only
# Anomaly detection handled by ML later
# -----------------------------
SENSOR_API_URL = "http://127.0.0.1:8000/api/sensor-readings/"
PLOT_IDS = [1, 2, 3]
SEND_EVERY_SECONDS = 20

# -----------------------------
# Sensor simulation parameters
# -----------------------------
MOISTURE_BASE = 50.0
TEMP_BASE = 25.0
HUMIDITY_BASE = 60.0

IRRIGATION_INTERVAL = 12 * 60 * 60  # every 12 hours
last_irrigation = datetime.now(timezone.utc) - timedelta(hours=6)

# reproducible randomness (optional but recommended)
rng = np.random.default_rng(seed=42)

def diurnal_temperature(hour_float: float) -> float:
    """Sine-wave temperature (min ~ 4am, max ~ 2pm)."""
    return TEMP_BASE + 5 * np.sin((2 * np.pi / 24) * (hour_float - 4))

def moisture_change(moisture: float, now: datetime) -> float:
    """Moisture decreases gradually; increases on irrigation interval."""
    global last_irrigation
    if (now - last_irrigation).total_seconds() >= IRRIGATION_INTERVAL:
        moisture += rng.uniform(10, 20)
        last_irrigation = now
    moisture -= rng.uniform(0.1, 0.3)
    return moisture

def humidity_from_temperature(temp: float) -> float:
    """Humidity inversely correlated with temperature + noise."""
    return HUMIDITY_BASE - (temp - TEMP_BASE) * 1.5 + rng.normal(0, 2)

# -----------------------------
# Anomaly scenarios - repeat every 60 minutes
# Severity kept as ground truth, not posted to API
# ML will create AnomalyEvent and set confidence
# -----------------------------
CYCLE_DURATION = 60

SCENARIOS = [
    # Plot 1: Short irrigation failure
    {
        "plot_id": 1,
        "sensor_type": "moisture",
        "start_min": 8,
        "end_min": 12,
        "kind": "drop",
        "magnitude": (15, 20),
        "severity": "medium",
        "label": "Irrigation failure (sudden moisture drop)",
    },
    # Plot 2: Brief temperature spike
    {
        "plot_id": 2,
        "sensor_type": "temperature",
        "start_min": 22,
        "end_min": 26,
        "kind": "spike",
        "magnitude": (6, 9),
        "severity": "medium",
        "label": "Heatwave (temperature spike)",
    },
    # Plot 3: Soil drying event
    {
        "plot_id": 3,
        "sensor_type": "moisture",
        "start_min": 35,
        "end_min": 40,
        "kind": "drop",
        "magnitude": (10, 15),
        "severity": "low",
        "label": "Soil drying event (moisture drop)",
    },
]

def active_scenarios(elapsed_min: float, plot_id: int, sensor_type: str):
    """Return scenarios active for this plot/sensor at this time.
    Uses modulo to make scenarios repeat every CYCLE_DURATION minutes.
    """
    # Use modulo to create repeating cycles
    cycle_position = elapsed_min % CYCLE_DURATION
    
    return [
        s for s in SCENARIOS
        if s["plot_id"] == plot_id
        and s["sensor_type"] == sensor_type
        and s["start_min"] <= cycle_position <= s["end_min"]
    ]

def apply_scenarios(value: float, elapsed_min: float, plot_id: int, sensor_type: str):
    """
    Apply scripted scenarios (no randomness deciding whether anomalies occur).
    Returns (new_value, ground_truth_events)
    ground_truth_events include severity, but are NOT sent to backend.
    """
    events = []
    for s in active_scenarios(elapsed_min, plot_id, sensor_type):
        kind = s["kind"]

        if kind == "drop":
            value -= rng.uniform(*s["magnitude"])
        elif kind == "spike":
            value += rng.uniform(*s["magnitude"])
        elif kind == "drift":
            value -= float(s["magnitude"])
        # else: unknown -> ignore

        events.append(
            {
                "severity": s["severity"],   # ✅ kept here for later/evaluation
                "label": s["label"],
                "kind": kind,
            }
        )
    return value, events

# -----------------------------
# Send readings to API
# -----------------------------
def send_reading(plot_id: int, sensor_type: str, value: float):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plot": plot_id,
        "sensor_type": sensor_type,
        "value": round(float(value), 2),
        "source": "simulator_scenarios",
    }

    resp = requests.post(SENSOR_API_URL, json=payload, headers=HEADERS)
    print(f"[PLOT {plot_id}] {sensor_type}={payload['value']} → status {resp.status_code}")
    if resp.status_code not in (200, 201):
        print("Response body:", resp.text)

# -----------------------------
# Main loop
# -----------------------------
def main():
    print("Starting sensor simulator with continuous anomaly generation")
    print(f"Monitoring plots: {PLOT_IDS}")
    print(f"Update interval: {SEND_EVERY_SECONDS}s (~{SEND_EVERY_SECONDS/60:.1f} min)")
    print(f"Anomaly cycle duration: {CYCLE_DURATION} minutes (repeating)")
    print(f"\nAnomaly schedule (repeats every {CYCLE_DURATION} min):")
    for s in SCENARIOS:
        print(f"  Plot {s['plot_id']}: {s['sensor_type']} {s['kind']} "
              f"({s['start_min']}-{s['end_min']} min) - {s['severity']} severity")
    print("\n" + "="*60 + "\n")

    start_time = datetime.now(timezone.utc)
    moisture_levels = {pid: MOISTURE_BASE for pid in PLOT_IDS}

    while True:
        now = datetime.now(timezone.utc)
        elapsed_min = (now - start_time).total_seconds() / 60.0
        cycle_min = elapsed_min % CYCLE_DURATION
        hour = now.hour + now.minute / 60.0

        print(f"Elapsed: {elapsed_min:.1f} min | Cycle: {cycle_min:.1f}/{CYCLE_DURATION} min")

        for plot_id in PLOT_IDS:
            # baseline values
            temperature= diurnal_temperature(hour) + rng.normal(0, 0.5)
            moisture_levels[plot_id] = moisture_change(moisture_levels[plot_id], now)
            humidity = humidity_from_temperature(temperature)

            # apply anomaly scenarios
            moisture, m_events = apply_scenarios(moisture_levels[plot_id], elapsed_min, plot_id, "moisture")
            temperature, t_events = apply_scenarios(temperature, elapsed_min, plot_id, "temperature")
            humidity, h_events = apply_scenarios(humidity, elapsed_min, plot_id, "humidity")

            # send readings to API
            send_reading(plot_id, "moisture", moisture)
            send_reading(plot_id, "temperature", temperature)
            send_reading(plot_id, "humidity", humidity)

            # log anomalies for verification
            for e in (m_events + t_events + h_events):
                print(f"  [ANOMALY] Plot {plot_id}: {e['kind']} ({e['severity']}) - {e['label']}")

        print()
        time.sleep(SEND_EVERY_SECONDS)

if __name__  == "__main__":
    main()