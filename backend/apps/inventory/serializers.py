from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "sku", "quantity", "created_at"]
        read_only_fields = ["id", "quantity", "created_at"]


class AdjustStockSerializer(serializers.Serializer):
    delta = serializers.IntegerField()
    reason = serializers.CharField(max_length=40, default="manual")
