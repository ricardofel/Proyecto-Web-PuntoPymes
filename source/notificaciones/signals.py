from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Importamos modelos de otros apps (Lazy import dentro de la función si hay ciclos)
from solicitudes.models import SolicitudAusencia
from notificaciones.services.notificacion_service import NotificacionService
from notificaciones.constants import TiposNotificacion

@receiver(post_save, sender=SolicitudAusencia)
def notificar_cambio_solicitud(sender, instance, created, **kwargs):
    if created:
        return # Solo notificamos cambios de estado, no creación inicial (opcional)
    
    # Si el estado cambió (asumiendo lógica de detección de cambios)
    # Le avisamos al empleado
    NotificacionService.crear_notificacion(
        usuario=instance.empleado.usuario, # Asumiendo relación
        titulo="Actualización de Solicitud",
        mensaje=f"Tu solicitud ha cambiado a estado: {instance.estado}",
        tipo=TiposNotificacion.INFO,
        url=f"/solicitudes/{instance.id}/"
    )