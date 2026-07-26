"""Contrato público do módulo catalog.

Outros módulos consultam serviços **por esta API**, sem importar o model ORM
`Service` diretamente (baixo acoplamento — ver docs/architecture/modules.md).
Retorna um DTO simples, não a entidade do ORM.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from .models import Service


@dataclass(frozen=True)
class ServiceInfo:
    id: uuid.UUID
    duration_minutes: int


def list_active_services(tenant_id: uuid.UUID) -> list[dict]:
    """Serviços ativos do tenant (para exibição pública no marketplace)."""
    return [
        {"id": str(s.id), "name": s.name, "duration_minutes": s.duration_minutes,
         "price_cents": s.price_cents}
        for s in Service.all_tenants.filter(tenant_id=tenant_id, is_active=True).order_by("name")
    ]


def get_service(tenant_id: uuid.UUID, service_id: uuid.UUID) -> ServiceInfo | None:
    """Serviço ativo do tenant, ou None. Filtra por tenant (RLS é a rede final)."""
    svc = (
        Service.all_tenants
        .filter(tenant_id=tenant_id, id=service_id, is_active=True)
        .only("id", "duration_minutes")
        .first()
    )
    return ServiceInfo(id=svc.id, duration_minutes=svc.duration_minutes) if svc else None
