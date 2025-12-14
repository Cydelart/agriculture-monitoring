import pandas as pd
from ML_Model import CropAnomalyDetector


data = {
    "timestamp": pd.date_range(
        start="2025-01-01 10:00:00",
        periods=15,
        freq="20min"
    ),

    # Temperature gradually increasing (normal)
    "temperature": [
        20, 21, 22, 23, 24,
        25, 26, 27, 28, 29,
        30, 31, 32, 33, 34
    ],

    # Soil moisture also increasing → positive correlation
    "soil_moisture": [
        30, 31, 32, 33, 34,
        35, 36, 37, 38, 39,
        40, 41, 42, 43, 44
    ],

    "plot": ["Plot A"] * 15
}

df = pd.DataFrame(data)

detector = CropAnomalyDetector()
result = detector.detect_all(df)

print("Anomalies detected:")
for row, anomaly in result.items():
    print(f"plot {row}: {anomaly}")
