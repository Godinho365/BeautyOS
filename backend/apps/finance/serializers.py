from rest_framework import serializers

from .models import Payment, Ticket, TicketItem


class TicketItemSerializer(serializers.ModelSerializer):
    subtotal_cents = serializers.IntegerField(read_only=True)

    class Meta:
        model = TicketItem
        fields = ["id", "description", "service_id", "quantity", "unit_price_cents", "subtotal_cents"]
        read_only_fields = ["id", "subtotal_cents"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "amount_cents", "method", "paid_at"]
        read_only_fields = ["id", "paid_at"]


class TicketSerializer(serializers.ModelSerializer):
    items = TicketItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    paid_cents = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            "id", "customer_id", "appointment_id", "status", "total_cents",
            "paid_cents", "currency", "closed_at", "created_at", "items", "payments",
        ]
        read_only_fields = fields

    def get_paid_cents(self, obj) -> int:
        return sum(p.amount_cents for p in obj.payments.all())


# --- Entradas ---------------------------------------------------------------
class OpenTicketSerializer(serializers.Serializer):
    customer_id = serializers.UUIDField()
    appointment_id = serializers.UUIDField(required=False, allow_null=True)


class AddItemSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=200)
    unit_price_cents = serializers.IntegerField(min_value=0)
    quantity = serializers.IntegerField(min_value=1, default=1)
    service_id = serializers.UUIDField(required=False, allow_null=True)


class RegisterPaymentSerializer(serializers.Serializer):
    amount_cents = serializers.IntegerField(min_value=1)
    method = serializers.ChoiceField(choices=Payment.Method.choices, default=Payment.Method.PIX)
