"""Copilot — camada de inteligência do BeautyOS (ver docs/ai/copilot.md).

Nesta fase o Copilot é **determinístico**: agrega dados dos módulos (via seus
`contracts`) e gera insights/sugestões **fundamentados nos números do tenant** —
sem alucinação e sem depender de LLM externo. É a linha de base e o guardrail
sobre o qual a evolução com LLM/RAG será construída.

Não importa models ORM de outros módulos: consome apenas os contratos públicos.
"""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass

from apps.crm.contracts import customers_count
from apps.finance.contracts import revenue_today_cents
from apps.inventory.contracts import low_stock_count
from apps.scheduling.contracts import appointments_today_count


@dataclass(frozen=True)
class Insights:
    revenue_today_cents: int
    appointments_today: int
    low_stock_products: int
    customers_total: int
    suggestions: list[str]


def compute_insights(tenant_id: uuid.UUID) -> dict:
    revenue = revenue_today_cents(tenant_id)
    appts = appointments_today_count(tenant_id)
    low_stock = low_stock_count(tenant_id)
    customers = customers_count(tenant_id)

    suggestions: list[str] = []
    if appts == 0:
        suggestions.append("Nenhum agendamento hoje — considere uma campanha de reativação.")
    if low_stock > 0:
        suggestions.append(f"{low_stock} produto(s) com estoque baixo — planeje reposição.")
    if revenue == 0 and appts > 0:
        suggestions.append("Há agendamentos hoje, mas nenhuma comanda fechada ainda.")
    if not suggestions:
        suggestions.append("Operação saudável — sem alertas no momento.")

    return asdict(
        Insights(
            revenue_today_cents=revenue,
            appointments_today=appts,
            low_stock_products=low_stock,
            customers_total=customers,
            suggestions=suggestions,
        )
    )
