"""Módulo scheduling — Agenda/Booking.

`Appointment` reserva um Serviço (catalog) com um Profissional (staff) em uma
data/hora, para um Cliente. Referencia os outros contextos **por ID** (sem FK
entre módulos), conforme docs/architecture/modules.md.

Invariante central: um Profissional não pode ter dois agendamentos ativos
sobrepostos. Reforçada em duas camadas (ver services.py e a migração):
  1. Aplicação — use case `book_appointment` valida antes de gravar.
  2. Banco — constraint EXCLUDE (btree_gist) como rede de segurança.
"""
from __future__ import annotations

from django.db import models

from apps.common.models import TenantScopedModel


class Appointment(TenantScopedModel):
    class Status(models.TextChoices):
        BOOKED = "booked", "Agendado"
        CANCELLED = "cancelled", "Cancelado"

    # Cliente final: por ora denormalizado; evolui para FK ao módulo CRM (Customer).
    customer_name = models.CharField(max_length=200)
    # Referências por ID a outros bounded contexts (sem FK — baixo acoplamento).
    professional_id = models.UUIDField()
    service_id = models.UUIDField()
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.BOOKED)

    class Meta:
        db_table = "scheduling_appointment"
        indexes = [models.Index(fields=["tenant_id", "professional_id", "starts_at"])]

    def __str__(self) -> str:
        return f"{self.customer_name} @ {self.starts_at:%Y-%m-%d %H:%M}"
