---
title: "Diretrizes de API"
type: api
status: ativo
owner: Backend
updated: 2026-07-24
tags: [api]
---

# Diretrizes de API

> **Status:** Ativo · **Dono:** Backend · **Última atualização:** 2026-07-24

## Objetivo

Padronizar o design da API REST do BeautyOS para que seja consistente, previsível, versionável e
segura — o contrato entre backend, web, mobile e integrações de terceiros (API-first).

## Contexto

A API é a fronteira pública do monólito modular. Estabilidade e consistência aqui reduzem
retrabalho em todos os clientes ([overview](../architecture/overview.md)).

## Responsabilidades

- **Backend:** expor casos de uso como recursos REST estáveis e documentados em OpenAPI.
- **Clientes (web/mobile):** consumir o contrato versionado, sem depender de detalhes internos.

## Convenções

- **REST + JSON**, recursos no plural: `/api/v1/appointments`.
- **Versionamento** no path: `/api/v1`. Mudança incompatível → `/api/v2` (ver Evolução).
- **Verbos HTTP:** `GET` (ler), `POST` (criar), `PUT/PATCH` (atualizar), `DELETE` (remover).
- **Nomes** em `kebab-case` no path; campos JSON em `snake_case` (alinha com o backend).
- **Tenant** é derivado do token — **nunca** trafega em query string.

## Padrão de erros (RFC 9457 — Problem Details)

```json
{
  "type": "https://beautyos.dev/errors/validation",
  "title": "Dados inválidos",
  "status": 422,
  "detail": "O campo starts_at é obrigatório.",
  "errors": [{ "field": "starts_at", "message": "obrigatório" }],
  "trace_id": "a1b2c3"
}
```

| Situação | Status |
|---|---|
| Sucesso com corpo | `200` / criação `201` |
| Sucesso sem corpo | `204` |
| Entrada inválida | `422` |
| Não autenticado | `401` |
| Sem permissão | `403` |
| Não encontrado (ou fora do tenant) | `404` |
| Conflito/idempotência | `409` |
| Rate limit | `429` (com `Retry-After`) |

> Recurso de outro tenant retorna **`404`** (não `403`), para não revelar existência.

## Paginação, filtro e ordenação

- Paginação por cursor (preferida em alto volume): `?limit=50&cursor=...`.
- Resposta inclui `data` e `page` (`next_cursor`, `has_more`).
- Filtros por query param explícito; ordenação via `?sort=-starts_at`.

> [!note] Implementação de referência (endurecimento)
> **OpenAPI:** contrato em `GET /api/schema` e Swagger UI em `GET /api/docs` (drf-spectacular).
> **Paginação:** hoje `PageNumberPagination` (`PAGE_SIZE=50`), envelope
> `{count, next, previous, results}` — `?page=N`. Migração para **cursor** fica para o alto
> volume (evolução). **Rate limiting:** `UserRateThrottle`/`AnonRateThrottle` (DRF), `429` ao
> exceder. Config em `backend/config/settings.py` (`REST_FRAMEWORK`).

## Idempotência

- `POST` que cria recurso aceita header `Idempotency-Key`; repetição retorna o mesmo resultado
  (evita duplicidade em retries de rede — relevante para pagamentos e agendamentos).

## Segurança & limites

- **HTTPS** obrigatório; **JWT** no header `Authorization: Bearer` ([segurança](../security/security.md)).
- **Rate limiting** por tenant+usuário; respostas `429` com `Retry-After`.
- Validação de entrada estrita; sem vazar stack traces.

## Exemplos

```http
POST /api/v1/appointments
Authorization: Bearer <jwt>
Idempotency-Key: 6f1c...-a
Content-Type: application/json

{ "customer_id": "…", "professional_id": "…", "service_id": "…", "starts_at": "2026-08-01T14:00:00Z" }
```
```http
HTTP/1.1 201 Created
Location: /api/v1/appointments/9ab...
{ "id": "9ab...", "status": "booked", "starts_at": "2026-08-01T14:00:00Z" }
```

## Boas práticas

- Contrato **OpenAPI 3.1** é fonte de verdade da API; gerar/validar clientes a partir dele.
- Respostas consistentes (mesmo envelope de erro, mesma paginação em toda a API).
- Campos aditivos são retrocompatíveis; remover/renomear exige nova versão.

## Más práticas

- ❌ Verbo na URL (`/getAppointments`).
- ❌ `tenant_id` em query string.
- ❌ Retornar `200` com corpo de erro.
- ❌ Quebrar contrato sem versionar.

## Impacto

Consistência da API reduz custo de integração e bugs de cliente; idempotência e Problem Details
melhoram robustez de web/mobile em redes instáveis.

## Evolução futura

- Publicar OpenAPI e portal de desenvolvedores para integrações do [Marketplace](../architecture/modules.md).
- Webhooks assinados para eventos de domínio ([events.md](../architecture/events.md)).
- Avaliar GraphQL/BFF **apenas** se houver ganho comprovado para o mobile.

## Referências

- [RFC 9457 — Problem Details](https://www.rfc-editor.org/rfc/rfc9457)
- [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0) · [Segurança](../security/security.md)
