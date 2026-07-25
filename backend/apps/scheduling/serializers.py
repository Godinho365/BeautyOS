from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Representação de saída de um agendamento."""

    class Meta:
        model = Appointment
        fields = [
            "id", "customer_name", "professional_id", "service_id",
            "starts_at", "ends_at", "status", "created_at",
        ]
        read_only_fields = fields


class AppointmentCreateSerializer(serializers.Serializer):
    """Entrada para criar um agendamento. `ends_at` é derivado do serviço."""

    customer_name = serializers.CharField(max_length=200)
    professional_id = serializers.UUIDField()
    service_id = serializers.UUIDField()
    starts_at = serializers.DateTimeField()
