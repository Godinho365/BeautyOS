---
title: "ADR-0004: Lista canônica de módulos (Bounded Contexts)"
type: decision
status: aceito
owner: Arquitetura
updated: 2026-07-24
tags: [adr, decisao]
---

# ADR-0004: Lista canônica de módulos (Bounded Contexts)

> **Status:** Aceito
> **Data:** 2026-07-24 · **Decisores:** Arquitetura, Produto

## Contexto e problema

A documentação anterior listava módulos de forma **conflitante**: `BUSINESS_RULES.md` citava
`Estoque` (sem Marketplace), enquanto `modules.md` citava `Marketplace` (sem Estoque). Sem uma
lista canônica, módulos, roadmap e modelo de domínio divergem. Precisamos de **uma** lista
oficial de bounded contexts que sirva de fonte única de verdade.

## Opções consideradas

- **Manter o conjunto mínimo atual** (apenas reconciliar os dois documentos existentes) — resolve
  o conflito, mas não descreve um SaaS de beleza completo.
- **Lista canônica expandida** — definir o conjunto de bounded contexts necessário para um
  produto de classe mundial no setor de beleza, cobrindo operação, financeiro, marketing e IA.

## Decisão

Adotamos a **lista canônica expandida** de bounded contexts. Ela é a fonte única de verdade,
detalhada em [architecture/modules.md](../architecture/modules.md):

| Módulo | Bounded Context | Responsabilidade central |
|---|---|---|
| Identidade/Auth | `identity` | Autenticação, usuários, sessões, tokens. |
| Tenant/Empresas | `tenant` | Empresas, unidades/filiais, planos/assinaturas. |
| Catálogo de Serviços | `catalog` | Serviços ofertados, durações, preços. |
| Profissionais | `staff` | Profissionais, agendas de trabalho, especialidades. |
| Agenda/Booking | `scheduling` | Agendamentos, disponibilidade, bloqueios. |
| CRM | `crm` | Clientes finais, histórico, segmentação. |
| Financeiro/Pagamentos | `finance` | Comandas, contas a pagar/receber, pagamentos. |
| Comissões | `commissions` | Cálculo e fechamento de comissões de profissionais. |
| Estoque | `inventory` | Produtos, entradas/saídas, saldo, consumo. |
| Marketing/Fidelidade | `marketing` | Campanhas, fidelidade, promoções. |
| IA/Copilot | `ai` | Copilotos, agentes, RAG, automações. |
| Marketplace | `marketplace` | Descoberta e agendamento público entre Empresas e Clientes. |
| Notificações | `notifications` | E-mail, SMS, push, WhatsApp; preferências. |

As dependências permitidas entre contextos e o _context map_ estão em
[modules.md](../architecture/modules.md).

## Consequências

### Positivas
- Elimina o conflito Estoque × Marketplace: **ambos** são módulos oficiais.
- Base consistente para roadmap, modelo de domínio e catálogo de eventos.

### Negativas / trade-offs
- Mais contextos exigem clareza de fronteiras para não acoplar módulos.

## Impacto

Alinha [modules.md](../architecture/modules.md), [domain-model.md](../architecture/domain-model.md),
[ROADMAP](../../.claude/context/ROADMAP.md) e as regras de negócio. Documentos que antes listavam
módulos passam a **referenciar** este ADR / `modules.md`, sem duplicar a lista.

## Referências

- [Módulos / Bounded Contexts](../architecture/modules.md)
- [Glossário](../glossary.md)
