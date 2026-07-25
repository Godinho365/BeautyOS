"""Registro das rotas do módulo catalog no router compartilhado da API v1.

Ver docs/api/api_guidelines.md.
"""
from .views import ServiceViewSet


def register(router):
    router.register("services", ServiceViewSet, basename="service")
