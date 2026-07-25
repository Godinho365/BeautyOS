from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"

    def ready(self):
        # Registra os handlers de eventos deste módulo ao subir a app.
        from . import handlers  # noqa: F401

        handlers.register()
