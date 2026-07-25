"""Views do módulo staff. Isolamento por tenant via manager escopado + RLS.
Ver docs/architecture/multi-tenant.md e docs/api/api_guidelines.md.
"""
from rest_framework import mixins, viewsets

from apps.common.tenant_context import get_current_tenant

from .models import Professional
from .serializers import ProfessionalSerializer


class ProfessionalViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProfessionalSerializer

    def get_queryset(self):
        return Professional.objects.all().order_by("name")

    def perform_create(self, serializer):
        serializer.save(tenant_id=get_current_tenant())
