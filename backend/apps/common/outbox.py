"""Transactional Outbox (ADR-0005 / docs/architecture/events.md).

`OutboxEvent` é gravado na MESMA transação do agregado (ex.: um Appointment),
garantindo que o evento só existe se o dado de negócio commitou. O relay
`process_pending` lê os pendentes e despacha aos handlers registrados
(events.py), com semântica at-least-once — consumidores devem ser idempotentes.

`OutboxEvent` é uma tabela de INFRAESTRUTURA (sem RLS): o relay é um processo de
sistema que percorre eventos de todos os tenants. Ao despachar, o relay entra no
contexto do tenant do evento, de modo que os handlers gravam dados isolados (RLS).
"""
from __future__ import annotations

import uuid

from django.db import models, transaction
from django.utils import timezone

from . import events
from .tenant_context import get_current_tenant, use_tenant


class OutboxEvent(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        PROCESSED = "processed", "Processado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    occurred_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    class Meta:
        db_table = "common_outbox_event"
        indexes = [models.Index(fields=["status", "occurred_at"])]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.status})"


def record_event(event_type: str, payload: dict, *, tenant_id: uuid.UUID | None = None) -> OutboxEvent:
    """Grava um evento na outbox. Deve rodar DENTRO da transação do agregado."""
    return OutboxEvent.objects.create(
        tenant_id=tenant_id or get_current_tenant(),
        event_type=event_type,
        payload=payload,
    )


def process_pending(limit: int = 100) -> int:
    """Despacha eventos pendentes aos handlers. Retorna quantos processou.

    Cada evento é processado no contexto do seu tenant (para a RLS valer nos
    handlers) e marcado como processado na mesma transação.
    """
    pendentes = list(
        OutboxEvent.objects.filter(status=OutboxEvent.Status.PENDING).order_by("occurred_at")[:limit]
    )
    processados = 0
    for evt in pendentes:
        with transaction.atomic():
            with use_tenant(evt.tenant_id):
                events.dispatch(evt.event_type, evt.payload, tenant_id=evt.tenant_id, event_id=evt.id)
            evt.status = OutboxEvent.Status.PROCESSED
            evt.processed_at = timezone.now()
            evt.save(update_fields=["status", "processed_at"])
        processados += 1
    return processados
