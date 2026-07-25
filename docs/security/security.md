---
title: "Segurança"
type: security
status: ativo
owner: Segurança
updated: 2026-07-24
tags: [seguranca, lgpd]
---

# Segurança

> **Status:** Ativo · **Dono:** Segurança · **Última atualização:** 2026-07-24

## Objetivo

Definir os controles de segurança do BeautyOS: autenticação, autorização, proteção de dados
(LGPD), postura OWASP e modelo de ameaças. Segurança é requisito de primeira classe em um SaaS
multi-tenant que guarda dados financeiros e pessoais.

## Contexto

O maior risco do produto é **vazamento cross-tenant** — mitigado pela estratégia de
[multi-tenant](../architecture/multi-tenant.md). Este documento cobre os demais vetores e
consolida os controles transversais.

## Responsabilidades

- **Auth (`identity`):** autenticação, emissão/rotação de tokens, MFA.
- **Tenant (`tenant`):** RBAC por Empresa (papéis × permissões).
- **Todos os módulos:** validação de entrada, escopo de tenant, auditoria de ações sensíveis.

## Autenticação (AuthN)

- **JWT** de curta duração (access) + **refresh token** rotativo e revogável.
- Senhas com hashing forte (Argon2/bcrypt); **MFA** para papéis administrativos.
- Tokens carregam `sub` (usuário) e claims de Empresa; **nunca** carregam dados sensíveis.

## Autorização (AuthZ) — RBAC por Empresa

Permissões são resolvidas por **papel dentro da Empresa** (um usuário pode ter papéis diferentes
em Empresas diferentes). Matriz base (exemplo, não exaustiva):

| Recurso \ Papel | Owner | Gestor | Profissional | Recepção |
|---|---|---|---|---|
| Empresa/configurações | CRUD | R | — | — |
| Agendamentos | CRUD | CRUD | R (os seus) | CRUD |
| Financeiro/Comandas | CRUD | CRUD | R (os seus) | C, R |
| Comissões | R | CRUD | R (as suas) | — |
| Estoque | CRUD | CRUD | R | R |
| Relatórios/IA | R | R | — | — |

> `C=criar R=ler U=atualizar D=excluir`. A matriz completa e versionada vive junto ao módulo
> `tenant`; esta tabela é o contrato de referência.

## Proteção de dados & LGPD

- **Bases legais** e finalidade documentadas por tipo de dado (cliente final, profissional).
- **Direitos do titular:** acesso, correção, exclusão/anonimização e portabilidade.
- **Minimização e retenção:** guardar o necessário; políticas de retenção por categoria.
- **Criptografia:** TLS em trânsito; em repouso no banco/backup; segredos em cofre (não no código).
- **Auditoria:** trilha imutável de ações sensíveis (quem, o quê, quando, tenant).

## Threat model (STRIDE) — resumo

| Ameaça | Exemplo | Mitigação |
|---|---|---|
| **S**poofing | Uso de token roubado | JWT curto, rotação de refresh, MFA. |
| **T**ampering | Alterar `tenant_id` na requisição | Tenant vem do token/sessão, nunca do cliente; RLS. |
| **R**epudiation | Negar ação feita | Auditoria imutável. |
| **I**nfo disclosure | Vazamento cross-tenant | `tenant_id` + RLS ([multi-tenant](../architecture/multi-tenant.md)). |
| **D**oS | Abuso de API | Rate limiting por tenant/usuário, cotas. |
| **E**levation | Escalar privilégio | RBAC verificado no servidor, testes de autorização. |

## Exemplos

- **Checagem de autorização** ocorre **sempre no servidor**, por caso de uso, com o tenant e o
  papel do usuário — nunca confiando em flags do frontend.
- **Rate limiting:** `429 Too Many Requests` com `Retry-After`, chave por `tenant_id`+usuário.

## Boas práticas

- Escopar toda query por tenant e depender da RLS como rede de segurança.
- Segredos em cofre/variáveis de ambiente ([12-Factor](../devops/deploy.md)).
- Validar e normalizar toda entrada; _output encoding_ para evitar XSS.
- Princípio do menor privilégio em credenciais de banco e integrações.

## Más práticas

- ❌ Confiar em `tenant_id`/permissões enviados pelo cliente.
- ❌ Logar dados pessoais/sensíveis ou tokens.
- ❌ Autorização só no frontend.
- ❌ Guardar segredos no repositório.

## Impacto

Controles bem definidos reduzem risco regulatório (LGPD) e de incidentes cross-tenant, que são
existenciais para um SaaS B2B. Custo: disciplina de auditoria e testes de autorização.

## Evolução futura

- OWASP **ASVS** como checklist formal por release.
- SSO/SAML e SCIM para clientes enterprise.
- Detecção de anomalias e alertas de acesso (ver [observabilidade](../observability/observability.md)).
- Pentests periódicos e programa de _bug bounty_.

## Referências

- [Multi-Tenant](../architecture/multi-tenant.md) · [Deploy/12-Factor](../devops/deploy.md)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/) · [LGPD (Lei 13.709/2018)](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
