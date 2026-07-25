from rest_framework import serializers

from .models import Professional


class ProfessionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ["id", "name", "email", "specialty", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
