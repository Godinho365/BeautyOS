"""Rotas do marketplace sob /api/v1/marketplace/. Ver docs/architecture/modules.md."""
from django.urls import path

from .views import (
    MyProfileView,
    PublicBookingView,
    PublicCompanyDetailView,
    PublicCompanyListView,
)

urlpatterns = [
    path("profile", MyProfileView.as_view(), name="marketplace-profile"),
    path("companies", PublicCompanyListView.as_view(), name="marketplace-companies"),
    path("companies/<slug:slug>", PublicCompanyDetailView.as_view(), name="marketplace-company"),
    path("companies/<slug:slug>/book", PublicBookingView.as_view(), name="marketplace-book"),
]
