# Multi-Tenant (resumo)

> **SSOT:** ver [`docs/architecture/multi-tenant.md`](../../docs/architecture/multi-tenant.md).
> Resumo operacional para o Claude Code — **não** redefina a estratégia aqui.

- Banco compartilhado com `tenant_id` em toda entidade de negócio, reforçado por **RLS** no
  PostgreSQL ([ADR-0003](../../docs/decisions/0003-tenancy-shared-db-rls.md)).
- **RBAC por Empresa**: ver [`docs/security/security.md`](../../docs/security/security.md).
- `tenant_id` vem do token/sessão — **nunca** do cliente.
