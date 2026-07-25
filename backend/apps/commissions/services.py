"""Casos de uso do módulo commissions (Service Layer).

Consumidor de `TicketClosed`: calcula a comissão do profissional que realizou o
atendimento (obtido do agendamento vinculado à comanda). Idempotente por
`source_event_id`. Ver docs/architecture/events.md.
"""
from __future__ import annotations

import uuid

from django.db import transaction

from apps.scheduling.contracts import get_professional_id

from .models import Commission, CommissionRule

DEFAULT_PERCENT_BPS = 0  # sem regra cadastrada => comissão zero (explícito)


def rate_for(tenant_id: uuid.UUID, professional_id: uuid.UUID) -> int:
    """Percentual (bps): regra do profissional, senão a padrão do tenant, senão 0."""
    rules = {
        r.professional_id: r.percent_bps
        for r in CommissionRule.objects.filter(
            professional_id__in=[professional_id, None]
        )
    }
    if professional_id in rules:
        return rules[professional_id]
    return rules.get(None, DEFAULT_PERCENT_BPS)


def record_commission_for_ticket(
    *, tenant_id: uuid.UUID, ticket_id: uuid.UUID, total_cents: int,
    appointment_id: uuid.UUID | None, event_id: uuid.UUID,
) -> Commission | None:
    """Gera a comissão da comanda fechada. Idempotente; retorna None se não aplicável."""
    if not appointment_id:
        return None  # sem atendimento vinculado, não há a quem atribuir
    with transaction.atomic():
        if Commission.objects.filter(source_event_id=event_id).exists():
            return None
        professional_id = get_professional_id(tenant_id, appointment_id)
        if professional_id is None:
            return None
        percent_bps = rate_for(tenant_id, professional_id)
        amount = total_cents * percent_bps // 10000
        return Commission.objects.create(
            tenant_id=tenant_id, professional_id=professional_id, ticket_id=ticket_id,
            base_cents=total_cents, percent_bps=percent_bps, amount_cents=amount,
            source_event_id=event_id,
        )
