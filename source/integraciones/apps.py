from django.apps import AppConfig

class IntegracionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'integraciones'

    def ready(self):
        import integraciones.signals
