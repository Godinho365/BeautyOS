"""Views do módulo crm. Isolamento por tenant via manager escopado + RLS."""
from rest_framework import mixins, viewsets

from apps.common.tenant_context import get_current_tenant

from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return Customer.objects.all().order_by("name")

    def perform_create(self, serializer):
        serializer.save(tenant_id=get_current_tenant())
