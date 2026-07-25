"""Módulo inventory — Estoque de produtos.

- `Product`: item físico com saldo (`quantity`), isolado por tenant (RLS).
- `StockMovement`: entrada/saída (delta) que altera o saldo; trilha auditável.
  `source_event_id` liga o movimento ao evento de origem (idempotência do consumidor).

Ver docs/architecture/modules.md (inventory) e docs/glossary.md.
"""
from __future__ import annotations

from django.db import models

from apps.common.models import TenantScopedModel


class Product(TenantScopedModel):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=60, blank=True)
    quantity = models.IntegerField(default=0)  # saldo atual

    class Meta:
        db_table = "inventory_product"
        indexes = [models.Index(fields=["tenant_id", "name"])]

    def __str__(self) -> str:
        return self.name


class StockMovement(TenantScopedModel):
    product = models.ForeignKey(Product, related_name="movements", on_delete=models.CASCADE)
    delta = models.IntegerField()  # + entrada, - saída
    reason = models.CharField(max_length=40, default="manual")
    source_event_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "inventory_stock_movement"
        indexes = [models.Index(fields=["tenant_id", "product"])]
