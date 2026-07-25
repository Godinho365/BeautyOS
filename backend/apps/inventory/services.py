"""Casos de uso do módulo inventory (Service Layer).

- `adjust_stock`: entrada/saída manual, com invariante de saldo não-negativo.
- `apply_ticket_sale`: consumidor de `TicketClosed` — baixa o estoque dos produtos
  vendidos na comanda. Idempotente por `source_event_id` (at-least-once).
"""
from __future__ import annotations

import uuid

from django.db import transaction

from apps.finance.contracts import get_product_lines

from .models import Product, StockMovement


class InventoryError(Exception):
    """Base de erros do módulo inventory."""


class NegativeStockError(InventoryError):
    """Operação deixaria o saldo negativo."""


def adjust_stock(
    *, tenant_id: uuid.UUID, product_id: uuid.UUID, delta: int,
    reason: str = "manual", source_event_id: uuid.UUID | None = None,
) -> Product:
    with transaction.atomic():
        product = Product.objects.select_for_update().filter(id=product_id).first()
        if product is None:
            raise InventoryError("Produto inexistente.")
        new_qty = product.quantity + delta
        if new_qty < 0:
            raise NegativeStockError("Saldo insuficiente em estoque.")
        StockMovement.objects.create(
            tenant_id=tenant_id, product=product, delta=delta,
            reason=reason, source_event_id=source_event_id,
        )
        product.quantity = new_qty
        product.save(update_fields=["quantity", "updated_at"])
    return product


def apply_ticket_sale(*, tenant_id: uuid.UUID, ticket_id: uuid.UUID, event_id: uuid.UUID) -> int:
    """Dá baixa nos produtos vendidos na comanda. Idempotente por event_id.

    Retorna quantos produtos tiveram baixa. Produtos não cadastrados no estoque
    são ignorados (a comanda pode referenciar itens não controlados).
    """
    # Idempotência: se já processamos este evento, não repete.
    if StockMovement.objects.filter(source_event_id=event_id).exists():
        return 0
    baixados = 0
    for line in get_product_lines(tenant_id, ticket_id):
        product = Product.objects.filter(id=line.product_id).first()
        if product is None:
            continue
        adjust_stock(
            tenant_id=tenant_id, product_id=line.product_id, delta=-line.quantity,
            reason="sale", source_event_id=event_id,
        )
        baixados += 1
    return baixados
