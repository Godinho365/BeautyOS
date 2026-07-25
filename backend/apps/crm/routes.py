"""Registro das rotas do módulo crm no router compartilhado da API v1."""
from .views import CustomerViewSet


def register(router):
    router.register("customers", CustomerViewSet, basename="customer")
