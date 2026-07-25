"""Composição das rotas da API v1.

Um ÚNICO DefaultRouter é compartilhado por todos os módulos (cada um registra
seus recursos via `register(router)`). Isso mantém o versionamento único
/api/v1 e evita o registro duplicado de conversores de sufixo do DRF.
Ver docs/api/api_guidelines.md.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.catalog.routes import register as register_catalog
from apps.scheduling.routes import register as register_scheduling
from apps.staff.routes import register as register_staff
from apps.tenant.routes import register as register_tenant

router = DefaultRouter(trailing_slash=False)
register_tenant(router)
register_catalog(router)
register_staff(router)
register_scheduling(router)

urlpatterns = [
    path("auth/", include("apps.identity.urls")),
    *router.urls,
]
