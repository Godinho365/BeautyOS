"""Views do módulo marketing. Isolamento por tenant via manager escopado + RLS."""
from rest_framework import mixins, viewsets

from apps.common.tenant_context import get_current_tenant

from .models import Campaign, LoyaltyAccount
from .serializers import CampaignSerializer, LoyaltyAccountSerializer


class CampaignViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = CampaignSerializer
    read_roles = frozenset({"owner", "manager"})

    def get_queryset(self):
        return Campaign.objects.all().order_by("name")

    def perform_create(self, serializer):
        serializer.save(tenant_id=get_current_tenant())


class LoyaltyAccountViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = LoyaltyAccountSerializer
    read_roles = frozenset({"owner", "manager"})

    def get_queryset(self):
        return LoyaltyAccount.objects.all().order_by("-points")
