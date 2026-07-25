"""Configurações do BeautyOS backend (walking skeleton).

Segue os princípios 12-Factor: toda configuração vem do ambiente
(ver docs/devops/deploy.md). Não colocar segredos aqui.
"""
from datetime import timedelta
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["*"]),
)
# Lê backend/.env se existir (dev). Em prod, as vars vêm do ambiente.
environ.Env.read_env(BASE_DIR / ".env")

# --- Segurança / core -------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-inseguro-troque-em-producao")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# --- Aplicações -------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    # Terceiros
    "rest_framework",
    "corsheaders",
    "drf_spectacular",
    # Módulos BeautyOS (bounded contexts) — ver docs/architecture/modules.md
    "apps.common",
    "apps.tenant",
    "apps.identity",
    "apps.catalog",
    "apps.staff",
    "apps.crm",
    "apps.scheduling",
    "apps.finance",
    "apps.inventory",
    "apps.commissions",
    "apps.marketing",
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # antes do CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "apps.common.middleware.TenantMiddleware",  # define app.tenant_id na transação (RLS)
]

# CORS: origens do painel web autorizadas a chamar a API (ver docs/frontend/overview.md).
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS", default=["http://localhost:3000"]
)

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

# --- Banco de dados ---------------------------------------------------------
# ATOMIC_REQUESTS=False de propósito: quem abre a transação da requisição é o
# TenantMiddleware, para poder aplicar `SET LOCAL app.tenant_id` DENTRO dela
# (essencial para a RLS). Ver apps/common/middleware.py e
# docs/architecture/multi-tenant.md.
DATABASES = {
    "default": {
        **env.db("DATABASE_URL", default="postgres://beautyos_app:beautyos_app@localhost:5432/beautyos"),
        "ATOMIC_REQUESTS": False,
    }
}

# --- Autenticação -----------------------------------------------------------
AUTH_USER_MODEL = "identity.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Autenticado + RBAC por papel (ver apps/common/permissions.py e security.md).
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "apps.common.permissions.RoleBasedPermission",
    ),
    # Schema OpenAPI via drf-spectacular.
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Paginação padrão (envelope {count,next,previous,results}). Ver api_guidelines.md.
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    # Rate limiting por usuário/anônimo (ajustar por ambiente).
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.UserRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"user": "1000/hour", "anon": "60/hour"},
}

SPECTACULAR_SETTINGS = {
    "TITLE": "BeautyOS API",
    "DESCRIPTION": "API do BeautyOS — SaaS de gestão do mercado da beleza.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    # claim customizada com o tenant do usuário (ver apps/identity/serializers.py)
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# --- Internacionalização ----------------------------------------------------
# --- Celery (relay assíncrono do Outbox) -----------------------------------
# Ver docs/architecture/events.md e docs/devops/deploy.md.
CELERY_BROKER_URL = env("REDIS_URL", default="redis://localhost:6379/0")
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_BEAT_SCHEDULE = {
    "process-outbox": {
        "task": "apps.common.tasks.process_outbox",
        "schedule": 10.0,  # segundos
    },
}

# --- Internacionalização ----------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# --- Estáticos --------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
