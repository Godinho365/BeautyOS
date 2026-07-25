---
title: "IA / Copilot"
type: ai
status: rascunho
owner: IA
updated: 2026-07-24
tags: [ia, copilot]
---

# IA / Copilot

> **Status:** Rascunho estruturado · **Dono:** IA · **Última atualização:** 2026-07-24

## Objetivo

Definir a estratégia de IA do BeautyOS: um **Copilot** que atua como gerente virtual de
crescimento da Empresa, além de agentes e automações que apoiam a operação.

## Contexto

IA é o principal diferencial do produto ([visão](../product/vision.md)). O módulo `ai`
**consome** dados dos demais contextos (CRM, financeiro, agenda) — nunca redefine suas regras
([módulos](../architecture/modules.md)) — e opera sob o mesmo isolamento multi-tenant.

## Responsabilidades

- Gerar insights e recomendações a partir dos dados **do próprio tenant**.
- Executar automações com **guardrails** e ações auditáveis.
- **Não** é dono de regra de negócio de outro módulo.

## Capacidades (visão)

| Capacidade | Descrição |
|---|---|
| **Copilot** | Assistente conversacional sobre o negócio (faturamento, agenda, clientes). |
| **RAG** | Respostas fundamentadas em dados do tenant (busca semântica com `pgvector`). |
| **Agentes/automações** | Tarefas como reengajar clientes inativos, sugerir reposição de estoque. |
| **Insights** | Alertas proativos (queda de recompra, horários ociosos). |

## Guardrails (obrigatórios)

- **Isolamento:** todo contexto e recuperação de dados é escopado por `tenant_id`
  ([multi-tenant](../architecture/multi-tenant.md)).
- **Autorização:** o Copilot age no limite do papel do usuário ([segurança](../security/security.md)).
- **Ações sensíveis** (enviar mensagem, alterar dado) exigem confirmação e são auditadas.
- **Sem dados pessoais** em logs/prompts além do necessário (LGPD).

## Exemplos

- "Quais horários ficaram ociosos esta semana?" → RAG sobre `scheduling` do tenant.
- Evento `ProductStockLow` → agente sugere pedido de reposição ([eventos](../architecture/events.md)).

## Boas práticas

- Fundamentar respostas (RAG) e citar a origem dos números.
- Medir **custo por tenant** (tokens) e impor cotas.
- Avaliar qualidade (evals) antes de expor uma automação.

## Más práticas

- ❌ Enviar dados de um tenant no contexto de outro.
- ❌ Executar ação irreversível sem confirmação/auditoria.
- ❌ Tratar saída do LLM como verdade sem _grounding_.

## Impacto

Diferencial competitivo e retenção; risco: custo de inferência, privacidade e alucinação —
mitigados por guardrails, RAG e limites por tenant.

## Evolução futura

- Detalhar arquitetura de agentes, memória e ferramentas.
- Catálogo de automações e sistema de _evals_.
- Seleção de modelos por custo/qualidade e _caching_ de contexto.

## Referências

- [Visão do Produto](../product/vision.md) · [Módulos](../architecture/modules.md)
- [Multi-Tenant](../architecture/multi-tenant.md) · [Segurança](../security/security.md)
