"""Módulo crm — Clientes finais.

`Customer` é o consumidor que a Empresa atende (distinto de `User`, que é quem
acessa o sistema). Entidade de negócio isolada por tenant (RLS). Ver
docs/architecture/modules.md (crm) e docs/glossary.md.
"""
from __future__ import annotations

from django.db import models

from apps.common.models import TenantScopedModel


class Customer(TenantScopedModel):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        db_table = "crm_customer"
        indexes = [models.Index(fields=["tenant_id", "name"])]

    def __str__(self) -> str:
        return self.name
