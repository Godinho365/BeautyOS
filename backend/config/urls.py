"""Roteamento raiz. A API é versionada em /api/v1 (ver docs/api/api_guidelines.md)."""
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    """Liveness simples, sem autenticação e sem tenant."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health", health, name="health"),
    path("api/v1/", include("config.api_v1")),
]
