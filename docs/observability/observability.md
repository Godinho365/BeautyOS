---
title: "Observabilidade"
type: observability
status: rascunho
owner: Plataforma
updated: 2026-07-24
tags: [observabilidade]
---

# Observabilidade

> **Status:** Rascunho estruturado · **Dono:** Plataforma · **Última atualização:** 2026-07-24

## Objetivo

Definir como o BeautyOS é observado em produção — logs, métricas e tracing — para detectar,
diagnosticar e prevenir problemas, sempre com recorte por **tenant**.

## Contexto

Em um SaaS multi-tenant, incidentes precisam ser atribuíveis a um tenant sem vazar dados entre
eles. Observabilidade sustenta os SLOs e alimenta a detecção de anomalias de
[segurança](../security/security.md).

## Responsabilidades

- **Cada módulo:** emitir logs estruturados e métricas de negócio próprias.
- **Plataforma:** coletar, correlacionar (trace_id) e alertar.

## Os três pilares

| Pilar | O quê | Ferramenta (sugerida) |
|---|---|---|
| **Logs** | Eventos estruturados (JSON) com `tenant_id`, `trace_id`, `user_id`. | Stack de logs centralizada. |
| **Métricas** | RED (Rate, Errors, Duration) + métricas de negócio. | Prometheus/OpenMetrics. |
| **Tracing** | Rastro fim-a-fim de requisições e jobs. | OpenTelemetry. |

## SLOs iniciais (proposta)

| Indicador | Meta |
|---|---|
| Disponibilidade da API | 99,9% mensal |
| Latência `p95` de leitura | < 300 ms |
| Latência `p95` de escrita | < 800 ms |
| Lag do relay Outbox | < 30 s `p95` |

## Boas práticas

- **Nunca** logar dados pessoais/sensíveis ou tokens ([segurança](../security/security.md)).
- Propagar `trace_id` da API para workers e para os eventos do [Outbox](../architecture/events.md).
- Toda métrica/log carrega `tenant_id` para recorte e cobrança futura.
- Alertas acionáveis (ligados a um runbook), não ruído.

## Más práticas

- ❌ Log em texto livre não estruturado.
- ❌ Métrica sem dimensão de tenant.
- ❌ Alerta sem dono/runbook.

## Impacto

Boa observabilidade reduz MTTR e habilita cobrança/limites por tenant; custo: volume de
telemetria e cardinalidade de métricas.

## Evolução futura

- Detecção de anomalias por tenant.
- Painéis por módulo e por SLO; orçamento de erro (error budget).
- Amostragem adaptativa de tracing.

## Referências

- [OpenTelemetry](https://opentelemetry.io/) · [Google SRE — SLOs](https://sre.google/workbook/implementing-slos/)
- [Segurança](../security/security.md) · [Eventos](../architecture/events.md)
