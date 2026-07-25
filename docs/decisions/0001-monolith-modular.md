---
title: "ADR-0001: Iniciar como Monólito Modular"
type: decision
status: aceito
owner: Arquitetura
updated: 2026-07-24
tags: [adr, decisao]
---

# ADR-0001: Iniciar como Monólito Modular

> **Status:** Aceito
> **Data:** 2026-07-24 · **Decisores:** Arquitetura, Tech Lead
> _Substitui o registro informal anterior em `.claude/decisions/0001-monolith.md`._

## Contexto e problema

O BeautyOS precisa chegar rápido ao mercado com um ERP modular para o setor de beleza, ao mesmo
tempo em que se prepara para escalar para centenas de milhares de empresas. Precisamos de uma
topologia de sistema que maximize velocidade de entrega e simplicidade operacional **agora**,
sem inviabilizar a evolução para serviços distribuídos **depois**.

## Opções consideradas

- **Monólito "big ball of mud"** — um único código sem fronteiras internas. Rápido no início,
  mas vira acoplamento e dívida rapidamente.
- **Monólito Modular** — uma aplicação implantável, dividida internamente em módulos/bounded
  contexts com baixo acoplamento e fronteiras explícitas.
- **Microsserviços desde o dia 1** — cada contexto como serviço independente. Máxima
  independência, mas alto custo operacional (rede, observabilidade, consistência distribuída)
  antes de haver escala que o justifique.

## Decisão

Adotamos o **Monólito Modular**: uma única aplicação (Django + DRF) organizada em módulos que
correspondem aos bounded contexts (ver [modules.md](../architecture/modules.md)). Cada módulo
expõe uma interface clara e comunica-se com os demais por contratos e **domain events**, não por
acesso direto a tabelas de outro módulo.

## Consequências

### Positivas
- Velocidade de desenvolvimento e um único pipeline de deploy.
- Transações e consistência simples (um banco), reduzindo complexidade inicial.
- Fronteiras internas já preparadas para extração futura de serviços.

### Negativas / trade-offs
- Escala apenas verticalmente/replicando o monólito inteiro (não por contexto isoladamente).
- Exige **disciplina** para não vazar fronteiras entre módulos (risco de virar monólito acoplado).

### Riscos e mitigações
- **Risco:** acoplamento acidental entre módulos. **Mitigação:** dependências permitidas
  documentadas em [modules.md](../architecture/modules.md), comunicação via eventos
  ([events.md](../architecture/events.md)) e revisão de PR.

## Impacto

Fundamenta toda a [arquitetura](../architecture/overview.md). A extração para microsserviços,
quando um contexto exigir escala ou ciclo de vida próprios, será registrada em um ADR futuro,
apoiada pelo isolamento já existente (módulos + eventos + Outbox — ver
[ADR-0005](0005-outbox-pattern.md)).

## Referências

- [Visão Geral da Arquitetura](../architecture/overview.md)
- [Módulos / Bounded Contexts](../architecture/modules.md)
- Sam Newman, _Monolith to Microservices_.
