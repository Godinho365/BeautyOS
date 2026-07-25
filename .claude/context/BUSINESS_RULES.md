# Regras de Negócio (resumo)

> **SSOT:** módulos em [`docs/architecture/modules.md`](../../docs/architecture/modules.md);
> isolamento em [`docs/architecture/multi-tenant.md`](../../docs/architecture/multi-tenant.md).
> Resumo operacional para o Claude Code.

- Cada **Empresa (tenant)** possui isolamento **completo** dos dados.
- Módulos são bounded contexts independentes e de baixo acoplamento; a **lista canônica** é
  definida por [ADR-0004](../../docs/decisions/0004-canonical-modules.md) — inclui, entre outros,
  Agenda, CRM, Financeiro, **Estoque**, Marketing/Fidelidade, IA e **Marketplace**.
- Comunicação entre módulos por **domain events** ([`docs/architecture/events.md`](../../docs/architecture/events.md)).
- Termos de negócio seguem o [`docs/glossary.md`](../../docs/glossary.md).
