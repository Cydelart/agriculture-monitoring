import pandas as pd
from datetime import datetime, timedelta

# ------------------------------
# Example class containing the function
# ------------------------------
class SensorAnalyzer:


    def sudden_change(self, df):
        anomalies = []

        if "timestamp" not in df.columns:
            raise ValueError("DataFrame must contain a 'timestamp' column.")

        # Sort newest -> oldest
        df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        SUDDEN_DROP_THRESHOLD = 10 # % 
        PROLONGED_THRESHOLD = 35 # % 
        PROLONGED_HOURS = 2 # hours
        MIN_HOURS = 1
        MAX_HOURS = 3


        #checking for the Sudden drop >10% in 1–3 hours

        last_idx = 0
        last_time = df.loc[last_idx, "timestamp"]
        last_moist = df.loc[last_idx, "moisture"]
        last_plot = df.loc[last_idx, "plot"]

        
        for i in range(1, len(df)):
            past_time = df.loc[i, "timestamp"]
            past_moist = df.loc[i, "moisture"]

            time_diff_h = (last_time - past_time).total_seconds() / 3600
            #print("time_diff_h =", time_diff_h)

            if time_diff_h > MAX_HOURS:
                break  # stop if over 3 hours

            if time_diff_h >= MIN_HOURS and past_moist - last_moist > SUDDEN_DROP_THRESHOLD:
                anomalies.append(
                    (last_plot,
                    f"Sudden moisture drop {past_moist - last_moist:.1f}% over {time_diff_h:.2f}h")
                )
                break  # stop after first anomaly detected



        # Prolonged low moisture detection 

        last_idx = 0  # most recent reading
        last_moist = df.loc[last_idx, "moisture"]

        # if the last reading is above threshold , no anomaly
        if last_moist >= PROLONGED_THRESHOLD:
            return anomalies

        # last reading is below threshold , check

        start_idx = last_idx
        for i in range(last_idx + 1, len(df)):
            if df.loc[i, "moisture"] < PROLONGED_THRESHOLD:

                start_idx = i  # extend the start of the below-threshold zone
            else:
                break  #reading above threshold

        # Duration between most recent and oldest in this low-moisture sequence
        duration_h = (df.loc[last_idx, "timestamp"] - df.loc[start_idx, "timestamp"]).total_seconds() / 3600

        # Record anomaly only if duration is long enough
        if duration_h >= PROLONGED_HOURS:
            plot = df.loc[last_idx, "plot"]
            anomalies.append(
                (plot, f"Prolonged low moisture <{PROLONGED_THRESHOLD}% for {duration_h:.2f}h")
            )

        return anomalies

