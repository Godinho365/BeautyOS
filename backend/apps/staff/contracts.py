"""Contrato público do módulo staff.

Outros módulos verificam profissionais **por esta API**, sem importar o model
ORM `Professional` (baixo acoplamento — ver docs/architecture/modules.md).
"""
from __future__ import annotations

import uuid

from .models import Professional


def professional_exists(tenant_id: uuid.UUID, professional_id: uuid.UUID) -> bool:
    """True se o profissional existe, é ativo e pertence ao tenant."""
    return (
        Professional.all_tenants
        .filter(tenant_id=tenant_id, id=professional_id, is_active=True)
        .exists()
    )
