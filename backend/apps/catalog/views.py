"""Views do módulo catalog. Isolamento por tenant via manager escopado + RLS.
Ver docs/architecture/multi-tenant.md e docs/api/api_guidelines.md.
"""
from rest_framework import mixins, viewsets

from apps.common.tenant_context import get_current_tenant

from .models import Service
from .serializers import ServiceSerializer


class ServiceViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ServiceSerializer

    def get_queryset(self):
        return Service.objects.all().order_by("name")

    def perform_create(self, serializer):
        # tenant_id derivado do contexto da requisição, não do payload.
        serializer.save(tenant_id=get_current_tenant())
