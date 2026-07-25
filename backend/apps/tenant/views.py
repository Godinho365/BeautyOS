"""Views do módulo tenant.

`BranchViewSet` demonstra a fatia E2E isolada por tenant: o queryset usa o
manager escopado (`Branch.objects`), que só enxerga o tenant corrente — reforçado
pela RLS no banco. O `tenant_id` na escrita vem do contexto, nunca do cliente.
Ver docs/architecture/multi-tenant.md e docs/api/api_guidelines.md.
"""
from rest_framework import mixins, viewsets

from apps.common.tenant_context import get_current_tenant

from .models import Branch
from .serializers import BranchSerializer


class BranchViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BranchSerializer

    def get_queryset(self):
        # Manager já escopado pelo tenant corrente (defesa em app + RLS no banco).
        return Branch.objects.all().order_by("name")

    def perform_create(self, serializer):
        # tenant_id derivado do contexto da requisição, não do payload.
        serializer.save(tenant_id=get_current_tenant())
