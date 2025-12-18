import numpy as np
import pandas as pd


class CorrelationAnomalyDetector:
    def moisture_temperature_correlation_anomaly(
            self,
            df,
            window_hours=2,
            
        ):
            """
            Detect anomaly ONLY for the most recent reading based on
            moisture-temperature correlation in the previous window.

            df must contain:
            - timestamp
            - temperature
            - soil_moisture
            """

            anomalies = []

            df = df.copy()
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            # Sort newest -> oldest
            df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)

            # --- Most recent reading ---
            latest = df.iloc[0]
            latest_time = latest["timestamp"]

            # --- Rolling window before latest ---
            window_start = latest_time - pd.Timedelta(hours=window_hours)
            window_df = df[
                (df["timestamp"] >= window_start) &
                (df["timestamp"] <= latest_time)
            ]


            corr = window_df["temperature"].corr(window_df["moisture"]) #the Pearson correlation coefficient between temperature and soil_moisture

            if corr <= 0:
                """anomalies.append(
                    (
                        latest_time,
                        f"Moisture-Temperature correlation anomaly "
                        f"(corr={corr:.2f}, expected > 0 over last {window_hours}h)"
                    )
                )"""
                anomalies.append({
                "plot": latest["plot"],
                "anomaly_type": f"Moisture-Temperature correlation anomaly "
                        f"(corr={corr:.2f}, expected > 0 over last {window_hours}h)",
                "severity": "medium",                  # à calculer selon la valeur
                "model_confidence": 0.95,            # ou valeur calculée par ton modèle
                "related_reading": latest["timestamp"]        # la lecture qui déclenche l’anomalie
                    
            })

            return anomalies