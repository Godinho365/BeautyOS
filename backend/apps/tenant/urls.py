"""Rotas do módulo tenant sob /api/v1/. Ver docs/api/api_guidelines.md."""
from rest_framework.routers import DefaultRouter

from .views import BranchViewSet

router = DefaultRouter(trailing_slash=False)
router.register("branches", BranchViewSet, basename="branch")

urlpatterns = router.urls
