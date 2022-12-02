from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bakerydemo.base"

    def ready(self):
        from . import listeners  # noqa
