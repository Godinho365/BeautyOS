"""Handlers de eventos do módulo commissions.

Consome `TicketClosed` e gera a comissão do profissional do atendimento.
Idempotente por `event_id`. Ver docs/architecture/events.md.
"""
from __future__ import annotations

import uuid

from apps.common.events import subscribe

from .services import record_commission_for_ticket


def on_ticket_closed(payload: dict, *, tenant_id: uuid.UUID, event_id: uuid.UUID) -> None:
    record_commission_for_ticket(
        tenant_id=tenant_id,
        ticket_id=payload["ticket_id"],
        total_cents=payload["total_cents"],
        appointment_id=payload.get("appointment_id"),
        event_id=event_id,
    )


def register() -> None:
    subscribe("TicketClosed", on_ticket_closed)
