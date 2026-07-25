"""Registro das rotas do módulo commissions no router compartilhado da API v1."""
from .views import CommissionRuleViewSet, CommissionViewSet


def register(router):
    router.register("commission-rules", CommissionRuleViewSet, basename="commission-rule")
    router.register("commissions", CommissionViewSet, basename="commission")
