# Arquitetura (resumo)

> **SSOT:** ver [`docs/architecture/overview.md`](../../docs/architecture/overview.md).
> Este arquivo é apenas um resumo operacional para o Claude Code — **não** edite a arquitetura aqui.

- **Estilo:** Monólito Modular ([ADR-0001](../../docs/decisions/0001-monolith-modular.md)),
  evolução futura para microsserviços.
- **Stack:** Django + DRF · PostgreSQL (RLS) · Redis · Celery · Docker · Next.js · Flutter.
- **Módulos:** ver [`docs/architecture/modules.md`](../../docs/architecture/modules.md).
- **Multi-tenant:** ver [`docs/architecture/multi-tenant.md`](../../docs/architecture/multi-tenant.md).

Detalhes, diagramas C4 e trade-offs estão na documentação de engenharia (`docs/`).
