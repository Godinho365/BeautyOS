"""Contrato público do módulo scheduling.

Outros módulos verificam agendamentos **por esta API**, sem importar o model ORM
`Appointment` (baixo acoplamento — ver docs/architecture/modules.md).
"""
from __future__ import annotations

import uuid

from .models import Appointment


def appointment_exists(tenant_id: uuid.UUID, appointment_id: uuid.UUID) -> bool:
    """True se o agendamento existe e pertence ao tenant."""
    return Appointment.all_tenants.filter(tenant_id=tenant_id, id=appointment_id).exists()
