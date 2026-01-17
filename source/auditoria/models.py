from django.db import models
from django.conf import settings
from auditoria.constants import AccionesLog


class LogAuditoria(models.Model):
    """Modelo que registra eventos de auditoría del sistema."""
    ACCIONES = AccionesLog.OPCIONES

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    accion = models.CharField(max_length=10, choices=ACCIONES)
    modulo = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    objeto_id = models.CharField(max_length=50)
    detalle = models.TextField()

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ["-fecha"]

    def __str__(self):
        return f"[{self.fecha}] {self.usuario} - {self.accion} {self.modelo}"
