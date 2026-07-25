---
title: Changelog
type: governance
status: ativo
owner: Engenharia
updated: 2026-07-24
tags: [changelog, historico]
---

# Changelog

Todas as mudanças relevantes da documentação/plataforma são registradas aqui.
Formato inspirado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/);
versionamento futuro seguirá [SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- **Comando `seed_demo`** (`python manage.py seed_demo`): cria tenant, usuário
  (`demo@beautyos.dev`/`demo12345`), serviços, profissionais, clientes e um agendamento de
  exemplo — idempotente. Destrava o smoke E2E do painel. **Verificado ponta a ponta**: login no
  painel Next.js → dashboard exibindo os dados semeados (browser → API JWT/CORS → Django → RLS).
- **Painel Web (Next.js)** em `frontend/`: app App Router + TypeScript com **login JWT** e
  dashboard que consome `/api/v1` (lista serviços/agendamentos, cria serviço). Cliente HTTP
  central (`lib/api.ts`) com Bearer + tratamento de 401. Backend ganha **CORS**
  (`django-cors-headers`, `CORS_ALLOWED_ORIGINS`). Serviço `frontend` no `docker-compose`.
  Build validado (`npm run build`). Ver [docs/frontend/overview.md](docs/frontend/overview.md).
- **Relay assíncrono do Outbox via Celery** (quita a dívida do relay síncrono): `config/celery.py`,
  tarefa `apps.common.tasks.process_outbox` agendada pelo **Celery beat** (a cada 10s). Adiciona
  serviços `redis` e `worker` ao `docker-compose.yml`. O comando `process_outbox` permanece para
  dev/CI. Ver [events.md](docs/architecture/events.md) e [deploy.md](docs/devops/deploy.md).
- **Módulo `commissions` (Comissões)**: `CommissionRule` (percentual em bps, por profissional
  ou padrão do tenant) + `Commission` (RLS). **Consome `TicketClosed`** e calcula a comissão do
  profissional do atendimento — idempotente por `source_event_id`. Endpoints
  `/api/v1/commission-rules` e `/api/v1/commissions`. `TicketClosed` passa a ter **dois
  consumidores** (estoque + comissões); payload ganha `appointment_id` e
  `scheduling.contracts.get_professional_id`.
- **Módulo `inventory` (Estoque)**: `Product` + `StockMovement` (RLS). Ajuste de estoque com
  invariante de saldo não-negativo (`/api/v1/products` + action `adjust`). **Consome `TicketClosed`**
  (`inventory.handlers.on_ticket_closed`) dando baixa nos produtos vendidos — idempotente por
  `source_event_id`. Adiciona `product_id` ao `TicketItem` (finance) + `finance.contracts.get_product_lines`.
- **Módulo `finance` (Comanda/Pagamento)**: `Ticket` + `TicketItem` + `Payment` (RLS).
  Use cases `open/add_item/register_payment/close_ticket` com invariantes reais (comanda
  fechada é imutável; só fecha com total > 0 e paga >= total). Emite `TicketClosed` via
  Outbox (consumidores futuros: estoque, comissões). Endpoints `/api/v1/tickets`
  (+ actions `items`, `payments`, `close`). 6 testes contra Postgres.
- **Módulo `crm` (Clientes finais)**: entidade `Customer` isolada por tenant (RLS), endpoints
  `/api/v1/customers`. O `Appointment` passa a referenciar `customer_id` real (via
  `crm.contracts`), substituindo o `customer_name` denormalizado.
- **Transactional Outbox + domain events** (ADR-0005): `OutboxEvent` + `record_event` +
  relay `process_pending`/comando `process_outbox`; registro de handlers em `common/events.py`.
  `book_appointment` emite `AppointmentBooked` na mesma transação.
- **Módulo `notifications`**: `Notification` (RLS) + handler idempotente que cria a confirmação
  ao consumir `AppointmentBooked`; endpoint `/api/v1/notifications`.
- **Módulo `scheduling` (Agenda/Booking)**: entidade `Appointment` (referencia `Service`/
  `Professional` por ID). Primeira regra de negócio real — **não-sobreposição por profissional** —
  em duas camadas: use case `book_appointment` (Service Layer) + constraint `EXCLUDE` (btree_gist)
  no PostgreSQL. Endpoints `/api/v1/appointments`; 6 testes (incl. constraint do banco e
  isolamento). Introduz o padrão `contracts.py` para dependência entre módulos sem acoplar ORM.
- **Módulo `staff` (Profissionais)**: entidade `Professional` isolada por tenant (RLS), endpoints
  `/api/v1/professionals` (listar/criar/detalhar) e 3 testes de isolamento.
- **Módulo `catalog` (Catálogo de Serviços)**: entidade `Service` (duração + preço em centavos)
  isolada por tenant (RLS), endpoints `/api/v1/services` (listar/criar/detalhar) e 3 testes de
  isolamento. Segue o padrão do walking skeleton. Ver [modules.md](docs/architecture/modules.md).

### Alterado
- **API v1 usa um único `DefaultRouter` compartilhado** (cada módulo contribui via
  `register(router)` em `routes.py`), eliminando o `RemovedInDjango60Warning` de conversor de
  sufixo registrado em duplicidade.
- **Backend — walking skeleton multi-tenant** (`backend/`): monólito modular Django+DRF com
  módulos `identity` (JWT) e `tenant` (Company + Branch). Isolamento por `tenant_id` + **RLS**
  provado ponta a ponta contra PostgreSQL, com role de aplicação não-superusuário
  (`beautyos_app`). Inclui `docker-compose.yml`, `Dockerfile` e job de CI `backend-tests`
  (Postgres + pytest). Ver [backend/README.md](backend/README.md).

- Fundação **docs-as-code**: [padrão de documentação](docs/CONTRIBUTING-DOCS.md),
  [índice do Vault](docs/README.md) e [glossário](docs/glossary.md).
- **Governança**: [Engineering Constitution](CLAUDE.md) e [Definition of Done](DEFINITION_OF_DONE.md).
- **ADRs** (MADR): [0001](docs/decisions/0001-monolith-modular.md)–[0005](docs/decisions/0005-outbox-pattern.md)
  e [índice](docs/decisions/README.md).
- **Documentos-farol**: [arquitetura C4](docs/architecture/overview.md),
  [multi-tenant](docs/architecture/multi-tenant.md), [módulos](docs/architecture/modules.md),
  [segurança](docs/security/security.md), [API](docs/api/api_guidelines.md).
- **Novos docs**: [modelo de domínio](docs/architecture/domain-model.md),
  [eventos](docs/architecture/events.md), [observabilidade](docs/observability/observability.md),
  [estratégia de testes](docs/testing/testing-strategy.md).
- **Obsidian**: [MOC raiz do Vault](docs/_MOC.md), [MOC de Arquitetura](docs/architecture/_MOC.md)
  e [template de documento](docs/templates/document-template.md).
- **Tooling/CI**: repositório Git inicializado; `.gitignore`/`.gitattributes`; validador de docs
  (`scripts/validate_docs.py`) e workflow de CI (`.github/workflows/ci.yml`) com lint de
  documentação (links, fences, frontmatter) + placeholder de testes.

### Alterado
- Reescrita ao padrão completo de `product/vision`, `database/modeling`, `devops/deploy`,
  `ai/copilot` e do `README.md` raiz.
- `.claude/context/*` reduzido a resumo + link, apontando para `docs/` como **SSOT**.
- `.claude/` (skills, prompt, template, checklist) alinhados aos documentos canônicos.

### Corrigido
- **Conflito de módulos** Estoque × Marketplace: unificados na lista canônica
  ([ADR-0004](docs/decisions/0004-canonical-modules.md)); ambos passam a ser módulos oficiais.
- Duplicação de arquitetura e de multi-tenant eliminada via política SSOT.

### Movido
- `docs/modules/modules.md` → [`docs/architecture/modules.md`](docs/architecture/modules.md).
- `.claude/decisions/0001-monolith.md` → [`docs/decisions/0001-monolith-modular.md`](docs/decisions/0001-monolith-modular.md).

## Referências

- [Definition of Done](DEFINITION_OF_DONE.md) · [Constitution](CLAUDE.md)
