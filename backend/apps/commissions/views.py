"""Views do módulo commissions. Isolamento por tenant via manager escopado + RLS.

`CommissionRule` é configurável (list/create); `Commission` é somente leitura
(gerada por evento). Ver docs/architecture/events.md.
"""
from rest_framework import mixins, viewsets

from apps.common.tenant_context import get_current_tenant

from .models import Commission, CommissionRule
from .serializers import CommissionRuleSerializer, CommissionSerializer


class CommissionRuleViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CommissionRuleSerializer
    read_roles = frozenset({"owner", "manager"})

    def get_queryset(self):
        return CommissionRule.objects.all().order_by("professional_id")

    def perform_create(self, serializer):
        serializer.save(tenant_id=get_current_tenant())


class CommissionViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CommissionSerializer
    read_roles = frozenset({"owner", "manager"})

    def get_queryset(self):
        return Commission.objects.all().order_by("-created_at")
