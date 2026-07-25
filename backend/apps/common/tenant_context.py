"""Contexto de tenant por requisição/execução.

Guarda o `tenant_id` corrente em um ContextVar (seguro para async e threads) e
o propaga para a sessão do PostgreSQL como `app.tenant_id`, que é lido pelas
políticas de Row-Level Security. Ver docs/architecture/multi-tenant.md.
"""
from __future__ import annotations

import contextlib
import uuid
from contextvars import ContextVar

from django.db import connection, transaction

_current_tenant: ContextVar[uuid.UUID | None] = ContextVar("current_tenant", default=None)

# Nome do parâmetro de sessão usado pela política RLS. Mantido em um só lugar.
DB_TENANT_PARAM = "app.tenant_id"


def get_current_tenant() -> uuid.UUID | None:
    return _current_tenant.get()


def set_db_tenant(tenant_id: uuid.UUID | None) -> None:
    """Aplica (ou limpa) o `app.tenant_id` na conexão atual via SET LOCAL.

    Requer estar dentro de uma transação (garantido por ATOMIC_REQUESTS). Usa
    `set_config(..., is_local => true)` para valer só até o fim da transação.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT set_config(%s, %s, true)",
            [DB_TENANT_PARAM, str(tenant_id) if tenant_id else ""],
        )


@contextlib.contextmanager
def use_tenant(tenant_id: uuid.UUID | None):
    """Define o tenant corrente (app + banco) dentro do bloco.

    Abre uma transação para que o `SET LOCAL app.tenant_id` persista em todas as
    queries do bloco (fora do ciclo de requisição não há transação garantida).
    Útil em testes, comandos e workers.
    """
    token = _current_tenant.set(tenant_id)
    try:
        with transaction.atomic():
            set_db_tenant(tenant_id)
            yield
    finally:
        _current_tenant.reset(token)
