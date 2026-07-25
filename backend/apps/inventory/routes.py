"""Registro das rotas do módulo inventory no router compartilhado da API v1."""
from .views import ProductViewSet


def register(router):
    router.register("products", ProductViewSet, basename="product")
