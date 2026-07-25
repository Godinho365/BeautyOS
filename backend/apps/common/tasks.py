"""Tarefas Celery da camada common.

`process_outbox` é o relay assíncrono do Transactional Outbox: roda
periodicamente (Celery beat) e despacha os eventos pendentes aos handlers.
Substitui o acionamento manual do comando `process_outbox`. Ver ADR-0005 e
docs/architecture/events.md.
"""
from celery import shared_task

from .outbox import process_pending


@shared_task(name="apps.common.tasks.process_outbox")
def process_outbox() -> int:
    """Processa a outbox; retorna quantos eventos foram despachados."""
    return process_pending()
