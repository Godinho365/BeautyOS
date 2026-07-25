from rest_framework import serializers

from .models import Campaign, LoyaltyAccount


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = ["id", "name", "description", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]


class LoyaltyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyAccount
        fields = ["id", "customer_id", "points", "created_at"]
        read_only_fields = fields
