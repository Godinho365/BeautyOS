"""Casos de uso do módulo marketing (Service Layer).

`earn_points_for_ticket`: consumidor de `TicketClosed` — credita pontos de
fidelidade ao Cliente (1 ponto por real gasto). Idempotente por `source_event_id`.
"""
from __future__ import annotations

import uuid

from django.db import transaction

from .models import LoyaltyAccount, LoyaltyEntry

POINTS_PER_CENTS = 100  # 1 ponto por real (100 centavos)


def earn_points_for_ticket(
    *, tenant_id: uuid.UUID, customer_id: uuid.UUID, total_cents: int, event_id: uuid.UUID
) -> int:
    """Credita pontos ao cliente. Retorna os pontos creditados (0 se já processado)."""
    with transaction.atomic():
        if LoyaltyEntry.objects.filter(source_event_id=event_id).exists():
            return 0
        points = total_cents // POINTS_PER_CENTS
        if points <= 0:
            return 0
        account, _ = LoyaltyAccount.objects.get_or_create(
            customer_id=customer_id, defaults={"tenant_id": tenant_id}
        )
        LoyaltyEntry.objects.create(
            tenant_id=tenant_id, account=account, points=points,
            reason="earn", source_event_id=event_id,
        )
        account.points += points
        account.save(update_fields=["points", "updated_at"])
        return points
