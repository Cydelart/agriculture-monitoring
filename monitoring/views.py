from rest_framework import viewsets, permissions
from .models import SensorReading, AnomalyEvent, AgentRecommendation
from .serializers import (
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer,
)
from .permissions import ReadOnlyOrFarmer, IsAdminFarmerWorker

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
class AnomalyEventViewSet(viewsets.ReadOnlyModelViewSet):
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
