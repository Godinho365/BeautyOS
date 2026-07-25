"""Testes de isolamento multi-tenant — o gate obrigatório do walking skeleton.

Prova, em dois níveis, que o dado de uma Empresa nunca vaza para outra:
  1. No banco (RLS): mesmo ignorando o manager escopado, a política bloqueia.
  2. Na API (E2E): usuários de tenants diferentes só enxergam o próprio dado.

Requer PostgreSQL (RLS não existe em SQLite). Ver docs/testing/testing-strategy.md
e docs/architecture/multi-tenant.md.
"""
import pytest
from rest_framework.test import APIClient

from apps.common.tenant_context import use_tenant
from apps.identity.models import User
from apps.tenant.models import Branch, Company


@pytest.fixture
def two_companies(db):
    a = Company.objects.create(name="Salão A")
    b = Company.objects.create(name="Salão B")
    with use_tenant(a.id):
        Branch.objects.create(tenant_id=a.id, name="Filial A")
    with use_tenant(b.id):
        Branch.objects.create(tenant_id=b.id, name="Filial B")
    return a, b


@pytest.mark.django_db(transaction=True)
def test_rls_bloqueia_cross_tenant_no_banco(two_companies):
    a, b = two_companies
    # Dentro do tenant A, mesmo o manager sem filtro (all_tenants) não vê B:
    # é a RLS do PostgreSQL agindo como rede de segurança final.
    with use_tenant(a.id):
        assert set(Branch.objects.values_list("name", flat=True)) == {"Filial A"}
        assert set(Branch.all_tenants.values_list("name", flat=True)) == {"Filial A"}


@pytest.mark.django_db(transaction=True)
def test_sem_tenant_nao_ve_nada(two_companies):
    # Sem tenant no contexto (ex.: requisição anônima), nenhuma linha de negócio.
    with use_tenant(None):
        assert list(Branch.all_tenants.all()) == []


@pytest.mark.django_db(transaction=True)
def test_api_isola_branches_por_tenant(two_companies):
    a, b = two_companies
    User.objects.create_user(email="dono@salaoa.com", password="senha123", tenant_id=a.id)
    User.objects.create_user(email="dono@salaob.com", password="senha123", tenant_id=b.id)

    client = APIClient()

    def branches_do(email):
        r = client.post(
            "/api/v1/auth/token",
            {"email": email, "password": "senha123"},
            format="json",
        )
        assert r.status_code == 200, r.content
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
        r = client.get("/api/v1/branches")
        assert r.status_code == 200, r.content
        return {item["name"] for item in r.data}

    assert branches_do("dono@salaoa.com") == {"Filial A"}
    assert branches_do("dono@salaob.com") == {"Filial B"}
