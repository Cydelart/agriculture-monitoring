
class ThresholdAnomaliesDetector:
    def threshold_anomalies(self, df):
        anomalies = []
        df = df.sort_values("timestamp", ascending=False).reset_index(drop=True)
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
            #anomalies.append((plot_number, "Heat stress: temperature >32°C"))
            anomalies.append({
                "plot": plot_number,
                "anomaly_type": "Heat stress: temperature >32°C",
                "severity": "low",                  # à calculer selon la valeur
                "model_confidence": 0.95,            # ou valeur calculée par ton modèle
                "related_reading": None       # la lecture qui déclenche l’anomalie
            })
        elif temp < 10:
            #anomalies.append((plot_number, "Cold stress: temperature <10°C"))
            print("temp !!!!")
            anomalies.append({
                "plot": plot_number,
                "anomaly_type": "Cold stress: temperature <10°C",
                "severity": "low",                  # à calculer selon la valeur
                "model_confidence": 0.95,            # ou valeur calculée par ton modèle
                "related_reading": None       # la lecture qui déclenche l’anomalie
            })
        # Normal range violation (but not extreme)
        elif not (tmin <= temp <= tmax):
            #anomalies.append((plot_number, f"Temperature outimeide normal range ({tmin}–{tmax}°C): {temp}°C"))
            anomalies.append({
                "plot": plot_number,
                "anomaly_type": f"Temperature outimeide normal range ({tmin}–{tmax}°C): {temp}°C",
                "severity": "low",                  # à calculer selon la valeur
                "model_confidence": 0.95,            # ou valeur calculée par ton modèle
                "related_reading": None       # la lecture qui déclenche l’anomalie
            })
        # ------------------------------
        # HUMIDITY
        # ------------------------------
        hum = row["humidity"]
        hmin=45
        hmax = 75

        # Alarm conditions
        if hum < 30:
            #anomalies.append((plot_number, "Dry conditions: humidity <30%"))
            anomalies.append({
                "plot": plot_number,
                "anomaly_type": "Dry conditions: humidity <30%",
                "severity": "low",                  # à calculer selon la valeur
                "model_confidence": 0.95,            # ou valeur calculée par ton modèle
                "related_reading": row["timestamp"]       # la lecture qui déclenche l’anomalie
            })
            
        elif hum > 85:
            print("humidity !!!")
            #anomalies.append((plot_number, "Excessive moisture: humidity >85%"))
            anomalies.append({
                "plot": plot_number,
                "anomaly_type": "Excessive moisture: humidity >85%",
                "severity": "low",                  # à calculer selon la valeur
                "model_confidence": 0.95,            # ou valeur calculée par ton modèle
                "related_reading": None       # la lecture qui déclenche l’anomalie
            })
        # Normal range violation
        elif not (hmin <= hum <= hmax):
            #anomalies.append((plot_number, f"Humidity outside normal range ({hmin}–{hmax}%): {hum}%"))
            anomalies.append({
                "plot": plot_number,
                "anomaly_type": f"Humidity outside normal range ({hmin}–{hmax}%): {hum}%",
                "severity": "low",                  # à calculer selon la valeur
                "model_confidence": 0.95,            # ou valeur calculée par ton modèle
                "related_reading": row["timestamp"]       # la lecture qui déclenche l’anomalie
            })
        # ------------------------------
        # SOIL MOISTURE
        # ------------------------------
        moist = row["moisture"]
        mmin=45
        mmax = 75

        # Alarm conditions
        if moist < 35:
            #anomalies.append((plot_number, "Critical soil moisture drop: <35%"))
            anomalies.append({
                "plot": plot_number,
                "anomaly_type": "Critical soil moisture drop: <35%",
                "severity": "low",                  # à calculer selon la valeur
                "model_confidence": 0.95,            # ou valeur calculée par ton modèle
                "related_reading": row["timestamp"]       # la lecture qui déclenche l’anomalie
            })
        # Normal range violation
        elif not (mmin <= moist <= mmax):
            #anomalies.append((plot_number, f"Soil moisture outside normal range ({mmin}–{mmax}%): {moist}%"))
            anomalies.append({
                "plot": plot_number,
                "anomaly_type": f"Soil moisture outside normal range ({mmin}–{mmax}%): {moist}%",
                "severity": "low",                  # à calculer selon la valeur
                "model_confidence": 0.95,            # ou valeur calculée par ton modèle
                "related_reading": row["timestamp"]       # la lecture qui déclenche l’anomalie
            })
        
        return anomalies