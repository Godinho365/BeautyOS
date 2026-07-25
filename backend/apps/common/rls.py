"""Utilitário para habilitar Row-Level Security (RLS) em tabelas de negócio.

Gera as operações de migração que ativam a RLS e criam a política de isolamento
por tenant, lendo `current_setting('app.tenant_id')` (definido pelo
TenantMiddleware). Ver docs/architecture/multi-tenant.md.

Uso numa migração:

    from apps.common.rls import enable_rls
    operations = [
        migrations.CreateModel(...),
        *enable_rls("tenant_branch"),
    ]
"""
from __future__ import annotations

from django.db import migrations

from .tenant_context import DB_TENANT_PARAM


def enable_rls(table: str):
    """Retorna operações que ativam RLS + política de isolamento na `table`.

    A política compara `tenant_id` da linha com o parâmetro de sessão. Usa
    `current_setting(param, true)` (o `true` evita erro se o parâmetro não
    estiver setado — nesse caso NULL, e nenhuma linha casa: nega por padrão).
    """
    policy = f"""
        ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
        ALTER TABLE {table} FORCE ROW LEVEL SECURITY;
        DROP POLICY IF EXISTS tenant_isolation ON {table};
        CREATE POLICY tenant_isolation ON {table}
            USING (tenant_id = NULLIF(current_setting('{DB_TENANT_PARAM}', true), '')::uuid)
            WITH CHECK (tenant_id = NULLIF(current_setting('{DB_TENANT_PARAM}', true), '')::uuid);
    """
    reverse = f"""
        DROP POLICY IF EXISTS tenant_isolation ON {table};
        ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;
    """
    return [migrations.RunSQL(sql=policy, reverse_sql=reverse)]
