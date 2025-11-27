from rest_framework import viewsets, permissions
from .models import (
    FarmProfile,
    FieldPlot,
    SensorReading,
    AnomalyEvent,
    AgentRecommendation,
)
from .serializers import (
    FarmProfileSerializer,
    FieldPlotSerializer,
    SensorReadingSerializer,
    AnomalyEventSerializer,
    AgentRecommendationSerializer,
)


class FarmProfileViewSet(viewsets.ModelViewSet):
    queryset = FarmProfile.objects.all()
    serializer_class = FarmProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


class FieldPlotViewSet(viewsets.ModelViewSet):
    queryset = FieldPlot.objects.all()
    serializer_class = FieldPlotSerializer
    permission_classes = [permissions.IsAuthenticated]


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all().order_by("-timestamp")
    serializer_class = SensorReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        plot_id = self.request.query_params.get("plot")
        if plot_id:
            qs = qs.filter(plot_id=plot_id)
        return qs


class AnomalyEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnomalyEvent.objects.all().order_by("-timestamp")
    serializer_class = AnomalyEventSerializer
    permission_classes = [permissions.IsAuthenticated]


class AgentRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentRecommendation.objects.all().order_by("-timestamp")
    serializer_class = AgentRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
