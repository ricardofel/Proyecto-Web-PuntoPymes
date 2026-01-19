from django.db.models.signals import post_save
from django.dispatch import receiver
from asistencia.models import JornadaCalculada
from notificaciones.services.notificacion_service import NotificacionService
from notificaciones.constants import TiposNotificacion

@receiver(post_save, sender=JornadaCalculada)
def notificar_novedad_asistencia(sender, instance, created, **kwargs):
    """Notifica al empleado si tiene atrasos o faltas tras el cálculo diario."""
    if instance.empleado.usuario:
        
        if instance.estado == JornadaCalculada.EstadoJornada.ATRASO:
            NotificacionService.crear_notificacion(
                usuario=instance.empleado.usuario,
                titulo="Registro de Atraso",
                mensaje=f"Entrada registrada con {instance.minutos_tardanza} minutos de retraso el día {instance.fecha}.",
                tipo=TiposNotificacion.ALERTA,
                url="/asistencia/mis-registros/"
            )
            
        elif instance.estado == JornadaCalculada.EstadoJornada.FALTA:
            NotificacionService.crear_notificacion(
                usuario=instance.empleado.usuario,
                titulo="Ausencia Registrada",
                mensaje=f"No se registraron marcaciones para el día {instance.fecha}. Por favor justifica tu falta.",
                tipo=TiposNotificacion.ERROR,
                url="/solicitudes/crear/"
            )