"""Testes do módulo marketing — fidelidade ao fechar comanda e campanhas.

Requer PostgreSQL (RLS). O `TicketClosed` agora tem TRÊS consumidores
(estoque, comissões, fidelidade). Ver docs/architecture/events.md.
"""
import pytest
from rest_framework.test import APIClient

from apps.common.outbox import process_pending
from apps.common.tenant_context import use_tenant
from apps.crm.models import Customer
from apps.identity.models import User
from apps.marketing.models import Campaign, LoyaltyAccount
from apps.tenant.models import Company


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    with use_tenant(a.id):
        cust = Customer.objects.create(tenant_id=a.id, name="Cliente A")
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id, role="owner")
    return {"a": a, "cust": cust}


def _client(email):
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


@pytest.mark.django_db(transaction=True)
def test_fechar_comanda_credita_pontos(cenario):
    a, cust = cenario["a"], cenario["cust"]
    client = _client("dono@a.com")
    tid = client.post("/api/v1/tickets", {"customer_id": str(cust.id)}, format="json").data["id"]
    client.post(f"/api/v1/tickets/{tid}/items", {"description": "Corte", "unit_price_cents": 8000}, format="json")
    client.post(f"/api/v1/tickets/{tid}/payments", {"amount_cents": 8000}, format="json")
    assert client.post(f"/api/v1/tickets/{tid}/close", {}, format="json").status_code == 200
    # relay -> fidelidade credita 80 pontos (R$ 80,00)
    process_pending()
    with use_tenant(a.id):
        acc = LoyaltyAccount.objects.get(customer_id=cust.id)
        assert acc.points == 80
    # idempotência: reprocessar não credita de novo
    process_pending()
    with use_tenant(a.id):
        assert LoyaltyAccount.objects.get(customer_id=cust.id).points == 80


@pytest.mark.django_db(transaction=True)
def test_campanha_crud_isolado_por_tenant(cenario):
    ca = _client("dono@a.com")
    r = ca.post("/api/v1/campaigns", {"name": "Promo Verão"}, format="json")
    assert r.status_code == 201, r.content
    assert {c["name"] for c in ca.get("/api/v1/campaigns").data["results"]} == {"Promo Verão"}

    b = Company.objects.create(name="Salão B")
    User.objects.create_user(email="dono@b.com", password="senha123", tenant_id=b.id, role="owner")
    cb = _client("dono@b.com")
    assert cb.get("/api/v1/campaigns").data["results"] == []  # B não vê campanha de A
