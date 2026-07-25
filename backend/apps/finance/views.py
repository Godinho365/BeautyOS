"""Views do módulo finance.

Delega aos use cases (services.py) e mapeia erros de negócio para HTTP:
422 para entrada/estado inválido, 409 para conflito (ex.: comanda fechada,
pagamento insuficiente). Isolamento por tenant via manager escopado + RLS.
"""
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.tenant_context import get_current_tenant

from .models import Ticket
from .serializers import (
    AddItemSerializer,
    OpenTicketSerializer,
    RegisterPaymentSerializer,
    TicketSerializer,
)
from .services import (
    ConflictFinanceError,
    InvalidFinanceError,
    add_item,
    close_ticket,
    open_ticket,
    register_payment,
)


def _map_error(exc):
    if isinstance(exc, ConflictFinanceError):
        return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
    return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class TicketViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = TicketSerializer

    def get_queryset(self):
        return (
            Ticket.objects.all()
            .prefetch_related("items", "payments")
            .order_by("-created_at")
        )

    def create(self, request, *args, **kwargs):
        payload = OpenTicketSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            ticket = open_ticket(tenant_id=get_current_tenant(), **payload.validated_data)
        except (InvalidFinanceError, ConflictFinanceError) as exc:
            return _map_error(exc)
        return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def items(self, request, pk=None):
        payload = AddItemSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            add_item(tenant_id=get_current_tenant(), ticket_id=pk, **payload.validated_data)
        except (InvalidFinanceError, ConflictFinanceError) as exc:
            return _map_error(exc)
        return Response(TicketSerializer(self.get_queryset().get(pk=pk)).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def payments(self, request, pk=None):
        payload = RegisterPaymentSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            register_payment(tenant_id=get_current_tenant(), ticket_id=pk, **payload.validated_data)
        except (InvalidFinanceError, ConflictFinanceError) as exc:
            return _map_error(exc)
        return Response(TicketSerializer(self.get_queryset().get(pk=pk)).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        try:
            ticket = close_ticket(tenant_id=get_current_tenant(), ticket_id=pk)
        except (InvalidFinanceError, ConflictFinanceError) as exc:
            return _map_error(exc)
        return Response(TicketSerializer(ticket).data, status=status.HTTP_200_OK)
