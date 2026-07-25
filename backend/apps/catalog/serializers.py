from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        # tenant_id nunca vem do cliente: é derivado do contexto (middleware).
        fields = ["id", "name", "duration_minutes", "price_cents", "currency", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
