"""Handlers de eventos do módulo marketing.

Consome `TicketClosed` e credita pontos de fidelidade ao Cliente. Idempotente
por `event_id`. Ver docs/architecture/events.md.
"""
from __future__ import annotations

import uuid

from apps.common.events import subscribe

from .services import earn_points_for_ticket


def on_ticket_closed(payload: dict, *, tenant_id: uuid.UUID, event_id: uuid.UUID) -> None:
    earn_points_for_ticket(
        tenant_id=tenant_id,
        customer_id=payload["customer_id"],
        total_cents=payload["total_cents"],
        event_id=event_id,
    )


def register() -> None:
    subscribe("TicketClosed", on_ticket_closed)
