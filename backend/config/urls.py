"""Roteamento raiz. A API é versionada em /api/v1 (ver docs/api/api_guidelines.md)."""
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(_request):
    """Liveness simples, sem autenticação e sem tenant."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health", health, name="health"),
    path("api/v1/", include("config.api_v1")),
    # Contrato OpenAPI + Swagger UI (ver docs/api/api_guidelines.md).
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
