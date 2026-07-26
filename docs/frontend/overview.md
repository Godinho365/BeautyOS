---
title: "Painel Web (Next.js)"
type: frontend
status: rascunho
owner: Frontend
updated: 2026-07-25
tags: [frontend, web, nextjs]
---

# Painel Web (Next.js)

## Objetivo

Dar interface de gestão ao BeautyOS: o painel web que a Empresa usa para operar
(agenda, comandas, cadastros), consumindo a API `/api/v1`.

## Contexto

App **Next.js (App Router, TypeScript)** no monorepo (`frontend/`), separado do
backend Django. Autentica via **JWT** e conversa com a API por HTTP. É o primeiro
consumidor real do contrato de API ([api_guidelines](../api/api_guidelines.md)).

## Responsabilidades

- **Autenticação:** login (e-mail/senha → `/api/v1/auth/token`), guarda do token.
- **Telas de gestão:** listar/criar recursos escopados pelo tenant do usuário.
- **NÃO** contém regra de negócio — isso é do backend; o front apenas orquestra UI.

## Estrutura

```
frontend/
  app/
    layout.tsx        # shell + estilos globais
    page.tsx          # dashboard (Copilot/insights + serviços)
    agenda/page.tsx   # agenda: lista + form de agendamento
    comandas/page.tsx # comandas: abrir, itens, pagamento, fechar
    login/page.tsx    # login JWT
    components/Nav.tsx # navegação (Dashboard/Agenda/Comandas/Sair)
  lib/
    api.ts            # cliente HTTP (Bearer, 401, api.list desempacota paginação)
    auth.ts           # token no localStorage
```

## Autenticação (walking skeleton)

- Login troca e-mail/senha por um **access token** JWT, guardado em `localStorage`.
- `lib/api.ts` injeta `Authorization: Bearer` e, em `401`, limpa o token e manda ao login.

> [!warning] Dívida conhecida
> `localStorage` é suficiente para o esqueleto, mas expõe o token a XSS. Evoluir para
> **cookies httpOnly + refresh token** ao endurecer (ver [segurança](../security/security.md)).

## CORS

O browser só chama a API se a origem do painel estiver em `CORS_ALLOWED_ORIGINS`
(backend, via `django-cors-headers`). Default: `http://localhost:3000`.

## Como rodar

```bash
# tudo junto (backend + db + redis + worker + frontend):
DB_PORT=5544 BACKEND_PORT=8090 FRONTEND_PORT=3001 docker compose up --build
# ou só o front (backend rodando à parte):
cd frontend && npm install && npm run dev
```
Painel em `http://localhost:3000` (ou a porta escolhida).

## Boas práticas

- Todo acesso à API passa por `lib/api.ts` (um único ponto para token e erros).
- Tipos explícitos para as respostas da API.
- Componentes de tela são _client components_ só quando precisam de interação/estado.

## Más práticas

- ❌ Guardar regra de negócio no front (ex.: decidir se uma comanda pode fechar).
- ❌ Chamar `fetch` cru espalhado; sempre via `lib/api.ts`.
- ❌ Confiar em dados do token para autorização — o servidor é a autoridade.

## Impacto

Primeira superfície de valor para o usuário final; valida o contrato de API na prática.

## Evolução futura

- Cookies httpOnly + refresh; SSR autenticado.
- Telas completas: agenda (calendário), comanda (itens/pagamento/fechar), estoque, relatórios.
- Design System e componentes reutilizáveis; testes (Playwright).
- Cliente de API gerado a partir do OpenAPI.

## Referências

- [Diretrizes de API](../api/api_guidelines.md) · [Segurança](../security/security.md)
- [Deploy & DevOps](../devops/deploy.md) · [Next.js](https://nextjs.org/docs)
