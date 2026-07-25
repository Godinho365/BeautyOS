"""Views do módulo notifications (somente leitura no skeleton).
Isolamento por tenant via manager escopado + RLS.
"""
from rest_framework import mixins, viewsets

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.all().order_by("-created_at")
