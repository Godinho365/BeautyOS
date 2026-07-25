"""Casos de uso do módulo scheduling (Service Layer — ver CODING_STANDARD).

`book_appointment` concentra a regra de negócio de agendar, incluindo a
invariante de **não-sobreposição por profissional**, aplicada em duas camadas:
  1. Checagem explícita na aplicação (erro 409 amigável).
  2. Constraint EXCLUDE no PostgreSQL como rede de segurança contra corridas.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from django.db import IntegrityError, transaction

from apps.catalog.contracts import get_service
from apps.common.outbox import record_event
from apps.crm.contracts import customer_exists
from apps.staff.contracts import professional_exists

from .models import Appointment


class BookingError(Exception):
    """Base de erros de agendamento."""


class InvalidBookingError(BookingError):
    """Referência inválida (serviço/profissional inexistente)."""


class OverlapError(BookingError):
    """Conflito de horário para o profissional."""


def book_appointment(
    *,
    tenant_id: uuid.UUID,
    customer_id: uuid.UUID,
    professional_id: uuid.UUID,
    service_id: uuid.UUID,
    starts_at: datetime,
) -> Appointment:
    service = get_service(tenant_id, service_id)
    if service is None:
        raise InvalidBookingError("Serviço inexistente ou inativo.")
    if not professional_exists(tenant_id, professional_id):
        raise InvalidBookingError("Profissional inexistente ou inativo.")
    if not customer_exists(tenant_id, customer_id):
        raise InvalidBookingError("Cliente inexistente.")

    ends_at = starts_at + timedelta(minutes=service.duration_minutes)

    # Camada 1 — checagem de sobreposição (intervalos [starts_at, ends_at)).
    conflito = (
        Appointment.objects
        .filter(
            professional_id=professional_id,
            status=Appointment.Status.BOOKED,
            starts_at__lt=ends_at,
            ends_at__gt=starts_at,
        )
        .exists()
    )
    if conflito:
        raise OverlapError("Já existe agendamento nesse horário para o profissional.")

    # Camada 2 — o INSERT roda em savepoint: se o constraint EXCLUDE barrar (corrida),
    # revertemos só o savepoint e devolvemos conflito, sem quebrar a transação da requisição.
    try:
        with transaction.atomic():
            appointment = Appointment.objects.create(
                tenant_id=tenant_id,
                customer_id=customer_id,
                professional_id=professional_id,
                service_id=service_id,
                starts_at=starts_at,
                ends_at=ends_at,
            )
            # Outbox: evento gravado na MESMA transação do agendamento (ADR-0005).
            record_event(
                "AppointmentBooked",
                {
                    "appointment_id": str(appointment.id),
                    "customer_id": str(customer_id),
                    "professional_id": str(professional_id),
                    "service_id": str(service_id),
                    "starts_at": starts_at.isoformat(),
                },
                tenant_id=tenant_id,
            )
            return appointment
    except IntegrityError as exc:
        raise OverlapError("Conflito de horário detectado.") from exc
