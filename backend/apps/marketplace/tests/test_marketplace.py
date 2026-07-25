"""Testes do marketplace — perfil, descoberta pública e booking público.

Requer PostgreSQL (RLS). O booking público identifica o tenant pelo slug e opera
sob `use_tenant`. Ver docs/architecture/modules.md e multi-tenant.md.
"""
from datetime import datetime, timezone

import pytest
from rest_framework.test import APIClient

from apps.catalog.models import Service
from apps.common.tenant_context import use_tenant
from apps.scheduling.models import Appointment
from apps.staff.models import Professional
from apps.identity.models import User
from apps.tenant.models import Company


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    with use_tenant(a.id):
        svc = Service.objects.create(tenant_id=a.id, name="Corte", duration_minutes=60, price_cents=8000)
        prof = Professional.objects.create(tenant_id=a.id, name="Ana")
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id, role="owner")
    return {"a": a, "svc": svc, "prof": prof}


def _owner():
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": "dono@a.com", "password": "senha123"}, format="json")
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


def _publish(client, slug="salao-a", published=True):
    return client.put(
        "/api/v1/marketplace/profile",
        {"slug": slug, "display_name": "Salão A", "is_published": published},
        format="json",
    )


@pytest.mark.django_db(transaction=True)
def test_publicar_e_descobrir(cenario):
    assert _publish(_owner()).status_code == 200
    # público (sem auth) vê a empresa publicada e seus serviços
    pub = APIClient()
    lst = pub.get("/api/v1/marketplace/companies")
    assert lst.status_code == 200
    assert {c["slug"] for c in lst.data} == {"salao-a"}
    det = pub.get("/api/v1/marketplace/companies/salao-a")
    assert det.status_code == 200
    assert {s["name"] for s in det.data["services"]} == {"Corte"}


@pytest.mark.django_db(transaction=True)
def test_nao_publicado_fica_invisivel(cenario):
    _publish(_owner(), published=False)
    pub = APIClient()
    assert pub.get("/api/v1/marketplace/companies").data == []
    assert pub.get("/api/v1/marketplace/companies/salao-a").status_code == 404


@pytest.mark.django_db(transaction=True)
def test_booking_publico_cria_agendamento(cenario):
    a, svc, prof = cenario["a"], cenario["svc"], cenario["prof"]
    _publish(_owner())
    pub = APIClient()
    r = pub.post(
        "/api/v1/marketplace/companies/salao-a/book",
        {"customer_name": "Maria", "phone": "1190000",
         "professional_id": str(prof.id), "service_id": str(svc.id),
         "starts_at": datetime(2026, 8, 1, 10, tzinfo=timezone.utc).isoformat()},
        format="json",
    )
    assert r.status_code == 201, r.content
    with use_tenant(a.id):
        assert Appointment.objects.filter(professional_id=prof.id).count() == 1


@pytest.mark.django_db(transaction=True)
def test_booking_publico_respeita_sobreposicao(cenario):
    svc, prof = cenario["svc"], cenario["prof"]
    _publish(_owner())
    pub = APIClient()
    body = {
        "customer_name": "Maria", "phone": "119",
        "professional_id": str(prof.id), "service_id": str(svc.id),
        "starts_at": datetime(2026, 8, 1, 10, tzinfo=timezone.utc).isoformat(),
    }
    assert pub.post("/api/v1/marketplace/companies/salao-a/book", body, format="json").status_code == 201
    # segundo booking sobreposto -> conflito
    assert pub.post("/api/v1/marketplace/companies/salao-a/book", body, format="json").status_code == 409
