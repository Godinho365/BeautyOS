---
title: "ADR-0003: Estratégia de Tenancy — Banco compartilhado com `tenant_id` + RLS"
type: decision
status: aceito
owner: Arquitetura
updated: 2026-07-24
tags: [adr, decisao]
---

# ADR-0003: Estratégia de Tenancy — Banco compartilhado com `tenant_id` + RLS

> **Status:** Aceito
> **Data:** 2026-07-24 · **Decisores:** Arquitetura, Backend, Segurança

## Contexto e problema

O BeautyOS deve isolar completamente os dados de cada Empresa (tenant) e, ao mesmo tempo,
escalar para centenas de milhares de tenants com custo operacional viável. A estratégia de
tenancy determina isolamento, custo, complexidade de operação e caminho de escala.

## Opções consideradas

- **Banco por tenant** — isolamento máximo, mas milhares de bancos/migrações inviabilizam a
  operação nessa escala.
- **Schema por tenant** — bom isolamento, porém `N` schemas geram sobrecarga de _migrations_ e
  de _connection pooling_ em larga escala.
- **Banco compartilhado + `tenant_id`** — uma base, discriminador em toda tabela de negócio.
  Escala bem; isolamento depende de disciplina de _query_.
- **Banco compartilhado + `tenant_id` + RLS** — o acima, com **Row-Level Security** do
  PostgreSQL reforçando o isolamento no próprio banco.

## Decisão

Adotamos **banco compartilhado com `tenant_id` em todas as entidades de negócio, reforçado por
Row-Level Security (RLS)**. O `tenant_id` corrente é definido por requisição (via variável de
sessão/`SET LOCAL`) e a política de RLS garante que nenhuma linha de outro tenant seja visível,
mesmo diante de uma _query_ que esqueça o filtro. Detalhes e diagramas em
[multi-tenant.md](../architecture/multi-tenant.md).

## Consequências

### Positivas
- Escala para muitos tenants com um único conjunto de _migrations_ e _pool_ de conexões.
- **Defesa em profundidade:** filtro na aplicação + RLS no banco.
- Custo por tenant baixo.

### Negativas / trade-offs
- Risco de _cross-tenant leakage_ se o `tenant_id` de sessão não for setado corretamente —
  exige middleware confiável.
- "Vizinho barulhento": tenants grandes podem impactar outros (mitigável com particionamento e,
  no limite, _sharding_ por tenant).

### Riscos e mitigações
- **Risco:** esquecer de setar o tenant de sessão. **Mitigação:** middleware obrigatório +
  testes automatizados de isolamento + RLS como rede de segurança.
- **Risco:** _bypass_ por conexões administrativas. **Mitigação:** contas de aplicação sem
  `BYPASSRLS`; segregação de credenciais.

## Impacto

É a decisão central de [multi-tenant](../architecture/multi-tenant.md),
[segurança](../security/security.md) e [modelagem de dados](../database/modeling.md). Habilita a
extração futura de um tenant/segmento para infraestrutura dedicada, se necessário.

## Referências

- [Multi-Tenant](../architecture/multi-tenant.md) · [Segurança](../security/security.md)
- [ADR-0002: PostgreSQL](0002-postgresql-primary-db.md)
