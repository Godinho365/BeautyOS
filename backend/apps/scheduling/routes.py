"""Registro das rotas do módulo scheduling no router compartilhado da API v1.

Ver docs/api/api_guidelines.md.
"""
from .views import AppointmentViewSet


def register(router):
    router.register("appointments", AppointmentViewSet, basename="appointment")
