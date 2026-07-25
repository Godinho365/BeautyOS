from rest_framework import serializers

from .models import Commission, CommissionRule


class CommissionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRule
        fields = ["id", "professional_id", "percent_bps", "created_at"]
        read_only_fields = ["id", "created_at"]


class CommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = [
            "id", "professional_id", "ticket_id", "base_cents",
            "percent_bps", "amount_cents", "status", "created_at",
        ]
        read_only_fields = fields
