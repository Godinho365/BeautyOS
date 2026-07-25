"""Testes do módulo commissions — cálculo por regra e consumo de TicketClosed.

Requer PostgreSQL (RLS). Exercita também DOIS consumidores do mesmo evento
(inventory + commissions). Ver docs/architecture/events.md.
"""
from datetime import datetime, timezone

import pytest
from rest_framework.test import APIClient

from apps.common.outbox import process_pending
from apps.common.tenant_context import use_tenant
from apps.commissions.models import Commission, CommissionRule
from apps.crm.models import Customer
from apps.catalog.models import Service
from apps.identity.models import User
from apps.scheduling.services import book_appointment
from apps.staff.models import Professional
from apps.tenant.models import Company


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    with use_tenant(a.id):
        svc = Service.objects.create(tenant_id=a.id, name="Corte", duration_minutes=60)
        prof = Professional.objects.create(tenant_id=a.id, name="Ana")
        cust = Customer.objects.create(tenant_id=a.id, name="Cliente A")
        appt = book_appointment(
            tenant_id=a.id, customer_id=cust.id, professional_id=prof.id,
            service_id=svc.id, starts_at=datetime(2026, 8, 1, 10, tzinfo=timezone.utc),
        )
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id)
    return {"a": a, "prof": prof, "cust": cust, "appt": appt}


def _client(email):
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


@pytest.mark.django_db(transaction=True)
def test_ticket_closed_gera_comissao(cenario):
    a, prof, cust, appt = cenario["a"], cenario["prof"], cenario["cust"], cenario["appt"]
    client = _client("dono@a.com")
    # regra: 40% para a profissional
    client.post(
        "/api/v1/commission-rules",
        {"professional_id": str(prof.id), "percent_bps": 4000},
        format="json",
    )
    # comanda vinculada ao atendimento, total 100,00, paga e fechada
    tid = client.post(
        "/api/v1/tickets",
        {"customer_id": str(cust.id), "appointment_id": str(appt.id)},
        format="json",
    ).data["id"]
    client.post(f"/api/v1/tickets/{tid}/items", {"description": "Corte", "unit_price_cents": 10000}, format="json")
    client.post(f"/api/v1/tickets/{tid}/payments", {"amount_cents": 10000}, format="json")
    assert client.post(f"/api/v1/tickets/{tid}/close", {}, format="json").status_code == 200
    # relay despacha TicketClosed -> comissão de 40,00 (40% de 100,00)
    process_pending()
    with use_tenant(a.id):
        com = Commission.objects.get()
        assert com.professional_id == prof.id
        assert com.amount_cents == 4000
    # idempotência: reprocessar não duplica
    process_pending()
    with use_tenant(a.id):
        assert Commission.objects.count() == 1


@pytest.mark.django_db(transaction=True)
def test_sem_regra_comissao_zero(cenario):
    a, cust, appt = cenario["a"], cenario["cust"], cenario["appt"]
    client = _client("dono@a.com")
    tid = client.post(
        "/api/v1/tickets",
        {"customer_id": str(cust.id), "appointment_id": str(appt.id)},
        format="json",
    ).data["id"]
    client.post(f"/api/v1/tickets/{tid}/items", {"description": "Corte", "unit_price_cents": 10000}, format="json")
    client.post(f"/api/v1/tickets/{tid}/payments", {"amount_cents": 10000}, format="json")
    client.post(f"/api/v1/tickets/{tid}/close", {}, format="json")
    process_pending()
    with use_tenant(a.id):
        assert Commission.objects.get().amount_cents == 0


@pytest.mark.django_db(transaction=True)
def test_isola_regras_por_tenant(cenario):
    a = cenario["a"]
    b = Company.objects.create(name="Salão B")
    User.objects.create_user(email="dono@b.com", password="senha123", tenant_id=b.id)
    ca = _client("dono@a.com")
    ca.post("/api/v1/commission-rules", {"percent_bps": 3000}, format="json")  # regra padrão do A
    cb = _client("dono@b.com")
    assert len(cb.get("/api/v1/commission-rules").data) == 0  # B não vê a regra de A
