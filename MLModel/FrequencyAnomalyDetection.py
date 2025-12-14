
class FrequencyAnomalyDetector :
    def frequency_anomalies(self, df, min_interval=5, max_interval=15):

        anomalies = []

        if "timestamp" not in df.columns:
            raise ValueError("DataFrame must contain a 'timestamp' column.")

        """at least 2 readings
        if len(df) < 2:
            return anomalies"""

        # Sort newest -> oldest
        df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)

        # Last two readings
        plot = df.loc[0, "plot"]
        
        
        last_time = df["timestamp"].iloc[0]
        prev_time = df["timestamp"].iloc[1]

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
