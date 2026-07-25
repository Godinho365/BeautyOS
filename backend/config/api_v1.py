"""Composição das rotas da API v1.

Um ÚNICO DefaultRouter é compartilhado por todos os módulos (cada um registra
seus recursos via `register(router)`). Isso mantém o versionamento único
/api/v1 e evita o registro duplicado de conversores de sufixo do DRF.
Ver docs/api/api_guidelines.md.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.catalog.routes import register as register_catalog
from apps.commissions.routes import register as register_commissions
from apps.crm.routes import register as register_crm
from apps.finance.routes import register as register_finance
from apps.inventory.routes import register as register_inventory
from apps.marketing.routes import register as register_marketing
from apps.notifications.routes import register as register_notifications
from apps.scheduling.routes import register as register_scheduling
from apps.staff.routes import register as register_staff
from apps.tenant.routes import register as register_tenant

router = DefaultRouter(trailing_slash=False)
register_tenant(router)
register_catalog(router)
register_staff(router)
register_crm(router)
register_scheduling(router)
register_finance(router)
register_inventory(router)
register_commissions(router)
register_marketing(router)
register_notifications(router)

urlpatterns = [
    path("auth/", include("apps.identity.urls")),
    path("ai/", include("apps.ai.urls")),
    path("marketplace/", include("apps.marketplace.urls")),
    *router.urls,
]
