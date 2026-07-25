"""Contrato público do módulo crm.

Outros módulos verificam clientes **por esta API**, sem importar o model ORM
`Customer` (baixo acoplamento — ver docs/architecture/modules.md).
"""
from __future__ import annotations

import uuid

from .models import Customer


def customer_exists(tenant_id: uuid.UUID, customer_id: uuid.UUID) -> bool:
    """True se o cliente existe e pertence ao tenant."""
    return Customer.all_tenants.filter(tenant_id=tenant_id, id=customer_id).exists()
