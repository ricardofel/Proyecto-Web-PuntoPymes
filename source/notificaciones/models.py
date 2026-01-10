from django.db import models
from django.conf import settings

class Notificacion(models.Model):
    TIPOS = [
        ('info', 'Información'),   # Azul
        ('success', 'Éxito'),      # Verde
        ('warning', 'Alerta'),     # Amarillo
        ('error', 'Error'),        # Rojo
    ]

    # Relación directa con el usuario (sin empresa obligatoria para agilizar)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones')
    
    titulo = models.CharField(max_length=100)
    mensaje = models.TextField()
    
    # Campos para la UI
    tipo = models.CharField(max_length=10, choices=TIPOS, default='info')
    leido = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True, null=True, help_text="Ruta relativa (ej: /empleados/1/)")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo} - {self.usuario}"