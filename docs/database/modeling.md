---
title: "Modelagem de Banco de Dados"
type: database
status: ativo
owner: Backend
updated: 2026-07-24
tags: [banco, dados]
---

# Modelagem de Banco de Dados

> **Status:** Ativo · **Dono:** Backend · **Última atualização:** 2026-07-24

## Objetivo

Definir as convenções de modelagem no PostgreSQL que garantem isolamento por tenant,
integridade, performance e evolução segura do schema.

## Contexto

Banco primário é **PostgreSQL** ([ADR-0002](../decisions/0002-postgresql-primary-db.md)). O
isolamento por tenant (`tenant_id` + RLS) é definido em
[multi-tenant.md](../architecture/multi-tenant.md) — **SSOT**; aqui aplicamos suas convenções ao
schema.

## Responsabilidades

- **Toda entidade de negócio** carrega `tenant_id` e o inclui nos índices.
- Migrações são versionadas, reversíveis e revisadas por PR.

## Convenções

| Tema | Convenção |
|---|---|
| Chave primária | `uuid` (`gen_random_uuid()`), evita colisão e vazamento de volume. |
| Tenant | `tenant_id uuid NOT NULL` em toda tabela de negócio; **1ª coluna** dos índices compostos. |
| Nomes | Tabelas no singular `snake_case` (`appointment`), FKs `<entidade>_id`. |
| Auditoria | `created_at`, `updated_at` (timestamptz); soft-delete quando exigido por LGPD. |
| Dinheiro | inteiro em centavos + moeda, **nunca** float. |
| Semiestruturado | `JSONB` para dados flexíveis; indexar o que for consultado. |

## Exemplo

```sql
CREATE TABLE ticket (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id  uuid NOT NULL REFERENCES company(id),
    customer_id uuid NOT NULL,
    total_cents bigint NOT NULL DEFAULT 0,
    currency   char(3) NOT NULL DEFAULT 'BRL',
    status     text NOT NULL DEFAULT 'open',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_ticket_tenant_status ON ticket (tenant_id, status);
-- RLS: ver docs/architecture/multi-tenant.md
```

## Boas práticas

- Índices compostos sempre iniciando por `tenant_id`.
- FKs para integridade; `ON DELETE` explícito e coerente com LGPD.
- Particionar por `tenant_id`/tempo tabelas de alto volume (agendamentos, movimentos de estoque).
- Migrações em duas fases para mudanças incompatíveis (expand/contract).

## Más práticas

- ❌ Tabela de negócio sem `tenant_id`.
- ❌ `float` para valores monetários.
- ❌ Índice que ignora `tenant_id` (leitura cruza tenants no plano).
- ❌ Migração destrutiva sem etapa reversível.

## Impacto

Determina performance sob multi-tenancy e a segurança do isolamento; escolhas ruins de índice
degradam todos os tenants.

## Evolução futura

- Particionamento declarativo e réplicas de leitura.
- `pgvector` para busca semântica da [IA](../ai/copilot.md).
- Estratégia de sharding por tenant para volume enterprise.

## Referências

- [Multi-Tenant](../architecture/multi-tenant.md) · [ADR-0002](../decisions/0002-postgresql-primary-db.md)
- [Modelo de Domínio](../architecture/domain-model.md)
