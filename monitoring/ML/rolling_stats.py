from datetime import timedelta
from math import sqrt
from django.utils import timezone

from monitoring.models import SensorReading


class RollingStatsService:
    """
    Computes rolling mean/std for a given (plot_id, sensor_type)
    using a TIME-BASED sliding window.
    """

    def __init__(self, window_hours=2, warn_z=3, crit_z=4):
        self.window = timedelta(hours=window_hours)
        self.warn_z = warn_z
        self.crit_z = crit_z

    # ---------------------------------------------------------
    # 1️⃣ Fetch readings from DB in rolling window
    # ---------------------------------------------------------
    def _fetch_window_readings(self, plot_id, sensor_type, now):
        """
        Get all readings in [now - window, now]
        """
        window_start = now - self.window

        return (
            SensorReading.objects
            .filter(
                plot_id=plot_id,
                sensor_type=sensor_type,
                timestamp__gte=window_start,
                timestamp__lte=now,
            )
            .order_by("timestamp")
        )

    # ---------------------------------------------------------
    # 2️⃣ Compute mean & std
    # ---------------------------------------------------------
    def _mean_std(self, values):
        n = len(values)
        if n == 0:
            return None, None

        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = sqrt(variance)

        return mean, std

    # ---------------------------------------------------------
    # 3️⃣ Main entry point
    # ---------------------------------------------------------
    def process_reading(self, plot_id, sensor_type, value, timestamp=None):

        now = timestamp or timezone.now()

        # 1. Fetch rolling window data
        readings = self._fetch_window_readings(plot_id, sensor_type, now)
        values = [r.value for r in readings]

        # 2. Compute stats
        mean, std = self._mean_std(values)

        # 3. Compute z-score
        if mean is None or std is None or std == 0:
            zscore = 0.0
            status = "ok"
            explanation = "Not enough data for anomaly detection"
        else:
            zscore = (value - mean) / std
            abs_z = abs(zscore)

            if abs_z >= self.crit_z:
                status = "critical"
                explanation = "Value is far outside normal range"
            elif abs_z >= self.warn_z:
                status = "warning"
                explanation = "Value is slightly outside normal range"

            elif abs_z >= 2.0:  # NEW: low-level anomaly threshold
                status = "low"
                explanation = "Value is mildly outside normal range"
            else:
                status = "ok"
                explanation = "Value is within normal range"

        # 4. Clear output
        return {
            "time": now.isoformat(),
            "plot_id": plot_id,
            "sensor_type": sensor_type,
            "value": round(value, 2),
            "rolling_mean": round(mean, 2) if mean is not None else None,
            "rolling_std": round(std, 2) if std is not None else None,
            "zscore": round(zscore, 2),
            "status": status,
            "explanation": explanation,
            "window_hours": self.window.total_seconds() / 3600,
            "samples_in_window": len(values),
            "window_values": [round(v, 2) for v in values],  # ← Tableau dynamique
        }
