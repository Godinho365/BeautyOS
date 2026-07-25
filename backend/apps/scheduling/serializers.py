from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Representação de saída de um agendamento."""

    class Meta:
        model = Appointment
        fields = [
            "id", "customer_id", "professional_id", "service_id",
            "starts_at", "ends_at", "status", "created_at",
        ]
        read_only_fields = fields


class AppointmentCreateSerializer(serializers.Serializer):
    """Entrada para criar um agendamento. `ends_at` é derivado do serviço."""

    customer_id = serializers.UUIDField()
    professional_id = serializers.UUIDField()
    service_id = serializers.UUIDField()
    starts_at = serializers.DateTimeField()
