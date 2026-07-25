"""Popula dados de demonstração para explorar o painel/API rapidamente.

Cria um tenant (Empresa), um usuário dono e alguns serviços, profissionais,
clientes e um agendamento. Idempotente: reexecutar não duplica.

    python manage.py seed_demo

Credenciais criadas:
    e-mail: demo@beautyos.dev
    senha:  demo12345
"""
from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.catalog.models import Service
from apps.common.tenant_context import use_tenant
from apps.crm.models import Customer
from apps.identity.models import User
from apps.scheduling.services import book_appointment
from apps.staff.models import Professional
from apps.tenant.models import Company

DEMO_EMAIL = "demo@beautyos.dev"
DEMO_PASSWORD = "demo12345"


class Command(BaseCommand):
    help = "Cria dados de demonstração (tenant, usuário, serviços, profissionais, clientes)."

    def handle(self, *args, **options):
        company, created = Company.objects.get_or_create(name="Salão Demo")
        self.stdout.write(("Empresa criada: " if created else "Empresa existente: ") + str(company.id))

        user, u_created = User.objects.get_or_create(
            email=DEMO_EMAIL,
            defaults={"tenant_id": company.id, "is_staff": True, "role": "owner"},
        )
        if u_created:
            user.set_password(DEMO_PASSWORD)
            user.tenant_id = company.id
            user.role = "owner"
            user.save()
        self.stdout.write(("Usuário criado: " if u_created else "Usuário existente: ") + DEMO_EMAIL)

        with use_tenant(company.id):
            svc_corte, _ = Service.objects.get_or_create(
                tenant_id=company.id, name="Corte Feminino",
                defaults={"duration_minutes": 60, "price_cents": 8000},
            )
            Service.objects.get_or_create(
                tenant_id=company.id, name="Barba",
                defaults={"duration_minutes": 30, "price_cents": 4000},
            )
            Service.objects.get_or_create(
                tenant_id=company.id, name="Manicure",
                defaults={"duration_minutes": 45, "price_cents": 5000},
            )
            prof, _ = Professional.objects.get_or_create(
                tenant_id=company.id, name="Ana Souza", defaults={"specialty": "Cabelo"}
            )
            Professional.objects.get_or_create(
                tenant_id=company.id, name="Bruno Lima", defaults={"specialty": "Barba"}
            )
            cust, _ = Customer.objects.get_or_create(
                tenant_id=company.id, name="Cliente Demo", defaults={"phone": "11999990000"}
            )

            # Um agendamento futuro (se ainda não houver nenhum para o profissional).
            from apps.scheduling.models import Appointment

            if not Appointment.objects.filter(professional_id=prof.id).exists():
                book_appointment(
                    tenant_id=company.id, customer_id=cust.id, professional_id=prof.id,
                    service_id=svc_corte.id, starts_at=timezone.now() + timedelta(days=1),
                )
                self.stdout.write("Agendamento de exemplo criado.")

        self.stdout.write(self.style.SUCCESS(
            f"Seed concluído. Login: {DEMO_EMAIL} / {DEMO_PASSWORD}"
        ))
