"""Contrato público do módulo finance.

Outros módulos consultam dados de comanda **por esta API**, sem importar os
models ORM (baixo acoplamento — ver docs/architecture/modules.md).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from django.db.models import Sum
from django.utils import timezone

from .models import Ticket, TicketItem


@dataclass(frozen=True)
class ProductLine:
    product_id: uuid.UUID
    quantity: int


def get_product_lines(tenant_id: uuid.UUID, ticket_id: uuid.UUID) -> list[ProductLine]:
    """Itens de PRODUTO (product_id não nulo) de uma comanda, agrupáveis por consumidores."""
    rows = (
        TicketItem.all_tenants
        .filter(tenant_id=tenant_id, ticket_id=ticket_id, product_id__isnull=False)
        .values_list("product_id", "quantity")
    )
    return [ProductLine(product_id=pid, quantity=qty) for pid, qty in rows]


def revenue_today_cents(tenant_id: uuid.UUID) -> int:
    """Soma (centavos) das comandas fechadas hoje."""
    today = timezone.localdate()
    agg = (
        Ticket.all_tenants
        .filter(tenant_id=tenant_id, status=Ticket.Status.CLOSED, closed_at__date=today)
        .aggregate(total=Sum("total_cents"))
    )
    return agg["total"] or 0
