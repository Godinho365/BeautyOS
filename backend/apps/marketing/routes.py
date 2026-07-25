"""Registro das rotas do módulo marketing no router compartilhado da API v1."""
from .views import CampaignViewSet, LoyaltyAccountViewSet


def register(router):
    router.register("campaigns", CampaignViewSet, basename="campaign")
    router.register("loyalty-accounts", LoyaltyAccountViewSet, basename="loyalty-account")
