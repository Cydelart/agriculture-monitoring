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
            df = df.sort_values("timestamp")

            # --- Most recent reading ---
            latest = df.iloc[-1]
            latest_time = latest["timestamp"]

            # --- Rolling window before latest ---
            window_start = latest_time - pd.Timedelta(hours=window_hours)
            window_df = df[
                (df["timestamp"] >= window_start) &
                (df["timestamp"] <= latest_time)
            ]


            corr = window_df["temperature"].corr(window_df["soil_moisture"]) #the Pearson correlation coefficient between temperature and soil_moisture

            if corr <= 0:
                anomalies.append(
                    (
                        latest_time,
                        f"Moisture-Temperature correlation anomaly "
                        f"(corr={corr:.2f}, expected > 0 over last {window_hours}h)"
                    )
                )

            return anomalies