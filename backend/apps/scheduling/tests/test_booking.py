"""Testes do módulo scheduling — regra de não-sobreposição e isolamento.

Requer PostgreSQL (RLS + constraint EXCLUDE) e role não-superusuário. Ver
docs/testing/testing-strategy.md e docs/architecture/multi-tenant.md.
"""
from datetime import datetime, timedelta, timezone

import pytest
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient

from apps.catalog.models import Service
from apps.common.tenant_context import use_tenant
from apps.crm.models import Customer
from apps.identity.models import User
from apps.scheduling.models import Appointment
from apps.staff.models import Professional
from apps.tenant.models import Company


def _dt(hour, minute=0):
    return datetime(2026, 8, 1, hour, minute, tzinfo=timezone.utc)


@pytest.fixture
def cenario(db):
    a = Company.objects.create(name="Salão A")
    b = Company.objects.create(name="Salão B")
    data = {"a": a, "b": b}
    with use_tenant(a.id):
        data["svc_a"] = Service.objects.create(tenant_id=a.id, name="Corte", duration_minutes=60)
        data["prof_a"] = Professional.objects.create(tenant_id=a.id, name="Ana")
        data["cust_a"] = Customer.objects.create(tenant_id=a.id, name="Cliente A")
    with use_tenant(b.id):
        data["svc_b"] = Service.objects.create(tenant_id=b.id, name="Corte", duration_minutes=60)
        data["prof_b"] = Professional.objects.create(tenant_id=b.id, name="Bruno")
        data["cust_b"] = Customer.objects.create(tenant_id=b.id, name="Cliente B")
    User.objects.create_user(email="dono@a.com", password="senha123", tenant_id=a.id)
    User.objects.create_user(email="dono@b.com", password="senha123", tenant_id=b.id)
    return data


def _client(email):
    c = APIClient()
    r = c.post("/api/v1/auth/token", {"email": email, "password": "senha123"}, format="json")
    assert r.status_code == 200, r.content
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")
    return c


def _book(client, cust, prof, svc, hour):
    return client.post(
        "/api/v1/appointments",
        {"customer_id": str(cust.id), "professional_id": str(prof.id),
         "service_id": str(svc.id), "starts_at": _dt(hour).isoformat()},
        format="json",
    )


@pytest.mark.django_db(transaction=True)
def test_agenda_e_calcula_fim_pelo_servico(cenario):
    client = _client("dono@a.com")
    r = _book(client, cenario["cust_a"], cenario["prof_a"], cenario["svc_a"], 10)
    assert r.status_code == 201, r.content
    # ends_at derivado da duração do serviço (60min), independente do fuso de exibição.
    starts = datetime.fromisoformat(r.data["starts_at"])
    ends = datetime.fromisoformat(r.data["ends_at"])
    assert ends - starts == timedelta(minutes=60)


@pytest.mark.django_db(transaction=True)
def test_rejeita_sobreposicao_mesmo_profissional(cenario):
    client = _client("dono@a.com")
    assert _book(client, cenario["cust_a"], cenario["prof_a"], cenario["svc_a"], 10).status_code == 201
    # 10:30 sobrepõe 10:00–11:00 -> conflito
    r = client.post(
        "/api/v1/appointments",
        {"customer_id": str(cenario["cust_a"].id), "professional_id": str(cenario["prof_a"].id),
         "service_id": str(cenario["svc_a"].id), "starts_at": _dt(10, 30).isoformat()},
        format="json",
    )
    assert r.status_code == 409, r.content


@pytest.mark.django_db(transaction=True)
def test_constraint_do_banco_barra_sobreposicao(cenario):
    """Camada 2: mesmo burlando o use case, a constraint EXCLUDE rejeita no banco."""
    a, prof, cust, svc = cenario["a"], cenario["prof_a"], cenario["cust_a"], cenario["svc_a"]
    with use_tenant(a.id):
        Appointment.objects.create(
            tenant_id=a.id, customer_id=cust.id, professional_id=prof.id,
            service_id=svc.id, starts_at=_dt(14), ends_at=_dt(15),
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():  # savepoint: isola o erro esperado
                Appointment.objects.create(
                    tenant_id=a.id, customer_id=cust.id, professional_id=prof.id,
                    service_id=svc.id, starts_at=_dt(14, 30), ends_at=_dt(15, 30),
                )


@pytest.mark.django_db(transaction=True)
def test_permite_horarios_adjacentes(cenario):
    client = _client("dono@a.com")
    assert _book(client, cenario["cust_a"], cenario["prof_a"], cenario["svc_a"], 10).status_code == 201
    # 11:00 começa exatamente quando o anterior termina -> sem sobreposição
    assert _book(client, cenario["cust_a"], cenario["prof_a"], cenario["svc_a"], 11).status_code == 201


@pytest.mark.django_db(transaction=True)
def test_rejeita_profissional_de_outro_tenant(cenario):
    # Dono A tenta agendar com o profissional do tenant B -> inválido (422).
    client = _client("dono@a.com")
    r = client.post(
        "/api/v1/appointments",
        {"customer_id": str(cenario["cust_a"].id), "professional_id": str(cenario["prof_b"].id),
         "service_id": str(cenario["svc_a"].id), "starts_at": _dt(9).isoformat()},
        format="json",
    )
    assert r.status_code == 422, r.content


@pytest.mark.django_db(transaction=True)
def test_isola_agendamentos_por_tenant(cenario):
    ca = _client("dono@a.com")
    cb = _client("dono@b.com")
    assert _book(ca, cenario["cust_a"], cenario["prof_a"], cenario["svc_a"], 10).status_code == 201
    assert _book(cb, cenario["cust_b"], cenario["prof_b"], cenario["svc_b"], 10).status_code == 201
    assert len(ca.get("/api/v1/appointments").data) == 1
    assert len(cb.get("/api/v1/appointments").data) == 1
