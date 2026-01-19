from django.apps import AppConfig


class PoaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'poa'

    def ready(self):
        import poa.signals