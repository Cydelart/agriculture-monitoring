from rest_framework import viewsets, permissions
from .models import SensorReading, AnomalyEvent, AgentRecommendation,UserProfile
from .serializers import (
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer,UserProfileSerializer
)
from .permissions import *
from rest_framework.decorators import api_view
from rest_framework.response import Response

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


@api_view(['GET'])
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
    recall = tp / total_readings if total_readings else 0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    false_positive_rate = fp / total_readings if total_readings else 0

    return Response({
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "false_positive_rate": false_positive_rate
    })