"""Módulo marketplace — descoberta e agendamento público.

`MarketplaceProfile` é o perfil PÚBLICO (opt-in) de uma Empresa no marketplace.
É uma tabela **GLOBAL** (sem RLS): o diretório de empresas publicadas precisa ser
legível entre tenants (é o propósito do marketplace). Guarda `company_id` (o tenant)
e um `slug` para a URL pública. Ver docs/architecture/modules.md (marketplace).
"""
from __future__ import annotations

from django.db import models

from apps.common.models import UUIDModel


class MarketplaceProfile(UUIDModel):
    # 1 perfil por Empresa. company_id é o tenant_id da Empresa dona.
    company_id = models.UUIDField(unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    display_name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        db_table = "marketplace_profile"

    def __str__(self) -> str:
        return f"{self.slug} ({'público' if self.is_published else 'rascunho'})"
