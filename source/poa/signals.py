from django.db.models.signals import post_save
from django.dispatch import receiver
from poa.models import ActividadEmpleado
from notificaciones.services.notificacion_service import NotificacionService
from notificaciones.constants import TiposNotificacion

@receiver(post_save, sender=ActividadEmpleado)
def notificar_asignacion_actividad(sender, instance, created, **kwargs):
    """
    Se ejecuta cuando se vincula un empleado a una actividad del POA.
    """
    # Solo notificamos si es una nueva asignación (created=True)
    if created and instance.empleado.usuario:
        
        actividad = instance.actividad
        print(f"--- DEBUG POA: Asignando actividad '{actividad.nombre}' a {instance.empleado} ---")

        NotificacionService.crear_notificacion(
            usuario=instance.empleado.usuario,
            titulo="Nueva Responsabilidad POA",
            mensaje=f"Se te ha asignado la actividad: '{actividad.nombre}'. Fecha límite: {actividad.fecha_fin}.",
            tipo=TiposNotificacion.INFO,
            url=f"/poa/objetivos/"  # Ajusta si tienes una vista de detalle específica
        )