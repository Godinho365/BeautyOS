#!/usr/bin/env python3
"""Validador de documentação (docs-as-code) do BeautyOS.

Verifica, em todos os arquivos Markdown do repositório:
  1. Links internos relativos resolvem (sem links quebrados).
  2. Blocos de código (```), incl. Mermaid, estão balanceados.
  3. Documentos em `docs/` possuem frontmatter YAML obrigatório com os campos mínimos.

Uso:
    python scripts/validate_docs.py

Sai com código 1 se encontrar qualquer problema (para falhar a CI); 0 se tudo estiver ok.
Sem dependências externas — usa apenas a biblioteca padrão.
"""
from __future__ import annotations
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED_FRONTMATTER = ("title", "type", "status", "owner", "updated", "tags")
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)]+)\)")  # ignora imagens ![]()
EXTERNAL = ("http://", "https://", "mailto:", "tel:")


def iter_markdown() -> list[str]:
    out: list[str] = []
    for dirpath, dirnames, filenames in os.walk(REPO):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for fn in filenames:
            if fn.endswith(".md"):
                out.append(os.path.join(dirpath, fn))
    return out


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        m = re.match(r"\s*([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data


def rel(path: str) -> str:
    return os.path.relpath(path, REPO).replace(os.sep, "/")


def main() -> int:
    broken_links: list[str] = []
    unbalanced: list[str] = []
    missing_fm: list[str] = []

    for path in iter_markdown():
        text = open(path, encoding="utf-8").read()

        # 1. fences balanceados
        if text.count("```") % 2 != 0:
            unbalanced.append(rel(path))

        # 2. links internos
        base = os.path.dirname(path)
        for m in LINK_RE.finditer(text):
            link = m.group(1).split("#")[0].strip()
            if not link or link.startswith(EXTERNAL):
                continue
            target = os.path.normpath(os.path.join(base, link))
            if not os.path.exists(target):
                broken_links.append(f"{rel(path)} -> {link}")

        # 3. frontmatter obrigatório em docs/
        if rel(path).startswith("docs/"):
            fm = parse_frontmatter(text)
            if fm is None:
                missing_fm.append(f"{rel(path)} (sem frontmatter)")
            else:
                faltando = [k for k in REQUIRED_FRONTMATTER if k not in fm]
                if faltando:
                    missing_fm.append(f"{rel(path)} (faltam: {', '.join(faltando)})")

    problemas = 0

    def report(titulo: str, itens: list[str]) -> None:
        nonlocal problemas
        if itens:
            problemas += len(itens)
            print(f"\n[FALHA] {titulo} ({len(itens)}):")
            for it in itens:
                print(f"  - {it}")

    report("Links internos quebrados", broken_links)
    report("Blocos de codigo desbalanceados", unbalanced)
    report("Frontmatter ausente/incompleto em docs/", missing_fm)

    total = len(iter_markdown())
    if problemas == 0:
        print(f"[OK] {total} arquivos .md validados: 0 problemas.")
        return 0
    print(f"\n[ERRO] {problemas} problema(s) em {total} arquivos .md.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
