"""Views do módulo scheduling.

O `create` delega ao use case `book_appointment` e mapeia os erros de negócio
para status HTTP (ver docs/api/api_guidelines.md). Isolamento por tenant via
manager escopado + RLS.
"""
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from apps.common.tenant_context import get_current_tenant

from .models import Appointment
from .serializers import AppointmentCreateSerializer, AppointmentSerializer
from .services import InvalidBookingError, OverlapError, book_appointment


class AppointmentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AppointmentSerializer
    # Recepção também agenda (ver matriz RBAC em docs/security/security.md).
    write_roles = frozenset({"owner", "manager", "reception"})

    def get_queryset(self):
        return Appointment.objects.all().order_by("starts_at")

    def create(self, request, *args, **kwargs):
        payload = AppointmentCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            appointment = book_appointment(
                tenant_id=get_current_tenant(),
                **payload.validated_data,
            )
        except InvalidBookingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except OverlapError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)
