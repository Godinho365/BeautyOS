---
title: "Contribuindo com a Documentação (Docs-as-Code)"
type: governance
status: ativo
owner: Arquitetura
updated: 2026-07-24
tags: [documentacao]
---

# Contribuindo com a Documentação (Docs-as-Code)

> **Status:** Ativo · **Dono:** Arquitetura · **Última atualização:** 2026-07-24

## Objetivo

Definir como a documentação do BeautyOS é escrita, revisada e mantida. No BeautyOS,
**documentação é código**: tem a mesma importância da implementação, segue revisão por _pull
request_ e nunca pode ficar desatualizada ou conflitante. Nenhuma decisão arquitetural pode
existir apenas no código ou na cabeça de alguém — tudo é registrado aqui.

## Contexto

À medida que o produto cresce para atender centenas de milhares de empresas, a documentação
precisa escalar junto: ser navegável, consistente e livre de duplicação. Este documento é o
contrato que garante isso. Ele é a fonte única de verdade sobre **como documentamos**.

## Responsabilidades

- **Autor(a) da mudança:** produzir/atualizar a documentação afetada no mesmo PR do código.
- **Revisor(a):** barrar PRs que alterem comportamento sem atualizar a documentação.
- **Dono da área (owner):** manter a fonte única de verdade (SSOT) do seu domínio consistente.

## Princípios

1. **Fonte Única de Verdade (SSOT).** Cada conceito tem **um** dono. Outros documentos
   **referenciam** (link), nunca copiam. Ex.: multi-tenant é definido só em
   [`architecture/multi-tenant.md`](architecture/multi-tenant.md); a lista de módulos só em
   [`architecture/modules.md`](architecture/modules.md).
2. **Documentação como código.** Versionada em Git, revisada por PR, com _diffs_ pequenos e
   mensagens claras.
3. **Decisões viram ADR.** Toda decisão arquitetural relevante é registrada em
   [`decisions/`](decisions/README.md) no formato MADR.
4. **Linguagem ubíqua.** Use os termos do [glossário](glossary.md). Um conceito = um nome, em
   todos os documentos, código e API.
5. **Escreva para quem chega agora.** Contexto antes de detalhe; exemplo antes de abstração.

## Template obrigatório de documento

Todo documento novo ou reescrito **deve** começar com **frontmatter** e conter as seções abaixo
(omita apenas as que comprovadamente não se aplicam, justificando). O arquivo base pronto está em
[`templates/document-template.md`](templates/document-template.md).

```markdown
---
title: "<Título>"
type: <architecture|api|database|security|product|ai|governance|reference|decision|moc>
status: <rascunho|ativo|descontinuado>
owner: <área>
updated: <YYYY-MM-DD>
tags: [<tag1>, <tag2>]
---

# <Título>

## Objetivo
Uma frase: o que este documento resolve e para quem.

## Contexto
Por que isto existe, o problema que endereça, restrições relevantes.

## Responsabilidades
Quem/o quê é responsável pelo que aqui descrito. Limites (o que NÃO é responsabilidade).

## <Conteúdo técnico>
O corpo do documento: diagramas (Mermaid), tabelas, regras, contratos.

## Exemplos
Casos concretos — código, payloads, cenários de uso.

## Boas práticas
O que fazer. Padrões recomendados.

## Más práticas
Anti-padrões a evitar, com o porquê.

## Decisões arquiteturais
Links para os ADRs que embasam este documento.

## Impacto
Consequências em escalabilidade, segurança, performance, custo, manutenção.

## Evolução futura
O que muda quando escalarmos; próximos passos conhecidos.

## Referências
Links internos e externos (padrões, RFCs, documentação oficial).
```

## Convenções de nomenclatura

- Arquivos: `kebab-case.md` (ex.: `multi-tenant.md`, `api-guidelines.md`).
- ADRs: `NNNN-titulo-em-kebab-case.md`, numeração sequencial de 4 dígitos.
- Diretórios em `docs/` por área de conhecimento (architecture, api, security, …).
- Termos de negócio sempre conforme o [glossário](glossary.md).
- Diagramas: **Mermaid** embutido no Markdown (nunca imagens binárias, para permitir _diff_).
- MOCs: arquivo `_MOC.md` por área (o underscore o mantém no topo da listagem).

## MOCs e Obsidian

O Vault ([`docs/`](README.md)) é compatível com Obsidian. Recomendações:

- **Frontmatter** em todo documento (`title`, `type`, `status`, `owner`, `updated`, `tags`) —
  veja o [template de documento](templates/document-template.md).
- **MOC (Map of Content):** cada área ganha um `_MOC.md` **quando tem 2+ documentos**; até lá é
  acessada pelo [MOC raiz](_MOC.md). Todo MOC de área liga-se de volta ao MOC raiz.
- **Links & backlinks:** use links Markdown relativos (portáveis e validáveis em CI); o Obsidian
  gera os backlinks automaticamente a partir deles.
- **Callouts:** `> [!note] > [!warning] > [!danger] > [!tip]` para destacar contexto.

## Boas práticas

- Prefira **link** a repetição: se precisar citar um conceito, aponte para o SSOT.
- Mantenha o cabeçalho de status/data atualizado a cada alteração significativa.
- Use tabelas para matrizes (papéis×permissões, ambiente×config).
- Escreva exemplos executáveis/copiáveis sempre que possível.

## Más práticas

- ❌ Copiar a mesma lista/definição em dois documentos (gera divergência silenciosa).
- ❌ Registrar decisão só na descrição de um PR ou no código.
- ❌ Documento sem dono e sem data (vira lixo não confiável).
- ❌ Diagrama como imagem (não versiona nem revisa bem).

## Impacto

Um padrão único reduz o custo de onboarding, elimina documentação conflitante e permite que a
base de conhecimento escale com o produto sem virar dívida.

## Evolução futura

- Automação de _lint_ de links quebrados e de seções obrigatórias em CI.
- Publicação estática (ex.: MkDocs/Docusaurus) a partir de `docs/`.
- Geração de referência de API a partir do contrato OpenAPI.

## Referências

- [MADR — Markdown Any Decision Records](https://adr.github.io/madr/)
- [C4 Model](https://c4model.com/)
- [Diátaxis — framework de documentação](https://diataxis.fr/)
- [The Twelve-Factor App](https://12factor.net/)
