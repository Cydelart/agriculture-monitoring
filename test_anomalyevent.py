# extract_anomalies.py

import os
import django

# ⚠️ Ajuste le chemin vers ton projet si nécessaire
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agriculture_backend.settings")
django.setup()

from monitoring.models import AnomalyEvent

def main():
    anomalies = AnomalyEvent.objects.all().order_by('-id')  # ordre décroissant
    
    if not anomalies.exists():
        print("Aucune anomalie enregistrée.")
        return

    print(f"Total anomalies: {anomalies.count()}\n")
    for a in anomalies:
        print(f"ID: {a.id}")
        print(f"Plot: {a.plot.name}")
        print(f"Type: {a.anomaly_type}")
        print(f"Severity: {a.severity}")
        print(f"Confidence: {a.model_confidence}")
        print(f"Timestamp of related reading: {a.related_reading.timestamp}")
        print("-" * 40)

if __name__ == "__main__":
    main()
