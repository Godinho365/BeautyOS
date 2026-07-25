"""Registro das rotas do módulo notifications no router compartilhado da API v1."""
from .views import NotificationViewSet


def register(router):
    router.register("notifications", NotificationViewSet, basename="notification")
