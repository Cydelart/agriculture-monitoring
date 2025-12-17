import time
import numpy as np
import requests
from datetime import datetime, timezone, timedelta

from django.utils.dateparse import parse_datetime

import os
import sys
import django

# Ajouter le dossier courant au PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Le module settings est dans le même dossier
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agriculture_backend.settings")

django.setup()
from monitoring.ML.rsagent import RSAgent

# Instantiate the agent once
rs_agent = RSAgent()
from monitoring.models import AnomalyEvent, SensorReading
from monitoring.ML.rolling_stats import RollingStatsService
rolling_service = RollingStatsService(window_hours=2)

# -----------------------------
# 2️⃣ API & auth setup
# -----------------------------
TOKEN_URL = "http://127.0.0.1:8000/api/token/"
USERNAME = "menyar"
PASSWORD = "menyar"

token_resp = requests.post(TOKEN_URL, json={"username": USERNAME, "password": PASSWORD})
if token_resp.status_code != 200:
    raise Exception(f"Failed to get token: {token_resp.status_code} → {token_resp.text}")

access_token = token_resp.json()["access"]
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}

SENSOR_API_URL = "http://127.0.0.1:8000/api/sensor-readings/"

# -----------------------------
# 3️⃣ Simulator settings
# -----------------------------
PLOT_IDS = [1, 2]
SEND_EVERY_SECONDS = 300  # 5 minutes
MOISTURE_BASE = 50.0
TEMP_BASE = 25.0
HUMIDITY_BASE = 60.0

IRRIGATION_INTERVAL = 12 * 60 * 60  # 12h
last_irrigation = datetime.now(timezone.utc) - timedelta(hours=6)
rng = np.random.default_rng(seed=42)

# -----------------------------
# 4️⃣ Scenario definitions
# -----------------------------
SCENARIOS = [

    # 1️⃣ Sudden drops → irrigation failure
    {
        "plot_id": 1,
        "sensor_type": "moisture",
        "start_min": 5,
        "end_min": 12,
        "kind": "drop",
        "magnitude": (15, 25),  # rapid drop
        "severity": "high",
        "label": "Irrigation failure (sudden moisture drop)",
    },

    # 2️⃣ Spikes → sensor malfunction or extreme events
    {
        "plot_id": 2,
        "sensor_type": "temperature",
        "start_min": 15,
        "end_min": 18,
        "kind": "spike",
        "magnitude": (6, 10),  # sudden spike
        "severity": "medium",
        "label": "Heatwave / sensor spike",
    },

    # 3️⃣ Drift → gradual sensor calibration drift
    {
        "plot_id": 1,
        "sensor_type": "humidity",
        "start_min": 5,
        "end_min": 30,
        "kind": "drift",
        "magnitude": (0.05, 0.15),  # small incremental change per step
        "severity": "low",
        "label": "Gradual humidity drift",
    },
]


# -----------------------------
# 5️⃣ Sensor value functions
# -----------------------------
def diurnal_temperature(hour_float: float) -> float:
    return TEMP_BASE + 5 * np.sin((2 * np.pi / 24) * (hour_float - 4))

def moisture_change(moisture: float, now: datetime) -> float:
    global last_irrigation
    if (now - last_irrigation).total_seconds() >= IRRIGATION_INTERVAL:
        moisture += rng.uniform(10, 20)
        last_irrigation = now
    moisture -= rng.uniform(0.1, 0.3)
    return moisture

def humidity_from_temperature(temp: float) -> float:
    return HUMIDITY_BASE - (temp - TEMP_BASE) * 1.5 + rng.normal(0, 2)

def active_scenarios(elapsed_min: float, plot_id: int, sensor_type: str):
    return [
        s for s in SCENARIOS
        if s["plot_id"] == plot_id
        and s["sensor_type"] == sensor_type
        and s["start_min"] <= elapsed_min <= s["end_min"]
    ]

