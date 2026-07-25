---
title: "ADR-0005: Outbox Pattern para publicação de Domain Events"
type: decision
status: aceito
owner: Arquitetura
updated: 2026-07-24
tags: [adr, decisao]
---

# ADR-0005: Outbox Pattern para publicação de Domain Events

> **Status:** Aceito
> **Data:** 2026-07-24 · **Decisores:** Arquitetura, Backend

## Contexto e problema

Os módulos do monólito modular ([ADR-0001](0001-monolith-modular.md)) comunicam-se por **domain
events** (ex.: `AppointmentBooked` dispara notificação e atualização de CRM). Precisamos
publicar esses eventos de forma **confiável**: se a transação de negócio commitou, o evento
**tem** que ser entregue; se falhou, não pode "vazar". Publicar direto num broker dentro da
transação cria o problema de _dual write_ (banco e broker podem divergir).

## Opções consideradas

- **Publicar direto no broker durante a transação** — simples, mas sujeito a inconsistência:
  commit no banco e falha no broker (ou vice-versa).
- **Two-phase commit (XA)** — consistência distribuída, porém complexo, lento e mal suportado.
- **Transactional Outbox** — o evento é gravado **na mesma transação** do dado de negócio, numa
  tabela `outbox`; um _relay_ assíncrono lê e publica, marcando como enviado.

## Decisão

Adotamos o **Transactional Outbox Pattern**. Handlers de negócio gravam o evento na tabela
`outbox` dentro da mesma transação do agregado. Um worker (Celery) faz o _relay_ para os
consumidores (in-process no monólito hoje; broker externo quando extrairmos serviços),
garantindo entrega **at-least-once**. Consumidores devem ser **idempotentes**. Detalhes em
[events.md](../architecture/events.md).

## Consequências

### Positivas
- Elimina _dual write_: consistência entre estado e eventos.
- Caminho natural para microsserviços — o mesmo Outbox alimenta um broker externo depois.

### Negativas / trade-offs
- Entrega **at-least-once** implica possibilidade de duplicatas → consumidores idempotentes.
- Latência de propagação (relay assíncrono) e necessidade de _cleanup_ da tabela `outbox`.

### Riscos e mitigações
- **Risco:** processamento duplicado. **Mitigação:** chave de idempotência por evento +
  deduplicação no consumidor.
- **Risco:** acúmulo na `outbox`. **Mitigação:** índice por status, arquivamento/purga periódica.

## Impacto

Fundamenta o [catálogo de eventos](../architecture/events.md) e o baixo acoplamento entre
[módulos](../architecture/modules.md). Requer observabilidade do _lag_ do relay (ver
[observabilidade](../observability/observability.md)).

## Referências

- [Catálogo de Eventos](../architecture/events.md)
- Chris Richardson, [Pattern: Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html)
