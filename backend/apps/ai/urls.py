"""Rotas do módulo ai sob /api/v1/ai/. Ver docs/ai/copilot.md."""
from django.urls import path

from .views import InsightsView

urlpatterns = [
    path("insights", InsightsView.as_view(), name="ai-insights"),
]
