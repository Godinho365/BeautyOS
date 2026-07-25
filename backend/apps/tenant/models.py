"""Módulo tenant — Empresas (tenants) e suas Unidades/Filiais.

- `Company` é uma tabela GLOBAL: cada linha É um tenant (seu `id` é o `tenant_id`
  usado pelas entidades de negócio). Não é isolada por RLS.
- `Branch` (Unidade/Filial) é uma entidade de NEGÓCIO isolada por RLS — o recurso
  usado para demonstrar o isolamento ponta a ponta.

Ver docs/architecture/modules.md (tenant) e docs/glossary.md.
"""
from __future__ import annotations

from django.db import models

from apps.common.models import TenantScopedModel, UUIDModel


class Company(UUIDModel):
    """Empresa cliente do BeautyOS. `id` é o identificador do tenant."""

    name = models.CharField(max_length=200)

    class Meta:
        db_table = "tenant_company"

    def __str__(self) -> str:
        return self.name


class Branch(TenantScopedModel):
    """Unidade/Filial de uma Empresa. Isolada por tenant (RLS)."""

    name = models.CharField(max_length=200)

    class Meta:
        db_table = "tenant_branch"
        indexes = [models.Index(fields=["tenant_id", "name"])]
        verbose_name_plural = "branches"

    def __str__(self) -> str:
        return self.name
