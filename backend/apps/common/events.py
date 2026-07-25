"""Registro de handlers de domain events (dispatch in-process).

No monólito modular, os consumidores de eventos são funções registradas aqui.
O relay do Outbox (outbox.py) chama `dispatch` para cada evento pendente.
Quando extrairmos serviços, este dispatch dá lugar a um broker externo — o
contrato do evento permanece. Ver docs/architecture/events.md e ADR-0005.
"""
from __future__ import annotations

import uuid
from collections import defaultdict
from typing import Callable

# handler(payload: dict, *, tenant_id: uuid.UUID, event_id: uuid.UUID) -> None
Handler = Callable[..., None]

_HANDLERS: dict[str, list[Handler]] = defaultdict(list)


def subscribe(event_type: str, handler: Handler) -> None:
    if handler not in _HANDLERS[event_type]:
        _HANDLERS[event_type].append(handler)


def dispatch(event_type: str, payload: dict, *, tenant_id: uuid.UUID, event_id: uuid.UUID) -> None:
    for handler in _HANDLERS.get(event_type, []):
        handler(payload, tenant_id=tenant_id, event_id=event_id)
