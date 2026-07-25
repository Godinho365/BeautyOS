from django.apps import AppConfig


class MarketingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.marketing"

    def ready(self):
        from . import handlers  # noqa: F401

        handlers.register()
