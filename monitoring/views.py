from rest_framework import viewsets, permissions
from .models import SensorReading, AnomalyEvent, AgentRecommendation,UserProfile
from .serializers import (
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer,UserProfileSerializer
)
from .permissions import *

from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models.functions import TruncHour
from django.db.models import Count

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]  # only logged in users can see profiles

# -------------------------------------------------------
# Sensor Readings (GET + POST)   ← teacher asked for this
# -------------------------------------------------------
class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all().order_by("-timestamp")
    serializer_class = SensorReadingSerializer
    permission_classes = [ReadOnlyOrFarmer]

    def get_queryset(self):
        qs = super().get_queryset()
        plot_id = self.request.query_params.get("plot")
        if plot_id:
            qs = qs.filter(plot_id=plot_id)
        return qs


# -------------------------------------------------------
# Anomalies (GET only)   ← teacher asked for GET list
# -------------------------------------------------------
class AnomalyEventViewSet(viewsets.ModelViewSet):
    queryset = AnomalyEvent.objects.all().order_by("-timestamp")
    serializer_class = AnomalyEventSerializer
    permission_classes = [IsAdminFarmerWorker]


# -------------------------------------------------------
# Recommendations (GET only)   ← teacher asked for GET list
# -------------------------------------------------------
class AgentRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentRecommendation.objects.all().order_by("-timestamp")
    serializer_class = AgentRecommendationSerializer
    permission_classes = [IsAdminFarmerWorker]

<<<<<<< HEAD

"""@api_view(['GET'])
def get_ml_metrics(request):
    # Count total anomalies detected
    total_anomalies = AnomalyEvent.objects.count()
    
    # Count anomalies linked to readings (true positives)
    tp = AnomalyEvent.objects.filter(related_reading__isnull=False).count()
    
    # Count all sensor readings
    total_readings = SensorReading.objects.count()
    
    # False positives = anomalies not linked to readings
    fp = total_anomalies - tp
    
    # Simple precision/recall computation (example)
    precision = tp / total_anomalies if total_anomalies else 0
    recall = tp / total_readings if total_readings else 0"""
=======
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_ml_metrics(request):
    total_anomalies = AnomalyEvent.objects.count()
    tp = AnomalyEvent.objects.count()
    total_readings = SensorReading.objects.count()
    fp = total_anomalies - tp
    precision = tp / total_anomalies if total_anomalies else 0
    recall = tp / total_anomalies if total_anomalies else 0
>>>>>>> main
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    false_positive_rate = fp / total_readings if total_readings else 0

    return Response({
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "false_positive_rate": false_positive_rate,
        "total_anomalies": total_anomalies,
        "true_positives": tp,
        "total_readings": total_readings   # ← ajouté
    })
def anomaly_curve(request):
    data = (
        AnomalyEvent.objects
        .annotate(hour=TruncHour("timestamp"))
        .values("hour")
        .annotate(count=Count("id"))
        .order_by("hour")
    )

    return Response([
        {
            "time": d["hour"].strftime("%H:%M"),
            "count": d["count"]
        }
        for d in data
    ])
