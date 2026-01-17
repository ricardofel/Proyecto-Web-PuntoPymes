from django.db import models
from integraciones.constants import EstadoIntegracion, EventosWebhook
class IntegracionErp(models.Model):
    """Configuración de conexiones a sistemas externos (SAP, Oracle, etc.)"""
    nombre = models.CharField(max_length=50, help_text="Ej: SAP HANA, Oracle Netsuite")
    url_api = models.URLField(help_text="Endpoint principal del sistema externo")
    api_key = models.CharField(max_length=255, help_text="Token de autenticación")
    usuario_api = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    fecha_ultima_sincronizacion = models.DateTimeField(null=True, blank=True)
    estado_sincronizacion = models.CharField(
        max_length=20, 
        choices=EstadoIntegracion.OPCIONES,
        default=EstadoIntegracion.EXITOSO
    )

    class Meta:
        verbose_name = "Configuración ERP"
        verbose_name_plural = "Integraciones ERP"

    def __str__(self):
        return f"{self.nombre} ({'Activo' if self.activo else 'Inactivo'})"


class Webhook(models.Model):
    EVENTOS = EventosWebhook.OPCIONES

    nombre = models.CharField(max_length=100, help_text="Ej: Notificar a Slack RRHH")
    evento = models.CharField(max_length=50, choices=EVENTOS)
    url_destino = models.URLField(help_text="URL donde se enviará el POST")
    secret_key = models.CharField(max_length=100, blank=True, null=True, help_text="Para firmar el payload")
    activo = models.BooleanField(default=True)
    
    intentos_fallidos = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} -> {self.evento}"


class LogIntegracion(models.Model):
    """Historial de comunicaciones (Auditoría técnica de integraciones)"""
    integracion = models.ForeignKey(IntegracionErp, on_delete=models.CASCADE, null=True, blank=True)
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=255)
    codigo_respuesta = models.IntegerField(help_text="Ej: 200, 404, 500")
    mensaje_respuesta = models.TextField(blank=True)

    def __str__(self):
        return f"{self.fecha.strftime('%Y-%m-%d %H:%M')} - {self.codigo_respuesta}"