def apply_scenarios(value, elapsed_min, plot_id, sensor_type):
    events = []
    for s in SCENARIOS:
        if s["plot_id"] == plot_id and s["sensor_type"] == sensor_type:
            if s["start_min"] <= elapsed_min <= s["end_min"]:
                magnitude = rng.uniform(s["magnitude"][0], s["magnitude"][1])

                if s["kind"] == "drop":
                    value -= magnitude
                elif s["kind"] == "spike":
                    value += magnitude
                elif s["kind"] == "drift":
                    value += magnitude  # gradual drift

                # Add event only if scenario is active
                events.append({"severity": s["severity"], "label": s["label"], "kind": s["kind"]})
                print(f"[ABNORMAL VALUE] plot={plot_id} sensor={sensor_type} value={value:.2f} kind={s['kind']}, severity={s['severity']}")

    return value, events

def send_reading(plot_id: int, sensor_type: str, value: float):
    # Prepare payload
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plot": plot_id,
        "sensor_type": sensor_type,
        "value": round(float(value), 2),
        "source": "simulator_scenarios",
    }

    # Send reading to API
    resp = requests.post(SENSOR_API_URL, json=payload, headers=HEADERS)
    print(f"[PLOT {plot_id}] {sensor_type}={payload['value']} → {resp.status_code}")

    if resp.status_code in (200, 201):
        # Compute rolling stats
        result = rolling_service.process_reading(
            plot_id=plot_id,
            sensor_type=sensor_type,
            value=payload["value"],
        )

        # Find the related reading object in DB
        reading_obj = (
            SensorReading.objects
            .filter(plot_id=plot_id, sensor_type=sensor_type)
            .order_by("-timestamp")
            .first()
        )

        # Map rolling status to severity
        

        if result["status"] != "ok":
           if result["status"] == "critical":
            severity = "high"
           elif result["status"] == "warning":
            severity = "medium"
           elif result["status"] == "low":
            severity = "low"
           anomaly = AnomalyEvent.objects.create(
            timestamp=datetime.now(timezone.utc),
            plot_id=plot_id,
            anomaly_type=f"{sensor_type}_zscore",
            severity=severity,
            model_confidence=abs(result["zscore"]),
            related_reading_id=reading_obj.id if reading_obj else None,
        )
           recommendation = rs_agent.generate_recommendation(anomaly)
           print(f"[RSAGENT] {recommendation.explanation_text} -> {recommendation.recommended_action}")

        # Clear console output
        print(f"[ROLLING] plot={plot_id} sensor={sensor_type} "
              f"mean={result['rolling_mean']} std={result['rolling_std']} "
              f"z={result['zscore']} status={result['status']}")
        print(f"[WINDOW] plot={plot_id} sensor={sensor_type} values={result['window_values']}")

# 6️⃣ Main simulation loop
# -----------------------------
def main():
    print("Starting realistic sensor simulator...")
    print(f"Plots: {PLOT_IDS}")
    print(f"Sending every {SEND_EVERY_SECONDS}s (~{SEND_EVERY_SECONDS/60:.1f} min)\n")

    start_time = datetime.now(timezone.utc)
    moisture_levels = {pid: MOISTURE_BASE for pid in PLOT_IDS}

    # Initialize rolling anomaly detector
    while True:
        now = datetime.now(timezone.utc)
        elapsed_min = (now - start_time).total_seconds() / 60.0
        hour = now.hour + now.minute / 60.0

        for plot_id in PLOT_IDS:
            # baseline sensor values
            temperature = diurnal_temperature(hour) + rng.normal(0, 0.5)
            moisture_levels[plot_id] = moisture_change(moisture_levels[plot_id], now)
            humidity = humidity_from_temperature(temperature)

            # apply scenarios
            moisture, m_events = apply_scenarios(moisture_levels[plot_id], elapsed_min, plot_id, "moisture")
            temperature, t_events = apply_scenarios(temperature, elapsed_min, plot_id, "temperature")
            humidity, h_events = apply_scenarios(humidity, elapsed_min, plot_id, "humidity")

            # send readings to backend
            send_reading(plot_id, "moisture", moisture)
            send_reading(plot_id, "temperature", temperature)
            send_reading(plot_id, "humidity", humidity)

            # log ground-truth scenarios
            for e in (m_events + t_events + h_events):
                print(f"[GROUND_TRUTH] plot={plot_id} {e['kind']} severity={e['severity']} → {e['label']}")

        time.sleep(SEND_EVERY_SECONDS)

if __name__ == "__main__":
    main()
