from django.db.models.signals import post_save
from django.dispatch import receiver
from solicitudes.models import SolicitudAusencia
from notificaciones.services.notificacion_service import NotificacionService
from notificaciones.constants import TiposNotificacion

@receiver(post_save, sender=SolicitudAusencia)
def notificar_flujo_solicitud(sender, instance, created, **kwargs):
    """
    Maneja las notificaciones de Ausencias (Vacaciones, Permisos, etc).
    Al ser una relación directa, NO requiere editar vistas.
    """
    
    # CASO 1: Nueva Solicitud -> Avisar al Jefe
    if created:
        # Intentamos obtener el jefe inmediato desde la Unidad Organizacional
        jefe = None
        if instance.empleado.unidad_org and instance.empleado.unidad_org.manager:
             jefe = instance.empleado.unidad_org.manager
        
        # Si existe el jefe y tiene usuario, le notificamos
        if jefe and jefe.usuario:
            NotificacionService.crear_notificacion(
                usuario=jefe.usuario,
                titulo="Nueva Solicitud por Aprobar",
                mensaje=f"{instance.empleado.nombres} solicita: {instance.ausencia.nombre}.",
                tipo=TiposNotificacion.INFO,
                url="/solicitudes/responder/" 
            )
        return

    # CASO 2: Cambio de Estado -> Avisar al Empleado
    if instance.empleado.usuario:
        # Definimos el mensaje según el estado
        titulo = "Actualización de Solicitud"
        tipo = TiposNotificacion.INFO
        mensaje = f"Tu solicitud está en estado: {instance.get_estado_display()}."

        if instance.estado == 'aprobado': 
            tipo = TiposNotificacion.EXITO
            titulo = "¡Solicitud Aprobada!"
            mensaje = "Tu solicitud ha sido aprobada. ¡Disfruta tu tiempo!"
        
        elif instance.estado == 'rechazado':
            tipo = TiposNotificacion.ERROR
            titulo = "Solicitud Rechazada"
            mensaje = "Tu solicitud no ha sido aprobada. Contacta con tu supervisor."
        
        elif instance.estado == 'devuelto':
            tipo = TiposNotificacion.ALERTA
            titulo = "Solicitud Devuelta"
            mensaje = "Se requiere más información para procesar tu solicitud."

        # Enviamos la notificación
        NotificacionService.crear_notificacion(
            usuario=instance.empleado.usuario,
            titulo=titulo,
            mensaje=mensaje,
            tipo=tipo,
            url=f"/solicitudes/detalle/{instance.id}/"
        )