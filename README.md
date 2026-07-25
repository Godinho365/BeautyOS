# BeautyOS Engineering Kit

**BeautyOS** é uma plataforma **SaaS multi-tenant** para gestão do mercado da beleza — o
*sistema operacional* de salões, barbearias, clínicas e redes de estética. Este repositório é o
**kit de engenharia**: a documentação de arquitetura, padrões e decisões que guiam a construção
do produto (docs-as-code) e o contexto operacional para o Claude Code.

> Este repositório é **documentação**, não código de aplicação. A documentação tem o mesmo peso
> da implementação: versionada, revisada por PR e mantida sempre consistente.

## Para quem é

- **Engenharia** (backend, frontend, mobile, dados, IA): fonte de verdade de arquitetura e padrões.
- **Arquitetura/Tech Lead**: registro de decisões (ADRs) e diretrizes.
- **Produto**: visão, escopo e roadmap.

## Por onde começar

1. [Visão do Produto](docs/product/vision.md) — o que estamos construindo e por quê.
2. [Visão Geral da Arquitetura](docs/architecture/overview.md) — estilo, stack e diagramas C4.
3. [Glossário](docs/glossary.md) — a linguagem ubíqua do domínio.
4. [Índice completo da documentação](docs/README.md) — o mapa de tudo.

## Pilares de qualidade

Toda decisão considera: **escalabilidade, modularidade, baixo acoplamento, alta coesão,
manutenibilidade, segurança, performance, testabilidade e observabilidade**. Padrões adotados:
DDD, Clean Architecture, SOLID, Repository/Service Layer, Domain Events, Outbox, OpenAPI,
OWASP, LGPD e 12-Factor App.

## Estrutura do repositório

```
.
├── README.md                 # você está aqui
├── docs/                     # documentação de engenharia (SSOT) — ver docs/README.md
│   ├── product/              # visão de produto
│   ├── architecture/         # arquitetura, módulos, multi-tenant, domínio, eventos
│   ├── api/                  # diretrizes de API
│   ├── database/             # modelagem de dados
│   ├── security/             # segurança, LGPD, RBAC
│   ├── observability/        # logs, métricas, tracing
│   ├── testing/              # estratégia de testes
│   ├── devops/               # deploy e CI/CD
│   ├── ai/                   # copilot / IA
│   └── decisions/            # ADRs (Architecture Decision Records)
└── .claude/                  # contexto operacional do Claude Code (skills, prompts, checklists)
```

## Contribuindo

Antes de editar qualquer documento, leia [CONTRIBUTING-DOCS.md](docs/CONTRIBUTING-DOCS.md):
define o template obrigatório, as convenções de nomenclatura e a política de **fonte única de
verdade (SSOT)**.
