from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import SensorReading, AnomalyEvent, AgentRecommendation, UserProfile
from .serializers import (
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer,
    UserProfileSerializer,
)
from .permissions import *

from mlmodule.iris_service import run_batch_detection


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



class AnomalyEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    - GET /anomalies/            -> list anomaly events
    - POST /anomalies/run-ml/   -> trigger ML batch inference
    """
    queryset = AnomalyEvent.objects.all().order_by("-timestamp")
    serializer_class = AnomalyEventSerializer
    permission_classes = [IsAdminFarmerWorker]

    @action(detail=False, methods=["post"], url_path="run-ml")
    def run_ml(self, request):
        minutes = int(request.data.get("minutes", 60))
        plot_id = request.data.get("plot_id", None)
        create_events = bool(request.data.get("create_events", True))

        results = run_batch_detection(
            plot_id=plot_id,        # None = ALL plots (your 3 models)
            minutes=minutes,
            create_events=create_events,
            no_duplicates=True,
        )

        return Response(results, status=status.HTTP_200_OK)



class AgentRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentRecommendation.objects.all().order_by("-timestamp")
    serializer_class = AgentRecommendationSerializer
    permission_classes = [IsAdminFarmerWorker]
