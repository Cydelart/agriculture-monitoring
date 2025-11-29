from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SensorReadingViewSet,
    AnomalyEventViewSet,
    AgentRecommendationViewSet,
)

router = DefaultRouter()
router.register("sensor-readings", SensorReadingViewSet, basename="sensor-reading")
router.register("anomalies", AnomalyEventViewSet, basename="anomaly")
router.register("recommendations", AgentRecommendationViewSet, basename="recommendation")

urlpatterns = [
    path("", include(router.urls)),
]
