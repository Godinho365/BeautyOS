"""Registro das rotas do módulo finance no router compartilhado da API v1."""
from .views import TicketViewSet


def register(router):
    router.register("tickets", TicketViewSet, basename="ticket")
