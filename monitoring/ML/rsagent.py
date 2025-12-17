import os
import django
from django.utils import timezone

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")
django.setup()

from monitoring.models import AnomalyEvent, AgentRecommendation

class RSAgent:
    """AI agent that generates recommendations for detected anomalies (Roxy the Watcher)."""
    
    def generate_recommendation(self, anomaly: AnomalyEvent):
        sensor = anomaly.related_reading.sensor_type if anomaly.related_reading else "unknown"
        plot = anomaly.plot.id

        # Map severity to action
        if anomaly.severity == "high":
            action = f"Immediate check required for plot {plot}: {sensor} anomaly detected."
        elif anomaly.severity == "medium":
            action = f"Monitor plot {plot} closely: {sensor} slightly abnormal."
        elif anomaly.severity == "low":
            action = f"Keep an eye on plot {plot}: {sensor} mildly unusual."
        else:
            action = f"No immediate action required for plot {plot}."

        explanation = (
            f"RSAgent Alert: {sensor} reading triggered a {anomaly.severity} anomaly "
            f"(z-score={anomaly.model_confidence:.2f})."
        )

        # Save recommendation in DB
        recommendation = AgentRecommendation.objects.create(
            anomaly_event=anomaly,
            recommended_action=action,
            explanation_text=explanation,
            confidence=abs(anomaly.model_confidence),
        )

        return recommendation

# ------------------------------
# Run the agent on existing anomalies
# ------------------------------
def main():
    agent = RSAgent()

    # Fetch anomalies without recommendation
    anomalies = AnomalyEvent.objects.filter(recommendation__isnull=True)

    for anomaly in anomalies:
        rec = agent.generate_recommendation(anomaly)
        print(f"[RSAGENT] {rec.explanation_text} -> {rec.recommended_action}")

if __name__ == "__main__":
    main()
