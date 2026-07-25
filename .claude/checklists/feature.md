# Checklist de Feature

> Concluir uma feature exige todos os itens abaixo. Referências apontam para o SSOT.

- [ ] **Arquitetura** — respeita fronteiras de módulo e context map ([modules](../../docs/architecture/modules.md)).
- [ ] **Multi-tenant** — `tenant_id` + RLS aplicados ([multi-tenant](../../docs/architecture/multi-tenant.md)).
- [ ] **API** — conforme [diretrizes](../../docs/api/api_guidelines.md) (erros, paginação, versão).
- [ ] **Eventos** — efeitos entre módulos via Outbox ([events](../../docs/architecture/events.md)).
- [ ] **Testes** — unit/integração + **isolamento de tenant** ([testes](../../docs/testing/testing-strategy.md)).
- [ ] **Segurança** — authz no servidor, LGPD, sem segredo no código ([segurança](../../docs/security/security.md)).
- [ ] **Performance** — índices por `tenant_id`, sem N+1.
- [ ] **Observabilidade** — logs/métricas com `tenant_id` e `trace_id` ([obs](../../docs/observability/observability.md)).
- [ ] **Documentação** — atualizada no mesmo PR ([docs-as-code](../../docs/CONTRIBUTING-DOCS.md)).
- [ ] **ADR** — decisão relevante registrada ([decisions](../../docs/decisions/README.md)).
