---
title: "Visão do Produto"
type: product
status: ativo
owner: Produto
updated: 2026-07-24
tags: [produto]
---

# Visão do Produto

> **Status:** Ativo · **Dono:** Produto · **Última atualização:** 2026-07-24

## Objetivo

Construir o **sistema operacional do mercado da beleza**: uma plataforma SaaS que centraliza a
gestão de salões, barbearias, clínicas de estética e redes, do agendamento à inteligência de
negócio.

## Contexto

O setor é fragmentado, majoritariamente pequenos negócios, com ferramentas isoladas (agenda,
financeiro, marketing em apps separados). O BeautyOS unifica isso em uma plataforma
**multi-tenant, modular e API-first** ([arquitetura](../architecture/overview.md)), com **IA como
diferencial** ([copilot](../ai/copilot.md)).

## Proposta de valor

- **Para o dono/gestor:** visão única do negócio, menos ferramentas, mais faturamento.
- **Para o profissional:** agenda e comissões claras no app ([mobile](../../.claude/skills/mobile.md)).
- **Para o cliente final:** agendar e ser lembrado de forma simples (inclusive via Marketplace).

## Público-alvo

Salões, barbearias, clínicas de estética e redes — do autônomo à operação com múltiplas filiais
(atendidos pelo mesmo modelo multi-tenant que escala a centenas de milhares de Empresas).

## Diferenciais

1. **IA/Copilot** como gerente virtual de crescimento.
2. **Modularidade**: a Empresa ativa só o que precisa ([módulos](../architecture/modules.md)).
3. **Marketplace** de descoberta e agendamento público.
4. **API-first**: integrações e ecossistema.

## Exemplos de resultado esperado

- Reduzir faltas (_no-show_) com lembretes automáticos ([notificações](../architecture/modules.md)).
- Aumentar recompra com fidelidade e campanhas segmentadas por CRM.

## Boas práticas

- Priorizar por fase do [roadmap](../../.claude/context/ROADMAP.md) e valor ao cliente.
- Toda decisão de escopo respeita as fronteiras de módulo.

## Más práticas

- ❌ Recursos que acoplam módulos por conveniência de UI.
- ❌ Otimizar para o autônomo quebrando o caso de redes (ou vice-versa).

## Impacto

Define a direção que orienta arquitetura, roadmap e priorização.

## Evolução futura

- Marketplace e ecossistema de integrações como motor de aquisição.
- Expansão internacional (multi-idioma/moeda) sobre a base multi-tenant.

## Referências

- [Arquitetura](../architecture/overview.md) · [Módulos](../architecture/modules.md) · [Roadmap](../../.claude/context/ROADMAP.md)
