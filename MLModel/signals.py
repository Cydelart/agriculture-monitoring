# core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import timedelta
import pandas as pd

from monitoring.models import SensorReading, AnomalyEvent
from MLModel.ML_Model import detect_all
from MLModel.ML_Model import sensor_dataframe

import logging
logger = logging.getLogger(__name__)

@receiver(post_save, sender=SensorReading)
def sensor_reading_post_save(sender, instance, created, **kwargs):

    if not created:
        return
    logger.info(f"📡 Signal received for reading {instance.id} "
                f"{instance.sensor_type}={instance.value} plot={instance.plot_id}")
    
    if instance.sensor_type != "humidity":
        print("attendre")
        return
    
    """short_window_start = instance.timestamp - timedelta(seconds=2)

    recent_qs = SensorReading.objects.filter(
        plot=instance.plot,
        timestamp__gte=short_window_start
    )

    sensor_types = set(recent_qs.values_list("sensor_type", flat=True))
    REQUIRED = {"moisture", "humidity", "temperature"}

    if not REQUIRED.issubset(sensor_types):
        logger.info("⏳ Waiting for full sensor triplet")
        return
    """

    #the readings of the same plot for the past 3 hours
    start_time = instance.timestamp - timedelta(hours=3)

    # Fetch readings for same plot
    qs = SensorReading.objects.filter(
        plot=instance.plot,
        timestamp__gte=start_time
    ).order_by("timestamp")

    """if qs.count() < 5:
        return  # not enough context"""

    # Convert to DataFrame
    data = []
    for r in qs:
        
        data.append({
            "timestamp": r.timestamp,
            "sensor_type": r.sensor_type,
            "value": r.value,
            "plot": r.plot
        })

    df = pd.DataFrame(data)
    print("===== df =====")
    print(df)
    df_final = sensor_dataframe(df,10) 

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    print("===== df_final =====")
    print(df_final)
    # Run ML
    anomalies = detect_all(df_final)
    print(anomalies)
    
    if not anomalies:
        print("pas d'anamolies")
        return

    

    for anomaly in anomalies:
        """try:
            plot_obj = FieldPlot.objects.get(name=anomaly["plot_name"])
        except FieldPlot.DoesNotExist:
            print(f"⚠ Plot {anomaly['plot_name']} not found")
            continue"""

        anomaly_event = AnomalyEvent.objects.create(
            plot=anomaly["plot"],
            anomaly_type=anomaly["anomaly_type"],
            severity=anomaly["severity"],
            model_confidence=anomaly["model_confidence"],
            related_reading=None
            # timestamp se remplit automatiquement avec auto_now_add
        )

        print(f"✅ Anomaly saved: {anomaly_event.anomaly_type} on plot {anomaly_event.plot}")
