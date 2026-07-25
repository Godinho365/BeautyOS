from rest_framework import serializers

from .models import MarketplaceProfile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketplaceProfile
        fields = ["id", "slug", "display_name", "bio", "is_published", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProfileWriteSerializer(serializers.Serializer):
    slug = serializers.SlugField(max_length=80)
    display_name = serializers.CharField(max_length=200)
    bio = serializers.CharField(required=False, allow_blank=True, default="")
    is_published = serializers.BooleanField(default=False)


class PublicBookingSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=200)
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True, default="")
    professional_id = serializers.UUIDField()
    service_id = serializers.UUIDField()
    starts_at = serializers.DateTimeField()
