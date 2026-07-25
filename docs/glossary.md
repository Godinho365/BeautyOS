---
title: "Glossário / Linguagem Ubíqua"
type: reference
status: ativo
owner: Arquitetura
updated: 2026-07-24
tags: [documentacao]
---

# Glossário / Linguagem Ubíqua

> **Status:** Ativo · **Dono:** Arquitetura · **Última atualização:** 2026-07-24

## Objetivo

Estabelecer a **linguagem ubíqua** do BeautyOS: um conceito, um nome — usado de forma idêntica
em documentação, código, banco de dados e API. Reduz ambiguidade e alinha domínio e engenharia.

## Contexto

Termos como "empresa", "cliente" e "conta" facilmente se confundem em um SaaS multi-tenant do
mercado da beleza. Este glossário é a referência canônica citada por todos os demais documentos
(ver [CONTRIBUTING-DOCS](CONTRIBUTING-DOCS.md)).

## Termos de plataforma

| Termo | Definição | Nome técnico sugerido |
|---|---|---|
| **Tenant** | Unidade de isolamento lógico de dados. No BeautyOS, 1 Tenant = 1 Empresa. | `tenant_id` |
| **Empresa** | O negócio de beleza cliente do BeautyOS (salão, barbearia, clínica, rede). | `Company` |
| **Unidade / Filial** | Local físico de uma Empresa (uma Empresa pode ter várias). | `Branch` |
| **Usuário** | Pessoa autenticável que acessa o sistema (dono, gestor, profissional, recepção). | `User` |
| **Papel (Role)** | Conjunto de permissões atribuído a um Usuário dentro de uma Empresa. | `Role` |
| **Plano / Assinatura** | Contrato comercial da Empresa com o BeautyOS (billing da plataforma). | `Subscription` |

## Termos de domínio (beleza)

| Termo | Definição | Nome técnico sugerido |
|---|---|---|
| **Profissional** | Pessoa que presta serviços (cabeleireiro, manicure, esteticista). | `Professional` |
| **Cliente Final** | Consumidor que agenda e compra serviços da Empresa. **Não** é Usuário do sistema. | `Customer` |
| **Serviço** | Item ofertado no catálogo (corte, manicure, coloração), com duração e preço. | `Service` |
| **Produto** | Item físico vendido ou consumido (cosmético), controlado em Estoque. | `Product` |
| **Agendamento** | Reserva de um Serviço com um Profissional em data/hora para um Cliente. | `Appointment` |
| **Comanda** | Conta aberta de um atendimento, agregando serviços e produtos consumidos. | `Ticket` / `Order` |
| **Comissão** | Valor devido a um Profissional por serviços/produtos realizados. | `Commission` |
| **Fidelidade** | Programa de pontos/recompensas para reter Clientes. | `LoyaltyProgram` |

## Termos de arquitetura

| Termo | Definição |
|---|---|
| **Bounded Context** | Fronteira dentro da qual um modelo de domínio é consistente. Ver [modules.md](architecture/modules.md). |
| **Módulo** | Implementação de um bounded context no monólito modular. |
| **Domain Event** | Fato de negócio ocorrido no passado (ex.: `AppointmentBooked`). Ver [events.md](architecture/events.md). |
| **Outbox** | Padrão que garante publicação confiável de eventos junto à transação. |
| **SSOT** | _Single Source of Truth_ — documento/dono canônico de um conceito. |
| **RLS** | _Row-Level Security_ do PostgreSQL, usado para isolamento por tenant. |
| **Copilot** | Assistente de IA que apoia a gestão da Empresa. Ver [copilot.md](ai/copilot.md). |

## Boas práticas

- Ao introduzir um termo novo de domínio, adicione-o aqui **antes** de usá-lo no código.
- Prefira o **nome técnico sugerido** em entidades, tabelas e endpoints.

## Más práticas

- ❌ Usar "cliente" ambiguamente para Empresa (tenant) e para Cliente Final. São entidades
  distintas: **Empresa** é quem contrata o BeautyOS; **Cliente Final** é quem a Empresa atende.

## Referências

- Eric Evans, _Domain-Driven Design_ (Ubiquitous Language).
- [Glossário de módulos](architecture/modules.md) para os limites de cada contexto.
