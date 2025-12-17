from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('farmer', 'Farmer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Farmer')
    def __str__(self):
        return f"{self.user.username} ({self.role})"



class FarmProfile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="farms")
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    size_hectares = models.FloatField()
    crop_type = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class FieldPlot(models.Model):
    farm = models.ForeignKey(FarmProfile, on_delete=models.CASCADE, related_name="plots")
    name = models.CharField(max_length=100)
    crop_variety = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.farm.name}"


class SensorReading(models.Model):
    SENSOR_TYPES = [
        ("moisture", "Soil Moisture"),
        ("temperature", "Air Temperature"),
        ("humidity", "Humidity"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name="readings")
    sensor_type = models.CharField(max_length=20, choices=SENSOR_TYPES)
    value = models.FloatField()
    source = models.CharField(max_length=30, default="simulator")

    def __str__(self):
        return f"{self.sensor_type}={self.value} ({self.plot.name})"


class AnomalyEvent(models.Model):
    SEVERITY_LEVELS = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    plot = models.ForeignKey(FieldPlot, on_delete=models.CASCADE, related_name="anomalies")
    anomaly_type = models.CharField(max_length=50)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS)
    model_confidence = models.FloatField()
    related_reading = models.ForeignKey(
        SensorReading, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="anomaly_events"
    )

    def __str__(self):
        return f"{self.anomaly_type} ({self.severity})"

#recommendation par l'ia
class AgentRecommendation(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    anomaly_event = models.OneToOneField(
        AnomalyEvent, on_delete=models.CASCADE, related_name="recommendation"
    )
    recommended_action = models.TextField()
    explanation_text = models.TextField()
    confidence = models.FloatField()

    def __str__(self):
        return f"Recommendation for {self.anomaly_event_id}"
