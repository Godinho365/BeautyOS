---
title: "Architecture Decision Records (ADRs)"
type: moc
status: ativo
owner: Arquitetura
updated: 2026-07-24
tags: [adr, decisao]
---

# Architecture Decision Records (ADRs)

> **Status:** Ativo · **Dono:** Arquitetura · **Última atualização:** 2026-07-24

## Objetivo

Registrar, de forma imutável e rastreável, as **decisões arquiteturais** do BeautyOS: contexto,
alternativas, escolha e consequências. Nenhuma decisão arquitetural relevante deve existir
apenas no código ou em conversas.

## Como usar

- **Nova decisão:** copie o [template](template.md), use o próximo número sequencial e abra um PR.
- **Mudou de ideia?** Não apague o ADR: crie um novo que o **substitui** e marque o antigo como
  `Descontinuado`/`Substituído por ADR-XXXX`.
- Formato adotado: **MADR** (ver [CONTRIBUTING-DOCS](../CONTRIBUTING-DOCS.md)).

## Índice

| ADR | Título | Status |
|---|---|---|
| [0001](0001-monolith-modular.md) | Iniciar como Monólito Modular | Aceito |
| [0002](0002-postgresql-primary-db.md) | PostgreSQL como banco primário | Aceito |
| [0003](0003-tenancy-shared-db-rls.md) | Tenancy: banco compartilhado + `tenant_id` + RLS | Aceito |
| [0004](0004-canonical-modules.md) | Lista canônica de módulos (bounded contexts) | Aceito |
| [0005](0005-outbox-pattern.md) | Outbox Pattern para domain events | Aceito |

## Referências

- [MADR](https://adr.github.io/madr/) · [adr.github.io](https://adr.github.io/)
