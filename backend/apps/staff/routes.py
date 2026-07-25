"""Registro das rotas do módulo staff no router compartilhado da API v1.

Ver docs/api/api_guidelines.md.
"""
from .views import ProfessionalViewSet


def register(router):
    router.register("professionals", ProfessionalViewSet, basename="professional")
