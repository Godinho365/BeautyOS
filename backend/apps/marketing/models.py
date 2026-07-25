"""Módulo marketing — campanhas e fidelidade.

- `Campaign`: campanha de marketing (stub inicial).
- `LoyaltyAccount`: saldo de pontos de fidelidade de um Cliente.
- `LoyaltyEntry`: lançamento de pontos (trilha; `source_event_id` = idempotência).

Isolados por tenant (RLS). Ver docs/architecture/modules.md (marketing) e events.md.
"""
from __future__ import annotations

from django.db import models

from apps.common.models import TenantScopedModel


class Campaign(TenantScopedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "marketing_campaign"
        indexes = [models.Index(fields=["tenant_id", "name"])]

    def __str__(self) -> str:
        return self.name


class LoyaltyAccount(TenantScopedModel):
    customer_id = models.UUIDField()
    points = models.IntegerField(default=0)

    class Meta:
        db_table = "marketing_loyalty_account"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "customer_id"], name="uniq_loyalty_account_customer"
            )
        ]


class LoyaltyEntry(TenantScopedModel):
    account = models.ForeignKey(LoyaltyAccount, related_name="entries", on_delete=models.CASCADE)
    points = models.IntegerField()
    reason = models.CharField(max_length=40, default="earn")
    source_event_id = models.UUIDField(null=True, blank=True)

    class Meta:
        db_table = "marketing_loyalty_entry"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant_id", "source_event_id"], name="uniq_loyalty_entry_source_event"
            )
        ]
