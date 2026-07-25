"""Testes de RBAC — autorização por papel na Empresa.

Requer PostgreSQL (RLS). Ver docs/security/security.md (matriz de papéis).
"""
import pytest
from rest_framework.test import APIClient

from apps.common.tenant_context import use_tenant
from apps.crm.models import Customer
from apps.identity.models import User
from apps.tenant.models import Company


@pytest.fixture
def empresa(db):
    a = Company.objects.create(name="Salão A")
    with use_tenant(a.id):
        cust = Customer.objects.create(tenant_id=a.id, name="Cliente A")

    def make(email, role):
        return User.objects.create_user(email=email, password="senha123", tenant_id=a.id, role=role)

    make("owner@a.com", "owner")
    make("prof@a.com", "professional")
    make("recep@a.com", "reception")
    return {"a": a, "cust": cust}


def _client(email):
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


@pytest.mark.django_db(transaction=True)
def test_owner_pode_criar_servico(empresa):
    r = _client("owner@a.com").post(
        "/api/v1/services", {"name": "Corte", "duration_minutes": 30, "price_cents": 5000}, format="json"
    )
    assert r.status_code == 201, r.content


@pytest.mark.django_db(transaction=True)
def test_profissional_nao_cria_servico(empresa):
    # Escrita em catálogo é restrita a owner/manager -> 403.
    r = _client("prof@a.com").post(
        "/api/v1/services", {"name": "Corte", "duration_minutes": 30, "price_cents": 5000}, format="json"
    )
    assert r.status_code == 403, r.content


@pytest.mark.django_db(transaction=True)
def test_profissional_pode_ler_servicos(empresa):
    assert _client("prof@a.com").get("/api/v1/services").status_code == 200


@pytest.mark.django_db(transaction=True)
def test_recepcao_agenda_mas_nao_cria_servico(empresa):
    recep = _client("recep@a.com")
    # recepção NÃO cria serviço
    assert recep.post(
        "/api/v1/services", {"name": "X", "duration_minutes": 30, "price_cents": 100}, format="json"
    ).status_code == 403
    # mas cadastra cliente (permitido)
    assert recep.post("/api/v1/customers", {"name": "Novo"}, format="json").status_code == 201


@pytest.mark.django_db(transaction=True)
def test_profissional_nao_ve_comissoes(empresa):
    # Leitura de comissões é restrita a owner/manager.
    assert _client("prof@a.com").get("/api/v1/commissions").status_code == 403
    assert _client("owner@a.com").get("/api/v1/commissions").status_code == 200
