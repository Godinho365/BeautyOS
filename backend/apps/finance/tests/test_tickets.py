"""Testes do módulo finance — Comanda, invariantes e evento TicketClosed.

Requer PostgreSQL (RLS) e role não-superusuário. Ver
docs/testing/testing-strategy.md e docs/architecture/events.md.
"""
import pytest
from rest_framework.test import APIClient

from apps.common.outbox import OutboxEvent
from apps.common.tenant_context import use_tenant
from apps.crm.models import Customer
from apps.finance.models import Ticket
from apps.identity.models import User
from apps.tenant.models import Company


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    b = Company.objects.create(name="Salão B")
    with use_tenant(a.id):
        ca = Customer.objects.create(tenant_id=a.id, name="Cliente A")
    with use_tenant(b.id):
        cb = Customer.objects.create(tenant_id=b.id, name="Cliente B")
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id)
    User.objects.create_user(email="dono@b.com", password="senha123", tenant_id=b.id)
    return {"a": a, "b": b, "ca": ca, "cb": cb}


def _client(email):
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


def _open(client, customer):
    r = client.post("/api/v1/tickets", {"customer_id": str(customer.id)}, format="json")
    assert r.status_code == 201, r.content
    return r.data["id"]


@pytest.mark.django_db(transaction=True)
def test_fluxo_completo_abre_item_paga_fecha(cenario):
    client = _client("dono@a.com")
    tid = _open(client, cenario["ca"])
    # adiciona 2 itens (30,00 + 20,00 = 50,00)
    client.post(f"/api/v1/tickets/{tid}/items", {"description": "Corte", "unit_price_cents": 3000}, format="json")
    r = client.post(f"/api/v1/tickets/{tid}/items", {"description": "Barba", "unit_price_cents": 2000}, format="json")
    assert r.data["total_cents"] == 5000
    # paga o total
    client.post(f"/api/v1/tickets/{tid}/payments", {"amount_cents": 5000, "method": "pix"}, format="json")
    # fecha
    r = client.post(f"/api/v1/tickets/{tid}/close", {}, format="json")
    assert r.status_code == 200, r.content
    assert r.data["status"] == "closed"
    # evento TicketClosed foi para a outbox
    assert OutboxEvent.objects.filter(event_type="TicketClosed").count() == 1


@pytest.mark.django_db(transaction=True)
def test_nao_fecha_sem_pagamento_suficiente(cenario):
    client = _client("dono@a.com")
    tid = _open(client, cenario["ca"])
    client.post(f"/api/v1/tickets/{tid}/items", {"description": "Corte", "unit_price_cents": 5000}, format="json")
    client.post(f"/api/v1/tickets/{tid}/payments", {"amount_cents": 3000}, format="json")
    r = client.post(f"/api/v1/tickets/{tid}/close", {}, format="json")
    assert r.status_code == 409, r.content


@pytest.mark.django_db(transaction=True)
def test_nao_fecha_comanda_sem_itens(cenario):
    client = _client("dono@a.com")
    tid = _open(client, cenario["ca"])
    r = client.post(f"/api/v1/tickets/{tid}/close", {}, format="json")
    assert r.status_code == 409, r.content


@pytest.mark.django_db(transaction=True)
def test_comanda_fechada_e_imutavel(cenario):
    client = _client("dono@a.com")
    tid = _open(client, cenario["ca"])
    client.post(f"/api/v1/tickets/{tid}/items", {"description": "Corte", "unit_price_cents": 5000}, format="json")
    client.post(f"/api/v1/tickets/{tid}/payments", {"amount_cents": 5000}, format="json")
    assert client.post(f"/api/v1/tickets/{tid}/close", {}, format="json").status_code == 200
    # não aceita novo item após fechada
    r = client.post(f"/api/v1/tickets/{tid}/items", {"description": "Extra", "unit_price_cents": 1000}, format="json")
    assert r.status_code == 409, r.content


@pytest.mark.django_db(transaction=True)
def test_rejeita_cliente_de_outro_tenant(cenario):
    # Dono A tenta abrir comanda para cliente do tenant B -> 422.
    client = _client("dono@a.com")
    r = client.post("/api/v1/tickets", {"customer_id": str(cenario["cb"].id)}, format="json")
    assert r.status_code == 422, r.content


@pytest.mark.django_db(transaction=True)
def test_isola_tickets_por_tenant(cenario):
    ca = _client("dono@a.com")
    cb = _client("dono@b.com")
    _open(ca, cenario["ca"])
    _open(cb, cenario["cb"])
    assert len(ca.get("/api/v1/tickets").data["results"]) == 1
    assert len(cb.get("/api/v1/tickets").data["results"]) == 1
