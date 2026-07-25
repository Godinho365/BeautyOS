"""Módulo staff — Profissionais.

`Professional` é a pessoa que presta serviços (cabeleireiro, manicure, esteticista).
Entidade de negócio isolada por tenant (RLS). Ver docs/architecture/modules.md
(staff) e docs/glossary.md.
"""
from __future__ import annotations

from django.db import models

from apps.common.models import TenantScopedModel


class Professional(TenantScopedModel):
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    # Especialidade livre por ora; evoluirá para vínculo com o catálogo de serviços.
    specialty = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "staff_professional"
        indexes = [models.Index(fields=["tenant_id", "name"])]

    def __str__(self) -> str:
        return self.name
