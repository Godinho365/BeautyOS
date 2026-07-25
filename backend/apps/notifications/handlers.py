"""Handlers de eventos do módulo notifications.

Consome `AppointmentBooked` e registra uma notificação de confirmação. É
**idempotente**: reprocessar o mesmo evento não duplica (get_or_create por
source_event_id). Ver docs/architecture/events.md.
"""
from __future__ import annotations

import uuid

from apps.common.events import subscribe

from .models import Notification


def on_appointment_booked(payload: dict, *, tenant_id: uuid.UUID, event_id: uuid.UUID) -> None:
    Notification.objects.get_or_create(
        source_event_id=event_id,
        defaults={
            "tenant_id": tenant_id,
            "channel": "email",
            "to": str(payload.get("customer_id", "")),
            "message": f"Agendamento {payload.get('appointment_id')} confirmado.",
        },
    )


def register() -> None:
    subscribe("AppointmentBooked", on_appointment_booked)
