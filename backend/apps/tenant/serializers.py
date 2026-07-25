from rest_framework import serializers

from .models import Branch


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        # tenant_id nunca vem do cliente: é derivado do contexto (middleware).
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]
