"""Contrato público do módulo inventory.

Exposto para consumo por outros módulos (ex.: ai/Copilot) sem acoplar ao ORM.
Ver docs/architecture/modules.md.
"""
from __future__ import annotations

import uuid

from .models import Product

LOW_STOCK_THRESHOLD = 5


def low_stock_count(tenant_id: uuid.UUID, threshold: int = LOW_STOCK_THRESHOLD) -> int:
    """Quantos produtos estão com saldo <= threshold."""
    return Product.all_tenants.filter(tenant_id=tenant_id, quantity__lte=threshold).count()
