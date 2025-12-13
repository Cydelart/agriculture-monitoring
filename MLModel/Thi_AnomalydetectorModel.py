import pandas as pd


class THIMonthlyDetector:

    DEVIATION_THRESHOLD = 15  # fixed business rule (%)

    def __init__(self, sustained_hours=2):
        self.sustained_hours = sustained_hours
        self.expected_thi_by_month = {}

    @staticmethod
    def compute_thi(T, RH):
        return T - (0.55 * (1 - RH / 100) * (T - 14.5))

    def train(self, df):
        """
        Learn expected THI per month from historical normal data
        """
        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["month"] = df["timestamp"].dt.month
        df["thi"] = self.compute_thi(df["temperature"], df["humidity"])

        self.expected_thi_by_month = (
            df.groupby("month")["thi"].median().to_dict()
        )

        return self.expected_thi_by_month

    def thi_anomalies(self, df, min_duration_hours):
        anomalies = []

        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["thi"] = self.compute_thi(df["temperature"], df["humidity"])

        # Sort newest -> oldest
        df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)

        # ---- Step 1: Check only the most recent reading ----
        latest = df.iloc[0]
        expected_THI_latest = self.expected_thi_by_month[latest["timestamp"].month]

        latest_deviation = abs(latest["thi"] - expected_THI_latest) / expected_THI_latest * 100

        if latest_deviation <= self.DEVIATION_THRESHOLD:
            return anomalies

        # ---- Step 2: Verify sustained deviation ----
        in_deviation = False
        start_time = -1
        start_thi = -1
        start_dev = -1

        for i in range(1, len(df)):
            temp = df.loc[i, "temperature"]
            hum = df.loc[i, "humidity"]
            plot = df.loc[i, "plot"]
            time = df.loc[i, "timestamp"]

            expected_THI = self.expected_thi_by_month[time.month]
            thi = self.compute_thi(temp, hum)

            deviation = abs(thi - expected_THI) / expected_THI * 100

            
            if deviation > 15:
                if not in_deviation:
                    in_deviation = True
                    start_time = time
                    start_thi = thi
                    start_dev = deviation
            else:
                if in_deviation:
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
            # =================================

        
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
