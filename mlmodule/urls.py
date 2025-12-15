"""
URL configuration for ML Module (Iris + AgriBot)
"""
from django.urls import path
from . import views

app_name = 'mlmodule'

urlpatterns = [
    # Iris - Anomaly Detection
    path('detect/', views.batch_detect, name='batch_detect'),
    path('check/', views.check_reading, name='check_reading'),
    
    # AgriBot - AI Recommendations
    path('advice/', views.get_advice, name='get_advice'),
    path('recommend/', views.generate_recommendation_for_anomaly, name='generate_recommendation'),
]
