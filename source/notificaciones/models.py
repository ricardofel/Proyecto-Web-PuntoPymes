from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

"""
Modelos de la app notificaciones:

- Notificacion (Buzón central - Tabla 10)
- NotificacionCanal (Entrega multicanal - Tabla 11)

Ver diccionario de datos Tablas 10 y 11.
"""


class Notificacion(models.Model):
    # Tabla notificacion
    id = models.BigAutoField(primary_key=True)
    empresa = models.ForeignKey("core.Empresa", on_delete=models.CASCADE)

    # FK a tu modelo de Usuario personalizado
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()

    # Contexto de origen (ej: 'ausencias', 'kpi')
    modulo = models.CharField(max_length=50)

    # ID polimórfico simple (referencia manual a la entidad origen)
    referencia_id = models.BigIntegerField(blank=True, null=True)

    # Datos extra para el frontend (JSONB en Postgres)
    metadata = models.JSONField(blank=True, null=True)

    leida = models.BooleanField(default=False)
    order_date = models.DateTimeField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notificacion"
        ordering = ["-order_date"]

    def __str__(self):
        return f"{self.titulo} - {self.usuario}"


class NotificacionCanal(models.Model):
    # Tabla notificacion_canal
    id = models.BigAutoField(primary_key=True)
    notificacion = models.ForeignKey(Notificacion, on_delete=models.CASCADE)

    # Ej: 'email', 'web', 'movil', 'sms'
    canal = models.CharField(max_length=20)

    # Ej: 'pendiente', 'enviado', 'error'
    estado_envio = models.CharField(max_length=20, default="pendiente")

    fecha_envio = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "notificacion_canal"

    def __str__(self):
        return f"{self.canal} -> {self.notificacion}"
