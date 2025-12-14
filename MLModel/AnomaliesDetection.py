
class ThresholdAnomaliesDetector:
    def threshold_anomalies(self, df):
        anomalies = []

        row = df.iloc[0]
        plot_number = row["plot"]
        # ------------------------------
        # TEMPERATURE
        # ------------------------------
        temp = row["temperature"]
        tmin = 18
        tmax = 28

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
        hmin=45
        hmax = 75

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
        mmin=45
        mmax = 75

        # Alarm conditions
        if moist < 35:
            anomalies.append((plot_number, "Critical soil moisture drop: <35%"))
        # Normal range violation
        elif not (mmin <= moist <= mmax):
            anomalies.append((plot_number, f"Soil moisture outside normal range ({mmin}–{mmax}%): {moist}%"))

        return anomalies