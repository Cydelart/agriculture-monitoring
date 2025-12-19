import pandas as pd
import numpy as np
from Thi_AnomalydetectorModel import THIMonthlyDetector
# -------------------------
# Full-year static dataframe (normal readings)
# -------------------------
start_time = pd.Timestamp("2025-01-01 00:00:00")
end_time   = pd.Timestamp("2025-12-31 23:55:00")

# Generate timestamps every 5 minutes
timestamps = pd.date_range(start=start_time, end=end_time, freq="5min")

# Temperature: normal daytime range 18-28°C
# Deterministic pattern using sine wave for small seasonal/diurnal variation
days = (timestamps - pd.Timestamp("2025-01-01")).total_seconds() / (24*3600)
temperature = 23 + 5 * np.sin(2 * np.pi * days / 365)  # oscillates 18-28°C roughly

# Humidity: normal range 45-75%
humidity = 60 + 15 * np.cos(2 * np.pi * days / 365)     # oscillates 45-75% roughly

# Plot column
plot = ["Plot 1"] * len(timestamps)

# Build dataframe
df_year_normal = pd.DataFrame({
    "timestamp": timestamps,
    "temperature": temperature,
    "humidity": humidity,
    "plot": plot
})


data = {
    "timestamp": pd.date_range(start="2025-01-01 10:00:00", periods=15, freq="15min"),

    # First 10 readings normal, last 5 extremely hot
    "temperature": [
        36, 36, 36, 36, 36, 36,   # normal (6*0.25h = 1.5h)
        36, 38, 40, 41, 42, 40, 39, 38, 37  # anomaly (9*0.25h = 2.25h)
    ],

    # First 10 readings normal, last 5 very low humidity
     "humidity": [
        30, 30, 30, 30, 30, 30,   # normal
        30, 25, 20, 18, 15, 20, 22, 25, 28  # anomaly
    ],

    # All readings belong to the same plot
    "plot": ["Plot 1"] * 15
}

df_test = pd.DataFrame(data)

"""print(df_year_normal.head())
print(df_year_normal.tail())
print(f"Total readings: {len(df_year_normal)}")"""

detector = THIMonthlyDetector(sustained_hours=2)
expected_thi = detector.train(df_year_normal)
print("Expected THI per month learned from training data:")
print(expected_thi)


result = detector.thi_anomalies(df_test, 2)

print("Anomalies detected:")
for plot, anomaly in result:
    print(f"Plot {plot}: {anomaly}")


