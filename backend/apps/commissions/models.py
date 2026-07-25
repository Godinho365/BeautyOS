"""Módulo commissions — comissões de profissionais.

- `CommissionRule`: percentual (em basis points) por profissional; a regra com
  `professional_id` nulo é o padrão do tenant.
- `Commission`: comissão gerada ao fechar uma comanda (consumo de `TicketClosed`).

Isolados por tenant (RLS). Valores em centavos. Ver docs/architecture/modules.md
(commissions) e docs/architecture/events.md.
"""
from __future__ import annotations

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TenantScopedModel


class CommissionRule(TenantScopedModel):
    # professional_id nulo = regra padrão do tenant.
    professional_id = models.UUIDField(null=True, blank=True)
    percent_bps = models.PositiveIntegerField(  # 4000 = 40,00%
        validators=[MinValueValidator(0), MaxValueValidator(10000)]
    )

    class Meta:
        db_table = "commissions_rule"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "professional_id"],
                name="uniq_commission_rule_prof",
            )
        ]


class Commission(TenantScopedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        PAID = "paid", "Paga"

    professional_id = models.UUIDField()
    ticket_id = models.UUIDField()
    base_cents = models.BigIntegerField()
    percent_bps = models.PositiveIntegerField()
    amount_cents = models.BigIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    source_event_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "commissions_commission"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "source_event_id"],
                name="uniq_commission_source_event",
            )
        ]
        indexes = [models.Index(fields=["tenant_id", "professional_id"])]
