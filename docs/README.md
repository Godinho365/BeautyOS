---
title: "Documentação do BeautyOS"
type: moc
status: ativo
owner: Arquitetura
updated: 2026-07-24
tags: [documentacao]
---

# Documentação do BeautyOS

> **Status:** Ativo · **Dono:** Arquitetura · **Última atualização:** 2026-07-24

Índice mestre da documentação de engenharia do BeautyOS — o **sistema operacional do mercado da
beleza**. Comece por aqui.

## Como navegar

- **Quer o mapa de conhecimento (Obsidian)?** Comece pelo [MOC raiz do Vault](_MOC.md).
- **Novo no projeto?** Leia [Visão do Produto](product/vision.md) → [Visão Geral da
  Arquitetura](architecture/overview.md) → [Glossário](glossary.md).
- **Vai escrever documentação?** Leia [Contribuindo com a Documentação](CONTRIBUTING-DOCS.md) e
  use o [template de documento](templates/document-template.md).
- **Vai tomar/entender uma decisão técnica?** Veja os [ADRs](decisions/README.md).

> [!note] README vs. MOC
> Este **README** é o *índice plano* de navegação. O [MOC raiz](_MOC.md) é o *mapa de
> conhecimento* do Obsidian (relações + backlinks). Os dois se complementam e não se duplicam.

## Mapa da documentação

### Produto
| Documento | Descrição |
|---|---|
| [Visão do Produto](product/vision.md) | Missão, público-alvo, proposta de valor. |

### Arquitetura
| Documento | Descrição |
|---|---|
| [Visão Geral (C4)](architecture/overview.md) | Estilo (monólito modular), stack, diagramas C4. |
| [Módulos / Bounded Contexts](architecture/modules.md) | **SSOT** da lista canônica de módulos e mapa de contextos. |
| [Multi-Tenant](architecture/multi-tenant.md) | **SSOT** de isolamento de dados por empresa. |
| [Modelo de Domínio](architecture/domain-model.md) | Agregados, entidades e invariantes por contexto. |
| [Catálogo de Eventos](architecture/events.md) | Domain events e Outbox Pattern. |

### API & Dados
| Documento | Descrição |
|---|---|
| [Diretrizes de API](api/api_guidelines.md) | REST, versionamento, erros, paginação, OpenAPI. |
| [Modelagem de Banco](database/modeling.md) | Convenções de schema, `tenant_id`, índices, migrações. |

### Qualidade & Operação
| Documento | Descrição |
|---|---|
| [Segurança](security/security.md) | AuthN/Z, RBAC, LGPD, OWASP, threat model. |
| [Observabilidade](observability/observability.md) | Logs, métricas, tracing, SLOs. |
| [Estratégia de Testes](testing/testing-strategy.md) | Pirâmide, cobertura, testes de contrato. |
| [Deploy & DevOps](devops/deploy.md) | 12-Factor, ambientes, CI/CD, IaC. |

### Inteligência Artificial
| Documento | Descrição |
|---|---|
| [Copilot / IA](ai/copilot.md) | Copilotos, agentes, RAG, guardrails, custos. |

### Decisões
| Documento | Descrição |
|---|---|
| [Índice de ADRs](decisions/README.md) | Todas as decisões arquiteturais registradas. |

## Convenções

Padrões de escrita, template obrigatório e política de **fonte única de verdade (SSOT)** estão
em [CONTRIBUTING-DOCS.md](CONTRIBUTING-DOCS.md). Termos de negócio seguem o
[Glossário](glossary.md).

## Relação com `.claude/`

O diretório `.claude/` contém o **contexto operacional do Claude Code** (skills, prompts,
checklists). Ele **não duplica** esta documentação: os arquivos de `.claude/context/` apontam
para os documentos de `docs/` como fonte única de verdade.
