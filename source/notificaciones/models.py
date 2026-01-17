from django.db import models
from django.conf import settings
from notificaciones.constants import TiposNotificacion

class Notificacion(models.Model):
    TIPOS = TiposNotificacion.OPCIONES

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default=TiposNotificacion.INFO)
    url_destino = models.CharField(max_length=200, blank=True, null=True, help_text="Link al hacer clic")
    
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"{self.usuario} - {self.titulo}"