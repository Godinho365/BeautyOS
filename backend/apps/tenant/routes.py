"""Registro das rotas do módulo tenant no router compartilhado da API v1.

Ver docs/api/api_guidelines.md. O router é único (config/api_v1.py) para evitar
múltiplos registros de conversores de sufixo pelo DRF.
"""
from .views import BranchViewSet


def register(router):
    router.register("branches", BranchViewSet, basename="branch")
