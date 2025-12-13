import pandas as pd
from ML_Model import CropAnomalyDetector


data = {
    "timestamp": pd.date_range(start="2025-01-01 10:00:00", periods=15, freq="5min"),

    # First 10 readings normal, last 5 extremely hot
    "temperature": [
        20, 21, 22, 23, 24,
        25, 26, 27, 28, 29,   # normal
        36, 38, 40, 41, 42    # strong anomaly zone
    ],

    # First 10 readings normal, last 5 very low
    "humidity": [
        50, 49, 48, 47, 46,
        45, 44, 43, 42, 41,   # normal
        30, 25, 20, 18, 15    # strong anomaly zone
    ],

    # Added plot column
    "plot": ["Plot A"] * 15
}

df = pd.DataFrame(data)

detector = CropAnomalyDetector()
result = detector.detect_all(df)

print("Anomalies detected:")
for row, anomaly in result.items():
    print(f"plot {row}: {anomaly}")
