"""Testes do módulo staff — isolamento por tenant e criação via API.

Requer PostgreSQL (RLS) e conexão como role não-superusuário. Ver
docs/testing/testing-strategy.md e docs/architecture/multi-tenant.md.
"""
import pytest
from rest_framework.test import APIClient

from apps.common.tenant_context import use_tenant
from apps.identity.models import User
from apps.staff.models import Professional
from apps.tenant.models import Company


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    b = Company.objects.create(name="Salão B")
    with use_tenant(a.id):
        Professional.objects.create(tenant_id=a.id, name="Ana", specialty="Cabelo")
    with use_tenant(b.id):
        Professional.objects.create(tenant_id=b.id, name="Bruno", specialty="Barba")
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id, role="owner")
    User.objects.create_user(email="dono@b.com", password="senha123", tenant_id=b.id, role="owner")
    return a, b


def _client(email):
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


@pytest.mark.django_db(transaction=True)
def test_rls_isola_professionals_no_banco(cenario):
    a, _ = cenario
    with use_tenant(a.id):
        assert set(Professional.all_tenants.values_list("name", flat=True)) == {"Ana"}


@pytest.mark.django_db(transaction=True)
def test_api_isola_professionals_por_tenant(cenario):
    assert {p["name"] for p in _client("dono@a.com").get("/api/v1/professionals").data} == {"Ana"}
    assert {p["name"] for p in _client("dono@b.com").get("/api/v1/professionals").data} == {"Bruno"}


@pytest.mark.django_db(transaction=True)
def test_api_cria_professional_no_tenant_correto(cenario):
    a, _ = cenario
    client = _client("dono@a.com")
    r = client.post(
        "/api/v1/professionals",
        {"name": "Carla", "specialty": "Unhas"},
        format="json",
    )
    assert r.status_code == 201, r.content
    assert {p["name"] for p in client.get("/api/v1/professionals").data} == {"Ana", "Carla"}
