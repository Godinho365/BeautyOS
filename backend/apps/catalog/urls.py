"""Rotas do módulo catalog sob /api/v1/. Ver docs/api/api_guidelines.md."""
from rest_framework.routers import DefaultRouter

from .views import ServiceViewSet

router = DefaultRouter(trailing_slash=False)
router.register("services", ServiceViewSet, basename="service")

urlpatterns = router.urls
