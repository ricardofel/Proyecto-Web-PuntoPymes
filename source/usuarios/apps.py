# usuarios/apps.py
from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    """
    Configuración de la aplicación 'usuarios'.

    Define el tipo de campo automático por defecto y
    registra señales al iniciar la aplicación.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "usuarios"

    def ready(self):
        """
        Método ejecutado cuando la aplicación está lista.

        Se utiliza para importar y registrar las señales
        asociadas a la aplicación.
        """
        import usuarios.signals
