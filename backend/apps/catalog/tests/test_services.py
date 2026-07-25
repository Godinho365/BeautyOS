"""Testes do módulo catalog — isolamento por tenant e criação via API.

Requer PostgreSQL (RLS) e conexão como role não-superusuário. Ver
docs/testing/testing-strategy.md e docs/architecture/multi-tenant.md.
"""
import pytest
from rest_framework.test import APIClient

from apps.catalog.models import Service
from apps.common.tenant_context import use_tenant
from apps.identity.models import User
from apps.tenant.models import Company


@pytest.fixture
def companies_com_usuarios(db):
    a = Company.objects.create(name="Salão A")
    b = Company.objects.create(name="Salão B")
    with use_tenant(a.id):
        Service.objects.create(tenant_id=a.id, name="Corte A", duration_minutes=30, price_cents=5000)
    with use_tenant(b.id):
        Service.objects.create(tenant_id=b.id, name="Corte B", duration_minutes=45, price_cents=7000)
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id, role="owner")
    User.objects.create_user(email="dono@b.com", password="senha123", tenant_id=b.id, role="owner")
    return a, b


def _client_para(email):
    client = APIClient()
    r = client.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return client


@pytest.mark.django_db(transaction=True)
def test_rls_isola_services_no_banco(companies_com_usuarios):
    a, _ = companies_com_usuarios
    with use_tenant(a.id):
        # all_tenants ignora o manager, mas a RLS ainda bloqueia o dado de B.
        assert set(Service.all_tenants.values_list("name", flat=True)) == {"Corte A"}


@pytest.mark.django_db(transaction=True)
def test_api_lista_services_isolado_por_tenant(companies_com_usuarios):
    assert {s["name"] for s in _client_para("dono@a.com").get("/api/v1/services").data} == {"Corte A"}
    assert {s["name"] for s in _client_para("dono@b.com").get("/api/v1/services").data} == {"Corte B"}


@pytest.mark.django_db(transaction=True)
def test_api_cria_service_no_tenant_correto(companies_com_usuarios):
    a, _ = companies_com_usuarios
    client = _client_para("dono@a.com")
    r = client.post(
        "/api/v1/services",
        {"name": "Barba", "duration_minutes": 20, "price_cents": 3000},
        format="json",
    )
    assert r.status_code == 201, r.content
    # O serviço criado pertence ao tenant A e aparece só para A.
    names = {s["name"] for s in client.get("/api/v1/services").data}
    assert names == {"Corte A", "Barba"}
    with use_tenant(a.id):
        assert Service.objects.get(name="Barba").tenant_id == a.id
