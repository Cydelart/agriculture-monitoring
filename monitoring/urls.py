from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SensorReadingViewSet,
    AnomalyEventViewSet,
    AgentRecommendationViewSet,
    UserProfileViewSet,
       get_ml_metrics   )
from .views import anomaly_curve

router = DefaultRouter()
router.register("sensor-readings", SensorReadingViewSet, basename="sensor-reading")
router.register("anomalies", AnomalyEventViewSet, basename="anomaly")
router.register("recommendations", AgentRecommendationViewSet, basename="recommendation")
router.register("user-profiles", UserProfileViewSet, basename="user-profile")  

urlpatterns = [
    path("", include(router.urls)),
    path('ml-metrics/', get_ml_metrics),
    path("anomaly-curve/", anomaly_curve),
]
