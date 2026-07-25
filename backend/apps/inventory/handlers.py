"""Handlers de eventos do módulo inventory.

Consome `TicketClosed` e dá baixa no estoque dos produtos vendidos. Idempotente
(a baixa é guardada por `source_event_id`). Ver docs/architecture/events.md.
"""
from __future__ import annotations

import uuid

from apps.common.events import subscribe

from .services import apply_ticket_sale


def on_ticket_closed(payload: dict, *, tenant_id: uuid.UUID, event_id: uuid.UUID) -> None:
    apply_ticket_sale(tenant_id=tenant_id, ticket_id=payload["ticket_id"], event_id=event_id)


def register() -> None:
    subscribe("TicketClosed", on_ticket_closed)
