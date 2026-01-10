from django.db import models
from django.conf import settings

class LogAuditoria(models.Model):
    ACCIONES = [
        ('CREAR', 'Creación'),
        ('EDITAR', 'Edición'),
        ('ELIMINAR', 'Eliminación'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, # Si borran al usuario, queda el log
        null=True, blank=True
    )
    accion = models.CharField(max_length=10, choices=ACCIONES)
    modulo = models.CharField(max_length=50) # Ej: EMPLEADOS
    modelo = models.CharField(max_length=50) # Ej: Empleado
    objeto_id = models.CharField(max_length=50) # ID del objeto afectado
    detalle = models.TextField() # Resumen de qué pasó
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.fecha}] {self.usuario} - {self.accion} {self.modelo}"