"""RBAC — permissões por papel na Empresa. Ver docs/security/security.md.

Modelo simples e declarativo: cada ViewSet define os conjuntos de papéis que
podem **ler** (métodos seguros) e **escrever** (POST/PUT/PATCH/DELETE). Sem
declaração, valem os defaults conservadores abaixo.

A autorização é sempre no **servidor** — o front nunca é a autoridade.
"""
from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

ALL_ROLES = frozenset({"owner", "manager", "professional", "reception"})
DEFAULT_READ_ROLES = ALL_ROLES
DEFAULT_WRITE_ROLES = frozenset({"owner", "manager"})


class RoleBasedPermission(BasePermission):
    """Autoriza conforme o papel do usuário e os conjuntos definidos na view."""

    message = "Seu papel não permite esta ação."

    def has_permission(self, request, view) -> bool:
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        role = getattr(user, "role", None)
        if request.method in SAFE_METHODS:
            allowed = getattr(view, "read_roles", DEFAULT_READ_ROLES)
        else:
            allowed = getattr(view, "write_roles", DEFAULT_WRITE_ROLES)
        return role in allowed
