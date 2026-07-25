"""Views do módulo ai/Copilot.

`GET /api/v1/ai/insights` devolve métricas e sugestões do dia para o tenant.
Restrito a papéis de gestão (owner/manager). Ver docs/ai/copilot.md.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import RoleBasedPermission
from apps.common.tenant_context import get_current_tenant

from .services import compute_insights


class InsightsView(APIView):
    permission_classes = [IsAuthenticated, RoleBasedPermission]
    read_roles = frozenset({"owner", "manager"})

    def get(self, request):
        return Response(compute_insights(get_current_tenant()))
