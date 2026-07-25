"""Casos de uso do módulo finance (Service Layer — ver CODING_STANDARD).

Invariantes:
- Comanda fechada é imutável (não aceita itens/pagamentos nem fechar de novo).
- Total da comanda = soma dos subtotais dos itens.
- Só fecha comanda com total > 0 e totalmente paga (pago >= total).
- Ao fechar, emite `TicketClosed` via Outbox (ADR-0005) — consumidores futuros:
  estoque (baixa) e comissões (cálculo). Ver docs/architecture/events.md.
"""
from __future__ import annotations

import uuid

from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from apps.common.outbox import record_event
from apps.crm.contracts import customer_exists
from apps.scheduling.contracts import appointment_exists

from .models import Payment, Ticket, TicketItem


class FinanceError(Exception):
    """Base de erros do módulo finance."""


class InvalidFinanceError(FinanceError):
    """Entrada/estado inválido (referência inexistente)."""


class ConflictFinanceError(FinanceError):
    """Operação não permitida no estado atual (ex.: comanda fechada)."""


def _get_open_ticket(ticket_id: uuid.UUID) -> Ticket:
    ticket = Ticket.objects.filter(id=ticket_id).first()
    if ticket is None:
        raise InvalidFinanceError("Comanda inexistente.")
    if ticket.status == Ticket.Status.CLOSED:
        raise ConflictFinanceError("Comanda já fechada.")
    return ticket


def _recompute_total(ticket: Ticket) -> None:
    agg = ticket.items.aggregate(total=Sum(F("quantity") * F("unit_price_cents")))
    ticket.total_cents = agg["total"] or 0
    ticket.save(update_fields=["total_cents", "updated_at"])


def open_ticket(*, tenant_id: uuid.UUID, customer_id: uuid.UUID, appointment_id: uuid.UUID | None = None) -> Ticket:
    if not customer_exists(tenant_id, customer_id):
        raise InvalidFinanceError("Cliente inexistente.")
    if appointment_id and not appointment_exists(tenant_id, appointment_id):
        raise InvalidFinanceError("Agendamento inexistente.")
    return Ticket.objects.create(
        tenant_id=tenant_id, customer_id=customer_id, appointment_id=appointment_id
    )


def add_item(
    *, tenant_id: uuid.UUID, ticket_id: uuid.UUID, description: str,
    unit_price_cents: int, quantity: int = 1, service_id: uuid.UUID | None = None,
) -> TicketItem:
    with transaction.atomic():
        ticket = _get_open_ticket(ticket_id)
        item = TicketItem.objects.create(
            tenant_id=tenant_id, ticket=ticket, description=description,
            unit_price_cents=unit_price_cents, quantity=quantity, service_id=service_id,
        )
        _recompute_total(ticket)
    return item


def register_payment(
    *, tenant_id: uuid.UUID, ticket_id: uuid.UUID, amount_cents: int, method: str = Payment.Method.PIX,
) -> Payment:
    with transaction.atomic():
        ticket = _get_open_ticket(ticket_id)
        return Payment.objects.create(
            tenant_id=tenant_id, ticket=ticket, amount_cents=amount_cents, method=method,
        )


def _paid_cents(ticket: Ticket) -> int:
    return ticket.payments.aggregate(paid=Sum("amount_cents"))["paid"] or 0


def close_ticket(*, tenant_id: uuid.UUID, ticket_id: uuid.UUID) -> Ticket:
    with transaction.atomic():
        ticket = _get_open_ticket(ticket_id)
        _recompute_total(ticket)
        if ticket.total_cents <= 0:
            raise ConflictFinanceError("Comanda sem itens não pode ser fechada.")
        if _paid_cents(ticket) < ticket.total_cents:
            raise ConflictFinanceError("Pagamento insuficiente para fechar a comanda.")
        ticket.status = Ticket.Status.CLOSED
        ticket.closed_at = timezone.now()
        ticket.save(update_fields=["status", "closed_at", "updated_at"])
        record_event(
            "TicketClosed",
            {
                "ticket_id": str(ticket.id),
                "customer_id": str(ticket.customer_id),
                "total_cents": ticket.total_cents,
            },
            tenant_id=tenant_id,
        )
    return ticket
