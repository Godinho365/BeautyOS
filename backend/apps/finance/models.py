"""Módulo finance — Comandas e Pagamentos.

- `Ticket` (Comanda): conta de um atendimento, agrega itens e pagamentos.
- `TicketItem`: linha da comanda (serviço/produto consumido).
- `Payment`: pagamento registrado na comanda.

Isolados por tenant (RLS). Valores sempre em centavos (int), nunca float
(ver docs/database/modeling.md). FKs internas ao módulo são permitidas; referências
a outros contextos (customer, service, appointment) são por ID.
"""
from __future__ import annotations

from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import TenantScopedModel


class Ticket(TenantScopedModel):
    class Status(models.TextChoices):
        OPEN = "open", "Aberta"
        CLOSED = "closed", "Fechada"

    customer_id = models.UUIDField()
    appointment_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    total_cents = models.BigIntegerField(default=0)
    currency = models.CharField(max_length=3, default="BRL")
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "finance_ticket"
        indexes = [models.Index(fields=["tenant_id", "status"])]

    def __str__(self) -> str:
        return f"Ticket {self.id} ({self.status})"


class TicketItem(TenantScopedModel):
    ticket = models.ForeignKey(Ticket, related_name="items", on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    service_id = models.UUIDField(null=True, blank=True)  # referência ao catalog (por ID)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price_cents = models.BigIntegerField(validators=[MinValueValidator(0)])

    class Meta:
        db_table = "finance_ticket_item"
        indexes = [models.Index(fields=["tenant_id", "ticket"])]

    @property
    def subtotal_cents(self) -> int:
        return self.quantity * self.unit_price_cents


class Payment(TenantScopedModel):
    class Method(models.TextChoices):
        CASH = "cash", "Dinheiro"
        CARD = "card", "Cartão"
        PIX = "pix", "Pix"

    ticket = models.ForeignKey(Ticket, related_name="payments", on_delete=models.CASCADE)
    amount_cents = models.BigIntegerField(validators=[MinValueValidator(1)])
    method = models.CharField(max_length=10, choices=Method.choices, default=Method.PIX)
    paid_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "finance_payment"
        indexes = [models.Index(fields=["tenant_id", "ticket"])]
