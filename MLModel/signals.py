# core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import timedelta
import pandas as pd

from monitoring.models import SensorReading, AnomalyEvent
from ML_Model import detect_all

@receiver(post_save, sender=SensorReading)
def sensor_reading_post_save(sender, instance, created, **kwargs):

    if not created:
        return

    #the readings of the same plot for the past 3 hours
    start_time = instance.timestamp - timedelta(hours=3)

    # Fetch readings for same plot
    qs = SensorReading.objects.filter(
        plot=instance.plot,
        timestamp__gte=start_time
    ).order_by("timestamp")

    if qs.count() < 5:
        return  # not enough context

    # Convert to DataFrame
    data = []
    for r in qs:
        data.append({
            "timestamp": r.timestamp,
            "sensor_type": r.sensor_type,
            "value": r.value,
            "plot": r.plot.name
        })

    df = pd.DataFrame(data)

    # 🔍 Run ML
    anomaly = detect_all(df, instance)

    if anomaly is None:
        return

    # 🧨 Save anomaly
    anomaly_event = AnomalyEvent.objects.create(
        plot=instance.plot,
        anomaly_type=anomaly["type"],
        severity=anomaly["severity"],
        model_confidence=anomaly["confidence"],
        related_reading=instance
    )
