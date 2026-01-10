from django.apps import AppConfig

class AuditoriaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auditoria'

    def ready(self):
        # ¡ESTO ES CRÍTICO! Sin esto, el espía duerme.
        import auditoria.signals