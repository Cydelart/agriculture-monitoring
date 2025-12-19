from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile, FarmProfile, FieldPlot, SensorReading, AnomalyEvent, AgentRecommendation

# Simple registration
admin.site.register(UserProfile)
admin.site.register(FarmProfile)
admin.site.register(FieldPlot)
admin.site.register(SensorReading)
admin.site.register(AnomalyEvent)
admin.site.register(AgentRecommendation)
