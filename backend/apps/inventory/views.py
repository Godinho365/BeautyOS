"""Views do módulo inventory. Isolamento por tenant via manager escopado + RLS."""
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.common.tenant_context import get_current_tenant

from .models import Product
from .serializers import AdjustStockSerializer, ProductSerializer
from .services import InventoryError, NegativeStockError, adjust_stock


class ProductViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all().order_by("name")

    def perform_create(self, serializer):
        serializer.save(tenant_id=get_current_tenant())

    @action(detail=True, methods=["post"])
    def adjust(self, request, pk=None):
        payload = AdjustStockSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            product = adjust_stock(tenant_id=get_current_tenant(), product_id=pk, **payload.validated_data)
        except NegativeStockError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except InventoryError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
