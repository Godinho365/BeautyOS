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


def customers_count(tenant_id: uuid.UUID) -> int:
    """Total de clientes do tenant."""
    return Customer.all_tenants.filter(tenant_id=tenant_id).count()


def get_or_create_customer(tenant_id: uuid.UUID, name: str, phone: str = "") -> uuid.UUID:
    """Retorna o id de um Cliente (cria se não existir por telefone). Usado no
    booking público do marketplace."""
    qs = Customer.all_tenants.filter(tenant_id=tenant_id)
    existing = qs.filter(phone=phone).first() if phone else None
    if existing:
        return existing.id
    customer = Customer.all_tenants.create(tenant_id=tenant_id, name=name, phone=phone)
    return customer.id
