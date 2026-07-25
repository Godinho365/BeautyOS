"""Testes do Copilot (insights determinísticos). Requer PostgreSQL (RLS).

Ver docs/ai/copilot.md.
"""
import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.catalog.models import Service
from apps.common.tenant_context import use_tenant
from apps.crm.models import Customer
from apps.finance.services import add_item, close_ticket, open_ticket, register_payment
from apps.identity.models import User
from apps.inventory.models import Product
from apps.staff.models import Professional
from apps.scheduling.services import book_appointment
from apps.tenant.models import Company


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    with use_tenant(a.id):
        svc = Service.objects.create(tenant_id=a.id, name="Corte", duration_minutes=60)
        prof = Professional.objects.create(tenant_id=a.id, name="Ana")
        cust = Customer.objects.create(tenant_id=a.id, name="Cliente A")
        Product.objects.create(tenant_id=a.id, name="Shampoo", quantity=2)  # estoque baixo
        book_appointment(
            tenant_id=a.id, customer_id=cust.id, professional_id=prof.id,
            service_id=svc.id, starts_at=timezone.now(),
        )
        t = open_ticket(tenant_id=a.id, customer_id=cust.id)
        add_item(tenant_id=a.id, ticket_id=t.id, description="Corte", unit_price_cents=5000)
        register_payment(tenant_id=a.id, ticket_id=t.id, amount_cents=5000)
        close_ticket(tenant_id=a.id, ticket_id=t.id)
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id, role="owner")
    User.objects.create_user(email="prof@a.com", password="senha123", tenant_id=a.id, role="professional")
    return {"a": a}


def _client(email):
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


@pytest.mark.django_db(transaction=True)
def test_insights_agrega_dados_do_tenant(cenario):
    data = _client("dono@a.com").get("/api/v1/ai/insights").data
    assert data["revenue_today_cents"] == 5000
    assert data["appointments_today"] == 1
    assert data["low_stock_products"] == 1
    assert data["customers_total"] == 1
    assert isinstance(data["suggestions"], list) and data["suggestions"]


@pytest.mark.django_db(transaction=True)
def test_insights_restrito_a_gestao(cenario):
    # Profissional não tem acesso aos insights (RBAC).
    assert _client("prof@a.com").get("/api/v1/ai/insights").status_code == 403
