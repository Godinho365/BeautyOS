"""Aplicação Celery do BeautyOS.

Worker + beat processam o relay do Outbox de forma assíncrona e periódica
(ver docs/architecture/events.md). Config lida do settings com namespace CELERY_.
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("beautyos")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
