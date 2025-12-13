import numpy as np
import pandas as pd


class CropAnomalyDetector:

    def __init__(self):
        # Normal ranges (indicative)
        self.thresholds = {
            "temperature": (18, 28),   # °C daytime
            "humidity": (45, 75),      # %
            "moisture": (45, 75),      # % soil moisture
        }

    # -----------------------------------------------------------
    # 1. THRESHOLD + ALARM ANOMALIES
    # -----------------------------------------------------------
    def threshold_anomalies(self, df):
        anomalies = []

        for i, row in df.iterrows():
            plot_number = row["plot"]
            # ------------------------------
            # TEMPERATURE
            # ------------------------------
            temp = row["temperature"]
            tmin, tmax = self.thresholds["temperature"]

            # Alarm conditions
            if temp > 32:
                anomalies.append((plot_number, "Heat stress: temperature >32°C"))
            elif temp < 10:
                anomalies.append((plot_number, "Cold stress: temperature <10°C"))

            # Normal range violation (but not extreme)
            elif not (tmin <= temp <= tmax):
                anomalies.append((plot_number, f"Temperature outimeide normal range ({tmin}–{tmax}°C): {temp}°C"))

            # ------------------------------
            # HUMIDITY
            # ------------------------------
            hum = row["humidity"]
            hmin, hmax = self.thresholds["humidity"]

            # Alarm conditions
            if hum < 30:
                anomalies.append((plot_number, "Dry conditions: humidity <30%"))
            elif hum > 85:
                anomalies.append((plot_number, "Excessive moisture: humidity >85%"))

            # Normal range violation
            elif not (hmin <= hum <= hmax):
                anomalies.append((plot_number, f"Humidity outside normal range ({hmin}–{hmax}%): {hum}%"))

            # ------------------------------
            # SOIL MOISTURE
            # ------------------------------
            moist = row["moisture"]
            mmin, mmax = self.thresholds["moisture"]

            # Alarm conditions
            if moist < 35:
                anomalies.append((plot_number, "Critical soil moisture drop: <35%"))
            # Normal range violation
            elif not (mmin <= moist <= mmax):
                anomalies.append((plot_number, f"Soil moisture outside normal range ({mmin}–{mmax}%): {moist}%"))

        return anomalies


    # -----------------------------------------------------------
    # 2. SUDDEN DROPS / SPIKES (moisture or temperature)
    # -----------------------------------------------------------
    """def sudden_change(self, df):
        anomalies = []

    # MUST contain a timestamp column
        if "timestamp" not in df.columns:
            raise ValueError("DataFrame must contain a 'timestamp' column for time-based anomaly detection.")

    
        df = df.sort_values("timestamp").reset_index(drop=True) #Tri Temporel
        df["timestamp"] = pd.to_datetime(df["timestamp"]) # Ensures timestamps are datetime

    # Compute time differences in hours
        df["time_diff_h"] = df["timestamp"].diff().dt.total_seconds() / 3600
        df["moist_diff"] = df["moisture"].diff()
        df["temp_diff"] = df["temperature"].diff()

        for i in range(1, len(df)):
            dt = df.loc[i, "time_diff_h"]
            moist_drop = df.loc[i, "moist_diff"]
            temp_delta = df.loc[i, "temp_diff"]

        # Skip if timestamp gap is too large (missing data handled elsewhere)
            if pd.isna(dt) or dt <= 0:
                continue

        # ---------------------------------------------------------
        # 1️⃣ SUDDEN MOISTURE DROP >10% IN 1–3 HOURS (Table 1)
        # ---------------------------------------------------------
            if -moist_drop > 10 and 1 <= dt <= 3:
                anomalies.append((plot_number,f"Sudden moisture drop {abs(moist_drop):.1f}% over {dt:.2f}h"
            ))

        # ---------------------------------------------------------
        # 2️⃣ ABRUPT TEMPERATURE CHANGE >10°C (within short interval)
        # ---------------------------------------------------------
            if abs(temp_delta) > 10 and dt <= 3:
                anomalies.append((plot_number,
                f"Abrupt temperature change {temp_delta:+.1f}°C over {dt:.2f}h"
            ))

        return anomalies"""

    def thi_anomalies(self, df, min_duration_hours):
        anomalies = []

        # EXPECTED THI
        expected_THI = 21.1  #formule expected : THI = T − (0.55 × (1 − RH/100) × (T − 14.5)) avec : T_expected = (18 + 28) / 2 = 23°C et RH_expected = (45 + 75) / 2 = 60%


        in_deviation = False
        start_time = -1     
        start_thi = -1     
        start_dev = -1    

        
        # Sort newest -> oldest
        df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        for i in range(len(df)):
            temp = df.loc[i, "temperature"]
            hum = df.loc[i, "humidity"]
            plot = df.loc[i, "plot"]
            time = df.loc[i, "timestamp"]

            # Compute THI
            thi = temp - (0.55 * (1 - hum / 100) * (temp - 14.5))

            # % deviation
            deviation = abs(thi - expected_THI) / expected_THI * 100

            if deviation > 15:
                if not in_deviation:
                    # start of deviation
                    in_deviation = True
                    start_time = time
                    start_thi = thi
                    start_dev = deviation
            else:
                if in_deviation:
                    # end of deviation, check duration
                    duration_h = (start_time - time).total_seconds() / 3600
                    if duration_h >= min_duration_hours:
                        anomalies.append(
                            (plot,
                            f"THI sustained deviation >15% "
                            f"(THI={start_thi:.2f}, deviation={start_dev:.1f}%, "
                            f"duration={duration_h:.2f}h)")
                        )
                    in_deviation = False
                    start_time = -1
                    start_thi = -1
                    start_dev = -1

        # Check if last readings are still in deviation
        if in_deviation and start_time != -1:
            duration_h = (start_time - df.iloc[-1]["timestamp"]).total_seconds() / 3600
            if duration_h >= min_duration_hours:
                plot = df.iloc[-1]["plot"]
                anomalies.append(
                    (plot,
                    f"THI sustained deviation >15% "
                    f"(THI={start_thi:.2f}, deviation={start_dev:.1f}%, "
                    f"duration={duration_h:.2f}h)")
                )

        return anomalies
        
        

    def frequency_anomalies(self, df, min_interval=5, max_interval=15):

        anomalies = []

        if "timestamp" not in df.columns:
            raise ValueError("DataFrame must contain a 'timestamp' column.")

        """# Need at least 2 readings
        if len(df) < 2:
            return anomalies"""

        # Sort by timestamp to be safe
        df = df.sort_values("timestamp")

        # Last two readings
        last_idx = df.index[-1]
        prev_idx = df.index[-2]

        last_time = df["timestamp"].iloc[-1]
        prev_time = df["timestamp"].iloc[-2]

        # Difference in minutes
        diff_min = (last_time - prev_time).total_seconds() / 60

        # --- Detect anomalies ---
        if diff_min > max_interval:
            anomalies.append(
                (plot, f"Reading delay: interval {diff_min:.1f} min (> {max_interval} min)")
            )

        elif diff_min < min_interval:
            anomalies.append(
                (plot, f"Too frequent readings: interval {diff_min:.1f} min (< {min_interval} min)")
            )

        return anomalies



    # -----------------------------------------------------------
    # WRAPPER: GROUP ALL ANOMALIES BY TIMESTAMP/INDEX
    # -----------------------------------------------------------
    def detect_all(self, df):
        all_anomalies = []

        # Add all threshold anomalies
        #all_anomalies += self.threshold_anomalies(df)
        
            # 3. Add THI anomalies
        all_anomalies += self.thi_anomalies(df, min_duration_hours=1.0)

        # Group anomalies per index
        grouped = {}
        for plot, anomaly in all_anomalies:
            grouped.setdefault(plot, []).append(anomaly)

        return grouped
