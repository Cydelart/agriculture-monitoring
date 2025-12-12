import time 
import random
import requests
from datetime import datetime, timezone

API_URL = "http://127.0.0.1:8000/api/sensor-readings/"

# ⚠️ make sure this token is still valid; if you get 401, you need a new one
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

# Week 2 Day 2 ywaliw multiple plots, run forever.

PLOT_IDS = [1, 2]          # put here the IDs of your plots, or just [1]
SEND_EVERY_SECONDS = 10    # how many seconds to wait between each batch

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json",
}


def send_reading(plot_id, sensor_type, value):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "plot": plot_id,
        "sensor_type": sensor_type,
        "value": value,
        "source": "simulator",
    }

    response = requests.post(API_URL, json=payload, headers=HEADERS)
    print(f"[PLOT {plot_id}] {sensor_type}={value} → status {response.status_code}")
    if response.status_code not in (200, 201):
        print("Response body:", response.text)


def main():
    print("Starting sensor simulator (Day 2 version)...")
    print(f"Plots: {PLOT_IDS}")
    print(f"Sending every {SEND_EVERY_SECONDS} seconds.\n")

    # Infinite loop: keeps running until you stop it
    while True:
        for plot_id in PLOT_IDS:
            # Generate random values like Day 1
            moisture = round(random.uniform(20, 80), 2)
            temperature = round(random.uniform(10, 35), 2)
            humidity = round(random.uniform(40, 95), 2)

            # Send to API
            send_reading(plot_id, "moisture", moisture)
            send_reading(plot_id, "temperature", temperature)
            send_reading(plot_id, "humidity", humidity)

        # Wait before next batch
        time.sleep(SEND_EVERY_SECONDS)


if __name__ == "__main__":
    main()
