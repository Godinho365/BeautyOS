"""Views do marketplace.

- Gestão do perfil (autenticado, owner/manager): criar/publicar o perfil do tenant.
- Descoberta pública (AllowAny): listar empresas publicadas e ver serviços.
- Booking público (AllowAny): agenda identificando o tenant pelo `slug`.

Ver docs/architecture/modules.md (marketplace) e multi-tenant.md.
"""
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.contracts import list_active_services
from apps.common.permissions import RoleBasedPermission
from apps.common.tenant_context import get_current_tenant, use_tenant
from apps.scheduling.services import InvalidBookingError, OverlapError

from .models import MarketplaceProfile
from .serializers import ProfileSerializer, ProfileWriteSerializer, PublicBookingSerializer
from .services import public_book, upsert_profile


class MyProfileView(APIView):
    """Perfil de marketplace do tenant autenticado (gestão)."""

    permission_classes = [IsAuthenticated, RoleBasedPermission]
    write_roles = frozenset({"owner", "manager"})
    read_roles = frozenset({"owner", "manager"})

    def get(self, request):
        profile = MarketplaceProfile.objects.filter(company_id=get_current_tenant()).first()
        if profile is None:
            return Response({"detail": "Sem perfil de marketplace."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProfileSerializer(profile).data)

    def put(self, request):
        payload = ProfileWriteSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        profile = upsert_profile(tenant_id=get_current_tenant(), **payload.validated_data)
        return Response(ProfileSerializer(profile).data, status=status.HTTP_200_OK)


class PublicCompanyListView(APIView):
    """Lista pública de empresas publicadas (sem autenticação)."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def get(self, request):
        profiles = MarketplaceProfile.objects.filter(is_published=True).order_by("display_name")
        return Response(ProfileSerializer(profiles, many=True).data)


class PublicCompanyDetailView(APIView):
    """Perfil público + serviços ativos da empresa (sem autenticação)."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def get(self, request, slug):
        profile = MarketplaceProfile.objects.filter(slug=slug, is_published=True).first()
        if profile is None:
            return Response({"detail": "Empresa não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        data = ProfileSerializer(profile).data
        # RLS: precisa do contexto do tenant para ler os serviços da Empresa.
        with use_tenant(profile.company_id):
            data["services"] = list_active_services(profile.company_id)
        return Response(data)


class PublicBookingView(APIView):
    """Agendamento público para a empresa identificada pelo `slug`."""

    permission_classes = [AllowAny]
    authentication_classes: list = []

    def post(self, request, slug):
        profile = MarketplaceProfile.objects.filter(slug=slug, is_published=True).first()
        if profile is None:
            return Response({"detail": "Empresa não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        payload = PublicBookingSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        try:
            appt = public_book(profile=profile, **payload.validated_data)
        except InvalidBookingError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        except OverlapError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        return Response({"appointment_id": str(appt.id)}, status=status.HTTP_201_CREATED)
