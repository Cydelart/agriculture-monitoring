from rest_framework import viewsets, permissions
from .models import SensorReading, AnomalyEvent, AgentRecommendation, UserProfile
from .serializers import (
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer,
    UserProfileSerializer,
)
from .permissions import *


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


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


class AnomalyEventViewSet(viewsets.ModelViewSet):
    queryset = AnomalyEvent.objects.all().order_by("-timestamp")
    serializer_class = AnomalyEventSerializer
    permission_classes = [IsAdminFarmerWorker]


class AgentRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentRecommendation.objects.all().order_by("-timestamp")
    serializer_class = AgentRecommendationSerializer
    permission_classes = [IsAdminFarmerWorker]
