# Prompt: Criar um módulo

> Contexto canônico: [`docs/architecture/modules.md`](../../docs/architecture/modules.md) ·
> [`domain-model.md`](../../docs/architecture/domain-model.md) ·
> [`events.md`](../../docs/architecture/events.md) · [`glossary.md`](../../docs/glossary.md).

Ao criar um módulo (bounded context), siga o [template](../templates/module_template.md) e:

1. **Domínio** — defina o bounded context, suas fronteiras e dependências permitidas
   (registre/atualize em [ADR-0004](../../docs/decisions/0004-canonical-modules.md) se novo).
2. **Entidades/Agregados** — raiz de agregado e invariantes ([domain-model](../../docs/architecture/domain-model.md)).
3. **Casos de uso** — camada de aplicação (Clean Architecture).
4. **APIs** — conforme [diretrizes de API](../../docs/api/api_guidelines.md).
5. **Eventos** — publique via Outbox ([events](../../docs/architecture/events.md)).
6. **Multi-tenant** — `tenant_id` + RLS ([multi-tenant](../../docs/architecture/multi-tenant.md)).
7. **Testes** — incluindo isolamento de tenant ([testes](../../docs/testing/testing-strategy.md)).

Antes de concluir, valide o [checklist de feature](../checklists/feature.md).
