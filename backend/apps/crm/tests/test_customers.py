"""Testes do módulo crm — isolamento por tenant e criação via API."""
import pytest
from rest_framework.test import APIClient

from apps.common.tenant_context import use_tenant
from apps.crm.models import Customer
from apps.identity.models import User
from apps.tenant.models import Company


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    b = Company.objects.create(name="Salão B")
    with use_tenant(a.id):
        Customer.objects.create(tenant_id=a.id, name="Cliente A")
    with use_tenant(b.id):
        Customer.objects.create(tenant_id=b.id, name="Cliente B")
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id)
    User.objects.create_user(email="dono@b.com", password="senha123", tenant_id=b.id)
    return a, b


def _client(email):
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


@pytest.mark.django_db(transaction=True)
def test_rls_isola_customers_no_banco(cenario):
    a, _ = cenario
    with use_tenant(a.id):
        assert set(Customer.all_tenants.values_list("name", flat=True)) == {"Cliente A"}


@pytest.mark.django_db(transaction=True)
def test_api_isola_customers_por_tenant(cenario):
    assert {c["name"] for c in _client("dono@a.com").get("/api/v1/customers").data["results"]} == {"Cliente A"}
    assert {c["name"] for c in _client("dono@b.com").get("/api/v1/customers").data["results"]} == {"Cliente B"}
