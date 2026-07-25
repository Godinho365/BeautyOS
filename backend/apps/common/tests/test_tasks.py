"""Testa a tarefa Celery do relay do Outbox.

Chamar a task diretamente executa o corpo de forma síncrona (sem broker), o que
prova que ela aciona o relay `process_pending`. O agendamento em produção é feito
pelo Celery beat (ver settings CELERY_BEAT_SCHEDULE). Ver docs/architecture/events.md.
"""
from datetime import datetime, timezone

import pytest

from apps.catalog.models import Service
from apps.common.tasks import process_outbox
from apps.common.tenant_context import use_tenant
from apps.crm.models import Customer
from apps.notifications.models import Notification
from apps.scheduling.services import book_appointment
from apps.staff.models import Professional
from apps.tenant.models import Company


@pytest.mark.django_db(transaction=True)
def test_task_process_outbox_despacha_eventos(db):
    a = Company.objects.create(name="Salão A")
    with use_tenant(a.id):
        svc = Service.objects.create(tenant_id=a.id, name="Corte", duration_minutes=60)
        prof = Professional.objects.create(tenant_id=a.id, name="Ana")
        cust = Customer.objects.create(tenant_id=a.id, name="Cliente A")
        book_appointment(
            tenant_id=a.id, customer_id=cust.id, professional_id=prof.id,
            service_id=svc.id, starts_at=datetime(2026, 8, 1, 10, tzinfo=timezone.utc),
        )
    # Relay acionado pela task Celery (execução síncrona ao chamar diretamente).
    assert process_outbox() == 1
    with use_tenant(a.id):
        assert Notification.objects.count() == 1
