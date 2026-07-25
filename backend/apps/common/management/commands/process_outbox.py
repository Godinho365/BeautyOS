"""Relay do Outbox: despacha eventos pendentes.

Hoje roda como comando (útil em dev/CI e como base do worker). Em produção vira
uma tarefa periódica do Celery. Ver docs/architecture/events.md.

    python manage.py process_outbox
"""
from django.core.management.base import BaseCommand

from apps.common.outbox import process_pending


class Command(BaseCommand):
    help = "Processa eventos pendentes da outbox, despachando aos handlers."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        n = process_pending(limit=options["limit"])
        self.stdout.write(self.style.SUCCESS(f"{n} evento(s) processado(s)."))
