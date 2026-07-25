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
- **Módulo `catalog` (Catálogo de Serviços)**: entidade `Service` (duração + preço em centavos)
  isolada por tenant (RLS), endpoints `/api/v1/services` (listar/criar/detalhar) e 3 testes de
  isolamento. Segue o padrão do walking skeleton. Ver [modules.md](docs/architecture/modules.md).
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
