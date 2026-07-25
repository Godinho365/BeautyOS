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
    "apps.notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "apps.common.middleware.TenantMiddleware",  # define app.tenant_id na transação (RLS)
]

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
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.openapi.AutoSchema",
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
