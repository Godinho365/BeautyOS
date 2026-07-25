---
title: "ADR-0002: PostgreSQL como banco de dados primário"
type: decision
status: aceito
owner: Arquitetura
updated: 2026-07-24
tags: [adr, decisao]
---

# ADR-0002: PostgreSQL como banco de dados primário

> **Status:** Aceito
> **Data:** 2026-07-24 · **Decisores:** Arquitetura, Backend

## Contexto e problema

O BeautyOS é transacional e multi-tenant: agendamentos, comandas, financeiro e estoque exigem
**consistência forte**, integridade referencial e isolamento confiável de dados por empresa.
Precisamos de um armazenamento primário que suporte esses requisitos e escale para muitos
tenants, além de recursos que apoiem o isolamento (ver [ADR-0003](0003-tenancy-shared-db-rls.md)).

## Opções consideradas

- **PostgreSQL** — relacional, ACID, RLS nativo, JSONB, extensões (particionamento, `pg_trgm`,
  `pgvector`), ecossistema maduro com Django.
- **MySQL/MariaDB** — relacional maduro, mas RLS/JSON e extensibilidade inferiores para nosso caso.
- **Banco NoSQL (ex.: MongoDB)** — flexível em schema, porém consistência transacional
  multi-documento e integridade referencial mais frágeis para dados financeiros.

## Decisão

Adotamos **PostgreSQL** como banco primário de todos os módulos do monólito. Recursos-chave
que exploramos: **Row-Level Security (RLS)** para reforço de isolamento por tenant, **JSONB**
para campos semiestruturados, particionamento para tabelas de alto volume e **pgvector** para
busca semântica do [Copilot/IA](../ai/copilot.md).

## Consequências

### Positivas
- Consistência forte e integridade para financeiro/estoque/agenda.
- RLS oferece uma segunda linha de defesa de isolamento além do filtro por `tenant_id`.
- Um só motor reduz custo operacional no monólito modular ([ADR-0001](0001-monolith-modular.md)).

### Negativas / trade-offs
- Escala de escrita é primariamente vertical + réplicas de leitura; _sharding_ por tenant exige
  esforço deliberado quando chegarmos a esse volume.

### Riscos e mitigações
- **Risco:** _hotspots_ em tabelas globais de alto volume. **Mitigação:** particionamento e
  índices compostos iniciando por `tenant_id` (ver [modelagem](../database/modeling.md)).

## Impacto

Base para [multi-tenant](../architecture/multi-tenant.md), [modelagem](../database/modeling.md)
e busca semântica da [IA](../ai/copilot.md).

## Referências

- [Multi-Tenant](../architecture/multi-tenant.md) · [Modelagem de Banco](../database/modeling.md)
- [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [pgvector](https://github.com/pgvector/pgvector)
