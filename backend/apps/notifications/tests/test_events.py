"""Testes do fluxo de eventos: booking -> Outbox -> relay -> Notification.

Prova o Transactional Outbox (ADR-0005) ponta a ponta e a idempotência do
consumidor. Requer PostgreSQL (RLS). Ver docs/architecture/events.md.
"""
from datetime import datetime, timezone

import pytest

from apps.common.outbox import OutboxEvent, process_pending
from apps.common.tenant_context import use_tenant
from apps.catalog.models import Service
from apps.crm.models import Customer
from apps.notifications.handlers import on_appointment_booked
from apps.notifications.models import Notification
from apps.scheduling.services import book_appointment
from apps.staff.models import Professional
from apps.tenant.models import Company


def _dt(hour):
    return datetime(2026, 8, 1, hour, 0, tzinfo=timezone.utc)


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    with use_tenant(a.id):
        svc = Service.objects.create(tenant_id=a.id, name="Corte", duration_minutes=60)
        prof = Professional.objects.create(tenant_id=a.id, name="Ana")
        cust = Customer.objects.create(tenant_id=a.id, name="Cliente A")
    return {"a": a, "svc": svc, "prof": prof, "cust": cust}


@pytest.mark.django_db(transaction=True)
def test_agendamento_grava_evento_na_outbox(cenario):
    a = cenario["a"]
    with use_tenant(a.id):
        book_appointment(
            tenant_id=a.id, customer_id=cenario["cust"].id,
            professional_id=cenario["prof"].id, service_id=cenario["svc"].id,
            starts_at=_dt(10),
        )
    # Evento pendente gravado na mesma transação (outbox é infra, sem tenant scope).
    eventos = OutboxEvent.objects.filter(event_type="AppointmentBooked", status="pending")
    assert eventos.count() == 1


@pytest.mark.django_db(transaction=True)
def test_relay_cria_notificacao_e_marca_processado(cenario):
    a = cenario["a"]
    with use_tenant(a.id):
        book_appointment(
            tenant_id=a.id, customer_id=cenario["cust"].id,
            professional_id=cenario["prof"].id, service_id=cenario["svc"].id,
            starts_at=_dt(10),
        )
    assert process_pending() == 1
    assert OutboxEvent.objects.filter(status="processed").count() == 1
    with use_tenant(a.id):
        assert Notification.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_relay_e_handler_idempotentes(cenario):
    a = cenario["a"]
    with use_tenant(a.id):
        book_appointment(
            tenant_id=a.id, customer_id=cenario["cust"].id,
            professional_id=cenario["prof"].id, service_id=cenario["svc"].id,
            starts_at=_dt(10),
        )
    assert process_pending() == 1
    assert process_pending() == 0  # nada mais pendente
    # Reprocessar o MESMO evento (ex.: retry) não duplica a notificação.
    evt = OutboxEvent.objects.get(event_type="AppointmentBooked")
    with use_tenant(a.id):
        on_appointment_booked(evt.payload, tenant_id=a.id, event_id=evt.id)
        assert Notification.objects.count() == 1
