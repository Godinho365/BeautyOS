"""Expõe o app Celery ao importar o pacote de configuração."""
from .celery import app as celery_app

__all__ = ("celery_app",)
