---
title: "Catálogo de Eventos de Domínio"
type: architecture
status: rascunho
owner: Arquitetura
updated: 2026-07-24
tags: [arquitetura]
---

# Catálogo de Eventos de Domínio

> **Status:** Rascunho estruturado · **Dono:** Arquitetura · **Última atualização:** 2026-07-24

## Objetivo

Catalogar os **domain events** que integram os módulos e definir como são publicados de forma
confiável (**Outbox Pattern**).

## Contexto

No monólito modular, módulos comunicam-se por eventos assíncronos, mantendo baixo acoplamento
([modules.md](modules.md)). A entrega confiável usa o Outbox ([ADR-0005](../decisions/0005-outbox-pattern.md)),
com semântica **at-least-once** e consumidores **idempotentes**.

## Responsabilidades

- **Produtor:** gravar o evento na `outbox` na mesma transação do agregado.
- **Relay (Celery):** publicar aos consumidores e marcar como enviado.
- **Consumidor:** processar de forma idempotente.

## Convenções de nomenclatura

- Nome no **passado**: `AppointmentBooked`, `TicketClosed`.
- Envelope: `event_id`, `event_type`, `tenant_id`, `occurred_at`, `version`, `payload`.
- `event_id` serve de **chave de idempotência**.

## Catálogo inicial

| Evento | Produtor | Consumidores | Efeito |
|---|---|---|---|
| `AppointmentBooked` | `scheduling` | `notifications`, `crm` | Confirma ao cliente; atualiza histórico. |
| `AppointmentCancelled` | `scheduling` | `notifications`, `crm` | Avisa; libera slot. |
| `TicketClosed` | `finance` | `inventory`, `commissions`, `crm` | Baixa estoque; gera comissão; histórico. |
| `PaymentConfirmed` | `finance` | `notifications` | Recibo ao cliente. |
| `ProductStockLow` | `inventory` | `notifications`, `ai` | Alerta e sugestão de reposição. |
| `CustomerCreated` | `crm` | `marketing` | Elegibilidade a campanhas/fidelidade. |

## Fluxo (Outbox)

```mermaid
sequenceDiagram
    participant UC as Caso de uso
    participant DB as PostgreSQL (agregado + outbox)
    participant RL as Relay (Celery)
    participant CS as Consumidor
    UC->>DB: BEGIN; salva agregado + insere evento na outbox; COMMIT
    RL->>DB: lê eventos pendentes
    RL->>CS: publica evento
    CS-->>RL: ack (idempotente)
    RL->>DB: marca como enviado
```

## Exemplo (envelope)

```json
{
  "event_id": "3f2b...",
  "event_type": "AppointmentBooked",
  "tenant_id": "9ab...",
  "occurred_at": "2026-07-24T12:00:00Z",
  "version": 1,
  "payload": { "appointment_id": "…", "customer_id": "…", "starts_at": "2026-08-01T14:00:00Z" }
}
```

## Boas práticas

- Consumidores idempotentes (dedupe por `event_id`).
- Versionar o `payload`; mudanças aditivas mantêm compatibilidade.
- Monitorar o **lag** do relay ([observabilidade](../observability/observability.md)).

## Más práticas

- ❌ Publicar direto no broker dentro da transação (dual write).
- ❌ Evento no presente/imperativo (`BookAppointment`) — isso é comando, não evento.
- ❌ Assumir entrega **exactly-once**.

## Impacto

Desacopla módulos e prepara a extração para microsserviços; custo: eventual duplicidade e
latência de propagação.

## Evolução futura

- Publicar **webhooks** externos assinados a partir do mesmo Outbox.
- Broker dedicado (Kafka/RabbitMQ) quando houver serviços separados.
- Esquema de eventos versionado em registro central.

## Referências

- [ADR-0005: Outbox](../decisions/0005-outbox-pattern.md) · [Módulos](modules.md)
- [microservices.io — Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html)
