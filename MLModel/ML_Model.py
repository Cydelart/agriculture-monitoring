import numpy as np
import pandas as pd

from AnomaliesDetection import ThresholdAnomaliesDetector 

from sudden_change_anomaly import SuddenChangeDetector

from Thi_AnomalydetectorModel import THIMonthlyDetector

from FrequencyAnomalyDetection import FrequencyAnomalyDetector

from CorrelationDetection import CorrelationAnomalyDetector 


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


def sensor_dataframe(df):
    

    df = df.copy()

    # Pivot table
    df_final = df.pivot_table(
        index=["timestamp", "plot"],
        columns="sensor_type",
        values="value",
        aggfunc="mean"
    ).reset_index()

    

    return df_final


# -----------------------------------------------------------
# WRAPPER: GROUP ALL ANOMALIES BY TIMESTAMP/INDEX
# -----------------------------------------------------------
thi_detector = THIMonthlyDetector(sustained_hours=2)

THIMonthlyDetector.train(df_year_normal);

def detect_all(df_final):

    all_anomalies = []
    

    all_anomalies += ThresholdAnomaliesDetector.threshold_anomalies(df_final)
    
    all_anomalies += SuddenChangeDetector.sudden_change(df_final)

    all_anomalies += THIMonthlyDetector.thi_anomalies(df_final,2)

    all_anomalies += FrequencyAnomalyDetector.frequency_anomalies(df_final,5,15)

    all_anomalies += CorrelationAnomalyDetector.moisture_temperature_correlation_anomaly(df_final,2) 

    # Group anomalies per index
    grouped = {}
    for plot, anomaly in all_anomalies:
        grouped.setdefault(plot, []).append(anomaly)

    return grouped
