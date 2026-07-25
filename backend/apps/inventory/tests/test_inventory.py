"""Testes do módulo inventory — ajuste de estoque, invariante e consumo de evento.

Requer PostgreSQL (RLS). Ver docs/architecture/events.md e multi-tenant.md.
"""
import pytest
from rest_framework.test import APIClient

from apps.common.outbox import process_pending
from apps.common.tenant_context import use_tenant
from apps.crm.models import Customer
from apps.identity.models import User
from apps.inventory.models import Product
from apps.tenant.models import Company


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    with use_tenant(a.id):
        prod = Product.objects.create(tenant_id=a.id, name="Shampoo", quantity=10)
        cust = Customer.objects.create(tenant_id=a.id, name="Cliente A")
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id, role="owner")
    return {"a": a, "prod": prod, "cust": cust}


def _client(email):
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


@pytest.mark.django_db(transaction=True)
def test_ajuste_de_estoque(cenario):
    client = _client("dono@a.com")
    pid = str(cenario["prod"].id)
    r = client.post(f"/api/v1/products/{pid}/adjust", {"delta": 5, "reason": "compra"}, format="json")
    assert r.status_code == 200, r.content
    assert r.data["quantity"] == 15


@pytest.mark.django_db(transaction=True)
def test_nao_permite_saldo_negativo(cenario):
    client = _client("dono@a.com")
    pid = str(cenario["prod"].id)
    r = client.post(f"/api/v1/products/{pid}/adjust", {"delta": -50}, format="json")
    assert r.status_code == 409, r.content


@pytest.mark.django_db(transaction=True)
def test_ticket_closed_baixa_estoque_e_idempotente(cenario):
    """Fluxo de evento: comanda com produto -> fecha -> relay -> baixa no estoque."""
    a, prod, cust = cenario["a"], cenario["prod"], cenario["cust"]
    client = _client("dono@a.com")
    # abre comanda, adiciona 3 unidades do produto, paga e fecha
    tid = client.post("/api/v1/tickets", {"customer_id": str(cust.id)}, format="json").data["id"]
    client.post(
        f"/api/v1/tickets/{tid}/items",
        {"description": "Shampoo", "unit_price_cents": 1000, "quantity": 3, "product_id": str(prod.id)},
        format="json",
    )
    client.post(f"/api/v1/tickets/{tid}/payments", {"amount_cents": 3000}, format="json")
    assert client.post(f"/api/v1/tickets/{tid}/close", {}, format="json").status_code == 200

    # antes do relay, estoque intacto
    with use_tenant(a.id):
        assert Product.objects.get(id=prod.id).quantity == 10
    # relay processa TicketClosed -> baixa 3
    assert process_pending() >= 1
    with use_tenant(a.id):
        assert Product.objects.get(id=prod.id).quantity == 7
    # reprocessar não baixa de novo (idempotência)
    process_pending()
    with use_tenant(a.id):
        assert Product.objects.get(id=prod.id).quantity == 7
