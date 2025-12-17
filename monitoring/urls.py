from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import CustomTokenObtainPairView
from .views import (
    SensorReadingViewSet,
    AnomalyEventViewSet,
    AgentRecommendationViewSet,
    UserProfileViewSet,
)

router = DefaultRouter()
router.register("sensor-readings", SensorReadingViewSet)
router.register("anomalies", AnomalyEventViewSet)
router.register("recommendations", AgentRecommendationViewSet)
router.register("profiles", UserProfileViewSet)

urlpatterns = [
    path("token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]

