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

"""print(df_year_normal.head())
print(df_year_normal.tail())
print(f"Total readings: {len(df_year_normal)}")"""

detector = THIMonthlyDetector(sustained_hours=2)
expected_thi = detector.train(df_year_normal)
print("Expected THI per month learned from training data:")
print(expected_thi)