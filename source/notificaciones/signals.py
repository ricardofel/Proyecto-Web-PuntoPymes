from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from solicitudes.models import SolicitudAusencia
from notificaciones.services.notificacion_service import NotificacionService
from notificaciones.constants import TiposNotificacion

@receiver(post_save, sender=SolicitudAusencia)
def notificar_cambio_solicitud(sender, instance, created, **kwargs):
    if created:
        return
    # se notifica cambio de estado 
    NotificacionService.crear_notificacion(
        usuario=instance.empleado.usuario,
        titulo="Actualización de Solicitud",
        mensaje=f"Tu solicitud ha cambiado a estado: {instance.estado}",
        tipo=TiposNotificacion.INFO,
        url=f"/solicitudes/{instance.id}/"
    )