"""Módulo catalog — Catálogo de Serviços.

`Service` é o item ofertado (corte, manicure, coloração), com duração e preço.
Entidade de negócio isolada por tenant (RLS). Ver docs/architecture/modules.md
(catalog) e docs/glossary.md.
"""
from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TenantScopedModel


class Service(TenantScopedModel):
    """Serviço ofertado pela Empresa.

    Preço em centavos (inteiro) + moeda — nunca float, conforme
    docs/database/modeling.md.
    """

    name = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_cents = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default="BRL")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "catalog_service"
        indexes = [models.Index(fields=["tenant_id", "name"])]

    def __str__(self) -> str:
        return self.name
