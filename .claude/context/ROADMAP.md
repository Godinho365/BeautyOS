# Roadmap

> Fases alinhadas à lista canônica de módulos ([ADR-0004](../../docs/decisions/0004-canonical-modules.md) /
> [`docs/architecture/modules.md`](../../docs/architecture/modules.md)). Resumo operacional.

| Fase | Foco | Módulos (contexts) |
|---|---|---|
| **1 — Fundação** | Operação básica do salão | `identity`, `tenant`, `catalog`, `staff`, `scheduling` |
| **2 — Monetização** | Dinheiro e relacionamento | `finance`, `commissions`, `crm`, `inventory` |
| **3 — Crescimento** | Retenção e inteligência | `marketing`, `notifications`, `ai` (Copilot) |
| **4 — Ecossistema** | Aquisição e escala | `marketplace`, integrações públicas (API/webhooks) |

Cada fase só é considerada pronta com documentação, testes, segurança, performance e
observabilidade conforme o [checklist](../checklists/feature.md).
