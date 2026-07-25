"""Módulo notifications — envio de mensagens (e-mail, SMS, push, WhatsApp).

`Notification` é o registro de uma notificação a enviar/enviada, isolado por
tenant (RLS). Neste skeleton, o "envio" é apenas registrado. `source_event_id`
liga a notificação ao evento de origem e garante idempotência do consumidor.
Ver docs/architecture/modules.md (notifications) e docs/architecture/events.md.
"""
from __future__ import annotations

from django.db import models

from apps.common.models import TenantScopedModel


class Notification(TenantScopedModel):
    channel = models.CharField(max_length=20, default="email")
    to = models.CharField(max_length=200)
    message = models.TextField()
    # Idempotência: um evento de origem gera no máximo uma notificação por tenant.
    source_event_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, default="sent")

    class Meta:
        db_table = "notifications_notification"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "source_event_id"],
                name="uniq_notification_source_event",
            )
        ]

    def __str__(self) -> str:
        return f"{self.channel} -> {self.to}"
