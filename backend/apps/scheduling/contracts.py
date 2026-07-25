"""Contrato público do módulo scheduling.

Outros módulos verificam agendamentos **por esta API**, sem importar o model ORM
`Appointment` (baixo acoplamento — ver docs/architecture/modules.md).
"""
from __future__ import annotations

import uuid

from django.utils import timezone

from .models import Appointment


def appointment_exists(tenant_id: uuid.UUID, appointment_id: uuid.UUID) -> bool:
    """True se o agendamento existe e pertence ao tenant."""
    return Appointment.all_tenants.filter(tenant_id=tenant_id, id=appointment_id).exists()


def get_professional_id(tenant_id: uuid.UUID, appointment_id: uuid.UUID) -> uuid.UUID | None:
    """Profissional do agendamento, ou None."""
    return (
        Appointment.all_tenants
        .filter(tenant_id=tenant_id, id=appointment_id)
        .values_list("professional_id", flat=True)
        .first()
    )


def appointments_today_count(tenant_id: uuid.UUID) -> int:
    """Quantidade de agendamentos ativos de hoje."""
    today = timezone.localdate()
    return Appointment.all_tenants.filter(
        tenant_id=tenant_id, status=Appointment.Status.BOOKED, starts_at__date=today
    ).count()
