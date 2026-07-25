"""Modelos-base compartilhados entre os módulos.

`TenantScopedModel` é a base de TODA entidade de negócio: carrega `tenant_id`,
timestamps de auditoria e um manager que já filtra pelo tenant corrente.
Ver docs/architecture/multi-tenant.md e docs/database/modeling.md.
"""
from __future__ import annotations

import uuid

from django.db import models

from .tenant_context import get_current_tenant


class UUIDModel(models.Model):
    """PK UUID + timestamps de auditoria (não escopado por tenant)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TenantScopedManager(models.Manager):
    """Manager que restringe as queries ao tenant corrente (defesa em app).

    A RLS no banco é a rede de segurança final; este filtro é a primeira camada
    (ver docs/architecture/multi-tenant.md — defesa em profundidade).
    """

    def get_queryset(self):
        qs = super().get_queryset()
        tenant_id = get_current_tenant()
        if tenant_id is None:
            # Sem tenant no contexto: não retorna nada de entidades escopadas.
            return qs.none()
        return qs.filter(tenant_id=tenant_id)


class TenantScopedModel(UUIDModel):
    """Base de toda entidade de negócio, isolada por Empresa (tenant)."""

    tenant_id = models.UUIDField(db_index=True, editable=False)

    # Manager default já escopado; `all_tenants` para operações administrativas.
    objects = TenantScopedManager()
    all_tenants = models.Manager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.tenant_id is None:
            current = get_current_tenant()
            if current is not None:
                self.tenant_id = current
        super().save(*args, **kwargs)
