"""Agregador de rotas da API v1.

Cada módulo (bounded context) contribui com suas rotas aqui, mantendo o
versionamento único /api/v1. Ver docs/api/api_guidelines.md.
"""
from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.identity.urls")),
    path("", include("apps.tenant.urls")),
]
