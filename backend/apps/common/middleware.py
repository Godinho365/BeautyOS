"""Middleware que estabelece o tenant da requisição.

Fluxo (ver docs/architecture/multi-tenant.md):
  1. Autentica o JWT e descobre o usuário (tabelas globais, sem RLS).
  2. Abre a transação da requisição e aplica `app.tenant_id` via SET LOCAL.
  3. A partir daí, toda query de entidade de negócio é isolada pela RLS + pelo
     manager escopado.

Por que a transação é gerenciada aqui (e ATOMIC_REQUESTS=False): o `SET LOCAL`
só persiste dentro de uma transação. Se deixássemos o Django abrir a transação
apenas ao redor da view (ATOMIC_REQUESTS), o SET feito no middleware — que roda
fora dela — não valeria para as queries da view.
"""
from __future__ import annotations

from django.db import transaction
from rest_framework_simplejwt.authentication import JWTAuthentication

from .tenant_context import _current_tenant, set_db_tenant

_jwt_authenticator = JWTAuthentication()


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def _resolve_tenant(self, request):
        """Retorna o tenant_id do usuário autenticado, ou None se anônimo."""
        try:
            result = _jwt_authenticator.authenticate(request)
        except Exception:
            return None
        if result is None:
            return None
        user, _token = result
        # Deixa o usuário disponível para as views sem reautenticar.
        request.user = user
        return getattr(user, "tenant_id", None)

    def __call__(self, request):
        tenant_id = self._resolve_tenant(request)
        token = _current_tenant.set(tenant_id)
        try:
            with transaction.atomic():
                set_db_tenant(tenant_id)
                response = self.get_response(request)
            return response
        finally:
            _current_tenant.reset(token)
