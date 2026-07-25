# Novo Módulo: <nome> (`<context>`)

> Siga o padrão de documentação em [`docs/CONTRIBUTING-DOCS.md`](../../docs/CONTRIBUTING-DOCS.md)
> e as fronteiras em [`docs/architecture/modules.md`](../../docs/architecture/modules.md).

## Objetivo
O que este bounded context resolve e seus limites.

## Contexto
Por que existe; dependências permitidas (context map).

## Entidades / Agregados
Raiz de agregado, entidades, VOs e invariantes.

## APIs
Recursos REST conforme [diretrizes de API](../../docs/api/api_guidelines.md).

## Eventos
Eventos produzidos/consumidos (via Outbox) — ver [events](../../docs/architecture/events.md).

## Multi-tenant
Como o `tenant_id` e a RLS se aplicam ([multi-tenant](../../docs/architecture/multi-tenant.md)).

## Testes
Unitários, integração e **isolamento de tenant** ([testes](../../docs/testing/testing-strategy.md)).

## Decisões / Impacto / Evolução futura / Referências
