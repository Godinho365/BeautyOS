# BeautyOS — Backend (walking skeleton)

Monólito modular (Django + DRF) com a fundação **multi-tenant** provada ponta a ponta:
`tenant_id` + **Row-Level Security (RLS)** no PostgreSQL. Ver
[docs/architecture/overview.md](../docs/architecture/overview.md) e
[docs/architecture/multi-tenant.md](../docs/architecture/multi-tenant.md).

> **Escopo deste skeleton:** apenas os módulos `identity` (auth/JWT) e `tenant`
> (Empresas + Unidades). Os demais bounded contexts existem como fronteiras a
> preencher — ver [docs/architecture/modules.md](../docs/architecture/modules.md).

## Estrutura

```
backend/
  config/            # projeto Django (settings, urls, api_v1, wsgi)
  apps/
    common/          # base multi-tenant: TenantScopedModel, middleware, RLS, contexto
    identity/        # User (global) + JWT
    tenant/          # Company (=tenant, global) + Branch (isolado por RLS)
  deploy/initdb/     # cria o role de aplicação NÃO-superusuário (RLS real)
  Dockerfile
```

## Como rodar (Docker Compose)

Na **raiz do repositório**:

```bash
# Portas do host são configuráveis (evita conflito com serviços locais):
DB_PORT=5544 BACKEND_PORT=8090 docker compose up --build
```

- API em `http://localhost:8090` (ou a porta que escolher).
- Health check: `GET /health`.
- As migrations rodam automaticamente na subida.

## Fluxo E2E (exemplo)

```bash
# 1. Autenticar (obter JWT)
curl -X POST http://localhost:8090/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"dono@salao.com","password":"senha123"}'

# 2. Listar Unidades do próprio tenant (isolado por RLS)
curl http://localhost:8090/api/v1/branches \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

## Testes

Os testes de **isolamento multi-tenant** exigem PostgreSQL (RLS não existe em
SQLite) e conectam como o role **não-superusuário** `beautyos_app` — caso
contrário a RLS seria ignorada (ver [ADR-0003](../docs/decisions/0003-tenancy-shared-db-rls.md)).

```bash
# Sobe um Postgres, cria o role de app e roda a suíte:
docker run -d --name bos-test -e POSTGRES_USER=beautyos -e POSTGRES_PASSWORD=beautyos \
  -e POSTGRES_DB=beautyos -p 5544:5432 postgres:16
docker exec -i bos-test psql -U beautyos -d beautyos < deploy/initdb/01-app-role.sql

pip install -r requirements.txt
DATABASE_URL=postgres://beautyos_app:beautyos_app@localhost:5544/beautyos \
DJANGO_SECRET_KEY=dev python -m pytest
```

A mesma suíte roda na CI ([.github/workflows/ci.yml](../.github/workflows/ci.yml)).

## Decisão-chave: RLS só funciona sem superusuário

O PostgreSQL **ignora RLS para superusuários e roles com `BYPASSRLS`**. Por isso o
app conecta como `beautyos_app` (`NOSUPERUSER`, `NOBYPASSRLS`), e as tabelas de
negócio usam `FORCE ROW LEVEL SECURITY` (aplica a política inclusive ao dono).
Ver [apps/common/rls.py](apps/common/rls.py) e
[deploy/initdb/01-app-role.sql](deploy/initdb/01-app-role.sql).
