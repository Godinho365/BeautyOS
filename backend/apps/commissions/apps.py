from django.apps import AppConfig


class CommissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.commissions"

    def ready(self):
        from . import handlers  # noqa: F401

        handlers.register()
