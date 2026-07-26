"""Casos de uso do marketplace (Service Layer).

O booking público identifica o tenant pelo `slug` (não por JWT) e opera dentro de
`use_tenant(company_id)` para que a RLS e as regras de negócio (não-sobreposição)
valham normalmente. Ver docs/architecture/multi-tenant.md e modules.md.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from apps.common.tenant_context import use_tenant
from apps.crm.contracts import get_or_create_customer
from apps.scheduling.services import book_appointment

from .models import MarketplaceProfile


def upsert_profile(
    *, tenant_id: uuid.UUID, slug: str, display_name: str,
    bio: str = "", is_published: bool = False,
) -> MarketplaceProfile:
    profile, _ = MarketplaceProfile.objects.update_or_create(
        company_id=tenant_id,
        defaults={"slug": slug, "display_name": display_name, "bio": bio,
                  "is_published": is_published},
    )
    return profile


def public_book(
    *, profile: MarketplaceProfile, customer_name: str, phone: str,
    professional_id: uuid.UUID, service_id: uuid.UUID, starts_at: datetime,
):
    """Agenda publicamente para a Empresa do perfil. Roda no contexto do tenant."""
    tenant_id = profile.company_id
    with use_tenant(tenant_id):
        customer_id = get_or_create_customer(tenant_id, customer_name, phone)
        return book_appointment(
            tenant_id=tenant_id, customer_id=customer_id,
            professional_id=professional_id, service_id=service_id, starts_at=starts_at,
        )
